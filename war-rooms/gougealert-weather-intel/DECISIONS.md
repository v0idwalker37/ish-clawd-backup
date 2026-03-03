# DECISIONS

*Append-only log. Format: [D###] OWNER — decision — rationale*
*Only the domain owner writes their decisions. Others can CHALLENGE via comms/*

---

[D001] ORCH — Primary initiative is weather-intelligence-driven product motion — User explicitly set this as the platform's primary effort.
[D002] ORCH — Monetization model shifts to 30-day Project Pass per same project + same address — Reduces friction and supports iterative quote uploads.
[D003] ORCH — Satellite imagery usage is limited to measurement/context (roof/gutter/etc), not damage determination — Avoid insurance liability and confusion.
[D004] ORCH — Every customer-facing artifact requires legal gate before release — Prevents defamation/legal-risk regressions at scale.
[D005] ORCH — Multi-event architecture is required (parallel regional incidents, separate promo assets per event+location) — National operations need concurrency by design.
[D006] ORCH — Preserve strict PII shielding in all public outputs and workflows — Non-negotiable user requirement.
[D007] ORCH — Weather feed ingestion is viable; relevance filtering is the critical challenge — Live NWS test succeeded but included high noise and non-relevant advisories.
[D008] ORCH — Build an explicit Event Qualification Layer before any page/PR/campaign automation — Prevents spammy or legally risky false positives.
[D009] MKTPR — Canonical event publishing unit is `(event_cluster_id, county_fips)` with optional city child pages — Reduces SEO duplication and operational/legal noise.
[D010] MKTPR — Event page generation is gated by qualification score + freshness window — Prevents irrelevant or spammy event pages.
[D011] MKTPR — Paid search blast is human-approved in MVP with tiered spend caps/auto-pause — Controls legal and cost risk during early operation.
[D012] MKTPR — PR model uses local-first then national amplification with strict contact frequency caps — Maximizes relevance while enforcing no-spam rule.
[D013] MKTPR — Event pages follow Active/Decay/Archive lifecycle and canonical handoff to evergreen location pages — Preserves SEO equity and limits stale content clutter.
[D014] MKTPR — North-star KPI is pass purchase from qualified-event sessions (not traffic volume) — Aligns optimization with revenue and customer value.
[D015] WXOPS — County FIPS is canonical geo key with ZIP/CBSA derived by confidence rules — Improves national consistency and lowers false-localization risk.
[D016] WXOPS — Use tiered source trust (T0 authoritative trigger, T1 corroboration, T2 enrichment) — Prevents noisy sources from triggering outward automation.
[D017] WXOPS — Qualification score bands: reject/monitor/review/auto with human review for 60–74 — Optimizes MVP precision over recall.
[D018] WXOPS — Apply deterministic hard suppress rules for test/admin/marine-only classes — Eliminates known noise before downstream systems.
[D019] WXOPS — Implement explicit event lifecycle state machine (RAW→...→ARCHIVED) with decay/expiry transitions — Required for reliable page/campaign orchestration.
[D020] WXOPS — Dedup strategy combines provider chains with spatiotemporal overlap clustering — Reduces duplicate event artifacts during severe outbreak periods.
[D021] WXOPS — Manual override actions require immutable audit logging with reason codes — Supports legal defensibility and debugging.
[D022] WXOPS — TTLs/thresholds remain config-driven per hazard family (not hardcoded) — Enables tuning without code redeploy.
[D023] GEOIMG — GEO outputs restricted to measurement-context classes only: roof area, pitch proxy, gutter LF, complexity markers — Keeps imagery scope outside insurance/damage determination.
[D024] GEOIMG — All GEO metrics require confidence labels + uncertainty ranges with suppression below threshold — Prevents false precision and overclaim risk.
[D025] GEOIMG — Use deterministic imagery quality confidence model (`C_base` + metric-specific confidence) before publishing values — Enables auditable, tunable safety controls.
[D026] GEOIMG — Hard-ban damage/causation/insurance/legal-claim language in GEO/UI layer — Enforces liability boundary and messaging consistency.
[D027] GEOIMG — Apply deterministic fallback ladder for stale/cloudy/low-res imagery, including context-lite and suppression modes — Avoids fail-open behavior under poor data quality.
[D028] GEOIMG — Require stratified ground-truth validation (n>=300) before broad rollout claims — Ensures confidence tiers correlate with real error.
[D029] GEOIMG — Maintain manual-review lane for high-value or low-confidence cases — Adds operational optionality and trust protection.
[D030] LEGAL — Deterministic hard-block compliance gate is mandatory before publishing any report/page/PR/ad artifact — Scales legal consistency and prevents high-risk copy leaks.
[D031] LEGAL — Insurance-adjuster conduct language, imagery causation claims, defamation language, legal-advice framing, and public PII exposure are zero-tolerance blocks — Enforces explicit liability boundaries.
[D032] LEGAL — Output-type-specific disclaimers with placement validation are required; missing disclaimer = reject — Prevents ambiguous legal posture in channel variants.
[D033] LEGAL — Review decisions use PASS / PASS_WITH_EDIT / ESCALATE / REJECT with mandatory escalation triggers for named accusations/legal-rights language — Routes high-risk edge cases to human/legal review.
[D034] LEGAL — Compliance logs are append-only with content hashes, policy versions, and override reason codes; retain >=24 months — Preserves defensibility and forensic traceability.
[D035] LEGAL — Incident campaigns must include geo/frequency/spend controls and global kill-switch — Limits runaway reputational/legal risk during high-velocity events.
[D036] LEGAL — Enforce range/confidence phrasing and ban certainty/guarantee claims in outward copy — Reduces misrepresentation risk.
[D037] LEGAL — Policy packs and adversarial compliance regression tests are versioned CI artifacts — Prevents drift-based compliance regressions.
[D038] ARCH — Core control plane uses explicit `event_run` state machine with idempotent action execution — Prevents concurrency chaos and enables deterministic rollback.
[D039] ARCH — Project Pass entitlement key is customer + normalized address + project scope — Enforces same-project same-address 30-day rule correctly.
[D040] ARCH — Legal gate is centralized service with versioned policy packs and PASS/FAIL/REVIEW contract at multiple insertion points — Improves consistency, auditability, and fail-closed behavior.
[D041] ARCH — Pass engine remains independent from weather event engine and joins via analytics/context hooks — Preserves product utility outside disasters and reduces coupling risk.
[D042] ARCH — Global and per-event kill-switches plus publish rollback (N/N-1) are mandatory before broad public automation — Limits blast radius during incidents.
[D043] CHAOS — For MVP, public automation is constrained to prevent regulatory/trust failure: no broad auto page/ad generation until precision + compliance thresholds are proven.
[D044] CHAOS — GEO numeric outputs below high-confidence tier are suppressed in MVP to reduce false-authority risk.
[D045] CHAOS — Publish path must be single-gateway API with signed compliance token; deny-by-default for all side channels.
[D046] CHAOS — Anti-abuse controls for 30-day pass (device/velocity/risk/identity checks) are required before national scaling.
[D047] CHAOS — Crisis ethics mode (utility-first, low-sales posture in first 24–48h) is required for event marketing.
