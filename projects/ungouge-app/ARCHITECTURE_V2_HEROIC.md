# Ungouge.ai Architecture V2 - Heroic Refactor

**Created:** 2026-02-17 17:52 EST  
**Author:** Ish (Opus 4.6 Ultra)  
**Status:** Architecture Phase - Production Design

## Executive Summary

This document defines the complete production architecture for ungouge.ai, transitioning from a monolithic FastAPI application to a distributed microservices architecture optimized for scalability, security, and maintainability.

**Key Changes:**
- Monolithic FastAPI → Microservices on Cloud Run
- Single database → Cloud SQL + Redis + GCS
- Synchronous processing → Async workers with Pub/Sub
- Manual deployments → Full CI/CD with Terraform
- Basic auth → Production-grade security (Secret Manager, JWT, rate limiting)
- No payment system → Stripe Checkout embedded + webhooks

## Current State Analysis

### Existing Codebase Structure
```
ungouge-app/
├── backend/                    # FastAPI monolith
│   ├── main.py                # App entry, middleware, CORS
│   ├── routers/
│   │   ├── auth.py           # JWT authentication
│   │   ├── quotes.py         # Quote upload & analysis
│   │   ├── payments.py       # Stripe integration (basic)
│   │   └── health.py         # Health checks
│   ├── quote_analyzer.py     # Cost model + extraction (102KB - LARGE)
│   ├── validators.py         # Input validation
│   └── middleware/
│       ├── security_logging.py
│       ├── data_retention.py  # GDPR compliance
│       └── dnt.py            # Do Not Track
├── frontend/                   # Next.js (older version)
│   ├── src/
│   ├── pages/
│   └── components/
└── infra/                     # Basic infrastructure

**Problems:**
1. quote_analyzer.py is 102KB - monolithic, hard to test/scale
2. No async processing - large files block the API
3. No proper queue system - just background tasks
4. Frontend not on Next.js 15 App Router
5. Stripe integration incomplete (no webhooks, no embedded checkout)
6. No Terraform - infrastructure not versioned
7. Secrets in environment variables
8. No CI/CD pipeline
```

### Key Dependencies Identified
- **Backend:** FastAPI, SQLAlchemy, Pydantic, slowapi (rate limiting), python-jose (JWT)
- **Frontend:** Next.js, React, TailwindCSS
- **Current hosting:** Unknown (needs verification)
- **Database:** Unknown (SQLAlchemy abstract, likely PostgreSQL or MySQL)

## Target Architecture

