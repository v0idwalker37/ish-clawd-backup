"""
Quote parsing service - Extract structured data from contractor quotes (PDF/images)
Uses OCR + AI to automatically parse line items, pricing, and metadata
"""
import os
import io
import re
from typing import Dict, List, Optional
from PIL import Image
import pytesseract
import PyPDF2
from openai import OpenAI
from anthropic import Anthropic

from exceptions import (
    CorruptFileError,
    TextExtractionError,
    NoLineItemsFoundError,
    AIProcessingError,
    EmptyFileError,
)

# Initialize AI clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY")) if os.getenv("ANTHROPIC_API_KEY") else None


def extract_text_from_pdf(file_bytes: bytes, filename: str) -> str:
    """
    Extract text from PDF file.
    
    Raises:
        CorruptFileError, TextExtractionError
    """
    try:
        pdf_file = io.BytesIO(file_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        extracted = text.strip()
        
        # Check if we got meaningful content
        if len(extracted) < 20:
            raise TextExtractionError(filename)
        
        return extracted
        
    except PyPDF2.errors.PdfReadError as e:
        raise CorruptFileError(filename, f"PDF read error: {str(e)}")
    except Exception as e:
        if isinstance(e, (CorruptFileError, TextExtractionError)):
            raise
        raise CorruptFileError(filename, str(e))


def extract_text_from_image(file_bytes: bytes, filename: str) -> str:
    """
    Extract text from image using OCR (Tesseract).
    
    Raises:
        CorruptFileError, TextExtractionError
    """
    try:
        image = Image.open(io.BytesIO(file_bytes))
        
        # Convert to RGB if needed
        if image.mode not in ('RGB', 'L'):
            image = image.convert('RGB')
        
        # Check image isn't too small for OCR
        width, height = image.size
        if width < 100 or height < 100:
            raise TextExtractionError(filename)
        
        # Run OCR
        text = pytesseract.image_to_string(image)
        extracted = text.strip()
        
        # Check if we got meaningful content
        if len(extracted) < 20:
            raise TextExtractionError(filename)
        
        return extracted
        
    except pytesseract.TesseractError as e:
        raise AIProcessingError("OCR", f"Tesseract error: {str(e)}")
    except Exception as e:
        if isinstance(e, (CorruptFileError, TextExtractionError, AIProcessingError)):
            raise
        raise CorruptFileError(filename, str(e))


def parse_quote_with_ai(text: str) -> Dict:
    """
    Use AI to parse extracted text into structured quote data
    
    Returns:
        {
            "project_type": str,
            "location": str,
            "contractor_name": str,
            "line_items": [
                {
                    "item_name": str,
                    "description": str,
                    "quoted_price": float,
                    "quantity": int,
                    "unit": str
                }
            ]
        }
    """
    
    prompt = f"""You are a contractor quote parser. Extract structured data from this contractor quote.

Quote text:
{text}

Extract the following information:
1. Project type (e.g., "roof_replacement", "kitchen_remodel", "deck_building", etc.)
2. Location (city, state, or ZIP code if present)
3. Contractor name/company
4. Line items with:
   - Item name (what the work/material is)
   - Description (optional details)
   - Quoted price (dollar amount)
   - Quantity (default to 1 if not specified)
   - Unit (e.g., "square", "linear foot", "item", "hour")

Return ONLY valid JSON in this exact format:
{{
  "project_type": "roof_replacement",
  "location": "Austin, TX",
  "contractor_name": "ABC Roofing",
  "line_items": [
    {{
      "item_name": "Asphalt shingles",
      "description": "30-year architectural shingles",
      "quoted_price": 3500.00,
      "quantity": 20,
      "unit": "square"
    }}
  ]
}}

Important rules:
- If you can't find a field, use null or empty string
- Convert all prices to numbers (remove $ and commas)
- Be smart about inferring project type from line items
- Group similar items together
- Extract ALL line items you can find
- If quantity is not specified, use 1
- If unit is not specified, use "item"

Return ONLY the JSON, no explanation."""

    import json
    
    try:
        # Try OpenAI first (GPT-4)
        if openai_client:
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a precise data extraction assistant. Return only valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=2000,
                    timeout=30  # 30 second timeout
                )
                
                result_text = response.choices[0].message.content.strip()
                
                # Remove markdown code blocks if present
                if result_text.startswith("```"):
                    result_text = re.sub(r'```json\n|```\n|```', '', result_text).strip()
                
                return json.loads(result_text)
                
            except Exception as openai_error:
                # If OpenAI fails, try Anthropic as fallback
                if anthropic_client:
                    from services.logger import logger
                    logger.warning(f"OpenAI failed, trying Anthropic: {str(openai_error)}")
                else:
                    raise AIProcessingError("OpenAI", str(openai_error))
        
        # Fallback to Anthropic (Claude)
        if anthropic_client:
            try:
                response = anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=2000,
                    temperature=0.1,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    timeout=30  # 30 second timeout
                )
                
                result_text = response.content[0].text.strip()
                
                # Remove markdown code blocks if present
                if result_text.startswith("```"):
                    result_text = re.sub(r'```json\n|```\n|```', '', result_text).strip()
                
                return json.loads(result_text)
                
            except Exception as anthropic_error:
                raise AIProcessingError("Anthropic", str(anthropic_error))
        
        # No AI service available
        raise AIProcessingError(
            "Configuration",
            "No AI API key configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY in environment variables."
        )
    
    except json.JSONDecodeError as e:
        raise AIProcessingError(
            "JSON Parsing",
            f"AI returned invalid JSON: {str(e)}"
        )
    except Exception as e:
        if isinstance(e, AIProcessingError):
            raise
        raise AIProcessingError("Unknown", str(e))


