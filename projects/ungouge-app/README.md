# GougeAlert - Fair Pricing for Home Improvement Projects

**Version 2.0 - Microservices Architecture**

GougeAlert helps homeowners avoid getting ripped off by analyzing contractor quotes with AI and providing fair market pricing comparisons.

---

## 🏗️ Architecture

**Production-ready microservices on Google Cloud Platform:**

- **API Gateway** (Cloud Run) - Auth, routing, rate limiting
- **Cost Model Service** (Cloud Run) - Quote cost analysis with Redis caching
- **Quote Extractor Service** (Cloud Run) - OCR + data extraction (Vision API)
- **Webhook Handler Service** (Cloud Run) - Stripe payment processing
- **Frontend** (Vercel) - Next.js 14 App Router
- **Database** (Cloud SQL) - MySQL 8.0, regional HA
- **Cache** (Memorystore) - Redis 7.0, read replicas
- **Storage** (Cloud Storage) - Uploaded quotes + generated PDFs
- **Messaging** (Pub/Sub) - Async event processing

See `ARCHITECTURE_V2_HEROIC.md` for complete architecture documentation.

---

## 🚀 Quick Start

### Local Development

```bash
# Clone the repo
git clone https://github.com/v0idwalker37/ish-clawd-backup.git
cd ungouge-app  # (repo directory name)

# Set up environment
cp .env.example .env
# Edit .env with your credentials

# Start all services
docker-compose up

# Services will be available at:
# - API Gateway: http://localhost:8000
# - Cost Model: http://localhost:8001
# - Quote Extractor: http://localhost:8002
# - Webhook Handler: http://localhost:8003
# - Frontend: http://localhost:3000 (separate repo)
```

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest services/*/test_main.py -v

# Run specific service tests
cd services/api-gateway
pytest test_main.py -v
```

---

## 📁 Project Structure

```
ungouge-app/
├── services/                    # Microservices
│   ├── api-gateway/            # Entry point for all requests
│   ├── cost-model/             # Quote analysis engine
│   ├── quote-extractor/        # OCR + data extraction
│   ├── webhook-handler/        # Stripe webhooks
│   ├── database/               # Schema migrations
│   └── README.md               # Services documentation
├── infra/                       # Infrastructure as Code
│   └── terraform/
│       ├── modules/            # Reusable Terraform modules
│       └── environments/
│           ├── staging/        # Staging environment
│           └── production/     # Production environment
├── .github/workflows/           # CI/CD pipelines
│   ├── deploy-staging.yml      # Auto-deploy to staging
│   └── deploy-production.yml   # Production deployment (manual approval)
├── backend/                     # Legacy monolith (being decomposed)
├── frontend/                    # Next.js 14 frontend (separate deployment)
├── docs/                        # Documentation
├── docker-compose.yml           # Local dev environment
├── ARCHITECTURE_V2_HEROIC.md   # Complete architecture doc
├── REFACTOR_PLAN_HEROIC.md     # Refactor strategy
├── IMPLEMENTATION_LOG.md        # Progress tracking
└── README.md                    # This file
```

---

## 🛠️ Technology Stack

**Backend:**
- FastAPI (Python 3.12)
- SQLAlchemy + AsyncPG
- Redis for caching
- Google Cloud Vision API
- Stripe for payments

**Frontend:**
- Next.js 14 (App Router)
- React 18
- TypeScript
- Tailwind CSS

**Infrastructure:**
- Google Cloud Platform
- Terraform for IaC
- Docker + Cloud Run
- GitHub Actions for CI/CD

**Observability:**
- Cloud Logging
- Cloud Monitoring
- Sentry for errors
- Custom metrics

---

## 🔐 Security

- **Authentication:** JWT with refresh tokens
- **HTTPS:** Enforced everywhere
- **Rate Limiting:** Per-IP, per-user limits
- **CORS:** Strict origin controls
- **Headers:** CSP, HSTS, XSS protection
- **Secrets:** Secret Manager (never in code)
- **Encryption:** Customer-managed keys (production)
- **DDoS:** Cloud Armor protection
- **Auditing:** All auth events logged

See `ARCHITECTURE_V2_HEROIC.md` section 5 for complete security design.

---

## 📊 Monitoring & Alerts

**Health Checks:**
- `/health/live` - Liveness probe
- `/health/ready` - Readiness probe (checks dependencies)

**Alerts:**
- Error rate > 5%
- Latency p99 > 2s
- Budget > 80%
- Database CPU > 80%
- SSL cert expiry < 30 days

**Dashboards:**
- Request rates & latency
- Error rates by service
- Database performance
- Cost breakdown

---

## 🚢 Deployment

### Staging (Auto)

Push to `develop` branch triggers automatic deployment:

```bash
git checkout develop
git merge feature/my-feature
git push origin develop
# CI/CD automatically deploys to staging
```

### Production (Manual Approval)

Push to `main` requires manual approval:

```bash
git checkout main
git merge develop
git push origin main
# GitHub Actions workflow waits for approval
# Reviewer approves in GitHub UI
# Deployment proceeds automatically
```

### Rollback

```bash
cd infra/terraform/environments/production
terraform apply -target=module.api_gateway -var="image_tag=<previous-sha>"
```

---

## 🧪 Testing Strategy

**Unit Tests:** Each service has `test_main.py`
**Integration Tests:** `tests/integration/` (TODO)
**E2E Tests:** Playwright (TODO)
**Load Tests:** k6 (TODO)

**Test Coverage Goals:**
- Services: >80%
- Critical paths: 100%

---

## 📈 Performance

**Targets:**
- API latency p50: <200ms
- API latency p99: <2s
- Quote extraction: <30s
- Cost analysis: <5s (cached: <100ms)

**Scaling:**
- API Gateway: 1-10 instances
- Cost Model: 1-20 instances
- Quote Extractor: 0-50 instances (bursty)
- Webhook Handler: 1-10 instances

---

## 🐛 Troubleshooting

### Services won't start locally

```bash
# Check logs
docker-compose logs -f api-gateway

# Verify database is running
docker-compose ps postgres

# Reset everything
docker-compose down -v
docker-compose up --build
```

### Database migrations failed

```bash
cd services/database
# TODO: Add Alembic commands
```

### Tests failing

```bash
# Ensure services are running
docker-compose up -d

# Check service health
curl http://localhost:8000/health/ready
curl http://localhost:8001/health/ready
```

---

## 📝 Documentation

- **Architecture:** `ARCHITECTURE_V2_HEROIC.md` (30KB, complete system design)
- **Refactor Plan:** `REFACTOR_PLAN_HEROIC.md` (heroic implementation strategy)
- **API Spec:** `services/api-gateway/openapi.yaml`
- **Services README:** `services/README.md`
- **Implementation Log:** `IMPLEMENTATION_LOG.md` (progress tracking)

---

## 🤝 Contributing

1. Create feature branch from `develop`
2. Write tests for new functionality
3. Ensure all tests pass
4. Submit PR with description
5. CI/CD runs checks
6. Code review required
7. Merge to `develop`
8. Auto-deploys to staging

---

## 📜 License

Proprietary - All rights reserved

---

## 🙏 Credits

Built by Jason Trask with AI assistance (Ish/Claude).

**Tech Stack:**
- FastAPI, Next.js, Google Cloud Platform
- Stripe, Terraform, Docker

**Contact:**
- Email: jasontrask@gmail.com
- GitHub: v0idwalker37

---

## 🎯 Roadmap

**V2.0 (Current):**
- [x] Microservices architecture design
- [ ] Service implementations (80% done)
- [ ] Terraform infrastructure (80% done)
- [ ] CI/CD pipelines (done)
- [ ] Staging deployment
- [ ] Production deployment

**V2.1:**
- [ ] Enhanced NLP for quote parsing
- [ ] Machine learning cost model
- [ ] Multi-language support
- [ ] Mobile apps (iOS/Android)

**V2.2:**
- [ ] Contractor marketplace
- [ ] Project management tools
- [ ] Payment escrow
- [ ] Review system

---

**Status:** 🚧 Active Development - V2.0 Heroic Refactor In Progress

**Last Updated:** 2026-02-17
