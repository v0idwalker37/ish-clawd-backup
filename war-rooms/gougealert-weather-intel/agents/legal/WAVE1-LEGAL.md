# WAVE 1 — LEGAL COMPLIANCE GATE (GougeAlert)
TEMPO: CRAFT
OWNER: LEGAL
DATE: 2026-03-03

## 0) Ignorance Declaration (S3)

### KNOWN
- Product must avoid insurance-adjuster behavior and legal-advice framing.
- Satellite/weather inputs are allowed for **context/measurement only**, not property damage causation claims.
- Public outputs include reports, promo pages, PR copy, and ad copy.
- PII protection in public outputs is non-negotiable.
- Prior war-room decisions already require deterministic legal gating before release.

### UNKNOWN
- Final jurisdiction footprint (single-state vs national), which can alter ad/disclaimer language specifics.
- Whether public artifacts will ever name contractors/businesses directly.
- Exact ad channels (Google Search, Meta, display, local PR wires) and character limits.
- Whether a licensed attorney/compliance officer is designated for escalations.

### ASSUMPTIONS
- This gate is a **product-policy gate**, not a substitute for formal legal counsel.
- Outputs are generated/assisted by AI and pass through deterministic rule checks.
- Incident marketing is event-driven from vetted weather events (via qualification layer).

---

## 1) Hard-Block Terms / Rules (Deterministic)

If any BLOCK rule hits, output status = `REJECTED` and cannot publish.

## 1.1 Block Category A — Insurance-Adjuster / Claims Handling Conduct
**Rule:** Block any text implying GougeAlert determines loss value, negotiates claims, or acts as insured representative.

**Hard-block patterns (examples):**
- "We estimate your insured loss"
- "We determine claim value"
- "We negotiate with your insurer"
- "We are your adjuster"
- "Guaranteed claim payout"
- "We file/appeal your insurance claim"
- "Actual cash value / replacement cost estimate by GougeAlert"

## 1.2 Block Category B — Damage Causation from Imagery/Data
**Rule:** Block any statement that imagery/weather data proves or determines property damage causation.

**Hard-block patterns (examples):**
- "Satellite confirms your roof was damaged"
- "Imagery proves hail caused your leak"
- "Our model determined storm-caused structural damage"
- "This image is legal proof of contractor liability"

## 1.3 Block Category C — Defamation / Accusatory Language
**Rule:** Block allegations of criminal/fraudulent conduct by identifiable people/businesses unless sourced to official public findings and legal-reviewed.

**Hard-block patterns (examples):**
- "Contractor X is a scam/fraud/criminal"
- "Company Y is price gouging" (as factual accusation)
- "They are stealing from homeowners"

## 1.4 Block Category D — Legal Advice Framing
**Rule:** Block instructions framed as legal advice.

**Hard-block patterns (examples):**
- "You should sue"
- "You are legally entitled to X"
- "This report proves your legal case"
- "Use this to force settlement"

## 1.5 Block Category E — Public PII Exposure
**Rule:** Block publication of direct identifiers in public outputs.

**Hard-block data classes:**
- Full name + street address combination
- Phone, email, full postal address
- Exact lat/long of private residence
- Quote documents containing owner identifiers
- Claim numbers/policy numbers/account IDs

## 1.6 Rule Priority
1. PII Block
2. Adjuster Block
3. Causation Block
4. Defamation Block
5. Legal Advice Block

Any single block hit overrides all lower-priority checks.

---

## 2) Required Disclaimers by Output Type

Disclaimers are mandatory. Missing disclaimer = auto-reject.

## 2.1 Customer-Facing Reports (long form)
**Must include (top + footer):**
1. "This report is informational and not legal, insurance, engineering, or public-adjusting advice."
2. "Weather and imagery data are contextual indicators and do not determine property damage causation."
3. "Consult licensed professionals (e.g., inspector, engineer, attorney, insurance representative) for formal determinations."

## 2.2 Promo Pages (event landing pages)
**Must include (above CTA footer):**
1. "GougeAlert provides quote-comparison intelligence, not insurance claim adjustment services."
2. "Event and imagery references are context only; they are not property damage determinations."
3. "No legal advice is provided."

