# GougeAlert Transition — Finalized Execution Plan

Date: 2026-03-03  
Owner: Jason (decision authority) + Ish (execution orchestrator)

## 0) Canonical Decisions (Locked)

1. **Sunset Ungouge brand now** (publicly invisible ASAP).
2. **Public product brand:** GougeAlert.
3. **Legal operating entity:** Ironwood Global Data Management LLC (Wyoming).
4. **Non-negotiable:** zero public exposure of Jason personal PII.
5. **Pricing model stays:** $9.99 standard, $4.99 weather promo, bulk tiers.
6. **Source synthesis rule:** legal/compliance overrides marketing language when conflicts exist.

---

## 1) What Must Happen First (Containment in 24 hours)

### Goal
Stop additional public PII exposure and reduce attack/discovery surface immediately.

### 24h Containment Checklist

1. **Front-end visibility kill switch (temporary):**
   - Replace Ungouge homepage with short transition page (no personal details).
   - Add `X-Robots-Tag: noindex, nofollow` + robots disallow all (temporary mode).
   - Remove Ungouge sitemap submissions and pause crawl promotion.
2. **Traffic shutoff:**
   - Pause paid campaigns and automated outbound linking to ungouge.ai.
3. **Public metadata scrub:**
   - Remove Vermont/location/personal identifiers from privacy/terms/contact pages.
4. **Inbound contact reroute:**
   - Disable public personal inbox exposure; route all support contacts to business aliases.
5. **Credential hygiene pass:**
   - Rotate exposed/legacy keys where feasible after cutover prep.

### Gate to proceed
Containment complete + manual check confirms no public page discloses personal home/location/contact details.

---

## 2) Conflict Resolution from Blueprint Corpus

### Resolved Conflicts

- **Domain conflict (`gougealert.ai` vs `gougealert.com`):** canonical = `gougealert.com`.
- **Entity conflict (Gouge Alert LLC vs Ironwood):** canonical operator = **Ironwood Global Data Management LLC**; GougeAlert is product brand.
- **Retention conflict (30/90 day patterns):** canonical privacy posture = minimize PII retention; enforce strict 30-day project-workspace policy for raw uploads/PII.
- **Legacy identity references:** Ungouge/Vermont references are deprecated and must be removed from public and code surfaces.

### Important Risk Correction
Some blueprint language says “never share data.” Operationally that must be rendered as:
- **No sale/no lead-gen sharing**, while still allowing strictly necessary processor use (Cloudflare/GCP/Stripe/etc) under contract.

---

## 3) Vendor + Infra Migration Runbook (Deterministic)

## Phase A — Inventory + Freeze
- Snapshot current Cloudflare/Vercel/GCP/Stripe/OAuth/Resend/Search Console config.
- Lower DNS TTL to 300 for changing records.
- Prepare rollback owners and baseline SLOs.

**Stop if:** unknown dependency remains.

## Phase B — Parallel Build (No cutover yet)
- Add/verify `gougealert.com` zone in Cloudflare.
- Add domains to Vercel (`gougealert.com`, `www`).
- Map `api.gougealert.com` to Cloud Run and wait for cert active.
- Keep old ungouge domains fully active during overlap.

**Gate:** new frontend + new API health both green.

## Phase C — Integration dual-stack
- Stripe: add new webhook endpoint while keeping old webhook active.
- Email: verify sender domain (recommended `send.gougealert.com`) + SPF/DKIM/DMARC.
- OAuth providers: add new callbacks/origins; keep old callbacks during overlap.
- Analytics/Search Console: add new domain properties + sitemap.

**Gate:** auth + checkout + webhook + email tests pass on both old/new domains.

## Phase D — Cutover
- Set GougeAlert as primary domain.
- Enable 301 redirects from ungouge.ai to gougealert.com.
- Run smoke suite twice.

**Immediate rollback triggers:** checkout failure, OAuth failure, webhook failures, 5xx spike.

## Phase E — Stabilize 72h
- Monitor logs, payment events, email deliverability, indexation.
- After stable window, increase DNS TTL and start old-surface decommission.

---

## 4) Codebase Impact Map (from repo scan)

## Critical files already showing Ungouge coupling

