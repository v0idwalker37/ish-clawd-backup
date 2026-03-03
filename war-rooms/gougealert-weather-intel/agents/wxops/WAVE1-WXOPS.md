# WAVE 1 — WXOPS: Event Detection + Qualification System (National Multi-Event)

TEMPO: CRAFT

## 0) KNOWN / UNKNOWN / ASSUMPTIONS (S3)

### KNOWN
- NWS `/alerts/active` is live and parseable; Wave 0 pulled 352 active alerts successfully.
- Raw feed contains noise (marine/admin/test advisories).
- ORCH decisions already require: multi-event architecture, explicit qualification layer, legal gate before outbound artifacts, strict PII shielding.
- Product needs weather relevance for quote context, not insurance-adjuster behavior.

### UNKNOWN
- Exact campaign geotarget granularity that MKT/PR will run first (county-only vs ZIP-level).
- Final legal language constraints for “event in area” phrasing at publish time.
- Tolerance for automation in MVP (fully auto-activate vs human-in-loop for borderline events).
- Source uptime/latency stats in production across all required providers.

### ASSUMPTIONS
- MVP should optimize precision over recall (miss some events > spam false events).
- County FIPS is the stable national join key; ZIP/metro are derived targeting layers.
- NWS/NOAA stays primary source of truth for weather hazard state changes.
- Event lifecycle drives downstream page/comms lifecycle directly.

---

## 1) Source Priority Stack (national, multi-source)

## Primary policy
Use a **tiered trust model**: highest-authority weather issuer defines hazard truth; lower tiers corroborate, enrich, or trigger human review only.

### Tier 0 — Authoritative Trigger Sources (can create/close events)
1. **NWS/NOAA CAP Alerts** (`api.weather.gov/alerts`) — warnings/watches/statements/advisories.
2. **NHC products** (via NOAA/NWS for tropical systems) — hurricane/tropical hazard continuity.
3. **SPC severe convective products** (outlooks/watch data) — early risk staging before warning spikes.

### Tier 1 — Government Corroboration / Impact Confirmation (cannot alone create weather event in MVP)
4. **FEMA declarations / IPAWS signals** — impact and escalation corroboration.
5. **State emergency management feeds** (if normalized) — local confirmation and granularity.

### Tier 2 — Enrichment only
6. Radar/satellite/public nowcast layers, utility outage aggregates, trusted local EM posts.

### Source resolution rules
- If Tier 0 conflicts with lower tiers, **Tier 0 wins**.
- Tier 1/2 can **raise confidence score** but not override Tier 0 hazard type/severity.
- Unknown source schema/version changes trigger `SOURCE_DEGRADED` flag and force human review.

---

## 2) Qualification Scoring Rubric + Thresholds

Score range: **0–100**. Event enters external automation only after passing threshold and controls.

## Rubric dimensions
- **Hazard Relevance (0–30):** hail, tornado, damaging wind, flood, wildfire, hurricane/tropical, severe thunderstorm receive high base values; marine/admin/test near zero.
- **Severity/Urgency/Certainty Composite (0–25):** mapped from source fields.
- **Geo Impact Weight (0–15):** affected county count, housing density proxy, metro overlap.
- **Freshness (0–10):** recency + not-near-expiration.
- **Multi-Source Corroboration (0–10):** Tier 1/2 confirmations.
- **Persistence/Update Signal (0–5):** repeated updates/extensions imply durable incident.
- **Data Quality Confidence (0–5):** parse integrity, geo confidence, dedup confidence.

### Thresholds (MVP)
- **0–39**: Reject (`SUPPRESSED_LOW_SIGNAL`)
- **40–59**: Monitor internally (`CANDIDATE`), no external actions
- **60–74**: Qualified but **human approval required** for promo/PR triggers
- **75–100**: Auto-activate event context (still behind LEGAL gate for outbound copy)

### Hard gates (override score)
- `event == Test Message` or administrative/test classes => immediate suppress.
- Marine-only/nav-only hazards => suppress unless explicitly whitelisted later.
- Geo confidence < 0.65 => hold for review.
- Expired or stale beyond hazard TTL => suppress/expire.

