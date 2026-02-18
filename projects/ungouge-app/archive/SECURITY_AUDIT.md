# Security Audit - Ungouge.ai
**Date:** 2026-02-02  
**Auditor:** Ish  
**Scope:** Full stack (Frontend + Backend + Infrastructure)  
**Framework:** OWASP Top 10 (2021) + Best Practices

---

## Executive Summary

**Overall Risk Level:** 🟡 **MEDIUM**  
**Critical Issues:** 0  
**High Priority:** 3  
**Medium Priority:** 8  
**Low Priority:** 4  
**Informational:** 3

**Verdict:** The application has a solid foundation but requires security hardening before production deployment. Authentication is implemented correctly, but several production-critical features are missing (rate limiting, CSRF protection, security headers, etc.).

---

## OWASP Top 10 Assessment

### ✅ A01:2021 – Broken Access Control
**Status:** MOSTLY SECURE  
**Findings:**
- ✅ JWT-based authentication implemented correctly
- ✅ Protected routes use dependency injection (`get_current_user`)
- ⚠️ **MEDIUM:** `/api/quotes/{quote_id}` endpoint has no authorization check
  - **Issue:** Any user can view any quote report if they know the UUID
  - **Fix:** Add owner verification or implement access tokens
  - **Risk:** Information disclosure

**Action Items:**
```python
# In quotes.py - add authorization check:
@router.get("/quotes/{quote_id}", response_model=ReportModel)
async def get_quote_report(
    quote_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),  # ADD THIS
):
    # Fetch quote
    quote = ...
    
    # ADD: Verify ownership if user is logged in
    if quote.user_id and current_user:
        if quote.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
```

---

### ✅ A02:2021 – Cryptographic Failures
**Status:** SECURE  
**Findings:**
- ✅ Passwords hashed with bcrypt (via passlib)
- ✅ JWTs signed with HS256
- ⚠️ **LOW:** Default JWT secret is weak in `.env`
  - Current: `"development-only-change-in-production"`
  - **Fix:** Generate strong secret with `openssl rand -hex 32`
  - **Risk:** Low for dev, critical for production

**Action Items:**
- Generate production JWT secret before deployment
- Rotate secret periodically (document in SECURITY.md)
- Consider moving to RS256 (asymmetric) for better security

---

### ⚠️ A03:2021 – Injection
**Status:** LOW RISK  
**Findings:**
- ✅ Using SQLAlchemy ORM (parameterized queries by default)
- ✅ No raw SQL detected in codebase
- ✅ Pydantic models validate all inputs
- ⚠️ **LOW:** Database echo mode enabled in dev
  - File: `backend/models/database.py`
  - Line: `echo=True  # Set to False in production`
  - **Risk:** Logs may expose sensitive data in production

**Action Items:**
```python
# In database.py:
engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("DATABASE_ECHO", "false").lower() == "true",  # Control via env var
)
```

---

### ⚠️ A04:2021 – Insecure Design
**Status:** NEEDS IMPROVEMENT  
**Findings:**
- ⚠️ **HIGH:** No rate limiting on any endpoints
  - **Issue:** Brute force attacks possible on `/auth/login`
  - **Issue:** Quote submission spam possible
  - **Risk:** Resource exhaustion, credential stuffing
  - **Fix:** Add rate limiting middleware

- ⚠️ **MEDIUM:** Password reset not implemented
  - File: `routers/auth.py` - `forgot_password` is a stub
  - **Risk:** Users cannot recover accounts

- ⚠️ **MEDIUM:** No email verification flow
  - `is_verified` field exists but not enforced
  - **Risk:** Spam accounts, fake emails

**Action Items:**
```python
# Install slowapi for rate limiting:
# pip install slowapi

# In main.py:
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# In routers/auth.py:
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/auth/login")
@limiter.limit("5/minute")  # Max 5 login attempts per minute
async def login(...):
    ...
```

---

