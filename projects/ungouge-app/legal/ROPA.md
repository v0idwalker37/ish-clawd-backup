# Records of Processing Activities (ROPA)

**Pursuant to Article 30(1) of the General Data Protection Regulation (EU) 2016/679**

---

| Field | Detail |
|---|---|
| **Document Owner** | UnGouge LLC |
| **Version** | 1.0 |
| **Date Created** | February 13, 2026 |
| **Last Reviewed** | February 13, 2026 |
| **Next Review Due** | August 13, 2026 |
| **Classification** | Internal / Confidential |

---

## 1. Controller Information

| Field | Detail |
|---|---|
| **Controller Name** | UnGouge LLC |
| **Registered Address** | Vermont, USA |
| **Contact Email** | legal@ungouge.ai |
| **Data Protection Officer** | Not required (fewer than 20 employees; processing is not core activity involving large-scale systematic monitoring or special category data) |
| **EU Representative (Art. 27)** | Not yet appointed — to be designated if monitoring confirms regular offering of services to EU data subjects |

> **Note:** UnGouge LLC is a US-based entity. This ROPA is maintained voluntarily as a best-practice measure and in anticipation of potential applicability of the GDPR where services are accessed by individuals located in the EU/EEA. If monitoring confirms that the service is directed at or regularly used by EU data subjects, an Art. 27 representative will be appointed.

---

## 2. Processing Activities

### 2.1 User Registration & Account Management

| Field | Detail |
|---|---|
| **Activity ID** | PA-001 |
| **Purpose of Processing** | To create and manage user accounts; authenticate users; enable access to paid services |
| **Lawful Basis (Art. 6)** | **6(1)(b)** — Performance of a contract (Terms of Service); **6(1)(f)** — Legitimate interest in account security |
| **Categories of Data Subjects** | Registered users (US homeowners; potentially EU/EEA visitors) |
| **Categories of Personal Data** | Full name, email address, password (bcrypt-hashed — original plaintext is never stored) |
| **Special Category Data (Art. 9)** | None |
| **Source of Data** | Directly from the data subject via registration form |
| **Recipients / Categories of Recipients** | Internal systems only; Google Cloud Platform (infrastructure processor) |
| **Third Country Transfers** | Data stored on Google Cloud (US region). For EU data subjects, transfer mechanism: EU Standard Contractual Clauses (SCCs) incorporated into Google Cloud DPA |
| **Retention Period** | Account data retained for the lifetime of the account + 90 days post-deletion request (to complete deletion pipeline). Inactive accounts purged after 12 months of inactivity with prior notice |
| **Technical & Organisational Measures** | Passwords hashed with bcrypt; httpOnly secure cookies (access token: 30 min, refresh token: 7 days); CSRF protection; rate limiting on registration/login endpoints; input validation and sanitisation |

---

### 2.2 Contractor Quote Analysis (Core Service)

| Field | Detail |
|---|---|
| **Activity ID** | PA-002 |
| **Purpose of Processing** | To analyse contractor quotes submitted by users; verify pricing fairness; generate verification reports |
| **Lawful Basis (Art. 6)** | **6(1)(b)** — Performance of a contract (delivery of the purchased report service) |
| **Categories of Data Subjects** | Registered and anonymous users; indirectly: contractors named in quotes, property owners at quoted addresses |
| **Categories of Personal Data** | Property addresses, contractor business names, quote line items and pricing, uploaded quote documents (images/PDFs — may contain names, addresses, phone numbers, licence numbers) |
| **Special Category Data (Art. 9)** | None |
| **Source of Data** | Directly from the data subject via quote upload form / manual entry |
| **Recipients / Categories of Recipients** | Google Cloud Platform (infrastructure); Google Gemini API (AI analysis processor — quote content transmitted for analysis) |
| **Third Country Transfers** | Data processed by Google Gemini API (US). Transfer mechanism for EU data subjects: EU SCCs per Google Cloud / AI DPA |
| **Retention Period** | **Anonymous users:** 30 days from report generation. **Authenticated users:** 90 days from report generation. After retention period, quote data and uploaded files are permanently deleted |
| **Technical & Organisational Measures** | File metadata stripping on upload (EXIF, GPS, embedded metadata removed); input validation; files stored in access-controlled cloud storage buckets; AI API calls use encrypted transit (TLS 1.2+); no persistent storage of data by Gemini API (configured for zero data retention / no model training) |

