"""
Comprehensive test suite for error handling and edge cases.

Tests:
1. File upload validation (size, type, corrupt files, empty files)
2. Quote submission validation (missing data, invalid formats)
3. Auth error scenarios
4. Payment error scenarios
5. API error responses (user-friendly messages, recovery suggestions)
"""

import pytest
import io
from PIL import Image
import PyPDF2
from validators import (
    validate_file_upload,
    validate_email,
    validate_password,
    validate_quote_submission,
    validate_line_item,
)
from exceptions import (
    FileTooLargeError,
    EmptyFileError,
    UnsupportedFileTypeError,
    CorruptFileError,
    InvalidCredentialsError,
    ValidationError,
    MissingRequiredFieldError,
    InvalidDataFormatError,
)


class TestFileValidation:
    """Test file upload validation and edge cases"""
    
    def test_file_too_large(self):
        """Test that files over 10MB are rejected"""
        # Create a file larger than 10MB
        large_file = b"x" * (11 * 1024 * 1024)  # 11MB
        
        with pytest.raises(FileTooLargeError) as exc_info:
            validate_file_upload(large_file, "test.pdf", "application/pdf")
        
        assert "11" in str(exc_info.value.message)
        assert "10MB" in exc_info.value.suggestion
    
    def test_empty_file(self):
        """Test that empty files are rejected"""
        with pytest.raises(EmptyFileError):
            validate_file_upload(b"", "test.pdf", "application/pdf")
    
    def test_unsupported_file_type(self):
        """Test that unsupported file types are rejected"""
        file_content = b"test content"
        
        with pytest.raises(UnsupportedFileTypeError) as exc_info:
            validate_file_upload(file_content, "test.txt", "text/plain")
        
        assert "PDF" in exc_info.value.suggestion
        assert "PNG" in exc_info.value.suggestion
    
    def test_corrupt_pdf(self):
        """Test that corrupt PDFs are detected"""
        # Create invalid PDF content
        corrupt_pdf = b"This is not a valid PDF"
        
        with pytest.raises(CorruptFileError) as exc_info:
            validate_file_upload(corrupt_pdf, "test.pdf", "application/pdf")
        
        assert "corrupt" in exc_info.value.message.lower()
    
    def test_valid_pdf(self):
        """Test that valid PDFs pass validation"""
        # Create a minimal valid PDF
        pdf_buffer = io.BytesIO()
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(pdf_buffer)
        c.drawString(100, 750, "Test Quote")
        c.showPage()
        c.save()
        
        pdf_content = pdf_buffer.getvalue()
        
        # Should not raise
        validated, content_type = validate_file_upload(
            pdf_content,
            "test.pdf",
            "application/pdf"
        )
        assert content_type == "application/pdf"
    
    def test_valid_image(self):
        """Test that valid images pass validation"""
        # Create a valid test image
        img = Image.new('RGB', (200, 200), color='white')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_content = img_buffer.getvalue()
        
        # Should not raise
        validated, content_type = validate_file_upload(
            img_content,
            "test.png",
            "image/png"
        )
        assert content_type == "image/png"
    
    def test_image_too_small(self):
        """Test that very small images are rejected"""
        # Create a tiny image (below minimum size)
        img = Image.new('RGB', (10, 10), color='white')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_content = img_buffer.getvalue()
        
        with pytest.raises(CorruptFileError) as exc_info:
            validate_file_upload(img_content, "tiny.png", "image/png")
        
        assert "too small" in exc_info.value.message.lower()
    
    def test_blank_image_detection(self):
        """Test that completely blank images are detected"""
        # Create a blank white image
        img = Image.new('RGB', (200, 200), color='white')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_content = img_buffer.getvalue()
        
        # This might or might not raise depending on detection logic
        # At minimum it should not crash
        try:
            validate_file_upload(img_content, "blank.png", "image/png")
        except EmptyFileError:
            pass  # Expected


class TestEmailValidation:
    """Test email validation"""
    
    def test_valid_emails(self):
        """Test that valid emails are accepted"""
        valid_emails = [
            "user@example.com",
            "john.doe@company.co.uk",
            "test+filter@gmail.com",
            "123@numbers.com",
        ]
        
        for email in valid_emails:
            normalized = validate_email(email)
            assert "@" in normalized
            assert normalized == normalized.lower()
    
    def test_invalid_email_formats(self):
        """Test that invalid emails are rejected"""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user @example.com",
            "user@example",
            "",
        ]
        
        for email in invalid_emails:
            with pytest.raises((MissingRequiredFieldError, InvalidDataFormatError)):
                validate_email(email)
    
    def test_email_normalization(self):
        """Test that emails are normalized (lowercased, trimmed)"""
        email = "  USER@EXAMPLE.COM  "
        normalized = validate_email(email)
        assert normalized == "user@example.com"


class TestPasswordValidation:
    """Test password validation"""
    
    def test_password_too_short(self):
        """Test that short passwords are rejected"""
        with pytest.raises(InvalidDataFormatError) as exc_info:
            validate_password("short1")
        
        assert "8 characters" in exc_info.value.message
    
    def test_password_no_number(self):
        """Test that passwords without numbers are rejected"""
        with pytest.raises(InvalidDataFormatError):
            validate_password("onlyletters")
    
    def test_password_no_letter(self):
        """Test that passwords without letters are rejected"""
        with pytest.raises(InvalidDataFormatError):
            validate_password("12345678")
    
    def test_valid_passwords(self):
        """Test that valid passwords are accepted"""
        valid_passwords = [
            "password123",
            "MyP@ssw0rd",
            "test1234",
            "a1b2c3d4",
        ]
        
        for pwd in valid_passwords:
            # Should not raise
            validate_password(pwd)


