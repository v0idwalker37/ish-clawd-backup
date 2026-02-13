# UnGouge.ai — Pre-Launch Deploy Checklist

**Last updated:** 2026-02-13  
**Stack:** FastAPI (Python 3.11) + Next.js 14 + PostgreSQL + Stripe + GCP Cloud Run

---

## Table of Contents

1. [Pre-Deploy: Environment Variables](#1-pre-deploy-environment-variables)
2. [Database Setup & Migrations](#2-database-setup--migrations)
3. [Backend: Build & Deploy to GCP Cloud Run](#3-backend-build--deploy-to-gcp-cloud-run)
4. [Frontend: Deploy to Vercel](#4-frontend-deploy-to-vercel)
5. [DNS Configuration](#5-dns-configuration)
6. [SSL/TLS Verification](#6-ssltls-verification)
7. [CORS & Security Headers](#7-cors--security-headers)
8. [Stripe Production Setup](#8-stripe-production-setup)
9. [Email Service (SMTP)](#9-email-service-smtp)
10. [Health Checks & Monitoring](#10-health-checks--monitoring)
11. [Post-Deploy Verification](#11-post-deploy-verification)
12. [Rollback Procedure](#12-rollback-procedure)
13. [Launch Day Runbook](#13-launch-day-runbook)

---

## 1. Pre-Deploy: Environment Variables

Every env var is documented in `.env.production.example`. Copy it and fill in real values:

```bash
cp .env.production.example .env.production
```

### Backend (GCP Cloud Run / Secret Manager)

| Variable | Required | Description |
|----------|----------|-------------|
| `ENVIRONMENT` | ✅ | Must be `production` |
| `DATABASE_URL` | ✅ | PostgreSQL async URL: `postgresql+asyncpg://user:pass@host:5432/ungouge` |
| `DATABASE_ECHO` | ❌ | Set `false` for production (default) |
| `JWT_SECRET_KEY` | ✅ | 256-bit random key for JWT signing |
| `CSRF_SECRET_KEY` | ✅ | 256-bit random key for CSRF tokens |
| `FRONTEND_URL` | ✅ | `https://ungouge.ai` |
| `STRIPE_SECRET_KEY` | ✅ | `sk_live_...` (NOT `sk_test_`) |
| `STRIPE_WEBHOOK_SECRET` | ✅ | `whsec_...` from production webhook |
| `STRIPE_PUBLISHABLE_KEY` | ✅ | `pk_live_...` |
| `SMTP_HOST` | ✅ | e.g. `smtp.sendgrid.net` |
| `SMTP_PORT` | ✅ | e.g. `587` |
| `SMTP_USER` | ✅ | SMTP username |
| `SMTP_PASSWORD` | ✅ | SMTP password / API key |
| `EMAIL_DEV_MODE` | ✅ | Must be `false` for production |
| `OPENAI_API_KEY` | ✅ | For quote analysis (GPT) |
| `ANTHROPIC_API_KEY` | ❌ | For quote analysis (Claude) |
| `GOOGLE_API_KEY` | ❌ | For quote analysis (Gemini) |
| `ENCRYPTION_KEY` | ✅ | AES-256 key for PII field encryption |
| `VIRUSTOTAL_API_KEY` | ❌ | Optional malware scanning for uploads |
| `REDIS_URL` | ⚠️ | Recommended for rate limiting in multi-instance |

### Frontend (Vercel Environment Variables)

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | ✅ | `https://api.ungouge.ai` |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | ✅ | `pk_live_...` |

### Generate Secrets

```bash
# JWT secret (256-bit)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# CSRF secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Encryption key (AES-256)
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**⬜ All backend env vars set in GCP Secret Manager or Cloud Run config**  
**⬜ All frontend env vars set in Vercel project settings**  
**⬜ No test/dev keys in production config**  
**⬜ `EMAIL_DEV_MODE=false` confirmed**

---

## 2. Database Setup & Migrations

### PostgreSQL Provisioning

Use GCP Cloud SQL (PostgreSQL 15+) or any managed PostgreSQL:

```bash
# Create Cloud SQL instance (if using GCP)
gcloud sql instances create ungouge-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-east1 \
  --root-password=CHANGE_ME \
  --storage-auto-increase

# Create database
gcloud sql databases create ungouge --instance=ungouge-db

# Create service account user
gcloud sql users create ungouge-app \
  --instance=ungouge-db \
  --password=CHANGE_ME
```

### Connection String

```
# Standard format
postgresql+asyncpg://ungouge-app:PASSWORD@/ungouge?host=/cloudsql/PROJECT:REGION:ungouge-db

# Or via private IP
postgresql+asyncpg://ungouge-app:PASSWORD@PRIVATE_IP:5432/ungouge
```

### Schema Migration

The app uses SQLAlchemy `create_all` on startup (creates tables if they don't exist). For schema changes, use Alembic:

```bash
cd backend

# Initialize Alembic (if not already done)
alembic init alembic

# Generate migration from model changes
alembic revision --autogenerate -m "initial production schema"

# Apply migrations
alembic upgrade head
```

### Pending Migrations

- [ ] `is_restricted` column on `users` table (GDPR Art. 18)
- [ ] `privacy_preferences` JSON column on `users` table (GDPR Art. 21)
- [ ] Token blacklist table (auto-created on startup)

**⬜ PostgreSQL instance provisioned and accessible**  
**⬜ Database created with correct user/permissions**  
**⬜ Connection string tested from Cloud Run network**  
**⬜ Schema migrations applied successfully**  
**⬜ Backup schedule configured (daily automated backups)**

---

## 3. Backend: Build & Deploy to GCP Cloud Run

### Prerequisites

```bash
# Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable sqladmin.googleapis.com
```

### Build & Push Docker Image

```bash
cd ~/clawd/projects/ungouge-app

# Build image
docker build -t gcr.io/YOUR_PROJECT/ungouge-api:v1.0.0 -f Dockerfile .

# Push to GCR
docker push gcr.io/YOUR_PROJECT/ungouge-api:v1.0.0
```

### Deploy to Cloud Run

```bash
gcloud run deploy ungouge-api \
  --image=gcr.io/YOUR_PROJECT/ungouge-api:v1.0.0 \
  --platform=managed \
  --region=us-east1 \
  --port=8000 \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=1 \
  --max-instances=10 \
  --timeout=300 \
  --concurrency=80 \
  --allow-unauthenticated \
  --add-cloudsql-instances=YOUR_PROJECT:us-east1:ungouge-db \
  --set-env-vars="ENVIRONMENT=production" \
  --set-env-vars="FRONTEND_URL=https://ungouge.ai" \
  --set-env-vars="EMAIL_DEV_MODE=false" \
  --set-env-vars="DATABASE_ECHO=false" \
  --set-secrets="DATABASE_URL=ungouge-database-url:latest" \
  --set-secrets="JWT_SECRET_KEY=ungouge-jwt-secret:latest" \
  --set-secrets="CSRF_SECRET_KEY=ungouge-csrf-secret:latest" \
  --set-secrets="STRIPE_SECRET_KEY=ungouge-stripe-secret:latest" \
  --set-secrets="STRIPE_WEBHOOK_SECRET=ungouge-stripe-webhook-secret:latest" \
  --set-secrets="SMTP_USER=ungouge-smtp-user:latest" \
  --set-secrets="SMTP_PASSWORD=ungouge-smtp-password:latest" \
  --set-secrets="OPENAI_API_KEY=ungouge-openai-key:latest" \
  --set-secrets="ENCRYPTION_KEY=ungouge-encryption-key:latest"
```

### Store Secrets in GCP Secret Manager

```bash
# Create each secret
echo -n "YOUR_VALUE" | gcloud secrets create ungouge-jwt-secret --data-file=-
echo -n "YOUR_VALUE" | gcloud secrets create ungouge-csrf-secret --data-file=-
echo -n "YOUR_VALUE" | gcloud secrets create ungouge-stripe-secret --data-file=-
echo -n "YOUR_VALUE" | gcloud secrets create ungouge-stripe-webhook-secret --data-file=-
echo -n "YOUR_VALUE" | gcloud secrets create ungouge-smtp-user --data-file=-
echo -n "YOUR_VALUE" | gcloud secrets create ungouge-smtp-password --data-file=-
echo -n "YOUR_VALUE" | gcloud secrets create ungouge-openai-key --data-file=-
echo -n "YOUR_VALUE" | gcloud secrets create ungouge-encryption-key --data-file=-
echo -n "postgresql+asyncpg://..." | gcloud secrets create ungouge-database-url --data-file=-

# Grant Cloud Run access to secrets
gcloud secrets add-iam-policy-binding ungouge-jwt-secret \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT" \
  --role="roles/secretmanager.secretAccessor"
# (repeat for each secret)
```

**⬜ Docker image builds successfully**  
**⬜ Image pushed to GCR**  
**⬜ All secrets stored in Secret Manager**  
**⬜ Cloud Run service deployed and running**  
**⬜ Health check returns `healthy` at `/health`**  
**⬜ `min-instances=1` set (no cold-start for first user)**

---

## 4. Frontend: Deploy to Vercel

### Option A: Vercel (Recommended)

```bash
cd frontend

# Install Vercel CLI
npm i -g vercel

# Link project (first time)
vercel link

# Set environment variables
vercel env add NEXT_PUBLIC_API_URL        # → https://api.ungouge.ai
vercel env add NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY  # → pk_live_...

# Deploy to production
vercel --prod
```

### Option B: Cloudflare Pages

```bash
cd frontend

# Build
npm run build

# Deploy via Wrangler
npx wrangler pages deploy .next --project-name=ungouge
```

### Vercel Configuration

In `vercel.json` (create if needed):

```json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "regions": ["iad1"],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-Content-Type-Options", "value": "nosniff" }
      ]
    }
  ]
}
```

**⬜ Frontend builds without errors (`npm run build`)**  
**⬜ Environment variables set in Vercel dashboard**  
**⬜ Deployed and accessible at Vercel URL**  
**⬜ API proxy/rewrites confirmed working**  
**⬜ Custom domain configured (see DNS below)**

---

## 5. DNS Configuration

### Domain: `ungouge.ai`

| Record | Type | Name | Value | TTL |
|--------|------|------|-------|-----|
| Frontend | CNAME | `@` / `ungouge.ai` | `cname.vercel-dns.com` | 300 |
| Frontend (www) | CNAME | `www` | `cname.vercel-dns.com` | 300 |
| Backend API | CNAME | `api` | `ungouge-api-HASH.run.app` | 300 |

### For Vercel

1. Go to Vercel Dashboard → Project → Settings → Domains
2. Add `ungouge.ai` and `www.ungouge.ai`
3. Follow DNS instructions (add CNAME or A records)

### For Cloud Run Custom Domain

```bash
# Map custom domain to Cloud Run service
gcloud run domain-mappings create \
  --service=ungouge-api \
  --domain=api.ungouge.ai \
  --region=us-east1

# Get DNS records to add
gcloud run domain-mappings describe \
  --domain=api.ungouge.ai \
  --region=us-east1
```

**⬜ `ungouge.ai` → Vercel frontend**  
**⬜ `www.ungouge.ai` → redirect to `ungouge.ai`**  
**⬜ `api.ungouge.ai` → Cloud Run backend**  
**⬜ DNS propagation confirmed (use `dig` or `nslookup`)**  
**⬜ No conflicting records**

---

## 6. SSL/TLS Verification

Both Vercel and Cloud Run provide automatic SSL. Verify:

```bash
# Check frontend SSL
curl -I https://ungouge.ai
# Should show HTTP/2 200 and proper headers

# Check API SSL
curl -I https://api.ungouge.ai/health
# Should show HTTP/2 200 with HSTS header

# Check certificate details
echo | openssl s_client -servername ungouge.ai -connect ungouge.ai:443 2>/dev/null | openssl x509 -noout -dates -subject

# Check HSTS header
curl -sI https://api.ungouge.ai/health | grep -i strict-transport
# Should return: Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

**⬜ Frontend HTTPS works (valid cert)**  
**⬜ API HTTPS works (valid cert)**  
**⬜ HTTP → HTTPS redirect works (HTTPSRedirectMiddleware)**  
**⬜ HSTS header present on API responses**  
**⬜ Certificate auto-renewal confirmed (managed SSL)**

---

## 7. CORS & Security Headers

### Update CORS Origins

In `backend/main.py`, the production CORS is driven by `FRONTEND_URL` env var:

```python
cors_origins = [
    "http://localhost:3000",    # dev only
    "http://localhost:3001",    # dev only
]
production_url = os.getenv("FRONTEND_URL")  # https://ungouge.ai
if production_url and production_url not in cors_origins:
    cors_origins.append(production_url)
```

**Verify:** `FRONTEND_URL=https://ungouge.ai` is set in Cloud Run.

### Security Headers Checklist

The backend adds these automatically when `ENVIRONMENT=production`:

- [x] `X-Content-Type-Options: nosniff`
- [x] `X-Frame-Options: DENY`
- [x] `X-XSS-Protection: 1; mode=block`
- [x] `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`
- [x] `Content-Security-Policy: default-src 'self'; ...`

The frontend (`next.config.js`) adds:

- [x] `Content-Security-Policy` (with `connect-src` allowing `api.ungouge.ai`)
- [x] `X-Frame-Options: DENY`
- [x] `X-Content-Type-Options: nosniff`
- [x] `Referrer-Policy: strict-origin-when-cross-origin`
- [x] `Permissions-Policy: camera=(), microphone=(), geolocation=()`

### Verify Headers

```bash
# Backend headers
curl -sI https://api.ungouge.ai/health | grep -iE "x-frame|x-content|strict-transport|content-security|x-xss"

# Frontend headers
curl -sI https://ungouge.ai | grep -iE "x-frame|x-content|referrer|permissions|content-security"
```

**⬜ CORS allows `https://ungouge.ai` only (no wildcards)**  
**⬜ All security headers present on both frontend and backend**  
**⬜ CSP `connect-src` includes `https://api.ungouge.ai`**  
**⬜ Cookies set with `Secure`, `HttpOnly`, `SameSite=Strict`**

---

## 8. Stripe Production Setup

### Switch to Live Keys

1. Go to [Stripe Dashboard](https://dashboard.stripe.com) → toggle to **Live mode**
2. Get live keys: `sk_live_...` and `pk_live_...`
3. Update env vars (both backend and frontend)

### Create Production Webhook

1. Stripe Dashboard → Developers → Webhooks → Add endpoint
2. **Endpoint URL:** `https://api.ungouge.ai/api/payments/webhook`
3. **Events to listen for:**
   - `checkout.session.completed`
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
4. Copy the **Signing secret** (`whsec_...`) → set as `STRIPE_WEBHOOK_SECRET`

### Test Webhook

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Test webhook locally (dev)
stripe listen --forward-to localhost:8000/api/payments/webhook

# Trigger a test event
stripe trigger checkout.session.completed
```

### Production Verification

```bash
# Verify webhook is reachable
curl -X POST https://api.ungouge.ai/api/payments/webhook \
  -H "Content-Type: application/json" \
  -d '{}'
# Should return 400 "Missing Stripe-Signature header" (expected — means endpoint is live)
```

**⬜ Live Stripe keys set (`sk_live_`, `pk_live_`)**  
**⬜ Production webhook endpoint created in Stripe Dashboard**  
**⬜ Webhook signing secret set in backend env**  
**⬜ Test payment completed successfully ($19.99)**  
**⬜ Webhook fires and payment record created in DB**  
**⬜ Report generated after successful payment**  
**⬜ Stripe Radar enabled for fraud detection**

---

## 9. Email Service (SMTP)

The app sends:
- Email verification (registration)
- Password reset links
- MFA OTP codes

### Configure SMTP

Recommended providers: **SendGrid**, **AWS SES**, **Mailgun**, **Postmark**

```bash
# SendGrid example
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=SG.your-sendgrid-api-key
EMAIL_DEV_MODE=false   # ⚠️ MUST be false for production
```

### Verify Email Delivery

```bash
# Test from Python
python -c "
import smtplib
from email.mime.text import MIMEText
msg = MIMEText('Test from UnGouge.ai')
msg['Subject'] = 'SMTP Test'
msg['From'] = 'noreply@ungouge.ai'
msg['To'] = 'your-test-email@example.com'
with smtplib.SMTP('smtp.sendgrid.net', 587) as s:
    s.starttls()
    s.login('apikey', 'YOUR_KEY')
    s.send_message(msg)
    print('Sent!')
"
```

**⬜ SMTP credentials configured**  
**⬜ `EMAIL_DEV_MODE=false`**  
**⬜ Test email sent and received**  
**⬜ SPF/DKIM/DMARC records added for `ungouge.ai`**  
**⬜ `noreply@ungouge.ai` as sender address**

---

## 10. Health Checks & Monitoring

### Health Check Endpoints

| Endpoint | Purpose | Expected Response |
|----------|---------|-------------------|
| `GET /health` | Basic health + DB check | `{"status":"healthy","database":"healthy","version":"1.0.0"}` |
| `GET /health/ready` | Readiness probe (DB connection) | `{"ready":true,"database":"connected"}` |
| `GET /health/live` | Liveness probe | `{"alive":true}` |
| `GET /api/health/detailed` | Full status (uptime, version, checks) | Detailed JSON |

### Cloud Run Health Check Config

```bash
gcloud run services update ungouge-api \
  --region=us-east1 \
  --startup-cpu-boost \
  --liveness-probe \
    --liveness-probe-path=/health/live \
    --liveness-probe-period=30 \
    --liveness-probe-failure-threshold=3 \
    --liveness-probe-initial-delay=10
```

### Monitoring Setup

1. **GCP Cloud Monitoring:**
   - Cloud Run request latency (alert if p99 > 5s)
   - Cloud Run error rate (alert if > 5% over 5 min)
   - Cloud SQL CPU/memory/connections
   - Cloud Run instance count

2. **Uptime Checks:**
   ```bash
   # Create uptime check
   gcloud monitoring uptime-check-configs create \
     --display-name="UnGouge API Health" \
     --resource-type=uptime-url \
     --hostname=api.ungouge.ai \
     --path=/health \
     --check-interval=300
   ```

3. **Alerting:**
   - Email/Slack/PagerDuty on health check failures
   - Alert on 5xx error rate > 1%
   - Alert on response time p95 > 3s
   - Alert on Cloud SQL storage > 80%

4. **Logging:**
   - Backend uses structured JSON logging (`python-json-logger`)
   - Security events logged via `SecurityAuditMiddleware`
   - View logs: `gcloud run services logs read ungouge-api --region=us-east1`

**⬜ Health endpoints responding correctly**  
**⬜ Cloud Run liveness/readiness probes configured**  
**⬜ Uptime monitoring enabled**  
**⬜ Alerting configured (email/Slack)**  
**⬜ Log Explorer queries saved for common issues**

---

## 11. Post-Deploy Verification

Run through this checklist after deployment:

### API Smoke Tests

```bash
BASE=https://api.ungouge.ai

# 1. Root endpoint
curl -s $BASE/ | jq .
# Expected: {"message":"Ungouge.ai API","version":"1.0.0","docs":"/docs"}

# 2. Health check
curl -s $BASE/health | jq .
# Expected: {"status":"healthy","database":"healthy",...}

# 3. Readiness
curl -s $BASE/health/ready | jq .
# Expected: {"ready":true,...}

# 4. Register a test user
curl -s -X POST $BASE/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123!","name":"Test User"}' | jq .

# 5. Login
curl -s -X POST $BASE/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123!"}' | jq .

# 6. HTTPS redirect (should 301/307 to HTTPS)
curl -sI http://api.ungouge.ai/health

# 7. CORS preflight
curl -sI -X OPTIONS $BASE/api/auth/login \
  -H "Origin: https://ungouge.ai" \
  -H "Access-Control-Request-Method: POST" | grep -i "access-control"

# 8. Rate limiting (hit it 6+ times quickly)
for i in {1..7}; do
  curl -s -o /dev/null -w "%{http_code}\n" -X POST $BASE/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com","password":"wrong"}'
done
# Last requests should return 429

# 9. Stripe webhook endpoint reachable
curl -s -X POST $BASE/api/payments/webhook -d '{}' -w "\n%{http_code}"
# Expected: 400 (Missing Stripe-Signature — correct behavior)
```

### Frontend Smoke Tests

```bash
# 1. Homepage loads
curl -sI https://ungouge.ai
# Expected: HTTP/2 200

# 2. Security headers present
curl -sI https://ungouge.ai | grep -iE "x-frame|csp|referrer"

# 3. API proxy works (if using Next.js rewrites)
curl -s https://ungouge.ai/api/health | jq .
```

### End-to-End Flow

- [ ] Visit `https://ungouge.ai` — homepage loads
- [ ] Register a new account — email verification sent
- [ ] Login with credentials — JWT cookie set
- [ ] Submit a quote (manual entry) — quote saved
- [ ] Click "Get Analysis" → Stripe Checkout opens
- [ ] Complete test payment ($19.99) — report generated
- [ ] View analysis report — all data renders
- [ ] Logout — cookies cleared, token blacklisted
- [ ] Password reset flow — email received, password changed

**⬜ All API smoke tests pass**  
**⬜ Frontend loads and renders correctly**  
**⬜ Full user flow (register → pay → report) works**  
**⬜ Mobile responsive check**  
**⬜ Error pages work (404, 500)**

---

## 12. Rollback Procedure

### Backend Rollback (Cloud Run)

```bash
# List revisions
gcloud run revisions list --service=ungouge-api --region=us-east1

# Rollback to previous revision
gcloud run services update-traffic ungouge-api \
  --to-revisions=ungouge-api-PREVIOUS_REVISION=100 \
  --region=us-east1

# Or deploy the previous image tag
gcloud run deploy ungouge-api \
  --image=gcr.io/YOUR_PROJECT/ungouge-api:v0.9.0 \
  --region=us-east1
```

### Frontend Rollback (Vercel)

```bash
# List deployments
vercel ls

# Promote a previous deployment to production
vercel promote DEPLOYMENT_URL
```

### Database Rollback

```bash
# Alembic downgrade
cd backend
alembic downgrade -1   # Roll back one revision
alembic downgrade BASE # Roll back to beginning (DANGEROUS)

# Or restore from backup (Cloud SQL)
gcloud sql backups list --instance=ungouge-db
gcloud sql backups restore BACKUP_ID --restore-instance=ungouge-db
```

### Emergency Kill Switch

```bash
# Immediately stop serving traffic
gcloud run services update-traffic ungouge-api \
  --to-revisions=KNOWN_GOOD_REVISION=100 \
  --region=us-east1

# Or scale to zero (blocks all traffic)
gcloud run services update ungouge-api \
  --max-instances=0 \
  --region=us-east1
```

**⬜ Rollback procedure tested in staging**  
**⬜ Previous revision identified and accessible**  
**⬜ Database backup verified and restorable**

---

## 13. Launch Day Runbook

### T-24h (Day Before)

- [ ] All env vars set and verified
- [ ] Database provisioned and migrated
- [ ] Staging environment fully tested
- [ ] Stripe webhook tested with live keys
- [ ] Email delivery confirmed
- [ ] DNS TTL lowered to 300s
- [ ] Team notified of launch window

### T-1h (One Hour Before)

- [ ] Final `git pull` and verify commit hash
- [ ] Build Docker image with release tag
- [ ] Run smoke tests against staging
- [ ] Confirm monitoring/alerting is active
- [ ] Open Stripe dashboard, GCP console, Vercel dashboard

### T-0 (Deploy)

1. **Deploy backend:**
   ```bash
   docker build -t gcr.io/PROJECT/ungouge-api:v1.0.0 .
   docker push gcr.io/PROJECT/ungouge-api:v1.0.0
   gcloud run deploy ungouge-api --image=gcr.io/PROJECT/ungouge-api:v1.0.0 ...
   ```

2. **Verify backend:**
   ```bash
   curl https://api.ungouge.ai/health
   ```

3. **Deploy frontend:**
   ```bash
   cd frontend && vercel --prod
   ```

4. **Verify frontend:**
   ```bash
   curl -I https://ungouge.ai
   ```

5. **Run full smoke test suite** (Section 11)

6. **Make a test purchase** (real $19.99 — refund after)

### T+1h (Post-Launch)

- [ ] Monitor error rates in GCP Console
- [ ] Check Stripe dashboard for successful payments
- [ ] Verify email delivery (registration, password reset)
- [ ] Check logs for any errors: `gcloud run services logs read ungouge-api`
- [ ] Test from mobile device
- [ ] Test from different browser

### T+24h (Day After)

- [ ] Review error logs
- [ ] Check database size and performance
- [ ] Verify daily cleanup task ran (data retention)
- [ ] Confirm backup was created
- [ ] Update DNS TTL back to 3600s
- [ ] Delete test accounts and refund test payments

---

## Quick Reference: Service URLs

| Service | URL |
|---------|-----|
| Frontend | `https://ungouge.ai` |
| API | `https://api.ungouge.ai` |
| API Docs | `https://api.ungouge.ai/docs` |
| Health | `https://api.ungouge.ai/health` |
| Stripe Dashboard | `https://dashboard.stripe.com` |
| GCP Console | `https://console.cloud.google.com` |
| Vercel Dashboard | `https://vercel.com/dashboard` |

---

*Last reviewed: 2026-02-13 — Ish*
