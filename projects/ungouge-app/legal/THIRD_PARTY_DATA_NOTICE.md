# Third-Party Data Notice — Contractor Data in User-Submitted Quotes

**Document Reference:** R-20  
**Controller:** UnGouge LLC, Vermont, USA  
**Contact:** legal@ungouge.ai  
**Date:** 2026-02-13  
**Review Date:** 2027-02-13  
**GDPR Basis:** Article 14 — Information to be provided where personal data have not been obtained from the data subject  

---

## 1. Background

UnGouge.ai is a $19.99 contractor quote analysis tool. Users upload quotes they have received from contractors (e.g., home improvement, construction, plumbing, electrical work). These quotes inherently contain personal data of the contractors, including:

- **Contractor name** (individual or business name)
- **Business address**
- **Phone number and/or email address**
- **License or registration numbers** (if included on the quote)
- **Pricing and service descriptions**

This data is provided to UnGouge by the user — not by the contractor directly. The contractor is a **third-party data subject** whose personal data UnGouge processes.

This notice documents the legal basis for processing this data, the safeguards in place, and the Article 14 analysis.

---

## 2. Legal Basis for Processing

### 2.1 Primary Basis: Legitimate Interest — Article 6(1)(f)

**Legitimate interest relied upon:** The legitimate interest of the user (who obtained the quote) in analyzing the pricing and scope of contractor quotes they received, to make informed purchasing decisions.

**Three-part test:**

#### Purpose Test
- **Interest identified:** Users have a direct, personal interest in understanding whether a contractor's quote is fairly priced. This is a consumer protection purpose.
- **Whose interest:** The user (data subject who is a party to the quote transaction), and UnGouge LLC (providing the analysis service).
- **Lawful and clearly articulated:** Yes. Analyzing commercial quotes received in the ordinary course of business/consumer transactions is a legitimate commercial activity.

#### Necessity Test
- **Is processing necessary?** Yes. The contractor's name and contact information appear on the quote and cannot be meaningfully separated from the pricing data without destroying the document's integrity and utility.
- **Could less data be used?** In theory, contractor identifying information could be redacted before analysis. However:
  - Users submit raw quote documents (PDFs, images) — automated redaction would be unreliable
  - The AI analysis needs to distinguish between multiple contractors in a comparison
  - License numbers may be relevant to verifying contractor legitimacy
  - Manual redaction would create an unreasonable burden on users and degrade the service
- **Conclusion:** Processing the contractor data as it appears on the quote is the minimum necessary for the service to function.

#### Balancing Test
- **Nature of data:** Business contact information provided in a commercial context. This is information the contractor has voluntarily placed on a commercial document intended for distribution to potential customers. **Sensitivity is low.**
- **Reasonable expectations:** When a contractor issues a quote, they reasonably expect the recipient to review, compare, and analyze that quote — including using tools to assist in evaluation. Contractors do not have a reasonable expectation that their business quotes will never be analyzed or compared.
- **Consequences for contractors:**
  - Contractor data is used **only** for price analysis within the user's session
  - Contractor data is **never shared, sold, or disclosed** to other users or third parties
  - Contractor data is **never used for marketing** or direct contact by UnGouge
  - No public-facing directory, ranking, or rating of contractors is created
  - The analysis output goes only to the user who submitted the quote
- **Vulnerable individuals:** Not applicable — contractors are business professionals acting in a commercial capacity.

**Conclusion: Legitimate interest is established.** The contractor's interest in controlling their business contact information does not override the user's legitimate interest in analyzing a commercial quote they received.

### 2.2 Alternative/Supporting Basis: User's Contractual Necessity

To the extent that the user's data processing is necessary for UnGouge to perform its contract with the user (Art. 6(1)(b)), this may provide an additional basis for processing the incidental contractor data contained in user-submitted documents. However, Art. 6(1)(b) applies to the contract with the user, not the contractor. Legitimate interest under Art. 6(1)(f) remains the primary basis for the contractor's data.

---

## 3. User Representations and Responsibilities

