# UNGOUGE.AI LAUNCH CHECKLIST — February 18, 2026

## Current State (Honest Assessment)

**What EXISTS and is substantial:**
- ✅ Backend monolith: 15,477 lines (FastAPI, auth, Stripe checkout, quote analysis, PDF generation, MFA, GDPR)
- ✅ Frontend: 7,730 lines (Next.js 14, 15 pages, login/register/dashboard/analyze/report/pricing/blog)
- ✅ Production Dockerfile (multi-stage, non-root, health checks, tesseract/poppler included)
- ✅ Deploy scripts (deploy_backend.sh, deploy_frontend.sh)
- ✅ DNS: ungouge.ai → 76.76.21.21 (Vercel)
- ✅ GCP project: ungouge-app (gcloud configured, void@ungouge.ai authenticated)
- ✅ Vercel project exists (frontend deployed at frontend-eight-mocha-56.vercel.app)
- ✅ Stripe integration built (create-checkout, webhook handler, $19.99 per report)
- ✅ Quote analysis engine (quote_analyzer.py: 2,419 lines + services/analyzer.py: 651 lines)
- ✅ Next.js rewrites `/api/*` → backend (already configured in next.config.js)
- ✅ CSP headers configured (Stripe, self, API)

**What is NOT ready:**
- ❌ GCP auth expired (gcloud needs re-auth — can't check what's deployed)
- ❌ No backend .env file (secrets not configured)
- ❌ No frontend .env file (API_URL not set)
- ❌ Unknown: Is Cloud SQL provisioned? Are secrets in Secret Manager? Is anything actually running?
- ❌ Vercel Git not connected (manual deploys only)
- ❌ Backend not confirmed deployed/running on Cloud Run
- ❌ Stripe keys not confirmed in production mode
- ❌ SSL/custom domain not confirmed on Vercel
- ❌ Email service (Resend) not confirmed working
- ❌ No end-to-end test has ever been run

**What I wrote today (microservices) — NOT NEEDED FOR LAUNCH:**
The 4 new microservices, Terraform modules, CI/CD pipelines — these are v2 architecture. The existing monolith is the launch vehicle. We deploy what works, not what's new and untested.

---

## Launch Plan: Deploy the Existing Monolith + Frontend

### Phase 0: GCP Access (BLOCKER — needs Jason)
- [ ] **Re-authenticate gcloud:** `gcloud auth login` (interactive — needs browser)
- [ ] **Verify GCP project:** Confirm `ungouge-app` is correct project
- [ ] After auth: inventory what's already deployed (Cloud Run, Cloud SQL, secrets)

### Phase 1: Backend Infrastructure (once GCP access restored)
- [ ] **Database:** Check if Cloud SQL exists, or provision it
  - If not: `gcloud sql instances create ungouge-app-db --database-version=MYSQL_8_0 --tier=db-f1-micro --region=us-central1`
  - Run initial schema migration
  - Or: use SQLite for MVP launch (backend already defaults to `sqlite+aiosqlite:///./ungouge.db`)
- [ ] **Secrets in Secret Manager:** Create/verify these exist:
  - `JWT_SECRET_KEY` (generate random 32-byte)
  - `CSRF_SECRET_KEY` (generate random 32-byte)
  - `ENCRYPTION_KEY` (generate random 32-byte)
  - `STRIPE_SECRET_KEY` (from Stripe dashboard — test or live?)
  - `STRIPE_WEBHOOK_SECRET` (from Stripe dashboard)
  - `RESEND_API_KEY` (for email)
  - `DATABASE_URL` (Cloud SQL connection string)
- [ ] **Decision needed:** Launch with Stripe TEST mode or LIVE mode?

### Phase 2: Backend Deployment
- [ ] **Build Docker image:** `docker build -t gcr.io/ungouge-app/ungouge-backend:v1 .`
- [ ] **Push to GCR:** `docker push gcr.io/ungouge-app/ungouge-backend:v1`
- [ ] **Deploy to Cloud Run:**
  ```
  gcloud run deploy ungouge-backend \
    --image gcr.io/ungouge-app/ungouge-backend:v1 \
    --region us-central1 \
    --allow-unauthenticated \
    --set-secrets "JWT_SECRET_KEY=JWT_SECRET_KEY:latest,..." \
    --add-cloudsql-instances ungouge-app:us-central1:ungouge-app-db
  ```
- [ ] **Verify health:** `curl https://<cloud-run-url>/health`
- [ ] **Test auth flow:** Register → Login → Get token
- [ ] **Test quote analysis:** Upload test quote → Get analysis
- [ ] **Test Stripe:** Create checkout session → Verify redirect URL

### Phase 3: Frontend Deployment
- [ ] **Set environment variables in Vercel:**
  - `API_URL` = Cloud Run backend URL (server-side, for rewrites)
  - `NEXT_PUBLIC_STRIPE_KEY` = Stripe publishable key
  - `NEXT_PUBLIC_PLAUSIBLE_DOMAIN` = ungouge.ai (if using Plausible)