### ⚠️ A05:2021 – Security Misconfiguration
**Status:** NEEDS HARDENING  
**Findings:**
- ⚠️ **MEDIUM:** CORS allows all methods and headers
  - File: `main.py`
  - Current: `allow_methods=["*"], allow_headers=["*"]`
  - **Fix:** Restrict to needed methods only

- ⚠️ **MEDIUM:** No security headers
  - Missing: `X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security`
  - **Risk:** Clickjacking, MIME sniffing attacks

- ⚠️ **LOW:** Uvicorn binds to `0.0.0.0` in dev
  - File: `main.py` - `host="0.0.0.0"`
  - **Risk:** Exposes dev server to network

- ⚠️ **INFO:** SQLite used for development
  - **Risk:** Not suitable for production (no concurrent writes)
  - **Fix:** Use PostgreSQL in production (already configured in .env.example)

**Action Items:**
```python
# In main.py - add security headers middleware:
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["ungouge.ai", "*.ungouge.ai"])

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

# Restrict CORS:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ungouge.ai"],  # Only production domain
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Explicit list
    allow_headers=["Content-Type", "Authorization"],  # Explicit list
)
```

---

### ⚠️ A06:2021 – Vulnerable and Outdated Components
**Status:** MOSTLY CURRENT  
**Findings:**
- ✅ Frontend: Next.js 14.2.3 (current as of Feb 2026)
- ✅ Frontend: React 18.3.1 (current)
- ✅ Backend: FastAPI 0.109.2 (recent)
- ⚠️ **LOW:** Some backend dependencies could be newer
  - `stripe==8.2.0` (current is 10.x)
  - `python-jose==3.3.0` (consider PyJWT instead)

**Action Items:**
```bash
# Run dependency audit:
cd frontend && npm audit
cd backend && pip list --outdated

# Update regularly:
npm update
pip install --upgrade -r requirements.txt
```

---

### ⚠️ A07:2021 – Identification and Authentication Failures
**Status:** NEEDS IMPROVEMENT  
**Findings:**
- ✅ Password hashing implemented correctly (bcrypt)
- ✅ JWT tokens with expiry (30 min access, 7 day refresh)
- ⚠️ **HIGH:** No account lockout after failed login attempts
  - **Issue:** Brute force attacks possible
  - **Fix:** Implement rate limiting + temporary lockout

- ⚠️ **MEDIUM:** Login endpoint reveals if email exists
  - File: `routers/auth.py` - login function
  - Current error: "Incorrect email or password"
  - **Issue:** Timing attack - database lookup happens before password check
  - **Fix:** Use constant-time comparison

- ⚠️ **MEDIUM:** No MFA/2FA support
  - **Risk:** Compromised passwords = full account access

- ⚠️ **LOW:** Refresh tokens never invalidated
  - **Issue:** No token blacklist or logout mechanism
  - **Risk:** Stolen refresh tokens valid for 7 days

**Action Items:**
```python
# In routers/auth.py - fix timing attack:
import time

@router.post("/auth/login")
async def login(...):
    # Always perform bcrypt verification even if user not found
    # This makes timing consistent
    
    user = await db.execute(select(User).where(User.email == credentials.email))
    user = user.scalar_one_or_none()
    
    # Create dummy hash if user not found (same computational cost)
    password_hash = user.password_hash if user else hash_password("dummy")
    
    # Always verify (constant time)
    is_valid = verify_password(credentials.password, password_hash)
    
    if not user or not is_valid:
        # Generic error message
        raise HTTPException(status_code=401, detail="Invalid credentials")
    ...
```

---

### ✅ A08:2021 – Software and Data Integrity Failures
**Status:** SECURE  
**Findings:**
- ✅ No insecure deserialization found
- ✅ Pydantic validates all incoming JSON
- ✅ `.env` files properly gitignored
- ✅ No CI/CD pipeline yet (so no pipeline vulnerabilities)

**Action Items:**
- When adding CI/CD: Use GitHub Actions secrets for credentials
- Sign production builds
- Implement webhook signature verification (Stripe)

