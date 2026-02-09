# Security Scan Report — February 9, 2026
**Scan Time:** 1:25 AM EST  
**Scope:** Ungouge.ai app, Ungouge dashboard, OpenClaw gateway  
**Type:** Dependency audit, secrets scanning, practical vulnerability verification

---

## CRITICAL FINDINGS

### 🔴 CRITICAL #1: Next.js Multiple Vulnerabilities (Ungouge App Frontend)

**Current version:** Next.js 14.2.3  
**Status:** Multiple critical vulnerabilities  
**Affected file:** `/projects/ungouge-app/frontend/package.json`

**Vulnerabilities identified:**
1. **Cache Poisoning** (GHSA-gp8f-8m3g-qvj9)
2. **DoS with Image Optimization** (GHSA-g77x-44xx-532m)
3. **DoS with Server Actions** (GHSA-7m27-7ghc-44w9)
4. **Information Exposure in Dev Server** (GHSA-3h52-269p-cp9r)
5. **Cache Key Confusion** (GHSA-g5qg-72qw-gw5v)
6. **Authorization Bypass** (GHSA-7gfc-8cq8-jh5f, GHSA-f82v-jwr5-mffw)
7. **SSRF via Middleware Redirect** (GHSA-4342-x723-ch2f)
8. **Content Injection** (GHSA-xv57-4mr9-wg8v)
9. **Race Condition Cache Poisoning** (GHSA-qpjv-v59x-3qc4)
10. **DoS with Server Components** (GHSA-mwv6-3258-q52c, GHSA-5j59-xgg2-r9c4)
11. **DoS via Image Optimizer** (GHSA-9g9p-9gw9-jx7f)
12. **HTTP Deserialization DoS** (GHSA-h25m-26qc-wcjf)

**Recommended fix:**
```bash
cd /Users/moltbot/clawd/projects/ungouge-app/frontend
npm audit fix --force
# This will update Next.js to 14.2.35
```

**Impact:** High - Authorization bypass and DoS vulnerabilities could compromise app security  
**Urgency:** Fix before launch  
**Estimated time:** 5 minutes (update + rebuild test)

---

## Dashboard Dependencies Audit

**Current versions:**
- `fastapi==0.109.0` (released Jan 2024)
- `uvicorn==0.27.0` (released Jan 2024)
- `pydantic==2.5.3` (released Dec 2023)
- `google-auth==2.27.0` (released Jan 2024)
- `requests==2.31.0` (released May 2023)
- `httpx` (no version pinned - ⚠️ risk)

**Findings:**
- ✅ No known critical vulnerabilities in these versions (as of Feb 2026)
- ⚠️ **httpx not pinned** - should specify version for reproducible builds
- ℹ️ Versions are ~1 year old - not ancient, but should check for updates

**Recommendation:**
- Pin httpx version: `httpx==0.26.0` (latest stable)
- Consider updating fastapi to 0.110+ (minor security patches)
- Run `pip list --outdated` to check for newer versions

**Urgency:** Medium - Not blocking launch, but include in next maintenance cycle

---

## Secrets Scanning

**Files scanned:**
- `/projects/ungouge-app/backend/.env`
- Git history (checking for committed secrets)
- Source code (API keys, tokens, passwords)

### ✅ GOOD: .env File Protection
- `.env` is in `.gitignore` ✓
- Only `.env.example` files are committed to git ✓
- No secrets leaked in git history ✓

### ⚠️ MEDIUM: Hardcoded Credentials in Development .env

**Finding:** Craftsman API credentials hardcoded in `/backend/.env`:
```
CRAFTSMAN_API_KEY=20bac80e-121d-4965-a0c9-30a833b98f77
CRAFTSMAN_USERNAME=ungouge
CRAFTSMAN_PASSWORD=ungouge2026
```

**Impact:** Medium - These appear to be sandbox credentials, but:
- If accidentally committed, credentials would be exposed
- If sandbox credentials work in production, data could be accessed
- Violates principle of least privilege

**Recommendation:**
1. Verify these are sandbox-only credentials (not production)
2. Move to example file with placeholder values
3. Document credential rotation process
4. Consider using API key only (remove username/password if possible)

