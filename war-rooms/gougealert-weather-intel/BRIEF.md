# War Room Brief

## Project
**GougeAlert Weather Intelligence Engine** — event-driven quote protection system that detects weather incidents, generates location-specific promo/report context, and ships legal-safe market messaging.

## Problem
Homeowners get rushed contractor quotes after severe weather events. Existing quote tools are static and miss timing/context. GougeAlert needs a real-time event layer that improves relevance without crossing into insurance-adjuster liability or defamation risk.

## Goals
1. Design production architecture for **multi-event, multi-region** weather alert operations.
2. Define **30-day Project Pass** model (same project + same address, multiple uploads).
3. Specify legal-safe report and marketing outputs (hard gate before publish).
4. Define event-specific promo page generation and lifecycle (create, update, sunset).
5. Define "Google blast" and PR orchestration tied to event geography and severity.
6. Define satellite imagery usage for measurement context only (no damage determination claims).
7. Produce implementable backlog with MVP slice and rollout plan.

## Constraints
- Public brand: **GougeAlert**; legal operator: Ironwood Global Data Management LLC (WY).
- Non-negotiable: **zero public PII exposure** for Jason.
- Must avoid insurance-adjuster behavior and language (no damage causation claims).
- Must avoid defamation and legal advice framing in reports and marketing.
- Pricing guardrails: $9.99 standard, $4.99 weather promo, commercial/bulk tiers unchanged.
- No spend without explicit user approval.

## Known Risks
- Liability risk from over-claiming weather/property damage linkage.
- False positives in event detection causing irrelevant promos.
- Multi-event orchestration complexity (duplicated/competing pages/campaigns).
- SEO cannibalization from too many event pages.
- Vendor account setup/cutover delays (Cloudflare, Vercel, GCP, Stripe, Resend).

## Success Criteria
- A complete technical + legal + marketing blueprint is produced with implementation-ready decisions.
- A deterministic legal gate spec exists for reports/pages/comms.
- A data model exists for event objects, pass binding, and promo assets.
- A first vertical slice (single-event MVP) is specified with test/rollback criteria.
- Decision trail is documented in DECISIONS.md for future continuity.

## Agents Needed
- ORCH (Ish) — orchestrator
- ARCH — platform + data architecture
- WXOPS — weather monitoring and event intelligence
- LEGAL — liability/compliance gate design
- MKT/PR — promo pages, PR, paid search event playbooks
- GEO/IMG — satellite/geo measurement integration
- CHAOS — challenge and failure-mode attack
