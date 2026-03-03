# CI/CD Patterns for Ungouge.ai

Best practices for continuous integration and deployment automation.

## Table of Contents

1. [Deployment Strategy](#deployment-strategy)
2. [GitHub Actions Patterns](#github-actions-patterns)
3. [Secret Management](#secret-management)
4. [Environment Configuration](#environment-configuration)
5. [Rollback Procedures](#rollback-procedures)
6. [Monitoring and Alerts](#monitoring-and-alerts)

---

## Deployment Strategy

### Branch Strategy

**Main Branch (Production)**
- Protected branch, requires PR approval
- Auto-deploys to production on merge
- All tests must pass
- Requires code review

**Develop Branch (Staging)**
- Integration branch for features
- Auto-deploys to staging environment
- Less strict requirements than main

**Feature Branches**
- `feature/description-here`
- Creates preview deployments
- Must pass all tests before merge

### Deployment Flow

```
Feature Branch → Pull Request → Preview Deployment
                                      ↓
                              Code Review + Tests
                                      ↓
                              Merge to develop → Staging Deploy
                                      ↓
                              Final Testing
                                      ↓
                              Merge to main → Production Deploy
```

---

## GitHub Actions Patterns

### Triggering Workflows

**Path-based Triggers**
```yaml
on:
  push:
    paths:
      - 'backend/**'
      - '.github/workflows/backend.yml'
```

Only run backend CI when backend code changes.

**Conditional Deployments**
```yaml
if: github.ref == 'refs/heads/main' && github.event_name == 'push'
```

Deploy only on main branch pushes.

### Job Dependencies

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    # ... test steps
  
  deploy:
    needs: [test]  # Won't run unless test succeeds
    runs-on: ubuntu-latest
    # ... deploy steps
```

### Matrix Builds

Test multiple Python versions:

```yaml
jobs:
  test:
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
```

### Caching Dependencies

**Python:**
```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'
    cache: 'pip'
```

**Node.js:**
```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'
    cache-dependency-path: './frontend/package-lock.json'
```

### Artifact Upload

```yaml
- name: Upload coverage
  uses: actions/upload-artifact@v4
  with:
    name: coverage-report
    path: coverage/
    retention-days: 30
```

---

## Secret Management

### GitHub Secrets

**Required Secrets for Backend:**
- `GCP_PROJECT_ID` - Google Cloud project ID
- `GCP_SA_KEY` - Service account JSON key (base64 encoded)
- `DATABASE_URL` - Production database connection string
- `GEMINI_API_KEY` - Google Gemini API key
- `JWT_SECRET` - Secret for JWT token signing

**Required Secrets for Frontend:**
- `VERCEL_TOKEN` - Vercel authentication token
- `VERCEL_ORG_ID` - Vercel organization ID
- `VERCEL_PROJECT_ID` - Vercel project ID

### Using Secrets in Workflows

```yaml
- name: Deploy to Cloud Run
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
    JWT_SECRET: ${{ secrets.JWT_SECRET }}
  run: |
    gcloud run deploy ... \
      --set-env-vars="DATABASE_URL=$DATABASE_URL,JWT_SECRET=$JWT_SECRET"
```

### Secret Rotation

**Quarterly Rotation Schedule:**
1. Generate new secret
2. Add as new GitHub secret with different name
3. Update workflow to use new secret
4. Verify deployments work
5. Delete old secret
6. Rename new secret to standard name

---

## Environment Configuration

### Environment-Specific Variables

**Development:**
```env
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///dev.db
CORS_ORIGINS=http://localhost:3000
```

**Staging:**
```env
LOG_LEVEL=INFO
DATABASE_URL=postgresql://staging-db...
CORS_ORIGINS=https://staging.ungouge.ai
```

**Production:**
```env
LOG_LEVEL=WARNING
DATABASE_URL=postgresql://production-db...
CORS_ORIGINS=https://ungouge.ai
SENTRY_DSN=https://...
```

### Environment Variable Validation

Run validation before deployment:

```yaml
- name: Validate environment
  run: python scripts/validate_env.py production
```

### Config File Pattern

**config.py:**
```python
import os
from typing import Literal

Environment = Literal["development", "staging", "production"]

class Config:
    ENVIRONMENT: Environment = os.getenv("ENVIRONMENT", "development")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    
    # Feature Flags
    ENABLE_ANALYTICS: bool = ENVIRONMENT == "production"
    
    @classmethod
    def validate(cls):
        """Validate required config is set."""
        required = ["DATABASE_URL", "GEMINI_API_KEY", "JWT_SECRET"]
        missing = [k for k in required if not getattr(cls, k, None)]
        if missing:
            raise ValueError(f"Missing required config: {missing}")

# Validate on import
Config.validate()
```

---

## Rollback Procedures

### Cloud Run Rollback

**View Revisions:**
```bash
gcloud run revisions list \
  --service=ungouge-backend \
  --project=$GCP_PROJECT_ID \
  --region=us-central1
```

**Rollback to Previous Revision:**
```bash
gcloud run services update-traffic ungouge-backend \
  --to-revisions=ungouge-backend-00066=100 \
  --project=$GCP_PROJECT_ID \
  --region=us-central1
```

**Automated Rollback on Health Check Failure:**
```yaml
- name: Health check
  id: health
  run: curl -f ${{ steps.deploy.outputs.url }}/health || echo "failed"

- name: Rollback on failure
  if: steps.health.outputs.result == 'failed'
  run: |
    gcloud run services update-traffic $SERVICE_NAME \
      --to-latest-revision=false \
      --to-revisions=$PREVIOUS_REVISION=100
```

### Vercel Rollback

**Via CLI:**
```bash
# List deployments
vercel list

# Promote a previous deployment
vercel promote <deployment-url> --prod
```

**Via Dashboard:**
1. Go to Vercel dashboard
2. Select project
3. Click "Deployments"
4. Find working deployment
5. Click "..." → "Promote to Production"

### Database Migration Rollback

**Alembic Downgrade:**
```bash
# Downgrade one revision
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade <revision_id>

# Downgrade to base
alembic downgrade base
```

**Safety Pattern:**
```python
# Always make migrations reversible
def upgrade():
    op.add_column('quotes', sa.Column('new_field', sa.String()))

def downgrade():
    op.drop_column('quotes', 'new_field')
```

---

## Monitoring and Alerts

### Health Check Endpoints

**Backend:**
```python
@app.get("/health")
async def health_check():
    """Health check for load balancers and monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": os.getenv("GIT_SHA", "unknown")
    }

@app.get("/health/detailed")
async def detailed_health(db: Session = Depends(get_db)):
    """Detailed health with dependencies."""
    checks = {
        "database": await check_database(db),
        "gemini_api": await check_gemini(),
        "redis": await check_redis() if REDIS_URL else "skipped"
    }
    
    all_healthy = all(v == "healthy" for v in checks.values())
    status_code = 200 if all_healthy else 503
    
    return JSONResponse(
        content={"status": "healthy" if all_healthy else "unhealthy", "checks": checks},
        status_code=status_code
    )
```

### GitHub Actions Status Badges

```markdown
# README.md
![Backend CI](https://github.com/ungouge/ungouge/actions/workflows/backend.yml/badge.svg)
![Frontend CI](https://github.com/ungouge/ungouge/actions/workflows/frontend.yml/badge.svg)
```

### Deployment Notifications

**Slack Integration:**
```yaml
- name: Notify Slack on deployment
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "✅ Production deployment successful!",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Deployment Complete*\nCommit: ${{ github.sha }}\nAuthor: ${{ github.actor }}"
            }
          }
        ]
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

### Error Tracking

**Sentry Integration:**
```python
import sentry_sdk

if os.getenv("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        environment=os.getenv("ENVIRONMENT", "production"),
        traces_sample_rate=0.1,
        profiles_sample_rate=0.1,
    )
```

---

## Best Practices Summary

### DO:
✅ Run tests before deploying  
✅ Use environment-specific configurations  
✅ Validate environment variables before deploy  
✅ Implement health checks  
✅ Use semantic versioning for releases  
✅ Tag Docker images with git SHA  
✅ Keep secrets in GitHub Secrets, never in code  
✅ Have rollback procedures documented and tested  
✅ Monitor deployments with alerts  
✅ Use caching to speed up CI builds  

### DON'T:
❌ Deploy without testing  
❌ Hardcode secrets in workflow files  
❌ Skip environment validation  
❌ Deploy on Friday afternoons  
❌ Make database migrations without rollback plan  
❌ Ignore health check failures  
❌ Deploy without health endpoints  
❌ Skip code review for production merges  
❌ Use `latest` tag in production  
❌ Deploy multiple changes simultaneously  

---

## Troubleshooting

### Common Issues

**"Deployment succeeded but site shows old version"**
- Clear CDN cache
- Check if correct revision is serving traffic
- Verify environment variables are set

**"Tests pass locally but fail in CI"**
- Check Python/Node version mismatch
- Verify all dependencies in requirements.txt/package.json
- Check for missing environment variables

**"Docker build fails in CI but works locally"**
- Check platform compatibility (add `--platform linux/amd64`)
- Verify Dockerfile uses multi-stage build correctly
- Check for missing files in .dockerignore

**"Health check fails after deployment"**
- Check database connection string
- Verify all required environment variables are set
- Check Cloud Run logs: `gcloud run logs read --service=ungouge-backend`

---

## Migration Checklist

Before going live with CI/CD:

- [ ] All secrets added to GitHub Secrets
- [ ] Health check endpoints implemented
- [ ] Database migrations tested with rollback
- [ ] Rollback procedures documented
- [ ] Error tracking (Sentry) configured
- [ ] Monitoring/alerts set up
- [ ] Deployment notifications configured
- [ ] Branch protection rules enabled on main
- [ ] Code owners file configured
- [ ] CI/CD workflows tested on staging
- [ ] Load testing performed
- [ ] Backup/restore procedures tested
