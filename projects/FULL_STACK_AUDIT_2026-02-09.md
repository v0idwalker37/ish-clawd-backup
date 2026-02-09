# 🔍 Full-Stack Code Audit Report
## Ungouge.ai Application + Executive Dashboard
### Date: February 9, 2026 | Auditor: Ish (AI Agent, Claude Opus 4.6)

---

## 1. Executive Summary

**Ungouge.ai is a promising homeowner advocacy platform with a solid product vision, comprehensive cost model data, and a well-structured backend. However, both the main application and executive dashboard have critical security vulnerabilities that MUST be fixed before any public launch.** The most urgent issues are: API keys and secrets committed to source code (including Stripe test keys, Google OAuth secrets, and Craftsman API credentials), a Next.js version with known CVEs, ephemeral database storage on Cloud Run that will lose all data on container restart, and an in-memory token blacklist that won't survive server restarts. The frontend code quality is high with polished UX, but the backend needs hardening for production. The dashboard is functional but architecturally brittle due to its reliance on ephemeral SQLite storage and static HTML files with duplicated JavaScript.

---

## 2. Overall Scores

| Category | Score | Grade |
|----------|-------|-------|
| **Ungouge.ai App** | **62/100** | C+ |
| **Executive Dashboard** | **48/100** | D+ |
| **Combined** | **55/100** | C- |

### Score Breakdown

| Dimension | App | Dashboard |
|-----------|-----|-----------|
| Security | 35/100 | 30/100 |
| Architecture | 72/100 | 55/100 |
| Auth | 70/100 | 65/100 |
| Database | 55/100 | 25/100 |
| Dependencies | 40/100 | 60/100 |
| Performance | 65/100 | 60/100 |
| Error Handling | 70/100 | 50/100 |
| Frontend UX | 85/100 | 75/100 |
| Cost Models | 90/100 | N/A |
| Launch Readiness | 30/100 | 35/100 |

---

## 3. 🔴 CRITICAL Issues (Must Fix Before Any Launch)

### CRIT-01: API Keys and Secrets in Source Code
**Severity: CRITICAL | Both Projects**

**Ungouge App** (`backend/.env`):
- Craftsman API key hardcoded: `20bac80e-121d-4965-a0c9-30a833b98f77`
- Craftsman username/password in plaintext: `ungouge` / `ungouge2026`
- JWT_SECRET_KEY defaults to `"development-only-change-in-production"` (line in `services/auth.py`)
- If this `.env` file is committed to git, ALL credentials are compromised

**Executive Dashboard** (`backend/.env.cloudrun`):
- Google OAuth Client Secret: `REDACTED`
- Stripe TEST API key: `sk_test_51SxXkQ2O0ZqQaOwm...`
- YouTube API key: `REDACTED_YOUTUBE_KEY`
- File has comment "DO NOT COMMIT TO PUBLIC REPOS" but the file IS in the codebase

**Dashboard** (`backend/main.py`, line ~58 and `backend/auth.py`, line ~12):
- Google OAuth Client ID hardcoded in TWO places: `1093157467231-3pgo81mrq5rjdvhvaa1uf81pk2ifhka2.apps.googleusercontent.com`

**Fix:** 
1. Immediately rotate ALL exposed credentials
2. Move all secrets to environment variables or a secrets manager (GCP Secret Manager)
3. Add `.env*` to `.gitignore`
4. Use `gcloud run deploy --set-env-vars` or `--update-secrets` for Cloud Run
5. Audit git history for committed secrets using `git log --all -p -- '*.env*'`

---

### CRIT-02: Next.js 14.2.3 Has Known Critical CVEs
**Severity: CRITICAL | Ungouge App**

**File:** `frontend/package.json` - `"next": "14.2.3"`

Next.js 14.2.3 has multiple known vulnerabilities including:
- **CVE-2024-34350**: Server-Side Request Forgery (SSRF) in Server Actions
- **CVE-2024-34351**: Open redirect vulnerability via Host header
- **CVE-2024-39693**: Denial of Service via crafted HTTP request
- Additional cache poisoning and header injection vectors