## 2.3 PR Copy / Press Materials
**Must include (boilerplate or notes to editor):**
1. "GougeAlert publishes market-context and quote-comparison tools; it does not provide legal services or claims-adjusting representation."
2. "Statements about weather events are based on public data and do not attribute causation for any specific property damage."

## 2.4 Ad Copy (short form)
**Must include short disclaimer variant in ad extension/landing page:**
- "Info only. Not legal/adjusting advice."
- "Weather data = context, not damage determination."

---

## 3) Allowed vs Forbidden Claim Templates

## 3.1 Allowed Templates (safe defaults)
- "Severe weather alerts were issued in [REGION] during [DATE RANGE]."
- "Use GougeAlert to compare contractor quotes with local event context."
- "Weather and imagery inputs provide context for planning questions."
- "This tool helps organize quote data and identify pricing outliers."
- "Results are estimates/ranges with confidence labels, not determinations."

## 3.2 Forbidden Templates (auto-block)
- "Your property was damaged by [EVENT]."
- "This contractor committed fraud/price gouging."
- "Our satellite analysis proves storm damage."
- "You should file/sue/appeal using this report."
- "Guaranteed savings/claim outcome/settlement."

## 3.3 Rewrites (deterministic remediation)
- Forbidden: "Your roof was damaged by last night’s hail."
  - Rewrite: "A hail alert was active near your area last night; obtain licensed inspection for damage determination."
- Forbidden: "Contractor X is gouging homeowners."
  - Rewrite: "Some quotes may vary significantly; compare multiple bids and request line-item detail."

---

## 4) Review Flow (Auto + Escalation)

## 4.1 Pipeline
1. **Draft Generation** → artifact metadata attached (`artifact_type`, `event_id`, `geo_scope`, `intended_channel`).
2. **Rule Scanner** (regex + phrase lists) → hard blocks/warnings.
3. **Semantic Classifier** → detects implied adjuster behavior, legal advice, causation, defamation tone.
4. **PII Detector + Redactor** → NER + pattern scan for identifiers.
5. **Disclaimer Validator** → checks required disclaimer presence by output type.
6. **Risk Score + Decision Engine** → `PASS / PASS_WITH_EDIT / ESCALATE / REJECT`.

## 4.2 Decision Logic
- `REJECT` if any hard-block hit.
- `ESCALATE` if no hard-block but medium/high semantic risk or named third party accusations.
- `PASS_WITH_EDIT` if only non-critical style issues + automated rewrites available.
- `PASS` only when no block, no unresolved warning, and disclaimers validated.

## 4.3 Mandatory Escalation Triggers
- Mentions specific contractor/person with negative allegations.
- Mentions legal rights/remedies.
- Mentions causation near certainty language ("proved", "confirmed", "caused").
- High-volume campaign launch tied to active disaster events.
- Any manual override request after block.

## 4.4 Human Review Roles
- **Compliance Reviewer (Tier 1):** approves escalated non-defamation copy.
- **Legal Counsel/Designate (Tier 2):** required for defamation-adjacent, legal-rights, or crisis PR text.

---

## 5) Audit Log Requirements

All public-facing artifacts must produce immutable audit records.

## 5.1 Required Fields
- `artifact_id`, `artifact_type`, `version`
- `created_at`, `reviewed_at`, `published_at`
- `generator_model`, `prompt_hash`, `policy_pack_version`, `rule_set_version`
- `event_ids`, `geo_scope`, `channel`
- `risk_flags[]`, `blocked_terms[]`, `pii_findings[]`
- `disclaimer_check = pass/fail`
- `decision = PASS/PASS_WITH_EDIT/ESCALATE/REJECT`
- `reviewer_id` (human if escalated)
- `override_used` + rationale
- `content_hash_before` / `content_hash_after`

## 5.2 Retention + Integrity
- Retain logs and artifact snapshots minimum 24 months.
- Append-only storage; no silent mutation.
- Any override requires explicit user identity + reason code.
- Weekly export checksum to detect tampering.

