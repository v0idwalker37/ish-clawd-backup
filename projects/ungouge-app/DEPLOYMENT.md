# Ungouge.ai Production Deployment Guide

**Last Updated:** 2026-02-02  
**Status:** Ready for deployment after pre-launch checklist completion

---

## Pre-Launch Security Checklist

### Critical (Must Complete Before Deploy)

- [ ] **Generate production JWT secret**
  ```bash
  openssl rand -hex 32
  ```
  Set as `JWT_SECRET_KEY` environment variable

- [ ] **Switch to PostgreSQL database**
  - Provision PostgreSQL instance (Railway, Supabase, AWS RDS)
  - Update `DATABASE_URL` environment variable
  - Run migrations: `alembic upgrade head`

- [ ] **Configure production CORS**
  - Set `FRONTEND_URL` to production domain
  - Verify CORS origins in `main.py`

- [ ] **Set environment to production**
  ```bash
  ENVIRONMENT=production
  ```

- [ ] **Disable database echo**
  ```bash
  DATABASE_ECHO=false
  ```

- [ ] **Configure email service**
  - Set up SendGrid, AWS SES, or Mailgun
  - Update SMTP credentials in environment variables
  - Set `EMAIL_DEV_MODE=false`

- [ ] **Add Stripe production keys**
  - Replace test keys with live keys
  - Update webhook secret

- [ ] **Set up Redis for production** (optional but recommended)
  - For token blacklist and rate limiting
  - Update `services/token_blacklist.py` to use Redis

- [ ] **Configure logging destination**
  - Sentry, Datadog, LogDNA, or CloudWatch
  - Set up alerts for auth failures, errors

- [ ] **Enable HTTPS**
  - Configure TLS/SSL certificates
  - Let's Encrypt recommended

- [ ] **Firewall configuration**
  - Allow ports: 443 (HTTPS), 80 (HTTP redirect)
  - Deny direct database access from public

---

## Deployment Platforms

### Recommended: Railway.app

**Why Railway:**
- Easy PostgreSQL provisioning
- Built-in Redis
- Environment variables per service
- Auto-deploy from GitHub
- Affordable ($5-20/month)

**Setup:**
1. Connect GitHub repository
2. Deploy backend service
3. Add PostgreSQL database
4. Add Redis instance
5. Set environment variables
6. Deploy frontend (Vercel or Railway)

### Alternative: AWS (More Complex)

**Services needed:**
- **EC2** or **ECS**: Run backend
- **RDS PostgreSQL**: Database
- **ElastiCache**: Redis
- **S3**: Static assets
- **CloudFront**: CDN
- **Route 53**: DNS

---

## Environment Variables (Production)

```bash
# Environment
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://user:pass@host:5432/ungouge
DATABASE_ECHO=false

# JWT
JWT_SECRET_KEY=<generated-with-openssl-rand-hex-32>

# Frontend
FRONTEND_URL=https://ungouge.ai

# Email
EMAIL_DEV_MODE=false
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<sendgrid-api-key>
FROM_EMAIL=noreply@ungouge.ai
FROM_NAME=Ungouge.ai

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Craftsman API
CRAFTSMAN_API_ENDPOINT=https://nec-api.craftsman-book.com
CRAFTSMAN_API_KEY=<production-key>
CRAFTSMAN_USERNAME=<production-username>
CRAFTSMAN_PASSWORD=<production-password>

# Optional: OpenAI
OPENAI_API_KEY=sk-...

# Redis (if using)
REDIS_HOST=redis-production.railway.internal
REDIS_PORT=6379
```

---

## Database Migration

### From SQLite (Dev) to PostgreSQL (Prod)

1. **Export data from SQLite** (optional, if you have test data to preserve):
   ```bash
   # Not recommended - start fresh in production
   ```

2. **Run migrations on PostgreSQL**:
   ```bash
   alembic upgrade head
   ```

3. **Verify tables created**:
   ```bash
   psql $DATABASE_URL -c "\dt"
   ```

---

## Monitoring & Logging

### Set Up Sentry (Error Tracking)

```bash
pip install sentry-sdk[fastapi]
```

