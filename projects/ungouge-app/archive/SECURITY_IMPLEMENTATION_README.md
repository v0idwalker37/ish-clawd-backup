# Security Implementation - UnGouge.ai

**Status:** Middleware created, integration pending  
**Created:** 2026-02-13 by Ish  
**Fixes:** 22 vulnerabilities identified in security audit

---

## ✅ Completed

### 1. CSP Headers (Frontend)
**File:** `frontend/next.config.js`

Added comprehensive security headers:
- Content-Security-Policy (CSP)
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- Referrer-Policy: strict-origin-when-cross-origin
- Permissions-Policy (camera, microphone, geolocation disabled)

### 2. CSRF Protection (Backend)
**File:** `backend/middleware/csrf.py`

Features:
- Secure token generation (random + timestamp + signature)
- 1-hour token lifetime
- Automatic validation on POST/PUT/DELETE/PATCH
- Skips validation for API key auth
- Cookie-based token delivery

**Usage:**
```python
from middleware.csrf import csrf_protect, CSRFProtection, set_csrf_cookie

# In main.py startup
app.state.csrf_secret = os.environ.get("CSRF_SECRET", secrets.token_urlsafe(32))

# On login/page load
csrf = CSRFProtection(app.state.csrf_secret)
token = csrf.generate_token()
set_csrf_cookie(response, token)

# Protect endpoints
@app.post("/api/quotes/submit", dependencies=[Depends(csrf_protect)])
async def submit_quote(...):
    ...
```

### 3. Input Validation (Backend)
**File:** `backend/middleware/input_validation.py`

Validates:
- Project types (34 whitelisted types, no fuzzy matching)
- Regions (51 states + 6 regions)
- Quote totals ($100 - $500,000)
- Line item costs ($0 - $100,000)
- Line item descriptions (500 char max, alphanumeric + safe punctuation)
- Email format
- Filenames (path traversal prevention)

**Usage:**
```python
from middleware.input_validation import validate_quote_input, InputValidator

# Validate entire quote
validated = validate_quote_input(
    project_type="roof-replacement",
    region="VT",
    total=15000.0,
    line_items=[...]
)

# Or validate individual fields
project = InputValidator.validate_project_type("Roof Replacement")  # -> "roof-replacement"
region = InputValidator.validate_region("Vermont")                   # -> "VT"
```

### 4. File Upload Security (Backend)
**File:** `backend/middleware/file_security.py`

Features:
- Magic byte validation (not just extension checking)
- Size limits (5MB images, 10MB PDFs)
- EXIF metadata stripping (images)
- PDF metadata removal
- SHA-256 file hashing
- VirusTotal API stub (ready to integrate)

**Usage:**
```python
from middleware.file_security import validate_uploaded_quote

@app.post("/api/quotes/upload")
async def upload_quote(file: UploadFile):
    clean_contents, mime_type, file_hash = await validate_uploaded_quote(file)
    # clean_contents has no metadata, safe to store/process
```

### 5. Rate Limiting (Backend)
**File:** `backend/middleware/rate_limit.py`

Limits:
- Quote analysis: 10/hour
- File upload: 5/hour
- Login: 5/15 minutes
- General API: 30/minute
- Create ops: 20/minute
- Delete ops: 10/minute

**Usage:**
```python
from middleware.rate_limit import limiter, get_rate_limit

# In main.py
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# On endpoints
@app.post("/api/quotes/analyze")
@limiter.limit(get_rate_limit("quote_analyze"))
async def analyze_quote(request: Request, ...):
    ...
```

---

## ⏳ Pending Integration

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements-security.txt
```

**Note:** `python-magic` requires `libmagic`:
- macOS: `brew install libmagic`
- Ubuntu: `apt-get install libmagic1`

### Step 2: Set Environment Variables
Add to `.env`:
```bash
# CSRF secret (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
CSRF_SECRET=your-secret-here

# Optional: VirusTotal API key for malware scanning
VIRUSTOTAL_API_KEY=your-key-here
```

### Step 3: Wire Up Middleware in main.py

**Add imports:**
```python
from middleware.csrf import csrf_protect, CSRFProtection, set_csrf_cookie
from middleware.input_validation import validate_quote_input, InputValidator
from middleware.file_security import validate_uploaded_quote
from middleware.rate_limit import limiter, rate_limit_exceeded_handler, get_rate_limit
from slowapi.errors import RateLimitExceeded
```

**In startup event:**
```python
@app.on_event("startup")
async def startup():
    # Initialize CSRF secret
    app.state.csrf_secret = os.environ.get("CSRF_SECRET", secrets.token_urlsafe(32))
    
    # Initialize rate limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
