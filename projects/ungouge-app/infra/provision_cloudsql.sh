#!/usr/bin/env bash
set -euo pipefail

# provision_cloudsql.sh
# Idempotent-ish script to create a Cloud SQL Postgres instance, create DB + user,
# and store DB password in Secret Manager. Run locally where gcloud is installed and
# authenticated (gcloud auth login or service account).

# Configuration (override via env vars)
PROJECT=${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null || echo "")}
if [ -z "$PROJECT" ]; then
  echo "ERROR: No GCP project configured. Set PROJECT_ID or run 'gcloud config set project <PROJECT>'" >&2
  exit 1
fi

INSTANCE_NAME=${INSTANCE_NAME:-ungouge-app-db}
REGION=${REGION:-us-central1}
DB_VERSION=${DB_VERSION:-POSTGRES_15}
TIER=${TIER:-db-f1-micro}
DB_NAME=${DB_NAME:-ungouge_app}
DB_USER=${DB_USER:-ungouge_admin}
SECRET_NAME=${SECRET_NAME:-ungouge-db-password}
SERVICE_ACCOUNT=${SERVICE_ACCOUNT:-}   # optional: service account email to grant roles to
SKIP_IAM=${SKIP_IAM:-false}            # set to true to skip IAM grants

# Ensure gcloud is available
if ! command -v gcloud >/dev/null 2>&1; then
  echo "ERROR: gcloud CLI not found. Install and authenticate locally: https://cloud.google.com/sdk/docs/install" >&2
  exit 1
fi

echo "Project: $PROJECT"

echo "Enabling required Google Cloud APIs (sqladmin, secretmanager) if needed..."
# Enable required APIs (idempotent)
gcloud services enable sqladmin.googleapis.com secretmanager.googleapis.com --project "$PROJECT" || {
  echo "Warning: failed to enable one or more APIs. You may need to enable them in the Cloud Console or check permissions." >&2
}

echo "Creating Cloud SQL instance: $INSTANCE_NAME ($DB_VERSION, $TIER) in $REGION"

# Create instance if it doesn't exist
if ! gcloud sql instances describe "$INSTANCE_NAME" --project "$PROJECT" >/dev/null 2>&1; then
  gcloud sql instances create "$INSTANCE_NAME" \
    --database-version="$DB_VERSION" \
    --tier="$TIER" \
    --region="$REGION" \
    --project="$PROJECT"
else
  echo "Instance $INSTANCE_NAME already exists — skipping creation"
fi

# Wait for instance to become RUNNABLE (up to ~5 minutes)
echo "Waiting for Cloud SQL instance to reach RUNNABLE state..."
for i in {1..60}; do
  state=$(gcloud sql instances describe "$INSTANCE_NAME" --project="$PROJECT" --format="value(state)" || echo "ERROR")
  if [ "$state" = "RUNNABLE" ]; then
    echo "Instance is RUNNABLE"
    break
  fi
  if [ "$state" = "ERROR" ]; then
    echo "ERROR: instance in ERROR state. Run 'gcloud sql operations list --instance=$INSTANCE_NAME --project=$PROJECT' to inspect." >&2
    exit 1
  fi
  echo -n "."
  sleep 5
  if [ $i -eq 60 ]; then
    echo "\nERROR: timeout waiting for instance to become RUNNABLE (5min). Check Cloud Console for details." >&2
    exit 1
  fi
done

# Create database if missing
if ! gcloud sql databases describe "$DB_NAME" --instance="$INSTANCE_NAME" --project="$PROJECT" >/dev/null 2>&1; then
  gcloud sql databases create "$DB_NAME" --instance="$INSTANCE_NAME" --project="$PROJECT"
else
  echo "Database $DB_NAME already exists — skipping"
fi

# Generate a strong password (openssl -> python3 -> fallback)
if command -v openssl >/dev/null 2>&1; then
  DB_PASS=$(openssl rand -hex 16)
elif command -v python3 >/dev/null 2>&1; then
  DB_PASS=$(python3 -c 'import secrets; print(secrets.token_hex(16))')
else
  DB_PASS=$(head -c 32 /dev/urandom | base64 | tr -dc 'A-Za-z0-9' | head -c 32)
fi

# Create or update user (Postgres: do NOT use a host parameter)
if ! gcloud sql users describe "$DB_USER" --instance="$INSTANCE_NAME" --project="$PROJECT" >/dev/null 2>&1; then
  gcloud sql users create "$DB_USER" --instance="$INSTANCE_NAME" --password="$DB_PASS" --project="$PROJECT"
else
  echo "User $DB_USER already exists — updating password"
  gcloud sql users set-password "$DB_USER" --instance="$INSTANCE_NAME" --password="$DB_PASS" --project="$PROJECT"
fi

# Store password in Secret Manager (create secret if needed; add new version otherwise)
if ! gcloud secrets describe "$SECRET_NAME" --project "$PROJECT" >/dev/null 2>&1; then
  echo -n "$DB_PASS" | gcloud secrets create "$SECRET_NAME" --data-file=- --project="$PROJECT"
else
  echo -n "$DB_PASS" | gcloud secrets versions add "$SECRET_NAME" --data-file=- --project="$PROJECT"
fi

# Optionally grant IAM roles to a Cloud Run service account
if [ -n "$SERVICE_ACCOUNT" ] && [ "${SKIP_IAM,,}" != "true" ]; then
  echo "Granting roles to $SERVICE_ACCOUNT"
  gcloud projects add-iam-policy-binding "$PROJECT" \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/cloudsql.client" \
    --project="$PROJECT"

  gcloud secrets add-iam-policy-binding "$SECRET_NAME" \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor" \
    --project="$PROJECT"
fi

CONN_NAME=$(gcloud sql instances describe "$INSTANCE_NAME" --project="$PROJECT" --format='value(connectionName)')

echo "\nCloud SQL provisioning complete."
echo "Secret stored as projects/$PROJECT/secrets/$SECRET_NAME"
echo "Cloud SQL connection name: $CONN_NAME"

echo "Example Cloud Run deploy (replace placeholders):"
echo "gcloud run deploy <SERVICE> --image=<IMAGE> --region=$REGION --add-cloudsql-instances=$CONN_NAME --set-secrets=DB_PASS=projects/$PROJECT/secrets/$SECRET_NAME:latest --service-account=<$SERVICE_ACCOUNT>"

echo "Notes:"
echo " - Do NOT commit secrets or plaintext passwords to git. Secret Manager is used above." 
echo " - Rotate passwords periodically. To rotate, run this script again (it adds a new secret version)."
echo " - If you prefer Private IP, set up a VPC peering and recreate the instance with private network settings (not handled by this script)."