## 5.3 Privacy in Logs
- Log PII findings as token classes, not raw values (e.g., `EMAIL_DETECTED`, not actual email).
- Do not store full original quote documents in public artifact logs.

---

## 6) Incident Marketing Risk Controls

## 6.1 Eligibility Controls
- Campaign activation only for qualified events (severity + geography + freshness threshold).
- Suppress non-home-repair event types (marine/test/admin).
- Timebox campaigns (start/end) with auto-sunset.

## 6.2 Content Controls
- No fear-based imperative claims ("Act now before insurers deny you").
- No guaranteed outcomes.
- No named-contractor accusations.
- No implied property-specific damage without inspection language.

## 6.3 Operational Controls
- Geo-fencing: county/ZIP boundaries must match event polygon confidence.
- Frequency caps: max impressions/contact cadence per user/session.
- Spend guardrails: default daily caps + automatic pause on elevated complaint rate.
- Crisis mode kill-switch: immediate pause for all event-triggered ads/pages.

## 6.4 Reputation Controls
- Publish transparent methodology page (what data does and does not mean).
- Fast correction workflow for inaccurate event context.
- Complaint triage SLA with legal/compliance visibility.

---

## 7) Proposed Decisions (Legal Domain) [Dx]

[D-L01] Establish deterministic hard-block gate before publish for all public artifacts.
- OPPOSITE: Rely on best-effort manual review.
- STEEL-MAN: Manual review can interpret nuance better than rules.
- WHY THIS: Scale + consistency require deterministic first pass; humans handle edge cases.

[D-L02] Treat adjuster-like claims handling language as zero-tolerance blocks.
- OPPOSITE: Allow soft claims-assistance wording for conversion.
- STEEL-MAN: Could increase click-through and sales.
- WHY THIS: Regulatory/liability exposure outweighs short-term conversion gains.

[D-L03] Ban causation assertions from weather/imagery outputs.
- OPPOSITE: Permit probabilistic causation statements.
- STEEL-MAN: Users want direct answers.
- WHY THIS: Keeps product in contextual-intelligence lane and away from adjudication risk.

[D-L04] Require output-type-specific disclaimers with placement rules.
- OPPOSITE: Single global disclaimer page.
- STEEL-MAN: Less copy clutter.
- WHY THIS: Channel-specific proximity reduces legal ambiguity and platform risk.

[D-L05] Enforce public PII zero-exposure in all generated marketing/report outputs.
- OPPOSITE: Permit partial identifiers for personalization.
- STEEL-MAN: Personalization can improve trust and conversion.
- WHY THIS: Privacy and safety requirements are explicit non-negotiables.

[D-L06] Add defamation-safe rewrite layer for accusatory language.
- OPPOSITE: Let marketing manually tone-edit.
- STEEL-MAN: Human tone control is more natural.
- WHY THIS: Automated rewrite catches obvious risk before human queue overload.

[D-L07] Require escalation for named-party allegations or legal-rights language.
- OPPOSITE: Auto-pass if confidence score low.
- STEEL-MAN: Reduces operational latency.
- WHY THIS: False negatives here are catastrophic; human review is mandatory.

[D-L08] Adopt immutable, append-only compliance audit logs with hashes.
- OPPOSITE: Store only final published copy.
- STEEL-MAN: Lower storage/ops cost.
- WHY THIS: Defensibility requires traceability of edits, overrides, and policy versions.

[D-L09] Incident campaigns must have auto-sunset + kill-switch controls.
- OPPOSITE: Manual lifecycle control only.
- STEEL-MAN: Humans better understand context.
- WHY THIS: Automation limits runaway risk during high-volume event windows.

[D-L10] Prohibit legal-advice framing and include explicit "not legal advice" language.
- OPPOSITE: Omit to avoid conversion friction.
- STEEL-MAN: Fewer disclaimers may increase action.
- WHY THIS: Clear boundary is essential to avoid unauthorized-practice perception.

