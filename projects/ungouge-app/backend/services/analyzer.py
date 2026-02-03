"""
Quote Analysis Service - Enhanced with Realistic Cost Models

This service analyzes contractor quotes by comparing them against:
1. Comprehensive project cost models with itemized breakdowns
2. BLS wage data with regional adjustments
3. Industry-standard markup ranges (overhead + profit)
4. Common upsell patterns and red flags

The analyzer uses fuzzy matching to categorize line items and applies
regional cost multipliers for accurate local pricing.
"""

import json
import os
from typing import List, Dict, Optional, Tuple
from difflib import SequenceMatcher
from models.quote import QuoteSubmission, LineItem
from models.report import Report, LineItemAnalysis
from sqlalchemy.ext.asyncio import AsyncSession

# Load cost models once at module load
_COST_MODELS = None
_BLS_RATES = None

def _load_cost_models():
    """Load project cost models from JSON file"""
    global _COST_MODELS
    if _COST_MODELS is None:
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        with open(os.path.join(data_dir, 'project_cost_models.json'), 'r') as f:
            _COST_MODELS = json.load(f)
    return _COST_MODELS

def _load_bls_rates():
    """Load BLS wage rates from JSON file"""
    global _BLS_RATES
    if _BLS_RATES is None:
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        with open(os.path.join(data_dir, 'sample_bls_rates.json'), 'r') as f:
            _BLS_RATES = json.load(f)
    return _BLS_RATES

def get_regional_multiplier(zip_code: str) -> Tuple[float, str]:
    """
    Determine regional cost multiplier based on ZIP code.
    Returns (multiplier, region_name)
    """
    if not zip_code or len(zip_code) < 1:
        return (1.0, "national_average")
    
    models = _load_cost_models()
    regional_data = models.get('regional_multipliers', {})
    
    # Use first digit of ZIP code
    zip_prefix = zip_code[0]
    
    for region_name, region_info in regional_data.items():
        if zip_prefix in region_info.get('zip_prefixes', []):
            return (region_info['multiplier'], region_name)
    
    # Default to national average
    return (1.0, "national_average")

def fuzzy_match_category(item_name: str, categories: Dict, threshold: float = 0.6) -> Optional[Tuple[str, float]]:
    """
    Use fuzzy string matching to find the best category match.
    Returns (category_key, confidence_score) or None
    """
    item_lower = item_name.lower()
    best_match = None
    best_score = 0.0
    
    # Keywords to search for in categories
    search_terms = item_lower.split()
    
    for category_key, category_data in categories.items():
        category_lower = category_key.lower().replace('_', ' ')
        
        # Direct substring match
        if category_lower in item_lower or item_lower in category_lower:
            score = 0.9
            if score > best_score:
                best_score = score
                best_match = category_key
                continue
        
        # Fuzzy match on full strings
        ratio = SequenceMatcher(None, item_lower, category_lower).ratio()
        if ratio > best_score:
            best_score = ratio
            best_match = category_key
        
        # Check individual words
        for term in search_terms:
            if len(term) > 3:  # Ignore short words
                if term in category_lower:
                    score = 0.7 + (len(term) / len(category_lower)) * 0.2
                    if score > best_score:
                        best_score = score
                        best_match = category_key
    
    if best_score >= threshold:
        return (best_match, best_score)
    return None

def extract_quantity_from_description(item_name: str, quantity: int) -> Tuple[int, str]:
    """
    Extract actual quantity and unit from item description.
    e.g., "Remove 2000 sq ft of old roofing" -> (2000, "sq ft")
    """
    import re
    
    # Common patterns
    patterns = [
        r'(\d+)\s*(?:square\s*)?(?:feet|foot|ft|sq\s*ft)',
        r'(\d+)\s*(?:linear\s*)?(?:feet|foot|ft|lf)',
        r'(\d+)\s*(?:squares?)',  # roofing squares
        r'(\d+)\s*(?:gallons?|gal)',
        r'(\d+)\s*(?:hours?|hrs?)',
    ]
    
    item_lower = item_name.lower()
    for pattern in patterns:
        match = re.search(pattern, item_lower)
        if match:
            extracted_qty = int(match.group(1))
            if 'sq' in item_lower or 'square' in item_lower:
                return (extracted_qty, 'sq_ft')
            elif 'linear' in item_lower or 'lf' in item_lower:
                return (extracted_qty, 'linear_ft')
            elif 'square' in item_lower and 'roof' in item_lower:
                return (extracted_qty, 'roofing_square')
            return (extracted_qty, 'units')
    
    return (quantity, 'units')