### Service Topology

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND LAYER                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Next.js 15 App Router (Vercel Edge + Serverless)         │  │
│  │  - Static pages (landing, pricing, about)                │  │
│  │  - Server Components (quote form, dashboard)             │  │
│  │  - API Routes (BFF pattern for client-side calls)       │  │
│  │  - Stripe Checkout embedded UI                           │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ HTTPS
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND SERVICES (GCP)                      │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ API Gateway (Cloud Run)                                │    │
│  │  - Authentication (JWT validation)                     │    │
│  │  - Rate limiting (per-IP, per-user)                   │    │
│  │  - Request routing                                     │    │
│  │  - CORS handling                                       │    │
│  │  - Security headers                                    │    │
│  └────────────────────────────────────────────────────────┘    │
│         │                    │                     │             │
│         │                    │                     │             │
│         ▼                    ▼                     ▼             │
│  ┌──────────────┐   ┌──────────────┐    ┌──────────────┐      │
│  │ Cost Model   │   │ Quote        │    │ Webhook      │      │
│  │ Service      │   │ Extractor    │    │ Handler      │      │
│  │ (Cloud Run)  │   │ Service      │    │ (Cloud Run)  │      │
│  │              │   │ (Cloud Run)  │    │              │      │
│  │ - Price calc │   │ - OCR (Vision│    │ - Stripe     │      │
│  │ - Cost logic │   │   API)       │    │   events     │      │
│  │ - Caching    │   │ - NLP parsing│    │ - Idempotent │      │
│  └──────────────┘   │ - Validation │    │   processing │      │
│         │            └──────────────┘    └──────────────┘      │
│         │                    │                     │             │
│         ▼                    ▼                     ▼             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Data & Queue Layer                    │   │
│  │                                                           │   │
│  │  ┌──────────────┐  ┌─────────────┐  ┌───────────────┐  │   │
│  │  │ Cloud SQL    │  │ Redis       │  │ Google        │  │   │
│  │  │ (MySQL)      │  │ (Memorystore│  │ Cloud Storage │  │   │
│  │  │              │  │  )          │  │ (GCS)         │  │   │
│  │  │ - Users      │  │ - Cache     │  │ - Uploaded    │  │   │
│  │  │ - Quotes     │  │ - Sessions  │  │   quotes      │  │   │
│  │  │ - Orders     │  │ - Rate      │  │ - Generated   │  │   │
│  │  │ - Tokens     │  │   limits    │  │   PDFs        │  │   │
│  │  └──────────────┘  └─────────────┘  └───────────────┘  │   │
│  │                                                           │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │ Pub/Sub Topics                                   │   │   │
│  │  │  - quote.uploaded                                │   │   │
│  │  │  - quote.analyzed                                │   │   │
│  │  │  - payment.completed                             │   │   │
│  │  │  - pdf.generate                                  │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Background Workers (Cloud Run Jobs)                     │   │
│  │  - PDF generation (quote summaries)                     │   │
│  │  - Email delivery (via Resend)                          │   │
│  │  - Data retention cleanup (GDPR)                        │   │
│  │  - Analytics aggregation                                │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                             │
│  - Stripe (payments)                                            │
│  - Resend (email)                                               │
│  - Google Vision API (OCR)                                      │
│  - Sentry (error tracking)                                      │
│  - Cloud Monitoring (metrics, logs, traces)                     │
└─────────────────────────────────────────────────────────────────┘
```

### Service Specifications

#### 1. API Gateway Service
**Purpose:** Entry point for all backend requests, handles cross-cutting concerns

**Responsibilities:**
- JWT token validation
- Rate limiting (per-IP: 100 req/min, per-user: 1000 req/hour)
- Request routing to downstream services
- CORS policy enforcement
- Security headers (CSP, HSTS, X-Frame-Options)
- Request/response logging
- Error handling & normalization

**Technology:**
- Language: Python 3.12
- Framework: FastAPI 0.115+
- Container: Cloud Run (min 1, max 10 instances)
- Memory: 512MB
- CPU: 1 vCPU
- Concurrency: 80 requests/instance

**API Contract (OpenAPI):**
```yaml
/api/auth/register:
  POST:
    summary: Register new user
    request: { email, password }
    response: { user_id, access_token, refresh_token }

/api/auth/login:
  POST:
    summary: Authenticate user
    request: { email, password }
    response: { access_token, refresh_token }

/api/quotes/upload:
  POST:
    summary: Upload contractor quote (PDF/image)
    headers: { Authorization: Bearer <token> }
    request: multipart/form-data { file }
    response: { quote_id, status: "processing" }

/api/quotes/{quote_id}:
  GET:
    summary: Get quote analysis results
    headers: { Authorization: Bearer <token> }
    response: { quote_id, status, extracted_data, cost_analysis }

/api/quotes/{quote_id}/checkout:
  POST:
    summary: Create Stripe Checkout session
    headers: { Authorization: Bearer <token> }
    response: { checkout_session_id, url }

/api/webhooks/stripe:
  POST:
    summary: Stripe webhook endpoint
    headers: { Stripe-Signature }
    request: Stripe Event JSON
    response: { received: true }
