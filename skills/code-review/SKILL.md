---
name: code-review
description: Security-first code review checklist and patterns for ungouge.ai. Covers security vulnerabilities, API design validation, performance patterns, type safety, error handling, and code quality standards. Use when reviewing pull requests, auditing code for security issues, validating API designs, checking for performance problems, ensuring type safety, or enforcing code quality standards.
---

# Code Review

Security-first code review checklist and quality standards for ungouge.ai.

## Quick Review Checklist

Before approving any PR, verify:

### 🔒 Security (CRITICAL)

- [ ] **No hardcoded secrets** (API keys, passwords, tokens)
- [ ] **Input validation** on all user inputs
- [ ] **SQL injection protection** (parameterized queries or ORM)
- [ ] **Authentication required** on protected endpoints
- [ ] **Authorization checks** (user can only access their data)
- [ ] **Rate limiting** on public/expensive endpoints
- [ ] **CORS configured properly** (no wildcard in production)
- [ ] **Sensitive data not logged** (passwords, tokens, PII)

### 🛡️ Data Protection

- [ ] **PII handled correctly** (encrypted at rest, masked in logs)
- [ ] **Database queries scoped to user** (no data leakage)
- [ ] **File uploads validated** (type, size, content)
- [ ] **External API responses validated** (don't trust external data)

### 🔍 Code Quality

- [ ] **Type hints** on all functions
- [ ] **Error handling** (no bare `except:`)
- [ ] **Logging** for debugging and audit trails
- [ ] **No commented-out code**
- [ ] **Functions under 50 lines** (decompose if larger)
- [ ] **Clear variable names** (no `x`, `data`, `temp`)

### ⚡ Performance

- [ ] **Database queries optimized** (no N+1, proper indexes)
- [ ] **Async used for I/O** (external APIs, database)
- [ ] **Pagination on list endpoints**
- [ ] **Caching where appropriate**
- [ ] **No blocking operations in async functions**

### 🧪 Testing

- [ ] **Tests included** for new functionality
- [ ] **Edge cases covered** (empty inputs, errors)
- [ ] **Mocks used** for external services

---

## Security Patterns

### ❌ Vulnerable Patterns

**SQL Injection:**
```python
# DANGEROUS - Never do this
query = f"SELECT * FROM quotes WHERE id = {user_input}"
db.execute(query)
```

**Hardcoded Secrets:**
```python
# DANGEROUS - Never do this
API_KEY = "sk-1234567890abcdef"
```

**Missing Auth:**
```python
# DANGEROUS - No authentication
@app.get("/admin/users")
def get_all_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

**Logging Sensitive Data:**
```python
# DANGEROUS - Logs password
logger.info(f"Login attempt: {email}, {password}")
```

### ✅ Secure Patterns

**Parameterized Queries:**
```python
# SAFE - Parameterized
db.query(Quote).filter(Quote.id == quote_id).first()
```

**Environment Variables:**
```python
# SAFE - From environment
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not configured")
```

**Proper Auth:**
```python
# SAFE - Requires authentication
@app.get("/admin/users")
def get_all_users(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    return db.query(User).all()
```

**Safe Logging:**
```python
# SAFE - No sensitive data
logger.info(f"Login attempt for user: {email}")
```

---

## API Design Validation

### Request/Response Patterns

**Good Response Structure:**
```python
class QuoteResponse(BaseModel):
    id: int
    project_type: str
    quote_amount: float
    created_at: datetime
    
    class Config:
        from_attributes = True  # For ORM compatibility
```

**Proper Error Responses:**
```python
# Return consistent error format
{
    "detail": "Quote not found",
    "error_code": "QUOTE_NOT_FOUND",
    "timestamp": "2026-03-03T09:00:00Z"
}
```

### Endpoint Naming

✅ **Good:**
- `GET /api/v1/quotes` - List quotes
- `POST /api/v1/quotes` - Create quote
- `GET /api/v1/quotes/{id}` - Get specific quote
- `PUT /api/v1/quotes/{id}` - Update quote
- `DELETE /api/v1/quotes/{id}` - Delete quote
- `POST /api/v1/quotes/{id}/analyze` - Action on quote

❌ **Bad:**
- `GET /api/v1/getQuotes`
- `POST /api/v1/createNewQuote`
- `GET /api/v1/quote_by_id`

---

## Error Handling

### ❌ Bad Error Handling

```python
# Too broad - catches everything
try:
    result = process_quote(data)
except:
    return {"error": "Something went wrong"}

# Leaks internal details
except Exception as e:
    return {"error": str(e)}  # May expose SQL, paths, etc.
```

### ✅ Good Error Handling

```python
try:
    result = await analyze_quote(data)
except QuoteNotFoundError as e:
    raise HTTPException(status_code=404, detail=str(e))
except ExternalServiceError as e:
    logger.error(f"External service failed: {e}")
    raise HTTPException(
        status_code=503,
        detail="Analysis service temporarily unavailable"
    )
except ValidationError as e:
    raise HTTPException(status_code=422, detail=e.errors())
except Exception as e:
    logger.exception("Unexpected error in analyze_quote")
    raise HTTPException(
        status_code=500,
        detail="An unexpected error occurred"
    )
```

---

## Performance Review

### Database Query Checks

**Check for N+1:**
```python
# BAD - N+1 queries
quotes = db.query(Quote).all()
for quote in quotes:
    print(quote.user.email)  # Separate query per quote!

# GOOD - Eager loading
quotes = db.query(Quote).options(joinedload(Quote.user)).all()
```

**Check for Missing Pagination:**
```python
# BAD - Returns entire table
@app.get("/quotes")
def list_quotes(db: Session = Depends(get_db)):
    return db.query(Quote).all()

# GOOD - Paginated
@app.get("/quotes")
def list_quotes(
    page: int = 1,
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit
    return db.query(Quote).offset(offset).limit(limit).all()
```

### Async Checks

```python
# BAD - Blocking call in async function
@app.get("/analyze")
async def analyze():
    result = requests.get(API_URL)  # Blocks event loop!
    return result.json()

# GOOD - Async HTTP client
@app.get("/analyze")
async def analyze():
    async with httpx.AsyncClient() as client:
        result = await client.get(API_URL)
    return result.json()
```

---

## Type Safety

### Required Type Hints

```python
# All functions must have type hints
def calculate_gouge_score(
    quoted_price: float,
    market_avg: float,
    location_factor: float = 1.0
) -> dict[str, Any]:
    """Calculate gouge likelihood score."""
    ...

# Use Optional for nullable
def get_user_by_email(
    db: Session,
    email: str
) -> Optional[User]:
    ...

# Use Union for multiple types
def process_input(
    data: Union[str, dict[str, Any]]
) -> ProcessedResult:
    ...
```

### Pydantic Model Requirements

```python
class QuoteCreate(BaseModel):
    # Use Field for validation
    project_type: str = Field(..., min_length=3, max_length=100)
    quote_amount: float = Field(..., gt=0, le=1000000)
    contractor_name: str = Field(..., min_length=2)
    
    # Add custom validators
    @field_validator('project_type')
    @classmethod
    def validate_project_type(cls, v: str) -> str:
        allowed = ['HVAC', 'Roofing', 'Electrical', 'Plumbing']
        if v not in allowed:
            raise ValueError(f'Must be one of: {allowed}')
        return v
```

---

## Review Comments Guide

### Blocking Issues (Must Fix)

Use **"BLOCKING:"** prefix:
```
BLOCKING: This endpoint lacks authentication. Add `current_user: User = Depends(get_current_user)` as a dependency.
```

### Suggestions (Should Consider)

Use **"SUGGESTION:"** prefix:
```
SUGGESTION: Consider adding an index on `quotes.user_id` for faster lookups.
```

### Questions (Need Clarification)

Use **"QUESTION:"** prefix:
```
QUESTION: Is this timeout value intentional? 60 seconds seems long for a health check.
```

### Praise (Acknowledge Good Work)

Use **"NICE:"** prefix:
```
NICE: Good use of dependency injection here. Clean and testable.
```

---

## Pre-Merge Checklist

### For All PRs

- [ ] CI pipeline passes
- [ ] No merge conflicts
- [ ] Commit messages are clear
- [ ] PR description explains the change
- [ ] Self-reviewed before requesting review

### For Feature PRs

- [ ] Tests added/updated
- [ ] Documentation updated if needed
- [ ] Migration included if schema changed
- [ ] Feature flag if needed for gradual rollout

### For Bug Fixes

- [ ] Test reproduces the bug (fails before fix)
- [ ] Test passes after fix
- [ ] Root cause documented in PR

### For Security Fixes

- [ ] Fix reviewed by second person
- [ ] No details in public commit message
- [ ] Affected users notified if needed
- [ ] Credentials rotated if exposed

---

## Quick Commands

**Run security scan:**
```bash
pip install bandit
bandit -r app/ -ll
```

**Run type check:**
```bash
pip install mypy
mypy app/ --ignore-missing-imports
```

**Run linter:**
```bash
pip install ruff
ruff check app/
```

**Check for hardcoded secrets:**
```bash
# Quick grep for common patterns
grep -rn "api_key\|password\|secret\|token" --include="*.py" app/ | grep -v "\.pyc"
```

---

## Summary

**Priority Order for Review:**
1. 🔒 **Security** - Check for vulnerabilities first
2. 🛡️ **Data Protection** - Verify user data is protected
3. ✅ **Correctness** - Does the code do what it should?
4. ⚡ **Performance** - Will it scale?
5. 📖 **Readability** - Can others maintain it?

**When in doubt:** Ask questions rather than approving. A 10-minute discussion now prevents a 10-hour debugging session later.
