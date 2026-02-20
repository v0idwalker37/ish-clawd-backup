"""
Unit tests for Cost Model Service
"""

import pytest
from fastapi.testclient import TestClient
from main import app, CostAnalysisRequest, LineItem, Location

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
    assert "status" in response.json()
    assert "checks" in response.json()

def test_analyze_quote_basic():
    """Test basic quote analysis"""
    request = {
        "quote_id": "test-quote-123",
        "line_items": [
            {
                "description": "Labor",
                "quantity": 40,
                "unit": "hours",
                "unit_price": 50.0
            },
            {
                "description": "Materials",
                "quantity": 1,
                "unit": "lot",
                "unit_price": 1000.0
            }
        ],
        "location": {
            "zip_code": "05663",
            "state": "VT"
        },
        "project_type": "flooring",
        "total_quoted": 3000.0
    }
    
    response = client.post("/analyze", json=request)
    assert response.status_code == 200
    
    data = response.json()
    assert data["quote_id"] == "test-quote-123"
    assert "total_cost" in data
    assert "fair_price_range" in data
    assert "confidence_score" in data
    assert "verdict" in data
    assert "breakdown" in data
    assert "recommendations" in data
    assert isinstance(data["confidence_score"], float)
    assert 0 <= data["confidence_score"] <= 1

def test_analyze_quote_invalid():
    """Test analysis with invalid data"""
    request = {
        "quote_id": "test-quote-456",
        "line_items": [],  # Empty line items
        "location": {
            "zip_code": "05663"
        },
        "project_type": "flooring"
    }
    
    response = client.post("/analyze", json=request)
    # Should still return 200 but with low confidence
    assert response.status_code == 200

def test_analyze_quote_caching():
    """Test that identical requests are cached"""
    request = {
        "quote_id": "test-quote-789",
        "line_items": [
            {
                "description": "Test Item",
                "quantity": 1,
                "unit": "ea",
                "unit_price": 100.0
            }
        ],
        "location": {
            "zip_code": "05663"
        },
        "project_type": "test"
    }
    
    # First request
    response1 = client.post("/analyze", json=request)
    assert response1.status_code == 200
    
    # Second identical request (should hit cache)
    response2 = client.post("/analyze", json=request)
    assert response2.status_code == 200
    
    # Results should be identical
    assert response1.json() == response2.json()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