**Fix:** Upgrade to Next.js 14.2.20+ or 15.x immediately:
```bash
cd frontend && npm install next@latest
```

---

### CRIT-03: Ephemeral Database on Cloud Run (Dashboard)
**Severity: CRITICAL | Dashboard**

**Files:** `backend/database.py` (line 10), `backend/auth.py` (line 13)

```python
DB_PATH = Path(os.environ.get('DATABASE_PATH', '/tmp/dashboard.db'))
# and
DB_PATH = os.environ.get("DATABASE_PATH", "/tmp/dashboard.db")
```

The dashboard uses SQLite stored in `/tmp/` on Cloud Run. This means:
- **ALL data is lost** when the container restarts (which happens after ~15 min of inactivity)
- All projects, tasks, expenses, time clock entries, and sessions are ephemeral
- The `seed_sample_data()` function re-seeds on every cold start, but any user modifications are lost
- Sessions table is also in `/tmp/`, so users get logged out on every cold start

The settings page even acknowledges this: *"The database resets when Cloud Run spins down"*

**Fix:**
1. Migrate to Cloud SQL (PostgreSQL) or Firestore for persistent storage
2. Use Redis or Cloud Memorystore for session storage
3. Until then, clearly warn users that data is not persistent

---

### CRIT-04: In-Memory Token Blacklist (App)
**Severity: CRITICAL | Ungouge App**

**File:** `backend/services/token_blacklist.py`

The token blacklist uses a Python set (`_blacklisted_tokens`) stored in process memory:
- Tokens survive only until the server restarts
- In a multi-worker or multi-instance deployment, blacklisted tokens on one worker are valid on another
- A logged-out user's JWT remains valid on other server instances
- Revoked tokens can be reused after server restart

**Fix:**
1. Use Redis for token blacklist storage
2. Or use short-lived JWTs (5-15 min) with refresh tokens stored in database
3. For MVP: consider cookie-only auth with server-side sessions (like the dashboard does)

---

### CRIT-05: CORS Allows All Origins (Dashboard)
**Severity: CRITICAL | Dashboard**

**File:** `backend/main.py` (lines 36-41)

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

`allow_origins=["*"]` with `allow_credentials=True` is a dangerous combination. While browsers block `Access-Control-Allow-Origin: *` when credentials are included, some proxies and non-browser clients don't enforce this. This opens the door to:
- Cross-site request forgery from any domain
- Session hijacking via malicious websites
- Data exfiltration from authenticated endpoints

**Fix:** Set `allow_origins` to `["https://dashboard.ungouge.ai"]` specifically.

---

## 4. 🟠 HIGH Issues (Fix Before Public Launch)

### HIGH-01: No Rate Limiting on Dashboard Auth Endpoints
**Severity: HIGH | Dashboard**

**File:** `backend/main.py` - `/auth/login`, `/auth/callback`

The OAuth endpoints have no rate limiting. While Google handles the OAuth rate limiting, the callback endpoint could be abused:
- Rapid-fire callback attempts with invalid codes
- Session table flooding (no cleanup on failed attempts)
- The `cleanup_expired_sessions()` function exists but is never called automatically

**Fix:**
1. Add rate limiting middleware (e.g., `slowapi`)
2. Schedule periodic session cleanup (e.g., on startup or via background task)
3. Limit concurrent sessions per user

---

### HIGH-02: SQL Injection Risk via Dynamic Query Building
**Severity: HIGH | Dashboard**

**File:** `backend/main.py`, `update_task()` (lines ~270-290)

```python
for field in allowed_fields:
    if field in task_data:
        updates.append(f"{field} = ?")
        values.append(task_data[field])
# ...
cursor.execute(f"""
    UPDATE tasks 
    SET {', '.join(updates)}
    WHERE id = ?
""", values)
```

