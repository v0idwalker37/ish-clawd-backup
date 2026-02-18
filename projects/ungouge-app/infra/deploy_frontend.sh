#!/usr/bin/env bash
set -euo pipefail

# deploy_frontend.sh
# Uses Vercel CLI (vercel) or API token to deploy the Next.js frontend and set environment variables.
# Requires: VERCEL_TOKEN environment variable or interactive login.

if ! command -v vercel >/dev/null 2>&1; then
  echo "Vercel CLI not installed. Install via 'npm i -g vercel' or use the Vercel web UI." >&2
  exit 1
fi

# Ensure you're in the frontend directory
cd "$(dirname "$0")/.." || exit 1
cd frontend || cd src || true

# Deploy preview or production
if [ "${VERCEL_ENV:-}" = "production" ]; then
  vercel --prod --token "$VERCEL_TOKEN"
else
  vercel --token "$VERCEL_TOKEN"
fi

# Example: Set env vars via Vercel CLI (interactive or token-based)
# vercel env add NEXT_PUBLIC_API_URL production
# vercel env add NEXT_PUBLIC_STRIPE_KEY production

echo "Frontend deploy triggered. If you prefer, set env vars in the Vercel dashboard or via 'vercel env' commands."