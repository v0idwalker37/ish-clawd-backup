# Operator Action Checklist — GougeAlert Transition

*Generated: March 3, 2026*

These are actions that **require Jason** (account access, vendor logins, financial accounts). Ish cannot do these autonomously.

---

## Phase A — Immediate Containment (ungouge.ai)

### A1. Vercel: Deploy sunset mode on ungouge.ai
- [ ] In Vercel dashboard → Project Settings → Environment Variables
- [ ] Add: `NEXT_PUBLIC_SUNSET_MODE=1` (Production only, for the ungouge.ai project)
- [ ] Trigger redeploy (or push the current branch — all code changes are committed)
- **Effect:** All routes rewrite to `/sunset` page → "Continue to GougeAlert.com" CTA
- **Rollback:** Remove env var + redeploy

### A2. Vercel: Create new project for gougealert.com
- [ ] Import same GitHub repo
- [ ] Set root directory to `projects/ungouge-app/frontend`
- [ ] Env vars: `NEXT_PUBLIC_SITE_URL=https://gougealert.com`, `NEXT_PUBLIC_API_URL=https://api.gougealert.com` (or keep old API URL temporarily)
- [ ] Do NOT set `NEXT_PUBLIC_SUNSET_MODE` on this project
- [ ] Custom domain → `gougealert.com` + `www.gougealert.com`

### A3. Cloudflare: DNS for gougealert.com
- [ ] Point `gougealert.com` and `www.gougealert.com` to Vercel (CNAME `cname.vercel-dns.com`)
- [ ] Point `api.gougealert.com` to Cloud Run (or keep proxying through existing setup)
- [ ] Redirect `gouge-alert.com` → `gougealert.com` (Page Rule or Bulk Redirect)

### A4. Google Search Console
- [ ] Add property: `gougealert.com`
- [ ] Submit sitemap: `https://gougealert.com/sitemap.xml`
- [ ] On `ungouge.ai` property: request removal of all indexed URLs (optional — noindex will handle it over time)

---

## Phase B — Backend Redeployment

### B1. Cloud Run: Redeploy with new env vars
- [ ] Update env vars on the Cloud Run service (or use the updated `deploy.sh`):
  - `FROM_EMAIL=noreply@gougealert.com`
  - `FROM_NAME=GougeAlert`
  - `FRONTEND_URL=https://gougealert.com`
  - `CORS_ORIGINS=https://gougealert.com,https://www.gougealert.com`
- [ ] Deploy: `cd backend && ./deploy.sh`
- [ ] Verify health: `curl https://api.gougealert.com/health`

### B2. Resend: Add gougealert.com sending domain
- [ ] Log into Resend dashboard
- [ ] Add domain: `gougealert.com`
- [ ] Add DNS records (DKIM, SPF, DMARC) in Cloudflare
- [ ] Verify domain in Resend
- [ ] Keep `ungouge.ai` domain active temporarily (in case of in-flight emails)

### B3. Stripe: Update branding
- [ ] Dashboard → Settings → Branding → Update business name to "GougeAlert"
- [ ] Dashboard → Settings → Public details → Update support URL/email
- [ ] Update webhook endpoint URL if API domain changes
- [ ] Statement descriptor: `GOUGEALERT` (max 22 chars)

---

## Phase C — Vendor Account Updates

### C1. Plausible Analytics
- [ ] Add site: `gougealert.com`
- [ ] (Optional) Keep `ungouge.ai` site to track sunset traffic decay
- [ ] Update script domain in PlausibleAnalytics.tsx if using custom proxy

### C2. GitHub
- [ ] Consider renaming repo from `ish-clawd-backup` to something GougeAlert-related (optional)
- [ ] Update any GitHub Actions secrets if domain-dependent

### C3. Cloudflare: Email routing
- [ ] Set up email routing for `gougealert.com` (support@, legal@, admin@, etc.)
- [ ] Forward to appropriate inboxes

---

## Phase D — Legal / Corporate

### D1. Wyoming LLC
- [ ] Confirm Ironwood Global Data Management LLC is active with WY Secretary of State
- [ ] Obtain EIN from IRS (SS-4 form)
- [ ] Open business bank account under Ironwood LLC

### D2. Stripe: Transfer to Ironwood
- [ ] Once EIN + bank account are ready, update Stripe to Ironwood entity
- [ ] Update tax/legal info in Stripe dashboard

### D3. Google Cloud: Billing
- [ ] Update billing contact/entity to Ironwood (once EIN exists)

---

## Phase E — Cleanup (After 30 Days)

### E1. Remove ungouge.ai from Vercel
- [ ] Delete or archive the sunset project after Google deindexes
- [ ] Set up permanent 301 redirect: `ungouge.ai/*` → `gougealert.com/*` via Cloudflare Page Rules

### E2. DNS cleanup
- [ ] Remove A/CNAME records for `ungouge.ai` that pointed to Vercel (keep domain registration)
- [ ] Remove `api.ungouge.ai` record once all API traffic routes to new domain

### E3. Resend: Remove old domain
- [ ] Remove `ungouge.ai` sending domain from Resend after confirming no in-flight emails

### E4. Remove `NEXT_PUBLIC_LEGACY_API_ORIGIN` from CSP config
- [ ] Once `api.ungouge.ai` is fully retired, remove the legacy CSP entry from `next.config.js`

---

## Verification Gates

Before each phase, verify:

| Gate | Check | Command |
|------|-------|---------|
| Code | Frontend builds | `cd frontend && npm run build` |
| Code | Backend tests pass | `cd backend && ./venv/bin/python -m pytest -q` |
| Deploy | Sunset mode works | Visit `https://ungouge.ai` → should show sunset page |
| Deploy | New site works | Visit `https://gougealert.com` → should show full site |
| Deploy | API health | `curl https://api.gougealert.com/health` |
| Email | Test email | Trigger password reset on gougealert.com |
| Payment | Test checkout | Submit test quote on gougealert.com (Stripe test mode) |
