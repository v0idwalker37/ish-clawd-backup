# Data Processing Agreement (DPA) Register

**Document Reference:** R-21  
**Controller:** UnGouge LLC, Vermont, USA  
**Contact:** legal@ungouge.ai  
**Date:** 2026-02-13  
**Review Date:** 2027-02-13  
**GDPR Basis:** Article 28 — Processor Obligations; Article 30 — Records of Processing Activities  

---

## 1. Purpose

This register documents all sub-processors engaged by UnGouge LLC, their processing activities, and the status of Data Processing Agreements required under Article 28 GDPR. It serves as part of UnGouge's records of processing activities (Art. 30) and demonstrates compliance with processor management obligations.

---

## 2. Sub-Processor Register

### 2.1 Google Cloud Platform (GCP)

| Field | Detail |
|-------|--------|
| **Processor** | Google LLC |
| **Registered Address** | 1600 Amphitheatre Parkway, Mountain View, CA 94043, USA |
| **Role** | Sub-processor (infrastructure hosting) |
| **Services Used** | Cloud Run, Cloud SQL (MySQL), Cloud Storage, Cloud Logging, Secret Manager, IAM, Cloud Monitoring |
| **Processing Purpose** | Hosting the UnGouge application, storing and processing user data, providing compute infrastructure for the service |
| **Data Categories Processed** | All categories: user accounts (names, emails, hashed passwords), uploaded contractor quotes, analysis results, security logs (IP addresses, timestamps), application configuration |
| **Data Subject Categories** | Registered users, contractors (named in quotes), website visitors (IP addresses in logs) |
| **Processing Location** | US (us-central1 primary, us-east1 for DR) |
| **Transfer Mechanism** | N/A for US-to-US; for EU data subjects: Google's Standard Contractual Clauses (SCCs) incorporated in their DPA |
| **Sub-processor's Sub-processors** | Google maintains a published list: https://cloud.google.com/terms/subprocessors |

#### DPA Status

| Item | Status |
|------|--------|
| **DPA executed?** | ✅ Yes — Google Cloud Data Processing Addendum |
| **DPA location** | https://cloud.google.com/terms/data-processing-addendum |
| **Acceptance method** | Accepted via Google Cloud Console (automatic with ToS) |
| **Date accepted** | *[Record date of GCP account creation / ToS acceptance]* |
| **SCC included?** | ✅ Yes — incorporated by reference in Google's DPA |
| **EU adequacy / transfer mechanism** | EU-US Data Privacy Framework (Google LLC is certified); SCCs as fallback |
| **Audit rights** | Per Section 7.5 of Google's DPA — via ISO 27001/SOC 2 audit reports (Google provides third-party audit reports in lieu of direct audit) |
| **Breach notification** | Google will notify "promptly and without undue delay" per DPA Section 7.3 |
| **Data deletion on termination** | Per DPA — data deleted upon contract termination, subject to applicable retention obligations |

#### Key Configuration Notes

| Setting | Value | GDPR Relevance |
|---------|-------|---------------|
| Data location restriction | us-central1 / us-east1 | Data residency control |
| Encryption at rest | Google-managed keys (default) | Art. 32 security |
| Encryption in transit | TLS 1.2+ enforced | Art. 32 security |
| Access logging | Cloud Audit Logs enabled | Art. 30 accountability |
| VPC Service Controls | *[Enabled/To be configured]* | Network-level data protection |

---

### 2.2 Google Gemini API (AI Processing)

| Field | Detail |
|-------|--------|
| **Processor** | Google LLC |
| **Registered Address** | 1600 Amphitheatre Parkway, Mountain View, CA 94043, USA |
| **Role** | Sub-processor (AI analysis) |
| **Services Used** | Gemini API (via Vertex AI or AI Studio) |
| **Processing Purpose** | Analyzing contractor quotes submitted by users — extracting pricing data, comparing against market rates, generating analysis reports |
| **Data Categories Processed** | Content of contractor quotes (contractor names, addresses, pricing, service descriptions), user prompts/queries |
| **Data Subject Categories** | Contractors (named in quotes), registered users (analysis queries) |
| **Processing Location** | US (Google Cloud infrastructure) |
| **Transfer Mechanism** | Same as GCP — Google's SCCs for EU data subjects |

#### DPA Status

| Item | Status |
|------|--------|
| **DPA executed?** | ✅ Yes — covered by Google Cloud Data Processing Addendum (same as GCP) |
| **DPA location** | https://cloud.google.com/terms/data-processing-addendum |
| **Date accepted** | *[Same as GCP account]* |
| **Specific terms** | Google Cloud AI/ML terms: https://cloud.google.com/terms/service-terms (Section for Generative AI) |

