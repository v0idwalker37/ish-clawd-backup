# WAVE 1B — CHAOS ATTACK MEMO
**Project:** GougeAlert Weather Intelligence Engine  
**Role:** CHAOS (devil’s advocate)  
**Date:** 2026-03-03

I’m attacking this as if I’m a regulator, a platform trust/safety reviewer, a journalist, a hostile competitor, and a fraud ring at the same time.

---

## Top 3 Project Killers (and what to do first)

### 1) **Regulatory reclassification as unlicensed adjuster/legal advisor**
Why it kills: disclaimers won’t save conduct. If workflow/output materially influences claims posture or legal action, states can treat this as regulated activity.

**Do first (this week):**
1. Create a **state-by-state prohibited-conduct matrix** (adjusting + UPL + consumer-protection triggers).
2. Encode it into product behavior gates (not just text linting).
3. Require human legal sign-off before any “claims-facing” copy/channel launch.

### 2) **Search/ads trust collapse from event-page over-generation and disaster opportunism optics**
Why it kills: one manual action or ad account suspension during a major event can zero out acquisition overnight.

**Do first (this week):**
1. Freeze city-level auto page generation; start county-only canonical with strict caps.
2. Enforce single “event dossier” per cluster and noindex near-duplicates by default.
3. Launch with paid-search manual approvals only + crisis kill switch tested in staging.

### 3) **30-day pass fraud/abuse (address replay, reseller abuse, chargebacks)**
Why it kills: low ticket + event spikes = easy target for card testers and pass-sharing rings; can erase margin and poison trust metrics.

**Do first (this week):**
1. Add anti-abuse controls (device fingerprint, velocity limits, payment risk scoring, pass binding checks).
2. Define “same project + same address” with strict normalization + proof-of-control signals.
3. Add fraud playbook: auto-hold, manual review queue, refund/chargeback SOP.

---

## Challenge Register

### [C-001] Disclaimers are being treated as liability armor (they are not)
- **Targets:** D004, D-L01, D-L02, D-L10
- **Attack:** You can still be regulated by what the system *does* (decision support that mimics claims handling), even if copy says “info only.”
- **Verdict:** **KILLED**
- **Mitigation / Reversal:** Reframe legal gate from phrase filter to **conduct gate**: ban features/workflows that rank claim outcomes, advise disputes, or represent insured interests.

### [C-002] “No causation claims” is fragile under probabilistic language drift
- **Targets:** D003, D-L03, GEO D8
- **Attack:** “Likely storm-related” phrasing will creep in via templates, PR edits, or model drift; regulators/judges read implication, not literal banned phrases.
- **Verdict:** **WOUNDED**
- **Mitigation / Reversal:** Lock outbound copy to approved template IDs for MVP; prohibit free-form generative prose in public channels.

### [C-003] Defamation risk persists even without naming contractors
- **Targets:** D-L06, D-L07
- **Attack:** If geography/time window is narrow, “local gouging” language can still be “of and concerning” identifiable businesses.
- **Verdict:** **WOUNDED**
- **Mitigation / Reversal:** Ban accusatory framing entirely; use neutral variance language and require evidence standards for any misconduct references.

### [C-004] Consumer-protection (UDAP/FTC) exposure from implied evidence claims
- **Targets:** MKT D110, LEGAL allowed templates
- **Attack:** “Weather context improves quote decisions” can become deceptive if uplift is unproven or inconsistent by region.
- **Verdict:** **WOUNDED**
- **Mitigation / Reversal:** Publish substantiation standard: no performance claim unless validated with pre-registered metrics and retained evidence.

### [C-005] Imagery confidence model can create false authority at Tier B/C
- **Targets:** GEO D2, D4, D9
- **Attack:** Users/contractors will anchor on numbers regardless of caveats; moderate-confidence ranges still drive hard decisions.
- **Verdict:** **KILLED**
- **Mitigation / Reversal:** For MVP, suppress numeric outputs below Tier A for high-stakes fields; show only qualitative context + “verify on-site” workflow.

### [C-006] Geo normalization errors can trigger wrong-county messaging
- **Targets:** WXOPS D101, D108
- **Attack:** County/ZIP crosswalk ambiguity + stale boundaries = false local targeting, which looks like spam or manipulation.
- **Verdict:** **WOUNDED**
- **Mitigation / Reversal:** Add geo-confidence hard floor for any outbound action and require human review when county-to-ZIP ambiguity > threshold.

