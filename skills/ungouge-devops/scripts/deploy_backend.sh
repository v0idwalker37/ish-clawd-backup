#!/bin/bash
#
# Backend deployment script for ungouge.ai
# Builds and deploys FastAPI backend to Google Cloud Run
#
# Usage:
#   ./deploy_backend.sh [environment]
#
# Arguments:
#   environment: production | staging (default: production)
#
# Requirements:
#   - gcloud CLI installed and authenticated
#   - Docker installed
#   - GCP_PROJECT_ID environment variable set
#   - Service account with Cloud Run Admin role

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT="${1:-production}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
BACKEND_DIR="${PROJECT_ROOT}/ungouge-backend"
GCP_PROJECT_ID="${GCP_PROJECT_ID:-}"
GCP_REGION="${GCP_REGION:-us-central1}"

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(production|staging)$ ]]; then
    echo -e "${RED}Error: Environment must be 'production' or 'staging'${NC}"
    exit 1
fi

# Check required tools
command -v docker >/dev/null 2>&1 || {
    echo -e "${RED}Error: docker is not installed${NC}"
    exit 1
}

command -v gcloud >/dev/null 2>&1 || {
    echo -e "${RED}Error: gcloud CLI is not installed${NC}"
    exit 1
}

# Check GCP_PROJECT_ID
if [ -z "$GCP_PROJECT_ID" ]; then
    echo -e "${RED}Error: GCP_PROJECT_ID environment variable not set${NC}"
    exit 1
fi

echo -e "${GREEN}=== Ungouge Backend Deployment ===${NC}"
echo "Environment: ${ENVIRONMENT}"
echo "Project ID:  ${GCP_PROJECT_ID}"
echo "Region:      ${GCP_REGION}"
echo ""

# Navigate to backend directory
cd "$BACKEND_DIR"

# Set service name based on environment
if [ "$ENVIRONMENT" == "production" ]; then
    SERVICE_NAME="ungouge-backend"
    IMAGE_TAG="gcr.io/${GCP_PROJECT_ID}/ungouge-backend:latest"
else
    SERVICE_NAME="ungouge-backend-staging"
    IMAGE_TAG="gcr.io/${GCP_PROJECT_ID}/ungouge-backend:staging"
fi

# Build Docker image
echo -e "${YELLOW}Building Docker image...${NC}"
docker build \
    --platform linux/amd64 \
    --tag "$IMAGE_TAG" \
    --file Dockerfile \
    .

# Push to Google Container Registry
echo -e "${YELLOW}Pushing image to GCR...${NC}"
docker push "$IMAGE_TAG"

# Deploy to Cloud Run
echo -e "${YELLOW}Deploying to Cloud Run...${NC}"

# Get current revision to preserve env vars
echo "Fetching current environment variables..."
ENV_VARS=$(gcloud run services describe "$SERVICE_NAME" \
    --project="$GCP_PROJECT_ID" \
    --region="$GCP_REGION" \
    --format="value(spec.template.spec.containers[0].env)" \
    2>/dev/null || echo "")

# Deploy with environment variables preserved
DEPLOY_CMD="gcloud run deploy ${SERVICE_NAME} \
    --image=${IMAGE_TAG} \
    --project=${GCP_PROJECT_ID} \
    --region=${GCP_REGION} \
    --platform=managed \
    --allow-unauthenticated \
    --memory=512Mi \
    --cpu=1 \
    --min-instances=0 \
    --max-instances=10 \
    --timeout=60s \
    --concurrency=80"

# Add environment variables if they exist
if [ -n "$ENV_VARS" ]; then
    DEPLOY_CMD="$DEPLOY_CMD --set-env-vars=${ENV_VARS}"
fi

eval "$DEPLOY_CMD"

# Get service URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --project="$GCP_PROJECT_ID" \
    --region="$GCP_REGION" \
    --format="value(status.url)")

echo ""
echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo -e "Service URL: ${GREEN}${SERVICE_URL}${NC}"
echo ""
echo "Health check: ${SERVICE_URL}/health"
echo ""

# Optionally run health check
read -p "Run health check? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Running health check...${NC}"
    if curl -f "${SERVICE_URL}/health" 2>/dev/null; then
        echo -e "${GREEN}✅ Health check passed!${NC}"
    else
        echo -e "${RED}❌ Health check failed!${NC}"
        exit 1
    fi
fi
