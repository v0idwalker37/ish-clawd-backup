# GougeAlert Weather Intelligence Blueprint (War Room Consolidation)

Date: 2026-03-03  
Scope: Weather-intelligence primary product motion with legal-safe, privacy-safe, multi-event operations.

## 1) Executive stance

Build this in phases:
1. **MVP-Guarded:** high-precision event qualification + private report context + manual legal approvals for any public artifact.
2. **Controlled Public:** canonical county event pages + constrained paid/PR with caps + kill-switches.
3. **National Scale:** multi-event automation with strict policy tokens, anti-abuse, and SLO gates.

This integrates ARCH, WXOPS, LEGAL, MKTPR, GEOIMG, and CHAOS outputs.

---

## 2) Product core

### 30-Day Project Pass
- One pass = one project + one normalized address + one customer identity.
- Valid for 30 days; supports total-only and itemized re-uploads for same project.
- Pass engine independent from weather engine; weather context can annotate pass analytics.

### Weather context policy
- Weather/satellite are **contextual inputs** for quote interpretation.
- No insurance-adjuster behavior.
- No property-damage causation claims from imagery.

---

## 3) System architecture

Pipeline:
1. Ingestion (NWS/NOAA primary)
2. Normalization + dedup
3. Qualification scoring + hard suppress filters
4. Event run orchestrator (state machine)
5. Legal gate service (multi-point)
6. Action executor (pages/campaign/pricing/comms)
7. Observability + audit + rollback

### Event run state machine
`DETECTED -> QUALIFIED -> LEGAL_PENDING -> READY -> ACTIVE -> SUNSETTING -> ARCHIVED`

Exception states: `REVOKED`, `FAILED`, `ROLLED_BACK`, `SUPPRESSED`.

### Multi-event arbitration
- Merge threshold for overlapping same-hazard events.
- One canonical page per `(event_cluster_id, county_fips)`.
- City child pages optional and canonicalized.

---

## 4) Legal and safety architecture

### Hard blocks
- adjuster/claims handling behavior
- imagery-based damage causation assertions
- defamation/accusatory language
- legal advice framing
- public PII exposure

### Gate contract
`PASS | PASS_WITH_EDIT | ESCALATE | REJECT`

### Mandatory legal insertion points
- L1 qualification output checks
- L2 report rendering
- L3 promo page rendering
- L4 outbound comms copy
- L5 final publish token validation

### Governance
- Single publish API only.
- Signed compliance token required for publish.
- Deny-by-default for side-channel publishing.

---

## 5) GEO/IMG policy

### Allowed outputs
- roof area estimate + confidence
- pitch proxy band/range + confidence
- gutter linear feet estimate + confidence
- roof complexity markers + confidence

### Forbidden outputs
- any statement that property damage exists/does not exist
- causation claims from satellite/weather data
- insurance, settlement, legal proof framing

### Confidence policy (MVP)
- High confidence: show numeric with bounded uncertainty.
- Moderate/low: range only or suppress.
- Very low: suppress metric and show “insufficient imagery quality.”

---

## 6) Marketing/PR operating model

### Content structure
- canonical county event hub
- optional city child pages (strict uniqueness threshold)
- evergreen location pages with canonical handoff after event sunset

### Paid search
- tiered by geo/event severity
- human-approved in MVP
- hard spend caps + auto-pause

### PR
- local-first utility lane
- national amplification second
- strict contact caps/cooldowns
- utility-first, no fear messaging

### Crisis ethics mode
- first 24–48h: utility-first posture, no hard-sell language.

---

## 7) Anti-abuse and trust controls

Required before national scaling:
- pass abuse controls (device, velocity, payment risk)
- upload integrity checks
- anomaly detection on quote data poisoning
- strict override logging and override quotas

---

## 8) Reliability and rollback

- idempotent action keys (`event_run_id + action_type + version`)
- retries + DLQ
- global and per-event kill switches
- artifact version rollback (N/N-1)
- audit trails with policy version hashes

---

## 9) MVP vertical slice (recommended)

Pilot scope:
- hazards: hail + severe thunderstorm
- source: NWS only
- geo: one pilot region
- outputs: report context + one canonical event page (manual legal publish)
- paid/PR: manual approval only

Go/No-Go gates:
- qualification false positive rate below threshold
- legal gate rejection reasons stable and declining
- no PII leaks in public artifacts
- kill-switch drill passes

---

## 10) What not to do (via negativa)

- no city-level mass auto-page generation at launch
- no auto paid blast launch in MVP
- no free-form generated legal/claims-adjacent copy
- no low-confidence satellite numbers in high-stakes contexts

---

## 11) Final recommendation

Proceed immediately with **MVP-Guarded** implementation. The design is strong, but CHAOS findings are valid: do not flip to broad public automation until precision/compliance/abuse controls are proven in production telemetry.
