---
name: ungouge-testing
description: Comprehensive pytest testing framework for FastAPI applications with focus on ungouge.ai backend. Provides test infrastructure, patterns, and best practices for unit testing, integration testing, security testing, and mocking external services. Use when writing tests, setting up test infrastructure, testing API endpoints, testing database operations, mocking Gemini API calls, or establishing testing patterns for the ungouge.ai Python/FastAPI backend.
---

# Ungouge Testing

Comprehensive testing infrastructure and patterns for the ungouge.ai FastAPI backend.

## Quick Start

### 1. Set Up Test Infrastructure

Copy test configuration files to your project:

```bash
# Copy conftest.py to your tests directory
cp scripts/conftest.py ~/projects/ungouge-backend/tests/

# Install required dependencies
pip install pytest pytest-cov pytest-asyncio httpx
```

### 2. Run Tests

Use the provided test runner:

```bash
# Run all tests
python scripts/run_tests.py

# Run only unit tests (fast)
python scripts/run_tests.py --unit

# Run with coverage report
python scripts/run_tests.py --coverage

# Generate HTML coverage report
python scripts/run_tests.py --html-coverage
```

### 3. Write Your First Test

Copy and adapt the example test patterns:

```bash
cp scripts/test_example.py ~/projects/ungouge-backend/tests/test_quotes.py
```

Edit to match your actual API endpoints and models.

## Core Components

### Scripts

**`conftest.py`** - Pytest configuration with fixtures for:
- Test database setup/teardown (SQLite in-memory)
- Authentication fixtures (`auth_headers_user`, `auth_headers_admin`)
- Mock data generators (`sample_quote_data`, `sample_rsmeans_data`, `mock_gemini_response`)
- Test client with dependency overrides

**`test_example.py`** - Complete test examples demonstrating:
- FastAPI endpoint testing
- Database operation testing
- Authentication/authorization testing
- External API mocking (Gemini)
- Pydantic validation testing
- Parametrized tests
- Async testing patterns

**`run_tests.py`** - Test runner with options for:
- Selective test execution (unit/integration/security)
- Coverage reporting (terminal and HTML)
- Failed test re-running
- Verbose output
- Debugger integration

### References

**`patterns.md`** - Comprehensive testing patterns including:
- Test structure and organization
- Unit testing patterns
- Integration testing patterns
- Security testing (auth, SQL injection, rate limiting)
- Mocking strategies
- Database testing
- Coverage goals and best practices

**`fastapi_testing.md`** - FastAPI-specific guidance:
- TestClient usage
- Async endpoint testing
- Dependency overrides
- Middleware testing
- Background tasks
- WebSocket testing
- File upload testing

## Testing Workflow

### 1. Before Writing Code

**Test-Driven Development (TDD):**

```python
# Write test first (it will fail)
def test_analyze_quote_returns_fair_assessment():
    result = analyze_quote(amount=8500, market_avg=8000)
    assert result["assessment"] == "FAIR"

# Implement feature to make test pass
def analyze_quote(amount, market_avg):
    if abs(amount - market_avg) / market_avg < 0.1:
        return {"assessment": "FAIR"}
```

### 2. During Development

**Run tests frequently:**

```bash
# Run specific test file while working on it
python scripts/run_tests.py --file test_quotes.py --verbose

# Re-run only failed tests
python scripts/run_tests.py --failed
```

### 3. Before Committing

**Ensure full test suite passes:**

```bash
# Run all tests with coverage
python scripts/run_tests.py --coverage

# Verify coverage meets threshold (80%+)
pytest --cov=app --cov-fail-under=80
```

## Common Testing Scenarios

### Testing API Endpoints

```python
def test_create_quote_endpoint(test_client, auth_headers_user):
    """Test quote creation through API."""
    response = test_client.post(
        "/api/v1/quotes",
        json={
            "project_type": "HVAC",
            "quote_amount": 5000.00,
            "contractor_name": "Test Co"
        },
        headers=auth_headers_user
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["project_type"] == "HVAC"
```

### Mocking Gemini API

```python
from unittest.mock import patch, MagicMock

@patch('google.generativeai.GenerativeModel')
def test_gemini_analysis(mock_gemini, sample_quote_data):
    """Test quote analysis with mocked Gemini."""
    # Configure mock response
    mock_response = MagicMock()
    mock_response.text = '{"evaluation": "FAIR", "confidence": 0.85}'
    mock_gemini.return_value.generate_content.return_value = mock_response
    
    # Call your service
    from app.services.gemini import analyze_quote
    result = analyze_quote(sample_quote_data)
    
    assert result["evaluation"] == "FAIR"
```

### Testing Database Operations

```python
def test_create_and_retrieve_quote(db_session):
    """Test database CRUD operations."""
    from app.models import Quote
    
    # Create
    quote = Quote(
        project_type="Roofing",
        quote_amount=12000.00,
        user_id=1
    )
    db_session.add(quote)
    db_session.commit()
    
    # Retrieve
    retrieved = db_session.query(Quote).filter_by(id=quote.id).first()
    assert retrieved.project_type == "Roofing"
```

### Testing Security

```python
@pytest.mark.security
def test_endpoint_requires_authentication(test_client):
    """Verify unauthenticated requests are rejected."""
    response = test_client.get("/api/v1/quotes")
    assert response.status_code == 401

@pytest.mark.security
def test_admin_endpoint_requires_admin_role(test_client, auth_headers_user):
    """Verify regular users can't access admin endpoints."""
    response = test_client.get(
        "/api/v1/admin/analytics",
        headers=auth_headers_user
    )
    assert response.status_code == 403
```

## Customization

### Adapting conftest.py

Update `conftest.py` to match your project structure:

1. **Import your app:**
   ```python
   from app.main import app
   from app.dependencies import get_db
   from app.models import Base
   ```

2. **Configure database:**
   ```python
   Base.metadata.create_all(bind=engine)
   ```

3. **Set up dependency overrides:**
   ```python
   app.dependency_overrides[get_db] = override_get_db
   ```

### Adding Custom Fixtures

Add project-specific fixtures to `conftest.py`:

```python
@pytest.fixture
def sample_user(db_session):
    """Create a test user."""
    from app.models import User
    user = User(email="test@example.com", hashed_password="xxx")
    db_session.add(user)
    db_session.commit()
    return user
```

## Coverage Targets

**Critical paths (100% coverage):**
- Authentication and authorization
- Payment processing
- Quote analysis logic
- RSMeans cost calculations

**API endpoints (90%+ coverage):**
- All public API routes
- Request validation
- Response serialization

**Business logic (95%+ coverage):**
- Service layer functions
- Data transformations
- Calculation logic

**Overall target: 80%+ coverage**

## Resources

### Read When Needed

- **[patterns.md](references/patterns.md)** - For detailed testing patterns, mocking strategies, and best practices
- **[fastapi_testing.md](references/fastapi_testing.md)** - For FastAPI-specific testing techniques (async, dependency injection, middleware)

### Example Files

- **[conftest.py](scripts/conftest.py)** - Copy to your `tests/` directory
- **[test_example.py](scripts/test_example.py)** - Reference for common test patterns
- **[run_tests.py](scripts/run_tests.py)** - Test runner script

## Next Steps

1. **Copy conftest.py** to `~/projects/ungouge-backend/tests/`
2. **Update imports** to match your project structure
3. **Write your first test** using `test_example.py` as a template
4. **Run tests** with `python scripts/run_tests.py --verbose`
5. **Aim for 80%+ coverage** before deploying new features
6. **Consult references/** for advanced patterns as needed
