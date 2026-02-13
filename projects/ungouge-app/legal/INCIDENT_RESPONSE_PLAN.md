# Data Breach Incident Response Plan

**Document Reference:** R-13  
**Controller:** UnGouge LLC, Vermont, USA  
**Contact:** legal@ungouge.ai  
**Date:** 2026-02-13  
**Review Date:** 2027-02-13  
**GDPR Basis:** Articles 33–34 — Notification of a Personal Data Breach  

---

## 1. Purpose and Scope

This plan establishes procedures for detecting, responding to, and recovering from personal data breaches, as defined by Article 4(12) GDPR:

> *"A breach of security leading to the accidental or unlawful destruction, loss, alteration, unauthorised disclosure of, or access to, personal data transmitted, stored or otherwise processed."*

This plan covers all personal data processed by UnGouge LLC, including:
- User account data (names, email addresses, hashed passwords)
- Contractor quotes and related documents uploaded by users
- Payment data processed via Stripe (when active)
- Security logs (IP addresses, authentication records)
- Any data held by sub-processors (Google Cloud, Gemini API, Stripe)

---

## 2. Incident Response Team

| Role | Responsibility | Contact |
|------|---------------|---------|
| **Incident Lead** | Overall coordination, decision-making, timeline enforcement | legal@ungouge.ai |
| **Technical Lead** | Investigation, containment, forensic analysis | Engineering team |
| **Communications Lead** | Supervisory authority notifications, data subject notifications | legal@ungouge.ai |
| **External Counsel** | Legal advice on notification obligations, regulatory liaison | *Engage as needed* |

> **Note:** As a small team, roles may overlap. The key requirement is that one person owns the 72-hour notification timeline.

---

## 3. Detection and Classification

### 3.1 Detection Sources

Incidents may be detected through:
- **Automated monitoring:** Google Cloud security alerts, anomalous access patterns, error rate spikes
- **Internal discovery:** Team member identifies suspicious activity, misconfiguration, or data exposure
- **External report:** User, security researcher, or third party reports a vulnerability or breach
- **Sub-processor notification:** Google Cloud, Stripe, or other processor notifies of an incident affecting our data
- **Regulatory inquiry:** Supervisory authority contacts us regarding a potential breach

### 3.2 Severity Classification

#### 🔴 Severity 1 — Critical

**Criteria:** Confirmed unauthorized access to, exfiltration of, or destruction of personal data.

Examples:
- Database breach with access to user accounts, emails, or quotes
- Ransomware affecting production systems
- Confirmed exfiltration of contractor quote data
- Compromise of authentication system (password hashes exposed)
- Stripe payment data compromised

**Response time:** Immediate. All other work stops.  
**Notification likely required:** Yes — both supervisory authority and data subjects.

#### 🟠 Severity 2 — High

**Criteria:** Unauthorized access to systems containing personal data, but exfiltration not confirmed. Or accidental exposure of personal data.

Examples:
- Unauthorized access to Cloud SQL instance (no confirmed data access)
- API endpoint exposing another user's data (access control bug)
- Backup files accessible without authentication
- Employee credential compromise (no confirmed data access)

**Response time:** Within 1 hour of detection.  
**Notification likely required:** Supervisory authority likely; data subjects depends on risk assessment.

#### 🟡 Severity 3 — Medium

**Criteria:** Security incident that could lead to a breach if not addressed, but no confirmed unauthorized access to personal data.

Examples:
- Vulnerability discovered in production (not yet exploited)
- Phishing attempt targeting team members (not successful)
- Misconfiguration detected and corrected before exploitation
- Sub-processor reports incident that did not affect our data

**Response time:** Within 4 hours.  
**Notification likely required:** Generally not, but document the assessment.

#### 🟢 Severity 4 — Low

**Criteria:** Minor security event with no path to personal data compromise.

Examples:
- Failed brute-force attempts (blocked by rate limiting)
- Port scanning or reconnaissance activity
- Spam or non-targeted automated attacks

**Response time:** Normal business hours.  
**Notification required:** No, but log for pattern analysis.

---

## 4. Response Procedure

### Phase 1: Detection and Initial Assessment (0–1 hour)

1. **Log the incident** — Record: date/time of detection, date/time of occurrence (if known), who detected it, initial description, affected systems
2. **Classify severity** using Section 3.2
3. **Assign Incident Lead** — This person owns the response from this point
4. **Start the 72-hour clock** — Under Art. 33, the clock starts when the controller becomes "aware" of a breach. Awareness means reasonable certainty that a security incident has led to personal data being compromised. **Document the exact time.**
5. **Preserve evidence** — Do not destroy logs, do not restart affected systems before forensic capture

### Phase 2: Containment (1–4 hours)

**Immediate containment actions (as applicable):**
- Revoke compromised credentials / rotate API keys
- Isolate affected systems (network segmentation, disable endpoints)
- Block identified attacker IP addresses
- Disable compromised user accounts and force password resets
- Enable additional logging on affected systems
- Take forensic snapshots of affected instances before remediation

**Do NOT:**
- Delete logs or evidence
- Communicate externally before Legal/Communications Lead approves messaging
- Assume containment is complete without verification

