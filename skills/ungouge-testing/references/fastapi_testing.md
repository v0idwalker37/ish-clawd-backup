# FastAPI-Specific Testing Guide

Comprehensive guide to testing FastAPI applications with async support, dependency injection, and middleware testing.

## Table of Contents

1. [TestClient Basics](#testclient-basics)
2. [Testing Async Endpoints](#testing-async-endpoints)
3. [Dependency Overrides](#dependency-overrides)
4. [Testing Middleware](#testing-middleware)
5. [Testing Background Tasks](#testing-background-tasks)
6. [Testing WebSockets](#testing-websockets)
7. [Testing File Uploads](#testing-file-uploads)

---

## TestClient Basics

### Basic Setup

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
```

### Testing Request/Response

```python
def test_create_quote(test_client, auth_headers):
    """Test POST endpoint with JSON body."""
    payload = {
        "project_type": "HVAC",
        "quote_amount": 5000.00,
        "contractor_name": "Test Co"
    }
    
    response = test_client.post(
        "/api/v1/quotes",
        json=payload,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["project_type"] == "HVAC"
    assert "id" in data
```

### Testing Query Parameters

```python
def test_list_quotes_with_filters(test_client, auth_headers):
    """Test GET endpoint with query parameters."""
    response = test_client.get(
        "/api/v1/quotes",
        params={"project_type": "HVAC", "min_amount": 1000},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert all(q["project_type"] == "HVAC" for q in data)
    assert all(q["quote_amount"] >= 1000 for q in data)
```

### Testing Path Parameters

```python
def test_get_quote_by_id(test_client, auth_headers):
    """Test GET endpoint with path parameter."""
    # Create a quote first
    create_response = test_client.post(
        "/api/v1/quotes",
        json={"project_type": "Roofing", "quote_amount": 8000},
        headers=auth_headers
    )
    quote_id = create_response.json()["id"]
    
    # Fetch it
    response = test_client.get(
        f"/api/v1/quotes/{quote_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json()["id"] == quote_id
```

---

## Testing Async Endpoints

### Async Test with httpx

For true async testing, use `httpx.AsyncClient`:

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_async_endpoint():
    """Test async endpoint with httpx AsyncClient."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/quotes")
        assert response.status_code == 200
```

### Testing Async Database Operations

```python
@pytest.mark.asyncio
async def test_async_database_query(async_db_session):
    """Test async database query."""
    from app.services.quote import get_quotes_async
    
    quotes = await get_quotes_async(async_db_session, limit=10)
    assert isinstance(quotes, list)
    assert len(quotes) <= 10
```

### Testing Background Task Completion

```python
import asyncio

@pytest.mark.asyncio
async def test_background_task_completes(test_client):
    """Test that background task completes successfully."""
    response = test_client.post(
        "/api/v1/quotes/analyze",
        json={"amount": 5000}
    )
    
    assert response.status_code == 202  # Accepted
    task_id = response.json()["task_id"]
    
    # Wait for task completion
    for _ in range(10):
        await asyncio.sleep(0.5)
        status_response = test_client.get(f"/api/v1/tasks/{task_id}")
        if status_response.json()["status"] == "completed":
            break
    
    assert status_response.json()["status"] == "completed"
```

---

## Dependency Overrides

### Overriding Database Dependency

```python
from app.main import app
from app.dependencies import get_db

def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
```

### Overriding Authentication

```python
from app.dependencies import get_current_user
from app.models import User

def override_get_current_user():
    """Override auth dependency to return test user."""
    return User(
        id=1,
        email="test@example.com",
        role="user"
    )

app.dependency_overrides[get_current_user] = override_get_current_user

def test_protected_endpoint(test_client):
    """Test endpoint that requires authentication."""
    response = test_client.get("/api/v1/me")
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
```

### Fixture-Based Dependency Overrides

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def test_client_with_auth(db_session):
    """Provide test client with auth override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    def override_get_current_user():
        return User(id=1, email="test@example.com", role="user")
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()
```

### Testing Different User Roles

```python
@pytest.fixture
def test_client_admin(db_session):
    """Test client authenticated as admin."""
    def override_current_user():
        return User(id=1, email="admin@example.com", role="admin")
    
    app.dependency_overrides[get_current_user] = override_current_user
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()

def test_admin_endpoint(test_client_admin):
    """Test that admin can access admin endpoints."""
    response = test_client_admin.get("/api/v1/admin/analytics")
    assert response.status_code == 200
```

---

## Testing Middleware

### Testing Custom Middleware

```python
def test_custom_header_middleware(test_client):
    """Test that middleware adds custom headers."""
    response = test_client.get("/")
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 0
```

### Testing CORS Middleware

```python
def test_cors_headers(test_client):
    """Test CORS middleware configuration."""
    response = test_client.options(
        "/api/v1/quotes",
        headers={"Origin": "https://ungouge.ai"}
    )
    
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://ungouge.ai"
    assert "POST" in response.headers["access-control-allow-methods"]
```

### Testing Rate Limiting Middleware

```python
import time

def test_rate_limit_middleware(test_client):
    """Test that rate limiting is enforced."""
    # Make requests up to the limit
    responses = []
    for i in range(15):
        response = test_client.get("/api/v1/quotes")
        responses.append(response.status_code)
        time.sleep(0.1)
    
    # Should have some 429 (Too Many Requests) responses
    assert 429 in responses
```

---

## Testing Background Tasks

### Testing Task Queueing

```python
from unittest.mock import patch, MagicMock

@patch('app.tasks.analyze_quote.delay')
def test_background_task_queued(mock_task, test_client, auth_headers):
    """Test that background task is queued correctly."""
    response = test_client.post(
        "/api/v1/quotes/analyze",
        json={"amount": 5000},
        headers=auth_headers
    )
    
    assert response.status_code == 202
    mock_task.assert_called_once()
```

### Testing Task Execution

```python
def test_analyze_quote_task():
    """Test the background task itself."""
    from app.tasks import analyze_quote_task
    
    result = analyze_quote_task(quote_id=1)
    
    assert result["status"] == "completed"
    assert "analysis" in result
```

---

## Testing WebSockets

### Basic WebSocket Test

```python
from fastapi.testclient import TestClient

def test_websocket_connection(test_client):
    """Test WebSocket connection and messaging."""
    with test_client.websocket_connect("/ws") as websocket:
        # Send message
        websocket.send_json({"message": "hello"})
        
        # Receive response
        data = websocket.receive_json()
        assert data["response"] == "hello"
```

### Testing WebSocket Authentication

```python
def test_websocket_requires_auth(test_client):
    """Test that WebSocket connection requires authentication."""
    with pytest.raises(Exception):  # Connection rejected
        with test_client.websocket_connect("/ws"):
            pass
```

---

## Testing File Uploads

### Single File Upload

```python
def test_upload_pdf(test_client, auth_headers):
    """Test PDF file upload."""
    files = {
        "file": ("quote.pdf", b"fake PDF content", "application/pdf")
    }
    
    response = test_client.post(
        "/api/v1/quotes/upload",
        files=files,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert "file_id" in response.json()
```

### Multiple File Upload

```python
def test_upload_multiple_files(test_client, auth_headers):
    """Test uploading multiple files."""
    files = [
        ("files", ("quote1.pdf", b"content1", "application/pdf")),
        ("files", ("quote2.pdf", b"content2", "application/pdf")),
    ]
    
    response = test_client.post(
        "/api/v1/quotes/batch-upload",
        files=files,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["uploaded"]) == 2
```

### Testing File Validation

```python
def test_upload_invalid_file_type(test_client, auth_headers):
    """Test that invalid file types are rejected."""
    files = {
        "file": ("malicious.exe", b"fake content", "application/x-msdownload")
    }
    
    response = test_client.post(
        "/api/v1/quotes/upload",
        files=files,
        headers=auth_headers
    )
    
    assert response.status_code == 400
    assert "invalid file type" in response.json()["detail"].lower()
```

---

## Testing Response Models

### Validating Response Schema

```python
from app.schemas import QuoteResponse

def test_response_matches_schema(test_client, auth_headers):
    """Test that API response matches Pydantic schema."""
    response = test_client.get("/api/v1/quotes/1", headers=auth_headers)
    
    assert response.status_code == 200
    
    # Validate against schema
    quote = QuoteResponse(**response.json())
    assert quote.id == 1
    assert quote.project_type is not None
```

### Testing Response Headers

```python
def test_response_headers(test_client):
    """Test custom response headers."""
    response = test_client.get("/api/v1/quotes")
    
    assert response.headers["Content-Type"] == "application/json"
    assert "X-Process-Time" in response.headers
```

---

## Testing Error Handling

### Testing 404 Responses

```python
def test_get_nonexistent_quote(test_client, auth_headers):
    """Test 404 for nonexistent resource."""
    response = test_client.get(
        "/api/v1/quotes/99999",
        headers=auth_headers
    )
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Quote not found"
```

### Testing Validation Errors

```python
def test_validation_error_format(test_client, auth_headers):
    """Test FastAPI validation error response format."""
    response = test_client.post(
        "/api/v1/quotes",
        json={"invalid": "data"},
        headers=auth_headers
    )
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert isinstance(data["detail"], list)
    assert "loc" in data["detail"][0]
    assert "msg" in data["detail"][0]
```

### Testing Custom Exception Handlers

```python
def test_custom_exception_handler(test_client):
    """Test custom exception is handled properly."""
    # Trigger custom exception
    response = test_client.get("/api/v1/trigger-custom-error")
    
    assert response.status_code == 500
    data = response.json()
    assert data["error_type"] == "CustomError"
    assert "message" in data
```

---

## Testing Request Validation

### Testing Required Fields

```python
@pytest.mark.parametrize("missing_field", [
    "project_type",
    "quote_amount",
    "contractor_name"
])
def test_missing_required_field(test_client, auth_headers, missing_field):
    """Test that missing required fields are rejected."""
    payload = {
        "project_type": "HVAC",
        "quote_amount": 5000,
        "contractor_name": "Test Co"
    }
    del payload[missing_field]
    
    response = test_client.post(
        "/api/v1/quotes",
        json=payload,
        headers=auth_headers
    )
    
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(missing_field in str(e) for e in errors)
```

### Testing Field Constraints

```python
def test_field_constraints(test_client, auth_headers):
    """Test field validation constraints."""
    payload = {
        "project_type": "A",  # Too short (min 3 chars)
        "quote_amount": -100,  # Negative
        "contractor_name": "X" * 300  # Too long (max 200)
    }
    
    response = test_client.post(
        "/api/v1/quotes",
        json=payload,
        headers=auth_headers
    )
    
    assert response.status_code == 422
```

---

## Performance Testing

### Testing Response Time

```python
import time

def test_endpoint_response_time(test_client, auth_headers):
    """Test that endpoint responds within acceptable time."""
    start = time.time()
    response = test_client.get("/api/v1/quotes", headers=auth_headers)
    duration = time.time() - start
    
    assert response.status_code == 200
    assert duration < 0.5  # Should respond in under 500ms
```

### Testing Concurrent Requests

```python
import concurrent.futures

def test_concurrent_requests(test_client, auth_headers):
    """Test handling of concurrent requests."""
    def make_request():
        return test_client.get("/api/v1/quotes", headers=auth_headers)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(10)]
        results = [f.result() for f in futures]
    
    assert all(r.status_code == 200 for r in results)
```

---

## Best Practices Summary

1. **Use dependency overrides** for clean test isolation
2. **Test both sync and async code paths** when using async
3. **Mock external services** to keep tests fast and reliable
4. **Test error cases** as thoroughly as success cases
5. **Validate response schemas** with Pydantic models
6. **Test middleware** separately from endpoints
7. **Use parametrize** for testing multiple scenarios
8. **Keep tests independent** - no shared state
9. **Test authentication and authorization** thoroughly
10. **Measure and enforce response time** requirements
