# Backend Security & Code Audit Report
**Project:** Ungouge.ai  
**Date:** 2026-02-06  
**Scope:** `/backend/` - FastAPI backend code  
**Auditor:** AI Code Review (Opus 4.6)

---

## Executive Summary

The Ungouge.ai backend demonstrates **solid security fundamentals** with proper authentication, input validation, rate limiting, and error handling. However, several issues ranging from **critical to low severity** were identified that should be addressed before production deployment.

### Summary by Severity
| Severity | Count | Status |
|----------|-------|--------|
| 🔴 Critical | 2 | Requires immediate fix |
| 🟠 High | 5 | Fix before production |
| 🟡 Medium | 8 | Should fix soon |
| 🔵 Low | 7 | Best practice improvements |

### Overall Assessment
- **Authentication:** Good - JWT with blacklist, bcrypt hashing, timing-safe comparisons
- **Authorization:** Good - Proper ownership checks on quotes
- **Input Validation:** Good - Comprehensive validators with user-friendly errors
- **Rate Limiting:** Good - Per-endpoint limits via SlowAPI
- **Error Handling:** Good - Custom exceptions, no stack trace leakage
- **Logging:** Good - Structured JSON logging for security events
- **Database:** Adequate - Async SQLAlchemy with proper indexing

---

## 🔴 Critical Issues

### 1. Hardcoded Default Secret Key
**File:** `main.py:17`, `services/auth.py:17`  
**Risk:** Authentication bypass, token forgery

```python
# main.py:17
secret_key: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")

# services/auth.py:17
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
```

**Problem:** If `JWT_SECRET_KEY` environment variable is not set, anyone can forge valid JWT tokens using the known default secret.

**Fix:**
```python
# Require the secret key - fail fast if not set
SECRET_KEY = os.environ["JWT_SECRET_KEY"]  # Raises KeyError if missing

# Or validate at startup
secret_key = os.getenv("JWT_SECRET_KEY")
if not secret_key or secret_key == "your-secret-key-change-in-production":
    raise RuntimeError("JWT_SECRET_KEY must be set to a secure random value")
```

---

### 2. Verification/Reset Tokens Logged in Production
**File:** `routers/auth.py:122-127`, `routers/auth.py:338-345`, `routers/auth.py:390-397`, `routers/auth.py:450-457`

```python
# routers/auth.py:122-127
logger.info(
    "email_verification_sent",
    extra={
        "user_id": user_id,
        "token": verification_token,  # REMOVE IN PRODUCTION
        "note": "Check logs for verification token (dev only)"
    }
)
```

**Problem:** Comments say "REMOVE IN PRODUCTION" but there's no mechanism to ensure this happens. If logs are shipped to a central logging system (CloudWatch, Datadog, etc.), tokens could be exposed to anyone with log access.

**Fix:**
```python
if os.getenv("ENVIRONMENT") != "production":
    logger.info(
        "email_verification_sent",
        extra={"user_id": user_id, "token": verification_token}
    )
else:
    logger.info(
        "email_verification_sent", 
        extra={"user_id": user_id}  # No token in production
    )
```

---

## 🟠 High Severity Issues

### 3. Missing Authentication on `/api/quotes` List Endpoint
**File:** `routers/quotes.py:179-196`

```python
@router.get("/quotes")
async def list_quotes(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """
    List all quotes (for admin/debugging)
    """
```

**Problem:** This endpoint lists ALL quotes from ALL users with no authentication. This is a data leak vulnerability.

**Fix:** Either remove this endpoint or require admin authentication:
```python
@router.get("/quotes")
async def list_quotes(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Require admin role
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
```

---

### 4. Missing Authentication on `/api/quotes/{quote_id}/report`
**File:** `routers/quotes.py:167-177`

```python
@router.get("/quotes/{quote_id}/report", response_model=ReportModel)
async def get_quote_full_report(
    quote_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get full analysis report for a specific quote
    This is an alias for GET /quotes/{quote_id} for clearer API semantics
    """
    return await get_quote_report(quote_id, db)  # Missing current_user!
```

**Problem:** The `get_quote_report` function expects `current_user` but this endpoint doesn't pass it, bypassing ownership checks.

**Fix:**
```python
@router.get("/quotes/{quote_id}/report", response_model=ReportModel)
async def get_quote_full_report(
    quote_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    return await get_quote_report(quote_id, db, current_user)
```

---

### 5. Token Blacklist Doesn't Persist Across Restarts
**File:** `services/token_blacklist.py:10-13`

```python
# In-memory cache for development (replace with Redis in production)
_blacklist_cache = {}
```

**Problem:** If the server restarts, all blacklisted tokens (logged out users) become valid again. This undermines the logout functionality.

**Fix:** Implement Redis-based blacklist for production (code is already commented in the file) or use database persistence:
```python
# Use environment variable to switch implementations
if os.getenv("REDIS_URL"):
    # Use Redis implementation
else:
    # Use database-backed implementation or warn loudly
    logger.warning("Token blacklist using in-memory storage - NOT SUITABLE FOR PRODUCTION")
```

