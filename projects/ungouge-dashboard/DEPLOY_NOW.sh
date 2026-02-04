#!/bin/bash
# Force complete rebuild

cd /Users/moltbot/clawd/projects/ungouge-dashboard/backend

echo "🔄 Deploying UnGouge Dashboard..."
echo "📝 Version: 2.4.1 (syntax fix + cache bust)"
echo ""

gcloud run deploy ungouge-dashboard \
  --source . \
  --region us-central1 \
  --allow-unauthenticated

echo ""
echo "✅ Deployment complete!"
echo "🌐 Test at: https://dashboard.ungouge.ai"
echo "🔍 IMPORTANT: Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)"
echo "📋 Check browser console (F12) for errors"
