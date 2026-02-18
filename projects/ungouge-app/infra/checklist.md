Sprint checklist — Launch push (today)

MUST (blockers)
- [x] Approve Cloud SQL cost ($7.50/mo)
- [~] Provision Cloud SQL (ungouge-app-db) — in progress (PENDING_CREATE)
- [ ] Create DB + user + store password in Secret Manager
- [x] Fix parse-upload auth (done)
- [x] Remove dead middleware (done)
- [x] Add error_id logging and return (done)
- [x] Enforce CSRF secret (done)
- [ ] Build and deploy backend to Cloud Run (staging/test mode)
- [ ] Deploy frontend to Vercel and set NEXT_PUBLIC_API_URL to backend
- [ ] Configure SMTP (Resend) and add SPF/DKIM records
- [ ] Smoke test: Register -> Submit -> Pay (test) -> Get report + PDF

SHOULD
- [ ] Move rate limiter to Redis (Cloud Memorystore)
- [ ] Tighten CSP (nonces for inline)
- [ ] Add monitoring (Cloud Run uptime checks + log-based alerts)

NICE
- [ ] Canary / blue-green deploy
- [ ] Full pentest or third-party security review

Notes
- Stripe live keys will be added after Jason finishes bank verification (likely Tuesday).
- Cloud Run will initially use test Stripe keys; switch to live keys when ready.

How I will report progress
- I will update this checklist as I complete items and write progress notes to memory/YYYY-MM-DD.md

Immediate progress (2026-02-15 13:05 EST)
- GCP project created: ungouge-app (billing linked)
- Production secrets created and stored: JWT_SECRET_KEY, CSRF_SECRET_KEY, ENCRYPTION_KEY
- Service account created: ungouge-run-sa@ungouge-app.iam.gserviceaccount.com (roles: cloudsql.client, secretmanager.secretAccessor, storage.objectViewer)
- Cloud SQL instance ungouge-app-db: PENDING_CREATE (Ish polling for RUNNABLE)

Next immediate steps (automated):
1. When Cloud SQL RUNNABLE -> create DB (ungouge_app), create user (ungouge_admin), store DB password in Secret Manager as 'ungouge-db-password'
2. Build backend image, push to Artifact Registry/GCR, deploy to Cloud Run (staging) with Cloud SQL attached and secrets mapped
3. Run alembic migrations (alembic upgrade head) and execute smoke tests
4. Prepare frontend deployment and DNS plan (Vercel token optional)

Run mode: Full-auto (Ish) — continuing unless you say "pause".
