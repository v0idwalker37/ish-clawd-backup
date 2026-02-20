"""
Unit tests for Quote Extractor Service
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_live():
    """Test liveness probe"""
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_health_ready():
    """Test readiness probe"""
    response = client.get("/health/ready")
    assert response.status_code in [200, 503]
    data = response.json()
    assert "status" in data
    assert "checks" in data

def test_extract_invalid_file_type():
    """Test extraction with invalid file type"""
    request = {
        "quote_id": "test-123",
        "file_url": "https://example.com/test.txt",
        "file_type": "txt"  # Invalid
    }
    
    response = client.post("/extract", json=request)
    assert response.status_code == 422  # Validation error

def test_extract_missing_fields():
    """Test extraction with missing required fields"""
    request = {
        "quote_id": "test-456"
        # Missing file_url and file_type
    }
    
    response = client.post("/extract", json=request)
    assert response.status_code == 422

# Note: Full extraction tests require mocking Vision API
# Add integration tests with actual Vision API calls

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