While the field names come from `allowed_fields` (whitelist), and values use parameterized queries, the f-string interpolation of column names is risky if `allowed_fields` is ever expanded carelessly. The current implementation is technically safe because field names are hardcoded, but this pattern is fragile.

**Fix:** Use an ORM (SQLAlchemy) or explicitly map each field to avoid f-string SQL construction entirely.

---

### HIGH-03: No Input Sanitization on Dashboard HTML Rendering
**Severity: HIGH | Dashboard**

**Files:** All static HTML files (`dashboard-v2.html`, `tasks.html`, `expenses.html`, etc.)

The dashboard renders task titles, project names, and descriptions directly into HTML via template literals:

```javascript
// dashboard-v2.html
<div class="task-title">${task.title}</div>
// tasks.html
<div class="task-title">${task.title}</div>
// expenses.html
<td>${expense.description}</td>
```

If a task title or expense description contains `<script>alert('XSS')</script>`, it will execute in the browser. Since only authorized users can create content currently, the risk is lower, but it's still a stored XSS vulnerability.

**Fix:** Escape HTML before rendering:
```javascript
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
```

---

### HIGH-04: Payment Integration is Scaffolded (App)
**Severity: HIGH | Ungouge App**

**File:** `backend/services/payment.py`

The Stripe payment service is almost entirely TODO:
- `create_checkout_session()` - TODO
- `handle_webhook()` - TODO  
- `get_payment_status()` - TODO
- No Stripe webhook verification
- No payment flow connected to quote analysis

The app promises "$19.99 per report" on the pricing page but has no way to collect payment.

**Fix:** Before launch:
1. Implement Stripe Checkout for one-time payments
2. Set up webhook handlers for payment confirmation
3. Gate report access behind confirmed payment
4. Add webhook signature verification

---

### HIGH-05: Email Service in Dev Mode Only (App)
**Severity: HIGH | Ungouge App**

**File:** `backend/services/email_service.py`

```python
EMAIL_DEV_MODE = os.getenv("EMAIL_DEV_MODE", "true").lower() == "true"
```

Email sending only prints to console. This means:
- Password reset tokens are logged to console but never sent to users
- MFA verification codes are logged to console but never emailed
- Email verification links never reach users
- Account recovery is impossible

**Fix:**
1. Set up SendGrid, AWS SES, or Gmail API for production email
2. Configure SMTP settings in production environment
3. Test the full email flow end-to-end

---

### HIGH-06: Debug Endpoint Exposed (Dashboard)
**Severity: HIGH | Dashboard**

**File:** `backend/main.py` (line ~184)

```python
@app.get("/api/debug/static")
def debug_static():
    """List files in static directory"""
```

This endpoint lists all static files and reveals the server's file structure. It has no authentication check and is accessible to anyone.

**Fix:** Remove or protect this endpoint behind authentication.

---

### HIGH-07: Duplicate `const urlParams` in login.html (Dashboard)
**Severity: HIGH (functionality) | Dashboard**

**File:** `backend/static/login.html` (lines 184 and 209)

```javascript
const urlParams = new URLSearchParams(window.location.search); // line 184
// ...
const urlParams = new URLSearchParams(window.location.search); // line 209
```

This is a JavaScript error - `const` cannot be redeclared in the same scope. This will throw a `SyntaxError` in strict mode and may break the error handling and auth check functionality on the login page.

**Fix:** Remove the duplicate declaration or use separate variable names.

---

### HIGH-08: No HTTPS Enforcement (App)
**Severity: HIGH | Ungouge App**

**File:** `backend/main.py`

While the app sets `secure=True` on cookies, there's no middleware to redirect HTTP to HTTPS. If deployed behind a load balancer without HTTPS enforcement, cookies could be sent over plaintext connections.

