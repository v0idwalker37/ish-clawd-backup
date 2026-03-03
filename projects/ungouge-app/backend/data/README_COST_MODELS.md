# GougeAlert Cost Models - Implementation Summary

## Overview
This directory contains comprehensive, realistic cost models for the GougeAlert quote analysis engine. The models are based on 2024-2025 market data and industry standards.

## Files Created/Updated

### 1. `project_cost_models.json` (NEW)
**Purpose:** Comprehensive cost database with detailed breakdowns for 10 major project types

**Project Types Covered:**
1. **Roof Replacement** - Asphalt shingles, per square (100 sq ft)
   - Materials: shingles, underlayment, flashing, ridge caps, drip edge
   - Labor: tear-off, installation, cleanup
   - Typical ranges: $350-650/square
   - Regional multipliers applied

2. **Kitchen Remodel** - Small/Medium/Large
   - Cabinets (stock/semi-custom/custom)
   - Countertops (laminate/granite/quartz/marble)
   - Backsplash, flooring, appliances
   - Plumbing, electrical, permits
   - Ranges: $15k-120k depending on size and finishes

3. **Bathroom Remodel** - Half bath to master bath
   - Tile work (floor and wall)
   - Fixtures (vanity, toilet, tub, shower)
   - Plumbing, electrical, ventilation
   - Ranges: $3k-75k depending on size

4. **HVAC Replacement** - AC, furnace, or complete systems
   - Equipment costs by tonnage and BTU
   - Installation labor
   - Ductwork, thermostats, permits
   - Typical home sizes: 1500-3000 sq ft

5. **Plumbing Repair** - Common repairs
   - Water heater (tank and tankless)
   - Pipe repairs (copper and PEX)
   - Drain cleaning, sewer line work
   - Fixture repairs and replacements

6. **Electrical Work** - Panel upgrades, rewiring, outlets
   - Panel upgrades (100A to 200A)
   - Whole house rewiring
   - Outlets, switches, lighting
   - Major appliance circuits

7. **Deck Building** - Per square foot by material
   - Pressure-treated pine: $25-50/sq ft
   - Cedar: $35-60/sq ft  
   - Composite (basic): $40-75/sq ft
   - Composite (premium): $55-95/sq ft

8. **Painting Interior** - Per room and per sq ft
   - Labor rates and material costs
   - Prep work included
   - Additional services (trim, cabinets, wallpaper removal)

9. **Siding Replacement** - Per sq ft by material
   - Vinyl: $6-10/sq ft
   - Fiber cement: $10-16/sq ft
   - Wood cedar: $12-20/sq ft
   - Engineered wood: $7.50-12/sq ft

10. **Window Replacement** - Per window by type
    - Double-hung, casement, picture, sliding
    - Vinyl budget to wood-clad premium
    - Typical ranges: $450-1200 per window installed

**Key Features:**
- **Regional Multipliers:** 7 US regions with multipliers (0.88x to 1.38x)
  - Northeast: 1.20x
  - Southeast: 0.90x
  - Pacific (CA): 1.38x
  - etc.
  
- **Common Upsells:** Red flags for each project type
  - Example: "Premium shingles when standard would work"
  - Example: "Unnecessary ductwork replacement"
  
- **Red Flags:** Specific warning signs per project
  - Example: "Tear-off >$75/square (should be $30-50)"
  - Example: "Simple drain snake >$300"

### 2. `sample_bls_rates.json` (UPDATED)
**Purpose:** Updated BLS wage data with regional variations for 2024-2025

**Occupation Codes Included:**
- 47-2031: Carpenters ($28.50/hr median)
- 47-2111: Electricians ($32.40/hr median)
- 47-2152: Plumbers ($31.20/hr median)
- 49-9021: HVAC Techs ($29.80/hr median)
- 47-2141: Painters ($23.60/hr median)
- 47-2181: Roofers ($25.90/hr median)
- Plus 14 more trades with 25th/75th percentiles

**Regional Adjustments:**
- Northeast: 1.25x (union presence, high COL)
- Southeast: 0.88x (right-to-work states, lower COL)
- California: 1.38x (highest in nation)
- Metro-specific multipliers (e.g., SF Bay Area: 1.65x)

**Additional Data:**
- Contractor markup standards (20-35%)
- Overhead breakdown (insurance, tools, marketing)
- Overtime and emergency rate guidelines
- Trade aliases for fuzzy matching

### 3. `analyzer.py` (COMPLETELY REWRITTEN)
**Purpose:** Sophisticated cost analysis engine using the new cost models

**Key Improvements:**

#### Fuzzy Matching
- Uses `SequenceMatcher` to match line items to cost model categories
- Handles variations in contractor terminology
- Confidence scoring (threshold: 0.6)
- Falls back to generic estimation for unknown items

#### Regional Intelligence
- ZIP code-based region detection (first digit)
- Automatic regional multiplier application
- Metro-area specific adjustments

