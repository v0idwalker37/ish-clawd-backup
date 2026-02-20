"""
Quote parsing service - Gemini Vision Edition
Uses Google Gemini 2.0 Flash for superior document extraction accuracy

Migration from OpenAI GPT-4o due to better accuracy in line item extraction
"""
import os
import io
import re
import base64
import json
from typing import Dict, List, Optional
from PIL import Image
import PyPDF2

# Will be initialized when API key is available
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not installed. Run: pip install google-generativeai")


def init_gemini():
    """Initialize Gemini with API key from environment"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    if not GEMINI_AVAILABLE:
        raise ValueError("google-generativeai package not installed")
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.0-flash')


def convert_pdf_to_images(file_bytes: bytes) -> List[Image.Image]:
    """
    Convert PDF pages to images for Gemini vision processing
    
    Note: For production, consider using pdf2image library for better quality
    This is a simple fallback that extracts images from PDF
    """
    try:
        from pdf2image import convert_from_bytes
        images = convert_from_bytes(file_bytes)
        return images
    except ImportError:
        # Fallback: just return a placeholder
        # In production, you'll want pdf2image installed
        raise ValueError("pdf2image not installed. Run: pip install pdf2image")


def parse_quote_with_gemini_vision(file_bytes: bytes, filename: str) -> Dict:
    """
    Use Gemini Vision to directly parse quote from image or PDF
    
    This is the primary method - much more accurate than OCR + text parsing
    
    Returns structured quote data matching the expected format
    """
    
    model = init_gemini()
    
    # Prepare the image(s) for Gemini
    if filename.lower().endswith('.pdf'):
        # Convert PDF to images
        try:
            images = convert_pdf_to_images(file_bytes)
        except:
            # Fallback to text extraction if pdf2image not available
            return parse_quote_with_gemini_text(file_bytes, filename)
    else:
        # Direct image processing
        images = [Image.open(io.BytesIO(file_bytes))]
    
    # Build the prompt
    prompt = """You are an expert contractor quote analyzer. Extract ALL information from this contractor quote document.

Extract the following information:
1. Project type (e.g., "roof_replacement", "kitchen_remodel", "deck_building", "concrete_work", "hvac_installation", etc.)
2. Location (city, state, ZIP code if visible)
3. Contractor name/company
4. Date (if visible)
5. ALL line items with complete details:
   - Item name (what the work/material is)
   - Description (any additional details)
   - **Quoted price (PRICE PER UNIT ONLY - e.g., $94.13/hour, $15.50/sqft, NOT the line total)**
   - Quantity (number of units - default 1 if not shown)
   - Unit (e.g., "square", "linear_foot", "item", "hour", "sqft")

CRITICAL RULES:
- Extract EVERY individual work/material line item you can see
- Pay close attention to quantities and units (squares, linear feet, etc.)
- Convert all prices to numbers (remove $, commas)
- Do NOT include totals, subtotals, grand totals, tax lines, or summary lines as line items — only actual work/material items
- **CRITICAL: quoted_price MUST be the PRICE PER UNIT, NEVER the line total.**
  - Example: "60 hours @ $94.13/hour = $5,647.80" → extract 94.13 as quoted_price, NOT 5647.80
  - If you see "Carpenter - $5,647.80 for 60 hours" → calculate unit price: 5647.80 / 60 = 94.13
  - If only a line total is shown with quantity, divide to get unit price
- IMPORTANT: Some quotes embed the price in the description text (e.g., "Interior painting - $3,800" or "Fire mantle installation ($2,500)"). If a line item has $0 or no price column but the description mentions a dollar amount, extract that dollar amount as the quoted_price.
- If a line item has NO price shown anywhere (not in a column, not in the description text, nowhere), set quoted_price to 0. Do NOT invent or estimate prices. Only extract prices that are explicitly stated in the document.
- Some quotes only provide a grand total with no per-item pricing. In that case, extract all work items with quoted_price: 0 and set the total to the stated grand total.
- Be precise with numbers - accuracy is critical
- If something is unclear, make your best inference but note it in description
- Look for fine print and detailed breakdowns

Return ONLY valid JSON in this exact format:
{
  "project_type": "roof_replacement",
  "location": "Austin, TX",
  "contractor_name": "ABC Roofing Co",
  "date": "2024-01-15",
  "line_items": [
    {
      "item_name": "Asphalt shingles - Architectural 30yr",
      "description": "GAF Timberline HDZ in Weathered Wood",
      "quoted_price": 3500.00,
      "quantity": 20,
      "unit": "square"
    },
    {
      "item_name": "Ice & water shield",
      "description": "Underlayment for eaves and valleys",
      "quoted_price": 450.00,
      "quantity": 3,
      "unit": "roll"
    }
  ],
  "total": 3950.00,
  "notes": "Any additional notes or observations"
}