async def analyze_quote(
    quote: QuoteSubmission,
    db: AsyncSession,
) -> Report:
    """
    Main quote analysis function using comprehensive cost models
    """
    
    # Load models
    cost_models = _load_cost_models()
    
    # Get regional multiplier
    regional_mult, region_name = get_regional_multiplier(quote.location)
    
    line_analyses = []
    total_quoted = 0.0
    total_fair_low = 0.0
    total_fair_high = 0.0
    
    for item in quote.line_items:
        analysis = await analyze_line_item(
            item,
            quote.project_type,
            quote.location,
            regional_mult,
            region_name,
            cost_models,
        )
        line_analyses.append(analysis)
        total_quoted += analysis.quoted_price
        total_fair_low += analysis.fair_price_low
        total_fair_high += analysis.fair_price_high
    
    # Generate overall assessment
    overall_assessment = generate_overall_assessment(
        total_quoted,
        total_fair_low,
        total_fair_high,
        line_analyses,
        quote.project_type,
        region_name,
    )
    
    return Report(
        id="",  # Will be set by caller
        project_type=quote.project_type,
        location=quote.location,
        total_quoted=total_quoted,
        total_fair_low=total_fair_low,
        total_fair_high=total_fair_high,
        overall_assessment=overall_assessment,
        line_items=line_analyses,
        created_at="",  # Will be set by caller
    )

async def analyze_line_item(
    item: LineItem,
    project_type: str,
    location: str,
    regional_mult: float,
    region_name: str,
    cost_models: Dict,
) -> LineItemAnalysis:
    """
    Analyze a single line item using cost models
    """
    
    # Get project-specific cost data
    project_data = cost_models.get('project_types', {}).get(project_type, {})
    
    if not project_data:
        # Unknown project type - use generic analysis
        return analyze_generic_line_item(item, regional_mult, region_name)
    
    # Extract quantity and unit from description
    actual_quantity, unit_type = extract_quantity_from_description(
        item.item_name,
        item.quantity
    )
    
    # Try to match line item to a category in the cost model
    fair_price_low = 0.0
    fair_price_high = 0.0
    explanation = ""
    matched_category = None
    confidence = 0.0
    
    # Search in materials, labor, and components sections
    for section_name in ['materials', 'labor', 'components', 'common_jobs', 'common_repairs']:
        section = project_data.get(section_name, {})
        if section:
            match_result = fuzzy_match_category(item.item_name, section)
            if match_result:
                matched_category, confidence = match_result
                category_data = section[matched_category]
                
                # Calculate fair price based on category data
                fair_low, fair_high, expl = calculate_fair_price_from_category(
                    category_data,
                    actual_quantity,
                    unit_type,
                    regional_mult,
                    matched_category,
                    section_name,
                )
                
                if fair_low > 0:
                    fair_price_low = fair_low
                    fair_price_high = fair_high
                    explanation = expl
                    break
    
    # If no match found, try generic estimation
    if fair_price_low == 0:
        return analyze_generic_line_item(item, regional_mult, region_name)
    
    # Determine assessment
    assessment = determine_assessment(
        item.quoted_price,
        fair_price_low,
        fair_price_high,
    )
    
    # Enhance explanation with assessment details
    explanation = enhance_explanation(
        explanation,
        item.quoted_price,
        fair_price_low,
        fair_price_high,
        assessment,
        matched_category,
        confidence,
        project_type,
        project_data,
    )
    
    return LineItemAnalysis(
        item_name=item.item_name,
        quoted_price=item.quoted_price,
        fair_price_low=round(fair_price_low, 2),
        fair_price_high=round(fair_price_high, 2),
        assessment=assessment,
        explanation=explanation,
        bls_rate=0.0,  # Not used in new model
        material_cost=0.0,  # Not used in new model
    )

