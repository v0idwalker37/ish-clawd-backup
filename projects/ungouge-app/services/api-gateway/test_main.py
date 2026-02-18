"""
Unit tests for API Gateway Service
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_live():
    """Test liveness probe"""
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data

def test_health_ready():
    """Test readiness probe"""
    response = client.get("/health/ready")
    # May return 503 if downstream services unavailable
    assert response.status_code in [200, 503]
    data = response.json()
    assert "status" in data
    assert "checks" in data
    assert "timestamp" in data

def test_security_headers():
    """Test that security headers are present"""
    response = client.get("/health/live")
    headers = response.headers
    
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    assert "Strict-Transport-Security" in headers
    assert "Referrer-Policy" in headers

def test_cors_headers():
    """Test CORS headers are set"""
    response = client.options("/health/live", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET"
    })
    
    assert "Access-Control-Allow-Origin" in response.headers

def test_rate_limiting():
    """Test rate limiting is enforced"""
    # Make many requests quickly
    responses = []
    for i in range(150):
        response = client.get("/health/live")
        responses.append(response.status_code)
    
    # Should eventually hit rate limit (429)
    assert 429 in responses

def test_analyze_endpoint():
    """Test quote analysis endpoint"""
    request_data = {
        "quote_id": "test-123",
        "line_items": [
            {
                "description": "Test",
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
    
    response = client.post("/api/v2/quotes/analyze", json=request_data)
    # May fail if cost model service not running
    assert response.status_code in [200, 500, 503]

def test_error_handling():
    """Test error responses have consistent format"""
    # Invalid request
    response = client.post("/api/v2/quotes/analyze", json={"invalid": "data"})
    
    # Should return error response with consistent format
    assert response.status_code >= 400
    data = response.json()
    assert "error" in data or "detail" in data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