Be thorough and accurate. Extract everything visible in the document."""

    try:
        # Send to Gemini with the image(s)
        if len(images) == 1:
            response = model.generate_content([prompt, images[0]])
        else:
            # Multiple pages - process together
            content = [prompt] + images
            response = model.generate_content(content)
        
        result_text = response.text.strip()
        
        # Clean up markdown code blocks if present
        if result_text.startswith("```"):
            result_text = re.sub(r'```json\n|```\n|```', '', result_text).strip()
        
        # Parse JSON
        parsed_data = json.loads(result_text)
        
        return parsed_data
    
    except Exception as e:
        raise ValueError(f"Gemini vision parsing failed: {str(e)}")


def parse_quote_with_gemini_text(file_bytes: bytes, filename: str) -> Dict:
    """
    Fallback: Extract text first, then parse with Gemini
    
    Less accurate than vision, but works when images can't be processed
    """
    
    model = init_gemini()
    
    # Extract text
    if filename.lower().endswith('.pdf'):
        pdf_file = io.BytesIO(file_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = "\n".join([page.extract_text() for page in pdf_reader.pages])
    else:
        # Would need OCR here - for now, raise error
        raise ValueError("Text fallback requires PDF. Use vision mode for images.")
    
    prompt = f"""You are an expert contractor quote analyzer. Parse this contractor quote text into structured data.

Quote text:
{text}

Extract all information following the same rules as the vision prompt.
Return ONLY valid JSON with: project_type, location, contractor_name, date, line_items, total, notes."""

    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        if result_text.startswith("```"):
            result_text = re.sub(r'```json\n|```\n|```', '', result_text).strip()
        
        return json.loads(result_text)
    
    except Exception as e:
        raise ValueError(f"Gemini text parsing failed: {str(e)}")


def detect_total_only_quote(parsed_data: Dict) -> bool:
    """
    Detect if a quote is total-only (no itemized costs).
    
    Returns True if:
    - Only 1-2 line items
    - All/most line items have $0 prices
    - One item matches the total exactly (probably "Project Total" line)
    - Sum of line items is far from total (Gemini may have estimated prices)
    """
    items = parsed_data.get("line_items", [])
    total = parsed_data.get("total", 0)
    
    if not items or total <= 0:
        return False
    
    # Very few items - likely total-only
    if len(items) <= 2:
        return True
    
    # Check if all/most items are $0
    non_zero_items = [i for i in items if i.get("quoted_price", 0) > 0]
    if len(non_zero_items) <= 1:
        return True
    
    # Check if one item matches total (probably "Project Total" line)
    for item in items:
        item_total = item.get("quoted_price", 0) * item.get("quantity", 1)
        if abs(item_total - total) < 1:
            return True
    
    # NEW: Check if many items exist but their sum is way off from total
    # This catches cases where Gemini invented prices despite instructions
    calculated_sum = sum(
        item.get("quoted_price", 0) * item.get("quantity", 1)
        for item in items
    )
    if calculated_sum > 0 and total > 0:
        ratio = calculated_sum / total
        # If sum of items is very different from total (off by >50%), likely total-only
        # with Gemini having made up numbers
        if ratio < 0.5 or ratio > 1.5:
            print(f"Total-only detected by sum mismatch: items sum ${calculated_sum:,.2f} vs total ${total:,.2f} (ratio {ratio:.2f})")
            return True
    
    # NEW: Check if all prices look suspiciously round (Gemini estimation artifacts)
    # Real quotes have varied prices; AI-estimated ones tend to be round numbers
    if len(non_zero_items) >= 5:
        round_count = sum(
            1 for i in non_zero_items
            if i.get("quoted_price", 0) % 100 == 0 or i.get("quoted_price", 0) % 50 == 0
        )
        if round_count / len(non_zero_items) > 0.8:
            print(f"Total-only detected by round-number heuristic: {round_count}/{len(non_zero_items)} items have round prices")
            return True
    
    return False


async def generate_estimated_breakdown(
    project_type: str,
    location: str,
    descriptions: List[str],
    total: float,
) -> Dict:
    """
    Use Gemini to estimate line item costs for total-only quotes.
    
    Based on:
    - Project type and location (regional pricing)
    - Description text from the quote
    - Industry standard percentages
    - Total budget
    
    Returns estimated line items with confidence levels.
    """
    
    model = init_gemini()
    
    # Build the estimation prompt
    prompt = f"""You are a construction cost estimator. A contractor provided a quote with ONLY a total price and no itemized costs.

