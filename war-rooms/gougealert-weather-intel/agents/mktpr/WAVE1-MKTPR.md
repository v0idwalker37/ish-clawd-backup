# WAVE 1 — MKT/PR System Design (GougeAlert Weather Intel)

**Owner:** MKT/PR  
**TEMPO:** CRAFT  
**Scope:** Event-triggered pages + paid search + PR + anti-spam controls + conversion telemetry

---

## 0) Ignorance Declaration (S3)

### KNOWN
- Live NWS alerts are ingestible; noise filtering is mandatory (Wave 0 result).
- Product model is a **30-day Project Pass** (same project + same address).
- Legal boundary: no insurance-adjuster behavior, no causation claims, no defamation.
- Multi-event, multi-region operation is required.
- PII shielding is non-negotiable.

### UNKNOWN
- Exact conversion baselines by channel (SEO vs paid vs PR referral).
- Which event classes have strongest pass-purchase intent by region.
- Final legal copy constraints for paid ads/headlines by jurisdiction.
- Operational bandwidth for manual approvals during high-velocity event windows.

### ASSUMPTIONS
- Event qualification scoring will be available to marketing systems as a structured field.
- County-level targeting is operationally viable and legally safer than hyperlocal address-level targeting.
- Early phase can tolerate partial manual review to reduce reputational risk.

---

## 1) Via Negativa (A1) — What to remove before adding

1. Remove generic, always-on “storm fear” messaging pages (high legal/reputation risk).
2. Remove one-page-per-city auto-generation as default (SEO cannibalization + thin content risk).
3. Remove auto-launch paid spend without human sign-off in MVP (cost/risk control).

---

## 2) Event + Location Promo Page Strategy

## Page architecture (3-layer model)

1. **Event Hub Page (canonical cluster root)**
   - Purpose: single source of truth for one qualified event cluster in one geography.
   - Includes: timeline, affected service area, pricing promo eligibility, legal-safe context, CTA to Project Pass.

2. **Location Detail Page (optional child page only for high-population areas)**
   - Purpose: localized intent capture (city/neighborhood keywords).
   - Must canonicalize to Event Hub unless it contains materially unique content.

3. **Evergreen Location Page (non-event baseline)**
   - Purpose: always-on SEO asset for city/county, receives canonical once event is sunset.

## Content template (legal-safe)
- “Recent severe weather **may increase quote variability** in this area.”
- “GougeAlert compares contractor quote line items and market ranges; it does **not** determine insurance coverage or damage cause.”
- CTA blocks:
  - “Start 30-Day Project Pass — compare multiple quotes for one project.”
  - “Upload your first quote in under 3 minutes.”

## Example URL patterns
- Event hub (canonical):  
  `/weather-events/{yyyy}/{event-class}/{state}/{county-fips}/{event-cluster-id}/`
- Optional city child page:  
  `/weather-events/{yyyy}/{event-class}/{state}/{city}/{event-cluster-id}/`
- Evergreen location page:  
  `/locations/{state}/{city}/quote-protection/`
- Archive recap page:  
  `/weather-events/archive/{yyyy}/{state}/{event-cluster-id}/`

---

## 3) Multi-Event Page Generation + Canonicalization

## Generation rules
- Generate pages only when:
  - event_qualification_score >= threshold (recommended 70/100),
  - confidence >= medium,
  - freshness window <= 72h from alert issue/major update,
  - event class in allowed list (hail, severe wind, tornado, flood, wildfire, hurricane, severe thunderstorm).

## Multi-event conflict handling
- If multiple events hit same county in overlap window:
  - Create one **county event stack page** with cards per event.
  - Canonical event page = most severe + most recent qualified cluster.
  - Secondary events remain indexable only if materially different hazard class/timeline.

## Canonicalization policy
- Canonical key: `(event_cluster_id, county_fips)`.
- City pages default `rel=canonical` to county page.
- Near-duplicate pages (>80% same body) auto noindex or canonical collapse.
- After sunset window, canonical from event page to evergreen location page.

---

## 4) Google Paid Search “Blast” Framework by Geography

> Framework design only. **Activation requires explicit spend approval.**

## Trigger tiers
- **Tier 1 (Local Blast):** single-county/dma severe event, score high, 24–96h window.
- **Tier 2 (Regional Blast):** 3+ counties or cross-DMA event cluster.
- **Tier 3 (National Signal):** major named storm/wildfire/flood with broad press interest.

## Campaign structure
- Account labels: `event_class`, `severity_band`, `geo_tier`, `event_cluster_id`.
- Campaign split:
  - Search | Brand-protected event intent
  - Search | Non-brand high-intent quote terms
  - Search | Competitor-defensive (optional, later phase)

