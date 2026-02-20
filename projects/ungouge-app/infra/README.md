Ungouge.app — Infra Runbook

Purpose

This folder contains scripts and runbooks to provision the minimal infra needed to launch Ungouge.ai:
- Cloud SQL (Postgres) instance for the app
- Backend container build + Cloud Run deployment
- Frontend deploy to Vercel + DNS pointers
- SMTP (Resend) setup notes and DNS records

High-level flow (today)
1. Generate production secrets locally (or in Secret Manager)
2. Provision Cloud SQL (Postgres 15, db-f1-micro, us-central1)
3. Create DB user, DB, and store credentials in Secret Manager
4. Build backend Docker image and push to Artifact Registry / GCR
5. Deploy backend to Cloud Run, attach Cloud SQL, map secrets
6. Deploy frontend to Vercel, set env vars to Cloud Run URL
7. Configure Resend (or chosen SMTP) DNS records for SPF/DKIM
8. Run smoke tests

Prereqs (must be available on the machine that runs these scripts)
- gcloud CLI installed and authenticated (gcloud auth login or service account)
- Docker (for local builds) or Cloud Build configured
- Vercel CLI or Vercel token for API operations (if automating frontend)
- Cloudflare access to update DNS records

Security note
- These scripts produce or reference secrets (JWT_SECRET_KEY, CSRF_SECRET_KEY, ENCRYPTION_KEY, DB passwords, Stripe keys, Resend API key). DO NOT commit these secrets to git. Use Google Secret Manager, Vercel's environment variables, or another secret store.

Cost guidance
- Cloud SQL: db-f1-micro (~$7.50/mo) — chosen for cost-consciousness. If you expect higher load, choose a larger tier.
- Cloud Run: start with minimal memory (512Mi) and concurrency (80) to reduce cold-starts and cost. Scale up if needed.

Files in this folder
- generate_secrets.sh — generates a local .env.prod file (DO NOT COMMIT)
- provision_cloudsql.sh — gcloud commands to create Cloud SQL, DB, and Secret Manager entries
- deploy_backend.sh — build/push Docker image and deploy to Cloud Run (placeholders)
- deploy_frontend.sh — Vercel CLI / API commands to deploy frontend and set env vars
- resend_setup.md — DNS records and Resend setup steps
- checklist.md — Sprint checklist and status markers

How I will proceed
- I will not run any gcloud/vercel commands automatically without credentials present.
- If you want me to execute any script from this folder, either run them locally (recommended) or provide temporary credentials/token (service account key, Vercel token). If you provide credentials, I will handle them securely and delete any temp files after use.

"Run now" options
1) I produce the scripts and you run them locally (recommended)
2) You provide a GCP service account JSON key and Vercel token, and I run them here (I'll delete keys afterwards) — only do this if you trust the environment.

Next step suggestion
- I will create the scripts now and spawn three worker sub-agents to validate and produce any missing details and a Terraform variant. Confirm if you want me to proceed.