Project: {project_type}
Location: {location}
Total Budget: ${total:,.2f}

Work items mentioned in the quote:
{chr(10).join(f"- {desc}" for desc in descriptions if desc)}

Your task: Estimate what each item likely costs, based on:
1. Typical cost percentages for {project_type} projects
2. Regional pricing in {location}
3. Industry standards and Bureau of Labor Statistics data
4. Typical material/labor splits

General guidelines for {project_type}:
- Materials: Usually 40-50% of total
- Labor: Usually 35-45% of total  
- Overhead/profit: Usually 10-20% of total

Provide conservative estimates. If uncertain, mark confidence as "low".

Return JSON with estimated line items that sum to the total:
{{
  "line_items": [
    {{
      "item_name": "...",
      "description": "...",
      "quoted_price": 0.00,
      "quantity": 1,
      "unit": "item",
      "estimated_total": 0.00,
      "confidence": "high|medium|low",
      "reasoning": "Based on typical X% of total for this item type in {location}"
    }}
  ],
  "methodology": "Brief explanation of estimation approach",
  "overall_confidence": "high|medium|low"
}}

IMPORTANT RULES:
- All estimated_total values MUST sum exactly to ${total:,.2f}
- quoted_price should be the per-unit price (estimated_total / quantity)
- Show at most 15 line items (combine similar items if needed)
- Sort by estimated_total descending (most expensive items first)
- Be realistic - don't wildly over-estimate or under-estimate
- Mark confidence honestly (high/medium/low) based on how standard the item is"""

    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Clean up markdown code blocks if present
        if result_text.startswith("```"):
            result_text = re.sub(r'```json\n|```\n|```', '', result_text).strip()
        
        # Parse JSON
        estimation_data = json.loads(result_text)
        
        # Validate that totals sum correctly (within $1 tolerance)
        estimated_sum = sum(item.get("estimated_total", 0) for item in estimation_data.get("line_items", []))
        if abs(estimated_sum - total) > 1:
            # Adjust proportionally to match total exactly
            ratio = total / estimated_sum if estimated_sum > 0 else 1
            for item in estimation_data["line_items"]:
                item["estimated_total"] = round(item["estimated_total"] * ratio, 2)
                item["quoted_price"] = round(item["estimated_total"] / item.get("quantity", 1), 2)
        
        return estimation_data
    
    except Exception as e:
        raise ValueError(f"Estimation generation failed: {str(e)}")


async def process_quote_file(file_bytes: bytes, filename: str) -> Dict:
    """
    Main entry point - process uploaded file with Gemini vision
    
    Args:
        file_bytes: Raw file bytes
        filename: Original filename (used to determine file type)
    
    Returns:
        Parsed quote data dictionary
    """
    
    # Try vision parsing first (most accurate)
    try:
        parsed_data = parse_quote_with_gemini_vision(file_bytes, filename)
    except Exception as e:
        # Fallback to text parsing if vision fails
        print(f"Vision parsing failed: {e}. Trying text fallback...")
        parsed_data = parse_quote_with_gemini_text(file_bytes, filename)
    
    # Validate structure
    if not parsed_data.get("line_items"):
        raise ValueError("No line items found in quote. Please verify the file is a contractor quote.")
    
    # Filter out total/subtotal/tax line items that the AI may have included
    TOTAL_PATTERNS = re.compile(
        r'^(total|subtotal|sub-total|sub total|grand total|balance due|amount due|'
        r'invoice total|project total|estimate total|quote total|net total|'
        r'sales tax|tax|vat|gst|hst)$',
        re.IGNORECASE,
    )
    parsed_data["line_items"] = [
        item for item in parsed_data["line_items"]
        if not TOTAL_PATTERNS.match((item.get("item_name") or "").strip())
    ]

    # Clean and validate line items
    for item in parsed_data["line_items"]:
        # Ensure required fields
        if "item_name" not in item or not item["item_name"]:
            item["item_name"] = "Unknown item"
        if "quoted_price" not in item:
            item["quoted_price"] = 0.0
        if "quantity" not in item:
            item["quantity"] = 1
        if "unit" not in item:
            item["unit"] = "item"
        if "description" not in item:
            item["description"] = ""
        
        # Type conversion with validation
        try:
            item["quoted_price"] = float(item["quoted_price"])
        except:
            item["quoted_price"] = 0.0
        
        # Safety net: if price is $0, check description for embedded dollar amounts
        if item["quoted_price"] == 0 and item.get("description"):
            price_match = re.search(r'\$\s*([\d,]+(?:\.\d{2})?)', item["description"])
            if price_match:
                try:
                    extracted = float(price_match.group(1).replace(",", ""))
                    if extracted > 0:
                        item["quoted_price"] = extracted
                except (ValueError, AttributeError):
                    pass
        
        # Also check item_name for embedded prices (e.g., "Painting - $3,800")
        if item["quoted_price"] == 0 and item.get("item_name"):
            price_match = re.search(r'\$\s*([\d,]+(?:\.\d{2})?)', item["item_name"])
            if price_match:
                try:
                    extracted = float(price_match.group(1).replace(",", ""))
                    if extracted > 0:
                        item["quoted_price"] = extracted
                        # Clean the price out of the name
                        item["item_name"] = re.sub(r'\s*[-–—]\s*\$[\d,]+(?:\.\d{2})?', '', item["item_name"]).strip()
                        item["item_name"] = re.sub(r'\s*\(\$[\d,]+(?:\.\d{2})?\)', '', item["item_name"]).strip()
                except (ValueError, AttributeError):
                    pass
        
        try:
            item["quantity"] = int(item["quantity"]) if item["quantity"] else 1
        except:
            item["quantity"] = 1
        
        # FIX: Detect if quoted_price is actually a line total (quantity > 1 and price seems too high)
        # Heuristic: if quantity > 1 and price * quantity would be absurdly high, assume price IS the line total
        qty = item["quantity"]
        price = item["quoted_price"]
        if qty > 1 and price > 0:
            # If the "unit price" times quantity would give a line total > $1M, it's probably wrong
            calculated_total = price * qty
            if calculated_total > 1_000_000:  # Unlikely to have million-dollar line items
                # Price is probably the line total - divide to get unit price
                unit_price = price / qty
                if unit_price >= 0.01:  # Sanity check: unit price should be at least 1 cent
                    item["quoted_price"] = round(unit_price, 2)
                    print(f"Corrected {item['item_name']}: detected line total ${price:,.2f}, converted to unit price ${unit_price:,.2f}")
    
    # Calculate total if not present
    if "total" not in parsed_data or not parsed_data["total"]:
        parsed_data["total"] = sum(
            item["quoted_price"] * item.get("quantity", 1) 
            for item in parsed_data["line_items"]
        )
    
    # Check if this is a total-only quote (no itemized costs)
    if detect_total_only_quote(parsed_data):
        print("Detected total-only quote - generating estimated breakdown...")
        
        # Collect descriptions for estimation
        descriptions = [
            f"{item.get('item_name', '')} - {item.get('description', '')}"
            for item in parsed_data.get("line_items", [])
            if item.get("item_name") or item.get("description")
        ]
        
        # Generate AI estimation
        try:
            estimation = await generate_estimated_breakdown(
                project_type=parsed_data.get("project_type", "general_contracting"),
                location=parsed_data.get("location", "United States"),
                descriptions=descriptions,
                total=parsed_data.get("total", 0),
            )
            
            # Replace line items with estimated breakdown
            parsed_data["line_items"] = estimation["line_items"]
            parsed_data["is_estimated"] = True
            parsed_data["estimation_confidence"] = estimation.get("overall_confidence", "medium")
            parsed_data["estimation_methodology"] = estimation.get("methodology", "AI-estimated based on industry standards")
            
            print(f"Generated {len(estimation['line_items'])} estimated line items")
        
        except Exception as e:
            print(f"Estimation failed: {e}. Keeping original parse.")
            # Mark as estimated but keep original data
            parsed_data["is_estimated"] = True
            parsed_data["estimation_confidence"] = "low"
            parsed_data["estimation_methodology"] = f"Original parse retained (estimation failed: {str(e)})"
    else:
        # Not a total-only quote - standard itemized quote
        parsed_data["is_estimated"] = False
        parsed_data["estimation_confidence"] = None
        parsed_data["estimation_methodology"] = None
    
    return parsed_data


async def process_multiple_files(files_data: list) -> dict:
    """
    Process multiple files as a single quote (multi-page quotes).
    
    Args:
        files_data: List of dicts with keys: bytes, filename, content_type
    
    Returns:
        Parsed quote data dictionary combining all pages
    """
    model = init_gemini()
    
    # Collect all images from all files
    all_images = []
    
    for file_data in files_data:
        file_bytes = file_data["bytes"]
        filename = file_data["filename"]
        
        # Convert to images
        if filename.lower().endswith('.pdf'):
            # PDF -> multiple images
            try:
                images = convert_pdf_to_images(file_bytes)
                all_images.extend(images)
            except Exception as e:
                print(f"Failed to process PDF {filename}: {e}")
                raise ValueError(f"Failed to process PDF file {filename}")
        else:
            # Single image file
            try:
                img = Image.open(io.BytesIO(file_bytes))
                all_images.append(img)
            except Exception as e:
                print(f"Failed to process image {filename}: {e}")
                raise ValueError(f"Failed to process image file {filename}")
    
    if not all_images:
        raise ValueError("No valid images found in uploaded files")
    
    # Build the multi-page prompt
    prompt = f"""You are an expert contractor quote analyzer. The following {len(all_images)} images are ALL PAGES of a SINGLE contractor quote document.