---

### 6. No Password Validation on Reset
**File:** `routers/auth.py:351-405`

```python
@router.post("/auth/reset-password", response_model=MessageResponse)
async def reset_password(request: PasswordResetVerify, ...):
    ...
    # Update password - No validation!
    user.password_hash = hash_password(request.new_password)
```

**Problem:** The password reset endpoint doesn't validate the new password strength (unlike registration which uses `validate_password`). Users could reset to "12345678".

**Fix:**
```python
from validators import validate_password

# Validate new password strength
try:
    validate_password(request.new_password)
except ValidationError as e:
    raise HTTPException(status_code=400, detail=str(e))

user.password_hash = hash_password(request.new_password)
```

---

### 7. Missing Input Validation on Profile Update Email
**File:** `routers/auth.py:251-296`

```python
@router.put("/auth/me", response_model=UserProfile)
async def update_user_profile(updates: UserUpdate, ...):
    if updates.email and updates.email != current_user.email:
        # No validation/normalization of email!
        current_user.email = updates.email
```

**Problem:** Unlike registration, the email update doesn't normalize the email or validate format properly (relies only on Pydantic `EmailStr`).

**Fix:**
```python
from validators import validate_email

if updates.email and updates.email != current_user.email:
    try:
        normalized_email = validate_email(updates.email)
    except InvalidDataFormatError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Check uniqueness with normalized email
    result = await db.execute(
        select(User).where(User.email == normalized_email)
    )
```

---

## 🟡 Medium Severity Issues

### 8. No Pagination Limit on Quotes List
**File:** `routers/quotes.py:149-165`, `routers/quotes.py:179-196`

```python
async def get_my_quotes(
    skip: int = 0,
    limit: int = 10,  # No max limit validation
    ...
):
```

**Problem:** A malicious user could request `limit=1000000` causing DoS via memory exhaustion.

**Fix:**
```python
from fastapi import Query

async def get_my_quotes(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),  # Max 100
    ...
):
```

---

### 9. Old Tokens Not Invalidated on Password Change
**File:** `routers/auth.py:351-405`

**Problem:** When a user resets their password, existing access tokens remain valid until expiry. If an attacker has stolen a token, the password reset doesn't revoke their access.

**Fix:** Track a "password changed at" timestamp and invalidate tokens issued before that time:
```python
# In User model
password_changed_at: Mapped[datetime] = mapped_column(DateTime)

# In verify_token
if payload.get("iat") < user.password_changed_at.timestamp():
    raise HTTPException(status_code=401, detail="Token invalidated by password change")
```

---

### 10. Email Verification Not Required for Login
**File:** `routers/auth.py:146-193`

```python
# Login allows unverified emails
if not user.is_active:
    raise AccountInactiveError()
# No check for user.is_verified!
```

**Problem:** Users can use the platform fully without verifying their email, reducing email deliverability trust and allowing throwaway emails.

**Fix:** Decide on policy - either require verification or track it:
```python
# Option 1: Warn but allow
if not user.is_verified:
    # Include warning in response or send reminder email
    
# Option 2: Require for certain features
# Check is_verified in endpoints that require trusted email
```

---

### 11. Race Condition in Token Blacklist Cleanup
**File:** `services/token_blacklist.py:34-44`

```python
@staticmethod
def _cleanup():
    now = datetime.utcnow()
    expired_tokens = [
        token for token, expires_at in _blacklist_cache.items()
        if now > expires_at
    ]
    for token in expired_tokens:
        del _blacklist_cache[token]  # Not thread-safe
```

**Problem:** In async/multi-worker environments, this dict modification during iteration could cause issues.

**Fix:**
```python
import threading
_lock = threading.Lock()

@staticmethod
def _cleanup():
    with _lock:
        now = datetime.utcnow()
        expired = [t for t, exp in _blacklist_cache.items() if now > exp]
        for token in expired:
            _blacklist_cache.pop(token, None)
```

---

### 12. Quote Parser Timeouts Could Block Workers
**File:** `services/quote_parser.py:90-97`, `services/quote_parser.py:114-121`

```python
response = openai_client.chat.completions.create(
    ...
    timeout=30  # 30 second timeout
)
```

**Problem:** 30-second timeout per API call could tie up workers. With multiple slow requests, the service degrades.

**Fix:** Use shorter timeouts and background processing:
```python
# Reduce timeout
timeout=15

# Or better: queue analysis jobs and return immediately
# Then poll for results or use webhooks
```

---

### 13. CSRF Token Uses Same Secret as JWT
**File:** `main.py:17`

```python
class CsrfSettings(BaseModel):
    secret_key: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
```

**Problem:** CSRF and JWT should use different secrets. If JWT secret leaks, CSRF is also compromised.

**Fix:**
```python
secret_key: str = os.getenv("CSRF_SECRET_KEY", os.getenv("JWT_SECRET_KEY", "..."))
```

---

### 14. No Cleanup of Expired Reset/Verification Tokens
**File:** `models/database.py`

**Problem:** `PasswordResetToken` and `EmailVerificationToken` tables grow indefinitely. No mechanism removes expired tokens.

