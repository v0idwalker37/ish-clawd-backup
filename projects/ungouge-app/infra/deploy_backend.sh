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

# Deploy with ALL required secrets and env vars
# This ensures email, database, Stripe, etc. are ALWAYS configured
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --add-cloudsql-instances ${PROJECT}:$REGION:ungouge-dashboard-db \
  --set-env-vars="EMAIL_DEV_MODE=false,SMTP_HOST=smtp.resend.com,SMTP_PORT=465,SMTP_USER=resend,FROM_EMAIL=noreply@ungouge.ai,FROM_NAME=UnGouge.ai,FRONTEND_URL=https://ungouge.ai" \
  --update-secrets="SMTP_PASSWORD=resend-api-key:latest,DB_PASSWORD=ungouge-db-password:latest,JWT_SECRET_KEY=JWT_SECRET_KEY:latest,CSRF_SECRET_KEY=CSRF_SECRET_KEY:latest,ENCRYPTION_KEY=ENCRYPTION_KEY:latest,STRIPE_SECRET_KEY=stripe-secret-key:latest,STRIPE_WEBHOOK_SECRET=stripe-webhook-secret:latest,GOOGLE_GEMINI_API_KEY=google-gemini-api-key:latest" \
  --project $PROJECT

echo ""
echo "✅ Deployment complete with all secrets and env vars configured"
echo "   - Email: Resend SMTP enabled"
echo "   - Database: Cloud SQL connected"
echo "   - Auth: JWT/CSRF configured"
echo "   - Payments: Stripe configured"
echo "   - AI: Gemini API configured"

echo "After deploy, run health checks against the /health endpoint and check logs:"
echo "  gcloud run services describe $SERVICE_NAME --region $REGION --platform managed --project $PROJECT"
echo "  gcloud logs read --project=$PROJECT --limit=50 --service=$SERVICE_NAME"