### [C-007] Event dedup logic will break during compound storms
- **Targets:** WXOPS D105, D106
- **Attack:** Merge/split errors create duplicate pages, conflicting campaign states, and contradictory messaging.
- **Verdict:** **WOUNDED**
- **Mitigation / Reversal:** In severe-event mode, downgrade to conservative dedup (county+hazard only), disable auto split/merge, and batch human reconciliation.

### [C-008] SEO architecture risks “programmatic thin content” penalties
- **Targets:** MKT D101, D102, D108
- **Attack:** Event/location permutations can still look auto-generated and low-unique-value, even with canonical tags.
- **Verdict:** **KILLED**
- **Mitigation / Reversal:** Start with one high-quality event hub per cluster, minimum unique-content threshold, and no indexation until quality checks pass.

### [C-009] PR cadence can be interpreted as disaster-chasing spam
- **Targets:** MKT D106, D107
- **Attack:** Even capped outreach can backfire if value signal is weak and timing feels exploitative.
- **Verdict:** **WOUNDED**
- **Mitigation / Reversal:** Add empathy + utility rubric before pitch release; no outreach unless you provide new, verifiable local value beyond self-promo.

### [C-010] Orchestration is too brittle for MVP blast radius
- **Targets:** D005, WXOPS/MKT/LEGAL full stack
- **Attack:** Event scoring + legal gate + SEO + ads + PR + sunset + pass logic is many coupled state machines; partial failure will publish contradictory artifacts.
- **Verdict:** **KILLED**
- **Mitigation / Reversal:** Slice MVP: weather qualification + private report context only. Delay public page/ads automation until reliability SLOs are proven.

### [C-011] Compliance-token design can be bypassed through side channels
- **Targets:** LEGAL implementation handoff
- **Attack:** One unguarded publish path (CMS manual post, ad console direct edit, PR tool integration) bypasses gate and nullifies legal architecture.
- **Verdict:** **KILLED**
- **Mitigation / Reversal:** Enforce policy at publish infrastructure layer (single publish API, signed tokens, deny by default, audit reconciliation of all outbound IDs).

### [C-012] 30-day pass definition is abuse-prone and gameable
- **Targets:** D002
- **Attack:** “Same project + same address” is ambiguous; attackers can reuse addresses, rotate cards/devices, and share outputs.
- **Verdict:** **KILLED**
- **Mitigation / Reversal:** Define strict project identity schema, bind pass to verified user/device/payment risk profile, add velocity/entropy checks and graduated friction.

### [C-013] Quote upload poisoning can manipulate outlier narratives
- **Targets:** Product core + MKT messaging
- **Attack:** Fake or selectively edited quotes can manufacture “volatility” claims and expose brand to misrepresentation accusations.
- **Verdict:** **WOUNDED**
- **Mitigation / Reversal:** Require document integrity checks, anomaly scoring, and exclude low-trust uploads from any aggregate claim generation.

### [C-014] Brand trust failure under crisis timing
- **Targets:** MKT tiered blast + PR
- **Attack:** Running acquisition-heavy campaigns right after destructive events can be framed as predatory regardless of legal cleanliness.
- **Verdict:** **WOUNDED**
- **Mitigation / Reversal:** Add crisis ethics mode: utility-first content only for first 24–48h, no hard-sell CTA, explicit community-help posture.

### [C-015] Governance gap: no named compliance owner / escalation SLA in architecture
- **Targets:** LEGAL unknowns, ops model
- **Attack:** Without accountable owner and response times, high-risk escalations stall or get waived ad hoc.
- **Verdict:** **WOUNDED**
- **Mitigation / Reversal:** Assign compliance DRI, define escalation matrix + SLA + override quorum; drill incident response before launch.

---

## Net Assessment
Current design is conceptually strong but **operationally over-ambitious and legally under-hardened for immediate national automation**. 

If you force launch as currently scoped, most likely failure sequence is:
1) false-confidence output or geo mismatch,
2) public/ad amplification,
3) complaint spike + platform/regulatory scrutiny,
4) forced rollback under reputational damage.

**CHAOS recommendation:** ship a constrained MVP (private/internal context + strict manual gates), prove compliance and precision, then progressively unlock public automation by hazard class and geography.