### 3.1 Terms of Service Requirements

Users of UnGouge.ai represent and warrant that:

1. **They obtained the quotes legitimately** — The quotes were provided to them directly by the contractor in the course of a genuine transaction or inquiry.
2. **They are authorized to submit the quotes** — They are the intended recipient of the quote, or have authorization from the recipient.
3. **They will not submit fabricated or third-party quotes** — Only quotes personally received by the user may be analyzed.
4. **They will not use the service to harass, defame, or harm contractors** — The analysis is for personal decision-making only.

### 3.2 Prohibited Uses

Users may **not** use UnGouge.ai to:
- Systematically collect or scrape contractor pricing data
- Build databases of contractor information
- Publish, share, or distribute analysis results in a way that identifies contractors
- Engage in competitive intelligence against contractors (e.g., a competing contractor analyzing rivals' quotes)
- Submit quotes obtained through deception or unauthorized means

### 3.3 Enforcement

Violation of these terms may result in account suspension and deletion of submitted data.

---

## 4. Data Processing Safeguards

### 4.1 Data Minimization

| Safeguard | Description |
|-----------|-------------|
| **Purpose limitation** | Contractor data is processed only for quote analysis — never for any secondary purpose |
| **No aggregation** | Contractor data from different users is never combined, aggregated, or cross-referenced |
| **No profiling** | No profiles of individual contractors are built |
| **No contact** | UnGouge never contacts contractors based on data in user-submitted quotes |
| **No sale** | Contractor data is never sold, licensed, or shared with third parties |
| **No indexing** | Contractor names and contact details are not indexed or made searchable |

### 4.2 Data Retention

| Data | Retention | Rationale |
|------|-----------|-----------|
| Uploaded quote documents | User-controlled — deleted upon user request or account deletion | User may need to reference past analyses |
| Analysis results | Same as uploaded documents | Tied to the user's account lifecycle |
| AI processing | Not retained by Gemini API (see DPA Register R-21 for data retention settings) | No persistent storage in AI pipeline |

### 4.3 Technical Safeguards

- Quote documents are stored encrypted at rest
- Access is scoped to the uploading user only (multi-tenant isolation)
- AI analysis passes quote content to Gemini API but does not store contractor data separately
- No full-text search indexing of contractor identifying information
- Deletion cascades: when a user deletes a quote or their account, all associated contractor data is purged

---

## 5. Article 14 Analysis — Transparency Obligations

### 5.1 The Obligation

Article 14 requires controllers to provide certain information to data subjects when personal data is not obtained directly from them. This creates a theoretical obligation to inform contractors whose data appears in user-submitted quotes.

### 5.2 Applicable Exemptions

**Article 14(5)(b) — Disproportionate Effort:**

> *"The provision of such information proves impossible or would involve a disproportionate effort, in particular for processing for archiving purposes in the public interest, scientific or historical research purposes or statistical purposes."*

UnGouge invokes this exemption on the following grounds:

1. **Identification burden:** UnGouge would need to parse every uploaded document to extract contractor contact information, verify it, and send individual notices. This is technically complex, error-prone, and disproportionate to the nature of the processing.

2. **Volume and diversity:** Quotes come in countless formats (PDFs, images, handwritten documents). Reliable automated extraction of contractor contact details is not feasible.

3. **Minimal impact:** The processing has negligible impact on contractors:
   - Their data is used only to help the quote recipient understand pricing
   - No contractor-visible action is taken based on the data
   - Data is not shared, published, or used for any purpose that could affect the contractor

4. **Risk of confusion/harm:** Contacting contractors to inform them that their quotes are being analyzed could:
   - Cause unnecessary alarm
   - Damage the user-contractor relationship
   - Be perceived as threatening or adversarial
   - Actually reveal to the contractor that the user is price-comparing (which the user may not wish to disclose)

### 5.3 Mitigating Measures (Required When Relying on Art. 14(5)(b))

When relying on the disproportionate effort exemption, the controller must take appropriate measures to protect the data subject's rights and freedoms, including making the information publicly available. UnGouge implements:

1. **Public privacy policy** — The UnGouge.ai Privacy Policy includes a section specifically addressing contractor data, explaining:
   - What contractor data is processed
   - The legal basis (legitimate interest)
   - That data is used only for quote analysis
   - That data is not shared, sold, or used for marketing
   - How contractors can exercise their rights (contact legal@ungouge.ai)

2. **Contractor rights page** — A dedicated page accessible from the Privacy Policy provides:
   - Plain-language explanation of what UnGouge does with contractor data
   - How to request information about whether their data is processed
   - How to request erasure
   - Contact: legal@ungouge.ai

3. **Erasure on request** — If a contractor contacts UnGouge requesting erasure of their data, UnGouge will:
   - Search for quotes containing the contractor's identifying information
   - Delete or redact the contractor's personal data from stored documents
   - Confirm completion to the contractor
   - This does not require deleting the user's account or analysis — only the contractor's personal data

### 5.4 Information That Would Be Provided (Art. 14(1)–(2))

For the record, and as published in our Privacy Policy, the following information applies:

| Art. 14 Requirement | Response |
|---------------------|----------|
| **(1)(a)** Identity and contact of controller | UnGouge LLC, legal@ungouge.ai |
| **(1)(b)** DPO contact | Not appointed (below threshold) |
| **(1)(c)** Purposes and legal basis | Quote analysis for the user; legitimate interest (Art. 6(1)(f)) |
| **(1)(d)** Categories of data | Name, business address, phone/email, license numbers, pricing |
| **(2)(a)** Retention period | Duration of user's account, or until erasure request |
| **(2)(b)** Legitimate interest pursued | User's interest in analyzing pricing of quotes they received |
| **(2)(c)** Right of access, rectification, erasure, restriction, objection | Available via legal@ungouge.ai |
| **(2)(d)** Right to lodge complaint with supervisory authority | Yes — with the relevant EU/EEA supervisory authority |
| **(2)(e)** Source of data | The contractor's own quote document, submitted by the quote recipient (user) |
| **(2)(f)** Automated decision-making | AI-assisted analysis is used, but no decisions with legal or significant effect on the contractor are made |

---

## 6. Contractor Rights

Despite relying on the Art. 14(5)(b) exemption for proactive notification, contractors retain all GDPR rights. If a contractor contacts UnGouge:

| Right | Response |
|-------|----------|
| **Access (Art. 15)** | Confirm whether data is processed; provide copy of data if so |
| **Rectification (Art. 16)** | Correct inaccurate data upon request |
| **Erasure (Art. 17)** | Delete/redact contractor data from stored quotes |
| **Restriction (Art. 18)** | Restrict processing while a dispute is resolved |
| **Object (Art. 21)** | Assess the objection; likely honor it given low impact of erasure on service |
| **Complaint** | Direct to relevant supervisory authority |

**Response timeline:** Within 30 days of receiving a verifiable request.

**Verification:** Contractor must provide sufficient information to identify the relevant records (e.g., their business name, approximate date of quote).

---

## 7. Record of Decision

| Item | Decision |
|------|----------|
| **Legal basis for contractor data** | Legitimate interest (Art. 6(1)(f)) |
| **Art. 14 exemption** | Disproportionate effort (Art. 14(5)(b)) |
| **Mitigating measures** | Public privacy policy, contractor rights page, erasure on request |
| **Risk to contractors** | Low — data used only for private price analysis by quote recipient |
| **Review date** | 2027-02-13 |

---

## 8. Review

This notice is reviewed:
- **Annually** (next: 2027-02-13)
- **Upon expansion** to new markets (particularly EU) where Art. 14 obligations may be enforced more stringently
- **Upon regulatory guidance** affecting the disproportionate effort exemption
- **Upon material change** to how contractor data is processed (e.g., if aggregation or comparison features are introduced)

---

*This document is maintained as part of UnGouge LLC's GDPR compliance documentation suite.*