[D-L11] Use range/confidence phrasing; ban certainty language in risk/value claims.
- OPPOSITE: Use assertive certainty copy for persuasion.
- STEEL-MAN: Strong claims improve CTR.
- WHY THIS: Over-certainty increases misrepresentation and complaint risk.

[D-L12] Require policy-pack versioning and periodic red-team regression tests.
- OPPOSITE: One-time policy setup.
- STEEL-MAN: Faster launch.
- WHY THIS: Language drift and model drift create compliance regression over time.

---

## 8) Red-Team Abuse Cases + Mitigations

1. **Abuse:** Prompt injection to force "prove damage" language.
   - **Mitigation:** Post-generation hard-block scan + causation classifier + reject.

2. **Abuse:** Marketing inserts competitor names with accusations.
   - **Mitigation:** Named-entity + defamation lexicon block + mandatory escalation.

3. **Abuse:** User-uploaded files leak owner name/address into page copy.
   - **Mitigation:** PII redaction layer before template fill; public-output sanitizer.

4. **Abuse:** Ad copy uses legal threat language for urgency.
   - **Mitigation:** Legal-advice phrase blocklist + channel preflight.

5. **Abuse:** "Guaranteed savings" claims in paid ads.
   - **Mitigation:** Guarantee language hard-block + replacement templates.

6. **Abuse:** Crisis event exploited with fear messaging.
   - **Mitigation:** Incident mode restrictions, sentiment guardrails, compliance approval gate.

7. **Abuse:** Manual override repeatedly used to bypass blocks.
   - **Mitigation:** Override quota alerts, two-person approval for repeated overrides.

8. **Abuse:** Model drift starts producing borderline adjuster phrasing.
   - **Mitigation:** Weekly adversarial test suite + automatic policy-pack update queue.

---

## 9) Pre-Mortem (A4)

### Most embarrassing failure scenario
A storm hits. Automated pages/ads launch with implied property-specific damage claims, include identifiable homeowner data, and accuse local contractors of gouging. Complaints and takedowns spike, trust collapses, and platform accounts are suspended.

### Failure chain
1. Event qualification passes noisy signals.
2. Generated copy includes aggressive causal/accusatory wording.
3. Missing disclaimer in one channel variant.
4. No escalation because threshold tuned too lenient.
5. High-volume launch amplifies issue quickly.

### Preventive controls
- Strict hard-block + mandatory disclaimers.
- Conservative escalation thresholds for launch phase.
- Channel-level preflight tests before bulk publish.
- Kill-switch tied to complaint/takedown/error metrics.

---

## 10) Plan-B Options (A2)

### Plan B1 — Manual-first release mode (first 30 days)
- **Use when:** false positives or policy drift exceed tolerance.
- **Action:** Auto-generation allowed, but all public outputs require human approval.
- **Switch cost:** Moderate (review staffing + slower publish cadence).

### Plan B2 — Reports-only mode, marketing pause
- **Use when:** ad/PR risk too high during active incidents.
- **Action:** Continue private reports with strict disclaimers; suspend promo/ads/PR automation.
- **Switch cost:** Low-to-moderate (reduced growth, lower legal exposure).

### Plan B3 — Context-only language lock
- **Use when:** repeated causation/defamation near-misses.
- **Action:** Force templates to approved neutral language library only.
- **Switch cost:** Low (less persuasive copy, highest safety).

---

## 11) Via Negativa (A1) — Remove Before Add
1. Remove all certainty words ("prove", "confirm", "guarantee") from default copy library.
2. Remove named-contractor mentions from any automated generation path.
3. Remove direct personalization tokens that can leak PII into public pages.

These removals reduce liability faster than adding more complex downstream controls.

---

## 12) Implementation Notes (for ARCH/MKT handoff)
- Build policy packs by channel: `report`, `promo`, `pr`, `ad`.
- Keep blocklists + allowlists versioned and testable in CI.
- Add compliance regression suite with adversarial prompts.
- Require publish API to attach `compliance_token` proving gate pass.

END OF WAVE1 LEGAL SPEC