#### Critical: Data Retention and Model Training

| Setting | Value | Status | Notes |
|---------|-------|--------|-------|
| **Model training opt-out** | ✅ Opted out | **CRITICAL** | Gemini API via Google Cloud (Vertex AI) does NOT use customer data for model training by default. Verify via: https://cloud.google.com/vertex-ai/generative-ai/docs/data-governance |
| **Input data retention** | Not retained beyond request processing | ✅ Confirmed | Per Google Cloud's Generative AI data governance: prompts and responses are not stored by Google for API customers on Vertex AI |
| **Output data retention** | Not retained beyond request processing | ✅ Confirmed | Same as above |
| **Logging** | Cloud Logging integration available (under our control) | ✅ | We control logging; logs subject to our retention policies |
| **Human review** | Disabled for paid API (no human review of prompts/responses) | ✅ Confirmed | Per Vertex AI terms |

> ⚠️ **IMPORTANT DISTINCTION:** The data governance for Gemini API depends on the access method:
> - **Vertex AI (Google Cloud):** Customer data is NOT used for model training, NOT retained, NOT reviewed. ✅ **This is our configuration.**
> - **Google AI Studio (free tier/consumer):** Different terms apply — data MAY be used for improvement. ❌ **NOT used by UnGouge.**
>
> **Action:** Ensure all Gemini API calls route through Vertex AI, not AI Studio.

#### Verification Checklist

- [ ] Confirm Vertex AI is the API endpoint (not AI Studio)
- [ ] Review Google's Generative AI data governance page quarterly
- [ ] Monitor for changes to Google's AI terms of service
- [ ] Maintain documentation of opt-out/data governance configuration

---

### 2.3 Stripe (Payment Processing)

| Field | Detail |
|-------|--------|
| **Processor** | Stripe, Inc. |
| **Registered Address** | 354 Oyster Point Blvd, South San Francisco, CA 94080, USA |
| **Role** | Sub-processor (payment processing) |
| **Services Used** | Stripe Payments, Stripe Checkout *(planned)* |
| **Processing Purpose** | Processing $19.99 per-use payments from users; managing payment methods; handling refunds and disputes |
| **Data Categories Processed** | User name, email, payment card details (PAN, expiry, CVC — handled entirely by Stripe), billing address, transaction history, payment status |
| **Data Subject Categories** | Registered users who make purchases |
| **Processing Location** | US (Stripe infrastructure); Stripe may process in multiple jurisdictions per their sub-processor list |
| **Transfer Mechanism** | Stripe's SCCs for EU data subjects; EU-US Data Privacy Framework (Stripe is certified) |

#### DPA Status

| Item | Status |
|------|--------|
| **DPA executed?** | ⏳ **PENDING — Execute before go-live** |
| **DPA location** | https://stripe.com/legal/dpa |
| **Acceptance method** | Execute via Stripe Dashboard or countersign |
| **Target execution date** | *Before payment processing goes live* |
| **SCC included?** | ✅ Yes — Stripe's DPA includes SCCs |
| **EU adequacy / transfer mechanism** | EU-US Data Privacy Framework; SCCs as fallback |
| **PCI DSS compliance** | ✅ Stripe is PCI DSS Level 1 certified |
| **Audit rights** | Per Stripe DPA — via third-party audit reports (SOC 2, PCI DSS) |
| **Breach notification** | Stripe will notify without undue delay per DPA terms |
| **Data deletion on termination** | Per Stripe DPA — subject to legal retention requirements (payment regulations) |

#### Pre-Go-Live Checklist

- [ ] **Execute Stripe DPA** (review and accept via Stripe Dashboard)
- [ ] Verify Stripe's current sub-processor list: https://stripe.com/legal/service-providers
- [ ] Configure Stripe to minimize data collection (only required fields)
- [ ] Implement Stripe Elements/Checkout (card data never touches our servers)
- [ ] Verify PCI compliance scope (SAQ-A if using Stripe hosted payment page)
- [ ] Update Privacy Policy with Stripe-specific data processing details
- [ ] Set up Stripe webhook security (signature verification)
- [ ] Test payment flow in Stripe test mode
- [ ] Review Stripe's data retention settings and configure as appropriate

> ⚠️ **BLOCKER:** Stripe DPA must be executed before accepting any real payments. No payment processing until this is complete.

---

## 3. Summary Matrix