### Phase 3: Investigation (1–48 hours)

Determine:
- **What data was affected?** (categories and volume)
- **How many data subjects?**
- **What was the attack vector / root cause?**
- **Is the breach ongoing or contained?**
- **What is the likely impact on data subjects?**
- **Were any sub-processors involved?**

Document all findings in the Incident Log (see Section 8).

### Phase 4: Notification (within 72 hours of awareness)

See Sections 5 and 6 for notification templates.

**Decision tree:**

```
Is it a personal data breach (Art. 4(12))?
├── No  → Document assessment. No notification required.
└── Yes → Is it likely to result in a risk to rights/freedoms?
    ├── No  → Document assessment. No supervisory authority notification.
    │         (Art. 33(1) exception: "unlikely to result in a risk")
    └── Yes → Notify supervisory authority within 72 hours (Art. 33)
              → Is it likely to result in HIGH risk to rights/freedoms?
                  ├── No  → No data subject notification required.
                  └── Yes → Notify affected data subjects without
                            undue delay (Art. 34)
```

### Phase 5: Remediation (24 hours – 2 weeks)

- Fix the root cause (patch, configuration change, code fix)
- Verify the fix in a staging environment
- Deploy to production
- Confirm no further unauthorized access
- Update security controls to prevent recurrence
- Review whether additional data subjects or categories were affected

### Phase 6: Post-Incident Review (within 2 weeks)

See Section 7.

---

## 5. Supervisory Authority Notification Template (Art. 33)

> **Timeline:** Within 72 hours of becoming aware. If notification is delayed, reasons for delay must be provided.

> **Recipient:** The lead supervisory authority of the EU/EEA member state(s) where affected data subjects reside. If unknown or multiple, notify the authority of the member state where UnGouge's EU representative is established (if appointed), or the authority most connected to the affected subjects.

---

**PERSONAL DATA BREACH NOTIFICATION**  
**Per Article 33 of Regulation (EU) 2016/679**

**1. Controller Details**

| Field | Detail |
|-------|--------|
| Controller name | UnGouge LLC |
| Address | Vermont, USA |
| Contact | legal@ungouge.ai |
| EU Representative | *[To be appointed if/when required]* |
| DPO | *Not appointed (fewer than threshold processing operations)* |

**2. Nature of the Breach**

| Field | Detail |
|-------|--------|
| Date/time breach occurred | *[YYYY-MM-DD HH:MM UTC]* |
| Date/time breach detected | *[YYYY-MM-DD HH:MM UTC]* |
| Date/time controller became aware | *[YYYY-MM-DD HH:MM UTC]* |
| Nature of breach | *[Confidentiality / Integrity / Availability]* |
| Description | *[Plain-language description of what happened]* |

**3. Data and Data Subjects Affected**

| Field | Detail |
|-------|--------|
| Categories of data subjects | *[e.g., Registered users, contractors named in quotes]* |
| Approximate number of data subjects | *[Number or estimate]* |
| Categories of personal data | *[e.g., Names, email addresses, contractor quotes]* |
| Approximate number of records | *[Number or estimate]* |

**4. Likely Consequences**

*[Description of likely consequences for data subjects, e.g., identity theft risk, financial loss, reputational damage, loss of confidentiality of commercial information]*

**5. Measures Taken**

*[Description of measures taken or proposed to address the breach, including mitigation measures for data subjects]*

**6. Reason for Delayed Notification (if applicable)**

*[If notification is made after 72 hours, explain the reasons for delay per Art. 33(1)]*

---

## 6. Data Subject Notification Template (Art. 34)

> **Timeline:** Without undue delay, when the breach is likely to result in a HIGH risk to the rights and freedoms of natural persons.

> **Language:** Clear and plain language, per Art. 34(2).

---

**Subject: Important Security Notice from UnGouge.ai**

Dear [User],

We are writing to inform you of a security incident that may affect your personal data.

**What happened:**  
*[Clear, plain-language description. Example: "On [date], we discovered that an unauthorized third party gained access to our database containing user account information. We immediately took steps to secure our systems and began an investigation."]*

**What data was involved:**  
*[Specific categories. Example: "Your name, email address, and the contractor quotes you uploaded to our platform may have been accessed. Your password was stored in a hashed format and was not exposed in plain text. No payment card information was affected."]*

**What we are doing:**  
*[Actions taken. Example: "We have secured the affected systems, engaged cybersecurity experts to investigate, and notified the relevant data protection authority. We have reset all user passwords as a precaution."]*

**What you can do:**  
*[Practical steps. Example:]*
- *Change your password on any other service where you used the same password*
- *Be alert for suspicious emails claiming to be from UnGouge.ai*
- *Monitor [relevant accounts] for unusual activity*
- *[If financial data involved: Consider placing a fraud alert on your credit file]*

**Contact us:**  
If you have questions or concerns, contact us at: **legal@ungouge.ai**

We sincerely apologize for this incident and are taking every step to prevent it from happening again.

UnGouge LLC  
legal@ungouge.ai

---

## 7. Post-Incident Review Process

Within **two weeks** of incident resolution, the Incident Lead conducts a formal review:

