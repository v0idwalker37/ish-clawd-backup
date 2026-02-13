# Legitimate Interest Assessment (LIA)

**Document Reference:** R-09  
**Controller:** UnGouge LLC, Vermont, USA  
**Contact:** legal@ungouge.ai  
**Date:** 2026-02-13  
**Review Date:** 2027-02-13  
**GDPR Basis:** Article 6(1)(f) — Legitimate Interests  

---

## Overview

This document records the Legitimate Interest Balancing Tests conducted by UnGouge LLC for processing activities where Article 6(1)(f) GDPR is relied upon as the lawful basis. Each assessment follows the three-part test required by the ICO and EDPB guidance:

1. **Purpose test** — Is there a legitimate interest behind the processing?
2. **Necessity test** — Is the processing necessary for that purpose?
3. **Balancing test** — Do the individual's interests override the legitimate interest?

---

## Assessment 1: Security Logging

### 1.1 Processing Activity Description

| Field | Detail |
|-------|--------|
| **Data processed** | IP addresses, timestamps, user-agent strings, failed authentication attempts, rate-limit triggers, error codes |
| **Data subjects** | Registered users, unauthenticated visitors |
| **Retention period** | 90 days (rolling), unless preserved for active security investigation |
| **Storage** | Google Cloud Logging, access restricted to infrastructure team |

### 1.2 Purpose Test

**Legitimate interest identified:** Protecting the security and integrity of the UnGouge.ai platform, its infrastructure, and its users' data from unauthorized access, credential stuffing, brute-force attacks, and other malicious activity.

**Whose interest:** UnGouge LLC (controller), all registered users (whose accounts and data must be protected), and the broader public interest in secure online services.

**Is it lawful?** Yes. Security of processing is explicitly recognized under GDPR Recital 49 as a legitimate interest. There is no applicable law prohibiting this logging.

**Is it clearly articulated?** Yes. The purpose is narrowly defined: detect and prevent unauthorized access to the platform.

**Is it a real and present interest?** Yes. Automated attacks against web applications are continuous and well-documented. UnGouge processes sensitive financial data (contractor quotes) that would be valuable to attackers.

### 1.3 Necessity Test

**Is the processing actually necessary for this purpose?**

Yes. Without logging IP addresses and failed authentication attempts, UnGouge would be unable to:
- Detect brute-force or credential-stuffing attacks in progress
- Identify the source of unauthorized access attempts
- Implement IP-based rate limiting or blocking
- Conduct forensic analysis after a security incident
- Comply with breach notification obligations under Art. 33 (which require understanding what happened)

**Could the purpose be achieved with less data?**

- **IP addresses:** Cannot be further minimized — they are the primary identifier for network-level threats. Truncation would defeat the purpose.
- **User-agent strings:** Could theoretically be omitted, but they are essential for distinguishing automated bots from legitimate users. Retained.
- **Timestamps:** Essential for correlation and timeline reconstruction. Cannot be omitted.
- **Failed auth details:** Only the fact of failure and the username attempted are logged — not passwords. This is the minimum necessary.

**Is there a less intrusive alternative?** No reasonable alternative exists. Security logging is a foundational control recognized by ISO 27001, SOC 2, and NIST frameworks.

### 1.4 Balancing Test

**Impact on data subjects:**

- **Nature of data:** IP addresses are personal data but are not special category data. The sensitivity is moderate.
- **Reasonable expectations:** Users reasonably expect that a service handling their financial data logs security events. This is standard industry practice disclosed in our Privacy Policy.
- **Volume of subjects:** All users and visitors, but processing is automated — no human reviews logs unless a security event triggers investigation.
- **Consequences for individuals:** Minimal. Data is used only for security analysis. No profiling, no marketing, no sharing with third parties. Worst case: a legitimate user's IP is temporarily rate-limited (self-correcting).
- **Vulnerable individuals:** No children or vulnerable populations are specifically affected.

**Safeguards in place:**

- 90-day rolling retention with automatic deletion
- Access restricted to infrastructure personnel via IAM roles
- Logs stored encrypted at rest (Google Cloud default encryption)
- No export or sharing of raw logs with third parties
- Processing is automated; human review only on security triggers
- Data subjects informed via Privacy Policy (Section: Security & Logging)
- Right to object honored — though we may demonstrate compelling legitimate grounds per Art. 21(1)

