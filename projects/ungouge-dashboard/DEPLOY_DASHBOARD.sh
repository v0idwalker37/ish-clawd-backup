#!/bin/bash
# ============================================================
# UnGouge Dashboard - One-Click Deploy Script
# ============================================================
# Run this AFTER: gcloud auth login (complete browser sign-in)
# 
# Usage: ./DEPLOY_DASHBOARD.sh
# ============================================================

set -e

BACKEND_DIR="/Users/moltbot/clawd/projects/ungouge-dashboard/backend"
SERVICE="ungouge-dashboard"
REGION="us-central1"
PROJECT="ungouge-dashboard"

echo "🚀 UnGouge Dashboard Deploy"
echo "================================"
echo ""

# Step 1: Verify gcloud auth
echo "📋 Step 1: Checking gcloud auth..."
if ! gcloud auth print-access-token &>/dev/null; then
    echo "❌ gcloud auth is not valid. Please run:"
    echo "   gcloud auth login"
    echo ""
    echo "Complete the browser sign-in, then re-run this script."
    exit 1
fi
echo "✅ Auth OK ($(gcloud config get-value account 2>/dev/null))"

# Step 2: Set project
echo ""
echo "📋 Step 2: Setting project..."
gcloud config set project "$PROJECT" 2>/dev/null
echo "✅ Project: $PROJECT"

# Step 3: Load env vars
echo ""
echo "📋 Step 3: Loading environment variables..."
ENV_FILE="$BACKEND_DIR/.env.cloudrun"
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Missing $ENV_FILE"
    exit 1
fi

# Build env vars string for gcloud (KEY=VALUE,KEY=VALUE)
ENV_VARS=""
while IFS= read -r line; do
    # Skip comments and empty lines
    [[ "$line" =~ ^#.*$ ]] && continue
    [[ -z "$line" ]] && continue
    if [ -z "$ENV_VARS" ]; then
        ENV_VARS="$line"
    else
        ENV_VARS="$ENV_VARS,$line"
    fi
done < "$ENV_FILE"

echo "✅ Environment variables loaded"

# Step 4: Deploy
echo ""
echo "📋 Step 4: Deploying to Cloud Run..."
echo "   Service: $SERVICE"
echo "   Region:  $REGION"
echo "   Source:   $BACKEND_DIR"
echo ""

cd "$BACKEND_DIR"

gcloud run deploy "$SERVICE" \
    --source . \
    --region "$REGION" \
    --allow-unauthenticated \
    --set-env-vars "$ENV_VARS" \
    --add-cloudsql-instances "ungouge-dashboard:us-central1:ungouge-dashboard-db" \
    --memory 256Mi \
    --cpu 1 \
    --timeout 60 \
    --max-instances 2 \
    --min-instances 0

echo ""
echo "📋 Step 5: Verifying deployment..."

# Get the URL
URL=$(gcloud run services describe "$SERVICE" --region "$REGION" --format 'value(status.url)' 2>/dev/null)
echo "✅ Service URL: $URL"

# Get revision
REVISION=$(gcloud run revisions list --service "$SERVICE" --region "$REGION" --limit 1 --format 'value(REVISION)' 2>/dev/null)
echo "✅ Active revision: $REVISION"

# Health check
echo ""
echo "📋 Step 6: Health check..."
HEALTH=$(curl -s "$URL/api/health" 2>/dev/null)
echo "   Response: $HEALTH"

echo ""
echo "================================"
echo "🎉 DEPLOYMENT COMPLETE!"
echo ""
echo "🌐 Dashboard: https://dashboard.ungouge.ai"
echo "🔧 Direct URL: $URL"
echo "📦 Revision: $REVISION"
echo ""
echo "Next steps:"
echo "1. Open https://dashboard.ungouge.ai in browser"
echo "2. Sign in with Google (void@ungouge.ai)"
echo "3. Verify projects and tasks load correctly"
echo "4. Test category filtering (All / UnGouge / YouTube)"
echo "================================"
