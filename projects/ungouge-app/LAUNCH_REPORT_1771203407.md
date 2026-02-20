# Ungouge App — Launch Report

**Date:** 2026-02-15 (Sunday)  
**Project:** `ungouge-app` (GCP project 1934459654)  
**Region:** us-central1  

---

## 1. Summary

The Ungouge backend was built, pushed to GCR, deployed to Cloud Run, and smoke-tested. Core endpoints are live and responding. Migrations failed (needs investigation). Resend domain verification did not complete (502 error from Resend API). Post-deploy IAM cleanup was performed successfully.

---

## 2. Steps Performed

### 2.1 Docker Build
- **Image:** `gcr.io/ungouge-app/ungouge-backend:autodeploy-1771198564`
- **Result:** ✅ Build succeeded (multi-stage, 7 layers)
- **Note:** Initial push from build script failed due to missing `docker-credential-gcloud` in PATH. Push was retried manually (see 2.2).
- **Log:** `/tmp/build_push_gcr_run2.out` (428 lines)

### 2.2 Image Push to GCR
- **Result:** ✅ Push succeeded
- **Digest:** `sha256:0875c0936a2bf386fc7c9d3fc559ae780ddf5f24e9f3c476c407a6ea4fc6f036`
- **Command used:**
  ```
  docker push gcr.io/ungouge-app/ungouge-backend:autodeploy-1771198564
  ```
- **Log:** `/tmp/push_and_deploy.out` (120 lines)

### 2.3 Cloud Run Deploy
- **Service:** `ungouge-backend` in `us-central1`
- **Revision:** `ungouge-backend-00005-ld8` (serving 100% traffic)
- **Cloud SQL instance:** `ungouge-app:us-central1:ungouge-app-db`
- **Result:** ✅ Deploy succeeded, healthcheck passed (HTTP 200)
- **Command used:**
  ```
  gcloud run deploy ungouge-backend \
    --image gcr.io/ungouge-app/ungouge-backend:autodeploy-1771198564 \
    --region us-central1 \
    --add-cloudsql-instances=ungouge-app:us-central1:ungouge-app-db \
    --allow-unauthenticated
  ```
- **Log:** `/tmp/deploy_run.out` (25 lines)

### 2.4 Database Migrations
- **Job:** `ungouge-backend-migrate` (Cloud Run Job)
- **Result:** ❌ Migration job failed
- **Execution ID:** `ungouge-backend-migrate-kms8k`
- **Next steps:** Inspect execution logs:
  ```
  gcloud run jobs executions describe ungouge-backend-migrate-kms8k --region=us-central1
  ```
  Or view in Console: https://console.cloud.google.com/run/jobs/executions/details/us-central1/ungouge-backend-migrate-kms8k?project=1934459654
- **Log:** `/tmp/migrations_run2.out` (20 lines)

### 2.5 Smoke Tests
- **Base URL:** `https://ungouge-backend-xwzrtkr2ea-uc.a.run.app`
- **Results:** ✅ 3/3 passed, 0 failed
  - `GET /health` → HTTP 200 ✅
  - `POST /api/v1/auth/register` → HTTP 201 ✅
  - `POST /api/v1/auth/login` → HTTP 200 ✅
- **Skipped:** Upload, analyze, PDF (no auth token obtained from login response)
- **Log:** `/tmp/smoke_tests_run3.out` (14 lines)

### 2.6 Domain / DNS / Resend
- **Resend domain setup:** ❌ Failed (502 from Resend API)
- **Cloudflare DNS:** No log found (`/tmp/cf_resend_dns.out` does not exist)
- **Log:** `/tmp/resend_domain_out` (5 lines)

### 2.7 IAM Cleanup (Post-Deploy)
- **Removed:** `roles/storage.admin` from Cloud Build SA (`1934459654@cloudbuild.gserviceaccount.com`)
- **Command used:**
  ```
  bash infra/cd-scripts/iam_changes.sh --remove-elevated
  ```
- **Verified:** IAM policy no longer contains `roles/storage.admin`
- **Post-cleanup IAM snapshot:** `/tmp/iam_after_cleanup.txt`

---

## 3. Service URLs

| Endpoint | URL |
|----------|-----|
| Cloud Run Service | https://ungouge-backend-xwzrtkr2ea-uc.a.run.app |
| Health Check | https://ungouge-backend-xwzrtkr2ea-uc.a.run.app/health |
| Console (Revisions) | https://console.cloud.google.com/run/detail/us-central1/ungouge-backend/revisions?project=ungouge-app |

---

## 4. Remaining IAM Roles (Post-Cleanup)

| Role | Member |
|------|--------|
| artifactregistry.admin | compute SA, cloudbuild SA |
| artifactregistry.writer | compute SA, cloudbuild SA |
| cloudbuild.builds.builder | cloudbuild SA |
| cloudsql.client | compute SA, ungouge-run-sa |
| iam.serviceAccountUser | cloudbuild SA |
| logging.logWriter | compute SA |
| owner | void@ungouge.ai |
| run.developer | cloudbuild SA |
| secretmanager.secretAccessor | compute SA |
| storage.objectViewer | ungouge-run-sa |

*Service agent roles (artifactregistry, cloudbuild, containerregistry, pubsub, run) omitted — these are Google-managed.*

---

## 5. Remaining Blockers

| Blocker | Priority | Notes |
|---------|----------|-------|
| **Migration job failed** | HIGH | Job `ungouge-backend-migrate-kms8k` failed. Check execution logs for root cause (likely DB connectivity or schema issue). |
| **Resend domain verification** | MEDIUM | Resend API returned 502 when adding `ungouge.ai`. Retry later or configure manually in Resend dashboard. |
| **Smoke test auth token** | LOW | Login returns 200 but smoke test couldn't extract token — may be a response format issue or expected if DB migrations haven't run yet. |
| **Custom domain mapping** | LOW | No custom domain mapped to Cloud Run yet. Service only accessible via auto-generated `.run.app` URL. |

---

## 6. Log Artifacts Index

| File | Description |
|------|-------------|
| `/tmp/build_push_gcr_run2.out` | Docker build output (428 lines) |
| `/tmp/push_and_deploy.out` | GCR push output (120 lines) |
| `/tmp/deploy_run.out` | Cloud Run deploy output (25 lines) |
| `/tmp/migrations_run2.out` | Migration job output (20 lines) |
| `/tmp/smoke_tests_run3.out` | Smoke test results (14 lines) |
| `/tmp/resend_domain_out` | Resend domain setup attempt (5 lines) |
| `/tmp/iam_after_cleanup.txt` | IAM policy after Storage Admin removal |

---

*Generated by CleanupReportAgent on 2026-02-15 19:56 EST*
