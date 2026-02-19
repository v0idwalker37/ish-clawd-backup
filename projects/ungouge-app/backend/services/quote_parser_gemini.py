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
   - Quoted price (dollar amount)
   - Quantity (number of units - default 1 if not shown)
   - Unit (e.g., "square", "linear_foot", "item", "hour", "sqft")

CRITICAL RULES:
- Extract EVERY individual work/material line item you can see
- Pay close attention to quantities and units (squares, linear feet, etc.)
- Convert all prices to numbers (remove $, commas)
- Do NOT include totals, subtotals, grand totals, tax lines, or summary lines as line items — only actual work/material items
- IMPORTANT: Some quotes embed the price in the description text (e.g., "Interior painting - $3,800" or "Fire mantle installation ($2,500)"). If a line item has $0 or no price column but the description mentions a dollar amount, extract that dollar amount as the quoted_price.
- Every line item should have a non-zero price unless the work is explicitly bundled/included at no charge. If you see $0, double-check the description for an embedded price.
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
    
    # Calculate total if not present
    if "total" not in parsed_data or not parsed_data["total"]:
        parsed_data["total"] = sum(
            item["quoted_price"] * item.get("quantity", 1) 
            for item in parsed_data["line_items"]
        )
    
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
   - Quoted price (dollar amount)
   - Quantity (number of units - default 1 if not shown)
   - Unit (e.g., "square", "linear_foot", "item", "hour", "sqft")

CRITICAL RULES:
- This is ONE quote split across {len(all_images)} pages - extract EVERYTHING
- Extract EVERY individual work/material line item you can see across ALL pages
- Pay close attention to quantities and units (squares, linear feet, etc.)
- Convert all prices to numbers (remove $, commas)
- Do NOT include totals, subtotals, grand totals, tax lines, or summary lines as line items — only actual work/material items
- IMPORTANT: Some quotes embed the price in the description text (e.g., "Interior painting - $3,800" or "Fire mantle installation ($2,500)"). If a line item has $0 or no price column but the description mentions a dollar amount, extract that dollar amount as the quoted_price.
- Every line item should have a non-zero price unless the work is explicitly bundled/included at no charge
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
    
    # Calculate total
    parsed_data["total"] = sum(
        item["quoted_price"] * item.get("quantity", 1) 
        for item in parsed_data["line_items"]
    )
    
    print(f"Successfully parsed {len(all_images)} pages → {len(parsed_data['line_items'])} line items")
    
    return parsed_data