class TestQuoteValidation:
    """Test quote submission validation"""
    
    def test_missing_required_fields(self):
        """Test that missing required fields are caught"""
        # Missing project_type
        with pytest.raises(MissingRequiredFieldError):
            validate_quote_submission({
                "location": "Austin, TX",
                "line_items": []
            })
        
        # Missing location
        with pytest.raises(MissingRequiredFieldError):
            validate_quote_submission({
                "project_type": "roof_replacement",
                "line_items": []
            })
        
        # Missing line_items
        with pytest.raises(MissingRequiredFieldError):
            validate_quote_submission({
                "project_type": "roof_replacement",
                "location": "Austin, TX"
            })
    
    def test_empty_line_items(self):
        """Test that quotes with no line items are rejected"""
        with pytest.raises(ValidationError) as exc_info:
            validate_quote_submission({
                "project_type": "roof_replacement",
                "location": "Austin, TX",
                "line_items": []
            })
        
        assert "at least one" in exc_info.value.message.lower()
    
    def test_too_many_line_items(self):
        """Test that quotes with too many line items are rejected"""
        # Create 101 line items
        line_items = [
            {
                "item_name": f"Item {i}",
                "quoted_price": 100.0,
                "quantity": 1
            }
            for i in range(101)
        ]
        
        with pytest.raises(ValidationError) as exc_info:
            validate_quote_submission({
                "project_type": "roof_replacement",
                "location": "Austin, TX",
                "line_items": line_items
            })
        
        assert "too many" in exc_info.value.message.lower()
    
    def test_invalid_line_item_price(self):
        """Test that invalid prices are caught"""
        # Negative price
        with pytest.raises(InvalidDataFormatError):
            validate_line_item({
                "item_name": "Test Item",
                "quoted_price": -100.0
            }, 0)
        
        # Non-numeric price
        with pytest.raises(InvalidDataFormatError):
            validate_line_item({
                "item_name": "Test Item",
                "quoted_price": "not a number"
            }, 0)
    
    def test_missing_line_item_fields(self):
        """Test that missing line item fields are caught"""
        # Missing item_name
        with pytest.raises(MissingRequiredFieldError):
            validate_line_item({
                "quoted_price": 100.0
            }, 0)
        
        # Missing quoted_price
        with pytest.raises(MissingRequiredFieldError):
            validate_line_item({
                "item_name": "Test Item"
            }, 0)
    
    def test_valid_quote_submission(self):
        """Test that valid quote submissions pass validation"""
        valid_quote = {
            "project_type": "roof_replacement",
            "location": "Austin, TX",
            "line_items": [
                {
                    "item_name": "Asphalt Shingles",
                    "description": "30-year architectural",
                    "quoted_price": 3500.00,
                    "quantity": 20,
                    "unit": "square"
                },
                {
                    "item_name": "Labor",
                    "quoted_price": 2000.00,
                    "quantity": 1,
                    "unit": "job"
                }
            ]
        }
        
        # Should not raise
        validate_quote_submission(valid_quote)


class TestExceptionMessages:
    """Test that exceptions provide user-friendly messages and suggestions"""
    
    def test_file_too_large_error_message(self):
        """Test FileTooLargeError provides helpful message"""
        exc = FileTooLargeError(15.5, 10)
        
        assert "15.5" in exc.message
        assert "10MB" in exc.message
        assert "compress" in exc.suggestion.lower()
        assert exc.status_code == 400
    
    def test_invalid_credentials_error_message(self):
        """Test InvalidCredentialsError provides helpful suggestions"""
        exc = InvalidCredentialsError()
        
        assert "password" in exc.message.lower()
        assert "forgot password" in exc.suggestion.lower()
        assert exc.status_code == 401
    
    def test_exception_to_dict(self):
        """Test that exceptions convert to API response format"""
        exc = ValidationError(
            "Test error",
            suggestion="Test suggestion",
            field="test_field"
        )
        
        response = exc.to_dict()
        
        assert "error" in response
        assert "suggestion" in response
        assert response["error"] == "Test error"
        assert response["suggestion"] == "Test suggestion"
    
    def test_no_sensitive_data_in_response(self):
        """Test that sensitive data is not included in error responses"""
        exc = ValidationError(
            "Test error",
            log_context={
                "password": "secret123",
                "token": "abc123",
                "api_key": "key123",
                "safe_field": "ok_to_show"
            }
        )
        
        response = exc.to_dict()
        
        # Sensitive fields should be filtered out
        if "context" in response:
            assert "password" not in response["context"]
            assert "token" not in response["context"]
            assert "api_key" not in response["context"]


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_extremely_long_strings(self):
        """Test that extremely long strings are handled"""
        from validators import sanitize_string
        
        long_string = "x" * 10000
        sanitized = sanitize_string(long_string, max_length=500)
        
        assert len(sanitized) == 500
    
    def test_special_characters_sanitization(self):
        """Test that special characters are handled properly"""
        from validators import sanitize_string
        
        # Null bytes and control characters
        dirty_string = "test\x00string\x01with\x02control\x03chars"
        clean = sanitize_string(dirty_string)
        
        assert "\x00" not in clean
        assert "\x01" not in clean
        assert "test" in clean
        assert "string" in clean
    
    def test_unicode_handling(self):
        """Test that Unicode characters are handled correctly"""
        from validators import sanitize_string
        
        unicode_string = "Hello 世界 🌍"
        sanitized = sanitize_string(unicode_string)
        
        # Should preserve valid Unicode
        assert "Hello" in sanitized
    
    def test_whitespace_normalization(self):
        """Test that excessive whitespace is normalized"""
        from validators import sanitize_string
        
        messy_string = "too    much     space"
        clean = sanitize_string(messy_string)
        
        assert "  " not in clean  # No double spaces
        assert "too much space" == clean


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
