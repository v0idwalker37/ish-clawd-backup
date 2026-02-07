# Security Audit Notes - Red Team Research
**Date:** 2026-02-07 (Autonomous Session)
**Scope:** Ungouge.ai app, dashboard.ungouge.ai, OpenClaw gateway

---

## Executive Summary

This document identifies potential attack vectors and security vulnerabilities across three systems:
1. Ungouge.ai application (main quote analysis platform)
2. Dashboard.ungouge.ai (executive dashboard)
3. OpenClaw gateway (AI agent framework on Jason's Mac)

**Threat Model:** External attackers, malicious users, and accidental exposure scenarios.

---

## 1. Ungouge.ai Application Security

### 1.1 File Upload Attack Vectors

**Current Implementation:**
- Users upload quote files (PDF, images, spreadsheets)
- Backend processes files for analysis
- Files stored temporarily or permanently (need to verify)

**Attack Vectors:**

#### 🔴 Critical: Malicious File Uploads
- **Threat:** Executable files disguised as PDFs (polyglot files)
- **Impact:** Remote code execution on server
- **Mitigation needed:**
  - Strict MIME type validation (not just extension checking)
  - File content verification (magic number validation)
  - Sandboxed file processing (containers/VMs)
  - Size limits enforced (currently unclear)
  - Antivirus/malware scanning before processing

#### 🟡 Medium: Path Traversal via Filenames
- **Threat:** Uploaded file with name like `../../etc/passwd`
- **Impact:** Overwrite system files or expose sensitive data
- **Mitigation needed:**
  - Sanitize filenames (strip path separators)
  - Generate random UUIDs for stored files
  - Store uploads outside webroot

#### 🟡 Medium: Denial of Service via Large Files
- **Threat:** Upload massive files to exhaust disk/memory
- **Impact:** Service degradation or crash
- **Mitigation needed:**
  - Hard file size limits (10 MB reasonable for quotes)
  - Rate limiting per user/IP
  - Disk quota monitoring

#### 🟡 Medium: XXE (XML External Entity) Attacks
- **Threat:** If parsing XML/SVG files, external entity expansion
- **Impact:** Server-side request forgery (SSRF), file disclosure
- **Mitigation needed:**
  - Disable external entity resolution in XML parsers
  - Avoid processing SVG/XML unless necessary

**Action Items:**
- [ ] Review file upload implementation in backend
- [ ] Verify MIME type validation
- [ ] Confirm sandboxed processing environment
- [ ] Test with malicious polyglot files
- [ ] Implement content-based validation (not just extension)

---

### 1.2 Authentication & Session Management

**Current Implementation (as of Feb 6 audit):**
- httpOnly cookies (access_token, refresh_token) ✅
- Cookie flags: HttpOnly=true, SameSite=strict, Secure=true (prod) ✅
- Backend reads from cookie OR Bearer header ✅

**Remaining Risks:**

#### 🟡 Medium: JWT Token Expiry Edge Cases
- **Threat:** Race conditions during token refresh
- **Impact:** Session fixation or auth bypass
- **Mitigation needed:**
  - Implement token rotation on refresh
  - Invalidate old refresh tokens after use
  - Track active sessions server-side (logout all sessions)

#### 🟡 Medium: Brute Force on Login
- **Threat:** Automated login attempts
- **Impact:** Account takeover
- **Mitigation needed:**
  - Rate limiting on /auth/login endpoint (5 attempts/15 min per IP)
  - CAPTCHA after 3 failed attempts
  - Account lockout after 10 failed attempts (24h)
  - Monitor for credential stuffing patterns

#### 🟢 Low: Session Fixation
- **Threat:** Attacker sets session ID before victim logs in
- **Impact:** Session hijacking
- **Current status:** Likely mitigated by httpOnly cookies, but verify
- **Action:** Ensure new session token issued on login

**Action Items:**
- [ ] Review token refresh logic for race conditions
- [ ] Implement rate limiting on auth endpoints
- [ ] Add CAPTCHA or similar bot detection
- [ ] Test session fixation scenarios

---

### 1.3 API Security

#### 🔴 Critical: SQL Injection (if using raw SQL)
- **Threat:** User input in SQL queries
- **Impact:** Database compromise, data exfiltration
- **Mitigation:**
  - Use parameterized queries or ORM (SQLAlchemy, Prisma)
  - Never concatenate user input into SQL
  - Least-privilege database user (no DROP, ALTER permissions)

**Need to verify:** Does backend use ORM or raw SQL?

#### 🟡 Medium: NoSQL Injection (if using MongoDB, etc.)
- **Threat:** Malicious payloads in JSON
- **Impact:** Authentication bypass, data leakage
- **Mitigation:**
  - Validate and sanitize all inputs
  - Use schema validation (Pydantic models)

#### 🟡 Medium: Rate Limiting on API Endpoints
- **Threat:** API abuse, DoS, data scraping
- **Impact:** Service degradation, cost inflation (if cloud-hosted)
- **Mitigation needed:**
  - `/analyze-quote`: 5 requests/hour per user (prevent abuse of paid service)
  - `/auth/*`: 10 requests/min per IP
  - Public endpoints: 100 requests/min per IP

#### 🟡 Medium: CORS Misconfiguration
- **Threat:** Allowing requests from any origin
- **Impact:** Cross-site attacks, data leakage
- **Current status:** Need to verify CORS policy
- **Mitigation:**
  - Restrict to specific domains (ungouge.ai, dashboard.ungouge.ai)
  - Never use `Access-Control-Allow-Origin: *` in production

**Action Items:**
- [ ] Audit SQL/database queries for injection risks
- [ ] Implement comprehensive rate limiting
- [ ] Review CORS configuration

---

### 1.4 Input Validation & Sanitization

#### 🔴 Critical: XSS (Cross-Site Scripting)
- **Threat:** Malicious scripts in user inputs reflected in UI
- **Impact:** Session hijacking, phishing, malware distribution
- **High-risk areas:**
  - Quote analysis results displayed to users
  - User profile data (name, email)
  - File metadata (filenames displayed)
- **Mitigation:**
  - Escape all user inputs in frontend (React does this by default, but verify)
  - Content Security Policy (CSP) headers
  - Never use `dangerouslySetInnerHTML` without sanitization

#### 🟡 Medium: Command Injection (if shelling out)
- **Threat:** If backend calls external tools (pdf2text, imagemagick, etc.)
- **Impact:** Remote code execution
- **Mitigation:**
  - Use libraries instead of shell commands
  - If unavoidable, strict input validation and escaping
  - Sandboxed execution environment

#### 🟡 Medium: LDAP/XPATH Injection (if applicable)
- **Threat:** Malicious input in directory queries
- **Impact:** Authentication bypass, data leakage
- **Mitigation:** Parameterized queries, input validation

**Action Items:**
- [ ] Review all user input handling
- [ ] Verify CSP headers in production
- [ ] Audit external tool usage (shell commands)

---

### 1.5 Infrastructure & Deployment

#### 🔴 Critical: Exposed Secrets in Code
- **Threat:** API keys, DB passwords in Git repo
- **Impact:** Complete system compromise
- **Mitigation:**
  - Use environment variables (.env files, NOT committed)
  - Secret management service (Google Secret Manager, Vault)
  - Scan repo for leaked secrets (git-secrets, truffleHog)

#### 🟡 Medium: Insecure Cloud Storage
- **Threat:** Public S3/GCS buckets with uploaded quotes
- **Impact:** Customer data exposure
- **Mitigation:**
  - Private buckets only
  - Signed URLs for temporary access
  - Encryption at rest (AES-256)

#### 🟡 Medium: Unpatched Dependencies
- **Threat:** Known vulnerabilities in npm/pip packages
- **Impact:** Various (RCE, XSS, etc.)
- **Mitigation:**
  - Regular `npm audit` / `pip-audit`
  - Automated dependency updates (Dependabot)
  - Monitor security advisories

**Action Items:**
- [ ] Run `git log -S 'password|api_key|secret'` to scan history
- [ ] Verify cloud storage bucket permissions
- [ ] Run `npm audit` on frontend, `pip-audit` on backend

---

## 2. Dashboard.ungouge.ai Security

### 2.1 OAuth Authentication Flow

**Current Implementation:**
- Google OAuth 2.0 server-side redirect flow ✅
- httpOnly cookies for session ✅

**Remaining Risks:**

#### 🟡 Medium: CSRF on OAuth Callback
- **Threat:** Attacker tricks victim into authorizing attacker's account
- **Impact:** Account linkage attacks
- **Mitigation needed:**
  - Use `state` parameter in OAuth flow (random token)
  - Verify `state` on callback
  - **Action:** Verify this is implemented

#### 🟡 Medium: Redirect URI Manipulation
- **Threat:** Attacker modifies redirect_uri to steal auth code
- **Impact:** Account takeover
- **Mitigation:**
  - Strict redirect_uri validation in Google Console
  - Server-side verification that redirect matches registered URI

**Action Items:**
- [ ] Review OAuth implementation for CSRF protection (state parameter)
- [ ] Verify redirect_uri whitelist in Google OAuth console

---

### 2.2 API Endpoints

#### 🔴 Critical: Unauthenticated Endpoints
- **Threat:** Public access to sensitive data
- **Impact:** Data breach
- **High-risk endpoints:**
  - `/api/tasks` (project tasks)
  - `/api/expenses` (financial data)
  - `/api/projects` (project details)
  - `/api/time-entries` (time tracking)
- **Mitigation:**
  - All endpoints MUST require authentication
  - Test: `curl https://dashboard.ungouge.ai/api/tasks` (should return 401)

#### 🟡 Medium: Insufficient Authorization (IDOR)
- **Threat:** User A accessing User B's data by changing IDs
- **Impact:** Data leakage
- **Example:** `/api/tasks/123` → Change to `/api/tasks/456` (another user's task)
- **Mitigation:**
  - Server-side authorization checks
  - Verify `task.owner_id == current_user.id` before returning data

#### 🟡 Medium: Mass Assignment Vulnerabilities
- **Threat:** User submits extra fields in API requests
- **Impact:** Privilege escalation (e.g., setting `is_admin=true`)
- **Mitigation:**
  - Use allowlists (Pydantic models with explicit fields)
  - Never directly assign `request.json` to database models

**Action Items:**
- [ ] Test all API endpoints for authentication requirement
- [ ] Test IDOR scenarios (access other user IDs)
- [ ] Review Pydantic models for mass assignment protection

---

### 2.3 Database Security

**Current Implementation:**
- SQLite database (development)
- Plan to migrate to PostgreSQL (production?)

**Risks:**

#### 🟡 Medium: SQLite in Production
- **Threat:** File-based DB not suitable for multi-user web apps
- **Impact:** Corruption, performance issues, no concurrent writes
- **Mitigation:**
  - Migrate to PostgreSQL or MySQL for production
  - SQLite acceptable for low-traffic internal tools only

#### 🟡 Medium: Database Credentials in Code
- **Threat:** DB password hardcoded or in committed .env
- **Impact:** Database compromise
- **Mitigation:**
  - Use environment variables
  - Rotate credentials regularly
  - Least-privilege DB user (app should not have DROP DATABASE)

**Action Items:**
- [ ] Confirm production database plan (PostgreSQL)
- [ ] Verify credentials management

---

### 2.4 Frontend Security

#### 🟡 Medium: XSS in Dashboard UI
- **Threat:** Task names, expense descriptions, project titles with malicious scripts
- **Impact:** Session hijacking, data theft
- **Mitigation:**
  - React's default escaping (should be sufficient)
  - CSP headers
  - Audit any `dangerouslySetInnerHTML` usage

#### 🟡 Medium: Sensitive Data in LocalStorage
- **Threat:** Auth tokens in localStorage accessible to XSS
- **Impact:** Session hijacking
- **Current status:** Using httpOnly cookies ✅ (correct approach)
- **Action:** Ensure NO sensitive data in localStorage

**Action Items:**
- [ ] Review frontend for XSS vulnerabilities
- [ ] Confirm no sensitive data in localStorage

---

## 3. OpenClaw Gateway Security

### 3.1 Local API Exposure

**Risk Profile:**
- Gateway runs on Jason's Mac (local network)
- Potentially accessible to other devices on LAN
- File system access, shell commands, browser control

#### 🔴 Critical: Unauthorized Access to Gateway API
- **Threat:** Malicious device on Jason's network accesses gateway
- **Impact:** Full system compromise (file access, command execution)
- **Mitigation:**
  - Gateway should bind to `127.0.0.1` (localhost only), NOT `0.0.0.0`
  - If remote access needed, use authentication tokens
  - Firewall rules to block external access

#### 🟡 Medium: CSRF on Gateway Actions
- **Threat:** Malicious website triggers gateway actions while Jason is logged in
- **Impact:** Unintended file modifications, command execution
- **Mitigation:**
  - CSRF tokens on state-changing operations
  - Verify `Origin` or `Referer` headers

**Action Items:**
- [ ] Verify gateway bind address (should be 127.0.0.1)
- [ ] Review gateway auth mechanism
- [ ] Test CSRF scenarios

---

### 3.2 Tool Permissions & Sandboxing

#### 🟡 Medium: Unrestricted File System Access
- **Threat:** Malicious prompt or skill reads sensitive files
- **Impact:** Credential theft, data exfiltration
- **Current mitigations (from config):**
  - Tool allowlists/denylists
  - Exec security modes
- **Additional needs:**
  - Audit logging of file access
  - Alerts on sensitive file access (`~/.ssh/`, `~/.aws/`, etc.)

#### 🟡 Medium: Command Injection via Exec Tool
- **Threat:** Malicious input in exec commands
- **Impact:** Arbitrary command execution
- **Mitigation:**
  - Input validation in skills
  - Avoid shell=True when possible
  - Audit exec usage in autonomous sessions

**Action Items:**
- [ ] Review exec security settings
- [ ] Implement audit logging for sensitive operations

---

### 3.3 Session Isolation

#### 🟡 Medium: Cross-Session Data Leakage
- **Threat:** Agent in one session accessing data from another
- **Impact:** Privacy breach (e.g., shared workspace across users)
- **Mitigation:**
  - Verify session isolation in OpenClaw architecture
  - Separate memory/context per session

**Action Items:**
- [ ] Verify session isolation in OpenClaw docs
- [ ] Test cross-session access scenarios

---

### 3.4 Channel Security (Telegram, etc.)

#### 🟡 Medium: Message Spoofing
- **Threat:** Attacker spoofs Telegram messages to trigger actions
- **Impact:** Unauthorized commands
- **Mitigation:**
  - Telegram bot token kept secret
  - Verify sender ID matches Jason's Telegram ID
  - Rate limiting on message processing

#### 🟡 Medium: Sensitive Data in Chat Logs
- **Threat:** Credentials, API keys sent via Telegram stored in logs
- **Impact:** Data exposure if device compromised
- **Mitigation:**
  - Avoid sending sensitive data via chat
  - Encrypted logging or ephemeral messages

**Action Items:**
- [ ] Review Telegram auth implementation
- [ ] Audit chat logs for sensitive data

---

## 3.5 Code Audit Results (Feb 7, 2026)

### Ungouge.ai Backend - Security Review

**Files Audited:**
- `backend/routers/quotes.py` (API endpoints)
- `backend/validators.py` (Input validation)
- `backend/main.py` (App configuration)

#### ✅ Strengths (Good Security Practices)

1. **CORS Configuration** (`main.py`)
   - Explicit origin allowlist (no `*` wildcard)
   - Credentials enabled with strict origins
   - Explicit methods and headers (no wildcards)

2. **Security Headers** (`main.py`)
   - X-Content-Type-Options: nosniff ✅
   - X-Frame-Options: DENY ✅
   - X-XSS-Protection: enabled ✅
   - Strict-Transport-Security (production) ✅
   - Content-Security-Policy ✅

3. **Rate Limiting** (`main.py`, `quotes.py`)
   - Global: 100/minute per IP
   - Quote uploads: 5/hour per IP
   - Quote submissions: 10/hour per IP

4. **Input Validation** (`validators.py`)
   - File size limits (10 MB max)
   - MIME type and extension checking
   - PDF/image integrity validation
   - String sanitization (removes control chars, null bytes)
   - Email/password strength validation

5. **Authentication & Authorization**
   - httpOnly cookies for tokens ✅
   - CSRF protection enabled ✅
   - Access control checks on quote retrieval
   - User ownership validation (IDOR protection)

6. **Database Security**
   - Using SQLAlchemy ORM (parameterized queries) ✅
   - No raw SQL concatenation found
   - Pagination limits enforced (max 100 per page)

7. **Error Handling**
   - Global exception handler prevents error leakage
   - Custom exception types with user-friendly messages
   - Detailed logging server-side, generic messages to clients

#### 🟡 Weaknesses & Gaps

1. **File Upload Security** (`validators.py`)
   - **Missing:** Magic number validation (only checks MIME type header + extension)
   - **Missing:** Antivirus/malware scanning
   - **Missing:** Sandboxed file processing (files processed in main app)
   - **Concern:** PyPDF2 is older library (potential known CVEs)
   - **Risk Level:** MEDIUM-HIGH
   - **Recommendation:** 
     - Add magic number validation for PDFs (`%PDF` signature)
     - Use `pikepdf` instead of PyPDF2 (more actively maintained)
     - Process uploads in isolated container/lambda
     - Consider ClamAV integration for virus scanning

2. **Content Security Policy** (`main.py`)
   - **Issue:** `'unsafe-inline'` for both scripts AND styles
   - **Impact:** Weakens XSS protection significantly
   - **Recommendation:**
     - Remove `'unsafe-inline'` for scripts
     - Use nonces or hashes for inline scripts
     - Keep `'unsafe-inline'` for styles if needed (lower risk)
     - Add `connect-src 'self'` to restrict API calls
     - Add `img-src 'self' data:` to control image sources
   - **Better CSP:**
     ```
     default-src 'self'; 
     script-src 'self'; 
     style-src 'self' 'unsafe-inline'; 
     connect-src 'self'; 
     img-src 'self' data:; 
     font-src 'self'; 
     object-src 'none'; 
     frame-ancestors 'none'; 
     base-uri 'self'; 
     form-action 'self'
     ```

3. **Session Management**
   - **Gap:** Token rotation on refresh not verified
   - **Gap:** No server-side session invalidation visible
   - **Recommendation:** Implement token rotation and session tracking

4. **API Security**
   - **Missing:** API request/response logging for audit trail
   - **Missing:** Anomaly detection (unusual quote patterns)
   - **Recommendation:** Add request logging, monitor for abuse patterns

5. **Environment Variables**
   - **Concern:** `.env` file present in backend/ (should be .gitignored)
   - **Action Required:** Verify .env is NOT committed to Git

#### ⚠️ Critical Action Items

1. **BEFORE LAUNCH:**
   - [ ] Scan Git history for secrets: `git log -S 'password|api_key|secret'`
   - [ ] Verify `.env` is in `.gitignore`
   - [ ] Test file upload with polyglot PDF/EXE
   - [ ] Harden CSP (remove unsafe-inline for scripts)
   - [ ] Add magic number validation to file uploads

2. **SHORT-TERM:**
   - [ ] Replace PyPDF2 with pikepdf
   - [ ] Implement file processing in isolated environment
   - [ ] Add ClamAV or similar virus scanning
   - [ ] Implement API audit logging
   - [ ] Add token rotation on refresh

---

## 4. Recommendations Summary

### Immediate (Pre-Launch) - Critical

1. **Ungouge.ai:**
   - [ ] Implement strict file upload validation (MIME types, content verification)
   - [ ] Add rate limiting to all API endpoints
   - [ ] Scan Git history for leaked secrets
   - [ ] Test SQL injection on all database queries
   - [ ] Verify CORS configuration (no wildcard in prod)

2. **Dashboard:**
   - [ ] Test all API endpoints for authentication requirement
   - [ ] Implement IDOR protection (user-owned resource checks)
   - [ ] Add CSRF protection to OAuth flow (state parameter)

3. **OpenClaw Gateway:**
   - [ ] Verify gateway binds to 127.0.0.1 only
   - [ ] Review exec security settings

### Short-Term (Post-Launch) - Medium Priority

4. **Ungouge.ai:**
   - [ ] Implement CAPTCHA on login
   - [ ] Set up automated dependency scanning (Dependabot)
   - [ ] Add CSP headers
   - [ ] Implement comprehensive logging and monitoring

5. **Dashboard:**
   - [ ] Migrate from SQLite to PostgreSQL
   - [ ] Set up automated backups
   - [ ] Implement admin audit logging

6. **OpenClaw Gateway:**
   - [ ] Add audit logging for sensitive file access
   - [ ] Implement alerts for unusual activity

### Long-Term - Low Priority

7. **All Systems:**
   - [ ] Penetration testing by external security firm
   - [ ] Bug bounty program (post-public launch)
   - [ ] Security training for any additional developers
   - [ ] Incident response plan

---

## 5. Testing Checklist

### Manual Tests to Run

**Ungouge.ai:**
- [ ] Upload malicious file (polyglot PDF/EXE)
- [ ] Upload file with path traversal filename (`../../etc/passwd.pdf`)
- [ ] Upload 100 MB file (test size limit)
- [ ] SQL injection in all form inputs: `' OR '1'='1' --`
- [ ] XSS in quote analysis: `<script>alert('XSS')</script>`
- [ ] Brute force login (verify lockout)
- [ ] Access API without auth token (should 401)

**Dashboard:**
- [ ] Access `/api/tasks` without login (should 401)
- [ ] Login as User A, try to access User B's task ID
- [ ] Submit task with extra fields: `{"title": "Test", "is_admin": true}`
- [ ] Test OAuth flow with manipulated `redirect_uri`

**OpenClaw Gateway:**
- [ ] Attempt to connect from another device on LAN
- [ ] Send crafted command via Telegram (if applicable)
- [ ] Attempt to read `~/.ssh/id_rsa` via prompt

---

## 6. Resources & Tools

**Security Scanning:**
- `npm audit` (Node.js dependencies)
- `pip-audit` (Python dependencies)
- `git-secrets` (scan for leaked credentials)
- `truffleHog` (deep Git history scan)
- OWASP ZAP (web app scanner)
- Burp Suite Community (manual testing)

**Monitoring:**
- Sentry (error tracking)
- CloudWatch / Google Cloud Monitoring
- fail2ban (brute force protection)

---

**End of Security Audit Notes - 2026-02-07**
**Next Steps:** Share with Jason, prioritize fixes, implement before launch.