```

**Environment Variables:**
- JWT_SECRET_KEY (from Secret Manager)
- DATABASE_URL (Cloud SQL connection string)
- REDIS_URL (Memorystore connection)
- COST_MODEL_SERVICE_URL
- QUOTE_EXTRACTOR_SERVICE_URL

**Health Check:**
- `/health/live` - Kubernetes liveness (returns 200 if process alive)
- `/health/ready` - Kubernetes readiness (checks DB, Redis connectivity)

---

#### 2. Cost Model Service
**Purpose:** Calculate fair market pricing for contractor work

**Responsibilities:**
- Accept parsed quote data (line items, materials, labor hours)
- Apply pricing models (regional adjustments, material costs, labor rates)
- Calculate confidence scores
- Return cost breakdown with recommendations
- Cache results (Redis, 1-hour TTL)

**Technology:**
- Language: Python 3.12
- Framework: FastAPI 0.115+
- Container: Cloud Run (min 1, max 20 instances)
- Memory: 1GB (cost models + caching)
- CPU: 2 vCPU (compute-intensive)
- Concurrency: 40 requests/instance

**API Contract:**
```yaml
/analyze:
  POST:
    summary: Analyze quote and return cost breakdown
    request:
      quote_id: string
      line_items: [{ description, quantity, unit, unit_price }]
      location: { zip_code, state }
      project_type: string
    response:
      quote_id: string
      total_cost: float
      fair_price_range: { min: float, max: float }
      confidence_score: float (0-1)
      breakdown: [{ category, estimated_cost, quoted_cost, variance }]
      recommendations: [string]
```

**Data Sources:**
- Historical quote database (Cloud SQL read replica)
- Material price APIs (cached in Redis)
- Regional labor rate tables (loaded at startup)

**Caching Strategy:**
- Key: `cost:quote_id:hash(line_items)`
- TTL: 1 hour
- Invalidation: On new historical data ingestion

---

#### 3. Quote Extractor Service
**Purpose:** Extract structured data from uploaded quotes (PDFs, images)

**Responsibilities:**
- Accept file from GCS (signed URL)
- Perform OCR using Google Vision API
- Parse extracted text into structured data
- Validate extracted fields
- Return parsed data + confidence scores

**Technology:**
- Language: Python 3.12
- Framework: FastAPI 0.115+
- Container: Cloud Run (min 0, max 50 instances - bursty workload)
- Memory: 2GB (Vision API responses can be large)
- CPU: 2 vCPU
- Timeout: 5 minutes (long-running OCR)
- Concurrency: 10 requests/instance (Vision API rate limits)

**API Contract:**
```yaml
/extract:
  POST:
    summary: Extract data from quote file
    request:
      quote_id: string
      file_url: string (GCS signed URL)
      file_type: string (pdf|image)
    response:
      quote_id: string
      status: string (success|partial|failed)
      confidence_score: float (0-1)
      extracted_data:
        contractor: { name, license, contact }
        line_items: [{ description, quantity, unit, unit_price, total }]
        totals: { subtotal, tax, total }
        project_details: { address, scope, timeline }
      errors: [string]
```

**External Dependencies:**
- Google Vision API (OCR)
- GCS (file access)

**Error Handling:**
- Partial extraction: Return what was successfully extracted + errors
- OCR failure: Retry once, then fail gracefully
- Timeout: Return partial results if >4min processing time

---

#### 4. Webhook Handler Service
**Purpose:** Process Stripe webhook events

**Responsibilities:**
- Validate Stripe webhook signature
- Parse event payload
- Implement idempotent processing (prevent duplicate event handling)
- Update order status in database
- Trigger downstream actions (PDF generation, email)
- Publish events to Pub/Sub

**Technology:**
- Language: Python 3.12
- Framework: FastAPI 0.115+
- Container: Cloud Run (min 1, max 10 instances)
- Memory: 512MB
- CPU: 1 vCPU
- Concurrency: 20 requests/instance

**API Contract:**
```yaml
/webhooks/stripe:
  POST:
    summary: Handle Stripe webhook events
    headers:
      Stripe-Signature: string
    request: Stripe Event JSON
    response: { received: true }
```

**Handled Events:**
- `checkout.session.completed` - Payment successful, create order
- `checkout.session.expired` - Checkout abandoned
- `payment_intent.succeeded` - Payment confirmed
- `payment_intent.payment_failed` - Payment failed

**Idempotency:**
- Store event_id in database with status (processing|completed|failed)
- Check event_id before processing
- Use database transaction to ensure atomic state updates

**Downstream Actions:**
- Publish to `payment.completed` topic → PDF worker generates summary
- Update quote status to "paid"
- Send confirmation email via Resend

---

#### 5. Background Workers (Cloud Run Jobs)

**PDF Generation Worker:**
- Trigger: Pub/Sub message on `pdf.generate` topic
- Input: quote_id, order_id
- Process: Generate quote summary PDF, upload to GCS, send email
- Frequency: On-demand (event-driven)

**Email Worker:**
- Trigger: Pub/Sub message on `email.send` topic
- Input: recipient, template_id, data
- Process: Render email template (React Email), send via Resend
- Frequency: On-demand (event-driven)

**Data Retention Worker:**
- Trigger: Cron schedule (daily at 2 AM UTC)
- Process: Delete quotes >90 days old, anonymize user data per GDPR
- Frequency: Daily

---

### Database Schema (Cloud SQL - MySQL 8.0)

```sql
-- Users table
CREATE TABLE users (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  email_verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_email (email)
);