```

**On quote analysis endpoint:**
```python
@app.post("/api/quotes/analyze", dependencies=[Depends(csrf_protect)])
@limiter.limit(get_rate_limit("quote_analyze"))
async def analyze_quote(
    request: Request,
    project_type: str,
    region: str,
    total: float,
    line_items: List[dict]
):
    # Validate inputs
    validated = validate_quote_input(project_type, region, total, line_items)
    
    # Use validated data
    result = analyze_quote_logic(
        validated["project_type"],
        validated["region"],
        validated["total"],
        validated["line_items"]
    )
    return result
```

**On file upload endpoint:**
```python
@app.post("/api/quotes/upload", dependencies=[Depends(csrf_protect)])
@limiter.limit(get_rate_limit("upload"))
async def upload_quote(request: Request, file: UploadFile):
    # Validate and clean file
    clean_contents, mime_type, file_hash = await validate_uploaded_quote(file)
    
    # Save/process cleaned file
    ...
```

**On login/page load (CSRF token delivery):**
```python
@app.get("/")
async def index():
    response = templates.TemplateResponse("index.html", {...})
    
    # Generate and set CSRF token
    csrf = CSRFProtection(app.state.csrf_secret)
    token = csrf.generate_token()
    set_csrf_cookie(response, token)
    
    return response
```

### Step 4: Frontend Changes

**Send CSRF token with requests:**
```javascript
// Get token from cookie
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

// Include in fetch headers
fetch('/api/quotes/submit', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': getCookie('csrf_token')
    },
    body: JSON.stringify(data)
})
```

---

## ⏳ Still TODO

### Dashboard
1. **BOLA audit** - Verify all endpoints check ownership
2. **API key hashing** - Hash keys with bcrypt before storage

### App
3. **SQL injection audit** - Verify parameterized queries everywhere
4. **Privacy policy** - Draft GDPR/CCPA compliant policy
5. **Terms of service** - Standard ToS
6. **Data retention** - Auto-delete quotes after 90 days
7. **Logging** - Structured JSON logs for security events
8. **Dependabot** - Enable on GitHub
9. **Security testing** - OWASP ZAP scan before launch

### OpenClaw
10. **Exec command policy** - Whitelist/confirmation/blocked lists
11. **File path policy** - Workspace-only access
12. **Security audit log** - Log all sensitive operations
13. **Panic word** - "FREEZE" stops all operations
14. **Cron approval** - Require approval before scheduling

---

## Testing

### Manual Testing Checklist

**CSRF Protection:**
- [ ] Submit quote without CSRF token → expect 403
- [ ] Submit quote with expired token → expect 403
- [ ] Submit quote with valid token → expect success

**Input Validation:**
- [ ] Submit invalid project type → expect 400
- [ ] Submit invalid region → expect 400
- [ ] Submit quote total $999,999 → expect 400
- [ ] Submit line item with <script> tag → expect sanitized

**File Upload:**
- [ ] Upload 20MB file → expect 413
- [ ] Upload .exe renamed to .pdf → expect 415
- [ ] Upload image with EXIF → verify EXIF stripped
- [ ] Upload PDF with metadata → verify metadata removed

**Rate Limiting:**
- [ ] Submit 11 quotes in 1 hour → expect 429 on 11th
- [ ] Upload 6 files in 1 hour → expect 429 on 6th

### Automated Testing

Add to test suite:
```python
def test_csrf_protection():
    # Without token
    response = client.post("/api/quotes/submit", json={...})
    assert response.status_code == 403
    
    # With valid token
    csrf = CSRFProtection(app.state.csrf_secret)
    token = csrf.generate_token()
    response = client.post(
        "/api/quotes/submit",
        json={...},
        headers={"X-CSRF-Token": token}
    )
    assert response.status_code == 200
```

---

## Security Audit Results

**Before:** 22 vulnerabilities (3 CRITICAL, 14 HIGH, 5 MEDIUM)  
**After middleware:** ~15 vulnerabilities remaining (0 CRITICAL, ~10 HIGH, ~5 MEDIUM)

### Fixed
- ✅ Next.js CVE (upgraded to 14.2.35)
- ✅ Missing CSP headers
- ✅ No CSRF protection
- ✅ File upload vulnerabilities
- ✅ Input validation gaps
- ✅ No rate limiting
- ✅ OAuth state parameter (dashboard - already done)

### Remaining
- ⏳ SQL injection audit (need to verify)
- ⏳ BOLA on all endpoints (need to verify)
- ⏳ API key storage (needs hashing)
- ⏳ Privacy policy (legal)
- ⏳ Terms of service (legal)
- ⏳ Logging implementation
- ⏳ OpenClaw hardening (5 items)

---

## Deployment Notes

**DO NOT deploy to production without:**
1. Setting `CSRF_SECRET` environment variable (unique, secret)
2. Installing `libmagic` on server
3. Testing all endpoints with new middleware
4. Verifying rate limits work correctly
5. Testing file upload security

**Production recommendations:**
- Use Redis for rate limiting (not in-memory)
- Enable VirusTotal scanning (optional, $)
- Monitor rate limit hits (track abuse)
- Regular security audits

---

**Questions? Ask Ish.**
