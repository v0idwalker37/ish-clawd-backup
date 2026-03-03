---
name: ungouge-devops
description: CI/CD and deployment automation for ungouge.ai full-stack application. Provides deployment scripts, GitHub Actions workflows, environment validation, and Docker optimization for FastAPI backend (Google Cloud Run) and Next.js frontend (Vercel). Use when deploying to production, setting up CI/CD pipelines, automating deployments, validating environment configuration, optimizing Docker images, or troubleshooting deployment issues.
---

# Ungouge DevOps

Comprehensive CI/CD and deployment automation for the ungouge.ai project.

## Quick Start

### 1. Deploy Backend (Cloud Run)

```bash
# Set required environment variables
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="us-central1"

# Deploy to production
./scripts/deploy_backend.sh production

# Deploy to staging
./scripts/deploy_backend.sh staging
```

### 2. Deploy Frontend (Vercel)

```bash
# Deploy to production
./scripts/deploy_frontend.sh production

# Deploy preview
./scripts/deploy_frontend.sh preview
```

### 3. Validate Environment

```bash
# Check all required variables and configs
python scripts/validate_env.py production
```

## Core Components

### Deployment Scripts

**`deploy_backend.sh`** - Backend deployment automation:
- Builds Docker image
- Pushes to Google Container Registry
- Deploys to Cloud Run
- Preserves environment variables
- Runs health checks
- Supports production and staging environments

**`deploy_frontend.sh`** - Frontend deployment automation:
- Builds Next.js application
- Deploys to Vercel
- Runs smoke tests
- Supports production and preview deployments

**`validate_env.py`** - Environment validation:
- Checks all required environment variables
- Validates GCP configuration
- Verifies Vercel setup
- Checks required files exist
- Color-coded output for easy scanning

### GitHub Actions Workflows

**`github-actions-backend.yml`** - Backend CI/CD pipeline:
- Runs tests with pytest
- Linting with ruff
- Type checking with mypy
- Security scanning with Trivy
- Builds and pushes Docker images
- Auto-deploys to Cloud Run on main branch
- Code coverage reporting

**`github-actions-frontend.yml`** - Frontend CI/CD pipeline:
- ESLint and TypeScript checks
- Next.js build verification
- Lighthouse performance audits
- Preview deployments for PRs
- Auto-deploys to Vercel on main branch
- Bundle size analysis

### References

**`cicd_patterns.md`** - Comprehensive CI/CD guidance:
- Deployment strategies and workflows
- GitHub Actions patterns
- Secret management
- Environment configuration
- Rollback procedures
- Monitoring and alerts

**`docker_optimization.md`** - Docker best practices:
- Multi-stage builds
- Layer caching
- Security hardening
- Image size optimization
- Cloud Run specific configurations

## Setup Guide

### Initial GitHub Actions Setup

1. **Add GitHub Secrets** (Settings → Secrets and variables → Actions):

**Backend Secrets:**
```
GCP_PROJECT_ID       - Your GCP project ID
GCP_SA_KEY           - Service account JSON key (base64)
DATABASE_URL         - Production database connection string
GEMINI_API_KEY       - Google Gemini API key
JWT_SECRET           - Secret for JWT signing
```

**Frontend Secrets:**
```
VERCEL_TOKEN         - Vercel authentication token
VERCEL_ORG_ID        - Vercel organization ID
VERCEL_PROJECT_ID    - Vercel project ID
```

2. **Copy Workflow Files**:

```bash
# Create workflows directory
mkdir -p .github/workflows

# Copy workflows
cp scripts/github-actions-backend.yml .github/workflows/backend.yml
cp scripts/github-actions-frontend.yml .github/workflows/frontend.yml

# Commit and push
git add .github/workflows/
git commit -m "Add CI/CD workflows"
git push
```

3. **Verify Workflows**:
- Go to GitHub → Actions tab
- Check that workflows appear
- Create a test PR to trigger preview deployment

### Initial GCP Setup

```bash
# Authenticate
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Create service account for CI/CD
gcloud iam service-accounts create github-actions \
    --display-name="GitHub Actions"

# Grant permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# Create and download key
gcloud iam service-accounts keys create key.json \
    --iam-account=github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com

# Base64 encode and add to GitHub Secrets as GCP_SA_KEY
cat key.json | base64
```

