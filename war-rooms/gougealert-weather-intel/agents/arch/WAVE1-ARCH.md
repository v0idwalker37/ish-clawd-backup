# WAVE 1 — ARCH: Target Architecture for GougeAlert Weather Intelligence

**TEMPO: CRAFT**

## 0) S3 — KNOWN / UNKNOWN / ASSUMPTIONS

### KNOWN
- GougeAlert is now a **weather-intelligence primary product effort**.
- Wave 0 proved live weather ingestion is viable; **noise filtering is the hard part**.
- Non-negotiables: legal gate on all customer/public outputs, strict PII shielding, no insurance-adjuster behavior, imagery for context only.
- Monetization anchor: **30-day Project Pass for same project + same address**.
- Multi-event concurrency is required (parallel incidents, regional campaigns).

### UNKNOWN
- Final cloud/provider commitments (GCP/Vercel/Cloudflare are likely but not fully locked).
- Exact legal policy text/versioning source of truth (internal doc repo vs DB policy store).
- Exact inbound channel mix at launch (web only vs web+API+email ingestion).
- Baseline quote volume and event burst profile in first 90 days.

### ASSUMPTIONS
- Existing Ungouge backend can host new services (or adjacent services) without rewrite.
- Postgres is available and acceptable as primary system-of-record.
- Human review is acceptable for high-risk legal gates during MVP.
- Initial event sources are NWS/NOAA-first; FEMA/news enrichment follows.

---

## 1) Via Negativa First (A1) — What to REMOVE before adding

1. **Remove fully automatic publishing** in MVP. Keep explicit legal/human release gate for public artifacts.
2. **Remove per-upload monetization logic** for same project/address; consolidate under pass entitlement service.
3. **Remove one-off campaign scripts**. Replace with event-run state machine + deterministic action executor.

---

## 2) Architecture Overview (Macro + Micro)

### Macro pattern (H1)
A single repeatable pattern drives the whole platform:

**Signal In → Qualification → Orchestration → Legal Gate → Publish/Execute → Observe → Sunset**

This same loop applies to:
- Macro: national multi-event operation
- Micro: one event in one county with one promo page

### Target component map

```text
[External Feeds]
  NWS/NOAA/FEMA/Enrichment
        |
        v
(1) Ingestion Service  ---> raw_event_store
        |
        v
(2) Normalizer + Deduper ---> canonical_event
        |
        v
(3) Qualification Engine ---> qualified_event(score, risk_tier)
        |
        v
(4) Event Orchestrator (state machine, concurrency arbitration)
        |
        +--------------------+
        |                    |
        v                    v
(5a) Legal Gate: Reports   (5b) Legal Gate: Public assets/comms
        |                    |
        +---------PASS-------+
                  |
                  v
(6) Action Executor (promo page, campaign, PR package, alerts)
                  |
                  v
(7) Observability + Audit + Rollback controls

Parallel domain:
[Quote Upload/API] -> Pass Resolver -> Project Pass Entitlement -> Report Pipeline
                                     ^
                         event context injected when relevant
```

---

## 3) Event Ingestion + Qualification Pipeline (required #1)

## 3.1 Pipeline stages

### Stage A — Ingestion (every 5 min MVP)
- Pull from `api.weather.gov/alerts/active` (MVP core).
- Persist immutable `raw_event` payload (JSON + source metadata + fetch timestamp).
- Use idempotency key: `source + source_event_id + source_updated_at`.

### Stage B — Normalize + Dedupe
- Map source payloads into canonical schema:
  - `hazard_type`, `severity`, `certainty`, `urgency`, `effective_at`, `expires_at`, `geo_shapes`, `source_refs`.
- Deduplicate across revisions:
  - Keep `canonical_event_id` stable, increment `event_revision`.
- Drop explicit non-market events and test/admin events.

### Stage C — Qualification
Scored qualification (0–100) with hard filters + weighted factors:
- Hard filters (must pass):
  - hazard in allowed set (hail/wind/tornado/wildfire/flood/hurricane/severe thunderstorm)
  - freshness window valid
  - geo confidence >= threshold
- Weighted factors:
  - severity/certainty/urgency composite
  - affected homeowner density proxy
  - recency half-life decay
  - event overlap with active runs (boost or merge)
- Output:
  - `qualified_event` with `qualification_score`, `risk_tier` (LOW/MED/HIGH), `recommended_actions`.

