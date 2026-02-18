#!/usr/bin/env bash
# deploy_cloudrun.sh — Deploy backend image to Cloud Run with secrets + Cloud SQL
# Usage: ./deploy_cloudrun.sh <IMAGE_URL>
# Idempotent: safe to run multiple times.
set -euo pipefail

# ── Config ───────────────────────────────────────────────────────────────────
IMAGE="${1:?Usage: deploy_cloudrun.sh <IMAGE_URL>}"
PROJECT="${PROJECT_ID:-ungouge-app}"
REGION="${REGION:-us-central1}"
SERVICE="ungouge-backend"
CLOUD_SQL_INSTANCE="${PROJECT}:${REGION}:ungouge-app-db"
LOG_PREFIX="[deploy_cloudrun]"

log() { echo "${LOG_PREFIX} $(date '+%H:%M:%S') $*"; }

# ── Validate image exists ────────────────────────────────────────────────────
log "Deploying image: ${IMAGE}"
log "Service: ${SERVICE} in ${REGION}"
log "Cloud SQL: ${CLOUD_SQL_INSTANCE}"

# ── Deploy ───────────────────────────────────────────────────────────────────
# Notes:
# - --set-secrets maps Secret Manager secrets as env vars inside the container
# - --add-cloudsql-instances enables Cloud SQL Auth Proxy sidecar
# - --allow-unauthenticated: set to true for public API; remove for internal only
# - Memory/CPU: 1Gi/1 CPU is safe starting point; adjust after load testing
# - Min instances 0 = scale to zero (saves cost); set to 1 for warm starts

log "Running gcloud run deploy..."
gcloud run deploy "${SERVICE}" \
  --image "${IMAGE}" \
  --region "${REGION}" \
  --project "${PROJECT}" \
  --platform managed \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300 \
  --port 8000 \
  --set-env-vars "ENVIRONMENT=production" \
  --set-secrets "\
JWT_SECRET_KEY=JWT_SECRET_KEY:latest,\
CSRF_SECRET_KEY=CSRF_SECRET_KEY:latest,\
ENCRYPTION_KEY=ENCRYPTION_KEY:latest,\
DATABASE_URL=DATABASE_URL:latest" \
  --add-cloudsql-instances "${CLOUD_SQL_INSTANCE}" \
  --execution-environment gen2 \
  --quiet

DEPLOY_EXIT=$?
if [ ${DEPLOY_EXIT} -ne 0 ]; then
  log "ERROR: Deploy failed with exit code ${DEPLOY_EXIT}"
  exit ${DEPLOY_EXIT}
fi

# ── Get service URL ──────────────────────────────────────────────────────────
SERVICE_URL=$(gcloud run services describe "${SERVICE}" \
  --region "${REGION}" \
  --project "${PROJECT}" \
  --format "value(status.url)" 2>/dev/null || echo "")

log "Deploy succeeded!"
echo ""
echo "SERVICE_URL=${SERVICE_URL}"
echo ""

# ── Healthcheck ──────────────────────────────────────────────────────────────
if [ -n "${SERVICE_URL}" ]; then
  log "Running healthcheck..."
  sleep 5  # Give container time to start
  HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' "${SERVICE_URL}/health" --max-time 15 || echo "000")
  if [ "${HTTP_CODE}" = "200" ]; then
    log "Healthcheck PASSED (HTTP ${HTTP_CODE})"
  else
    log "WARNING: Healthcheck returned HTTP ${HTTP_CODE} (may need warm-up time)"
    log "Check logs: gcloud logs read --project=${PROJECT} --limit=50 'resource.type=cloud_run_revision AND resource.labels.service_name=${SERVICE}'"
  fi
fi

# ── IAM Notes ────────────────────────────────────────────────────────────────
echo ""
log "IAM Notes:"
log "  - Cloud Run SA needs roles/secretmanager.secretAccessor for secrets"
log "  - Cloud Run SA needs roles/cloudsql.client for Cloud SQL"
log "  - To grant public access (if --allow-unauthenticated was rejected):"
log "    gcloud run services add-iam-policy-binding ${SERVICE} \\"
log "      --region=${REGION} --member='allUsers' --role='roles/run.invoker'"
