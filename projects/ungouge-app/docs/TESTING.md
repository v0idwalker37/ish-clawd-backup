# Testing Guide

Comprehensive testing strategy for Ungouge.ai v2 microservices architecture.

---

## Test Pyramid

```
        E2E Tests
      ╱           ╲
    Integration Tests
  ╱                   ╲
Unit Tests (Foundation)
```

**80% Unit** → **15% Integration** → **5% E2E**

---

## 1. Unit Tests

Test individual functions and classes in isolation.

### Running Unit Tests

```bash
# All services
pytest services/*/test_main.py -v

# Specific service
cd services/api-gateway
pytest test_main.py -v

# With coverage
pytest test_main.py -v --cov=main --cov-report=html

# Watch mode (reruns on file changes)
pytest-watch test_main.py
```

### Writing Unit Tests

**Example:** `services/cost-model/test_main.py`

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_analyze_quote():
    request = {
        "quote_id": "test-123",
        "line_items": [...],
        "location": {"zip_code": "05663"},
        "project_type": "flooring"
    }
    
    response = client.post("/analyze", json=request)
    assert response.status_code == 200
    assert "confidence_score" in response.json()
```

### Test Coverage Goals

| Component | Target | Current |
|-----------|--------|---------|
| Cost Model | >80% | TODO |
| Quote Extractor | >80% | TODO |
| Webhook Handler | >90% | TODO |
| API Gateway | >85% | TODO |

---

## 2. Integration Tests

Test interactions between services and external dependencies.

### Running Integration Tests

```bash
# Start services
docker-compose up -d

# Run integration tests
pytest tests/integration/ -v

# Stop services
docker-compose down
```

### Test Categories

**Service-to-Service:**
- API Gateway → Cost Model
- API Gateway → Quote Extractor
- Webhook Handler → Pub/Sub

**Service-to-Database:**
- User registration
- Quote creation
- Order processing

**Service-to-External:**
- Vision API (OCR)
- Stripe webhooks
- Redis caching

### Example Integration Test

```python
# tests/integration/test_quote_flow.py

async def test_full_quote_analysis_flow():
    # 1. Upload quote
    upload_response = await client.post("/api/v2/quotes/upload", ...)
    quote_id = upload_response.json()["quote_id"]
    
    # 2. Extract data (calls Quote Extractor)
    extract_response = await client.post("/api/v2/quotes/extract", ...)
    assert extract_response.status_code == 200
    
    # 3. Analyze costs (calls Cost Model)
    analyze_response = await client.post("/api/v2/quotes/analyze", ...)
    assert analyze_response.status_code == 200
    assert "verdict" in analyze_response.json()
```

---

## 3. End-to-End Tests

Test complete user workflows using real browser automation.

### Running E2E Tests

```bash
# Install Playwright
npm install -g playwright
playwright install

# Run E2E tests
pytest tests/e2e/ --headed

# Specific test
pytest tests/e2e/test_user_journey.py::test_signup_to_quote
```

### Example E2E Test

```python
# tests/e2e/test_user_journey.py

async def test_signup_to_quote(page):
    # 1. User signs up
    await page.goto("http://localhost:3000/signup")
    await page.fill("#email", "test@example.com")
    await page.fill("#password", "SecurePassword123!")
    await page.click("button[type=submit]")
    
    # 2. Upload quote
    await page.goto("http://localhost:3000/upload")
    await page.set_input_files("#quote-file", "test_quote.pdf")
    await page.click("button#upload")
    
    # 3. View analysis
    await page.wait_for_selector(".analysis-result")
    verdict = await page.text_content(".verdict")
    assert verdict in ["Fair", "Overpriced", "Suspiciously Low"]
```

---

## 4. Load Testing

Test system performance under load using **Locust**.

### Running Load Tests

```bash
# Install locust
pip install locust

# Run load test
locust -f tests/load/locustfile.py --host=http://localhost:8000

# Open browser to http://localhost:8089
# Configure: Users=100, Spawn rate=10
```

### Example Load Test

```python
# tests/load/locustfile.py

from locust import HttpUser, task, between

class QuoteUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def analyze_quote(self):
        self.client.post("/api/v2/quotes/analyze", json={...})
    
    @task(1)
    def get_profile(self):
        self.client.get("/api/v2/auth/profile")