def calculate_fair_price_from_category(
    category_data: Dict,
    quantity: int,
    unit_type: str,
    regional_mult: float,
    category_name: str,
    section_name: str,
) -> Tuple[float, float, str]:
    """
    Calculate fair price range from category data
    Returns (low, high, explanation_base)
    """
    
    # Handle different data structures
    if isinstance(category_data, dict):
        # Crew labor (highest priority - most specific)
        if 'crew_hours_per_square' in category_data and 'loaded_crew_rate_per_hour' in category_data:
            hours_per_sq = category_data['crew_hours_per_square']
            rate = category_data['loaded_crew_rate_per_hour']
            base_cost_per_sq = hours_per_sq * rate
            range_low = category_data.get('range_low', base_cost_per_sq * 0.8)
            range_high = category_data.get('range_high', base_cost_per_sq * 1.2)
            fair_low = range_low * regional_mult * quantity
            fair_high = range_high * regional_mult * quantity
            
            expl = f"Crew labor for {category_name.replace('_', ' ')}: {hours_per_sq} crew-hrs/square × ${rate}/hr = ${base_cost_per_sq:.0f}/square. "
            expl += f"Typical range: ${range_low:.0f}-${range_high:.0f}/square. "
            expl += f"For {quantity} square(s) with regional adjustment ({regional_mult:.2f}x), "
            expl += f"fair range is ${fair_low:,.0f}-${fair_high:,.0f}."
            
            return (fair_low, fair_high, expl)
        
        # Look for cost indicators
        if 'total_low' in category_data and 'total_high' in category_data:
            base_low = category_data['total_low']
            base_high = category_data['total_high']
            fair_low = base_low * regional_mult * quantity
            fair_high = base_high * regional_mult * quantity
            
            expl = f"Based on industry data for {category_name.replace('_', ' ')}, "
            expl += f"typical cost is ${base_low:,.0f}-${base_high:,.0f} per unit. "
            expl += f"With regional adjustment ({regional_mult:.2f}x), "
            expl += f"fair range for {quantity} unit(s) is ${fair_low:,.0f}-${fair_high:,.0f}."
            
            return (fair_low, fair_high, expl)
        
        elif 'total' in category_data:
            base_total = category_data['total']
            fair_low = base_total * 0.85 * regional_mult * quantity
            fair_high = base_total * 1.15 * regional_mult * quantity
            
            expl = f"Typical cost for {category_name.replace('_', ' ')} is ${base_total:,.0f}. "
            expl += f"Regional adjustment ({regional_mult:.2f}x) applied. "
            
            return (fair_low, fair_high, expl)
        
        elif 'cost_per_square' in category_data:
            # Per-square pricing (roofing etc)
            base_cost = category_data['cost_per_square']
            range_low = category_data.get('range_low', base_cost * 0.85)
            range_high = category_data.get('range_high', base_cost * 1.15)
            fair_low = range_low * regional_mult * quantity
            fair_high = range_high * regional_mult * quantity
            
            expl = f"Standard cost for {category_name.replace('_', ' ')} is ${base_cost:,.0f}/square (100 sq ft). "
            expl += f"Range: ${range_low:,.0f}-${range_high:,.0f}/square. "
            expl += f"For {quantity} square(s) with regional adjustment ({regional_mult:.2f}x), "
            expl += f"fair range is ${fair_low:,.0f}-${fair_high:,.0f}."
            
            return (fair_low, fair_high, expl)
        
        elif 'per_sq_ft' in str(category_data):
            # Per square foot pricing
            for key, value in category_data.items():
                if 'per_sq_ft' in key and isinstance(value, (int, float)):
                    base_cost = value
                    fair_low = base_cost * 0.9 * regional_mult * quantity
                    fair_high = base_cost * 1.3 * regional_mult * quantity
                    
                    expl = f"Standard cost for {category_name.replace('_', ' ')} is ${base_cost:.2f}/sq ft. "
                    expl += f"For {quantity} sq ft with regional adjustment, fair range is ${fair_low:,.0f}-${fair_high:,.0f}."
                    
                    return (fair_low, fair_high, expl)
        
        elif 'range_low' in category_data and 'range_high' in category_data:
            base_low = category_data['range_low']
            base_high = category_data['range_high']
            fair_low = base_low * regional_mult * quantity
            fair_high = base_high * regional_mult * quantity
            
            expl = f"Market range for {category_name.replace('_', ' ')}: ${base_low:,.0f}-${base_high:,.0f}. "
            expl += f"Adjusted for region ({regional_mult:.2f}x)."
            
            return (fair_low, fair_high, expl)
        
        elif 'low' in category_data and 'high' in category_data:
            base_low = category_data['low']
            base_high = category_data['high']
            fair_low = base_low * regional_mult * quantity
            fair_high = base_high * regional_mult * quantity
            
            expl = f"Market range for {category_name.replace('_', ' ')}: ${base_low:,.0f}-${base_high:,.0f}. "
            expl += f"Adjusted for region ({regional_mult:.2f}x)."
            
            return (fair_low, fair_high, expl)
        
        elif 'equipment' in category_data and 'installation' in category_data:
            equipment = category_data.get('equipment', 0)
            installation = category_data.get('installation', 0)
            base_total = equipment + installation
            fair_low = base_total * 0.85 * regional_mult * quantity
            fair_high = base_total * 1.15 * regional_mult * quantity
            
            expl = f"Typical cost breakdown: ${equipment:,.0f} equipment + ${installation:,.0f} installation. "
            expl += f"Regional adjustment: {regional_mult:.2f}x."
            
            return (fair_low, fair_high, expl)
        
        elif 'hours_per_square' in category_data and 'rate_per_hour' in category_data:
            hours_per_sq = category_data['hours_per_square']
            rate = category_data['rate_per_hour']
            base_cost_per_sq = hours_per_sq * rate
            # Apply contractor markup (20-35%)
            fair_low = base_cost_per_sq * 1.20 * regional_mult * quantity
            fair_high = base_cost_per_sq * 1.35 * regional_mult * quantity
            
            expl = f"Labor for {category_name.replace('_', ' ')}: {hours_per_sq} hrs/square × ${rate}/hr = ${base_cost_per_sq:.0f}/square. "
            expl += f"With 20-35% markup and regional adjustment ({regional_mult:.2f}x), "
            expl += f"fair range for {quantity} square(s) is ${fair_low:,.0f}-${fair_high:,.0f}."
            
            return (fair_low, fair_high, expl)
        
        elif 'labor_hours' in category_data and 'rate_per_hour' in category_data:
            hours = category_data['labor_hours']
            rate = category_data['rate_per_hour']
            materials = category_data.get('materials', 0)
            base_total = (hours * rate) + materials
            
            # Apply markup
            fair_low = base_total * 1.20 * regional_mult * quantity
            fair_high = base_total * 1.35 * regional_mult * quantity
            
            expl = f"Labor: {hours} hrs @ ${rate}/hr"
            if materials > 0:
                expl += f" + ${materials} materials"
            expl += f". With standard markup and regional adjustment ({regional_mult:.2f}x)."
            
            return (fair_low, fair_high, expl)
    
    # Couldn't determine pricing
    return (0.0, 0.0, "")

