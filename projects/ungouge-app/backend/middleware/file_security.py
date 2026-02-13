"""
File Upload Security
- Size validation
- Type validation (magic bytes, not just extension)
- Metadata stripping (EXIF, PDF metadata)
- Malware scanning (optional, via VirusTotal API)
"""

import os
import hashlib
import magic
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException, status
from PIL import Image
import PyPDF2
import io

# Max file sizes
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_IMAGE_SIZE = 5 * 1024 * 1024   # 5MB
MAX_PDF_SIZE = 10 * 1024 * 1024    # 10MB

# Allowed MIME types
ALLOWED_IMAGE_TYPES = {
    'image/jpeg',
    'image/png',
    'image/webp',
    'image/heic'
}

ALLOWED_PDF_TYPE = 'application/pdf'

class FileSecurityValidator:
    """Validates and secures uploaded files"""
    
    @staticmethod
    async def validate_file_size(file: UploadFile, max_size: int = MAX_FILE_SIZE) -> int:
        """
        Validate file size
        Returns file size in bytes
        """
        # Read file to get size
        contents = await file.read()
        size = len(contents)
        
        # Reset file pointer
        await file.seek(0)
        
        if size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size {size} exceeds maximum of {max_size} bytes"
            )
        
        return size
    
    @staticmethod
    async def validate_file_type(file: UploadFile, allowed_types: set) -> str:
        """
        Validate file type using magic bytes (not just extension)
        Returns MIME type
        """
        # Read first 2048 bytes for magic number detection
        contents = await file.read(2048)
        await file.seek(0)
        
        # Detect MIME type from magic bytes
        mime = magic.from_buffer(contents, mime=True)
        
        if mime not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"File type {mime} not allowed. Allowed types: {', '.join(allowed_types)}"
            )
        
        return mime
    
    @staticmethod
    async def strip_image_metadata(file: UploadFile) -> bytes:
        """
        Strip EXIF and other metadata from image
        Returns cleaned image bytes
        """
        contents = await file.read()
        await file.seek(0)
        
        try:
            # Open image
            img = Image.open(io.BytesIO(contents))
            
            # Create new image without metadata
            data = list(img.getdata())
            clean_img = Image.new(img.mode, img.size)
            clean_img.putdata(data)
            
            # Save to bytes
            output = io.BytesIO()
            clean_img.save(output, format=img.format or 'PNG')
            return output.getvalue()
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to process image: {str(e)}"
            )
    
    @staticmethod
    async def strip_pdf_metadata(file: UploadFile) -> bytes:
        """
        Strip metadata from PDF
        Returns cleaned PDF bytes
        """
        contents = await file.read()
        await file.seek(0)
        
        try:
            # Read PDF
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(contents))
            pdf_writer = PyPDF2.PdfWriter()
            
            # Copy pages without metadata
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
            
            # Remove metadata
            pdf_writer.add_metadata({})
            
            # Write to bytes
            output = io.BytesIO()
            pdf_writer.write(output)
            return output.getvalue()
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to process PDF: {str(e)}"
            )
    
    @staticmethod
    def calculate_file_hash(contents: bytes) -> str:
        """Calculate SHA-256 hash of file contents"""
        return hashlib.sha256(contents).hexdigest()
    
    @staticmethod
    async def scan_for_malware(file: UploadFile, virustotal_api_key: Optional[str] = None) -> bool:
        """
        Scan file for malware using VirusTotal API
        Returns True if clean, raises exception if malware detected
        
        Note: Requires VirusTotal API key (optional, free tier: 4 requests/min)
        """
        if not virustotal_api_key:
            # Skip if no API key configured
            return True
        
        # TODO: Implement VirusTotal API integration
        # For now, just return True (skip scanning)
        return True


async def validate_uploaded_quote(file: UploadFile) -> Tuple[bytes, str, str]:
    """
    Validate and secure uploaded quote file (image or PDF)
    
    Returns:
        (clean_contents, mime_type, file_hash)
    
    Raises:
        HTTPException if validation fails
    """
    validator = FileSecurityValidator()
    
    # Validate file type first (cheap check)
    allowed_types = ALLOWED_IMAGE_TYPES | {ALLOWED_PDF_TYPE}
    mime_type = await validator.validate_file_type(file, allowed_types)
    
    # Validate size
    if mime_type in ALLOWED_IMAGE_TYPES:
        await validator.validate_file_size(file, MAX_IMAGE_SIZE)
    else:
        await validator.validate_file_size(file, MAX_PDF_SIZE)
    
    # Strip metadata based on file type
    if mime_type in ALLOWED_IMAGE_TYPES:
        clean_contents = await validator.strip_image_metadata(file)
    elif mime_type == ALLOWED_PDF_TYPE:
        clean_contents = await validator.strip_pdf_metadata(file)
    else:
        # Shouldn't reach here due to type validation above
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type"
        )
    
    # Calculate hash for deduplication/tracking
    file_hash = validator.calculate_file_hash(clean_contents)
    
    # Optional: Scan for malware
    # await validator.scan_for_malware(file, virustotal_api_key)
    
    return clean_contents, mime_type, file_hash