**Fix:** Add HTTPS redirect middleware:
```python
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
if ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

---

### HIGH-09: Session Token in URL (Dashboard)
**Severity: HIGH | Dashboard**

**File:** `backend/main.py`, `auth_callback()` (line ~178)

```python
response = RedirectResponse(url=f"/?auth_token={session_token}", status_code=302)
```

After OAuth callback, the session token is passed in the URL query string. This means:
- Session tokens appear in browser history
- Session tokens appear in server access logs
- Session tokens may be leaked via `Referer` headers
- Shared links could include active session tokens

**Fix:** Use a short-lived exchange code pattern:
1. Store the session token server-side keyed by a random nonce
2. Pass only the nonce in the URL
3. Exchange the nonce for the session token via an API call, then delete the nonce

---

## 5. 🟡 MEDIUM Issues (Fix Within First Month)

### MED-01: No Database Migrations (App)
**Severity: MEDIUM | Ungouge App**

**File:** `backend/models/database.py`

The app uses SQLAlchemy async models but has no migration system (Alembic). Schema changes require dropping and recreating the database, which means data loss.

**Fix:** Set up Alembic for database migrations.

---

### MED-02: Two Competing Quote Parsers (App)
**Severity: MEDIUM | Ungouge App**

**Files:** `backend/services/quote_parser.py`, `backend/services/quote_parser_gemini.py`

Two separate quote parsing services exist:
1. `quote_parser.py` - Uses OpenAI + Anthropic with OCR fallback
2. `quote_parser_gemini.py` - Uses Google Gemini Vision API

Both are imported but there's no clear selection logic. This creates confusion about which parser is used and doubles the testing surface.

**Fix:** Consolidate into a single parser service with configurable AI backend, or implement a clear fallback chain.

---

### MED-03: Hardcoded Q1 Goals (Dashboard)
**Severity: MEDIUM | Dashboard**

**File:** `backend/static/dashboard-v2.html` (in `renderGoalsPod()`)

```javascript
const q1Goals = [
    { name: 'Launch YouTube Channel', progress: 30, target: '100%' },
    { name: 'Deploy Ungouge.ai', progress: 85, target: '100%' },
    // ...
];
```

Goals are hardcoded in JavaScript. They should be stored in the database or API.

**Fix:** Move goals to the database with CRUD endpoints.

---

### MED-04: No File Upload Size Validation on Frontend (App)
**Severity: MEDIUM | Ungouge App**

**File:** `frontend/src/components/FileUpload.tsx`

The FileUpload component validates file types but the size limit check may not match the backend's 10MB limit defined in `backend/validators.py`. There's no upload progress indicator for large files.

**Fix:** Add consistent file size validation on frontend matching backend limits. Add upload progress feedback.

---

### MED-05: No Automated Session Cleanup (Dashboard)
**Severity: MEDIUM | Dashboard**

**File:** `backend/auth.py`

The `cleanup_expired_sessions()` function exists but is never automatically invoked. Over time, the sessions table grows without bound.

**Fix:** Add a periodic cleanup task or call cleanup on each auth check.

---

### MED-06: Massive HTML Files with Inline JavaScript (Dashboard)
**Severity: MEDIUM | Dashboard**

**Files:** `dashboard-v2.html` (1,833 lines), `tasks.html` (400+ lines), etc.

All JavaScript is inline within HTML files. The dashboard-v2.html file alone is 1,833 lines with hundreds of lines of inline JavaScript. This makes:
- Debugging difficult
- CSP (Content Security Policy) impossible with inline scripts
- Code reuse across pages impossible
- Testing essentially impossible

**Fix:** Extract JavaScript into separate `.js` files. Consider migrating to a frontend framework (even vanilla JS modules would be an improvement).

---

### MED-07: No Content Security Policy Headers (Both)
**Severity: MEDIUM | Both Projects**

Neither application sets CSP headers. This allows:
- Inline script execution (XSS amplification)
- Loading resources from any domain
- Clickjacking attacks

**Fix:** Add CSP headers via middleware. For the app, the existing security headers middleware should include CSP. For the dashboard, add FastAPI middleware.

---

### MED-08: Category Filtering Uses Hardcoded Project Names (Dashboard)
**Severity: MEDIUM | Dashboard**

**File:** `backend/static/dashboard-v2.html`

```javascript
const categoryProjectNames = {
    'ungouge': ['Ungouge.ai Platform', 'Executive Dashboard', 'Business Operations'],
    'youtube': ['YouTube Channel', 'Content Library', 'Podcast Distribution']
};
```

Filtering relies on exact project name matching. If a project is renamed, the filter breaks silently.

**Fix:** Use the `category` field from the database (`project.category`) instead of name matching.

---

### MED-09: No Error Boundaries (App Frontend)
**Severity: MEDIUM | Ungouge App**

The React frontend has no error boundaries. If any component throws during rendering, the entire app crashes with a white screen.

**Fix:** Add React Error Boundaries around major page sections.

---

### MED-10: Dashboard Page Files Don't Check Auth (Dashboard)
**Severity: MEDIUM | Dashboard**

**Files:** `tasks.html`, `expenses.html`, `project-detail.html`

While these pages make API calls that require authentication, the HTML files themselves are served without auth checks via explicit routes:

```python
@app.get("/tasks.html")
def serve_tasks_page():
    return FileResponse(os.path.join(static_dir, "tasks.html"))
