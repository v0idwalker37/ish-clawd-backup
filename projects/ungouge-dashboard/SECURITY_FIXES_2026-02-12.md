# Security Fixes — 2026-02-12

## Dashboard (dashboard.ungouge.ai) — Applied

### 1. Rate Limiting (NEW) ✅
- **Library:** slowapi (already in requirements.txt)
- **Global default:** 100 requests/minute per IP
- **Auth endpoints:** 10/minute (login, callback)
- **Write endpoints:** 30/minute (create/update tasks, expenses)
- **Delete endpoints:** 20/minute (delete tasks, expenses)
- **Stripe API:** 10/minute (expensive external calls)
- **Timeclock:** 10/minute (clock in/out)
- **Account deletion:** 3/hour (destructive, most restrictive)

### 2. HSTS Header (NEW) ✅
- Added `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`
- Forces HTTPS for 1 year, covers all subdomains

### 3. Global Exception Handler (NEW) ✅
- Catches all unhandled exceptions
- Returns generic message: "An internal error occurred. Please try again later."
- Logs full error details server-side (method, path, exception type)
- Prevents stack trace / internal detail leakage

### 4. Error Detail Sanitization ✅
- Fixed `delete_account` endpoint: was returning raw exception string
- Now returns generic message, logs details server-side

## Already Secure (Verified)

### Main App (ungouge.ai backend)
- ✅ Next.js 14.2.35 (up to date)
- ✅ Rate limiting via slowapi
- ✅ CSRF protection via fastapi-csrf-protect
- ✅ Security headers (CSP, X-Frame-Options, HSTS, XSS protection)
- ✅ Global exception handler (no internal leakage)
- ✅ CORS hardened (explicit origins, methods, headers)
- ✅ Input validation via Pydantic models + validators.py
- ✅ HTTPS redirect middleware in production

### Dashboard (pre-existing)
- ✅ Security headers (CSP, X-Frame-Options, X-XSS-Protection, Referrer-Policy, Permissions-Policy)
- ✅ OAuth state parameter CSRF protection
- ✅ httpOnly + Secure + SameSite cookies
- ✅ Session expiration (24h) + cleanup
- ✅ Authorized email whitelist (void@ungouge.ai only)
- ✅ SQL parameterization (all queries use %s placeholders)
- ✅ Dynamic field updates use allowed_fields whitelist (not user input)
- ✅ Blog slug sanitization (regex: alphanumeric + hyphens only)
- ✅ File permissions: .env (600), config (600)

### Infrastructure
- ✅ Config file permissions: 600 (owner read/write only)
- ✅ .env in .gitignore
- ✅ Cloud SQL private networking
- ✅ Google OAuth 2.0 (no password auth)

## Remaining Items (Backlog)

### Medium Priority
- [ ] BOLA audit: Dashboard is single-user (void@ungouge.ai only), so BOLA is not currently exploitable. When multi-user support is added, add ownership checks.
- [ ] API versioning (/api/v1/ prefix) — for future compatibility
- [ ] Structured logging with automatic sensitive data redaction
- [ ] Security monitoring/alerting (Google Cloud Monitoring)
- [ ] Dependency audit automation (npm audit + pip-audit in CI/CD)

### Low Priority
- [ ] Cookie `__Host-` prefix
- [ ] Honeypot fields on public forms
- [ ] SRI hashes for CDN resources

## Deployment Required
These fixes are in the local codebase. To deploy to production:
```bash
cd /Users/moltbot/clawd/projects/ungouge-dashboard
./DEPLOY_DASHBOARD.sh
```

---
*Fixes applied: 2026-02-12, 8:43-9:00 AM EST*
*Auditor: Ish (Opus 4.6 + extended thinking)*