## Naming convention examples
- Campaign: `GA_US_VT_BURLINGTON_T1_HAIL_20260303_EC4821`
- Ad group: `AG_EXACT_ROOF_QUOTE_COMPARE_MONTPELIER`
- Keyword set tag: `KW_INTENT_POSTSTORM_QUOTES`
- Creative set: `CR_V3_LEGALSAFE_PASS499`

## Geo framework
- Primary: county + DMA targeting.
- Secondary: radius overlays around impacted metro cores.
- Exclusions: unaffected counties, low-confidence zones.

## Spend guardrails (MVP)
- Hard daily caps by tier.
- Auto-pause when:
  - CPA > threshold for 24h,
  - legal gate fails,
  - event status downgraded/expired.

---

## 5) PR Outreach Workflow (Local + National)

## Two-lane PR model
1. **Local newsroom lane** (immediate utility)
   - Targets: local TV meteorologists, local papers, local radio, county FB community admins.
   - Angle: “How homeowners can avoid rushed quote mistakes after [event].”
   - Asset: city/county-specific quick facts + legal-safe checklist.

2. **National lane** (pattern narrative)
   - Targets: consumer finance desks, home/real-estate reporters, weather-business desks.
   - Angle: “Post-event quote volatility trend data, regionalized but anonymized.”
   - Asset: monthly trend brief + event snapshots.

## Workflow steps
1. Event qualifies and legal-safe brief auto-drafted.
2. PR packet generated (headline options, 3 data bullets, expert quote, disclaimer).
3. Human review + approve.
4. Distribution:
   - T+0: local first,
   - T+12h: national if event scale qualifies,
   - T+48h: one follow-up with new data only.
5. Log pickup and referral tags back to analytics.

## Outreach frequency caps
- Max 1 initial + 1 follow-up per reporter per event.
- Cooldown: no same reporter pitch >2 times per 14 days unless inbound response.
- Suppress list for non-responsive contacts after 3 ignored event cycles.

---

## 6) Frequency Controls + Sunset Policy (No Spam)

## Frequency controls
- **Page creation cap:** max 1 canonical page per `(event_cluster_id, county_fips)`.
- **Page update cadence:** max 2 meaningful updates/day unless severity escalation.
- **Paid ad refresh:** max 1 copy refresh/24h per ad group.
- **PR touches:** max 2 touches per contact per event cycle.

## Sunset lifecycle
1. **Active:** event live + 0–7 days.
2. **Decay:** 8–30 days (reduced prominence, no aggressive CTA copy).
3. **Archive:** >30 days (no paid support; page becomes recap/educational).
4. **Canonical handoff:** event page canonical to evergreen location page at archive transition.

---

## 7) Conversion Instrumentation + KPI System

## Required tracking dimensions
- `event_cluster_id`
- `event_class`
- `severity_band`
- `geo_id` (county_fips/dma/state)
- `channel` (organic, paid_search, pr_referral, direct)
- `campaign_id`, `ad_group_id`, `creative_id`
- `landing_page_type` (event_hub, city_child, evergreen)
- `pass_price_offer` (4.99 promo / 9.99 standard)

## Core funnel events
1. Page view (qualified event page)
2. CTA click to pass checkout
3. Checkout start
4. Pass purchase complete
5. First quote upload
6. Second quote upload within 30 days (retention quality proxy)

## KPI stack
- **North-star:** Project Pass purchase rate from qualified event sessions.
- **Efficiency:** Cost per pass (paid), PR referral CPA, blended CAC.
- **Quality:** % purchasers uploading 2+ quotes within pass window.
- **Risk:** % assets blocked by legal gate; complaint rate; unsubscribe/negative feedback rate.
- **SEO health:** indexed page-to-conversion ratio; cannibalization incidents/month.

---

## 8) Proposed Decisions (S1 opposite test included)

[D101] MKT/PR — Use one canonical event page per `(event_cluster_id, county_fips)` as the default publishing unit.  
**Opposite:** publish city-first pages as canonical.  
**Steel-man:** city pages can match intent more tightly.  
**Why this:** county canonical dramatically lowers duplicate risk and operational noise while preserving city capture via child pages.  
**Type:** SAFE

[D102] MKT/PR — Allow city child pages only when population/intent threshold is met; otherwise canonical to county.  
**Opposite:** create child pages for every city.  
**Steel-man:** maximal SEO footprint.  
**Why this:** footprint without unique value becomes thin/spammy and increases legal review load.  
**Type:** SAFE

