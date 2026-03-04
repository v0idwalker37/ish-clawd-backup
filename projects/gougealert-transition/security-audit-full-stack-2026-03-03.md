# Full-Stack Security Audit (OWASP + Red-Team) — 2026-03-03

## Scope
- App repo: `projects/ungouge-app` (FastAPI backend + Next.js frontend)
- Runtime/ops: OpenClaw gateway host posture and control plane
- Focus: OWASP Top 10 risk mapping + practical red-team attack paths

## Methodology (executed)
1. OpenClaw security audit: `openclaw security audit --deep`
2. Frontend dependency scan: `npm audit --omit=dev --audit-level=high --json`
3. Backend dependency integrity: `pip check`, `pip list --outdated`, `pip-audit`
4. Static pattern scans:
   - potential hardcoded secret patterns
   - broad `except:` usage and risky execution calls
   - CORS wildcard checks
5. Auth/access quick endpoint review across backend routers.

---

## Executive Summary

### Overall
- **Status:** Functionally stable, but not security-complete for public national automation.
- **Critical findings:** 2
- **High findings:** 4
- **Medium findings:** 6
- **Low findings:** 5

### Top Risks Right Now
1. **Untrusted skill code present** (`skills/evolver`) with dangerous exec/env-harvesting signatures (critical).
2. **Vulnerable dependencies** in both frontend and backend (high).
3. **Legacy public domain still indexable** (`ungouge.ai`) with old sitemap/robots (high reputational/PII-surface risk).
4. **OpenClaw reverse-proxy trust not configured** (warn; low impact while loopback-only).

---

## Findings Detail

## F-01 (CRITICAL) — Untrusted skill code safety findings
- Evidence: OpenClaw deep audit reports `skills/evolver` with multiple dangerous patterns:
  - shell execution (`child_process`) and env-harvesting + network-send indicators.
- Risk: potential credential exfiltration / arbitrary command behavior if executed.
- Recommendation:
  - quarantine/remove `skills/evolver` unless explicitly trusted and manually audited line-by-line.
  - keep disabled from operational flows.

## F-02 (HIGH) — Frontend dependency vulnerabilities
- Evidence from npm audit:
  - `jspdf <=4.1.0` high-severity vulnerabilities (injection/object injection).
  - `next` version range includes advisories (DoS class advisories).
- Risk: client-side injection surface and framework-level denial-of-service vectors.
- Recommendation:
  - upgrade `jspdf` to `>=4.2.0` immediately.
  - plan phased Next.js security upgrade path with compatibility testing.

## F-03 (HIGH) — Backend dependency vulnerabilities
- Evidence from `pip-audit`:
  - vulnerabilities in: `cryptography`, `python-jose`, `python-multipart`, `starlette`, `pillow`, `ecdsa`.
- Risk: known CVEs in auth/file-handling/framework layers.
- Recommendation:
  - patch sprint with pinned upgrades and regression tests.
  - priority: `python-jose`, `python-multipart`, `starlette`, `cryptography`.

## F-04 (HIGH) — Legacy domain still publicly indexable
- Evidence (preflight):
  - `ungouge.ai` returns HTTP 200 live marketing content.
  - `robots.txt` still `Allow: /` and old sitemap exposed.
- Risk: stale/legacy brand exposure; privacy and legal posture drift.
- Recommendation:
  - immediate sunset mode on old Vercel project (`NEXT_PUBLIC_SUNSET_MODE=1`) + redeploy.
  - follow with redirect + Search Console removals.

## F-05 (MEDIUM) — Broad exception handling in parser/auth areas
- Evidence from static scan: multiple bare `except:` occurrences in auth/parser/validator files.
- Risk: swallowing security-relevant exceptions, ambiguous failure handling.
- Recommendation:
  - replace bare except with typed exceptions and explicit logging context.

## F-06 (MEDIUM) — Upgrade debt in security-sensitive packages
- Evidence: many outdated packages including FastAPI/Starlette/OpenAI/SQLAlchemy/Cryptography.
- Risk: lagging security patch baseline and compounding future upgrade risk.
- Recommendation:
  - quarterly dependency update policy + monthly security patch window.

## F-07 (MEDIUM) — Operational misconfiguration warning
- Evidence: `gateway.trustedProxies` unset warning.
- Risk: if gateway is ever reverse-proxied publicly without trusted proxy config, local-client checks can be spoofed.
- Recommendation:
  - keep loopback-only OR configure trusted proxies before any proxy exposure.

