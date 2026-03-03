# Testing Patterns for Ungouge.ai Backend

Comprehensive testing patterns and best practices for FastAPI applications.

## Table of Contents

1. [Test Structure](#test-structure)
2. [Unit Testing Patterns](#unit-testing-patterns)
3. [Integration Testing Patterns](#integration-testing-patterns)
4. [Security Testing](#security-testing)
5. [Mocking External Services](#mocking-external-services)
6. [Database Testing](#database-testing)
7. [Coverage Goals](#coverage-goals)

---

## Test Structure

### Organizing Test Files

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── unit/
│   ├── test_schemas.py      # Pydantic model validation
│   ├── test_auth.py         # Authentication logic
│   ├── test_services.py     # Business logic
│   └── test_utils.py        # Utility functions
├── integration/
│   ├── test_api_quotes.py   # Quote endpoints
│   ├── test_api_auth.py     # Auth endpoints
│   └── test_database.py     # DB operations
└── security/
    ├── test_auth_security.py
    ├── test_input_validation.py
    └── test_rate_limiting.py
```

### Test Naming Convention

```python
def test_<function>_<scenario>_<expected_result>():
    """
    Clear description of what is being tested.
    """
```

**Examples:**
- `test_create_quote_with_valid_data_returns_201()`
- `test_login_with_invalid_password_returns_401()`
- `test_analyze_quote_with_negative_amount_raises_validation_error()`

---

## Unit Testing Patterns

### Testing Pydantic Models

```python
from pydantic import ValidationError
import pytest

def test_quote_model_validates_positive_amount():
    """Ensure quote amounts must be positive."""
    from app.schemas import QuoteCreate
    
    # Valid case
    quote = QuoteCreate(
        project_type="HVAC",
        quote_amount=5000.00,
        contractor_name="Test Co"
    )
    assert quote.quote_amount == 5000.00
    
    # Invalid case
    with pytest.raises(ValidationError) as exc:
        QuoteCreate(
            project_type="HVAC",
            quote_amount=-100,
            contractor_name="Test Co"
        )
    assert "greater than 0" in str(exc.value)
```

### Testing Business Logic

```python
def test_calculate_gouge_score_fair_price():
    """Test gouge score calculation for fair pricing."""
    from app.services.analysis import calculate_gouge_score
    
    result = calculate_gouge_score(
        quoted_price=8500,
        market_avg=8000,
        market_std_dev=1000
    )
    
    assert result["score"] < 0.5  # Fair price
    assert result["assessment"] == "FAIR"
```

### Testing Utility Functions

```python
@pytest.mark.parametrize("location,expected_factor", [
    ("Burlington, VT", 0.98),
    ("New York, NY", 1.38),
    ("Jackson, MS", 0.82),
])
def test_get_location_factor(location, expected_factor):
    """Test location cost factor lookup."""
    from app.utils.location import get_location_factor
    
    factor = get_location_factor(location)
    assert abs(factor - expected_factor) < 0.01
```

---

## Integration Testing Patterns

### Testing API Endpoints

```python
@pytest.mark.integration
def test_analyze_quote_endpoint_full_flow(
    test_client,
    auth_headers_user,
    sample_quote_data
):
    """Test complete quote analysis flow through API."""
    # Submit quote
    response = test_client.post(
        "/api/v1/quotes/analyze",
        json=sample_quote_data,
        headers=auth_headers_user
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "analysis" in data
    assert "id" in data
    assert "created_at" in data
    
    # Verify analysis content
    analysis = data["analysis"]
    assert analysis["total_evaluation"] in ["FAIR", "HIGH", "POSSIBLE_GOUGE"]
    assert 0 <= analysis["gouge_likelihood"] <= 1
    assert len(analysis["line_item_analysis"]) > 0
```

### Testing Error Responses

```python
@pytest.mark.integration
def test_api_returns_proper_error_format(test_client):
    """Ensure all errors follow consistent format."""
    response = test_client.post(
        "/api/v1/quotes/analyze",
        json={"invalid": "data"}
    )
    
    assert response.status_code in [400, 401, 422]
    data = response.json()
    assert "detail" in data  # FastAPI standard error format
```

### Testing Database Transactions

```python
@pytest.mark.integration
def test_quote_creation_rollback_on_error(db_session):
    """Verify transaction rollback on error."""
    from app.models import Quote
    from app.services.quote import create_quote
    
    initial_count = db_session.query(Quote).count()
    
    # Force an error during creation
    with pytest.raises(Exception):
        with db_session.begin():
            create_quote(db_session, invalid_data)
    
    # Verify rollback
    final_count = db_session.query(Quote).count()
    assert final_count == initial_count
```

---

## Security Testing

### Testing Authentication

```python
@pytest.mark.security
def test_jwt_token_expiration():
    """Ensure expired tokens are rejected."""
    from app.auth import create_access_token, verify_token
    from jose import ExpiredSignatureError
    import time
    
    # Create token with 1-second expiry
    token = create_access_token(
        {"sub": "test@example.com"},
        expires_delta=timedelta(seconds=1)
    )
    
    time.sleep(2)
    
    with pytest.raises(ExpiredSignatureError):
        verify_token(token)
```

### Testing Authorization

```python
@pytest.mark.security
@pytest.mark.parametrize("endpoint,required_role", [
    ("/api/v1/admin/analytics", "admin"),
    ("/api/v1/admin/users", "admin"),
])
def test_endpoint_requires_role(
    test_client,
    auth_headers_user,
    endpoint,
    required_role
):
    """Verify role-based access control."""
    # Regular user should be denied
    response = test_client.get(endpoint, headers=auth_headers_user)
    assert response.status_code == 403
```

### Testing Input Sanitization

```python
@pytest.mark.security
def test_sql_injection_protection(test_client, auth_headers_user):
    """Verify SQL injection attempts are neutralized."""
    malicious_input = {
        "project_type": "'; DROP TABLE quotes; --",
        "contractor_name": "Robert'; DROP TABLE users; --"
    }
    
    response = test_client.post(
        "/api/v1/quotes/analyze",
        json=malicious_input,
        headers=auth_headers_user
    )
    
    # Should either validate and reject, or safely escape
    # (Either 422 validation error or 200 with escaped data)
    assert response.status_code in [200, 422]
```

### Testing Rate Limiting

```python
@pytest.mark.security
@pytest.mark.slow
def test_rate_limiting_enforced(test_client, auth_headers_user):
    """Verify rate limiting prevents abuse."""
    endpoint = "/api/v1/quotes/analyze"
    
    # Make requests up to the limit
    responses = []
    for _ in range(11):  # Assuming limit is 10/minute
        response = test_client.post(
            endpoint,
            json={"test": "data"},
            headers=auth_headers_user
        )
        responses.append(response.status_code)
    
    # At least one should be rate limited
    assert 429 in responses  # Too Many Requests
```

---

## Mocking External Services

### Mocking Gemini API

```python
from unittest.mock import patch, MagicMock

@pytest.mark.unit
@patch('google.generativeai.GenerativeModel')
def test_gemini_analysis_with_mock(mock_gemini):
    """Test Gemini integration with mocked response."""
    # Configure mock
    mock_response = MagicMock()
    mock_response.text = '''{
        "evaluation": "FAIR",
        "confidence": 0.85,
        "reasoning": "Price within market range"
    }'''
    mock_gemini.return_value.generate_content.return_value = mock_response
    
    from app.services.gemini import analyze_quote
    result = analyze_quote({"amount": 5000})
    
    assert result["evaluation"] == "FAIR"
    assert result["confidence"] == 0.85
```

### Mocking Database Queries

```python
from unittest.mock import MagicMock

def test_service_with_mocked_db():
    """Test service layer with mocked database."""
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = Quote(
        id=1,
        project_type="HVAC",
        quote_amount=5000
    )
    
    from app.services.quote import get_quote_by_id
    quote = get_quote_by_id(mock_db, 1)
    
    assert quote.id == 1
    assert quote.project_type == "HVAC"
```

### Mocking HTTP Requests

```python
import responses

@responses.activate
def test_external_api_call():
    """Test external API with mocked HTTP responses."""
    responses.add(
        responses.GET,
        "https://api.external.com/data",
        json={"status": "success", "data": []},
        status=200
    )
    
    from app.services.external import fetch_data
    result = fetch_data()
    
    assert result["status"] == "success"
```

---

## Database Testing

### Testing Queries

```python
@pytest.mark.integration
def test_query_quotes_by_date_range(db_session):
    """Test filtering quotes by date."""
    from app.models import Quote
    from datetime import datetime, timedelta
    
    # Create test data
    today = datetime.utcnow()
    yesterday = today - timedelta(days=1)
    
    quote1 = Quote(project_type="A", created_at=today, quote_amount=1000)
    quote2 = Quote(project_type="B", created_at=yesterday, quote_amount=2000)
    db_session.add_all([quote1, quote2])
    db_session.commit()
    
    # Query
    from app.services.quote import get_quotes_in_range
    results = get_quotes_in_range(
        db_session,
        start_date=today.date(),
        end_date=today.date()
    )
    
    assert len(results) == 1
    assert results[0].project_type == "A"
```

### Testing Relationships

```python
@pytest.mark.integration
def test_user_quotes_relationship(db_session):
    """Test ORM relationship between User and Quote."""
    from app.models import User, Quote
    
    user = User(email="test@example.com", hashed_password="xxx")
    db_session.add(user)
    db_session.commit()
    
    quote1 = Quote(user_id=user.id, project_type="A", quote_amount=1000)
    quote2 = Quote(user_id=user.id, project_type="B", quote_amount=2000)
    db_session.add_all([quote1, quote2])
    db_session.commit()
    
    # Test relationship
    db_session.refresh(user)
    assert len(user.quotes) == 2
```

---

## Coverage Goals

### Target Coverage Levels

- **Overall**: 80%+ code coverage
- **Critical paths**: 100% (auth, payment, analysis)
- **API endpoints**: 90%+
- **Business logic**: 95%+
- **Utility functions**: 85%+

### Running Coverage Reports

```bash
# Terminal report
pytest --cov=app --cov-report=term-missing

# HTML report
pytest --cov=app --cov-report=html
open htmlcov/index.html

# Fail if coverage below threshold
pytest --cov=app --cov-fail-under=80
```

### What to Test

**High Priority:**
- Authentication and authorization
- Data validation
- Business logic calculations
- External API integrations
- Database operations
- Error handling

**Medium Priority:**
- Utility functions
- Data transformations
- Logging behavior

**Lower Priority:**
- Configuration loading
- Simple getters/setters
- Straightforward CRUD operations

### What NOT to Test

- Third-party library internals
- Framework behavior (FastAPI, Pydantic)
- Generated code
- Trivial property accessors

---

## Best Practices

1. **Arrange-Act-Assert Pattern**
   ```python
   def test_example():
       # Arrange: Set up test data
       user = create_test_user()
       
       # Act: Execute the behavior
       result = authenticate(user.email, "password")
       
       # Assert: Verify the outcome
       assert result.is_authenticated
   ```

2. **One Assertion Per Test** (when practical)
   - Makes failures easier to diagnose
   - Each test has a single responsibility

3. **Use Descriptive Test Names**
   - `test_login_with_invalid_email_returns_400` ✅
   - `test_login_error` ❌

4. **Keep Tests Independent**
   - Tests should not depend on execution order
   - Each test should set up its own data

5. **Test Edge Cases**
   - Empty strings, null values
   - Maximum/minimum boundaries
   - Unexpected data types

6. **Use Fixtures for Common Setup**
   - Reduces duplication
   - Makes tests more readable

7. **Mock External Dependencies**
   - Tests should be fast and reliable
   - Don't rely on external services being available

8. **Write Tests First for Bug Fixes**
   - Reproduce the bug with a failing test
   - Fix the code
   - Verify test passes

---

## Common Pitfalls to Avoid

❌ **Testing Implementation Details**
```python
# Bad: Testing internal state
def test_cache_implementation():
    assert service._cache == {}
```

✅ **Testing Behavior**
```python
# Good: Testing observable behavior
def test_caching_improves_performance():
    first_call_time = measure_time(service.get_data())
    second_call_time = measure_time(service.get_data())
    assert second_call_time < first_call_time
```

❌ **Overly Complex Tests**
```python
# Bad: Too much setup
def test_complex():
    user = User()
    quote = Quote()
    analysis = Analysis()
    # 50 lines of setup...
    assert something
```

✅ **Simple, Focused Tests**
```python
# Good: Use fixtures for complex setup
def test_simple(user, quote, analysis):
    assert something
```
