# Ungouge.ai Microservices

This directory contains all microservices for the Ungouge.ai v2 architecture.

## Services

### API Gateway (`api-gateway/`)
- **Port:** 8000
- **Purpose:** Entry point for all backend requests
- **Responsibilities:**
  - JWT authentication
  - Rate limiting
  - Request routing
  - Security headers
  - CORS handling

### Cost Model Service (`cost-model/`)
- **Port:** 8001
- **Purpose:** Calculate fair market pricing for contractor quotes
- **Responsibilities:**
  - Quote cost analysis
  - Regional pricing adjustments
  - Result caching (Redis)
  - Confidence scoring

### Quote Extractor Service (`quote-extractor/`)
- **Port:** 8002
- **Purpose:** Extract structured data from uploaded quotes
- **Responsibilities:**
  - OCR (Google Vision API)
  - Text parsing
  - Data extraction
  - Validation

### Webhook Handler Service (`webhook-handler/`)
- **Port:** 8003
- **Purpose:** Process Stripe webhook events
- **Responsibilities:**
  - Webhook signature validation
  - Idempotent event processing
  - Order status updates
  - Pub/Sub publishing

## Local Development

### Prerequisites
- Docker & Docker Compose
- Python 3.12+
- Google Cloud SDK (for Quote Extractor)

### Quick Start

```bash
# Start all services
docker-compose up

# Run a single service
docker-compose up api-gateway

# Rebuild after code changes
docker-compose up --build

# View logs
docker-compose logs -f api-gateway

# Stop all services
docker-compose down
```

### Testing Individual Services

```bash
# API Gateway
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready

# Cost Model
curl http://localhost:8001/health/live

# Quote Extractor
curl http://localhost:8002/health/live

# Webhook Handler
curl http://localhost:8003/health/live
```

### Environment Variables

Create a `.env` file in the project root:

```env
# Stripe (get from dashboard.stripe.com)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# GCP (for Quote Extractor)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
GCP_PROJECT_ID=gen-lang-client-0199462206
```

## Service Communication

Services communicate via HTTP:
- API Gateway → Cost Model Service (internal)
- API Gateway → Quote Extractor Service (internal)
- Webhook Handler → Pub/Sub → Background Workers

## Production Deployment

Services are deployed to Google Cloud Run via Terraform:

```bash
cd infra/terraform/environments/staging
terraform init
terraform plan
terraform apply
```

See `infra/terraform/` for full infrastructure code.

## Testing

### Unit Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests for a service
cd services/cost-model
pytest

# Run all tests
pytest services/
```

### Integration Tests

```bash
# Start services
docker-compose up -d

# Run integration tests
pytest tests/integration/

# Stop services
docker-compose down
```

## Database Migrations

```bash
# Apply migrations
cd services/database
# TODO: Add Alembic commands
```

## Monitoring

- **Health Checks:** All services expose `/health/live` and `/health/ready`
- **Metrics:** Cloud Monitoring (production)
- **Logs:** Cloud Logging (production)
- **Errors:** Sentry (production)

## Architecture

See `ARCHITECTURE_V2_HEROIC.md` in the project root for complete architecture documentation.

## Contributing

1. Create a feature branch
2. Make changes
3. Run tests
4. Submit PR
5. CI/CD will test and deploy to staging

## Troubleshooting

### Service won't start
- Check Docker logs: `docker-compose logs <service-name>`
- Verify database is running: `docker-compose ps`
- Check environment variables

### Database connection failed
- Ensure PostgreSQL is healthy: `docker-compose ps postgres`
- Check DATABASE_URL format: `postgresql+asyncpg://user:pass@host:port/db`

### Redis connection failed
- Ensure Redis is healthy: `docker-compose ps redis`
- Check REDIS_URL format: `redis://host:port`

### Vision API errors (Quote Extractor)
- Ensure GCP credentials are mounted
- Verify service account has Vision API access
- Check GCP_PROJECT_ID is correct

## Next Steps

- [ ] Add comprehensive unit tests
- [ ] Implement integration test suite
- [ ] Add Prometheus metrics
- [ ] Set up distributed tracing
- [ ] Add request/response logging
- [ ] Implement circuit breakers
- [ ] Add performance benchmarks
