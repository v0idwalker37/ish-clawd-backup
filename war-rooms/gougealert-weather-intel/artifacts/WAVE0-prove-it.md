# Wave 0 — Prove It (Mandatory)

## Riskiest Assumption
We can reliably normalize live weather alerts into usable, market-relevant event objects for automated promo/report context generation.

## 30-Minute Reality Test
Ran live fetch against NWS API:
- Endpoint: `https://api.weather.gov/alerts/active`
- Result: HTTP 200, 352 active alerts at test time.
- Parsed key fields (`event`, `severity`, `certainty`, `urgency`, `sent`, `expires`, `areaDesc`, `id`) successfully.

### Findings
1. Data is available and ingestible in real-time.
2. Feed includes **non-market-relevant noise** (marine/weather advisory types) and occasional `Test Message` events.
3. Event normalization is feasible, but relevance filtering is mandatory before downstream automation.

## Decision Impact
- The platform can run a Sentinel ingestion pipeline.
- Must add Event Qualification Layer before page/PR/promo generation.

## Minimal Qualification Criteria (Draft)
- Include only hazard classes tied to home repair quote volatility (hail, wind, tornado, wildfire, flood, hurricane, severe thunderstorm).
- Exclude marine/navigation-only events by default.
- Drop test/admin events.
- Require geo confidence + time freshness window.

## Pre-Mortem (A4)
How this fails:
- We auto-publish pages for irrelevant advisories and look spammy.
- Wrong geo mapping creates false local promos.
- Overly broad event classes trigger unnecessary campaign spend.

Mitigation:
- Qualification scoring + manual approval threshold for first phase.
- Geo boundary validation tests.
- Spend guardrails and auto-pause rules.

## Verdict
**Assumption survives (WOUNDED but viable):** ingestion is straightforward; relevance filtering is the true complexity and must be first-class in architecture.