async def process_quote_file(file_bytes: bytes, filename: str) -> Dict:
    """
    Main entry point - process uploaded file and return structured data.
    
    Args:
        file_bytes: Raw file bytes (already validated)
        filename: Original filename (used to determine file type)
    
    Returns:
        Parsed quote data dictionary
    
    Raises:
        TextExtractionError, NoLineItemsFoundError, AIProcessingError
    """
    
    # Determine file type and extract text
    if filename.lower().endswith('.pdf'):
        extracted_text = extract_text_from_pdf(file_bytes, filename)
    elif filename.lower().endswith(('.png', '.jpg', '.jpeg', '.heic')):
        extracted_text = extract_text_from_image(file_bytes, filename)
    else:
        # This should have been caught by validators, but just in case
        from exceptions import UnsupportedFileTypeError
        raise UnsupportedFileTypeError("unknown", filename)
    
    # Double-check we got meaningful text
    if not extracted_text or len(extracted_text) < 20:
        raise TextExtractionError(filename)
    
    # Parse with AI
    parsed_data = parse_quote_with_ai(extracted_text)
    
    # Validate structure
    if not parsed_data.get("line_items") or len(parsed_data["line_items"]) == 0:
        raise NoLineItemsFoundError(filename)
    
    # Clean and validate data
    for item in parsed_data["line_items"]:
        # Ensure all required fields exist
        if "item_name" not in item or not item["item_name"]:
            item["item_name"] = "Unknown item"
        if "quoted_price" not in item:
            item["quoted_price"] = 0.0
        if "quantity" not in item:
            item["quantity"] = 1
        if "unit" not in item:
            item["unit"] = "item"
        
        # Convert types safely
        try:
            price = float(item["quoted_price"])
            # Sanitize unrealistic values
            if price < 0:
                price = 0.0
            if price > 10_000_000:  # $10M line item seems unrealistic
                from services.logger import logger
                logger.warning(f"Extremely high line item price detected: ${price:,.2f}")
            item["quoted_price"] = price
        except (TypeError, ValueError):
            item["quoted_price"] = 0.0
        
        try:
            qty = int(item["quantity"])
            if qty < 1:
                qty = 1
            if qty > 100000:  # Sanity check
                qty = 1
            item["quantity"] = qty
        except (TypeError, ValueError):
            item["quantity"] = 1
    
    # Add metadata about parsing
    parsed_data["_metadata"] = {
        "text_length": len(extracted_text),
        "line_items_found": len(parsed_data["line_items"]),
        "source_file": filename,
    }
    
    return parsed_data