### 1.5 Conclusion

**Result: Legitimate interest is established.**

The interest in platform security is compelling, explicitly recognized by Recital 49, and directly serves the protection of all users' data. Processing is limited to the minimum necessary, retention is short, access is restricted, and the impact on data subjects is low. The safeguards in place adequately protect individuals' rights. No opt-out mechanism is provided for core security logging, as the controller's compelling interest in security (and obligation under Art. 32) overrides the right to object, consistent with Art. 21(1).

---

## Assessment 2: Service Improvement Analytics

### 2.1 Processing Activity Description

| Field | Detail |
|-------|--------|
| **Data processed** | Aggregate usage patterns: feature usage frequency, page navigation flows, session duration, error rates, quote analysis completion rates |
| **Data subjects** | Registered users |
| **Retention period** | Aggregate statistics retained indefinitely; underlying event-level data retained 12 months then deleted or aggregated |
| **Storage** | Google Cloud, internal analytics pipeline |

**Important distinction:** UnGouge does NOT use third-party analytics platforms (e.g., Google Analytics). Analytics are processed internally using first-party, server-side event logging. No data is shared with advertising networks.

### 2.2 Purpose Test

**Legitimate interest identified:** Understanding how users interact with UnGouge.ai to improve service quality, identify bugs, prioritize feature development, and optimize user experience.

**Whose interest:** UnGouge LLC (improving its product and business), and users (who benefit from a better-functioning service).

**Is it lawful?** Yes. Product improvement through analytics is a widely recognized legitimate business interest (Recital 47: "processing of personal data strictly necessary for the purposes of preventing fraud also constitutes a legitimate interest"; product improvement is analogous and well-established in regulatory guidance).

**Is it clearly articulated?** Yes. The purpose is to understand aggregate usage patterns to improve the service — not to profile individual users or make automated decisions about them.

### 2.3 Necessity Test

**Is the processing actually necessary?**

Yes. Without usage analytics, UnGouge cannot:
- Identify which features are used vs. ignored
- Detect systematic errors or UX failures
- Prioritize development resources effectively
- Measure whether changes improve the service

**Could the purpose be achieved with less data?**

Yes — and it is. UnGouge applies the following minimization measures:
- **Aggregation:** Analytics queries return aggregate counts and percentages, not individual user records
- **No behavioral profiling:** No individual-level usage profiles are built
- **No cross-service tracking:** No fingerprinting, no ad-tech identifiers
- **Server-side only:** No client-side tracking scripts or pixels
- **Pseudonymization:** Event-level data uses internal user IDs, not names or emails

**Is there a less intrusive alternative?** The current approach already represents a minimal, privacy-respectful implementation. Pure aggregate analytics without any event-level data would lose the ability to detect bugs and errors in specific flows.

### 2.4 Balancing Test

**Impact on data subjects:**

- **Nature of data:** Usage patterns (which pages visited, which features used). Low sensitivity.
- **Reasonable expectations:** Users reasonably expect a SaaS product to track how its features are used. This is universal practice.
- **Consequences for individuals:** Negligible. No decisions are made about individuals. No content is served differently based on analytics. No data is shared externally.
- **Vulnerable individuals:** Not specifically impacted.

**Safeguards in place:**

- Aggregation at query time — individual records not surfaced in reports
- Pseudonymized event-level data
- No third-party analytics or advertising trackers
- 12-month retention for event-level data
- Access limited to product team
- Disclosed in Privacy Policy
- Right to object honored — users may request exclusion from analytics

### 2.5 Conclusion

**Result: Legitimate interest is established.**

Service improvement analytics using server-side, first-party data with aggregation represents one of the least intrusive forms of analytics processing. The interest is genuine and clearly benefits both the controller and users. Individual impact is negligible. An opt-out mechanism is available for users who object, and their objection will be honored by excluding their events from the analytics pipeline.

---

## Assessment 3: Fraud Prevention

### 3.1 Processing Activity Description

| Field | Detail |
|-------|--------|
| **Data processed** | IP addresses, request rates, API usage patterns, account creation velocity, payment patterns (when Stripe is active), behavioral signals (e.g., rapid-fire quote submissions) |
| **Data subjects** | All users and visitors interacting with the platform |
| **Retention period** | Real-time processing; flagged events retained 180 days for pattern analysis; automated blocks logged for 90 days |
| **Storage** | Google Cloud, internal fraud detection logic |

