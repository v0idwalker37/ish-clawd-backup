# Deployment Guide

Complete guide for deploying Ungouge.ai v2 to staging and production environments.

---

## Prerequisites

- **Google Cloud Platform account** with billing enabled
- **GitHub account** with repository access
- **Terraform** 1.9+ installed locally
- **gcloud CLI** installed and authenticated
- **Docker** installed locally
- **GitHub Actions** secrets configured

---

## Initial Setup

### 1. GCP Project Configuration

```bash
# Set project ID
export GCP_PROJECT_ID=gen-lang-client-0199462206

# Authenticate
gcloud auth login
gcloud config set project $GCP_PROJECT_ID

# Enable required APIs (already in Terraform, but can enable manually)
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  storage.googleapis.com \
  pubsub.googleapis.com \
  secretmanager.googleapis.com \
  vision.googleapis.com \
  vpcaccess.googleapis.com
```

### 2. Create GCS Buckets for Terraform State

```bash
# Staging
gsutil mb -p $GCP_PROJECT_ID -l us-central1 gs://ungouge-terraform-state-staging
gsutil versioning set on gs://ungouge-terraform-state-staging

# Production
gsutil mb -p $GCP_PROJECT_ID -l us-central1 gs://ungouge-terraform-state-production
gsutil versioning set on gs://ungouge-terraform-state-production
```

### 3. Create Service Account for CI/CD

```bash
# Create service account
gcloud iam service-accounts create ungouge-github-actions \
  --display-name="Ungouge GitHub Actions"

# Grant permissions
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member="serviceAccount:ungouge-github-actions@$GCP_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member="serviceAccount:ungouge-github-actions@$GCP_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member="serviceAccount:ungouge-github-actions@$GCP_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# Create key
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=ungouge-github-actions@$GCP_PROJECT_ID.iam.gserviceaccount.com

# Copy key content to GitHub Secrets as GCP_SERVICE_ACCOUNT_KEY
cat github-actions-key.json

# Delete local key file (sensitive!)
rm github-actions-key.json
```

### 4. Configure GitHub Secrets

Go to GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:

| Secret Name | Value |
|-------------|-------|
| `GCP_SERVICE_ACCOUNT_KEY` | Contents of `github-actions-key.json` |
| `STRIPE_SECRET_KEY_STAGING` | Stripe test mode secret key |
| `STRIPE_SECRET_KEY_PRODUCTION` | Stripe live mode secret key |
| `STRIPE_WEBHOOK_SECRET_STAGING` | Stripe webhook secret (test) |
| `STRIPE_WEBHOOK_SECRET_PRODUCTION` | Stripe webhook secret (live) |
| `SLACK_WEBHOOK_URL` | Slack webhook for deployment notifications |

### 5. Store Secrets in Secret Manager

```bash
# JWT secret
echo -n "$(openssl rand -base64 32)" | \
  gcloud secrets create jwt-secret --data-file=-

# Stripe keys (staging)
echo -n "sk_test_..." | \
  gcloud secrets create stripe-secret-staging --data-file=-

echo -n "whsec_..." | \
  gcloud secrets create stripe-webhook-secret-staging --data-file=-

# Stripe keys (production)
echo -n "sk_live_..." | \
  gcloud secrets create stripe-secret-production --data-file=-

echo -n "whsec_..." | \
  gcloud secrets create stripe-webhook-secret-production --data-file=-
```

---

## Staging Deployment

### Option 1: Automatic (via Git)

**Triggers:** Push to `develop` branch

```bash
git checkout develop
git pull
git merge feature/my-feature
git push origin develop
```

GitHub Actions will:
1. Run linting & tests
2. Build Docker images
3. Push to GCR
4. Apply Terraform
5. Run smoke tests
6. Notify Slack

**Monitor:** https://github.com/v0idwalker37/ish-clawd-backup/actions

---

### Option 2: Manual (via Terraform)

```bash
cd infra/terraform/environments/staging

# Initialize
terraform init

# Review plan
terraform plan

# Apply changes
terraform apply

# Get outputs
terraform output api_gateway_url
```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] All tests passing in staging
- [ ] Smoke tests verified
- [ ] Database backup completed
- [ ] Change request approved
- [ ] Rollback plan documented
- [ ] On-call engineer notified
- [ ] Maintenance window scheduled (if needed)

### Deployment Steps

1. **Merge to main**

```bash
git checkout main
git pull
git merge develop
git push origin main
```

2. **GitHub Actions triggers** (requires manual approval)
   - Builds images
   - Plans Terraform changes
   - **PAUSES for approval**

3. **Review & Approve**
   - Go to GitHub Actions
   - Review Terraform plan
   - Click "Approve" if safe

4. **Automated steps continue:**
   - Applies Terraform
   - Runs smoke tests
   - Monitors error rates
   - Notifies Slack