### 7.1 Review Agenda

1. **Timeline reconstruction** — What happened, when, and how
2. **Detection effectiveness** — How was it detected? Could we have detected it sooner?
3. **Response effectiveness** — Did the response plan work? What gaps emerged?
4. **Root cause analysis** — What was the fundamental cause? (Use 5-Whys or similar)
5. **Notification assessment** — Were notifications timely and complete?
6. **Impact assessment** — Final determination of affected data subjects and data categories

### 7.2 Review Outputs

- **Incident Report** — Permanent record filed in the breach register
- **Remediation verification** — Confirmation that root cause is fixed
- **Preventive measures** — Changes to prevent recurrence (technical, procedural, or policy)
- **Plan updates** — Changes to this Incident Response Plan based on lessons learned
- **Training needs** — Any training gaps identified

### 7.3 Breach Register

Maintain a register of all incidents (including those assessed as not requiring notification) containing:

| Field | Detail |
|-------|--------|
| Incident ID | Sequential identifier |
| Date detected | When the incident was identified |
| Date resolved | When containment/remediation was complete |
| Severity | Classification per Section 3.2 |
| Description | What happened |
| Data affected | Categories and volume |
| Subjects affected | Number and categories |
| Root cause | Determined cause |
| Notification | Whether SA/data subjects were notified, with rationale |
| Remediation | Actions taken |

> This register satisfies Art. 33(5): *"The controller shall document any personal data breaches, comprising the facts relating to the personal data breach, its effects and the remedial action taken."*

---

## 8. Incident Log Template

For each active incident, maintain a running log:

```
INCIDENT LOG
============
Incident ID:     [INC-YYYY-NNN]
Severity:        [1-Critical / 2-High / 3-Medium / 4-Low]
Status:          [Active / Contained / Resolved / Closed]
Incident Lead:   [Name]
72-hour deadline: [YYYY-MM-DD HH:MM UTC]

TIMELINE
--------
[YYYY-MM-DD HH:MM] — [Who] — [What happened / action taken]
[YYYY-MM-DD HH:MM] — [Who] — [What happened / action taken]
...

AFFECTED SYSTEMS
----------------
- [System 1]
- [System 2]

AFFECTED DATA
-------------
- Categories: [list]
- Volume: [estimate]
- Subjects: [estimate]

CONTAINMENT ACTIONS
-------------------
- [Action 1] — [Status: Done/Pending]
- [Action 2] — [Status: Done/Pending]

NOTIFICATIONS
-------------
- Supervisory authority: [Not required / Sent YYYY-MM-DD / Pending]
- Data subjects: [Not required / Sent YYYY-MM-DD / Pending]
- Sub-processors: [Notified / N/A]

ROOT CAUSE
----------
[To be determined during investigation]

REMEDIATION
-----------
- [Fix 1] — [Status]
- [Fix 2] — [Status]
```

---

## 9. Communication Guidelines

### Internal Communication
- Use only secure channels (encrypted messaging or in-person) during active incidents
- Do not discuss incident details on public Slack channels, social media, or unencrypted email
- All external communications must be approved by the Communications Lead

### External Communication
- **Supervisory authorities:** Formal notification per template (Section 5)
- **Data subjects:** Notification per template (Section 6), approved by Legal
- **Sub-processors:** Notify if they need to take action (e.g., credential rotation)
- **Media:** No comment until Legal approves a statement. Default response: "We are aware of a security matter and are investigating. We will provide updates as appropriate."
- **Law enforcement:** Engage if criminal activity is suspected, coordinating with Legal

---

## 10. Testing and Maintenance

### Tabletop Exercises
- Conduct **annually** (minimum)
- Simulate scenarios across all severity levels
- Test the 72-hour notification timeline
- Document results and update plan

### Plan Review
- **Annually** or after any Severity 1 or 2 incident
- Update contact information, sub-processor list, and procedures
- Verify notification templates are current with regulatory guidance

### Team Training
- All team members: security awareness and incident recognition
- Incident Response Team: annual walkthrough of this plan
- New team members: briefed within 30 days of joining

---

## Appendix A: Key GDPR Articles Reference

| Article | Requirement |
|---------|-------------|
| Art. 4(12) | Definition of personal data breach |
| Art. 33(1) | Notify supervisory authority within 72 hours |
| Art. 33(2) | Processor must notify controller without undue delay |
| Art. 33(3) | Content of supervisory authority notification |
| Art. 33(4) | Information may be provided in phases |
| Art. 33(5) | Obligation to document all breaches |
| Art. 34(1) | Notify data subjects when high risk |
| Art. 34(2) | Clear and plain language |
| Art. 34(3) | Exceptions to data subject notification |

---

## Appendix B: Sub-Processor Incident Contacts

| Processor | Incident Reporting |
|-----------|--------------------|
| Google Cloud Platform | Via Google Cloud Console > Support; Google's DPA requires notification without undue delay |
| Google Gemini API | Via Google Cloud support channels |
| Stripe | Via Stripe Dashboard > Support; security@stripe.com |

---

*This document is maintained as part of UnGouge LLC's GDPR compliance documentation suite.*