**Fix:** Add periodic cleanup task:
```python
# In lifespan or as cron job
async def cleanup_expired_tokens(db: AsyncSession):
    await db.execute(
        delete(PasswordResetToken).where(PasswordResetToken.expires_at < datetime.utcnow())
    )
    await db.execute(
        delete(EmailVerificationToken).where(EmailVerificationToken.expires_at < datetime.utcnow())
    )
    await db.commit()
```

---

### 15. Fuzzy Matching Threshold May Miss Items
**File:** `services/analyzer.py:60`

```python
def fuzzy_match_category(item_name: str, categories: Dict, threshold: float = 0.6)
```

**Problem:** 0.6 threshold may produce false negatives for legitimate items. Analysis shows "unknown" for many valid line items.

**Recommendation:** Consider:
- Lower threshold to 0.5 with manual review flag
- Use ML classifier instead of fuzzy matching
- Track match rates and tune threshold based on data

---

## 🔵 Low Severity Issues

### 16. Inconsistent Error Response Format
**File:** Various

Some endpoints return `{"detail": "message"}`, others return `{"error": "...", "suggestion": "..."}`. 

**Fix:** Standardize on the custom exception format everywhere.

---

### 17. Missing Request ID for Error Tracking
**File:** `main.py:63-77`

```python
return JSONResponse(
    status_code=500,
    content={
        "detail": "An internal error occurred...",
        "error_id": None  # In production, return a traceable error ID
    }
)
```

**Fix:** Generate and return error IDs:
```python
error_id = str(uuid.uuid4())
log_error(..., details={"error_id": error_id, ...})
return JSONResponse(..., content={"error_id": error_id, ...})
```

---

### 18. Health Check Leaks Database Error Details
**File:** `routers/health.py:22`

```python
db_status = f"unhealthy: {str(e)}"  # Leaks error details
```

**Fix:** Return generic status, log details:
```python
except Exception as e:
    logger.error(f"Health check DB error: {e}")
    db_status = "unhealthy"
```

---

### 19. File Upload Doesn't Limit Concurrent Requests
**File:** `routers/quotes.py:199-260`

**Problem:** Rate limit is 5/hour, but 5 simultaneous large file uploads could exhaust memory.

**Fix:** Add semaphore or connection limit:
```python
_upload_semaphore = asyncio.Semaphore(3)  # Max 3 concurrent uploads

async with _upload_semaphore:
    contents = await file.read()
```

---

### 20. Deprecated `datetime.utcnow()` Usage
**File:** Throughout codebase

`datetime.utcnow()` is deprecated in Python 3.12+.

**Fix:** Use timezone-aware datetimes:
```python
from datetime import datetime, timezone
datetime.now(timezone.utc)
```

---

### 21. Missing `.env.example` for Required Variables
**Problem:** Developers may miss required environment variables.

**Fix:** Create `.env.example`:
```
JWT_SECRET_KEY=your-32-char-secret-here
CSRF_SECRET_KEY=another-secret
DATABASE_URL=sqlite+aiosqlite:///./ungouge.db
OPENAI_API_KEY=sk-...
ENVIRONMENT=development
```

---

### 22. No API Versioning
**File:** `main.py`

**Problem:** API changes could break existing clients.

**Fix:** Add version prefix:
```python
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
```

---

## Quick Wins (Easy Fixes)

1. ✅ **Remove token logging** - Delete the `token: verification_token` lines (30 min)
2. ✅ **Add auth to quote list** - Require authentication on `/quotes` endpoint (15 min)
3. ✅ **Fix report endpoint** - Pass `current_user` to `get_quote_report` (5 min)
4. ✅ **Validate pagination** - Add `Query(ge=1, le=100)` to limit params (10 min)
5. ✅ **Validate reset password** - Call `validate_password()` (5 min)
6. ✅ **Mask health errors** - Remove error details from response (5 min)
7. ✅ **Require JWT secret** - Change from `getenv` to `environ[]` (5 min)

---

## Recommended Priority Order

### Week 1 (Critical/High)
1. Fix hardcoded secret key issue
2. Remove token logging in production
3. Add authentication to `/quotes` and `/quotes/{id}/report`
4. Implement Redis token blacklist
5. Add password validation on reset

### Week 2 (Medium)
6. Add pagination limits
7. Implement token invalidation on password change
8. Add concurrent upload limits
9. Separate CSRF secret
10. Add expired token cleanup

### Week 3 (Low/Hardening)
11. Standardize error responses
12. Add request IDs
13. API versioning
14. Create `.env.example`
15. Update to timezone-aware datetimes

---

## Conclusion

The Ungouge.ai backend has a solid security foundation with proper authentication, rate limiting, and input validation. The critical issues (secret key, token logging) are easy fixes that should be addressed immediately. The high-severity authorization gaps on the quotes endpoints need prompt attention. Medium and low issues can be addressed iteratively.

**Overall Security Grade: B-** (A- after critical/high fixes)

---

*Report generated by AI code review. Manual verification recommended for production deployment.*
