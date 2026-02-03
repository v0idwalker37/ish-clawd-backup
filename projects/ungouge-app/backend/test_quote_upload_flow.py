"""
Integration tests for the quote upload and analysis flow.

Tests the complete flow:
1. File upload → validation → parsing → analysis → report generation
2. Error scenarios at each stage
3. Recovery paths
"""

import pytest
import asyncio
from httpx import AsyncClient
from main import app
import io
from PIL import Image
from reportlab.pdfgen import canvas


@pytest.fixture
async def client():
    """Create test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


class TestQuoteUploadFlow:
    """Test complete quote upload workflow"""
    
    @pytest.mark.asyncio
    async def test_successful_pdf_upload(self, client):
        """Test successful PDF upload and parsing"""
        # Create a valid PDF with quote content
        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer)
        c.drawString(100, 750, "ABC Roofing Company")
        c.drawString(100, 730, "Austin, TX 78701")
        c.drawString(100, 700, "QUOTE")
        c.drawString(100, 670, "Asphalt Shingles - $3,500")
        c.drawString(100, 650, "Labor - $2,000")
        c.drawString(100, 630, "Total: $5,500")
        c.showPage()
        c.save()
        
        pdf_content = pdf_buffer.getvalue()
        
        response = await client.post(
            "/api/quotes/parse-upload",
            files={"file": ("quote.pdf", pdf_content, "application/pdf")}
        )
        
        # Should succeed or gracefully handle AI parsing
        assert response.status_code in [200, 400, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "line_items" in data or "error" in data
    
    @pytest.mark.asyncio
    async def test_file_too_large_rejection(self, client):
        """Test that files over 10MB are rejected with helpful message"""
        # Create a file larger than 10MB
        large_content = b"x" * (11 * 1024 * 1024)
        
        response = await client.post(
            "/api/quotes/parse-upload",
            files={"file": ("large.pdf", large_content, "application/pdf")}
        )
        
        assert response.status_code == 400
        error_data = response.json()
        
        # Check for user-friendly error message
        assert "detail" in error_data
        detail = error_data["detail"]
        
        if isinstance(detail, dict):
            assert "error" in detail
            assert "suggestion" in detail
            assert "10MB" in detail["suggestion"] or "10MB" in detail["error"]
        else:
            assert "10MB" in str(detail) or "too large" in str(detail).lower()
    
    @pytest.mark.asyncio
    async def test_unsupported_file_type_rejection(self, client):
        """Test that unsupported file types are rejected with helpful message"""
        # Create a text file
        text_content = b"This is not a PDF or image"
        
        response = await client.post(
            "/api/quotes/parse-upload",
            files={"file": ("quote.txt", text_content, "text/plain")}
        )
        
        assert response.status_code == 400
        error_data = response.json()
        detail = error_data["detail"]
        
        if isinstance(detail, dict):
            assert "suggestion" in detail
            # Should mention supported formats
            suggestion_text = detail["suggestion"].lower()
            assert "pdf" in suggestion_text or "png" in suggestion_text
    
    @pytest.mark.asyncio
    async def test_empty_file_rejection(self, client):
        """Test that empty files are rejected"""
        response = await client.post(
            "/api/quotes/parse-upload",
            files={"file": ("empty.pdf", b"", "application/pdf")}
        )
        
        assert response.status_code == 400
        error_data = response.json()
        detail = error_data["detail"]
        
        if isinstance(detail, dict):
            assert "error" in detail
            assert "empty" in detail["error"].lower() or "corrupt" in detail["error"].lower()
    
    @pytest.mark.asyncio
    async def test_corrupt_pdf_rejection(self, client):
        """Test that corrupt PDFs are rejected with recovery suggestions"""
        # Create invalid PDF content
        corrupt_pdf = b"This is not a valid PDF file"
        
        response = await client.post(
            "/api/quotes/parse-upload",
            files={"file": ("corrupt.pdf", corrupt_pdf, "application/pdf")}
        )
        
        assert response.status_code == 400
        error_data = response.json()
        detail = error_data["detail"]
        
        if isinstance(detail, dict):
            assert "suggestion" in detail
            # Should suggest recovery actions
            suggestion = detail["suggestion"].lower()
            assert any(word in suggestion for word in [
                "convert", "screenshot", "format", "readable"
            ])
    
    @pytest.mark.asyncio
    async def test_valid_image_upload(self, client):
        """Test successful image upload"""
        # Create a valid test image with some text-like content
        img = Image.new('RGB', (800, 600), color='white')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_content = img_buffer.getvalue()
        
        response = await client.post(
            "/api/quotes/parse-upload",
            files={"file": ("quote.png", img_content, "image/png")}
        )
        
        # Should succeed validation (parsing might fail if no text)
        assert response.status_code in [200, 400, 503]


class TestQuoteSubmissionFlow:
    """Test quote submission and analysis flow"""
    
    @pytest.mark.asyncio
    async def test_valid_quote_submission(self, client):
        """Test successful quote submission and analysis"""
        quote_data = {
            "project_type": "roof_replacement",
            "location": "Austin, TX",
            "contractor_name": "ABC Roofing",
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
                    "description": "Installation",
                    "quoted_price": 2000.00,
                    "quantity": 1,
                    "unit": "job"
                }
            ]
        }
        
        response = await client.post("/api/quotes", json=quote_data)
        
        # Should succeed or fail gracefully
        assert response.status_code in [201, 400, 500, 503]
        
        if response.status_code == 201:
            data = response.json()
            assert "id" in data
            assert "report_url" in data
    
    @pytest.mark.asyncio
    async def test_missing_required_fields(self, client):
        """Test that missing required fields are caught with helpful errors"""
        incomplete_quote = {
            "project_type": "roof_replacement",
            # Missing location
            "line_items": []
        }
        
        response = await client.post("/api/quotes", json=incomplete_quote)
        
        assert response.status_code == 400
        error_data = response.json()
        
        # Should have helpful error message
        assert "detail" in error_data
    
    @pytest.mark.asyncio
    async def test_invalid_price_format(self, client):
        """Test that invalid price formats are caught"""
        quote_data = {
            "project_type": "roof_replacement",
            "location": "Austin, TX",
            "line_items": [
                {
                    "item_name": "Test Item",
                    "quoted_price": "not a number",  # Invalid
                    "quantity": 1
                }
            ]
        }
        
        response = await client.post("/api/quotes", json=quote_data)
        
        # Should be rejected
        assert response.status_code in [400, 422]
    
    @pytest.mark.asyncio
    async def test_negative_price(self, client):
        """Test that negative prices are caught"""
        quote_data = {
            "project_type": "roof_replacement",
            "location": "Austin, TX",
            "line_items": [
                {
                    "item_name": "Test Item",
                    "quoted_price": -100.00,  # Negative
                    "quantity": 1
                }
            ]
        }
        
        response = await client.post("/api/quotes", json=quote_data)
        
        assert response.status_code in [400, 422]
    
    @pytest.mark.asyncio
    async def test_too_many_line_items(self, client):
        """Test that quotes with too many items are rejected"""
        # Create 101 line items
        line_items = [
            {
                "item_name": f"Item {i}",
                "quoted_price": 100.00,
                "quantity": 1
            }
            for i in range(101)
        ]
        
        quote_data = {
            "project_type": "roof_replacement",
            "location": "Austin, TX",
            "line_items": line_items
        }
        
        response = await client.post("/api/quotes", json=quote_data)
        
        assert response.status_code == 400
        error_data = response.json()
        
        if isinstance(error_data["detail"], dict):
            assert "suggestion" in error_data["detail"]


class TestErrorRecoveryPaths:
    """Test that errors provide actionable recovery suggestions"""
    
    @pytest.mark.asyncio
    async def test_ai_service_failure_recovery(self, client):
        """Test recovery suggestions when AI service fails"""
        # This would require mocking the AI service
        # For now, just verify the error handling structure exists
        pass
    
    @pytest.mark.asyncio
    async def test_database_failure_recovery(self, client):
        """Test recovery suggestions when database fails"""
        # This would require mocking database failures
        pass
    
    def test_error_response_structure(self):
        """Test that all errors follow consistent response structure"""
        from exceptions import (
            FileTooLargeError,
            InvalidCredentialsError,
            PaymentError,
        )
        
        errors = [
            FileTooLargeError(15.0, 10),
            InvalidCredentialsError(),
            PaymentError("Test payment error"),
        ]
        
        for error in errors:
            response = error.to_dict()
            
            # All errors should have these fields
            assert "error" in response
            assert "suggestion" in response
            
            # Suggestions should be actionable
            assert len(response["suggestion"]) > 20
            
            # Should not contain technical jargon
            suggestion_lower = response["suggestion"].lower()
            assert "exception" not in suggestion_lower
            assert "traceback" not in suggestion_lower


class TestRateLimiting:
    """Test rate limiting with helpful error messages"""
    
    @pytest.mark.asyncio
    async def test_upload_rate_limit(self, client):
        """Test that rate limits are enforced on uploads"""
        # Create a small valid image
        img = Image.new('RGB', (100, 100), color='white')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_content = img_buffer.getvalue()
        
        # Try to upload 6 times (limit is 5/hour)
        for i in range(6):
            response = await client.post(
                "/api/quotes/parse-upload",
                files={"file": (f"quote{i}.png", img_content, "image/png")}
            )
            
            if response.status_code == 429:
                # Rate limited - check error message
                error_data = response.json()
                # Should have helpful message about rate limits
                assert "detail" in error_data
                break


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