In `main.py`:
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://...@sentry.io/...",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,  # 10% of transactions
    environment="production",
)
```

### Log Aggregation

**Option 1: Datadog**
- Real-time dashboard
- Custom metrics
- $15/month starter

**Option 2: LogDNA/Mezmo**
- Structured log search
- Alerts
- $30/month

**Option 3: CloudWatch** (if on AWS)
- Native AWS integration
- Pay per GB ingested

---

## Security Hardening Checklist

### Application Level

- [x] Rate limiting enabled
- [x] CSRF protection configured
- [x] Security headers added
- [x] SQL injection protected (ORM)
- [x] XSS protection (React)
- [x] Access control on resources
- [x] Password hashing (bcrypt)
- [x] JWT with expiry
- [x] Token blacklist for logout
- [x] Structured logging
- [x] Error messages sanitized

### Infrastructure Level

- [ ] HTTPS enforced (redirect HTTP → HTTPS)
- [ ] WAF enabled (Cloudflare or AWS WAF)
- [ ] DDoS protection
- [ ] Database backups automated
- [ ] Secrets in environment variables (not code)
- [ ] Network security groups configured
- [ ] SSH keys rotated regularly
- [ ] Principle of least privilege (IAM/permissions)

---

## Performance Optimization

### Backend

- [ ] Database indexes on:
  - `users.email`
  - `quotes.user_id`
  - `quotes.created_at`
  - `password_reset_tokens.token`
  - `email_verification_tokens.token`

- [ ] Connection pooling configured:
  ```python
  engine = create_async_engine(
      DATABASE_URL,
      pool_size=20,
      max_overflow=10,
  )
  ```

- [ ] Enable gzip compression:
  ```python
  from fastapi.middleware.gzip import GZipMiddleware
  app.add_middleware(GZipMiddleware, minimum_size=1000)
  ```

### Frontend

- [ ] Next.js static optimization enabled
- [ ] Images optimized (next/image)
- [ ] CDN for static assets (Vercel, CloudFront)
- [ ] Lighthouse score >90

---

## Backup Strategy

### Database Backups

**Automated (Railway/AWS RDS):**
- Daily snapshots (retain 7 days)
- Weekly backups (retain 4 weeks)
- Monthly archives (retain 12 months)

**Manual:**
```bash
pg_dump $DATABASE_URL > backup-$(date +%Y%m%d).sql
```

### Disaster Recovery

1. **Recovery Time Objective (RTO):** 4 hours
2. **Recovery Point Objective (RPO):** 24 hours
3. **Backup restore testing:** Quarterly

---

## Post-Deployment Tasks

### Week 1

- [ ] Monitor error rates in Sentry
- [ ] Check rate limit effectiveness (adjust if needed)
- [ ] Verify email delivery (check spam folders)
- [ ] Test payment flow end-to-end
- [ ] Monitor database performance
- [ ] Set up uptime monitoring (UptimeRobot, Pingdom)

### Month 1

- [ ] Review security logs for anomalies
- [ ] Update dependencies (npm audit, pip list --outdated)
- [ ] Analyze user feedback for bugs
- [ ] Optimize slow database queries
- [ ] Review and adjust rate limits based on usage

### Quarterly

- [ ] Security audit (re-run OWASP checklist)
- [ ] Dependency updates
- [ ] Backup restoration test
- [ ] Performance benchmarking
- [ ] Review and rotate API keys

---

## Scaling Plan

### Traffic Milestones

**1,000 users/month:**
- Current setup sufficient
- Single server, basic PostgreSQL

**10,000 users/month:**
- Upgrade database (more CPU/RAM)
- Add Redis for caching
- Consider CDN for static assets

**100,000+ users/month:**
- Load balancer (multiple backend instances)
- Read replicas for database
- Separate worker processes for analysis
- Message queue (Celery + Redis)
- Object storage for uploaded quotes (S3)

---

## Rollback Plan

If deployment fails or critical bug discovered:

1. **Revert to previous version**:
   ```bash
   git revert HEAD
   git push
   # Railway/Vercel auto-deploys
   ```

2. **Database rollback** (if migrations applied):
   ```bash
   alembic downgrade -1
   ```

3. **Communicate downtime**:
   - Status page update
   - Email to affected users
   - Social media announcement

---

## Contact & Support

**Technical Issues:** jasontrask@gmail.com  
**Security Concerns:** security@ungouge.ai (set up before launch)

---

## Next Steps

1. Complete pre-launch checklist above
2. Set up production environment on Railway/AWS
3. Configure monitoring (Sentry + logs)
4. Test in staging environment
5. Deploy to production
6. Monitor closely for 48 hours
7. Announce launch 🚀