def analyze_generic_line_item(
    item: LineItem,
    regional_mult: float,
    region_name: str,
) -> LineItemAnalysis:
    """
    Generic analysis for items that don't match known categories
    """
    
    # Use simple estimation based on price magnitude
    quoted = item.quoted_price
    
    # Assume quoted price might be fair, give a range around it
    fair_low = quoted * 0.7
    fair_high = quoted * 1.1
    
    assessment = "unknown"
    explanation = (
        f"We don't have specific pricing data for '{item.item_name}'. "
        f"This appears to be a specialized or custom item. "
        f"We recommend getting 2-3 additional quotes for comparison. "
        f"Based on the quoted price of ${quoted:,.2f}, a reasonable range "
        f"might be ${fair_low:,.0f}-${fair_high:,.0f}, but this is a rough estimate."
    )
    
    return LineItemAnalysis(
        item_name=item.item_name,
        quoted_price=item.quoted_price,
        fair_price_low=round(fair_low, 2),
        fair_price_high=round(fair_high, 2),
        assessment=assessment,
        explanation=explanation,
        bls_rate=0.0,
        material_cost=0.0,
    )

def determine_assessment(
    quoted_price: float,
    fair_low: float,
    fair_high: float,
) -> str:
    """
    Determine the assessment category based on how much over fair price
    
    Categories:
    - fair: within 10% of fair high
    - slightly_high: 10-25% over fair high
    - high: 25-50% over fair high  
    - gouging: >50% over fair high
    """
    if quoted_price <= fair_high * 1.10:
        return "fair"
    elif quoted_price <= fair_high * 1.25:
        return "slightly_high"
    elif quoted_price <= fair_high * 1.50:
        return "high"
    else:
        return "gouging"