### Frontend
- `frontend/next.config.js` (CSP connect-src hardcoded `https://api.ungouge.ai`)
- `frontend/src/components/PlausibleAnalytics.tsx` (default domain `ungouge.ai`)
- `frontend/src/app/robots.ts` (sitemap points to Ungouge)
- `frontend/src/app/sitemap.ts` (`BASE_URL` hardcoded `https://ungouge.ai`)
- `frontend/src/app/terms/page.tsx` (brand/domain/emails/legal copy)
- `frontend/content/legal/privacy-policy.md` (contains Ungouge + Vermont location reference)

### Backend
- `backend/main.py` (root message “Ungouge.ai API”, CORS tied to `FRONTEND_URL`)
- `backend/routers/auth.py` (default frontend URL fallback to `https://ungouge.ai`)
- `backend/deploy.sh`, `backend/redeploy-with-email.sh` (Ungouge service names/emails/secrets)
- `infra/*` Terraform/resource naming `ungouge-*` and domain references

### Product/data logic gaps vs new plan
- Current resubmit policy appears 90-day in migration docs; target is 30-day project pass lock.
- No explicit `[Address + User Name + Trade Category]` lock entity yet.
- Retention middleware still includes 90-day behavior for authenticated quotes.

---

## 5) Required Data Model + API Changes

## New/updated entities
1. **project_passes**
   - `id`, `user_id`, `project_fingerprint_hash`, `trade_category`, `address_hash`, `name_hash`, `status`, `expires_at`.
2. **quote_ingestions**
   - Link uploads to pass, store redacted extraction, PII confidence, purge deadlines.
3. **retention_jobs**
   - Track purge eligibility/execution/audit trail for files + DB records.

## Hashing & minimization
- Store hashes/tokenized forms for lock checks; avoid storing raw address/name where not needed.
- Separate redacted analytical payload from raw upload object.

## API contract deltas
- `POST /api/quotes` should require/issue a project pass context.
- `POST /api/payments/checkout` should bind payment to project pass ID.
- `POST /api/quotes/resubmit` should validate same pass fingerprint and 30-day window.
- `GET /api/report/{id}` should return compliance metadata (retention expiry + disclaimer version).
- Admin/compliance endpoint for purge status and DSAR job status.

---

## 6) Engineering Execution Sprints

## Sprint 1 (Containment + Rebrand Core)
- Implement domain/brand replacements in frontend+backend critical files.
- Add temporary de-publication mode for ungouge.ai.
- Externalized env config for all domain constants (no hardcoded Ungouge URLs).

**Exit tests:**
- CSP/CORS valid on GougeAlert.
- Robots/sitemap/canonical correct.
- No personal/public PII in legal/contact pages.

## Sprint 2 (Project Pass + Privacy Core)
- Add `project_passes` model + enforcement middleware.
- Move total-only resubmit logic to 30-day pass rules.
- Implement PII minimization at ingest (redaction/tokenization pipeline).

**Exit tests:**
- pass lock blocks changed address/name/trade combinations.
- paid/unpaid flow works with Stripe webhooks.
- regression tests for auth/report/payment green.

## Sprint 3 (Retention + Compliance automation)
- Replace mixed 90-day retention paths with strict policy matrix.
- Implement 30-day file/data incineration job + audit logs.
- Add output guardrail tests (disclaimer, prohibited phrasing, neutral language).

**Exit tests:**
- scheduled purge removes raw artifacts on schedule.
- audit trail exists for each deletion event.
- compliance test suite blocks unsafe output regressions.

---

## 7) Orchestration Plan (Subagent-ready)

I can run this as parallel tracks with weekly gates:
- Track L (Legal/compliance artifacts)
- Track I (Infra/vendor cutover)
- Track E (App implementation)
- Track Q (QA + launch gate)

Each track outputs checklist evidence; no phase advances without gate signoff.

---

## 8) Launch Gate (Must all be true)

- No public personal PII exposure in site/app/docs.
- Legal pages and disclaimers updated to GougeAlert + Ironwood.
- Stripe, OAuth, email, analytics operational on new domain.
- Project-pass lock and retention jobs active in production.
- Rollback playbook tested and time-bounded.

---

## 9) Immediate Next Actions (Ish)

1. Execute a **PII exposure audit** against current frontend/legal content and produce exact redaction patch list.
2. Generate a **file-by-file implementation patch plan** for Sprint 1.
3. Prepare a **cutover checklist sheet** (operator runbook format) for Cloudflare/Vercel/GCP/Stripe/OAuth.

This is now execution-ready and sequenced to avoid another messy migration.
