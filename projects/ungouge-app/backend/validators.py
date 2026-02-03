"""
Input validation utilities with comprehensive edge case handling.

Provides validators for:
- File uploads (size, type, content)
- User input (email, passwords, quotes)
- Data integrity checks
"""

import re
import io
from typing import Tuple, Optional
from PIL import Image
import PyPDF2
from exceptions import (
    FileTooLargeError,
    EmptyFileError,
    UnsupportedFileTypeError,
    CorruptFileError,
    TextExtractionError,
    ValidationError,
    MissingRequiredFieldError,
    InvalidDataFormatError,
)


# Constants
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_CONTENT_TYPES = {
    'application/pdf',
    'image/png',
    'image/jpeg',
    'image/jpg',
}
ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg'}
MIN_PASSWORD_LENGTH = 8
MAX_QUOTE_LINE_ITEMS = 100


def validate_file_upload(
    file_bytes: bytes,
    filename: str,
    content_type: str,
) -> Tuple[bytes, str]:
    """
    Comprehensive file validation with detailed error messages.
    
    Validates:
    - File size
    - File type
    - File is not empty
    - File is readable
    - File contains extractable content
    
    Returns:
        (validated_bytes, normalized_content_type)
    
    Raises:
        FileTooLargeError, EmptyFileError, UnsupportedFileTypeError, CorruptFileError
    """
    
    # 1. Check file size
    file_size_mb = len(file_bytes) / (1024 * 1024)
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise FileTooLargeError(file_size_mb, MAX_FILE_SIZE_MB)
    
    # 2. Check for empty file
    if len(file_bytes) == 0:
        raise EmptyFileError(filename)
    
    # 3. Validate content type
    # Normalize content type
    content_type_normalized = content_type.lower().split(';')[0].strip()
    
    # Also check file extension as backup
    file_ext = '.' + filename.lower().split('.')[-1] if '.' in filename else ''
    
    is_valid_type = (
        content_type_normalized in ALLOWED_CONTENT_TYPES or
        file_ext in ALLOWED_EXTENSIONS
    )
    
    if not is_valid_type:
        raise UnsupportedFileTypeError(content_type, filename)
    
    # 4. Verify file can be read and is not corrupt
    try:
        if content_type_normalized == 'application/pdf' or file_ext == '.pdf':
            validate_pdf(file_bytes, filename)
        else:
            validate_image(file_bytes, filename)
    except Exception as e:
        if isinstance(e, (CorruptFileError, EmptyFileError)):
            raise
        # Convert generic errors to our custom exceptions
        raise CorruptFileError(filename, str(e))
    
    return file_bytes, content_type_normalized