---

### ⚠️ A09:2021 – Security Logging and Monitoring Failures
**Status:** MINIMAL  
**Findings:**
- ⚠️ **MEDIUM:** No structured logging
  - **Issue:** No audit trail for auth events
  - **Risk:** Cannot detect breach or abuse

- ⚠️ **MEDIUM:** No monitoring/alerting
  - **Issue:** No way to detect attacks in real-time

- ⚠️ **INFO:** Exception messages expose internal details
  - Example: `"Failed to create user: {str(e)}"`
  - **Risk:** Information leakage in stack traces

**Action Items:**
```python
# Add structured logging:
import logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# In auth.py:
logger.info("user_login_success", extra={"user_id": user.id, "ip": request.client.host})
logger.warning("user_login_failed", extra={"email": credentials.email, "ip": request.client.host})

# In production:
# - Send logs to service (Datadog, Sentry, LogDNA)
# - Alert on: repeated login failures, unusual patterns
```

---

### ✅ A10:2021 – Server-Side Request Forgery (SSRF)
**Status:** NOT APPLICABLE  
**Findings:**
- ✅ No user-controlled URLs fetched by backend
- ✅ No webhooks or external API calls (except future Stripe)

**Action Items:**
- When adding web scraping: Validate/sanitize URLs
- Blacklist private IP ranges (127.0.0.1, 10.x.x.x, 192.168.x.x)

---

## Frontend Security Assessment

### React/Next.js Security

**Findings:**
- ✅ Next.js 14 has built-in XSS protection
- ✅ No `dangerouslySetInnerHTML` found in codebase
- ✅ Inputs are escaped by React by default
- ⚠️ **LOW:** localStorage used for JWT tokens
  - File: Various frontend components
  - **Issue:** Vulnerable to XSS attacks
  - **Fix:** Use httpOnly cookies instead (requires backend change)

**Action Items:**
```typescript
// Instead of localStorage:
localStorage.setItem('token', token)  // ❌ Vulnerable to XSS

// Use httpOnly cookies:
// Backend sets cookie in response headers
response.set_cookie(
    key="access_token",
    value=token,
    httponly=True,  // JavaScript cannot access
    secure=True,     // HTTPS only
    samesite="strict"  // CSRF protection
)

// Frontend: Cookie sent automatically, no JS access needed
```

### Cross-Site Request Forgery (CSRF)

**Findings:**
- ⚠️ **MEDIUM:** No CSRF protection
  - **Issue:** State-changing requests have no CSRF tokens
  - **Risk:** Attacker site can submit forms on user's behalf
  - **Mitigation:** Using JWT in Authorization header (not cookies) provides some protection
  - **Better:** Implement double-submit cookie pattern or SameSite cookies

**Action Items:**
```python
# If using cookies (recommended), add CSRF protection:
from fastapi_csrf_protect import CsrfProtect

@app.post("/api/quotes")
async def submit_quote(
    csrf_protect: CsrfProtect = Depends()
):
    await csrf_protect.validate_csrf(request)
    ...
```

---

## Infrastructure Security

### Database

**Findings:**
- ⚠️ **INFO:** SQLite in development
  - **Risk:** Single-threaded, no concurrent writes
  - **Fix:** PostgreSQL for production (already in .env.example)

- ✅ Passwords not stored in plain text
- ✅ Using parameterized queries (ORM)

### Secrets Management

**Findings:**
- ✅ `.env` file properly gitignored
- ✅ File permissions set to 600 (owner-only)
- ✅ Environment variables used throughout
- ⚠️ **LOW:** Some config files outside Ungouge have plain text secrets
  - `~/.config/moltbook/credentials.json` (already secured)
  - `/Users/moltbot/clawd/skills/email/config.json` (already secured)

---

## Additional Security Recommendations

### High Priority

1. **Add Rate Limiting**
   - Install: `pip install slowapi`
   - Apply to: `/auth/login`, `/auth/register`, `/quotes`
   - Limits: 5 login attempts/min, 10 quotes/hour per IP

