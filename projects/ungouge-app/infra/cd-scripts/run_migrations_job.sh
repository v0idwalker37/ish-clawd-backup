#!/usr/bin/env bash
# run_migrations_job.sh — Run alembic migrations via Cloud Run Job
# Usage: ./run_migrations_job.sh <IMAGE_URL>
# Idempotent: creates job if not exists, updates if exists, then executes.
set -euo pipefail

# ── Config ───────────────────────────────────────────────────────────────────
IMAGE="${1:?Usage: run_migrations_job.sh <IMAGE_URL>}"
PROJECT="${PROJECT_ID:-ungouge-app}"
REGION="${REGION:-us-central1}"
JOB_NAME="ungouge-backend-migrate"
CLOUD_SQL_INSTANCE="${PROJECT}:${REGION}:ungouge-app-db"
LOG_PREFIX="[migrations]"

log() { echo "${LOG_PREFIX} $(date '+%H:%M:%S') $*"; }

# ── Check if job exists ─────────────────────────────────────────────────────
log "Checking if job ${JOB_NAME} exists..."
JOB_EXISTS=$(gcloud run jobs describe "${JOB_NAME}" \
  --region "${REGION}" \
  --project "${PROJECT}" \
  --format "value(name)" 2>/dev/null || echo "")

if [ -n "${JOB_EXISTS}" ]; then
  log "Job exists, updating..."
  gcloud run jobs update "${JOB_NAME}" \
    --image "${IMAGE}" \
    --region "${REGION}" \
    --project "${PROJECT}" \
    --set-secrets "DATABASE_URL=DATABASE_URL:latest" \
    --set-cloudsql-instances "${CLOUD_SQL_INSTANCE}" \
    --set-env-vars "ENVIRONMENT=production" \
    --command "alembic" \
    --args "upgrade,head" \
    --task-timeout 300 \
    --max-retries 1 \
    --memory 512Mi \
    --cpu 1 \
    --execution-environment gen2 \
    --quiet
else
  log "Creating new job..."
  gcloud run jobs create "${JOB_NAME}" \
    --image "${IMAGE}" \
    --region "${REGION}" \
    --project "${PROJECT}" \
    --set-secrets "DATABASE_URL=DATABASE_URL:latest" \
    --set-cloudsql-instances "${CLOUD_SQL_INSTANCE}" \
    --set-env-vars "ENVIRONMENT=production" \
    --command "alembic" \
    --args "upgrade,head" \
    --task-timeout 300 \
    --max-retries 1 \
    --memory 512Mi \
    --cpu 1 \
    --execution-environment gen2 \
    --quiet
fi

# ── Execute the migration job ────────────────────────────────────────────────
log "Executing migration job..."
gcloud run jobs execute "${JOB_NAME}" \
  --region "${REGION}" \
  --project "${PROJECT}" \
  --wait \
  --quiet

EXEC_EXIT=$?
if [ ${EXEC_EXIT} -ne 0 ]; then
  log "ERROR: Migration job failed with exit code ${EXEC_EXIT}"
  log "Check logs: gcloud run jobs executions list --job=${JOB_NAME} --region=${REGION} --project=${PROJECT}"
  exit ${EXEC_EXIT}
fi

log "Migrations completed successfully"
log "Verify: gcloud run jobs executions list --job=${JOB_NAME} --region=${REGION} --project=${PROJECT} --limit=3"