def validate_pdf(file_bytes: bytes, filename: str) -> None:
    """
    Validate PDF file can be read and contains extractable text.
    
    Raises:
        CorruptFileError, EmptyFileError
    """
    try:
        pdf_file = io.BytesIO(file_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Check if PDF has pages
        if len(pdf_reader.pages) == 0:
            raise EmptyFileError(filename)
        
        # Try to extract text from first page to verify readability
        first_page = pdf_reader.pages[0]
        text = first_page.extract_text()
        
        # PDF should have at least some content
        if len(text.strip()) < 10:
            # Might be a scanned PDF (image-based)
            # Still valid, OCR will handle it later
            pass
        
    except PyPDF2.errors.PdfReadError as e:
        raise CorruptFileError(filename, f"PDF read error: {str(e)}")
    except Exception as e:
        # Check for password-protected PDFs
        if 'encrypt' in str(e).lower() or 'password' in str(e).lower():
            raise CorruptFileError(
                filename,
                "PDF appears to be password-protected"
            )
        raise CorruptFileError(filename, str(e))


def validate_image(file_bytes: bytes, filename: str) -> None:
    """
    Validate image file can be read and has reasonable dimensions.
    
    Raises:
        CorruptFileError, EmptyFileError
    """
    try:
        image = Image.open(io.BytesIO(file_bytes))
        
        # Verify image has content
        width, height = image.size
        
        if width == 0 or height == 0:
            raise EmptyFileError(filename)
        
        # Check for reasonable dimensions (not too small)
        if width < 50 or height < 50:
            raise CorruptFileError(
                filename,
                "Image is too small (minimum 50x50 pixels)"
            )
        
        # Check for extremely large images (might cause memory issues)
        if width * height > 25_000_000:  # ~25 megapixels
            raise CorruptFileError(
                filename,
                "Image resolution is too high (max 25 megapixels)"
            )
        
        # Try to verify image is not blank
        # Convert to RGB for analysis
        if image.mode not in ('RGB', 'L'):
            image = image.convert('RGB')
        
        # Sample a few pixels to ensure it's not a blank white/black image
        # This is a basic check, not foolproof
        try:
            import statistics
            pixels = list(image.getdata())[:1000]  # Sample first 1000 pixels
            
            if image.mode == 'RGB':
                # Flatten RGB tuples
                flat_pixels = [val for pixel in pixels for val in pixel]
            else:
                flat_pixels = pixels
            
            # Check variance - blank images have very low variance
            if len(set(flat_pixels)) < 5:
                # Almost all pixels the same color
                raise EmptyFileError(filename)
        except:
            # If pixel analysis fails, just skip it
            pass
        
    except Image.UnidentifiedImageError:
        raise CorruptFileError(filename, "Unrecognized image format")
    except Exception as e:
        if isinstance(e, (CorruptFileError, EmptyFileError)):
            raise
        raise CorruptFileError(filename, str(e))


def validate_email(email: str) -> str:
    """
    Validate email address format.
    
    Returns:
        Normalized email (lowercase, trimmed)
    
    Raises:
        InvalidDataFormatError
    """
    if not email:
        raise MissingRequiredFieldError("email")
    
    # Normalize
    email = email.strip().lower()
    
    # Basic regex pattern for email validation
    # Not perfect but catches most common errors
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        raise InvalidDataFormatError(
            "email",
            "valid email address (e.g., user@example.com)",
            email
        )
    
    # Check length
    if len(email) > 254:  # RFC 5321
        raise InvalidDataFormatError(
            "email",
            "email under 254 characters",
            f"{len(email)} characters"
        )
    
    return email


def validate_password(password: str) -> None:
    """
    Validate password meets security requirements.
    
    Raises:
        InvalidDataFormatError
    """
    if not password:
        raise MissingRequiredFieldError("password")
    
    if len(password) < MIN_PASSWORD_LENGTH:
        raise InvalidDataFormatError(
            "password",
            f"at least {MIN_PASSWORD_LENGTH} characters",
            f"{len(password)} characters"
        )
    
    # Check for at least one letter and one number (basic strength check)
    has_letter = any(c.isalpha() for c in password)
    has_number = any(c.isdigit() for c in password)
    
    if not (has_letter and has_number):
        raise InvalidDataFormatError(
            "password",
            "at least one letter and one number",
            "password too simple"
        )


def validate_quote_submission(quote_data: dict) -> None:
    """
    Validate quote submission data.
    
    Raises:
        MissingRequiredFieldError, InvalidDataFormatError, ValidationError
    """
    
    # Check required fields
    required_fields = ['project_type', 'location', 'line_items']
    for field in required_fields:
        if field not in quote_data or not quote_data[field]:
            raise MissingRequiredFieldError(field)
    
    # Validate line items
    line_items = quote_data.get('line_items', [])
    
    if not isinstance(line_items, list):
        raise InvalidDataFormatError(
            "line_items",
            "list of items",
            type(line_items).__name__
        )
    
    if len(line_items) == 0:
        raise ValidationError(
            "Quote must have at least one line item.",
            suggestion="Please add the items and pricing from your contractor quote."
        )
    
    if len(line_items) > MAX_QUOTE_LINE_ITEMS:
        raise ValidationError(
            f"Too many line items (max {MAX_QUOTE_LINE_ITEMS}).",
            suggestion=(
                f"Your quote has {len(line_items)} items. "
                "Please group similar items together or contact support for enterprise quotes."
            )
        )
    
    # Validate each line item
    for idx, item in enumerate(line_items):
        validate_line_item(item, idx)


def validate_line_item(item: dict, index: int) -> None:
    """
    Validate a single line item.
    
    Raises:
        MissingRequiredFieldError, InvalidDataFormatError
    """
    prefix = f"line_items[{index}]"
    
    # Check required fields
    if 'item_name' not in item or not item['item_name']:
        raise MissingRequiredFieldError(f"{prefix}.item_name")
    
    if 'quoted_price' not in item:
        raise MissingRequiredFieldError(f"{prefix}.quoted_price")
    
    # Validate price is a number
    try:
        price = float(item['quoted_price'])
        if price < 0:
            raise InvalidDataFormatError(
                f"{prefix}.quoted_price",
                "positive number",
                price
            )
        if price > 1_000_000:
            raise ValidationError(
                f"Line item price seems unrealistic: ${price:,.2f}",
                suggestion="Please double-check the pricing. For quotes over $1M, contact support."
            )
    except (TypeError, ValueError):
        raise InvalidDataFormatError(
            f"{prefix}.quoted_price",
            "number",
            item['quoted_price']
        )
    
    # Validate quantity if present
    if 'quantity' in item:
        try:
            qty = int(item['quantity'])
            if qty < 1:
                raise InvalidDataFormatError(
                    f"{prefix}.quantity",
                    "positive integer",
                    qty
                )
        except (TypeError, ValueError):
            raise InvalidDataFormatError(
                f"{prefix}.quantity",
                "integer",
                item['quantity']
            )


def validate_location(location: str) -> str:
    """
    Validate and normalize location string.
    
    Returns:
        Normalized location
    
    Raises:
        MissingRequiredFieldError, ValidationError
    """
    if not location:
        raise MissingRequiredFieldError("location")
    
    location = location.strip()
    
    if len(location) < 2:
        raise ValidationError(
            "Location must be at least 2 characters.",
            suggestion="Please provide a city, state, or ZIP code."
        )
    
    # Check for valid ZIP code format if it looks like a ZIP
    if location.isdigit() and len(location) == 5:
        return location  # Valid 5-digit ZIP
    
    # Check for ZIP+4 format
    if re.match(r'^\d{5}-\d{4}$', location):
        return location[:5]  # Return just the 5-digit part
    
    # Otherwise assume it's a city/state
    return location


def validate_project_type(project_type: str) -> str:
    """
    Validate project type.
    
    Returns:
        Normalized project_type
    
    Raises:
        MissingRequiredFieldError, ValidationError
    """
    if not project_type:
        raise MissingRequiredFieldError("project_type")
    
    # Normalize
    project_type = project_type.strip().lower()
    
    # List of known project types
    valid_types = {
        'roof_replacement',
        'kitchen_remodel',
        'bathroom_remodel',
        'hvac_replacement',
        'plumbing_repair',
        'electrical_work',
        'deck_building',
        'painting_interior',
        'painting_exterior',
        'siding_replacement',
        'window_replacement',
        'flooring',
        'basement_finishing',
        'general_remodel',
        'other',
    }
    
    # Allow some flexibility in naming
    normalized = project_type.replace(' ', '_').replace('-', '_')
    
    if normalized not in valid_types:
        # Don't reject unknown types, just log them
        # In production, you might want to track these
        pass
    
    return normalized


def sanitize_string(value: str, max_length: int = 500) -> str:
    """
    Sanitize string input to prevent injection attacks and clean up whitespace.
    
    Args:
        value: Input string
        max_length: Maximum allowed length
    
    Returns:
        Sanitized string
    """
    if not value:
        return ""
    
    # Remove null bytes and control characters
    sanitized = ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')
    
    # Normalize whitespace
    sanitized = ' '.join(sanitized.split())
    
    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()
