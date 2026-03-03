#!/usr/bin/env bash
# Backend deployment script - ALWAYS includes email, database, and all secrets
# This is the ONLY script you should use to deploy the backend
set -euo pipefail

PROJECT_ID="ungouge-434620"
REGION="us-central1"
SERVICE="ungouge-backend"

echo "📦 Building Docker image..."
cd "$(dirname "$0")"
IMAGE_TAG=$(git rev-parse --short HEAD 2>/dev/null || echo "manual")
IMAGE="gcr.io/$PROJECT_ID/$SERVICE:$IMAGE_TAG"

docker build -t "$IMAGE" .

echo "☁️  Pushing to Google Container Registry..."
gcloud auth configure-docker --quiet
docker push "$IMAGE"

echo "🚀 Deploying to Cloud Run with ALL configuration..."
gcloud run deploy $SERVICE \
  --image="$IMAGE" \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --add-cloudsql-instances="$PROJECT_ID:$REGION:ungouge-dashboard-db" \
  --set-env-vars="EMAIL_DEV_MODE=false,SMTP_HOST=smtp.resend.com,SMTP_PORT=465,SMTP_USER=resend,FROM_EMAIL=noreply@gougealert.com,FROM_NAME=GougeAlert,FRONTEND_URL=https://gougealert.com" \
  --update-secrets="SMTP_PASSWORD=resend-api-key:latest,DB_PASSWORD=ungouge-db-password:latest,JWT_SECRET_KEY=JWT_SECRET_KEY:latest,CSRF_SECRET_KEY=CSRF_SECRET_KEY:latest,ENCRYPTION_KEY=ENCRYPTION_KEY:latest,STRIPE_SECRET_KEY=stripe-secret-key:latest,STRIPE_WEBHOOK_SECRET=stripe-webhook-secret:latest,GOOGLE_GEMINI_API_KEY=google-gemini-api-key:latest" \
  --project=$PROJECT_ID

echo ""
echo "✅ Deployment complete!"
echo "   📧 Email: ENABLED (Resend SMTP)"
echo "   💾 Database: CONNECTED (Cloud SQL)"
echo "   🔐 Auth: CONFIGURED (JWT/CSRF)"
echo "   💳 Payments: CONFIGURED (Stripe)"
echo "   🤖 AI: CONFIGURED (Gemini)"
echo ""
echo "🔍 Check deployment:"
echo "   gcloud run services describe $SERVICE --region=$REGION"
echo ""
echo "📋 View logs:"
echo "   gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE\" --limit=50"