```

A user can view the page UI (albeit with empty data) without being authenticated. API calls will fail with 401, but the page structure is still visible.

**Fix:** Either:
1. Add auth checks to the static file serving routes
2. Or use the root route pattern that checks auth before serving files

---

## 6. 🟢 LOW Issues (Nice to Have)

### LOW-01: No Logging Framework (Dashboard)
Uses `print()` statements for all logging. Should use Python's `logging` module with structured output for Cloud Run.

### LOW-02: No Favicon (Dashboard)
No favicon configured. Browsers generate 404s for `/favicon.ico` on every page load.

### LOW-03: Cookie Logging (Dashboard)
**File:** `backend/main.py`, root route (line ~113):
```python
print(f"🔍 All cookies: {request.cookies}")
```
Logs all cookies including session tokens to stdout. Remove in production.

### LOW-04: `onKeyPress` Deprecated (App)
**File:** `frontend/src/components/ChatWidget.tsx`
Uses `onKeyPress` which is deprecated. Use `onKeyDown` instead.

### LOW-05: Mock Data in Dashboard Page (App)
**File:** `frontend/src/app/dashboard/page.tsx`
Dashboard page uses hardcoded mock data instead of fetching from the API.

### LOW-06: Missing `alt` Text on Some Images
Some components reference images without descriptive alt text.

### LOW-07: No `robots.txt` or `sitemap.xml` (App)
Missing SEO essentials for the public-facing website.

### LOW-08: Build Version Comments in Source (Dashboard)
```python
# rebuild Mon Feb  9 15:30:00 EST 2026 - Auth fix: clear stale cookies
```
Build comments in source code. Use git tags/releases instead.

### LOW-09: Settings Page Notification Changes Not Persisted (App)
**File:** `frontend/src/app/dashboard/settings/page.tsx`
```javascript
// TODO: Save to backend
```
Notification preferences aren't saved anywhere.

### LOW-10: Account Deletion Not Implemented (App)
**File:** `frontend/src/app/dashboard/settings/page.tsx`
```javascript
// TODO: Implement account deletion
alert('Account deletion not yet implemented');
```

---

## 7. ✅ What's Working Well

### Ungouge.ai App — Strengths

1. **Exceptional Cost Model Data** 🏆
   - 14 project types with detailed material costs, labor rates, and regional multipliers
   - 6 additional `new_models/` with granular data (concrete, driveway, fence, flooring, garage door, gutter)
   - BLS wage data properly sourced with occupational codes
   - Regional multipliers cover all US regions with zip prefix mapping
   - Red flags and common upsells documented per project type
   - Synonym matching system (`synonyms_and_aliases.json`) for fuzzy matching contractor line items — very clever

2. **Well-Structured Backend Architecture**
   - Clean separation: routers → services → models
   - Comprehensive custom exception hierarchy (`exceptions.py`)
   - Input validation with dedicated `validators.py` (file upload, email, password, quote)
   - FastAPI best practices followed (dependency injection, Pydantic models)
   - Security headers middleware configured

3. **Polished Frontend UX**
   - Professional, modern design with Tailwind CSS
   - Responsive layouts for mobile
   - Nice PriceGauge visualization component
   - ChatWidget with FAQ matching — good UX touch
   - Clear value proposition on landing page
   - Strong privacy-first messaging throughout (footer, about, pricing)

4. **Strong Product Vision**
   - Clear differentiation: "We NEVER sell your data"
   - Pricing transparency ($19.99/report, no subscriptions)
   - Privacy Policy written in plain English — refreshing
   - Terms of Service include "Plain English Summary" — excellent

5. **Auth System (App)**
   - JWT with httpOnly cookies (more secure than localStorage)
   - Token blacklisting on logout
   - MFA via email verification codes
   - Password reset with time-limited tokens
   - Email verification flow
   - bcrypt password hashing

### Executive Dashboard — Strengths

1. **Functional MVP Dashboard**
   - Clean dark theme with professional executive styling
   - Working OAuth 2.0 with Google (server-side redirect, no popups)
   - Category filtering (Ungouge / YouTube) with proper data segregation
   - Time clock with real-time timer — nice founder tool
   - Keyboard shortcuts (/, t, e, s, r, ?)

2. **Good Database Schema**
   - Proper indexes on frequently queried columns
   - CHECK constraints for status and priority fields
   - Foreign keys with CASCADE/SET NULL

3. **API Integration Architecture**
   - Clean API abstraction classes (YouTubeAPI, StripeAPI, GoogleAnalyticsAPI)
   - In-memory caching with TTL for external API responses
   - Graceful fallback when APIs are not configured

4. **Kanban Board Views**
   - Project swimlane layout with collapsible sections
   - Task cards with priority coloring and due date awareness
   - Separate views for Ungouge and YouTube project categories

---

## 8. 📋 Recommended Fix Order

### Phase 1: Security Emergency (Before ANY Deployment) — 1-2 Days

1. **Rotate all exposed credentials** (Google OAuth, Stripe, YouTube, Craftsman API keys)
2. **Move all secrets to environment variables** and remove from source code
3. **Add `.env*` to `.gitignore`** and scrub git history
4. **Upgrade Next.js** to 14.2.20+ (`npm install next@latest`)
5. **Fix CORS** on dashboard to `["https://dashboard.ungouge.ai"]`
6. **Remove debug endpoint** (`/api/debug/static`)
7. **Remove cookie logging** from dashboard root route
8. **Fix duplicate `urlParams`** in login.html

### Phase 2: Auth & Data Integrity — 3-5 Days

9. **Replace in-memory token blacklist** with Redis or database-backed solution
10. **Migrate dashboard to persistent database** (Cloud SQL or Firestore)
11. **Fix session token in URL** issue (use exchange code pattern)
12. **Add rate limiting** to both apps' auth endpoints
13. **Add HTML sanitization** to all dashboard rendered content
14. **Add CSP headers** to both applications
15. **Set up proper email delivery** for the app (SendGrid/AWS SES)

### Phase 3: Launch Readiness — 1-2 Weeks

16. **Implement Stripe payment flow** (checkout → webhook → report access)
17. **Set up Alembic** database migrations for the app
18. **Consolidate quote parsers** into single service with configurable backend
19. **Add React Error Boundaries** to frontend
20. **Extract dashboard JS** into separate files
21. **Add HTTPS redirect** middleware for production
22. **Implement account deletion** endpoint
23. **Implement notification settings** persistence

### Phase 4: Polish — Ongoing

24. Add structured logging to both apps
25. Add monitoring and alerting (Google Cloud Monitoring)
26. Add automated testing (pytest for backend, Jest/Playwright for frontend)
27. Set up CI/CD pipeline
28. Add `robots.txt` and `sitemap.xml`
29. Performance optimization (lazy loading, image optimization)

---

## 9. 🏗️ Architecture Recommendations

### Ungouge App

**Current:** Next.js 14 (frontend) + FastAPI (backend) + SQLite → Good separation, needs production DB

**Recommended Production Architecture:**
```
                    ┌──────────────┐
                    │   Vercel     │
                    │  (Next.js)   │
                    └──────┬───────┘
                           │ API calls
                    ┌──────┴───────┐
                    │  Cloud Run   │
                    │  (FastAPI)   │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────┴─────┐ ┌───┴───┐ ┌─────┴─────┐
        │ Cloud SQL  │ │ Redis │ │   Stripe  │
        │ PostgreSQL │ │       │ │  Webhook  │
        └────────────┘ └───────┘ └───────────┘