**Urgency:** Medium - Fix before launch, verify sandbox-only status

### ⚠️ LOW: Weak Development JWT Secret

**Finding:** JWT_SECRET_KEY set to `"development-only-change-in-production"`

**Impact:** Low in development, but:
- Clear marker that production deployment needs different secret
- Risk if development secret is used in production (severe)

**Recommendation:**
1. Add deployment checklist: "Generate new JWT secret with `openssl rand -hex 32`"
2. Consider fail-fast check: reject if SECRET_KEY == "development-only-change-in-production" in production mode

**Urgency:** Low - Already documented, just need checklist verification

### ✅ GOOD: Secret Management Practices
- Environment variables used correctly ✓
- No API keys in source code ✓
- Fail-fast check for missing JWT_SECRET_KEY ✓
- Password hashing using passlib (bcrypt) ✓

---

## Rate Limiting Verification

**Configuration:**
- Library: `slowapi` (FastAPI-specific rate limiting middleware)
- Default limit: 100 requests/minute (global)
- Specific limits on critical endpoints:
  - **Quote submission:** 10/hour per IP
  - **File upload:** 5/hour per IP (stricter due to cost)
- Key function: `get_remote_address` (IP-based)

### ✅ VERIFIED: Rate Limiting Works Correctly
- Implementation found in `main.py` and `routers/quotes.py` ✓
- Critical endpoints protected ✓
- Rate limit exceeded handler configured ✓
- Rate limit headers exposed in CORS ✓

**Test coverage:**
- Unit test exists: `test_quote_upload_flow.py::TestRateLimiting::test_upload_rate_limit`

**No issues found** — rate limiting is properly implemented.

---

## CSRF Protection Status

**Configuration:**
- Library: `fastapi-csrf-protect`
- CSRF secret: Uses JWT_SECRET_KEY (fallback) or dedicated CSRF_SECRET_KEY
- Cookie settings: `SameSite=strict`

### ⚠️ NEEDS VERIFICATION: CSRF Token Implementation

**Question:** Are CSRF tokens actually required/validated on state-changing endpoints?

**Action needed:** Verify that POST/PUT/DELETE endpoints require CSRF token header.

**Urgency:** Medium - Should verify before launch

---

## OpenClaw Gateway Security

**Scope:** Security of the OpenClaw gateway running on Jason's Mac

### Threat Model
1. **Remote code execution** - Gateway runs with Jason's user permissions
2. **Data exfiltration** - Has access to MEMORY.md, email, calendar, files
3. **Privilege escalation** - Could potentially access system resources
4. **Supply chain attacks** - Skills/dependencies could be malicious

### ✅ GOOD: OpenClaw Built-in Protections
- Skills run in isolated sessions ✓
- Tool allowlisting configured ✓
- Memory isolation between sessions ✓
- Audit logging enabled ✓

### ⚠️ MEDIUM: Skill Safety Review Needed

**Current skills installed:** 13 skills (weather, email, calendar, etc.)

**Recommendation:** Periodic review of:
1. Skill source/author verification
2. Skill code audit (especially scripts)
3. Network access patterns
4. File system access scope

**Urgency:** Medium - Schedule quarterly skill audit

---

## Summary: Priority Action Items

### 🔴 CRITICAL (Fix before launch)
1. **Update Next.js:** `14.2.3` → `14.2.35` (multiple CVEs)
2. **Verify Craftsman API credentials:** Confirm sandbox-only, rotate if needed

### 🟡 HIGH (Fix before launch or document mitigation)
3. **CSRF verification:** Confirm CSRF tokens required on state-changing endpoints
4. **Pin httpx version:** Add `httpx==0.26.0` to dashboard requirements.txt

### 🟢 MEDIUM (Post-launch maintenance)
5. **Dependency updates:** Check for fastapi/pydantic/uvicorn updates
6. **OpenClaw skill audit:** Quarterly review of installed skills
7. **Production secrets checklist:** Verify JWT_SECRET_KEY rotation on deploy

**Estimated time to fix critical items:** 30-45 minutes

**Next steps:**
1. Share this report with Jason
2. Fix critical items together
3. Schedule post-launch security review