-- Quotes table
CREATE TABLE quotes (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  user_id CHAR(36) NOT NULL,
  file_url VARCHAR(1024) NOT NULL,  -- GCS path
  file_type VARCHAR(50) NOT NULL,   -- pdf, image
  status VARCHAR(50) NOT NULL,      -- uploaded, processing, analyzed, paid, failed
  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  processed_at TIMESTAMP NULL,
  
  -- Extracted data (JSON)
  extracted_data JSON NULL,
  extraction_confidence FLOAT NULL,
  
  -- Cost analysis (JSON)
  cost_analysis JSON NULL,
  
  -- GDPR: retention period
  expires_at TIMESTAMP GENERATED ALWAYS AS (DATE_ADD(uploaded_at, INTERVAL 90 DAY)) STORED,
  
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_user_id (user_id),
  INDEX idx_status (status),
  INDEX idx_expires_at (expires_at)
);

-- Orders table (Stripe payments)
CREATE TABLE orders (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  user_id CHAR(36) NOT NULL,
  quote_id CHAR(36) NOT NULL,
  stripe_session_id VARCHAR(255) UNIQUE NOT NULL,
  stripe_payment_intent_id VARCHAR(255) NULL,
  amount_cents INT NOT NULL,
  currency VARCHAR(3) DEFAULT 'usd',
  status VARCHAR(50) NOT NULL,  -- pending, paid, failed, refunded
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  paid_at TIMESTAMP NULL,
  
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (quote_id) REFERENCES quotes(id) ON DELETE CASCADE,
  INDEX idx_stripe_session (stripe_session_id),
  INDEX idx_status (status)
);

-- Webhook events (idempotency)
CREATE TABLE webhook_events (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  event_id VARCHAR(255) UNIQUE NOT NULL,  -- Stripe event ID
  event_type VARCHAR(100) NOT NULL,
  status VARCHAR(50) NOT NULL,  -- processing, completed, failed
  payload JSON NOT NULL,
  processed_at TIMESTAMP NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  INDEX idx_event_id (event_id),
  INDEX idx_status (status),
  INDEX idx_created_at (created_at)
);