### 3.2 Purpose Test

**Legitimate interest identified:** Preventing fraud, abuse, and misuse of the UnGouge.ai platform, including but not limited to:
- Automated scraping of the service
- Creation of fake accounts to exploit free tiers or trial periods
- Abuse of the AI analysis API (e.g., using UnGouge as a proxy to Gemini)
- Payment fraud (when Stripe integration is live)
- Denial-of-service through excessive usage

**Whose interest:** UnGouge LLC (protecting its business and infrastructure), legitimate users (whose service quality degrades under abuse), and Recital 47 explicitly recognizes fraud prevention as a legitimate interest.

**Is it lawful?** Yes. Fraud prevention is one of the most clearly established legitimate interests in GDPR jurisprudence and guidance.

### 3.3 Necessity Test

**Is the processing actually necessary?**

Yes. As a $19.99 per-use service with AI processing costs, UnGouge is directly exposed to financial loss from abuse. Without fraud prevention measures:
- Automated bots could consume expensive Gemini API calls
- Fake accounts could exploit any promotional offers
- The platform could be used as a proxy to access AI capabilities
- Payment chargebacks could threaten the business

**Could the purpose be achieved with less data?**

The current approach is already proportionate:
- **Rate limiting** uses only IP + endpoint + time window — the minimum needed
- **Account velocity checks** use only email domain + creation timestamp
- **Behavioral signals** are heuristic-based, not building persistent profiles
- **No credit scoring or background checks** on users
- **No external data enrichment** — all signals are first-party

**Is there a less intrusive alternative?** CAPTCHAs alone are insufficient (easily bypassed). Rate limiting without IP addresses is technically impossible. The current layered approach uses the minimum data necessary.

### 3.4 Balancing Test

**Impact on data subjects:**

- **Nature of data:** IP addresses and request patterns. Moderate sensitivity.
- **Reasonable expectations:** Users expect a paid online service to protect itself against abuse. Rate limiting and fraud checks are standard.
- **Consequences for individuals:**
  - *Legitimate users:* May occasionally trigger a rate limit, resulting in a temporary delay (self-resolving). No permanent consequences.
  - *Flagged accounts:* May be suspended pending manual review. Users can contact support to resolve.
  - *No automated decisions with legal or significant effects* without human review — consistent with Art. 22 requirements.
- **False positives:** Acknowledged risk. Mitigated by human review for any action more severe than temporary rate limiting.

**Safeguards in place:**

- Rate limits are temporary and self-resolving
- Account suspensions require human review before permanent action
- Users can appeal via support (legal@ungouge.ai)
- No external sharing of fraud signals
- 180-day retention for flagged events (proportionate to investigation timelines)
- Disclosed in Privacy Policy and Terms of Service
- Right to object: acknowledged, but compelling grounds for fraud prevention will generally override per Art. 21(1)

### 3.5 Conclusion

**Result: Legitimate interest is established.**

Fraud prevention is explicitly recognized by GDPR Recital 47 as a legitimate interest. UnGouge's measures are proportionate, use minimal data, include human oversight for significant actions, and provide an appeal mechanism. The impact on legitimate users is negligible (occasional rate limiting). For users engaged in actual abuse, the controller's interest clearly overrides. Opt-out is not provided for core fraud prevention controls, as the compelling legitimate interest and the interests of other users justify continued processing per Art. 21(1).

---

## General Notes

### Data Subject Rights

For all processing activities covered by this assessment, data subjects retain:
- **Right to be informed** (Art. 13/14) — addressed in Privacy Policy
- **Right of access** (Art. 15) — requests to legal@ungouge.ai
- **Right to erasure** (Art. 17) — honored unless retention is necessary for security investigation or legal obligation
- **Right to object** (Art. 21) — honored for analytics; for security and fraud prevention, compelling grounds assessment applies

### Review Schedule

This assessment will be reviewed:
- **Annually** (next review: 2027-02-13)
- **Upon material change** to processing activities, data categories, or technical architecture
- **Upon regulatory guidance** from a supervisory authority relevant to these processing activities

### Approval

| Role | Name | Date |
|------|------|------|
| Data Controller | UnGouge LLC | 2026-02-13 |
| Prepared by | Legal/Compliance | 2026-02-13 |

---

*This document is maintained as part of UnGouge LLC's GDPR compliance documentation suite.*