---

## Database Migrations

### Staging

```bash
cd services/database

# Review migration
cat alembic/versions/001_initial_schema.sql

# Apply migration
./migrate.sh staging
```

### Production

```bash
# Create backup first!
gcloud sql export sql ungouge-db-production \
  gs://ungouge-backups/backup_$(date +%Y%m%d_%H%M%S).sql \
  --database=ungouge

# Apply migration (requires confirmation)
./migrate.sh production
```

---

## Rollback Procedures

### Service Rollback (Cloud Run)

```bash
# List revisions
gcloud run revisions list --service=api-gateway-production --region=us-central1

# Route traffic to previous revision
gcloud run services update-traffic api-gateway-production \
  --to-revisions=api-gateway-production-00042-xyz=100 \
  --region=us-central1
```

### Database Rollback

```bash
# Restore from backup
gcloud sql import sql ungouge-db-production \
  gs://ungouge-backups/backup_20260217_150000.sql \
  --database=ungouge
```

### Terraform Rollback

```bash
cd infra/terraform/environments/production

# Revert to previous state
terraform state pull > current-state.json
terraform state push previous-state.json

# Apply old configuration
git checkout <previous-commit>
terraform apply
```

---

## Monitoring Deployment

### Health Checks

```bash
# Staging
curl https://staging.ungouge.ai/health/ready

# Production
curl https://api.ungouge.ai/health/ready
```

### View Logs

```bash
# Cloud Run logs
gcloud run services logs read api-gateway-production \
  --region=us-central1 \
  --limit=50

# Or in console
https://console.cloud.google.com/logs/query
```

### Check Metrics

```bash
# Error rate
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/request_count"'

# Latency
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/request_latencies"'
```

---

## Disaster Recovery

### Full System Failure

1. **Restore database from backup**
2. **Redeploy services from known-good commit**
3. **Verify all health checks**
4. **Run smoke tests**
5. **Monitor for 30 minutes**

### Data Loss

- Database backups: 30 days retention
- Point-in-time recovery: 7 days
- Transaction logs: Binary log enabled

### RTO/RPO Targets

| Metric | Target | Current |
|--------|--------|---------|
| **RTO** (Recovery Time Objective) | <4 hours | TBD |
| **RPO** (Recovery Point Objective) | <1 hour | TBD |

---

## Troubleshooting

### Deployment Failed

```bash
# Check GitHub Actions logs
# https://github.com/v0idwalker37/ish-clawd-backup/actions

# Check Terraform state
cd infra/terraform/environments/staging
terraform show

# Manually retry
terraform apply
```

### Service Won't Start

```bash
# Check logs
gcloud run services logs read api-gateway-staging --region=us-central1

# Check service status
gcloud run services describe api-gateway-staging --region=us-central1

# Check secrets
gcloud secrets versions access latest --secret=jwt-secret
```

### Database Connection Issues

```bash
# Check Cloud SQL instance
gcloud sql instances describe ungouge-db-staging

# Test connection from Cloud Shell
gcloud sql connect ungouge-db-staging --user=root

# Check VPC connector
gcloud compute networks vpc-access connectors describe ungouge-vpc-connector-staging \
  --region=us-central1
```

---

## Best Practices

### DO ✅
- **Always deploy to staging first**
- **Run full test suite before production deploy**
- **Create database backups before migrations**
- **Monitor deployments for 30+ minutes**
- **Use feature flags for risky changes**
- **Document all changes in changelog**
- **Notify team before production deploy**

### DON'T ❌
- **Don't deploy on Friday afternoons**
- **Don't skip staging environment**
- **Don't delete backups <30 days old**
- **Don't deploy multiple services simultaneously**
- **Don't ignore failing health checks**
- **Don't deploy without rollback plan**

---

## Deployment Checklist

**Pre-Deployment:**
- [ ] All tests passing (unit, integration, E2E)
- [ ] Code review completed
- [ ] Security scan passed
- [ ] Performance benchmarks acceptable
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Database migration reviewed
- [ ] Rollback plan documented

**During Deployment:**
- [ ] Announce in Slack
- [ ] Monitor GitHub Actions
- [ ] Review Terraform plan
- [ ] Approve deployment
- [ ] Watch logs in real-time
- [ ] Verify health checks
- [ ] Run smoke tests

**Post-Deployment:**
- [ ] Monitor error rates (30 min)
- [ ] Check latency metrics
- [ ] Verify database queries
- [ ] Test critical user flows
- [ ] Update status page
- [ ] Notify team of completion
- [ ] Document any issues

---

## Support

- **Documentation:** See `/docs` directory
- **Runbooks:** See `/docs/runbooks` (TODO)
- **On-Call:** PagerDuty rotation (TODO)
- **Slack:** #ungouge-alerts

---

**Last Updated:** 2026-02-17
