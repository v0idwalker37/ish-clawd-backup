#!/usr/bin/env bash
set -euo pipefail

# deploy_backend.sh
# Build Docker image and deploy to Cloud Run. Requires gcloud authenticated and project set.

PROJECT=${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null || echo "")}
if [ -z "$PROJECT" ]; then
  echo "ERROR: No GCP project configured. Set PROJECT_ID or run 'gcloud config set project <PROJECT>'" >&2
  exit 1
fi

SERVICE_NAME=${SERVICE_NAME:-ungouge-backend}
REGION=${REGION:-us-central1}
IMAGE_TAG=${IMAGE_TAG:-$(git rev-parse --short HEAD || echo "manual")}
IMAGE=gcr.io/$PROJECT/$SERVICE_NAME:$IMAGE_TAG

echo "Building Docker image: $IMAGE"
docker build -t $IMAGE ..

echo "Authenticating Docker to gcr"
gcloud auth configure-docker --quiet

echo "Pushing image to GCR"
docker push $IMAGE

# Recommend: create secrets in Secret Manager (JWT_SECRET_KEY, CSRF_SECRET_KEY, ENCRYPTION_KEY, STRIPE keys, ungouge-db-password)
# Then deploy Cloud Run mapping secrets via --set-secrets

echo "Deploying to Cloud Run: $SERVICE_NAME"

gcloud run deploy $SERVICE_NAME \
  --image $IMAGE \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated=false \
  --add-cloudsql-instances ${PROJECT}:$REGION:ungouge-app-db \
  --project $PROJECT

echo "Deployment complete. To map secrets into Cloud Run, run (example):"
echo "  gcloud run services update $SERVICE_NAME --region $REGION --update-secrets \"
echo "    JWT_SECRET_KEY=projects/$PROJECT/secrets/JWT_SECRET_KEY:latest \"
echo "    CSRF_SECRET_KEY=projects/$PROJECT/secrets/CSRF_SECRET_KEY:latest \""

echo "After deploy, run health checks against the /health endpoint and check logs:"
echo "  gcloud run services describe $SERVICE_NAME --region $REGION --platform managed --project $PROJECT"
echo "  gcloud logs read --project=$PROJECT --limit=50 --service=$SERVICE_NAME"
