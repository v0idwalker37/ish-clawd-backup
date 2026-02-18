#!/usr/bin/env bash
# build_push_ar.sh — Build and push backend image to Artifact Registry
# Idempotent, retries with exponential backoff. Safe to run multiple times.
set -euo pipefail

# ── Config ───────────────────────────────────────────────────────────────────
PROJECT="${PROJECT_ID:-ungouge-app}"
REGION="${REGION:-us-central1}"
REPO="ungouge-backend"
AR_HOST="${REGION}-docker.pkg.dev"
TAG="autodeploy-$(date +%s)"
IMAGE="${AR_HOST}/${PROJECT}/${REPO}:${TAG}"
CONTEXT_DIR="${CONTEXT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
MAX_RETRIES=3
LOG_PREFIX="[build_push_ar]"

log() { echo "${LOG_PREFIX} $(date '+%H:%M:%S') $*"; }

# ── Step 1: Authenticate docker to AR ────────────────────────────────────────
log "Authenticating docker to ${AR_HOST}"
gcloud auth configure-docker "${AR_HOST}" --quiet 2>/dev/null || true
log "Auth configured (idempotent)"

# ── Step 2: Build image ─────────────────────────────────────────────────────
log "Building image: ${IMAGE}"
log "Context: ${CONTEXT_DIR}"

# Key fix: --provenance=false --sbom=false prevents attestation manifests
# that cause '400 Bad Request' on Artifact Registry push.
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

# ── Step 3: Push with retries + exponential backoff ──────────────────────────
push_with_retry() {
  local attempt=1
  local delay=5
  while [ ${attempt} -le ${MAX_RETRIES} ]; do
    log "Push attempt ${attempt}/${MAX_RETRIES}..."
    if docker push "${IMAGE}" 2>&1; then
      log "Push succeeded on attempt ${attempt}"
      return 0
    fi
    local exit_code=$?
    log "Push failed (exit ${exit_code}), waiting ${delay}s before retry..."
    sleep ${delay}
    delay=$((delay * 2))
    attempt=$((attempt + 1))
  done
  log "ERROR: Push failed after ${MAX_RETRIES} attempts"
  return 1
}

push_with_retry
PUSH_EXIT=$?

if [ ${PUSH_EXIT} -ne 0 ]; then
  log "PUSH_FAIL ${IMAGE}"
  exit 1
fi

# ── Step 4: Output ───────────────────────────────────────────────────────────
log "SUCCESS"
echo ""
echo "IMAGE=${IMAGE}"
echo ""
log "To deploy: ./deploy_cloudrun.sh ${IMAGE}"
