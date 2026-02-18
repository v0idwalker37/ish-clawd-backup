#!/usr/bin/env bash
# iam_changes.sh — Minimal IAM grants to unblock artifact push + Cloud Run deploy
# Idempotent: add-iam-policy-binding is a no-op if binding already exists.
# Usage: ./iam_changes.sh [--remove-elevated]
set -euo pipefail

PROJECT="${PROJECT_ID:-ungouge-app}"
REGION="${REGION:-us-central1}"
LOG_PREFIX="[iam]"

log() { echo "${LOG_PREFIX} $(date '+%H:%M:%S') $*"; }

# ── Discover service account emails ──────────────────────────────────────────
PROJECT_NUMBER=$(gcloud projects describe "${PROJECT}" --format="value(projectNumber)" 2>/dev/null || echo "")
if [ -z "${PROJECT_NUMBER}" ]; then
  log "ERROR: Could not determine project number for ${PROJECT}"
  exit 1
fi

CLOUD_BUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
CLOUD_RUN_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"  # Default Cloud Run SA

log "Project: ${PROJECT} (number: ${PROJECT_NUMBER})"
log "Cloud Build SA: ${CLOUD_BUILD_SA}"
log "Compute/Cloud Run SA: ${COMPUTE_SA}"
echo ""

# ── Required grants ──────────────────────────────────────────────────────────
log "=== Applying required IAM bindings ==="

# 1. Cloud Build SA needs Artifact Registry Writer to push images
log "Grant: Cloud Build SA -> Artifact Registry Writer"
gcloud projects add-iam-policy-binding "${PROJECT}" \
  --member="serviceAccount:${CLOUD_BUILD_SA}" \
  --role="roles/artifactregistry.writer" \
  --condition=None \
  --quiet 2>/dev/null || log "  (may already exist)"

# 2. Cloud Build SA needs Storage Admin for GCR fallback (legacy)
log "Grant: Cloud Build SA -> Storage Admin (GCR fallback)"
gcloud projects add-iam-policy-binding "${PROJECT}" \
  --member="serviceAccount:${CLOUD_BUILD_SA}" \
  --role="roles/storage.admin" \
  --condition=None \
  --quiet 2>/dev/null || log "  (may already exist)"

# 3. Compute SA (Cloud Run) needs Secret Manager access
log "Grant: Compute SA -> Secret Manager Secret Accessor"
gcloud projects add-iam-policy-binding "${PROJECT}" \
  --member="serviceAccount:${COMPUTE_SA}" \
  --role="roles/secretmanager.secretAccessor" \
  --condition=None \
  --quiet 2>/dev/null || log "  (may already exist)"

# 4. Compute SA (Cloud Run) needs Cloud SQL Client
log "Grant: Compute SA -> Cloud SQL Client"
gcloud projects add-iam-policy-binding "${PROJECT}" \
  --member="serviceAccount:${COMPUTE_SA}" \
  --role="roles/cloudsql.client" \
  --condition=None \
  --quiet 2>/dev/null || log "  (may already exist)"

# 5. Cloud Build SA needs Cloud Run Developer (for CI/CD deploy)
log "Grant: Cloud Build SA -> Cloud Run Developer"
gcloud projects add-iam-policy-binding "${PROJECT}" \
  --member="serviceAccount:${CLOUD_BUILD_SA}" \
  --role="roles/run.developer" \
  --condition=None \
  --quiet 2>/dev/null || log "  (may already exist)"

# 6. Cloud Build SA needs Service Account User (to deploy as compute SA)
log "Grant: Cloud Build SA -> Service Account User"
gcloud projects add-iam-policy-binding "${PROJECT}" \
  --member="serviceAccount:${CLOUD_BUILD_SA}" \
  --role="roles/iam.serviceAccountUser" \
  --condition=None \
  --quiet 2>/dev/null || log "  (may already exist)"

echo ""
log "All required IAM bindings applied."

# ── Optional: Remove elevated roles after first push ─────────────────────────
if [ "${1:-}" = "--remove-elevated" ]; then
  echo ""
  log "=== Removing elevated/temporary roles ==="

  # Remove Storage Admin (only needed for initial GCR push)
  log "Removing: Cloud Build SA -> Storage Admin"
  gcloud projects remove-iam-policy-binding "${PROJECT}" \
    --member="serviceAccount:${CLOUD_BUILD_SA}" \
    --role="roles/storage.admin" \
    --quiet 2>/dev/null || log "  (not found, OK)"

  # Downgrade AR Writer to AR Reader if only pulls needed
  # (Keep writer if CI/CD will push regularly)
  # log "Removing: Cloud Build SA -> Artifact Registry Writer"
  # gcloud projects remove-iam-policy-binding "${PROJECT}" \
  #   --member="serviceAccount:${CLOUD_BUILD_SA}" \
  #   --role="roles/artifactregistry.writer" \
  #   --quiet 2>/dev/null || log "  (not found, OK)"

  log "Elevated roles removed."
fi

echo ""
log "Verify current bindings:"
log "  gcloud projects get-iam-policy ${PROJECT} --flatten='bindings[].members' --format='table(bindings.role,bindings.members)' | grep -E '(cloudbuild|compute)'"
