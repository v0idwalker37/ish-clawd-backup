# Backend Deployment

## THE RULE: Use `deploy.sh` - Nothing Else

**Always deploy backend using:**
```bash
cd ~/clawd/projects/ungouge-app/backend
./deploy.sh
```

**Why?** This script includes ALL required configuration:
- ✅ Email (Resend SMTP) - so receipts actually send
- ✅ Database (Cloud SQL) - so data persists
- ✅ Auth (JWT/CSRF) - so login works
- ✅ Payments (Stripe) - so checkout works
- ✅ AI (Gemini) - so analysis works

**DO NOT:**
- ❌ Use raw `gcloud run deploy` commands (will wipe email config)
- ❌ Use old deploy scripts in `/infra` (may be outdated)
- ❌ Deploy via Cloud Console UI (doesn't include secrets)

## What Gets Deployed

Every deployment includes these env vars and secrets:

**Environment Variables:**
- `EMAIL_DEV_MODE=false` - Email sending enabled
- `SMTP_HOST=smtp.resend.com`
- `SMTP_PORT=465`
- `SMTP_USER=resend`
- `FROM_EMAIL=noreply@ungouge.ai`
- `FRONTEND_URL=https://ungouge.ai`

**Secrets (from Secret Manager):**
- `SMTP_PASSWORD` → resend-api-key
- `DB_PASSWORD` → ungouge-db-password
- `JWT_SECRET_KEY` → JWT_SECRET_KEY
- `CSRF_SECRET_KEY` → CSRF_SECRET_KEY
- `ENCRYPTION_KEY` → ENCRYPTION_KEY
- `STRIPE_SECRET_KEY` → stripe-secret-key
- `STRIPE_WEBHOOK_SECRET` → stripe-webhook-secret
- `GOOGLE_GEMINI_API_KEY` → google-gemini-api-key

## If Secrets Are Missing

If a secret doesn't exist in Secret Manager, create it:

```bash
# Example: Create Resend API key
echo -n "re_YourAPIKey" | gcloud secrets create resend-api-key --data-file=-

# Grant Cloud Run access
PROJECT_NUMBER=$(gcloud projects describe ungouge-434620 --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding resend-api-key \
  --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## Quick Deploy

From anywhere in the project:
```bash
cd ~/clawd/projects/ungouge-app/backend && ./deploy.sh
```

That's it. Email, database, everything works.

## Why This Keeps Breaking

**The Problem:** When you deploy with raw `gcloud run deploy` commands, Cloud Run replaces ALL env vars and secrets with whatever you specify in that command. If you don't include email config, it gets wiped.

**The Solution:** `deploy.sh` ALWAYS includes everything. No more forgetting email config.

## Verification

After deploy, check email is configured:
```bash
gcloud run services describe ungouge-backend \
  --region=us-central1 \
  --format=yaml | grep -A 5 "EMAIL_DEV_MODE"
```

Should show:
```yaml
- name: EMAIL_DEV_MODE
  value: "false"
```

If it shows `true` or is missing, the deployment didn't use `deploy.sh`.

---

**Last Updated:** 2026-02-21  
**Purpose:** Stop the "email config disappeared again" cycle