---

## 3) Event Object Schema + Dedup Strategy

## Canonical event object (proposed)
```json
{
  "event_id": "evt_<ulid>",
  "event_key": "hash(hazard_family|geo_cluster_id|time_bucket)",
  "hazard_family": "hail|tornado|wind|flood|wildfire|hurricane|winter|other",
  "hazard_type": "Severe Thunderstorm Warning",
  "status": "RAW|CANDIDATE|QUALIFIED|ACTIVE|DECAYING|EXPIRED|SUPPRESSED|ARCHIVED",
  "score": 0,
  "score_breakdown": {
    "relevance": 0,
    "severity_urgency_certainty": 0,
    "geo_impact": 0,
    "freshness": 0,
    "corroboration": 0,
    "persistence": 0,
    "data_quality": 0
  },
  "source_priority": "T0|T1|T2",
  "source_records": [
    {
      "provider": "NWS",
      "external_id": "https://api.weather.gov/alerts/...",
      "sent_at": "ISO-8601",
      "effective_at": "ISO-8601",
      "expires_at": "ISO-8601",
      "severity": "Severe",
      "urgency": "Immediate",
      "certainty": "Observed",
      "raw_event": "Severe Thunderstorm Warning",
      "area_desc": "..."
    }
  ],
  "geo": {
    "county_fips": ["50023"],
    "state_codes": ["VT"],
    "zip5": ["05602", "05673"],
    "cbsa": ["XXXX"],
    "geo_confidence": 0.0,
    "geometry_ref": "s3://.../evt_x.geojson"
  },
  "timing": {
    "detected_at": "ISO-8601",
    "qualified_at": "ISO-8601",
    "activated_at": "ISO-8601",
    "last_seen_at": "ISO-8601",
    "fresh_until": "ISO-8601",
    "expire_at": "ISO-8601"
  },
  "lifecycle": {
    "version": 1,
    "state_reason": "threshold_passed|manual_override|expired|source_cancelled",
    "manual_override": "NONE|FORCE_ON|FORCE_OFF|FORCE_SCORE",
    "parent_event_id": null
  },
  "dedup": {
    "cluster_id": "clu_<id>",
    "duplicate_of": null,
    "overlap_score": 0.0,
    "dedup_confidence": 0.0
  }
}
```

## Dedup strategy
1. **Provider-native chain first:** use source IDs + update/cancel relationships when available.
2. **Spatiotemporal clustering second:** same hazard_family + overlap of impacted county sets >= 60% + time overlap within 6h window => same cluster.
3. **Event key canonicalization:** deterministic hash of hazard family + geo cluster + time bucket (e.g., 3h).
4. **Split rule:** if overlap drops below 30% after update, split into child event(s).
5. **Merge rule:** if two candidates converge >80% overlap and same family, merge with oldest `event_id` retained.

---

## 4) Geo Normalization (County/ZIP/Metro)

## Normalization pipeline
1. Parse source area descriptors + polygons + UGC where present.
2. Normalize to **county FIPS** as canonical geography.
3. Expand county FIPS to ZIP5 using maintained crosswalk table.
4. Map county FIPS to CBSA/metro for campaign grouping and PR regional labeling.

### Data model rules
- **Canonical key:** county FIPS.
- ZIP is derivative and may be many-to-many; store confidence weight per ZIP if ambiguous.
- Metro assignment uses OMB CBSA mapping; non-metro counties remain county-only.

### Confidence policy
- County confidence >= 0.85 required for auto-activation.
- ZIP-level targeting only when ZIP confidence >= 0.70.
- If confidence is low: publish/trigger at county or state level only (never over-precise).

---

## 5) Freshness, Expiration, Lifecycle States

## Lifecycle states
`RAW -> NORMALIZED -> CANDIDATE -> QUALIFIED -> ACTIVE -> DECAYING -> EXPIRED -> ARCHIVED`