### Stage D — Orchestrator intake
- Only qualified events enter orchestrator queue.
- Store explainability vector for audit (why scored this way).

## 3.2 Qualification pseudocode

```python
if not allowed_hazard(event.hazard): reject("HAZARD_NOT_ALLOWED")
if event.is_test or event.is_marine_only: reject("NON_MARKET_NOISE")
if geo_confidence(event) < 0.70: reject("LOW_GEO_CONFIDENCE")

score = (
  sev_weight(event.severity) +
  certainty_weight(event.certainty) +
  urgency_weight(event.urgency) +
  density_weight(event.geo) +
  freshness_weight(event.effective_at)
)

risk_tier = tier(score)
emit_qualified_event(event_id, score, risk_tier, explainability)
```

---

## 4) Multi-Event Orchestration Model (required #2)

## 4.1 Core entity: Event Run
`event_run` = one operational campaign instance for a qualified event in a defined geo scope.

State machine:
`DETECTED -> QUALIFIED -> LEGAL_PENDING -> READY -> ACTIVE -> SUNSETTING -> ARCHIVED`

Exception states:
`REVOKED`, `ROLLED_BACK`, `FAILED`

## 4.2 Concurrency arbitration rules
When multiple events overlap:
1. Compute geo overlap (`zip/fips intersection %`).
2. If overlap > 70% and hazard family same, **merge into primary run**.
3. If overlap > 70% but hazards differ, keep both but assign one **primary customer context** by higher severity.
4. Never allow >1 active promo page per `hazard_family + geo_cluster` canonical slug.

## 4.3 Action graph per run
Each `event_run` has actions, each with independent status + retries:
- `create_promo_page`
- `update_pr_package`
- `prepare_google_blast`
- `activate_event_pricing`
- `sunset_assets`

Action executor is idempotent (`event_run_id + action_type + version`).

---

## 5) 30-Day Project Pass Data Model Integration (required #3)

## 5.1 Canonical model

### Tables
- `property_address`
  - `id`, `normalized_address`, `geocode_lat`, `geocode_lng`, `address_fingerprint`
- `project_scope`
  - `id`, `project_type` (roof, siding, gutters, etc), `scope_signature`
- `project_pass`
  - `id`, `customer_id_or_email_hash`, `property_address_id`, `project_scope_id`, `starts_at`, `ends_at`, `status`, `origin_event_run_id?`
- `quote_submission`
  - `id`, `project_pass_id?`, `property_address_id`, `project_scope_id`, `uploaded_at`, `source_channel`, `report_id`

### Entitlement rule
Attach an upload to existing pass iff:
- same `customer_id_or_email_hash`
- same `property_address_id` (normalized)
- same `project_scope_id` (or scope similarity >= threshold if configured)
- `now <= ends_at`

Else: create new pass at checkout.

## 5.2 Operational behavior
- First paid upload creates pass (`30-day TTL`).
- Subsequent uploads in window are zero-friction under pass.
- Pass can carry event context (`origin_event_run_id`) for pricing attribution/analytics only.
- Pass engine is independent of event engine (important for non-event traffic).

---

## 6) Legal Gate Insertion Points (required #4)

Legal gate must be deterministic + auditable (rule engine first, optional LLM lint second).

## 6.1 Gate locations
1. **Gate L1 — Event qualification output**
   - Blocks event classes or language profiles that imply causation liability risk.
2. **Gate L2 — Customer report rendering**
   - Enforces disclaimers and banned phrases (no damage-causation claims).
3. **Gate L3 — Promo page content**
   - Checks defamation/legal advice violations; enforces neutral framing.
4. **Gate L4 — Outbound comms (PR/email/ads/social drafts)**
   - Ensures policy-safe wording and no overreach.
5. **Gate L5 — Final publish action**
   - Hard stop if prior gate version mismatch or stale approval token.

## 6.2 Gate result contract
`PASS | FAIL | REVIEW_REQUIRED`
- `FAIL`: hard block + reason codes.
- `REVIEW_REQUIRED`: route to human legal approver queue.
- Record policy version + hash used for decision in audit table.

---

## 7) Reliability, Rollback, Observability (required #5)

## 7.1 Reliability
- At-least-once delivery with idempotent consumers.
- Retries with exponential backoff + dead-letter queues.
- Outbox pattern for state-change events from Postgres.
- All critical writes within transactional boundaries.

