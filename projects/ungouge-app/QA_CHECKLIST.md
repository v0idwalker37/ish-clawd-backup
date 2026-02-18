# Ungouge.ai — QA & Hardening Checklist
*Soft launch → Production hardening phase*
*Created: 2026-02-17*

## Priority 1: Core Flow (tomorrow morning with Jason)
- [ ] Real E2E: Register → Submit quote → Pay $19.99 → See report on screen
- [ ] Report shows in Dashboard → My Quotes
- [ ] PDF download works
- [ ] Receipt email arrives
- [ ] Try on real mobile device (iPhone)

## Priority 2: Security (Ish can run tonight/tomorrow)
- [ ] Input validation: XSS payloads in quote fields
- [ ] Input validation: SQL injection attempts
- [ ] CSRF protection verification
- [ ] Cookie flags verified in browser (HttpOnly, Secure, SameSite)
- [ ] Rate limiting: hit registration/login limits
- [ ] Auth bypass attempts (tampered cookies, expired tokens)
- [ ] File upload: malicious files (non-PDF, oversized, crafted)
- [ ] IDOR: try accessing another user's quote/report

## Priority 3: Functional Edge Cases
- [ ] Cold start latency (first request after scale-to-zero)
- [ ] Session refresh after 30min (access token expiry)
- [ ] MFA enable → login with MFA → disable
- [ ] Password reset flow
- [ ] Quote with 1 line item vs 20 line items
- [ ] Quote with special characters in fields (unicode, emoji, HTML)
- [ ] Stripe webhook retry (what if webhook arrives late?)
- [ ] Double-submit prevention (click pay twice fast)
- [ ] Back button after payment

## Priority 4: Quality & Polish
- [ ] Analyzer output quality review (are reports useful?)
- [ ] PDF formatting/branding check
- [ ] Error messages user-friendly (not raw stack traces)
- [ ] Loading states visible during slow operations
- [ ] 404 page for bad routes
- [ ] Mobile nav menu works
- [ ] Cross-browser: Chrome, Firefox, Safari

## Priority 5: Ops & Monitoring
- [x] Cloud Run monitoring alerts (5xx, latency, no-traffic)
- [ ] Sentry error tracking
- [ ] Log review: check for warnings/errors in Cloud Run logs
- [ ] Database backup verification
- [ ] Cold start optimization (min instances = 1?)

## Priority 6: Domain Cleanup
- [ ] quotarian.com → ungouge.ai redirect
- [ ] quotarion.app → ungouge.ai redirect
- [ ] quotarion.com → ungouge.ai redirect
(CF API redirect rule failed — needs dashboard or different approach)

## Security Scan Results (2026-02-17 23:45)

| Test | Result | Notes |
|------|--------|-------|
| Cold start latency | ✅ 249ms | No issue |
| SQL injection (login) | ✅ Blocked | Pydantic validation rejects |
| IDOR (cross-user access) | ✅ Blocked | Returns 401/403 |
| Unauthenticated access | ✅ Blocked | Returns 401 |
| Cookie flags | ✅ Correct | HttpOnly, Secure, SameSite=strict |
| Rate limiting (login) | ✅ Working | 429 after 4 attempts |
| XSS in name field | ⚠️ Stored raw | React escapes on render, but backend should sanitize |
| XSS in quote fields | ⚠️ Stored raw | Same — React-safe but needs backend sanitization |