Side states: `SUPPRESSED` (false positive/noise), `OVERRIDDEN` (human force-on/off).

## State transition rules (core)
- `CANDIDATE -> QUALIFIED`: score >= 60 and hard gates pass.
- `QUALIFIED -> ACTIVE`: score >= 75 OR human approves.
- `ACTIVE -> DECAYING`: no reinforcing updates for hazard-specific idle window.
- `DECAYING -> EXPIRED`: source expiry passed + grace window elapsed.
- Any state -> `SUPPRESSED`: test/admin/noise classification or operator force-off.

## Freshness and TTL defaults (initial)
- Tornado/severe thunderstorm warnings: fresh 0–2h; hard expire by source + 1h grace.
- Flood/wildfire: fresh 0–12h; decay to 24–48h depending updates.
- Hurricane/tropical: fresh 0–24h; decay 72h with updates.

(Exact TTLs should be config-driven per hazard family.)

---

## 6) False-Positive Controls + Human Override Points

## False-positive controls
- **Denylist classes:** test/admin/marine-only by default.
- **Minimum score + hard gate combo:** no single weak signal triggers activation.
- **Source quorum for borderline events:** 60–74 score requires human review and/or corroboration.
- **Flap guard:** cooldown (e.g., 30 min) before reactivating a recently expired/suppressed event.
- **Anomaly checks:** sudden huge geo expansion without matching severity update flags for manual review.
- **Schema drift detector:** if critical source fields disappear/change, automatic downgrade to human-in-loop mode.

## Human override points
1. Force activate event (`FORCE_ON`) when local signal is real but score underestimates.
2. Force suppress (`FORCE_OFF`) when event is technically valid but commercially irrelevant/risky.
3. Force score adjustment (`FORCE_SCORE`) with required reason code.
4. Merge/split override for ambiguous multi-cell storms.
5. Geo scope override (county-only fallback if ZIP precision questionable).

All overrides must write immutable audit entries: actor, timestamp, reason, affected downstream artifacts.

---

## 7) Proposed Decisions (WXOPS)

[D101] WXOPS — County FIPS is the canonical geography key; ZIP/metro are derived layers.  
Opposite: ZIP-first canonical model.  
Steel-man opposite: ZIP aligns to ad platforms directly.  
Why this: FIPS is stable and source-aligned; ZIP is volatile and ambiguous.

[D102] WXOPS — Tiered source trust model (T0 trigger, T1 corroborate, T2 enrich).  
Opposite: equal-weight multi-source voting.  
Steel-man opposite: diversified source resilience.  
Why this: equal voting amplifies noisy feeds; authority hierarchy reduces legal/relevance risk.

[D103] WXOPS — Qualification score gate with 4 bands (reject/monitor/review/auto).  
Opposite: binary trigger/no-trigger.  
Steel-man opposite: simpler implementation.  
Why this: graded thresholds enable national scale without all-or-nothing noise.

[D104] WXOPS — Borderline events (60–74) require human approval for outward automation.  
Opposite: fully automatic all qualified events.  
Steel-man opposite: faster reaction time.  
Why this: MVP precision and trust > speed; reduces embarrassing false promos.

[D105] WXOPS — Dedup uses provider chain + spatiotemporal overlap clustering.  
Opposite: provider ID only dedup.  
Steel-man opposite: less compute and fewer merge mistakes.  
Why this: cross-source incident convergence requires spatial logic for multi-event reality.

[D106] WXOPS — Event lifecycle is explicit state machine with decay and archive states.  
Opposite: stateless “latest alert only” model.  
Steel-man opposite: minimal storage and logic.  
Why this: downstream page/campaign orchestration needs deterministic state transitions.

[D107] WXOPS — Hard suppress rules (test/admin/marine-only) override score.  
Opposite: trust score alone for all event classes.  
Steel-man opposite: one unified algorithmic path.  
Why this: known-noise classes should be blocked deterministically.

