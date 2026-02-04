#!/bin/bash
# Deploy UnGouge Dashboard to Google Cloud Run

cd /Users/moltbot/clawd/projects/ungouge-dashboard/backend

echo "🔄 Deploying UnGouge Dashboard..."
echo "📝 Version: 3.0.0 (Server-side OAuth redirect flow)"
echo ""

# Check if GOOGLE_CLIENT_SECRET is set
if [ -z "$GOOGLE_CLIENT_SECRET" ]; then
    echo "⚠️  GOOGLE_CLIENT_SECRET not set in environment"
    echo "❌ Please set GOOGLE_CLIENT_SECRET before deploying:"
    echo "   export GOOGLE_CLIENT_SECRET='your-secret-here'"
    echo ""
    echo "Or set it in Cloud Run after deployment:"
    echo "   gcloud run services update ungouge-dashboard --region us-central1 \\"
    echo "     --set-env-vars GOOGLE_CLIENT_SECRET='your-secret-here'"
    exit 1
fi

gcloud run deploy ungouge-dashboard \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "GOOGLE_CLIENT_SECRET=$GOOGLE_CLIENT_SECRET"

echo ""
echo "✅ Deployment complete!"
echo "🌐 Test at: https://dashboard.ungouge.ai"
echo "🔐 OAuth flow: Click 'Sign in with Google' → Redirects to Google → Back to dashboard"
echo "📋 Check browser console (F12) for any errors"
