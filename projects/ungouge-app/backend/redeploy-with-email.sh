#!/usr/bin/env bash
# Redeploy current backend image with email env vars restored

set -euo pipefail

PROJECT_ID="ungouge-434620"
REGION="us-central1"
SERVICE="ungouge-backend"

# Get the current image (don't rebuild, just redeploy with email config)
CURRENT_IMAGE=$(gcloud run services describe $SERVICE \
  --region=$REGION \
  --format='value(spec.template.spec.containers[0].image)' 2>/dev/null)

echo "Current image: $CURRENT_IMAGE"
echo "Re-deploying with email configuration..."

# IMPORTANT: This assumes you have these secrets already created in Secret Manager:
# - resend-api-key (your Resend API key)
#
# If not created yet, run:
# echo -n "re_YourResendAPIKey" | gcloud secrets create resend-api-key --data-file=-

gcloud run deploy $SERVICE \
  --image=$CURRENT_IMAGE \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --set-env-vars="EMAIL_DEV_MODE=false,SMTP_HOST=smtp.resend.com,SMTP_PORT=465,SMTP_USER=resend,FROM_EMAIL=noreply@gougealert.com,FROM_NAME=GougeAlert" \
  --update-secrets="SMTP_PASSWORD=resend-api-key:latest"

echo ""
echo "✅ Backend redeployed with email configuration"
echo ""
echo "Test email by triggering another payment or run:"
echo "  gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=ungouge-backend\" --limit=50 --format=\"value(textPayload)\" | grep -i email"
