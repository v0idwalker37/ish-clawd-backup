# Architecture (Transition Draft)

## Canonical Operating Model
- Product: GougeAlert (national B2C quote auditing)
- Entity: Ironwood Global Data Management LLC (WY)
- Core stack: Next.js (Vercel) + FastAPI (Cloud Run) + Cloud SQL + Cloudflare + Stripe + Document AI + Gemini

## Program Architecture Tracks
1. **Containment Track**
   - Stop public discoverability of Ungouge
   - Prevent further PII leakage vectors
2. **Identity Track**
   - Brand/domain/legal text migration to GougeAlert + Ironwood
3. **Platform Track**
   - Vendor account, DNS, certs, webhooks, callbacks, env vars, billing/profile updates
4. **Application Track**
   - Rebrand strings/domains
   - PII minimization pipeline
   - 30-day pass lock + data incineration jobs
5. **Launch Track**
   - Smoke tests, legal signoff gates, phased re-enable

## Non-Negotiables
- Zero public founder PII exposure
- Legal/compliance-safe output behavior
- No destructive changes without rollback path