```

### Performance Targets

| Endpoint | p50 | p95 | p99 |
|----------|-----|-----|-----|
| /health/live | <50ms | <100ms | <200ms |
| /analyze | <2s | <5s | <10s |
| /extract | <10s | <30s | <60s |

---

## 5. Security Testing

### Static Analysis

```bash
# Bandit (security linter)
bandit -r services/ -f json -o bandit-report.json

# Safety (dependency vulnerabilities)
safety check --json
```

### Vulnerability Scanning

```bash
# Scan Docker images
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image \
  gcr.io/gen-lang-client-0199462206/api-gateway:latest
```

### Penetration Testing

```bash
# OWASP ZAP
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t http://localhost:8000
```

---

## 6. Smoke Tests

Quick sanity checks after deployment.

### Staging Smoke Tests

```bash
# Health checks
curl -f https://staging.ungouge.ai/health/live
curl -f https://staging.ungouge.ai/health/ready

# Basic functionality
curl -X POST https://staging.ungouge.ai/api/v2/quotes/analyze \
  -H "Content-Type: application/json" \
  -d '{"quote_id": "smoke-test", ...}'
```

### Production Smoke Tests

Run automatically after deployment via GitHub Actions.

---

## 7. Test Data

### Fixtures

```python
# tests/fixtures.py

@pytest.fixture
def sample_quote():
    return {
        "quote_id": "test-123",
        "line_items": [
            {"description": "Labor", "quantity": 40, "unit": "hours", "unit_price": 50.0},
            {"description": "Materials", "quantity": 1, "unit": "lot", "unit_price": 1000.0}
        ],
        "location": {"zip_code": "05663", "state": "VT"},
        "project_type": "flooring",
        "total_quoted": 3000.0
    }

@pytest.fixture
def authenticated_user():
    # Create test user, return JWT token
    pass
```

### Factories

```python
# tests/factories.py

import factory
from models import User, Quote

class UserFactory(factory.Factory):
    class Meta:
        model = User
    
    email = factory.Faker('email')
    password_hash = "hashed_password"

class QuoteFactory(factory.Factory):
    class Meta:
        model = Quote
    
    user_id = factory.SubFactory(UserFactory)
    file_url = "https://example.com/quote.pdf"
    status = "pending"
```

---

## 8. Continuous Testing (CI/CD)

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml

name: Test Suite

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run unit tests
        run: pytest services/*/test_main.py -v --cov
  
  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Start services
        run: docker-compose up -d
      - name: Run integration tests
        run: pytest tests/integration/ -v
```

---

## 9. Test Best Practices

### DO ✅
- **Test behavior, not implementation**
- **Use descriptive test names:** `test_analyze_returns_overpriced_verdict_when_quote_exceeds_fair_range`
- **One assertion per test** (when possible)
- **Mock external dependencies** (Vision API, Stripe, etc.)
- **Use fixtures for common setup**
- **Keep tests fast** (<1s per unit test)
- **Clean up after tests** (delete test data)

### DON'T ❌
- **Don't test framework code** (FastAPI internals)
- **Don't use production credentials**
- **Don't skip flaky tests** (fix them!)
- **Don't test implementation details**
- **Don't use sleep() for timing** (use proper async waits)

---

## 10. Debugging Failed Tests

### View test output

```bash
pytest test_main.py -v -s  # -s shows print statements
```

### Debug specific test

```bash
pytest test_main.py::test_analyze_quote -v --pdb
```

### Check logs

```bash
docker-compose logs api-gateway
docker-compose logs cost-model
```

### Interactive debugging

```python
# Add to test
import pdb; pdb.set_trace()

# Or use breakpoint() (Python 3.7+)
breakpoint()
```

---

## Summary

| Test Type | Tools | When | Coverage |
|-----------|-------|------|----------|
| Unit | pytest | Every commit | 80%+ |
| Integration | pytest + docker-compose | Every PR | Key flows |
| E2E | Playwright | Before deploy | Critical paths |
| Load | Locust | Weekly | Bottlenecks |
| Security | Bandit, Trivy | Every deploy | All images |
| Smoke | curl | After deploy | Health checks |

---

**Next Steps:**
1. Write missing unit tests (current coverage: TODO)
2. Implement integration test suite
3. Set up E2E tests with Playwright
4. Configure load testing in staging
5. Add security scanning to CI/CD