def enhance_explanation(
    base_explanation: str,
    quoted_price: float,
    fair_low: float,
    fair_high: float,
    assessment: str,
    category: str,
    confidence: float,
    project_type: str,
    project_data: Dict,
) -> str:
    """
    Enhance explanation with assessment-specific details and red flags
    """
    
    explanation = base_explanation + "\n\n"
    
    percent_over = ((quoted_price - fair_high) / fair_high * 100) if fair_high > 0 else 0
    
    if assessment == "fair":
        explanation += f"✓ This quote (${quoted_price:,.2f}) falls within the fair range. "
        explanation += "The pricing appears reasonable for your area."
    
    elif assessment == "slightly_high":
        explanation += f"⚠ This quote is about {percent_over:.0f}% above typical market rates. "
        explanation += "While not unreasonable, you might be able to negotiate this down or "
        explanation += "get a better price from another contractor."
    
    elif assessment == "high":
        explanation += f"⚠⚠ This quote is {percent_over:.0f}% above fair market value. "
        explanation += "This is significantly elevated. We strongly recommend getting 2-3 additional "
        explanation += "quotes and questioning this pricing with the contractor."
    
    else:  # gouging
        explanation += f"🚨 RED FLAG: This quote is {percent_over:.0f}% above fair market value. "
        explanation += "This appears to be price gouging. Do not proceed with this contractor. "
        explanation += "Get multiple competing quotes immediately."
    
    # Add red flags if applicable
    if assessment in ["high", "gouging"]:
        red_flags = project_data.get('red_flags', [])
        if red_flags:
            # Check if any red flags match this category
            category_lower = category.lower() if category else ""
            relevant_flags = [
                flag for flag in red_flags 
                if any(word in flag.lower() for word in category_lower.split('_'))
            ]
            if relevant_flags:
                explanation += "\n\n⚠ Specific red flags for this item:\n"
                for flag in relevant_flags[:2]:  # Show top 2 most relevant
                    explanation += f"• {flag}\n"
    
    return explanation