## 7.2 Rollback
- Global kill switch: pause publish/external actions.
- Per-event kill switch: set `event_run.status=REVOKED` => auto-unpublish assets and pause spend.
- Versioned promo page artifacts (N, N-1 rollback in <2 min).
- Billing safety: if wrongful activation occurs, auto-credit/refund path linked to `event_run_id`.

## 7.3 Observability
- OpenTelemetry traces across ingest→qualify→legal→publish.
- Core metrics:
  - `event_ingest_latency_p95`
  - `qualification_false_positive_rate`
  - `legal_gate_fail_rate_by_reason`
  - `publish_success_rate`
  - `rollback_invocation_count`
  - `pass_match_rate` / `pass_mismatch_rate`
- Dashboards:
  - Event command center
  - Legal gate health
  - Project pass economics
- SLOs (MVP):
  - 99% qualified-event decisions < 2 min from ingest
  - 99.5% legal gate response < 3 sec
  - 99% publish actions complete < 5 min post-approval

---

## 8) MVP Slice (single event) and Scale Path (required #6)

## 8.1 MVP slice — one event family, one region
Scope:
- Source: NWS only
- Hazard family: hail + severe thunderstorm
- Geo scope: one pilot state/region
- Actions: promo page + event pricing + internal alert
- Legal: deterministic rules + mandatory human review on public publish

Implementation steps (4-week slice):
1. Build ingestion/normalization/qualification services.
2. Implement `event_run` state machine + basic arbiter.
3. Implement Project Pass resolver in quote upload path.
4. Add L2/L3/L5 legal gates.
5. Add action executor for promo page + pricing toggle.
6. Add command-center dashboard (single event view).
7. Run simulated event replay tests before live.

Exit criteria:
- 3 live events processed end-to-end without manual data fixes.
- <10% false positive qualification on pilot hazard family.
- 100% public outputs carry logged legal gate approval.

## 8.2 Scale path — many concurrent events
Scale upgrades:
- Add FEMA/news enrichers and hazard families incrementally.
- Partition queues by `geo_cluster` and `hazard_family`.
- Introduce automated merge/split for overlapping event runs.
- Expand legal gates to risk-tiered auto-approve for low-risk templates.
- Add campaign budget governor and SEO canonicalization manager.
- Move from single-region to national with per-region rate limits.

Scale target:
- 50+ concurrent active `event_run`s with deterministic arbitration and <5 min action latency.

---

## 9) Proposed Decisions [Dx] (with Opposite + Plan B + Type)

### [D101] ARCH — Use canonical `event_run` state machine as control plane.
- **Opposite:** ad-hoc scripts per event/campaign.
- **Steel-man opposite:** faster initial shipping.
- **Why this:** prevents concurrency chaos and enables rollback/audit.
- **TYPE:** SAFE
- **Plan B:** keep scripts but require runbook + approval gates (switch cost: ~2 weeks refactor later).

### [D102] ARCH — Postgres as source-of-truth for events, passes, legal audits.
- **Opposite:** distributed stores from day 1.
- **Steel-man opposite:** better horizontal scale upfront.
- **Why this:** fastest path to correctness + transactional integrity.
- **TYPE:** SAFE
- **Plan B:** add event-stream backbone later (switch cost: moderate, 3–4 weeks migration).

### [D103] ARCH — Qualification as explicit scoring service before orchestration.
- **Opposite:** trigger workflows directly from ingestion.
- **Steel-man opposite:** lower latency, fewer components.
- **Why this:** Wave 0 proved relevance filtering is the core risk.
- **TYPE:** SAFE
- **Plan B:** temporary manual triage queue (switch cost: low, +ops labor).

### [D104] ARCH — Separate legal gate service with versioned policy packs.
- **Opposite:** inline legal checks scattered in each service.
- **Steel-man opposite:** less infra overhead.
- **Why this:** centralized compliance, auditability, faster policy updates.
- **TYPE:** SAFE
- **Plan B:** shared library in monolith for MVP (switch cost: medium, ~2 weeks extraction).

### [D105] ARCH — Project Pass entitlement keyed by customer + normalized address + project scope.
- **Opposite:** key only by customer/time window.
- **Steel-man opposite:** simpler UX, fewer misses.
- **Why this:** enforces same-project/same-address requirement correctly.
- **TYPE:** SAFE
- **Plan B:** allow manual support override for borderline scope matches (switch cost: low).