## F-08 (LOW/MEDIUM) — Group policy config mismatch
- Evidence: Telegram allowlist mode with empty allow lists (message drops).
- Risk: operational reliability (missed alerts), not direct exploit.
- Recommendation:
  - set explicit allow list or open policy intentionally.

## F-09 (LOW) — No immediate CORS wildcard finding
- Evidence: backend CORS configuration uses explicit origins/methods/headers.
- Risk: currently acceptable.
- Recommendation:
  - keep explicit list; avoid wildcard in production.

---

## OWASP Top 10 Mapping (2021)

### A01 Broken Access Control — **Medium (improving)**
- Positive: protected routes generally require auth dependency.
- Remaining: continue IDOR tests per endpoint and role boundaries.

### A02 Cryptographic Failures — **High**
- Dependency CVEs in crypto/auth stack (`python-jose`, `cryptography`).

### A03 Injection — **Medium**
- Positive: ORM usage and input sanitization present.
- Risk remains in vulnerable libraries and content generation pathways.

### A04 Insecure Design — **Medium (improving)**
- Positive: legal gate, kill-switch, signed compliance token, rollback hooks added.
- Remaining: complete production adapter hardening before full automation.

### A05 Security Misconfiguration — **High**
- Legacy domain still public/indexable.
- Proxy trust warning and ops config drift.

### A06 Vulnerable/Outdated Components — **High**
- Confirmed by npm audit + pip-audit.

### A07 Identification & Authentication Failures — **Medium**
- MFA and auth flows exist; maintain brute-force and token abuse tests.

### A08 Software & Data Integrity Failures — **Medium**
- Signed compliance token path exists (good).
- Need stronger supply-chain policy (lockfiles, provenance checks, signed release process).

### A09 Security Logging & Monitoring Failures — **Medium (improving)**
- Positive: legal gate audit logging and structured security logging.
- Remaining: centralized alerting thresholds and incident automation.

### A10 SSRF / Request Forgery classes — **Low/Medium**
- No direct SSRF sink identified in quick scan.
- Next/Image optimizer advisory indicates framework-level DoS exposure if misconfigured.

---

## Red-Team Scenarios (targeted)

## RT-01 Compliance bypass attempt
- Attack: publish artifact without valid compliance token.
- Expected: HTTP 403.
- Current: enforced in `/api/publish-gateway` ✅

## RT-02 Kill-switch bypass
- Attack: publish while global kill-switch enabled.
- Expected: HTTP 503 block.
- Current: enforced ✅

## RT-03 Pass abuse replay
- Attack: rapid quote uploads under same project pass.
- Expected: 429 once thresholds reached.
- Current: total/hourly guardrails now implemented ✅

## RT-04 Event state abuse
- Attack: illegal lifecycle transitions (e.g., DETECTED -> ACTIVE directly).
- Expected: transition rejection.
- Current: guarded transition matrix implemented ✅

## RT-05 Legacy domain leakage
- Attack: SEO crawl/index old domain content.
- Expected: noindex/disallow and/or redirect.
- Current: not yet remediated ❌

## RT-06 Dependency exploitability
- Attack: known CVE exploitation in stale libs.
- Expected: patched baseline.
- Current: pending patch sprint ❌

---

## Prioritized Remediation Plan

### Next 24 hours
1. Quarantine/remove untrusted `skills/evolver` from active environment.
2. Contain `ungouge.ai` immediately (sunset mode + robots/sitemap suppression).
3. Patch high-risk deps:
   - frontend `jspdf` first,
   - backend `python-multipart`, `python-jose`, `starlette`, `cryptography`.

### Next 72 hours
4. Run full regression and security test suite post-upgrade.
5. Add targeted IDOR/authz negative tests for quote/report/event endpoints.
6. Add alert thresholds for legal gate rejects, publish rejects, kill-switch activations.

### Next 1–2 weeks
7. Establish dependency policy (monthly patch cadence, CVE gate in CI).
8. Add release integrity controls (artifact hashing, provenance checks).
9. Formalize incident response runbook for weather automation failures.

---

## Final Assessment
Architecture direction is strong and materially improved (legal gate, tokenized publish, kill-switch, rollback, pass abuse controls). The remaining blockers are mostly **ops hygiene + dependency security + legacy domain containment**, not fundamental product architecture flaws.