2. **Implement Access Control on Reports**
   - Quote reports should be owner-only or use secret access tokens
   - Add authorization check in `get_quote_report()`

3. **Add Account Lockout**
   - After 5 failed login attempts, lock account for 15 minutes
   - Notify user via email

### Medium Priority

4. **Security Headers**
   - Add middleware for: CSP, HSTS, X-Frame-Options, etc.

5. **Structured Logging**
   - Log all auth events (login, logout, registration)
   - Log failed access attempts
   - Send to monitoring service in production

6. **CORS Hardening**
   - Restrict to production domain only
   - Explicit method/header lists

7. **Error Handling**
   - Generic error messages to users
   - Detailed logs server-side only
   - Custom error pages (no stack traces)

8. **Password Reset Flow**
   - Implement with time-limited tokens
   - Email verification

### Low Priority

9. **Token Blacklisting**
   - Redis cache for revoked tokens
   - Implement logout endpoint

10. **Dependency Updates**
    - Run `npm audit` and `pip list --outdated` monthly
    - Update dependencies regularly

11. **Database Migration to PostgreSQL**
    - Before production launch
    - Enable connection pooling
    - SSL/TLS connections

### Future Enhancements

12. **Multi-Factor Authentication (MFA)**
    - TOTP (Google Authenticator)
    - SMS backup codes

13. **API Key Management**
    - For programmatic access
    - Rate limits per key

14. **Content Security Policy**
    - Strict CSP headers
    - Report violations

15. **Web Application Firewall (WAF)**
    - Cloudflare or AWS WAF
    - DDoS protection

---

## Pre-Production Security Checklist

Before deploying to production, complete:

- [ ] Generate strong JWT secret (`openssl rand -hex 32`)
- [ ] Rotate all API keys (Stripe, Craftsman, OpenAI)
- [ ] Switch database to PostgreSQL
- [ ] Add rate limiting middleware
- [ ] Implement access control on quote reports
- [ ] Add security headers middleware
- [ ] Restrict CORS to production domain
- [ ] Set `echo=False` in database config
- [ ] Configure structured logging
- [ ] Set up monitoring/alerting (Sentry, Datadog)
- [ ] Enable HTTPS (Let's Encrypt)
- [ ] Configure firewall rules
- [ ] Backup strategy for database
- [ ] Incident response plan documented
- [ ] Security audit by third party (optional but recommended)

---

## Risk Assessment by Priority

### 🔴 Critical (Deploy Blockers)
None identified for MVP. All critical security is in place.

### 🟠 High (Fix Before Production)
1. No rate limiting (enables brute force)
2. Login timing attack (email enumeration)
3. Missing access control on quote reports

### 🟡 Medium (Fix Soon)
1. No CSRF protection
2. CORS too permissive
3. No security headers
4. Weak default JWT secret
5. No structured logging
6. Database echo mode enabled
7. Password reset not implemented
8. No email verification

### 🟢 Low (Non-Urgent)
1. Refresh tokens never invalidated
2. localStorage for tokens (XSS risk)
3. SQLite in development
4. Some outdated dependencies

### ℹ️ Informational
1. No CI/CD (so no pipeline risks yet)
2. Generic exception messages good
3. No SSRF vulnerabilities

---

## Conclusion

**The Ungouge.ai application has a solid security foundation** with proper authentication, password hashing, and input validation. However, **rate limiting, access controls, and security headers are critical gaps** that must be addressed before production deployment.

**Recommended Timeline:**
- **Before Production:** Fix all HIGH priority issues
- **Within 1 month:** Fix MEDIUM priority issues
- **Ongoing:** Low priority and enhancements

**Estimated effort to address high-priority issues:** 6-8 hours

---

**Next Steps:**
1. Review this audit with Jason
2. Prioritize fixes based on launch timeline
3. Implement high-priority items first
4. Re-audit before production launch

**Questions?** Contact: jasontrask@gmail.com