def generate_overall_assessment(
    total_quoted: float,
    total_fair_low: float,
    total_fair_high: float,
    line_analyses: List[LineItemAnalysis],
    project_type: str,
    region_name: str,
) -> str:
    """
    Generate comprehensive overall assessment of the entire quote
    """
    
    # Calculate overall percentage difference
    if total_fair_high > 0:
        percent_diff = ((total_quoted - total_fair_high) / total_fair_high * 100)
    else:
        percent_diff = 0
    
    # Determine overall tone
    if total_quoted <= total_fair_high * 1.10:
        assessment = "FAIR"
        tone = "✓ This quote appears to be fair and reasonable overall."
        recommendation = "You can proceed with confidence, though it never hurts to get one more quote for comparison."
    elif total_quoted <= total_fair_high * 1.25:
        assessment = "SLIGHTLY HIGH"
        tone = "⚠ This quote is slightly elevated but not unreasonable."
        recommendation = "Try negotiating, especially on the line items flagged above. Get 1-2 additional quotes for leverage."
    elif total_quoted <= total_fair_high * 1.50:
        assessment = "HIGH"
        tone = "⚠⚠ This quote is higher than typical market rates for your area."
        recommendation = "DO NOT accept this quote without getting at least 2-3 competing quotes. Use our analysis when negotiating."
    else:
        assessment = "GOUGING"
        tone = "🚨 This quote appears to be significantly overpriced and may be price gouging."
        recommendation = "DO NOT proceed with this contractor. Get multiple quotes from other contractors immediately."
    
    # Count problematic items
    high_items = [a for a in line_analyses if a.assessment in ["high", "gouging"]]
    slightly_high_items = [a for a in line_analyses if a.assessment == "slightly_high"]
    unknown_items = [a for a in line_analyses if a.assessment == "unknown"]
    
    # Build summary
    summary = f"## Overall Assessment: {assessment}\n\n{tone}\n\n"
    
    summary += f"**Total Quoted:** ${total_quoted:,.2f}\n"
    summary += f"**Fair Range:** ${total_fair_low:,.2f} - ${total_fair_high:,.2f}\n"
    
    if percent_diff > 0:
        summary += f"**Amount Over Fair Price:** ${total_quoted - total_fair_high:,.2f} ({percent_diff:.0f}%)\n\n"
    else:
        summary += "\n"
    
    # Break down problem areas
    if high_items:
        summary += f"### 🚨 Major Issues ({len(high_items)} items)\n"
        summary += "The following items are significantly overpriced:\n"
        for item in high_items[:5]:  # Show top 5
            over = ((item.quoted_price - item.fair_price_high) / item.fair_price_high * 100)
            summary += f"• **{item.item_name}**: ${item.quoted_price:,.2f} "
            summary += f"(should be ${item.fair_price_low:,.0f}-${item.fair_price_high:,.0f}, "
            summary += f"{over:.0f}% over)\n"
        summary += "\n"
    
    if slightly_high_items:
        summary += f"### ⚠ Items to Negotiate ({len(slightly_high_items)} items)\n"
        for item in slightly_high_items[:3]:  # Show top 3
            summary += f"• **{item.item_name}**: ${item.quoted_price:,.2f} "
            summary += f"(fair range: ${item.fair_price_low:,.0f}-${item.fair_price_high:,.0f})\n"
        summary += "\n"
    
    if unknown_items:
        summary += f"### ℹ Unknown Items ({len(unknown_items)} items)\n"
        summary += "These items don't match our database. Get additional quotes for comparison.\n\n"
    
    # Add regional context
    summary += f"**Regional Context:** This analysis uses {region_name.replace('_', ' ').title()} pricing. "
    summary += f"Costs vary significantly by location.\n\n"
    
    # Add recommendation
    summary += f"### Recommendation\n{recommendation}\n\n"
    
    # Add specific advice for project type
    summary += f"**{project_type.replace('_', ' ').title()} Notes:** "
    
    project_specific_advice = {
        "roof_replacement": "Roofing is competitive. Get 3+ quotes. Beware contractors pushing unnecessary repairs or premium materials.",
        "kitchen_remodel": "Kitchens vary wildly by material choices. Ensure you're comparing apples to apples on cabinet quality, countertop materials, and appliances.",
        "bathroom_remodel": "Tile work labor is often where markup hides. Get itemized breakdown of tile cost vs. installation.",
        "hvac_replacement": "Equipment costs are somewhat fixed. Watch for unnecessary ductwork replacement claims and oversized equipment.",
        "plumbing_repair": "Plumbing has high emergency premiums. If not a true emergency, get daytime rates. Material markup is common.",
        "electrical_work": "Licensed electricians command fair rates. Watch for per-outlet charges >$200 and unnecessary panel upgrades.",
        "deck_building": "Material choice drives cost. Pressure-treated vs. composite is a huge price difference. Labor should be consistent.",
        "painting_interior": "Very competitive field. Get 3+ quotes. Material markup and unnecessary prep are common upsells.",
        "siding_replacement": "Material choice is key. Installation labor should be fairly consistent per sq ft across contractors.",
        "window_replacement": "Financing gimmicks are common. Pay attention to window quality (vinyl vs. wood-clad) and installation details.",
    }
    
    summary += project_specific_advice.get(project_type, "Get multiple quotes and compare line-by-line.")
    
    return summary