### [D106] ARCH — Event-action executor idempotency key on `(event_run_id, action_type, version)`.
- **Opposite:** best-effort fire-and-forget actions.
- **Steel-man opposite:** faster to implement.
- **Why this:** prevents duplicate pages/spend/notifications during retries.
- **TYPE:** SAFE
- **Plan B:** post-action dedupe cron (switch cost: low-medium, operationally messy).

### [D107] ARCH — Manual approval required for high-risk legal outputs in MVP.
- **Opposite:** full auto-publish after gates pass.
- **Steel-man opposite:** maximum speed and coverage.
- **Why this:** protects brand/legal posture while policy confidence is immature.
- **TYPE:** SAFE
- **Plan B:** risk-tiered auto-publish only for low-risk templates (switch cost: low).

### [D108] ARCH — Geo overlap arbitration with merge threshold (70%) for similar hazards.
- **Opposite:** every qualified event gets independent campaign.
- **Steel-man opposite:** full granularity preserves local nuance.
- **Why this:** avoids SEO/campaign cannibalization and conflicting messaging.
- **TYPE:** SAFE
- **Plan B:** lower threshold + canonical page linking strategy (switch cost: low).

### [D109] ARCH — Keep pass engine independent from event engine.
- **Opposite:** event-coupled pass lifecycle only.
- **Steel-man opposite:** simpler attribution and promo logic.
- **Why this:** product remains useful in non-disaster flow; lower coupling risk.
- **TYPE:** SAFE
- **Plan B:** soft-couple via analytics join tables only (switch cost: minimal).

### [D110] ARCH — Add kill-switch and reversible publish (N/N-1) before nationwide scale.
- **Opposite:** rely on manual rollback steps.
- **Steel-man opposite:** avoids extra engineering now.
- **Why this:** catastrophic mistakes will happen; rollback must be mechanized.
- **TYPE:** RADICAL (operational rigor early)
- **Plan B:** scripted rollback runbook with pager escalation (switch cost: low-medium).

---

## 10) Pre-Mortem (A4): How this fails in production

1. **False positive storm** publishes irrelevant promos.
   - Mitigation: stricter qualification thresholds + human review + automatic revoke path.
2. **Legal drift** (policy changed but old templates still publish).
   - Mitigation: policy version pinning at publish time; fail closed on mismatch.
3. **Multi-event overlap confusion** causes duplicate campaigns and SEO self-competition.
   - Mitigation: overlap arbiter + canonical slug rules + single-primary page rule.
4. **Pass misbinding** charges users again for same project/address.
   - Mitigation: address normalization tests, entitlement simulation suite, support override tooling.
5. **Rollback too slow** during public mistake.
   - Mitigation: one-click event revoke + cached artifact invalidation + pre-tested rollback drills.

---

## 11) Plan-B Options (cross-cutting)

- **Plan-B Infra:** If event volume exceeds Postgres queue tolerance, introduce Pub/Sub/Kafka while keeping Postgres system-of-record.
- **Plan-B Legal:** If deterministic rules produce high false blocks, add second-stage LLM lint + human triage queue.
- **Plan-B Pass Matching:** If strict scope matching rejects valid repeats, enable fuzzy scope matcher with confidence bands + manual confirmation UX.
- **Plan-B Operations:** If 24/7 manual review is unsustainable, enable risk-tiered auto-publish only for pre-approved low-risk templates.

---

## 12) Immediate Build Backlog (implementation-ready)

1. Create DB migrations for `raw_event`, `canonical_event`, `qualified_event`, `event_run`, `legal_gate_log`, `project_pass`.
2. Implement ingestion worker with immutable raw payload storage and idempotency.
3. Implement qualification service with explainability output.
4. Implement event-run orchestrator + overlap arbiter.
5. Implement pass resolver middleware on quote upload endpoint.
6. Implement legal gate service (rule engine + reason codes + policy versioning).
7. Implement action executor for promo page + pricing toggle + revoke.
8. Instrument traces/metrics and create command-center dashboard.
9. Add replay harness using historical NWS events for regression testing.
10. Run game day: false-positive inject + rollback drill + legal gate failure drill.

---

## Final architectural stance
This design optimizes for **correctness under legal and reputational risk first**, then scales to high concurrency through a stable event-run control plane. It keeps the monetization core (30-day same project/same address pass) independent but context-aware, so GougeAlert can win both during and outside weather surges.