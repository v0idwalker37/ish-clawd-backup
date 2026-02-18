#!/usr/bin/env bash
# build_push_gcr.sh — Fallback: Build and push to gcr.io (Container Registry)
# Use this if Artifact Registry push fails. Idempotent.
set -euo pipefail

# ── Config ───────────────────────────────────────────────────────────────────
PROJECT="${PROJECT_ID:-ungouge-app}"
TAG="autodeploy-$(date +%s)"
IMAGE="gcr.io/${PROJECT}/ungouge-backend:${TAG}"
CONTEXT_DIR="${CONTEXT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
MAX_RETRIES=3
LOG_PREFIX="[build_push_gcr]"

log() { echo "${LOG_PREFIX} $(date '+%H:%M:%S') $*"; }

# ── Step 1: Authenticate docker to gcr.io ────────────────────────────────────
log "Authenticating docker to gcr.io"
gcloud auth configure-docker gcr.io --quiet 2>/dev/null || true

# ── Step 2: Build image ─────────────────────────────────────────────────────
log "Building image: ${IMAGE}"
docker build \
  --provenance=false \
  --sbom=false \
  -t "${IMAGE}" \
  -f "${CONTEXT_DIR}/Dockerfile" \
  "${CONTEXT_DIR}"

BUILD_EXIT=$?
if [ ${BUILD_EXIT} -ne 0 ]; then
  log "ERROR: Build failed with exit code ${BUILD_EXIT}"
  exit ${BUILD_EXIT}
fi
log "Build succeeded"

# ── Step 3: Push with retries ────────────────────────────────────────────────
attempt=1
delay=5
while [ ${attempt} -le ${MAX_RETRIES} ]; do
  log "Push attempt ${attempt}/${MAX_RETRIES}..."
  if docker push "${IMAGE}" 2>&1; then
    log "Push succeeded on attempt ${attempt}"
    echo ""
    echo "IMAGE=${IMAGE}"
    echo ""
    log "To deploy: ./deploy_cloudrun.sh ${IMAGE}"
    exit 0
  fi
  log "Push failed, waiting ${delay}s..."
  sleep ${delay}
  delay=$((delay * 2))
  attempt=$((attempt + 1))
done

log "ERROR: Push failed after ${MAX_RETRIES} attempts"
exit 1