#### Smart Quantity Detection
- Extracts quantities from item descriptions
- Recognizes units: sq ft, linear ft, roofing squares, gallons, hours
- Pattern matching with regex

#### Realistic Pricing
- Loads detailed cost models from JSON
- Matches to materials, labor, components sections
- Calculates fair price ranges per category
- Applies industry-standard markups (20-35%)

#### Assessment Categories
- **fair:** ≤10% over fair high price
- **slightly_high:** 10-25% over (negotiate territory)
- **high:** 25-50% over (get more quotes)
- **gouging:** >50% over (reject contractor)

#### Enhanced Explanations
- Specific, actionable feedback per line item
- References actual cost data ("Typical cost: $X-Y")
- Shows percentage over fair price
- Includes red flags from cost models
- Project-specific advice

#### Overall Assessment
- Comprehensive summary with categories
- Breaks down major issues vs. negotiable items
- Lists unknown items needing additional quotes
- Regional context explanation
- Project-specific recommendations

**Example Output:**
```
## Overall Assessment: HIGH

⚠⚠ This quote is higher than typical market rates for your area.

**Total Quoted:** $8,500.00
**Fair Range:** $5,200.00 - $6,500.00
**Amount Over Fair Price:** $2,000.00 (31%)

### 🚨 Major Issues (2 items)
• **Roof tear-off and disposal**: $1,800.00 (should be $600-900, 100% over)
• **Ridge cap installation**: $650.00 (should be $350-450, 44% over)

### Recommendation
DO NOT accept this quote without getting at least 2-3 competing quotes...
```

## How It Works

### Flow:
1. **Quote Submitted** → Contains project type, location (ZIP), line items
2. **Regional Detection** → ZIP code → Region → Multiplier (e.g., 1.20x)
3. **Line Item Analysis:**
   - Extract quantity and unit from description
   - Fuzzy match to cost model category
   - Calculate fair price using cost model data
   - Apply regional multiplier
   - Determine assessment category
   - Generate specific explanation
4. **Overall Assessment:**
   - Aggregate all line items
   - Calculate total vs. fair range
   - Flag problematic items
   - Provide actionable recommendations

### Example Matching:
**User Input:** "Remove old shingles and dispose - 20 squares"
- **Fuzzy Match:** `materials.tear_off` (confidence: 0.85)
- **Cost Data:** $30-50/square (labor + disposal)
- **Regional Mult:** 1.20x (Northeast)
- **Calculation:** 20 squares × $30-50 × 1.20 = $720-1200
- **Assessment:** If quoted $1800 → "high" (50% over)

## Data Sources
- **BLS OES Survey 2024-2025:** Occupational wage data
- **Industry Standards:** RSMeans, HomeAdvisor, contractor associations
- **Market Research:** Regional pricing studies, contractor surveys
- **Red Flags Database:** Common contractor tactics and upsells

## Maintenance
- **Quarterly Updates:** Adjust for material price fluctuations
- **Annual Reviews:** Update BLS rates, regional multipliers
- **Feedback Loop:** Incorporate user-reported actual costs
- **A/B Testing:** Compare model predictions vs. actual quotes received

## Usage in Backend

```python
from services.analyzer import analyze_quote

# Quote submission includes:
# - project_type: "roof_replacement"
# - location: "02115" (ZIP code)
# - line_items: [{"item_name": "...", "quoted_price": 1000, "quantity": 1}, ...]

report = await analyze_quote(quote, db)

# Returns Report with:
# - total_quoted, total_fair_low, total_fair_high
# - overall_assessment (markdown formatted)
# - line_items with individual assessments
```

## Future Enhancements
1. **Machine Learning:** Train model on actual quote data to improve matching
2. **Real-time Material Prices:** API integration with Home Depot, lumber yards
3. **Contractor Database:** Track historical quotes by contractor for pattern detection
4. **Negotiation Scripts:** Generate specific talking points for price negotiation
5. **Photo Analysis:** Use CV to estimate quantities from project photos
6. **Seasonal Adjustments:** Factor in busy/slow seasons for trades
7. **Supply Chain Events:** Adjust for lumber shortages, tariffs, etc.

## Testing Recommendations
1. **Unit Tests:** Test fuzzy matching with various contractor terminologies
2. **Integration Tests:** Full quote analysis with known good/bad quotes
3. **Regional Tests:** Verify multipliers produce realistic results per region
4. **Edge Cases:** Unknown items, custom work, unusual quantities
5. **Performance:** Ensure JSON loading is cached, analysis is fast (<500ms)

## Red Flags for QA
If the analyzer produces these results, investigate:
- Fair price range wider than 100% (too much uncertainty)
- Regional multiplier >2x or <0.5x (data error)
- All items marked "unknown" (matching failure)
- Assessment "fair" for quote 50%+ over market (logic error)
- Negative fair prices (calculation error)

---

**Last Updated:** 2024-12-15  
**Version:** 1.0  
**Authors:** GougeAlert Development Team