```

Key Changes:
1. **PostgreSQL on Cloud SQL** instead of SQLite
2. **Redis** for token blacklist and session caching
3. **Alembic** for schema migrations
4. **Stripe Checkout** with webhook verification
5. **SendGrid** for transactional email
6. **Cloud Storage** for file uploads (quote PDFs/images)

### Executive Dashboard

**Current:** FastAPI + SQLite + Static HTML → Too fragile for production

**Recommended Path:**

**Option A (Quick Fix):** Keep current architecture but:
- Move to Cloud SQL for persistent storage
- Extract JS into modules
- Add proper authentication middleware for static files

**Option B (Better):** Migrate to:
- **Supabase** (PostgreSQL + auth + real-time) as backend
- **React/Next.js** frontend with shared component library from the main app
- This eliminates the duplicated HTML/JS issue entirely

**Option C (Best, Long-term):** Merge the dashboard INTO the Ungouge app as an admin panel, using the same auth system and database. This eliminates an entire deployment, reduces maintenance burden, and consolidates security surface.

---

## 10. 🚀 Launch Readiness Checklist

### Ungouge.ai App

- [ ] 🔴 Rotate and secure all API keys and secrets
- [ ] 🔴 Upgrade Next.js to patched version
- [ ] 🔴 Replace in-memory token blacklist with persistent store
- [ ] 🔴 Set up production database (PostgreSQL)
- [ ] 🟠 Implement Stripe payment flow end-to-end
- [ ] 🟠 Set up production email delivery
- [ ] 🟠 Add rate limiting to auth endpoints
- [ ] 🟠 Add CSP and security headers
- [ ] 🟠 Add HTTPS redirect middleware
- [ ] 🟡 Set up database migrations (Alembic)
- [ ] 🟡 Add error boundaries to React frontend
- [ ] 🟡 Add monitoring and alerting
- [ ] 🟡 Add robots.txt and sitemap.xml
- [ ] 🟡 Set up automated testing
- [ ] 🟡 Configure CI/CD pipeline
- [ ] 🟢 Add structured logging
- [ ] 🟢 Performance optimization pass

### Executive Dashboard

- [ ] 🔴 Rotate all exposed credentials
- [ ] 🔴 Fix CORS to specific origin
- [ ] 🔴 Migrate to persistent database
- [ ] 🔴 Fix duplicate urlParams JS error
- [ ] 🟠 Remove debug endpoint
- [ ] 🟠 Add XSS protection (HTML escaping)
- [ ] 🟠 Remove cookie/token logging
- [ ] 🟠 Fix session token in URL
- [ ] 🟠 Add rate limiting
- [ ] 🟡 Add auth checks to static file routes
- [ ] 🟡 Extract inline JavaScript
- [ ] 🟡 Add automated session cleanup
- [ ] 🟡 Move hardcoded goals to database
- [ ] 🟢 Add structured logging
- [ ] 🟢 Add favicon
- [ ] 🟢 Remove build comments from source

---

## Appendix A: Files Audited

### Ungouge App (38 files)
- `backend/main.py`
- `backend/.env`
- `backend/requirements.txt`
- `backend/exceptions.py`
- `backend/validators.py`
- `backend/models/database.py`
- `backend/models/auth.py`
- `backend/models/quote.py`
- `backend/models/report.py`
- `backend/models/password_reset.py`
- `backend/routers/auth.py`
- `backend/routers/quotes.py`
- `backend/routers/health.py`
- `backend/services/auth.py`
- `backend/services/analyzer.py`
- `backend/services/quote_parser.py`
- `backend/services/quote_parser_gemini.py`
- `backend/services/payment.py`
- `backend/services/logger.py`
- `backend/services/token_blacklist.py`
- `backend/services/mfa_service.py`
- `backend/services/email_service.py`
- `backend/services/bls_data.py`
- `backend/services/synonym_matcher.py`
- `backend/data/project_cost_models.json` (4,593 lines)
- `backend/data/material_costs.json`
- `backend/data/sample_bls_rates.json`
- `backend/data/synonyms_and_aliases.json`
- `backend/data/new_models/*.json` (6 files)
- `frontend/package.json`, `tsconfig.json`
- `frontend/src/app/layout.tsx`, `page.tsx`, `globals.css`
- `frontend/src/app/login/page.tsx`, `register/page.tsx`
- `frontend/src/app/analyze/page.tsx`
- `frontend/src/app/report/[id]/page.tsx`
- `frontend/src/app/dashboard/layout.tsx`, `page.tsx`
- `frontend/src/app/dashboard/quotes/page.tsx`, `account/page.tsx`, `settings/page.tsx`
- `frontend/src/app/pricing/page.tsx`, `about/page.tsx`, `privacy/page.tsx`, `terms/page.tsx`
- `frontend/src/components/Header.tsx`, `Footer.tsx`, `QuoteForm.tsx`, `FileUpload.tsx`, `PriceGauge.tsx`, `ReportCard.tsx`, `ChatWidget.tsx`
- `frontend/src/lib/api.ts`, `seo.ts`

### Executive Dashboard (14 files)
- `backend/main.py`
- `backend/auth.py`
- `backend/database.py`
- `backend/api_integrations.py`
- `backend/requirements.txt`
- `backend/Dockerfile`
- `backend/.env.cloudrun`
- `backend/static/login.html`
- `backend/static/dashboard-v2.html`
- `backend/static/tasks.html`
- `backend/static/expenses.html`
- `backend/static/settings.html`
- `backend/static/projects-ungouge.html`
- `backend/static/projects-youtube.html`
- `backend/static/project-detail.html`

---

## Appendix B: Cost Model Quality Assessment

The cost model data (`project_cost_models.json`) is **exceptionally well-structured** and represents the most valuable IP in the codebase. Key observations:

| Metric | Assessment |
|--------|------------|
| **Project Coverage** | 14 project types + 6 new models = 20 total ✅ |
| **Data Granularity** | Material + labor + crew rates + ranges ✅ |
| **Regional Accuracy** | 8 regions with multipliers (0.9-1.3x) ✅ |
| **BLS Integration** | Proper OCC codes, median + percentile rates ✅ |
| **Red Flags** | Each project type has documented gouging indicators ✅ |
| **Common Upsells** | Each project type identifies common contractor upsells ✅ |
| **Synonym Matching** | 400+ synonyms across flooring, roofing, HVAC, etc. ✅ |
| **Data Currency** | Labeled "2024-2025" — should be verified annually ⚠️ |
| **Edge Cases** | Some project types lack complexity multipliers ⚠️ |

**Recommendation:** This data is the competitive moat. Protect it with proper access controls, update it quarterly, and consider it trade-secret-level IP.

---

*Report generated by Ish (Claude Opus 4.6) on February 9, 2026*
*Total files audited: 52+ across both projects*
*Methodology: Full source code review, security analysis, architecture assessment, and UX evaluation*
