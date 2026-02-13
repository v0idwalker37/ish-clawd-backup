"""Classify downloaded files: is this actually a contractor quote?

Uses Claude Vision API for image classification (~$0.002 per image).
Falls back to heuristics if API is unavailable.
"""

import os
import base64
import logging
import mimetypes
from typing import Tuple

from ..config import CLAUDE_API_KEY, IMAGE_EXTENSIONS
from ..models import ClassificationResult

logger = logging.getLogger(__name__)

# Claude classification prompt
CLASSIFICATION_PROMPT = """Look at this image and determine if it is a contractor quote, estimate, or bid for home improvement/construction work.

A contractor quote typically includes:
- A contractor/company name
- Line items for work to be done
- Dollar amounts for labor/materials
- Project description (roofing, plumbing, HVAC, remodel, etc.)
- Sometimes a customer name/address

Respond with EXACTLY one of:
- YES — This is clearly a contractor quote, estimate, or bid
- NO — This is NOT a contractor quote (it's a receipt, screenshot, meme, random photo, etc.)
- UNSURE — It might be a quote but you can't tell for sure

Just respond with the single word: YES, NO, or UNSURE"""

# Cache to avoid re-classifying
_classification_cache = {}


def classify_file(filepath: str, use_api: bool = True) -> Tuple[ClassificationResult, str]:
    """Classify whether a file is a contractor quote.
    
    Returns:
        (ClassificationResult, reason_string)
    """
    if not os.path.exists(filepath):
        return ClassificationResult.NOT_QUOTE, "file_not_found"

    # Check cache
    if filepath in _classification_cache:
        return _classification_cache[filepath]

    ext = os.path.splitext(filepath)[1].lower()

    # PDFs: assume they're quotes if they passed our download filters
    # (we only download from quote-related contexts)
    if ext == ".pdf":
        result = (ClassificationResult.QUOTE, "pdf_from_quote_context")
        _classification_cache[filepath] = result
        return result

    # DOCX: same assumption
    if ext in (".docx", ".doc"):
        result = (ClassificationResult.QUOTE, "document_from_quote_context")
        _classification_cache[filepath] = result
        return result

    # Images: use Claude Vision API if available
    if ext in IMAGE_EXTENSIONS:
        if use_api and CLAUDE_API_KEY:
            return classify_image_with_claude(filepath)
        else:
            # Heuristic fallback: assume quote if from quote context
            result = (ClassificationResult.UNSURE, "no_api_available")
            _classification_cache[filepath] = result
            return result

    return ClassificationResult.NOT_QUOTE, "unknown_file_type"


def classify_image_with_claude(filepath: str) -> Tuple[ClassificationResult, str]:
    """Use Claude Vision API to classify an image."""
    try:
        import anthropic
    except ImportError:
        logger.warning("anthropic package not installed, skipping classification")
        return ClassificationResult.UNSURE, "anthropic_not_installed"

    try:
        # Read and encode image
        with open(filepath, "rb") as f:
            image_data = f.read()

        # Determine media type
        ext = os.path.splitext(filepath)[1].lower()
        media_type_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        media_type = media_type_map.get(ext, "image/jpeg")

        # Encode to base64
        b64_data = base64.b64encode(image_data).decode("utf-8")

        # Call Claude API
        client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=10,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": b64_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": CLASSIFICATION_PROMPT,
                        },
                    ],
                }
            ],
        )

        answer = response.content[0].text.strip().upper()
        
        if "YES" in answer:
            result = (ClassificationResult.QUOTE, "claude_confirmed")
        elif "NO" in answer:
            result = (ClassificationResult.NOT_QUOTE, "claude_rejected")
        else:
            result = (ClassificationResult.UNSURE, "claude_unsure")

        _classification_cache[filepath] = result
        logger.debug(f"Classified {os.path.basename(filepath)}: {result[0].value} ({result[1]})")
        return result

    except Exception as e:
        logger.error(f"Classification API error for {filepath}: {e}")
        result = (ClassificationResult.UNSURE, f"api_error: {str(e)[:100]}")
        _classification_cache[filepath] = result
        return result


def classify_batch(filepaths: list, use_api: bool = True) -> dict:
    """Classify multiple files. Returns dict of filepath -> (result, reason)."""
    results = {}
    for fp in filepaths:
        results[fp] = classify_file(fp, use_api=use_api)
    return results