Extract ALL information from across ALL pages:

1. Project type (e.g., "roof_replacement", "kitchen_remodel", "deck_building", "concrete_work", "hvac_installation", etc.)
2. Location (city, state, ZIP code if visible)
3. Contractor name/company
4. Date (if visible)
5. ALL line items from ALL pages with complete details:
   - Item name (what the work/material is)
   - Description (any additional details)
   - **Quoted price (PRICE PER UNIT ONLY - e.g., $94.13/hour, $15.50/sqft, NOT the line total)**
   - Quantity (number of units - default 1 if not shown)
   - Unit (e.g., "square", "linear_foot", "item", "hour", "sqft")

CRITICAL RULES:
- This is ONE quote split across {len(all_images)} pages - extract EVERYTHING
- Extract EVERY individual work/material line item you can see across ALL pages
- Pay close attention to quantities and units (squares, linear feet, etc.)
- Convert all prices to numbers (remove $, commas)
- Do NOT include totals, subtotals, grand totals, tax lines, or summary lines as line items — only actual work/material items
- **CRITICAL: quoted_price MUST be the PRICE PER UNIT, NEVER the line total.**
  - Example: "60 hours @ $94.13/hour = $5,647.80" → extract 94.13 as quoted_price, NOT 5647.80
  - If you see "Carpenter - $5,647.80 for 60 hours" → calculate unit price: 5647.80 / 60 = 94.13
  - If only a line total is shown with quantity, divide to get unit price
