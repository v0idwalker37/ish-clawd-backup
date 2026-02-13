# Security Implementation Plan
*Created: 2026-02-13 7:09 AM*
*Target: Fix 22 vulnerabilities before launch*

## Status Legend
- ✅ Complete
- 🔄 In Progress
- ⏳ Pending
- ⏭️ Post-Launch

---

## Phase 1: Pre-Launch Critical (Before public launch)

### Frontend (Next.js)
1. ✅ **Next.js upgrade to 14.2.35+** - Already done
2. ✅ **Add CSP headers** - Implemented in next.config.js
3. ✅ **CSRF token middleware** - Created backend/middleware/csrf.py
4. ✅ **Input validation middleware** - Created backend/middleware/input_validation.py
5. ✅ **Rate limiting middleware** - Created backend/middleware/rate_limit.py

### Backend (FastAPI)
6. ✅ **File upload security** - Created backend/middleware/file_security.py
   - ✅ Strip metadata (EXIF/PDF)
   - ✅ File type validation (magic bytes)
   - ✅ Size limits (10MB max)
   - ⏳ Malware scanning (VirusTotal API stub ready)
7. ✅ **Input validation**
   - ✅ Line item descriptions: 500 char max, sanitized
   - ✅ Project type whitelist (34 types)
   - ✅ Region whitelist (51 states + 6 regions)
8. ✅ **SQL injection audit** - All queries use SQLAlchemy ORM (verified safe)
9. ⏳ **Integrate middleware into main.py** - Wire up all new middleware
   - ⏳ CSRF protection on POST/PUT/DELETE
   - ⏳ Rate limiting on endpoints
   - ⏳ Input validation on quote endpoints
   - ⏳ File security on upload endpoint

### Dashboard
10. ✅ **OAuth state parameter** - Already implemented (verified in main.py)
11. ✅ **Rate limiting** - Already implemented (slowapi)
12. ✅ **HSTS header** - Already implemented
13. ✅ **Error sanitization** - Already implemented
14. ⏳ **BOLA audit** - Verify ownership checks on all endpoints
15. ⏳ **API key hashing** - Hash keys before storage (bcrypt)

### Documentation & Legal
16. ⏳ **Privacy policy** - GDPR/CCPA compliant
17. ⏳ **Terms of service**
18. ⏳ **Data retention policy** - Auto-delete quotes after 90 days
19. ⏳ **User data export** - JSON download feature

### DevOps
20. ⏳ **Dependabot enable** - GitHub automated scanning
21. ⏳ **Logging implementation** - Structured JSON logs
22. ⏳ **Security testing** - OWASP ZAP scan

---

## Phase 2: OpenClaw Hardening (This week)

### Command Execution Safety
23. ⏳ **Exec command policy**
   - Safe whitelist: ls, cat, grep, find, git status
   - Require confirmation: rm, mv, chmod, curl
   - Blocked: rm -rf, sudo rm, dd, mkfs
24. ⏳ **File path policy**
   - Whitelist: ~/clawd/, ~/moltbot/
   - Require confirmation: ~/.ssh/, ~/.aws/, ~/.env*
   - Blocked: /etc/, /System/, /private/
25. ⏳ **Security audit log** - `memory/security-audit.log`
26. ⏳ **Panic word mechanism** - "FREEZE" stops all operations
27. ⏳ **Cron job approval** - Show schedule + command before creation

### Memory & Skills
28. ⏳ **Memory file integrity** - Git commits after every session
29. ⏳ **Skill signature verification** - Trust only verified sources

---

## Phase 3: Post-Launch Hardening (After revenue positive)

30. ⏭️ **Session rotation** - Rotate on login/logout
31. ⏭️ **IP + User-Agent binding** - Optional, degrades mobile UX
32. ⏭️ **Refresh token reduction** - 7 days → 24-48 hours
33. ⏭️ **Token revocation list** - Redis cache
34. ⏭️ **CAPTCHA on failed login** - After 3rd attempt
35. ⏭️ **Cloud Run instance limits** - Prevent cost explosion
36. ⏭️ **Central logging** - Papertrail or Logtail
37. ⏭️ **Intrusion detection** - Alert on suspicious patterns
38. ⏭️ **Weekly security review** - Jason reads alert summary

---

## Implementation Order (Today)

### Round 1: Quick wins (1-2 hours)
- [ ] CSP headers
- [ ] CSRF tokens
- [ ] Input validation (line items, project types)
- [ ] OAuth state parameter
- [ ] Dependabot enable

### Round 2: Backend hardening (2-3 hours)
- [ ] File upload security (metadata stripping, size limits)
- [ ] Rate limiting middleware
- [ ] SQL injection audit
- [ ] BOLA audit
- [ ] API key hashing

### Round 3: OpenClaw security (1-2 hours)
- [ ] Exec command policy
- [ ] File path policy
- [ ] Security audit log
- [ ] Panic word mechanism
- [ ] Cron approval workflow

### Round 4: Documentation (1-2 hours)
- [ ] Privacy policy draft
- [ ] Terms of service draft
- [ ] Data retention implementation

---

## Testing Checklist

After each fix:
- [ ] Unit tests pass
- [ ] Manual testing
- [ ] Security test (try to exploit)
- [ ] Document in changelog

Before launch:
- [ ] Full OWASP ZAP scan
- [ ] Manual penetration test
- [ ] Jason review and approval

---

*Total estimated time: 8-12 hours*
*Target completion: Before Ungouge launch (March 1, 2026)*