[D103] MKT/PR — Gate page generation behind qualification score and freshness window.  
**Opposite:** generate pages for all alerts.  
**Steel-man:** captures long-tail edge cases.  
**Why this:** avoids reputational damage from irrelevant pages and aligns with no-spam rule.  
**Type:** SAFE

[D104] MKT/PR — Keep paid search blast launch human-approved in MVP.  
**Opposite:** fully automate ad launch.  
**Steel-man:** speed advantage during fast events.  
**Why this:** legal/cost downside of false positives is larger than speed benefit early on.  
**Type:** SAFE

[D105] MKT/PR — Segment paid campaigns by geo tier (local/regional/national) with hard spend caps and auto-pause triggers.  
**Opposite:** one national campaign per event class.  
**Steel-man:** simpler operations.  
**Why this:** geography-specific intent and costs vary too much; tiering improves control and attribution.  
**Type:** SAFE

[D106] MKT/PR — Run PR in two lanes (local utility first, national pattern second).  
**Opposite:** national-only outreach.  
**Steel-man:** larger reach with less list management.  
**Why this:** local relevance drives faster trust and better near-term conversion; national is amplification, not substitute.  
**Type:** SAFE

[D107] MKT/PR — Enforce explicit outreach caps and cooldowns across paid/PR/page updates.  
**Opposite:** optimize purely for velocity during event windows.  
**Steel-man:** first mover can capture attention.  
**Why this:** spam penalties and brand damage outlive short-term gains.  
**Type:** SAFE

[D108] MKT/PR — Apply 3-phase sunset (Active/Decay/Archive) with canonical handoff to evergreen pages.  
**Opposite:** keep event pages indefinitely as standalone indexed assets.  
**Steel-man:** potential residual SEO traffic.  
**Why this:** handoff preserves SEO equity while preventing stale-event clutter and cannibalization.  
**Type:** SAFE

[D109] MKT/PR — Standardize campaign and page metadata around `event_cluster_id` for cross-channel attribution.  
**Opposite:** channel-specific IDs only.  
**Steel-man:** easier per-tool setup.  
**Why this:** without shared IDs, impact attribution and optimization loop break.  
**Type:** SAFE

[D110] MKT/PR — Primary success metric is pass purchase rate from qualified-event sessions, not traffic volume.  
**Opposite:** optimize for sessions/impressions.  
**Steel-man:** easier top-funnel growth reporting.  
**Why this:** revenue and customer utility depend on conversion + quote upload behavior, not vanity traffic.  
**Type:** SAFE

---

## 9) Pre-Mortem (A4)

How this fails in production:
1. **False-positive event pages** create “storm-chasing spam” reputation.
2. **SEO cannibalization** from duplicate event/location permutations collapses rankings.
3. **Paid burst overspend** on low-intent geos during noisy alert periods.
4. **PR fatigue** from repetitive outreach causes journalist suppression.
5. **Attribution gaps** make channel ROI unknowable, so budget shifts become guesswork.
6. **Legal drift** in ad/page copy introduces liability language under urgency.

Early warning signals:
- Rising legal-gate rejection rate.
- High bounce + low CTA on event pages.
- CPA spikes with no lift in first/second quote uploads.
- Increasing “not relevant” feedback from PR contacts.

---

## 10) Plan-B Options (A2)

1. **Plan B for noisy automation:** move to semi-manual publishing queue for all Tier-2/3 events.  
   - Switch cost: low-medium (workflow + staffing, no major replatform).

2. **Plan B for poor paid economics:** pause paid blast; shift budget to PR + organic event hubs + retargeting only.  
   - Switch cost: low (campaign pause + creative reuse).

3. **Plan B for SEO duplication issues:** collapse city child pages into one county stack page + FAQ modules.  
   - Switch cost: medium (redirect/canonical remap).

4. **Plan B for low conversion despite traffic:** reframe CTA around “upload first quote free preview” before pass upsell.  
   - Switch cost: medium-high (product/checkout flow changes).

5. **Plan B for legal bottleneck:** pre-approved copy library by event class/severity to reduce review latency.  
   - Switch cost: low (template engineering + legal sign-off batch).

---

## 11) Immediate Implementation Backlog (MKT/PR slice)

1. Build event page template set (hub + child + evergreen handoff blocks).
2. Implement canonical key logic + duplicate-content detector.
3. Define campaign naming + UTM schema with required IDs.
4. Build tiered paid blast checklist (human-approval gate included).
5. Build PR packet generator template and media-list segmentation.
6. Implement frequency guardrail rules in scheduler/orchestrator.
7. Wire analytics events through pass purchase + quote upload milestones.
8. Create weekly dashboard: conversion, legal rejections, cannibalization incidents.