| Processor | Service | DPA Status | Data Training Opt-Out | Transfer Mechanism | Last Reviewed |
|-----------|---------|------------|----------------------|-------------------|---------------|
| Google Cloud Platform | Hosting (Cloud Run, Cloud SQL, Storage) | ✅ Executed | N/A | SCCs + DPF | 2026-02-13 |
| Google Gemini API | AI quote analysis (via Vertex AI) | ✅ Executed (same DPA) | ✅ Not used for training (Vertex AI) | SCCs + DPF | 2026-02-13 |
| Stripe | Payment processing | ⏳ **Pending** | N/A | SCCs + DPF (upon execution) | 2026-02-13 |

---

## 4. Sub-Processor Management Procedures

### 4.1 New Sub-Processor Onboarding

Before engaging any new sub-processor:

1. **Data mapping** — Document what personal data will be shared, categories of data subjects, and processing purpose
2. **DPA execution** — Execute a DPA compliant with Art. 28(3) requirements before any data sharing
3. **Security assessment** — Review the processor's security certifications (SOC 2, ISO 27001, PCI DSS as applicable)
4. **Transfer assessment** — If data will be transferred outside the EU/EEA, confirm an appropriate transfer mechanism (adequacy decision, SCCs, BCRs, or DPF)
5. **Privacy Policy update** — Update the public Privacy Policy to disclose the new processor
6. **Register update** — Add the processor to this register
7. **Data subject notification** — If material change, consider whether data subjects should be informed

### 4.2 Ongoing Monitoring

| Activity | Frequency |
|----------|-----------|
| Review processor's security certifications | Annually |
| Check for changes to processor's DPA or terms | Quarterly |
| Review processor's sub-processor list for changes | Quarterly |
| Verify data processing configuration (retention, training opt-outs) | Quarterly |
| Audit processor data access logs (where available) | As needed / upon incident |
| Review this register | Annually (or upon change) |

### 4.3 Sub-Processor Change Notification

Per Google's DPA, Google will notify of new sub-processors and provide an objection mechanism. UnGouge will:
- Subscribe to Google Cloud sub-processor change notifications
- Review changes within 30 days
- Object if a new sub-processor poses unacceptable risk

Similarly, Stripe provides sub-processor change notifications via their legal page.

### 4.4 Sub-Processor Termination

When ceasing use of a sub-processor:
1. Ensure all personal data is retrieved or confirmed deleted
2. Obtain written confirmation of data deletion (or certificate of destruction)
3. Revoke all access credentials and API keys
4. Update this register and the Privacy Policy
5. Retain the DPA and deletion confirmation for audit purposes (6 years)

---

## 5. Art. 28(3) DPA Requirements Checklist

For each DPA, verify the following mandatory provisions are included:

| Requirement | Art. 28(3) ref | GCP | Gemini | Stripe |
|-------------|---------------|-----|--------|--------|
| Process only on documented instructions | (a) | ✅ | ✅ | ⏳ |
| Confidentiality obligations for personnel | (b) | ✅ | ✅ | ⏳ |
| Security measures (Art. 32) | (c) | ✅ | ✅ | ⏳ |
| Sub-processor restrictions | (d) | ✅ | ✅ | ⏳ |
| Assistance with data subject rights | (e) | ✅ | ✅ | ⏳ |
| Assistance with security obligations (Art. 32-36) | (f) | ✅ | ✅ | ⏳ |
| Data deletion/return on termination | (g) | ✅ | ✅ | ⏳ |
| Audit rights | (h) | ✅ | ✅ | ⏳ |

---

## 6. Review and Approval

| Item | Detail |
|------|--------|
| **Last reviewed** | 2026-02-13 |
| **Next review** | 2027-02-13 (or upon new processor engagement) |
| **Reviewed by** | Legal/Compliance |
| **Approved by** | UnGouge LLC |

---

## Appendix: Key Links

| Resource | URL |
|----------|-----|
| Google Cloud DPA | https://cloud.google.com/terms/data-processing-addendum |
| Google Cloud Sub-processors | https://cloud.google.com/terms/subprocessors |
| Google Vertex AI Data Governance | https://cloud.google.com/vertex-ai/generative-ai/docs/data-governance |
| Google Cloud AI/ML Service Terms | https://cloud.google.com/terms/service-terms |
| Stripe DPA | https://stripe.com/legal/dpa |
| Stripe Sub-processors | https://stripe.com/legal/service-providers |
| Stripe Security | https://stripe.com/docs/security |
| EU-US Data Privacy Framework | https://www.dataprivacyframework.gov/ |

---

*This document is maintained as part of UnGouge LLC's GDPR compliance documentation suite.*