- IMPORTANT: Some quotes embed the price in the description text (e.g., "Interior painting - $3,800" or "Fire mantle installation ($2,500)"). If a line item has $0 or no price column but the description mentions a dollar amount, extract that dollar amount as the quoted_price.
- If a line item has NO price shown anywhere (not in a column, not in the description text, nowhere), set quoted_price to 0. Do NOT invent or estimate prices. Only extract prices that are explicitly stated in the document.
- Some quotes only provide a grand total with no per-item pricing. In that case, extract all work items with quoted_price: 0 and set the total to the stated grand total.
- Be precise with numbers - accuracy is critical
- Look for fine print and detailed breakdowns across all pages

Return ONLY valid JSON in this exact format:
{{
  "project_type": "kitchen_remodel",
  "location": "Austin, TX",
  "contractor_name": "ABC Construction",
  "date": "2024-01-15",
  "line_items": [
    {{
      "item_name": "Cabinet installation",
      "description": "Custom maple cabinets with soft-close hinges",
      "quoted_price": 8500.00,
      "quantity": 1,
      "unit": "item"
    }},
    {{
      "item_name": "Granite countertops",
      "description": "Level 3 granite, 3cm thickness",
      "quoted_price": 4200.00,
      "quantity": 45,
      "unit": "sqft"
    }}
  ]
}}"""
    
    # Generate content with all images
    try:
        response = model.generate_content([prompt] + all_images)
        response_text = response.text
    except Exception as e:
        print(f"Gemini API error processing {len(all_images)} images: {e}")
        raise ValueError(f"AI failed to process the quote images: {str(e)}")
    
    # Parse JSON response
    try:
        # Extract JSON from markdown code blocks if present
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
        else:
            json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
        
        parsed_data = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}\nRaw response: {response_text[:500]}")
        raise ValueError("AI returned invalid data format. Please try again or use a clearer image.")
    
    # Validate structure
    if not parsed_data.get("line_items"):
        raise ValueError(f"No line items found across {len(all_images)} pages. Please verify these are contractor quote documents.")
    
    # Filter out totals/subtotals
    TOTAL_PATTERNS = re.compile(
        r'^(total|subtotal|sub-total|sub total|grand total|balance due|amount due|'
        r'invoice total|project total|estimate total|quote total|net total|'
        r'sales tax|tax|vat|gst|hst)$',
        re.IGNORECASE,
    )
    
    original_count = len(parsed_data["line_items"])
    parsed_data["line_items"] = [
        item for item in parsed_data["line_items"]
        if not TOTAL_PATTERNS.match(item.get("item_name", ""))
    ]
    filtered_count = original_count - len(parsed_data["line_items"])
    if filtered_count > 0:
        print(f"Filtered out {filtered_count} total/subtotal lines")
    
    # Post-process line items
    for item in parsed_data["line_items"]:
        # Extract embedded prices from descriptions/names
        if item.get("quoted_price", 0) == 0:
            text_to_search = f"{item.get('item_name', '')} {item.get('description', '')}"
            price_match = re.search(r'\$?([\d,]+(?:\.\d{2})?)', text_to_search)
            if price_match:
                try:
                    extracted = float(price_match.group(1).replace(',', ''))
                    if extracted > 0:
                        item["quoted_price"] = extracted
                        item["item_name"] = re.sub(r'\s*[-–—]\s*\$[\d,]+(?:\.\d{2})?', '', item["item_name"]).strip()
                        item["item_name"] = re.sub(r'\s*\(\$[\d,]+(?:\.\d{2})?\)', '', item["item_name"]).strip()
                except (ValueError, AttributeError):
                    pass
        
        try:
            item["quantity"] = int(item["quantity"]) if item["quantity"] else 1
        except:
            item["quantity"] = 1
        
        # FIX: Detect if quoted_price is actually a line total (same as single-file parser)
        qty = item["quantity"]
        price = item["quoted_price"]
        if qty > 1 and price > 0:
            calculated_total = price * qty
            if calculated_total > 1_000_000:  # Unlikely to have million-dollar line items
                unit_price = price / qty
                if unit_price >= 0.01:
                    item["quoted_price"] = round(unit_price, 2)
                    print(f"Multi-file corrected {item['item_name']}: detected line total ${price:,.2f}, converted to unit price ${unit_price:,.2f}")
    
    # Calculate total
    parsed_data["total"] = sum(
        item["quoted_price"] * item.get("quantity", 1) 
        for item in parsed_data["line_items"]
    )
    
    print(f"Successfully parsed {len(all_images)} pages → {len(parsed_data['line_items'])} line items")
    
    # Check if this is a total-only quote (no itemized costs)
    if detect_total_only_quote(parsed_data):
        print("Detected total-only quote in multi-file upload - generating estimated breakdown...")
        
        # Collect descriptions for estimation
        descriptions = [
            f"{item.get('item_name', '')} - {item.get('description', '')}"
            for item in parsed_data.get("line_items", [])
            if item.get("item_name") or item.get("description")
        ]
        
        # Generate AI estimation
        try:
            estimation = await generate_estimated_breakdown(
                project_type=parsed_data.get("project_type", "general_contracting"),
                location=parsed_data.get("location", "United States"),
                descriptions=descriptions,
                total=parsed_data.get("total", 0),
            )
            
            # Replace line items with estimated breakdown
            parsed_data["line_items"] = estimation["line_items"]
            parsed_data["is_estimated"] = True
            parsed_data["estimation_confidence"] = estimation.get("overall_confidence", "medium")
            parsed_data["estimation_methodology"] = estimation.get("methodology", "AI-estimated based on industry standards")
            
            print(f"Generated {len(estimation['line_items'])} estimated line items")
        
        except Exception as e:
            print(f"Estimation failed: {e}. Keeping original parse.")
            # Mark as estimated but keep original data
            parsed_data["is_estimated"] = True
            parsed_data["estimation_confidence"] = "low"
            parsed_data["estimation_methodology"] = f"Original parse retained (estimation failed: {str(e)})"
    else:
        # Not a total-only quote - standard itemized quote
        parsed_data["is_estimated"] = False
        parsed_data["estimation_confidence"] = None
        parsed_data["estimation_methodology"] = None
    
    return parsed_data
