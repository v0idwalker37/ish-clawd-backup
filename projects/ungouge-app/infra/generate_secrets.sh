#!/usr/bin/env bash
set -euo pipefail

# generate_secrets.sh
# Generates production secrets locally into .env.prod (safe file perms)
# WARNING: Do NOT commit .env.prod. Upload to Secret Manager or Vercel envs.

if [ -f .env.prod ]; then
  echo ".env.prod already exists. Move it aside if you want to regenerate." >&2
  exit 1
fi

echo "Generating production secrets..."

JWT_SECRET_KEY=$(openssl rand -hex 32)
CSRF_SECRET_KEY=$(python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(32))
PY
)
ENCRYPTION_KEY=$(openssl rand -base64 32)

cat > .env.prod <<EOF
# Generated secrets — DO NOT COMMIT
JWT_SECRET_KEY=${JWT_SECRET_KEY}
CSRF_SECRET_KEY=${CSRF_SECRET_KEY}
ENCRYPTION_KEY=${ENCRYPTION_KEY}
EOF

chmod 600 .env.prod

echo "Done. .env.prod generated (600 perms)."
echo "Next: upload these values to Secret Manager or your deploy platform (Vercel/Cloud Run)."
echo "Example (gcloud):"
echo "  gcloud secrets create JWT_SECRET_KEY --data-file=<(echo -n \"$JWT_SECRET_KEY\") || true"
echo "  gcloud secrets create CSRF_SECRET_KEY --data-file=<(echo -n \"$CSRF_SECRET_KEY\") || true"
echo "  gcloud secrets create ENCRYPTION_KEY --data-file=<(echo -n \"$ENCRYPTION_KEY\") || true"

echo "Caveat: If you run the gcloud commands, make sure you're authenticated and have project set."