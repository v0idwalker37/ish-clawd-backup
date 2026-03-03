"""
Pytest configuration and shared fixtures for ungouge.ai backend testing.

This module provides:
- Test database setup and teardown
- Authentication fixtures
- Mock data generators
- Test client configuration
"""

import os
import sys
from typing import Generator, Dict, Any
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))


@pytest.fixture(scope="session")
def test_db_url() -> str:
    """Return test database URL (in-memory SQLite)."""
    return "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_engine(test_db_url):
    """Create a fresh database engine for each test."""
    engine = create_engine(
        test_db_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Import your models and create tables
    # from app.models import Base
    # Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """Provide a transactional database session for each test."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=db_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="module")
def test_client(db_session) -> Generator[TestClient, None, None]:
    """
    Provide a FastAPI TestClient with dependency overrides.
    
    Usage:
        def test_endpoint(test_client):
            response = test_client.get("/api/endpoint")
            assert response.status_code == 200
    """
    # from app.main import app
    # from app.dependencies import get_db
    
    # def override_get_db():
    #     try:
    #         yield db_session
    #     finally:
    #         pass
    
    # app.dependency_overrides[get_db] = override_get_db
    
    # with TestClient(app) as client:
    #     yield client
    
    # app.dependency_overrides.clear()
    
    # Placeholder for when app is imported
    yield None


@pytest.fixture
def auth_headers_user() -> Dict[str, str]:
    """
    Provide authentication headers for a regular user.
    
    Returns:
        Dict with Authorization header containing valid JWT token
    """
    # In real implementation, generate or use a test JWT
    return {
        "Authorization": "Bearer test_user_token",
        "Content-Type": "application/json"
    }


@pytest.fixture
def auth_headers_admin() -> Dict[str, str]:
    """
    Provide authentication headers for an admin user.
    
    Returns:
        Dict with Authorization header containing valid admin JWT token
    """
    return {
        "Authorization": "Bearer test_admin_token",
        "Content-Type": "application/json"
    }


@pytest.fixture
def sample_quote_data() -> Dict[str, Any]:
    """
    Provide sample quote data for testing.
    
    Returns:
        Dict containing realistic quote submission data
    """
    return {
        "project_type": "HVAC Installation",
        "location": "Burlington, VT",
        "quote_amount": 12500.00,
        "contractor_name": "Test HVAC Co",
        "line_items": [
            {
                "description": "2-ton heat pump installation",
                "quantity": 1,
                "unit_price": 8500.00,
                "total": 8500.00
            },
            {
                "description": "Ductwork modification",
                "quantity": 1,
                "unit_price": 2000.00,
                "total": 2000.00
            },
            {
                "description": "Labor",
                "quantity": 20,
                "unit_price": 100.00,
                "total": 2000.00
            }
        ],
        "notes": "Test quote for verification"
    }


@pytest.fixture
def sample_rsmeans_data() -> Dict[str, Any]:
    """
    Provide sample RSMeans cost data for testing.
    
    Returns:
        Dict containing realistic cost database entries
    """
    return {
        "items": [
            {
                "code": "HVAC-001",
                "description": "Heat Pump, 2-ton, including installation",
                "unit": "EA",
                "material_cost": 4500.00,
                "labor_cost": 2500.00,
                "equipment_cost": 500.00,
                "total_cost": 7500.00
            }
        ],
        "location_factor": 0.98,  # Vermont factor
        "labor_rate": 75.00
    }


@pytest.fixture
def mock_gemini_response() -> Dict[str, Any]:
    """
    Provide a mock Gemini API response for testing.
    
    Returns:
        Dict mimicking Gemini API analysis output
    """
    return {
        "analysis": {
            "total_evaluation": "FAIR",
            "gouge_likelihood": 0.25,
            "line_item_analysis": [
                {
                    "item": "2-ton heat pump installation",
                    "market_range": {"low": 7000, "high": 9500, "avg": 8200},
                    "quoted_price": 8500,
                    "assessment": "FAIR",
                    "notes": "Within market range for Vermont"
                }
            ],
            "recommendations": [
                "Request itemized warranty details",
                "Verify contractor licensing"
            ]
        },
        "confidence": 0.85
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "security: marks tests as security-focused"
    )