---

### 2.3 Payment Processing

| Field | Detail |
|---|---|
| **Activity ID** | PA-003 |
| **Purpose of Processing** | To process payments for verification reports ($19.99/report) |
| **Lawful Basis (Art. 6)** | **6(1)(b)** — Performance of a contract (payment for service); **6(1)(c)** — Legal obligation (tax/financial record-keeping) |
| **Categories of Data Subjects** | Paying users |
| **Categories of Personal Data** | Name, email, billing address, payment card details (handled entirely by Stripe — UnGouge never receives or stores raw card numbers; only Stripe customer ID, last 4 digits, and transaction metadata are retained) |
| **Special Category Data (Art. 9)** | None |
| **Source of Data** | Directly from data subject via Stripe-hosted payment elements |
| **Recipients / Categories of Recipients** | Stripe, Inc. (payment processor — independent controller for PCI-DSS compliance; processor for transaction execution on UnGouge's behalf) |
| **Third Country Transfers** | Stripe processes data in the US. Transfer mechanism for EU data subjects: EU SCCs per Stripe DPA |
| **Retention Period** | Transaction records: retained for duration required by applicable tax law (typically 7 years for US tax purposes). Stripe customer IDs: retained for lifetime of account + post-deletion retention period |
| **Technical & Organisational Measures** | PCI-DSS compliant via Stripe Elements (card data never touches UnGouge servers); HTTPS-only payment flows; Stripe webhook signature verification; idempotency keys for payment requests |

> **Status:** Payment processing via Stripe is **planned but not yet implemented**. This entry will be updated when the integration goes live.

---

### 2.4 Security & Access Logging

| Field | Detail |
|---|---|
| **Activity ID** | PA-004 |
| **Purpose of Processing** | To detect and prevent unauthorised access, fraud, abuse, and security incidents; to maintain system integrity and availability |
| **Lawful Basis (Art. 6)** | **6(1)(f)** — Legitimate interest in security of the service and protection of users |
| **Legitimate Interest Assessment** | Interest: protecting service and user data from attacks. Necessity: logging is essential for incident detection/response. Balance: minimal privacy impact; logs contain technical identifiers, not content data. Data subjects can object under Art. 21 |
| **Categories of Data Subjects** | All users and visitors (authenticated and anonymous) |
| **Categories of Personal Data** | IP addresses, user agent strings, request timestamps, authentication event logs (login success/failure, token refresh), rate-limiting trigger records, CSRF validation failures |
| **Special Category Data (Art. 9)** | None |
| **Source of Data** | Automatically collected from HTTP requests and application events |
| **Recipients / Categories of Recipients** | Google Cloud Platform (infrastructure — Cloud Logging) |
| **Third Country Transfers** | Logs stored on Google Cloud (US). Transfer mechanism: EU SCCs per Google Cloud DPA |
| **Retention Period** | Security logs: 90 days. Rate-limiting records: 24 hours. Authentication failure logs: 30 days |
| **Technical & Organisational Measures** | Access to logs restricted to authorised personnel; logs encrypted at rest and in transit; no logging of passwords, tokens, or full request bodies; automated log rotation and deletion |

---

### 2.5 Email Communications

| Field | Detail |
|---|---|
| **Activity ID** | PA-005 |
| **Purpose of Processing** | To send transactional emails (account verification, password reset, purchase receipts, report delivery notifications); to respond to user enquiries |
| **Lawful Basis (Art. 6)** | **6(1)(b)** — Performance of a contract (transactional communications necessary for service delivery); **6(1)(f)** — Legitimate interest in responding to enquiries |
| **Categories of Data Subjects** | Registered users; individuals who contact legal@ungouge.ai |
| **Categories of Personal Data** | Name, email address, communication content |
| **Special Category Data (Art. 9)** | None |
| **Source of Data** | Directly from data subject (registration, enquiry); generated by system events (transaction triggers) |
| **Recipients / Categories of Recipients** | Email service provider (to be specified when selected — e.g., SendGrid, AWS SES); Google Cloud Platform |
| **Third Country Transfers** | Email provider (US-based, to be confirmed). Transfer mechanism: EU SCCs per provider DPA |
| **Retention Period** | Transactional email logs: 90 days. Support correspondence: 1 year from last communication |
| **Technical & Organisational Measures** | TLS encryption for email transit; SPF/DKIM/DMARC configured; no marketing emails sent without explicit consent; unsubscribe mechanism for any future optional communications |

---

### 2.6 Data Retention & Automated Deletion

| Field | Detail |
|---|---|
| **Activity ID** | PA-006 |
| **Purpose of Processing** | To enforce data minimisation by automatically deleting personal data after the defined retention period; to comply with deletion requests (Art. 17) |
| **Lawful Basis (Art. 6)** | **6(1)(c)** — Legal obligation (GDPR data minimisation principle, Art. 5(1)(e)); **6(1)(f)** — Legitimate interest in maintaining a clean, compliant data environment |
| **Categories of Data Subjects** | All users (anonymous and authenticated) |
| **Categories of Personal Data** | All categories listed in PA-001 through PA-005 |
| **Special Category Data (Art. 9)** | None |
| **Source of Data** | Internal systems (data already collected under other processing activities) |
| **Recipients / Categories of Recipients** | None (internal processing only) |
| **Third Country Transfers** | N/A (deletion occurs within existing infrastructure) |
| **Retention Schedule** | See table below |
| **Technical & Organisational Measures** | Automated deletion jobs (cron-based); deletion verification logging; backup purge aligned with retention periods; permanent deletion (not soft-delete) after retention window closes |

#### Retention Schedule Summary

| Data Category | Anonymous Users | Authenticated Users | Legal Hold Override |
|---|---|---|---|
| Quote data & uploaded files | 30 days | 90 days | Yes — extended if required by legal proceedings |
| Account data (name, email, hashed password) | N/A | Lifetime of account + 90 days post-deletion | Yes |
| Security logs | 90 days | 90 days | Yes |
| Payment/transaction records | N/A | Per applicable tax law (up to 7 years) | Yes |
| Support correspondence | 1 year from last contact | 1 year from last contact | Yes |
| Rate-limiting records | 24 hours | 24 hours | No |

---

## 3. Sub-Processors

| Processor | Role | Data Accessed | DPA in Place | Transfer Mechanism | Location |
|---|---|---|---|---|---|
| **Google Cloud Platform** | Infrastructure hosting, storage, logging | All categories | Yes — Google Cloud DPA | EU SCCs (incorporated) | United States |
| **Google Gemini API** | AI-powered quote analysis | Quote content, uploaded documents | Yes — Google AI DPA | EU SCCs (incorporated) | United States |
| **Stripe, Inc.** *(planned)* | Payment processing | Name, email, billing address, payment details | To be executed prior to go-live | EU SCCs (Stripe DPA) | United States |

> All sub-processors are required to:
> - Process data only on documented instructions from UnGouge LLC
> - Ensure persons authorised to process data are under confidentiality obligations
> - Implement appropriate technical and organisational security measures
> - Assist UnGouge in responding to data subject rights requests
> - Delete or return data upon termination of the processing agreement
> - Make available all information necessary to demonstrate compliance

---

## 4. International Data Transfers

UnGouge LLC is established in the United States. All data is stored and processed in the United States.

For personal data originating from EU/EEA data subjects, the following safeguards apply:

| Transfer | Mechanism | Status |
|---|---|---|
| EU → Google Cloud (US) | Standard Contractual Clauses (Module 2: Controller to Processor) per Google Cloud DPA | Active |
| EU → Google Gemini API (US) | Standard Contractual Clauses per Google AI terms | Active |
| EU → Stripe (US) | Standard Contractual Clauses per Stripe DPA | Pending (planned integration) |

A Transfer Impact Assessment (TIA) should be completed for each transfer when EU user volume becomes material.

---

## 5. Technical and Organisational Security Measures (Art. 32)

### 5.1 Encryption & Data Protection
- Passwords hashed using bcrypt (cost factor ≥ 10)
- All data in transit encrypted via TLS 1.2+
- Data at rest encrypted via Google Cloud default encryption (AES-256)
- Uploaded file metadata stripped (EXIF, GPS, embedded PII removed)

### 5.2 Access Control & Authentication
- httpOnly, Secure, SameSite cookies for session management
- Short-lived access tokens (30 minutes) with refresh tokens (7 days)
- CSRF token protection on all state-changing endpoints
- Role-based access control for administrative functions

### 5.3 Input Validation & Abuse Prevention
- Server-side input validation and sanitisation on all endpoints
- Rate limiting on authentication, upload, and API endpoints
- Request size limits on file uploads
- Content-type validation for uploaded files

### 5.4 Infrastructure Security
- Google Cloud Platform managed infrastructure with SOC 2 Type II certification
- Automated security patching
- Network-level firewalling and DDoS protection
- Logging and monitoring via Google Cloud operations suite

### 5.5 Organisational Measures
- Access to production systems limited to authorised personnel
- Security incident response procedure documented
- Regular review of access permissions
- Sub-processor agreements with security obligations

---

## 6. Data Subject Rights Procedures

UnGouge LLC facilitates the following rights for EU/EEA data subjects:

| Right | Article | Implementation |
|---|---|---|
| **Right of Access** | Art. 15 | Data export available via account settings or upon request to legal@ungouge.ai |
| **Right to Rectification** | Art. 16 | Users can update name/email in account settings; other corrections via legal@ungouge.ai |
| **Right to Erasure** | Art. 17 | Account deletion available in settings; triggers deletion of all associated data per retention schedule |
| **Right to Restriction** | Art. 18 | Upon request to legal@ungouge.ai; account flagged and processing suspended |
| **Right to Data Portability** | Art. 20 | Structured JSON export of user data and quote history available upon request |
| **Right to Object** | Art. 21 | Upon request to legal@ungouge.ai; applicable to processing based on legitimate interest (PA-004, PA-005) |
| **Rights re: Automated Decision-Making** | Art. 22 | AI analysis provides informational reports only — no decisions with legal or similarly significant effects are made solely by automated means |

**Response timeline:** Within 30 days of verified request. Extension of up to 60 additional days permitted for complex requests, with notification to the data subject.

**Verification:** Identity verification required before processing access, portability, or deletion requests.

**Contact:** All rights requests should be directed to **legal@ungouge.ai**.

---

## 7. Data Protection Impact Assessment (DPIA) Screening

| Criterion (per Art. 35 & WP29 Guidelines) | Applicable? | Notes |
|---|---|---|
| Systematic and extensive evaluation of personal aspects (profiling) | No | AI analysis evaluates quotes, not individuals |
| Large-scale processing of special categories | No | No special category data processed |
| Systematic monitoring of publicly accessible areas | No | Not applicable |
| New technologies | Partial | Use of generative AI for document analysis — low risk as output is informational only |
| Processing preventing data subjects from exercising a right | No | Not applicable |
| Large-scale processing | No | Small-scale service with limited user base |

**Conclusion:** A full DPIA is not currently required. This assessment will be revisited if processing activities change materially (e.g., significant increase in EU users, addition of profiling features, or processing of special category data).

---

## 8. Breach Notification Procedure

In the event of a personal data breach:

1. **Detection & Containment** — Identify scope, contain the breach, preserve evidence
2. **Risk Assessment** — Evaluate likelihood and severity of risk to data subjects' rights and freedoms
3. **Supervisory Authority Notification (Art. 33)** — If risk threshold met, notify the relevant EU/EEA supervisory authority within 72 hours of becoming aware
4. **Data Subject Notification (Art. 34)** — If high risk to individuals, notify affected data subjects without undue delay
5. **Documentation** — Record all breaches regardless of notification threshold (date, facts, effects, remedial actions)
6. **Post-Incident Review** — Conduct root cause analysis and implement preventive measures

**Breach log location:** Maintained internally by UnGouge LLC.

---

## 9. Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-02-13 | UnGouge LLC | Initial creation |

**Review frequency:** Every 6 months or upon material change to processing activities, whichever is sooner.

**Triggers for immediate review:**
- New processing activity introduced
- New sub-processor engaged
- Change in data categories collected
- Security incident or breach
- Regulatory guidance or legal change affecting processing

---

*This document is maintained by UnGouge LLC pursuant to Article 30(1) GDPR and is available to supervisory authorities upon request.*
