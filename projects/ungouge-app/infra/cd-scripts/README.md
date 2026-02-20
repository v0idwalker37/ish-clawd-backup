# CD Pipeline Scripts — UnGouge Backend

## Root Cause

Docker buildx attestation manifests (provenance/SBOM) cause `400 Bad Request` on
Artifact Registry push. All image layers push fine, but the attestation manifest
HEAD check fails. **Fix:** build with `--provenance=false --sbom=false`.

## Quick Start (run in order)

```bash
cd infra/cd-scripts
chmod +x *.sh

# 1. Fix IAM permissions first
./iam_changes.sh

# 2. Build & push to Artifact Registry
./build_push_ar.sh
# → outputs IMAGE=us-central1-docker.pkg.dev/ungouge-app/ungouge-backend:autodeploy-<ts>

# 3. If AR push fails, use GCR fallback
./build_push_gcr.sh
# → outputs IMAGE=gcr.io/ungouge-app/ungouge-backend:autodeploy-<ts>

# 4. Run database migrations
./run_migrations_job.sh <IMAGE>

# 5. Deploy to Cloud Run
./deploy_cloudrun.sh <IMAGE>

# 6. Smoke test
./smoke_tests.sh
# or: ./smoke_tests.sh https://ungouge-backend-xxxxx-uc.a.run.app

# 7. DNS + Email (Cloudflare + Resend)
./cf_resend_dns.sh --zone-id <YOUR_CF_ZONE_ID> --domain ungouge.ai --vercel-cname cname.vercel-dns.com
```

## Environment Variables

All scripts default to:
- `PROJECT_ID=ungouge-app`
- `REGION=us-central1`

Override with: `PROJECT_ID=my-project ./build_push_ar.sh`

## Secrets

Scripts read secrets from Secret Manager at runtime via `gcloud secrets versions access`.
No secret values are stored in scripts, logs, or output.

Required secrets: `JWT_SECRET_KEY`, `CSRF_SECRET_KEY`, `ENCRYPTION_KEY`, `DATABASE_URL`,
`CLOUDFLARE_API_TOKEN`, `RESEND_API_KEY`

## Files

| Script | Purpose |
|--------|---------|
| `build_push_ar.sh` | Build + push to Artifact Registry (primary) |
| `build_push_gcr.sh` | Build + push to gcr.io (fallback) |
| `deploy_cloudrun.sh` | Deploy image to Cloud Run with secrets + Cloud SQL |
| `run_migrations_job.sh` | Run alembic migrations via Cloud Run Job |
| `smoke_tests.sh` | Post-deploy smoke tests (health, register, login, upload, analyze, PDF) |
| `cf_resend_dns.sh` | Cloudflare DNS + Resend email domain setup |
| `iam_changes.sh` | IAM grants for service accounts |
| `DIAGNOSIS.md` | Detailed root-cause analysis |