- [ ] **Connect custom domain:** Verify ungouge.ai is properly connected in Vercel
  - DNS already points to 76.76.21.21 (Vercel)
  - Add domain in Vercel dashboard if not already added
  - SSL auto-provisioned by Vercel
- [ ] **Deploy frontend:** `vercel --prod` or push to connected Git branch
- [ ] **Verify:** Visit https://ungouge.ai — homepage loads
- [ ] **Verify:** `/api/health` proxies to backend and returns OK

### Phase 4: Stripe Configuration
- [ ] **Decision:** Test mode vs Live mode for launch
- [ ] **Create webhook endpoint in Stripe dashboard:**
  - URL: `https://<cloud-run-url>/api/payments/webhook`
  - Events: `checkout.session.completed`, `payment_intent.succeeded`, `payment_intent.payment_failed`
- [ ] **Verify webhook secret** matches what's in Secret Manager
- [ ] **Test checkout flow:** Create session → Complete payment (test card) → Verify report generated
- [ ] **Pricing:** Confirm $19.99 per report is correct

### Phase 5: Email Service
- [ ] **Resend setup:** Verify API key works
- [ ] **Domain verification:** Verify ungouge.ai in Resend for sending
- [ ] **Test:** Registration email, password reset email
- [ ] **From address:** noreply@ungouge.ai (or whatever is configured)

### Phase 6: End-to-End Testing
- [ ] **Full user journey:**
  1. Visit ungouge.ai → Homepage loads, looks good
  2. Click "Get Started" → Registration page
  3. Register with email/password → Account created
  4. Upload a contractor quote (PDF/image) → Quote extracted
  5. View analysis results → Cost breakdown shown
  6. Click "Get Full Report" → Stripe checkout
  7. Complete payment (test card) → Report generated
  8. View/download report → PDF works
  9. Dashboard → Shows quote history
  10. Logout → Login again → Session works
- [ ] **Error cases:**
  - Invalid email registration
  - Wrong password login
  - Upload non-quote file
  - Stripe payment failure
  - Session expiry
- [ ] **Mobile responsive:** Test on phone-sized viewport
- [ ] **Cross-browser:** Chrome, Firefox, Safari (at minimum Chrome)

### Phase 7: Polish & Hardening
- [ ] **Error pages:** 404, 500 pages look professional
- [ ] **Loading states:** Spinners/skeletons during API calls
- [ ] **Rate limiting:** Verify rate limits work (registration, login, analysis)
- [ ] **Security headers:** Verify CSP, HSTS, X-Frame-Options active
- [ ] **Meta tags:** Title, description, OG image for social sharing
- [ ] **Favicon:** Exists and looks right
- [ ] **Analytics:** Plausible or similar configured (optional for day 1)
- [ ] **Cookie consent banner:** Working (exists in frontend as CookieConsent.tsx)
- [ ] **Terms of Service:** Page exists (/terms)
- [ ] **Privacy Policy:** Page exists (/privacy)

### Phase 8: Monitoring (launch day)
- [ ] **Cloud Run logs:** Accessible, no errors
- [ ] **Health check:** Backend responding
- [ ] **Stripe webhook:** Events being received
- [ ] **Error alerting:** At minimum, check Cloud Logging manually
- [ ] **Uptime:** Service stays up under initial traffic

---

## Decisions Needed Before I Start

1. **GCP auth** — You need to run `gcloud auth login` (interactive, needs browser). Can you do that now or give me another way in?

2. **Stripe mode** — Launch with TEST keys (safe, fake payments) or LIVE keys (real money)?

3. **Database** — Cloud SQL ($7-10/month) or SQLite for MVP? (SQLite is simpler but doesn't scale and loses data on redeploy unless we mount a volume)

4. **Email** — Is Resend configured and domain verified? Or skip email verification for day 1?

5. **Scope** — Is the existing monolith + frontend good enough to launch? Or are there features you consider must-have that aren't built?

6. **Content** — Is the copy on the homepage/about/pricing pages final? Or do they need editing?

---

## Time Estimate

| Phase | Estimated Time | Blocker? |
|-------|---------------|----------|
| Phase 0: GCP Access | 5 min | **YES — needs Jason** |
| Phase 1: Infrastructure | 30-60 min | Depends on what exists |
| Phase 2: Backend Deploy | 30-45 min | |
| Phase 3: Frontend Deploy | 20-30 min | |
| Phase 4: Stripe Config | 15-30 min | |
| Phase 5: Email Service | 15-30 min | |
| Phase 6: E2E Testing | 60-90 min | |
| Phase 7: Polish | 60-120 min | |
| Phase 8: Monitoring | 15 min | |

**Total: 4-7 hours of focused work**

If GCP auth is resolved tonight, I can have this done by morning.

---

## What I Will NOT Do

- Not deploying the new microservices (untested, unnecessary for launch)
- Not rewriting anything — deploying what exists
- Not over-engineering — MVP launch, iterate later
- Not touching anything without the decisions above answered