### Initial Vercel Setup

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Link project
cd frontend
vercel link

# Get org and project IDs
cat .vercel/project.json

# Add to GitHub Secrets:
# - VERCEL_ORG_ID
# - VERCEL_PROJECT_ID
# - VERCEL_TOKEN (from vercel.com/account/tokens)
```

## Common Workflows

### Deploy Backend with New Environment Variables

```bash
# Deploy with updated env vars
gcloud run deploy ungouge-backend \
  --image=gcr.io/$GCP_PROJECT_ID/ungouge-backend:latest \
  --project=$GCP_PROJECT_ID \
  --region=us-central1 \
  --set-env-vars="DATABASE_URL=$DATABASE_URL,NEW_VAR=$VALUE"
```

**⚠️ Important**: Always use `--set-env-vars` when deploying, or variables will be lost.

### Rollback Backend Deployment

```bash
# List revisions
gcloud run revisions list \
  --service=ungouge-backend \
  --project=$GCP_PROJECT_ID

# Rollback to specific revision
gcloud run services update-traffic ungouge-backend \
  --to-revisions=ungouge-backend-00066=100 \
  --project=$GCP_PROJECT_ID
```

### Rollback Frontend Deployment

```bash
# List deployments
vercel list

# Promote previous deployment
vercel promote <deployment-url> --prod
```

### Check Deployment Health

```bash
# Backend
curl https://your-backend-url.run.app/health

# Frontend
curl https://ungouge.ai
```

### View Logs

```bash
# Cloud Run logs
gcloud run logs read \
  --service=ungouge-backend \
  --project=$GCP_PROJECT_ID \
  --limit=100

# Vercel logs
vercel logs ungouge.ai
```

## Deployment Checklist

**Before Every Production Deploy:**

- [ ] All tests passing locally
- [ ] Environment variables validated (`python scripts/validate_env.py production`)
- [ ] Database migrations tested with rollback
- [ ] Health check endpoints working
- [ ] Previous revision noted for rollback
- [ ] Monitoring/alerts active

**After Deployment:**

- [ ] Health check passed
- [ ] Smoke tests passed
- [ ] Error monitoring shows no spikes
- [ ] API latency normal
- [ ] Frontend loads correctly
- [ ] Database connection working

## Troubleshooting

### "Deployment succeeded but env vars missing"

**Cause**: Deployed without `--set-env-vars`

**Fix**:
```bash
# Re-deploy with env vars
./scripts/deploy_backend.sh production
```

### "Health check failing after deploy"

**Check**:
1. Database connection string correct?
2. All required env vars set?
3. Cloud Run logs: `gcloud run logs read --service=ungouge-backend`

### "Tests pass locally but fail in CI"

**Check**:
1. Python/Node version mismatch?
2. Missing dependencies in requirements.txt?
3. Missing environment variables for tests?

### "Docker build fails in CI"

**Common causes**:
- Platform mismatch (add `--platform linux/amd64`)
- Missing files in .dockerignore
- Build dependencies not installed

**Fix**: See [docker_optimization.md](references/docker_optimization.md)

## Resources

### Detailed Documentation

- **[cicd_patterns.md](references/cicd_patterns.md)** - For CI/CD strategies, GitHub Actions patterns, secret management, monitoring
- **[docker_optimization.md](references/docker_optimization.md)** - For Dockerfile optimization, multi-stage builds, Cloud Run configurations

### Scripts

- **[deploy_backend.sh](scripts/deploy_backend.sh)** - Backend deployment automation
- **[deploy_frontend.sh](scripts/deploy_frontend.sh)** - Frontend deployment automation
- **[validate_env.py](scripts/validate_env.py)** - Environment validation
- **[github-actions-backend.yml](scripts/github-actions-backend.yml)** - Backend CI/CD workflow
- **[github-actions-frontend.yml](scripts/github-actions-frontend.yml)** - Frontend CI/CD workflow

## Best Practices

✅ **DO**:
- Validate environment before deploying
- Use `--set-env-vars` to preserve variables
- Tag Docker images with git SHA
- Run health checks after deployment
- Keep deployment scripts in version control
- Document rollback procedures

❌ **DON'T**:
- Deploy without testing
- Hardcode secrets in workflows
- Skip environment validation
- Deploy on Friday afternoons
- Ignore health check failures
- Use `latest` tag in production
