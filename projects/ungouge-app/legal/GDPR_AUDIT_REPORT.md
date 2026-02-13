# GDPR Compliance Audit Report — UnGouge.ai

**Audit Date:** February 13, 2026
**Auditor:** Automated GDPR/DSGVO Expert System + Manual Code Review
**Scope:** Full application stack (backend, frontend, legal documents)
**Application:** UnGouge.ai — Contractor Quote Verification Tool
**Entity:** UnGouge LLC (Vermont, USA)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Automated Scanner Results](#2-automated-scanner-results)
3. [Data Protection Impact Assessment (DPIA)](#3-data-protection-impact-assessment-dpia)
4. [Privacy Policy vs. Code Gap Analysis](#4-privacy-policy-vs-code-gap-analysis)
5. [Detailed Findings by GDPR Article](#5-detailed-findings-by-gdpr-article)
6. [Remediation Roadmap](#6-remediation-roadmap)
7. [Appendix — Data Flow Map](#7-appendix--data-flow-map)

---

## 1. Executive Summary

### Overall Assessment: 🟡 MODERATE RISK — Needs Remediation Before Launch

UnGouge.ai demonstrates **strong foundational security practices** — httpOnly cookies, bcrypt password hashing, CSRF protection, rate limiting, input validation, security headers, and structured logging. The GDPR data subject rights endpoints (GET/DELETE `/auth/my-data`) are implemented and functional.

However, **several critical gaps** must be addressed before the application processes EU/EEA personal data in production:

| Category | Status | Priority |
|----------|--------|----------|
| Legal basis documentation | 🟡 Partial | HIGH |
| Data subject rights (Art. 15-22) | 🟡 Partial (export & delete exist; rectification, restriction, objection missing) | HIGH |
| Cookie consent mechanism | 🔴 Missing | CRITICAL |
| Data retention enforcement | 🟡 Built but not wired | HIGH |
| Records of Processing Activities (Art. 30) | 🔴 Missing | HIGH |
| Data Processing Agreements (Art. 28) | 🔴 Not documented | HIGH |
| International transfer safeguards (Chapter V) | 🟡 SCCs mentioned but not executed | MEDIUM |
| DPIA (Art. 35) | 🔴 Not previously conducted (now provided below) | HIGH |
| Consent for data transfer to Google Gemini | 🟡 Documented in policy; no runtime consent | HIGH |
| Privacy by Design (Art. 25) | 🟢 Strong technical implementation | LOW |
| Data breach notification (Art. 33-34) | 🟡 Policy documented; no incident response procedure | MEDIUM |
| DPO designation | ⚪ Not required (< 20 employees, no large-scale monitoring) | N/A |

**Estimated effort to reach compliance:** 2-3 weeks of focused engineering + legal review.

---

## 2. Automated Scanner Results

The GDPR Compliance Checker script (`gdpr_compliance_checker.py`) was run against the backend codebase.

### Raw Output Summary

| Metric | Value |
|--------|-------|
| Files Scanned | 65 (includes venv — inflated counts) |
| Compliance Score | 0/100 (heavily skewed by venv false positives) |
| Critical Issues | 36 |
| High Issues | 3,258 |
| Medium Issues | 38 |

### Interpretation

The scanner's score of 0/100 is **not representative** of actual compliance. The vast majority of "high" findings (3,258) are false positives from:

- **venv/site-packages/** — Third-party library files containing email regex patterns, IP address handling, etc.
- **test_*.py files** — Test data containing numbers that match German ID patterns
- **data/*.json** — Cost model data with numeric patterns

**Actual production code findings (filtered):**

| Finding | Files Affected | Real Risk |
|---------|---------------|-----------|
| Email addresses logged in auth failures | `services/logger.py` | MEDIUM — email logged in `log_auth_failure()` |
| IP addresses logged | `services/logger.py`, `routers/auth.py` | LOW — legitimate security logging |
| Verification tokens logged in dev mode | `routers/auth.py` | LOW — dev-only, gated by environment check |
| No consent mechanism detected | Frontend-wide | CRITICAL — no cookie banner or consent management |
| MFA codes stored in DB (unencrypted column) | `models/database.py` | MEDIUM — short-lived (10 min) but plaintext |

---

## 3. Data Protection Impact Assessment (DPIA)

*Per GDPR Article 35 — Required when processing is likely to result in a high risk to the rights and freedoms of natural persons.*

### 3.1 DPIA Threshold Assessment

| WP29 Criterion | Applicable? | Details |
|----------------|-------------|---------|
| Evaluation/scoring | ⚠️ Partial | AI analysis of quotes produces assessments ("overpriced", "fair") but does not profile individuals |
| Automated decision-making with legal/significant effects | ❌ No | Reports are informational only; no automated decisions affect individuals |
| Systematic monitoring | ❌ No | No location tracking, no behavioral monitoring |
| Sensitive/special category data | ❌ No | No health, biometric, racial, political data |
| Large-scale data processing | ❌ No | Single-use consumer tool, not mass surveillance |
| Matching/combining datasets | ⚠️ Partial | Quotes sent to Google Gemini API for analysis; BLS data cross-referenced |
| Vulnerable data subjects | ❌ No | Adults 18+ only; no children, employees, patients |
| Innovative technology | ⚠️ Partial | AI/LLM analysis of user-uploaded documents |
| Data transferred outside EU | ✅ Yes | Data processed in US; sent to Google Cloud (Gemini API) |

**DPIA Determination:** DPIA is **recommended** (2+ criteria met: innovative AI processing + cross-border transfer + dataset combining). While not strictly mandatory under strict reading, it is **best practice** given Gemini API processing of uploaded documents.

### 3.2 Processing Description

| Element | Description |
|---------|-------------|
| **Purpose** | Analyze contractor quotes to determine fair pricing |
| **Data categories** | Email, name, project location (city-level), contractor quotes (names, addresses, prices, line items), uploaded files (images/PDFs of quotes) |
| **Data subjects** | Homeowners (users), contractors (named in quotes, not users of the system) |
| **Recipients** | Google (Gemini API), Stripe (planned), SendGrid (planned) |
| **Retention** | 30d anonymous, 90d authenticated, until deletion for saved quotes |
| **Legal basis** | Contract performance (Art. 6(1)(b)) for core service; Legitimate interest (Art. 6(1)(f)) for security logging and service improvement |

### 3.3 Necessity and Proportionality

| Principle | Assessment |
|-----------|-----------|
| **Purpose limitation** | ✅ Data used only for quote analysis; no secondary marketing use |
| **Data minimization** | ✅ Only collects what's needed for analysis |
| **Accuracy** | ✅ Users can correct profile data; quote data is user-submitted |
| **Storage limitation** | 🟡 Retention policy defined but NOT enforced in code |
| **Integrity/confidentiality** | ✅ TLS, bcrypt, httpOnly cookies, CSRF, security headers |

### 3.4 Risk Assessment

| Risk | Likelihood | Impact | Residual Risk | Mitigation |
|------|-----------|--------|---------------|------------|
| Unauthorized access to quote data | Low | High | **Medium** | Auth, RBAC, encryption at rest (claimed but verify) |
| Data breach exposing PII | Low | High | **Medium** | Security headers, rate limiting, structured logging |
| Gemini API data retention/misuse | Medium | High | **High** | Google DPA required; verify no-training config |
| Quote data not deleted per retention policy | High | Medium | **High** | Retention middleware built but NOT wired up |
| Third-party contractor PII in quotes | Medium | Medium | **Medium** | Contractors named in quotes are data subjects too |
| IP address logging without consent | Medium | Low | **Low** | Legitimate interest (security); document in policy |
| Cross-border transfer without safeguards | Medium | High | **High** | SCCs mentioned but not executed |

### 3.5 DPIA Conclusion

**Overall risk level: MEDIUM-HIGH**

The primary risks are:
1. **Data retention not enforced** — quotes persist indefinitely until middleware is wired
2. **No executed DPA with Google** for Gemini API processing
3. **No cookie consent mechanism** for EU users
4. **Contractor data subjects** — third-party personal data in quotes lacks specific legal basis documentation

---

## 4. Privacy Policy vs. Code Gap Analysis

### 4.1 Gaps Where Policy Claims Exceed Code Reality

| # | Privacy Policy Claims | Code Reality | Risk | GDPR Article |
|---|----------------------|-------------|------|-------------|
| **GAP-01** | "Uploaded quotes are automatically deleted after 90 days" (§6.1) | `cleanup_expired_quotes()` is implemented in `middleware/data_retention.py` but **no cron job, scheduler, or startup hook calls it**. Quotes persist indefinitely. | 🔴 CRITICAL | Art. 5(1)(e) — Storage limitation |
| **GAP-02** | "Cookie Consent Banner: When required by law, we display a cookie consent banner" (§8.4) | **No cookie consent component exists** in the frontend. No `CookieConsent`, `CookieBanner`, or similar component found. | 🔴 CRITICAL | Art. 6(1)(a), ePrivacy Directive |
| **GAP-03** | "We respect 'Do Not Track' (DNT) browser signals" (§8.5) | **No DNT header detection** in backend or frontend code. No middleware or hook checks for DNT. | 🟡 MEDIUM | Voluntary commitment in policy |
| **GAP-04** | "Encryption at Rest: Uploaded quotes and personal data are encrypted at rest using AES-256" (§9) | Database is SQLite in dev (`ungouge.db`). **No application-level encryption at rest** is implemented. Relies entirely on hosting provider's disk encryption. | 🟡 MEDIUM | Art. 32(1)(a) |
| **GAP-05** | "You can export all your quotes and reports as PDF or JSON" (frontend privacy page) | Only JSON export via `GET /auth/my-data`. **No PDF export** is implemented. | 🟡 LOW | Art. 20 — Data portability |
| **GAP-06** | "Payment processing is secured by Stripe" (multiple references) | Stripe integration is **scaffolded but not functional**. `payment.py` has TODO comments throughout. Currently the app skips payment entirely. | 🟡 LOW (pre-launch) | Art. 13(1)(e) — if claiming Stripe when not using it |
| **GAP-07** | Policy mentions contact email `legal@ungouge.ai`; frontend privacy page uses `privacy@ungouge.ai` | **Inconsistent contact addresses** across legal docs and frontend. | 🟡 LOW | Art. 13(1)(a) |
| **GAP-08** | "We will notify affected users within 72 hours" (§10) | **No breach notification procedure, template, or automation exists** in code. | 🟡 MEDIUM | Art. 33-34 |
| **GAP-09** | "Standard Contractual Clauses (SCCs)" for international transfers (§7.2) | **No executed SCCs** found or referenced. Merely stated in policy text. | 🔴 HIGH | Art. 46(2)(c) |
| **GAP-10** | Policy §8.2 describes "Functional" and "Analytics" cookies as optional | **No opt-in/opt-out mechanism** for any cookie category. All cookies are set without user choice. | 🔴 CRITICAL | ePrivacy Directive, Art. 6(1)(a) |
| **GAP-11** | "Regular Reviews: We conduct periodic security reviews" (§9) | **No evidence** of scheduled security audits or penetration testing. | 🟡 MEDIUM | Art. 32(1)(d) |
| **GAP-12** | Policy frontend page date says "Last updated: February 3, 2024" | Legal PRIVACY_POLICY.md says "February 13, 2026". **Date mismatch** between rendered page and actual policy. | 🟡 MEDIUM | Art. 13 — transparency |

### 4.2 Gaps Where Code Does More Than Policy Describes

| # | Code Behavior | Policy Coverage | Risk | GDPR Article |
|---|--------------|----------------|------|-------------|
| **GAP-13** | `log_auth_failure()` logs email addresses of failed login attempts | Policy §3.2 mentions "Log Data: IP address, access times, pages viewed" but **doesn't mention email logging** | 🟡 MEDIUM | Art. 13(1)(d) — categories of data |
| **GAP-14** | `log_quote_submission()` logs IP address + user_id + project_type | Not specifically described in policy as a retention category | 🟡 LOW | Art. 13(2)(a) — retention periods |
| **GAP-15** | MFA codes stored as plaintext in User model (`mfa_code` column) | Policy mentions security measures but MFA code storage isn't addressed | 🟡 MEDIUM | Art. 32 — appropriate security |
| **GAP-16** | Registration logs verification token in dev mode with email | Acceptable in dev, but log infrastructure could leak in misconfigured staging | 🟡 LOW | Art. 32 |

### 4.3 Areas of Good Alignment ✅

| Policy Claim | Code Implementation | Status |
|-------------|-------------------|--------|
| "We never sell your personal data" | No third-party marketing, lead-gen, or data broker integrations | ✅ Verified |
| httpOnly cookies for auth | `httponly=True, samesite="strict"` on all auth cookies | ✅ Verified |
| Access token 30min / Refresh 7d | `ACCESS_TOKEN_EXPIRE_MINUTES=30`, `REFRESH_TOKEN_EXPIRE_DAYS=7` | ✅ Verified |
| Password hashed with bcrypt | `CryptContext(schemes=["bcrypt"])` | ✅ Verified |
| Right to access (data export) | `GET /auth/my-data` — comprehensive JSON export | ✅ Verified |
| Right to erasure (data deletion) | `DELETE /auth/my-data` — cascading delete of all user data | ✅ Verified |
| CSRF protection | `fastapi-csrf-protect` with httpOnly cookie | ✅ Verified |
| Rate limiting | slowapi on all sensitive endpoints (login, register, upload) | ✅ Verified |
| Security headers | X-Content-Type-Options, X-Frame-Options, CSP, HSTS (prod) | ✅ Verified |
| File metadata stripping | EXIF removal from images, PDF metadata stripping | ✅ Verified |
| Token blacklist on logout | Both access and refresh tokens blacklisted | ✅ Verified |

---

## 5. Detailed Findings by GDPR Article

### Art. 5 — Principles of Processing

| Principle | Status | Notes |
|-----------|--------|-------|
| Lawfulness, fairness, transparency | 🟡 | Legal bases documented in policy; transparency gaps in logging disclosures |
| Purpose limitation | ✅ | Data used only for stated purposes |
| Data minimization | ✅ | Only necessary data collected |
| Accuracy | 🟡 | No dedicated rectification endpoint (only profile name update via PUT /auth/me) |
| Storage limitation | 🔴 | **Retention policy exists in code but is never executed** |
| Integrity & confidentiality | 🟡 | Strong transport security; at-rest encryption unverified |
| Accountability | 🔴 | No Art. 30 records, no DPA documentation |

### Art. 6 — Lawfulness of Processing

| Processing Activity | Legal Basis Claimed | Assessment |
|---------------------|-------------------|------------|
| Quote analysis | Contract (Art. 6(1)(b)) | ✅ Appropriate |
| Payment processing | Contract (Art. 6(1)(b)) | ✅ Appropriate |
| Account communications | Contract / Legit. interest | ✅ Appropriate |
| Service improvement | Legitimate interest (Art. 6(1)(f)) | 🟡 No documented balancing test |
| Fraud prevention / security logs | Legitimate interest (Art. 6(1)(f)) | 🟡 No documented balancing test |
| Analytics cookies | Consent (Art. 6(1)(a)) — per policy | 🔴 **No consent mechanism implemented** |

### Art. 7 — Conditions for Consent

- **Finding:** No consent management platform (CMP) or cookie consent banner exists
- **Impact:** Any processing based on consent (analytics cookies) is unlawful without valid consent
- **Recommendation:** Implement cookie consent with granular opt-in before setting non-essential cookies

### Art. 12-14 — Transparency & Information Obligations

| Requirement | Status |
|-------------|--------|
| Identity of controller | ✅ UnGouge LLC identified |
| Contact details | 🟡 Inconsistent (legal@ vs privacy@) |
| Purposes of processing | ✅ Documented |
| Legal basis for each purpose | ✅ Table in policy §4 |
| Recipients/categories | ✅ Google, Stripe, hosting, email |
| International transfers | 🟡 Mentioned but safeguards not executed |
| Retention periods | ✅ Documented per category |
| Data subject rights | ✅ Documented |
| Right to lodge complaint with DPA | ✅ Referenced with EDPB link |
| Automated decision-making info | ✅ "Not subject to automated decision-making" |

### Art. 15-22 — Data Subject Rights

| Right | Article | Implementation Status |
|-------|---------|---------------------|
| Access | Art. 15 | ✅ `GET /auth/my-data` — returns full JSON export |
| Rectification | Art. 16 | 🟡 **Partial** — `PUT /auth/me` updates name only. Cannot correct email (UI says "Email cannot be changed"). Cannot correct quote data. |
| Erasure | Art. 17 | ✅ `DELETE /auth/my-data` — cascading delete |
| Restriction | Art. 18 | 🔴 **Not implemented** — no mechanism to restrict processing while issues resolved |
| Portability | Art. 20 | 🟡 **Partial** — JSON export only, no PDF. Machine-readable ✅ |
| Objection | Art. 21 | 🔴 **Not implemented** — no mechanism to object to legitimate interest processing |
| Automated decisions | Art. 22 | ⚪ N/A — no automated decisions with legal effects |

### Art. 25 — Data Protection by Design and Default

| Measure | Status |
|---------|--------|
| Minimal data collection | ✅ |
| httpOnly secure cookies | ✅ |
| Password hashing (bcrypt) | ✅ |
| CSRF protection | ✅ |
| Input validation & sanitization | ✅ |
| File upload security (type, size, metadata strip) | ✅ |
| Rate limiting on sensitive endpoints | ✅ |
| Security headers (CSP, HSTS, X-Frame-Options) | ✅ |
| Token blacklisting | ✅ |
| Timing-attack resistant password check | ✅ |

**Assessment:** Privacy by design implementation is **excellent**.

### Art. 28 — Data Processors

| Processor | DPA Status | Notes |
|-----------|-----------|-------|
| Google (Gemini API) | 🔴 **No executed DPA** | Google Cloud DPA terms exist but must be formally accepted |
| Stripe | 🟡 **TBD** | Not yet integrated; Stripe DPA auto-applies |
| Hosting provider | 🔴 **Unknown** | No hosting provider DPA documented |
| SendGrid | 🔴 **Not yet set up** | Will need DPA when integrated |

### Art. 30 — Records of Processing Activities (ROPA)

**Status: 🔴 Missing**

No ROPA exists. Required contents:
- Name and contact details of controller
- Purposes of processing
- Categories of data subjects and personal data
- Categories of recipients
- Transfers to third countries
- Retention periods
- Security measures description

### Art. 32 — Security of Processing

| Measure | Status |
|---------|--------|
| Encryption in transit (TLS) | ✅ HTTPS redirect in production |
| Encryption at rest | 🟡 Claimed but not implemented at application level |
| Pseudonymization | ❌ Not implemented |
| Confidentiality (access controls) | ✅ Auth required for user data |
| Integrity (input validation) | ✅ Comprehensive validation |
| Availability (backups) | 🔴 Not documented |
| Regular testing | 🔴 No evidence of security testing schedule |

### Art. 33-34 — Breach Notification

**Status: 🟡 Partial**

- Policy commits to 72-hour notification ✅
- Structured security logging exists ✅
- **No incident response procedure documented** 🔴
- **No breach notification template** 🔴
- **No DPA contact list for notification** 🔴

### Art. 44-49 — International Transfers

**Status: 🟡 Requires Action**

- Data processed in US (UnGouge LLC is a US entity)
- Data sent to Google Gemini API (US-based processing)
- Policy mentions SCCs but **no evidence of executed SCCs**
- EU-US Data Privacy Framework may apply if Google is certified (verify)
- For EU users accessing the service, adequate safeguards required

---

## 6. Remediation Roadmap

### 🔴 P0 — Critical (Must fix before processing EU data)

| # | Issue | Action | Effort | GDPR Article |
|---|-------|--------|--------|-------------|
| R-01 | **No cookie consent mechanism** | Implement cookie consent banner with granular opt-in (e.g., `react-cookie-consent` or custom). Block non-essential cookies until consent given. | 2-3 days | Art. 6(1)(a), ePrivacy |
| R-02 | **Data retention not enforced** | Wire `cleanup_expired_quotes()` to a scheduler (APScheduler, celery-beat, or cron). Run daily. Also wire `cleanup_expired_tokens()`. | 1 day | Art. 5(1)(e) |
| R-03 | **No Records of Processing Activities** | Create ROPA document listing all processing activities per Art. 30 requirements. | 1 day | Art. 30 |
| R-04 | **No DPA with Google (Gemini API)** | Execute Google Cloud DPA. Verify Gemini API configuration doesn't use data for model training. Document in ROPA. | 1 day (legal) | Art. 28 |
| R-05 | **SCCs not executed** | Execute SCCs for international data transfers or verify EU-US DPF applicability for all processors. | 1-2 days (legal) | Art. 46 |

### 🟡 P1 — High (Fix before public launch)

| # | Issue | Action | Effort | GDPR Article |
|---|-------|--------|--------|-------------|
| R-06 | **Missing Art. 16 rectification** | Add endpoint to update email address. Add ability to edit/correct quote data (at minimum location, contractor name). | 2-3 days | Art. 16 |
| R-07 | **Missing Art. 18 restriction of processing** | Add account suspension/restriction flag. When set, data is retained but not processed. Expose via API. | 1-2 days | Art. 18 |
| R-08 | **Missing Art. 21 right to object** | Add opt-out mechanism for legitimate interest processing (service improvement analytics). | 1 day | Art. 21 |
| R-09 | **Legitimate interest balancing test** | Document balancing tests for: security logging, service improvement, fraud prevention. | 1 day (legal) | Art. 6(1)(f) |
| R-10 | **Privacy policy date mismatch** | Update frontend privacy page date to match actual PRIVACY_POLICY.md date. | 15 minutes | Art. 12 |
| R-11 | **Inconsistent contact emails** | Standardize on one email (recommend `legal@ungouge.ai` per PRIVACY_POLICY.md). Update frontend. | 15 minutes | Art. 13 |
| R-12 | **Email logged in auth failures** | Consider hashing or truncating email in `log_auth_failure()` to minimize PII in logs. Or document as legitimate interest. | 30 minutes | Art. 5(1)(c) |
| R-13 | **Breach notification procedure** | Create incident response plan, notification templates, DPA contact list. | 1 day | Art. 33-34 |
| R-14 | **MFA codes stored as plaintext** | Hash MFA codes before storage (compare hashed values) or accept risk given 10-min expiry. Document decision. | 2 hours | Art. 32 |
| R-15 | **DNT not honored despite policy claim** | Either implement DNT signal detection or remove claim from privacy policy. | 1 day or 15 min | Policy alignment |

### 🟢 P2 — Medium (Address within 3 months of launch)

| # | Issue | Action | Effort | GDPR Article |
|---|-------|--------|--------|-------------|
| R-16 | **No PDF data export** | Add PDF report export in addition to JSON for data portability. | 2-3 days | Art. 20 |
| R-17 | **No application-level encryption at rest** | Implement field-level encryption for PII columns (email, name) or document reliance on infrastructure encryption. | 3-5 days | Art. 32 |
| R-18 | **Account deletion not wired in frontend settings** | Settings page shows "Delete Account" button with `alert('Account deletion not yet implemented')`. Wire to `DELETE /auth/my-data`. | 2 hours | Art. 17 |
| R-19 | **No data backup/recovery documentation** | Document backup strategy, recovery procedures, and testing schedule. | 1 day | Art. 32 |
| R-20 | **Third-party contractor data** | Quotes contain contractor PII (names, addresses). Document legal basis (legitimate interest) and add notice that users should have obtained quotes legitimately. | 1 day (legal) | Art. 6, Art. 14 |
| R-21 | **Hosting provider DPA** | Execute DPA with hosting/infrastructure provider. | 1 day (legal) | Art. 28 |

---

## 7. Appendix — Data Flow Map

```
┌──────────────────────────────────────────────────────────────┐
│                        USER (EU/US)                          │
│  Provides: email, name, password, quote files, project info  │
└──────────────────────────┬───────────────────────────────────┘
                           │ HTTPS (TLS 1.2+)
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js)                        │
│  Sets: auth cookies (httpOnly, secure, samesite=strict)       │
│  Collects: form data, file uploads                            │
│  Stores: nothing in localStorage (cookies only)               │
└──────────────────────────┬───────────────────────────────────┘
                           │ HTTPS + httpOnly cookies
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI)                          │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Auth Router │  │Quote Router │  │  Security Middleware │  │
│  │  - register  │  │ - submit    │  │  - CORS             │  │
│  │  - login     │  │ - parse     │  │  - CSRF             │  │
│  │  - MFA       │  │ - report    │  │  - Rate Limit       │  │
│  │  - my-data   │  │ - list      │  │  - Security Headers │  │
│  │  - logout    │  │             │  │  - Audit Logging    │  │
│  └──────┬───────┘  └──────┬──────┘  └─────────────────────┘  │
│         │                 │                                    │
│         ▼                 ▼                                    │
│  ┌──────────────────────────────────┐                         │
│  │         SQLite Database           │                         │
│  │  Tables: users, quotes,           │                         │
│  │  quote_line_items, analysis_      │                         │
│  │  reports, payments, tokens        │                         │
│  │  ⚠️ No app-level encryption       │                         │
│  │  ⚠️ Retention cleanup NOT wired   │                         │
│  └──────────────────────────────────┘                         │
└──────────────────────┬───────────────────────────────────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
┌─────────────┐ ┌───────────┐ ┌──────────┐
│ Google       │ │ Stripe    │ │ SendGrid │
│ Gemini API   │ │ (planned) │ │ (planned)│
│              │ │           │ │          │
│ Receives:    │ │ Receives: │ │ Receives:│
│ - Quote      │ │ - Card    │ │ - Email  │
│   images/PDF │ │   details │ │   address│
│ - Project    │ │ - Amount  │ │ - Name   │
│   details    │ │           │ │          │
│              │ │           │ │          │
│ ⚠️ No DPA    │ │ ⚠️ Not yet │ │ ⚠️ Not   │
│   executed   │ │ integrated│ │ integrated│
└─────────────┘ └───────────┘ └──────────┘

LOGGING FLOWS:
  - Auth events → structured JSON logs (user_id, IP, action)
  - Security events → security.jsonl (requests, errors, access denied)
  - Quote submissions → structured logs (quote_id, user_id, IP)
  - ⚠️ Auth failures log email addresses
  - ⚠️ Log retention = 365 days (defined but not enforced)
```

### Data Categories Collected

| Category | Data Elements | Legal Basis | Retention |
|----------|--------------|-------------|-----------|
| Account data | Email, name, password hash | Contract (Art. 6(1)(b)) | Until account deletion |
| Auth tokens | JWT access/refresh, MFA codes | Contract | 30min / 7d / 10min |
| Quote data | Project type, location, contractor name, line items, prices | Contract | 30d anon / 90d auth (NOT ENFORCED) |
| Uploaded files | Images, PDFs of contractor quotes | Contract | 90d (NOT ENFORCED) |
| Security logs | IP addresses, user agents, auth events, emails (failures) | Legitimate interest (Art. 6(1)(f)) | 365d (NOT ENFORCED) |
| Payment data | Transaction IDs, amounts (via Stripe) | Contract | 7 years (legal requirement) |

---

## Certification

This audit report was generated on **February 13, 2026** using:
- Automated GDPR Compliance Checker (gdpr_compliance_checker.py)
- Manual code review of all backend routes, models, services, middleware
- Manual review of all frontend pages and components
- Cross-reference analysis between privacy policy and actual code behavior
- DPIA methodology per WP29 guidelines and GDPR Art. 35

**This report does not constitute legal advice.** A qualified Data Protection Officer or legal counsel should review these findings before they are actioned. The automated scanner results should be interpreted with awareness of false positive rates, particularly when scanning directories containing third-party dependencies.

---

*Report generated by GDPR/DSGVO Expert Skill v1.0*