[D108] WXOPS — Confidence-gated geo precision: low confidence falls back to county/state targeting.  
Opposite: always target most granular ZIP inferred.  
Steel-man opposite: better local relevance potential.  
Why this: false locality hurts credibility and can create legal/messaging risk.

[D109] WXOPS — Every manual override requires reason code + immutable audit log.  
Opposite: lightweight override toggles without strict logging.  
Steel-man opposite: lower operator friction.  
Why this: auditability protects trust, debugging, and legal posture.

[D110] WXOPS — Config-driven hazard TTLs and thresholds (not hardcoded constants).  
Opposite: hardcoded defaults in pipeline.  
Steel-man opposite: fastest MVP ship.  
Why this: regional variability and tuning needs make runtime config essential.

---

## 8) Pre-Mortem (A4)

### Most embarrassing failure modes
1. **Spam burst:** dozens of irrelevant promo pages from advisory noise.  
2. **Wrong geography:** marketing claims storm relevance in the wrong county/ZIP.  
3. **Event duplication:** same storm creates multiple competing pages/campaigns.  
4. **Stale event persistence:** expired event continues driving outreach.  
5. **Feed drift blindness:** schema/source change silently degrades qualification quality.

### Mitigations
- Hard denylist + threshold bands + human review band.
- Canonical county-first normalization with confidence floors.
- Deterministic dedup cluster IDs and merge/split rules.
- Lifecycle sweeper job + strict expiry grace windows.
- Source health monitor + auto-fallback to review-only mode.

---

## 9) Plan B Options (A2)

### Plan B1 — Source outage / degraded authoritative feed
- Fallback to last-known active events + Tier 1 corroboration only.
- Freeze new auto-activations; route all candidates to human queue.
- **Switch cost:** Low/Medium (feature flag + queue volume increase).

### Plan B2 — Dedup instability in severe outbreak days
- Temporarily enforce coarse dedup at county+hazard family only.
- Disable aggressive split/merge until storm wave passes.
- **Switch cost:** Medium (higher manual cleanup, lower duplicate risk).

### Plan B3 — ZIP mapping confidence too weak nationally
- Run county/metro-only targeting for MVP.
- Enable ZIP targeting per-state after validation.
- **Switch cost:** Low (reduced granularity, improved precision).

### Plan B4 — Score tuning too noisy
- Increase auto threshold from 75 to 85 and widen human review band.
- **Switch cost:** Low (fewer auto events, slower scale).

---

## 10) Via Negativa (A1): 3 Things to Remove Before Adding More

1. Remove non-weather/admin/test classes from ingestion output early.
2. Remove ZIP-level automation where geo confidence is below threshold.
3. Remove auto-publish rights for borderline score band until error rate is proven.

---

## 11) Minimal Cron / Check Cadence Proposal

MVP cadence (single region to national-ready):

- **Every 2 min:** Poll Tier 0 feeds (NWS/NOAA primary endpoints).
- **Every 5 min:** Run normalization + dedup + score recompute for open clusters.
- **Every 5 min:** Lifecycle sweeper (decay/expire transitions).
- **Every 10 min:** Poll Tier 1 corroboration sources (FEMA/state EM where integrated).
- **Every 15 min:** Human review digest for `60–74` queue + anomalies.
- **Hourly:** Source schema/health diagnostics and precision/recall telemetry snapshot.
- **Daily (off-peak):** Rebuild county↔ZIP↔CBSA mapping checks and drift report.

If queue spikes or major outbreak detected: temporarily tighten to 1-min Tier 0 polling and 3-min recompute loop.

---

## 12) Implementation Notes for Downstream Teams

- LEGAL should define allowed event-language templates keyed by lifecycle state.
- MKT/PR should bind page creation only to `ACTIVE` and sunset to `EXPIRED`+grace.
- ARCH should persist raw source payloads for forensic replay and score tuning.
- CHAOS should attack threshold calibration using historical false-positive simulation.

This design prioritizes **high signal, explicit state, and auditable control** so GougeAlert can operate nationally without turning into an alert spam cannon.
