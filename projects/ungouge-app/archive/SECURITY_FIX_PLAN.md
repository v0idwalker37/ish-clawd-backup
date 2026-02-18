# Security Fix Implementation Plan

**Started:** 2026-02-02 13:21 EST  
**Priority:** HIGH → MEDIUM → LOW  
**Scope:** All projects (Ungouge, Moltbot workspace, skills, credentials)

---

## Phase 1: HIGH Priority Fixes (Ungouge)

### 1.1 Add Rate Limiting ⏳ IN PROGRESS
**Files to modify:**
- `backend/requirements.txt` - add slowapi
- `backend/main.py` - configure limiter
- `backend/routers/auth.py` - apply limits to login/register
- `backend/routers/quotes.py` - apply limits to quote submission

**Implementation:**
- Login: 5 attempts per minute per IP
- Registration: 3 per hour per IP
- Quote submission: 10 per hour per IP
- Global: 100 requests per minute per IP

### 1.2 Fix Access Control on Quote Reports
**Files to modify:**
- `backend/routers/quotes.py` - add authorization check to `get_quote_report()`

**Logic:**
- If quote has no user_id → public (anyone can view)
- If quote has user_id → only owner can view
- Alternative: Generate secret access tokens for sharing

### 1.3 Fix Login Timing Attack
**Files to modify:**
- `backend/routers/auth.py` - make login timing constant

**Implementation:**
- Always hash a dummy password if user not found
- Same computational cost regardless of email existence
- Generic error message

---

## Phase 2: MEDIUM Priority Fixes

### 2.1 Add Security Headers
**Files:** `backend/main.py`
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- Strict-Transport-Security
- Content-Security-Policy
- X-XSS-Protection

### 2.2 Harden CORS
**Files:** `backend/main.py`
- Restrict origins to production domain
- Explicit method list (no wildcards)
- Explicit header list

### 2.3 Add Structured Logging
**Files:** Multiple
- Install python-json-logger
- Log auth events (success/failure)
- Log quote submissions
- Log access denied events

### 2.4 Disable Database Echo in Production
**Files:** `backend/models/database.py`
- Control via environment variable
- Default to False

### 2.5 Implement Password Reset Flow
**Files:** `backend/routers/auth.py`, new models
- Generate time-limited reset tokens
- Store in database with expiry
- Send email with reset link
- Complete reset endpoint

### 2.6 Add Email Verification Flow
**Files:** Multiple
- Verification token on registration
- Send verification email
- Verify endpoint
- Enforce verified status for sensitive actions

### 2.7 Add CSRF Protection
**Files:** `backend/main.py`, routers
- Install fastapi-csrf-protect
- Add CSRF tokens to forms
- Validate on state-changing requests

### 2.8 Improve Error Handling
**Files:** All routers
- Generic messages to users
- Detailed logs server-side
- No stack traces in responses

---

## Phase 3: LOW Priority Fixes

### 3.1 Token Blacklisting (Logout)
**Files:** New service, auth router
- Redis for revoked tokens
- Implement logout endpoint
- Check blacklist on token validation

### 3.2 Update Dependencies
- Run npm audit (frontend)
- Run pip list --outdated (backend)
- Update to latest stable versions

### 3.3 Move to PostgreSQL Setup Docs
- Document migration path
- Connection pooling config
- SSL/TLS setup

### 3.4 Switch to httpOnly Cookies
**Files:** Frontend + Backend
- Backend sets httpOnly cookies
- Remove localStorage usage
- Update auth flow

---

## Phase 4: Workspace & Infrastructure Security

### 4.1 Audit Moltbot Skills ⏳ PENDING
- Review all skill scripts for vulnerabilities
- Check for hardcoded credentials
- Verify file permissions
- Add .gitignore entries

### 4.2 Secure Email Configuration ✅ DONE
- Permissions set to 600
- Added to .gitignore

### 4.3 Secure Moltbot Configuration
- Review gateway config
- Audit channel credentials
- Check cron job security

### 4.4 YouTube Channel Security (Future)
- API credentials storage
- OAuth token management
- Upload permissions

---

## Status Tracking

✅ = Complete  
⏳ = In Progress  
⏸️ = Blocked/Waiting  
📋 = Planned

### HIGH Priority
- [ ] ⏳ Rate limiting
- [ ] 📋 Access control on reports
- [ ] 📋 Fix login timing attack

### MEDIUM Priority
- [ ] 📋 Security headers
- [ ] 📋 CORS hardening
- [ ] 📋 Structured logging
- [ ] 📋 Database echo control
- [ ] 📋 Password reset
- [ ] 📋 Email verification
- [ ] 📋 CSRF protection
- [ ] 📋 Error handling

### LOW Priority
- [ ] 📋 Token blacklisting
- [ ] 📋 Dependency updates
- [ ] 📋 PostgreSQL docs
- [ ] 📋 httpOnly cookies

---

**Next action:** Implement rate limiting