-- Blacklisted tokens (JWT revocation)
CREATE TABLE blacklisted_tokens (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  jti VARCHAR(255) UNIQUE NOT NULL,  -- JWT ID
  user_id CHAR(36) NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  INDEX idx_jti (jti),
  INDEX idx_expires_at (expires_at)
);
```

---

### Infrastructure as Code (Terraform)

**Directory Structure:**
```
infra/
├── terraform/
│   ├── modules/
│   │   ├── cloud-run/          # Reusable Cloud Run service module
│   │   ├── cloud-sql/          # Cloud SQL + read replica
│   │   ├── redis/              # Memorystore Redis
│   │   ├── gcs/                # Storage buckets
│   │   ├── pubsub/             # Pub/Sub topics + subscriptions
│   │   ├── secrets/            # Secret Manager
│   │   └── iam/                # Service accounts + IAM roles
│   ├── environments/
│   │   ├── staging/
│   │   │   └── main.tf
│   │   └── production/
│   │       └── main.tf
│   └── backend.tf              # Remote state (GCS bucket)
```

**Key Resources:**
- Cloud Run services (API Gateway, Cost Model, Quote Extractor, Webhook Handler)
- Cloud SQL instance (MySQL 8.0, 2 vCPUs, 8GB RAM)
- Cloud SQL read replica (for analytics)
- Memorystore Redis (Standard tier, 1GB)
- GCS buckets (uploaded-quotes, generated-pdfs)
- Pub/Sub topics (quote.uploaded, payment.completed, pdf.generate)
- Secret Manager secrets (JWT_SECRET, STRIPE_SECRET, DB_PASSWORD)
- Service accounts (one per service, least privilege)
- VPC connector (private access to Cloud SQL)

---

### CI/CD Pipeline (GitHub Actions)

**Workflows:**

1. **PR Validation** (on pull_request)
   - Lint code (ruff, eslint)
   - Run unit tests
   - Run integration tests (against staging DB)
   - Security scan (bandit, npm audit)
   - Build Docker images (don't push)

2. **Staging Deployment** (on push to `develop` branch)
   - Build Docker images
   - Push to Artifact Registry
   - Run Terraform plan
   - Apply Terraform (staging environment)
   - Run smoke tests
   - Notify on Slack/Discord

3. **Production Deployment** (on push to `main` branch, requires approval)
   - Build Docker images (production tags)
   - Push to Artifact Registry
   - Run Terraform plan
   - **Manual approval required**
   - Apply Terraform (production environment)
   - Run E2E tests against production
   - Monitor error rates for 30 minutes
   - Rollback if error rate >1%

**Secrets (GitHub Actions):**
- `GCP_SERVICE_ACCOUNT_KEY` - Service account for Terraform + deployments
- `SENTRY_DSN` - Error tracking
- `SLACK_WEBHOOK` - Deployment notifications

---

### Security Architecture

#### Secrets Management
- **ALL secrets** in Google Secret Manager
- **NO secrets** in environment variables
- **NO secrets** in openclaw.json or config files
- Runtime secret fetching via Secret Manager API
- Automatic secret rotation (monthly for sensitive keys)

**Secrets Inventory:**
- JWT_SECRET_KEY (256-bit random)
- CSRF_SECRET_KEY (separate from JWT)
- DATABASE_PASSWORD (Cloud SQL)
- REDIS_PASSWORD (Memorystore)
- STRIPE_SECRET_KEY (live + test)
- STRIPE_WEBHOOK_SECRET (live + test)
- RESEND_API_KEY
- GOOGLE_VISION_API_KEY (service account JSON)
- SENTRY_DSN

#### Authentication & Authorization
- **JWT tokens** (access: 15min TTL, refresh: 7 days TTL)
- Token blacklist (for logout/revocation)
- Password hashing: bcrypt (cost factor 12)
- Email verification required before first quote upload
- Rate limiting: 5 failed login attempts → 15min lockout

#### Data Protection
- **Encryption at rest:** All GCS, Cloud SQL, Redis (Google-managed keys)
- **Encryption in transit:** TLS 1.3 everywhere
- **GDPR compliance:**
  - Data retention: 90 days for quotes, 7 years for orders (tax)
  - Right to erasure: User deletion anonymizes data
  - Data export: API endpoint for user data dump

#### Network Security
- **VPC:** All services in private VPC, no public IPs
- **Cloud SQL:** Private IP only, no public access
- **Redis:** VPC peering, no public access
- **Cloud Run:** Ingress restricted (only from load balancer)
- **DDoS protection:** Cloud Armor (WAF)

#### Input Validation
- **All endpoints:** Pydantic models for request validation
- **File uploads:** Magic number validation (not just extension)
- **SQL injection:** Parameterized queries only (SQLAlchemy ORM)
- **XSS prevention:** React auto-escaping + CSP headers
- **CSRF protection:** Token validation on all state-changing requests

---

### Monitoring & Observability

#### Metrics (Cloud Monitoring)
- **Golden Signals:**
  - Latency: p50, p95, p99 response times per endpoint
  - Traffic: Requests per second
  - Errors: Error rate (4xx, 5xx)
  - Saturation: CPU, memory, DB connections

- **Business Metrics:**
  - Quote uploads per hour
  - Successful vs failed extractions
  - Average processing time
  - Conversion rate (uploads → payments)
  - Revenue (Stripe webhooks)

#### Logging (Cloud Logging)
- **Structured logs** (JSON format)
- **Log levels:** DEBUG (staging), INFO (production)
- **Security audit log:** All auth events, payment events, data access
- **Retention:** 30 days (standard), 1 year (audit logs)

#### Error Tracking (Sentry)
- **All unhandled exceptions** sent to Sentry
- **Context:** User ID, request ID, stack trace
- **Alerts:** Critical errors → Slack/PagerDuty

#### Tracing (Cloud Trace)
- **Distributed tracing** across all services
- **Trace sampling:** 10% in production, 100% in staging
- **Integration:** OpenTelemetry SDK

---

### Stripe Integration Architecture

#### Checkout Flow (Embedded)
```javascript
// Frontend (Next.js)
const handleCheckout = async (quoteId) => {
  // 1. Create Checkout session
  const response = await fetch(`/api/quotes/${quoteId}/checkout`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${accessToken}` }
  });
  const { checkout_session_id } = await response.json();
  
  // 2. Embed Stripe Checkout (not redirect)
  const stripe = await loadStripe(process.env.NEXT_PUBLIC_STRIPE_KEY);
  const { error } = await stripe.redirectToCheckout({
    sessionId: checkout_session_id
  });
  
  if (error) {
    // Handle error
  }
};
```

#### Backend Checkout Session Creation
```python
# API Gateway: /api/quotes/{quote_id}/checkout
@router.post("/{quote_id}/checkout")
async def create_checkout_session(
    quote_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Verify quote belongs to user
    quote = db.query(Quote).filter_by(id=quote_id, user_id=current_user.id).first()
    if not quote:
        raise HTTPException(404, "Quote not found")
    
    # 2. Calculate price
    amount_cents = calculate_service_fee(quote.cost_analysis)
    
    # 3. Create Stripe Checkout session
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': f'Quote Analysis - {quote_id}',
                    'description': 'Ungouge.ai contractor quote verification'
                },
                'unit_amount': amount_cents,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=f'{FRONTEND_URL}/quotes/{quote_id}/success',
        cancel_url=f'{FRONTEND_URL}/quotes/{quote_id}',
        client_reference_id=quote_id,
        metadata={
            'quote_id': quote_id,
            'user_id': current_user.id
        }
    )
    
    # 4. Store session ID in orders table
    order = Order(
        user_id=current_user.id,
        quote_id=quote_id,
        stripe_session_id=session.id,
        amount_cents=amount_cents,
        status='pending'
    )
    db.add(order)
    db.commit()
    
    return {
        'checkout_session_id': session.id,
        'url': session.url
    }
```

#### Webhook Handler (Idempotent)
```python
# Webhook Handler Service: /webhooks/stripe
@app.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    # 1. Verify signature
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(400, "Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(400, "Invalid signature")
    
    # 2. Check for duplicate event (idempotency)
    existing = db.query(WebhookEvent).filter_by(event_id=event.id).first()
    if existing:
        if existing.status == 'completed':
            return {'received': True}  # Already processed
        elif existing.status == 'processing':
            raise HTTPException(409, "Event already processing")
        # If failed, allow retry
    
    # 3. Create webhook event record (mark as processing)
    webhook_event = WebhookEvent(
        event_id=event.id,
        event_type=event.type,
        status='processing',
        payload=event
    )
    db.add(webhook_event)
    db.commit()
    
    # 4. Handle event
    try:
        if event.type == 'checkout.session.completed':
            session = event.data.object
            quote_id = session.metadata.get('quote_id')
            
            # Update order status
            order = db.query(Order).filter_by(
                stripe_session_id=session.id
            ).first()
            order.status = 'paid'
            order.stripe_payment_intent_id = session.payment_intent
            order.paid_at = datetime.utcnow()
            
            # Update quote status
            quote = db.query(Quote).filter_by(id=quote_id).first()
            quote.status = 'paid'
            
            db.commit()
            
            # Publish event to Pub/Sub for downstream processing
            publisher = pubsub_v1.PublisherClient()
            topic_path = publisher.topic_path(PROJECT_ID, 'payment.completed')
            message_data = json.dumps({
                'quote_id': quote_id,
                'order_id': str(order.id),
                'user_id': order.user_id
            }).encode('utf-8')
            publisher.publish(topic_path, data=message_data)
        
        # Mark webhook event as completed
        webhook_event.status = 'completed'
        webhook_event.processed_at = datetime.utcnow()
        db.commit()
        
    except Exception as e:
        # Mark as failed, log error
        webhook_event.status = 'failed'
        db.commit()
        raise
    
    return {'received': True}
```

---

### Deployment Strategy

#### Environment Progression
1. **Local Development**
   - Docker Compose for backend services
   - Local MySQL + Redis
   - Next.js dev server
   - Stripe CLI for webhook testing

2. **Staging** (staging.ungouge.ai)
   - Full GCP infrastructure (smaller instance sizes)
   - Stripe TEST mode
   - Seeded test data
   - Used for QA, E2E testing, demos

3. **Production** (ungouge.ai)
   - Full GCP infrastructure (production sizing)
   - Stripe LIVE mode
   - Blue/green deployment for zero-downtime
   - Canary releases (10% traffic → 50% → 100%)

#### Rollback Procedure
1. Detect issue (error rate spike, Sentry alerts)
2. Revert Cloud Run services to previous revision
3. If database migration was applied, run rollback migration
4. Notify team on Slack
5. Post-mortem within 24 hours

---

### Cost Estimation

**Monthly GCP Costs (Production):**
- Cloud Run (5 services, avg 2-5 instances): ~$200-400
- Cloud SQL (db-n1-standard-2, 100GB): ~$150
- Cloud SQL read replica: ~$100
- Memorystore Redis (1GB Standard): ~$50
- GCS (1TB storage, 10TB egress): ~$50
- Pub/Sub (10M messages/month): ~$10
- Cloud Monitoring + Logging: ~$50
- **Total: ~$600-800/month**

**Additional Costs:**
- Vercel (Pro plan): $20/month
- Stripe (2.9% + $0.30 per transaction)
- Resend (email): $20/month (10k emails)
- Sentry (Team plan): $26/month
- **Total: ~$66/month + transaction fees**

**Grand Total: ~$670-870/month**

---

### Success Metrics

**Technical:**
- API latency p95 <500ms
- Quote extraction success rate >95%
- Cost model accuracy ±10% of actual costs
- System uptime 99.9% (SLA)
- Zero critical vulnerabilities (security scans)

**Business:**
- 1000 quotes analyzed/month (month 1)
- 10% conversion rate (upload → payment)
- Average processing time <60 seconds
- Customer satisfaction score >4.5/5

---

## Implementation Roadmap

**Phase 0: Architecture & Design** (COMPLETE)
- ✅ Architecture document (this file)
- ⏳ OpenAPI specs (in progress)
- ⏳ Database migration scripts
- ⏳ Terraform modules

**Phase 1: Core Services** (1-2 weeks)
- [ ] Extract cost model from monolith → standalone service
- [ ] Build quote extractor service (Vision API + NLP)
- [ ] Refactor API gateway (auth, routing, rate limiting)
- [ ] Build webhook handler (Stripe integration)
- [ ] Unit + integration tests (>80% coverage)

**Phase 2: Infrastructure** (3-5 days)
- [ ] Terraform all GCP resources (staging + production)
- [ ] Set up CI/CD (GitHub Actions)
- [ ] Migrate secrets to Secret Manager
- [ ] Configure monitoring + alerting

**Phase 3: Frontend** (1 week)
- [ ] Upgrade to Next.js 15 App Router
- [ ] Implement Stripe Checkout (embedded UI)
- [ ] Build quote upload flow
- [ ] Build dashboard (order history, receipts)
- [ ] Transactional emails (React Email + Resend)

**Phase 4: Testing & Launch** (3-5 days)
- [ ] E2E testing (Playwright)
- [ ] Load testing (1000 concurrent users)
- [ ] Security audit (OWASP ZAP, manual pentest)
- [ ] Staging smoke tests
- [ ] **Production launch** 🚀

---

**Total Timeline:** 3-4 weeks (with parallel work, Opus 4.6 Ultra + sub-agents)

**Next Steps:**
1. Review & approve this architecture
2. Generate OpenAPI specs for all services
3. Start Phase 1 implementation (service extraction)

---

*This document is a living architecture. Update as design evolves.*
