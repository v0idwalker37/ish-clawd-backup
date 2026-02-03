# Ungouge.ai Architecture Documentation

> **Why we built it this way** - Tech stack decisions, design patterns, and system architecture

**Last Updated:** 2024-02-02  
**Current Version:** 1.0.0

---

## Table of Contents

- [Tech Stack Overview](#tech-stack-overview)
- [Why Next.js + FastAPI?](#why-nextjs--fastapi)
- [Why Gemini Vision?](#why-gemini-vision)
- [Database Design](#database-design)
- [Authentication Strategy](#authentication-strategy)
- [Cost Model System](#cost-model-system)
- [Security Architecture](#security-architecture)
- [Deployment Architecture](#deployment-architecture)
- [Trade-offs & Alternatives](#trade-offs--alternatives)

---

## Tech Stack Overview

### Frontend: Next.js 14 (App Router) + TypeScript

**Components:**
- **Framework:** Next.js 14.2
- **Language:** TypeScript 5.4+
- **Styling:** Tailwind CSS 3.4
- **Forms:** React Hook Form + Zod
- **HTTP Client:** Axios
- **Icons:** Lucide React
- **Animation:** Framer Motion

### Backend: FastAPI + Python 3.11

**Components:**
- **Framework:** FastAPI 0.109
- **Language:** Python 3.11+
- **Validation:** Pydantic v2
- **Database:** SQLAlchemy 2.0 (async)
- **Auth:** JWT (python-jose)
- **Password Hashing:** bcrypt (passlib)
- **Rate Limiting:** SlowAPI
- **Security:** fastapi-csrf-protect

### Data Layer

**Components:**
- **Primary Database:** PostgreSQL 14+
- **Dev Database:** SQLite (aiosqlite)
- **ORM:** SQLAlchemy 2.0 (async)
- **Migrations:** Alembic

### External Services

**Components:**
- **AI Parsing:** Google Gemini 2.0 Flash
- **Payments:** Stripe
- **Email:** SendGrid / SMTP
- **Cost Data:** Craftsman National Construction Estimator API
- **Wage Data:** BLS (Bureau of Labor Statistics) API

---

## Why Next.js + FastAPI?

### The Decision

We chose a **decoupled architecture** with separate frontend and backend rather than a monolithic framework (Django, Rails, etc.).

### Reasoning

#### Why Next.js?

1. **Modern React patterns** - App Router provides excellent developer experience
2. **TypeScript by default** - Type safety across the entire frontend
3. **Performance** - Built-in optimizations (image optimization, code splitting)
4. **SEO-friendly** - Server-side rendering for landing pages
5. **Deployment** - Seamless Vercel hosting (zero-config)
6. **Ecosystem** - Huge React ecosystem for components

**Alternatives considered:**
- ❌ **SvelteKit** - Smaller ecosystem, less contractor-friendly
- ❌ **Remix** - Too new, uncertain future at the time
- ❌ **Create React App** - No SSR, deprecated by React team
- ✅ **Next.js** - Best balance of features, ecosystem, and performance

#### Why FastAPI?

1. **Speed** - One of the fastest Python frameworks (async support)
2. **Type Safety** - Pydantic models provide runtime validation + docs
3. **Auto-docs** - OpenAPI/Swagger docs generated automatically
4. **Modern Python** - Leverages Python 3.11+ features (type hints, async/await)
5. **Easy AI integration** - Simple to integrate with OpenAI, Gemini, etc.
6. **Developer experience** - Hot reload, excellent error messages

**Alternatives considered:**
- ❌ **Django** - Too heavy, ORM conflicts with async patterns
- ❌ **Flask** - Less modern, no built-in validation/docs
- ❌ **Node.js (Express)** - Python has better AI/ML libraries
- ✅ **FastAPI** - Best for AI-heavy, data-driven APIs

#### Why Separate Frontend + Backend?

**Advantages:**
- **Independent scaling** - Scale backend separately from frontend
- **Technology flexibility** - Can swap frontend without touching backend
- **Team parallelization** - Frontend & backend can develop independently
- **Best tool for each job** - Python excels at data/AI, JS excels at UI
- **API-first** - Easy to add mobile apps or third-party integrations later

**Trade-offs:**
- ⚠️ **More complexity** - Two codebases, two deployments
- ⚠️ **CORS setup** - Must configure cross-origin requests
- ⚠️ **Two servers** - More infrastructure vs monolith

**Why it's worth it:**
For an AI-heavy application like Ungouge, having Python on the backend is essential. The complexity trade-off is minimal with modern deployment platforms (Vercel, Railway).

---

## Why Gemini Vision?

### The Migration

Originally started with **OpenAI GPT-4** for quote parsing. Migrated to **Google Gemini 2.0 Flash** in February 2024.

### Why Gemini?

#### 1. **Accuracy** (Most Important)

Gemini Vision's document understanding is **significantly better** than GPT-4o for contractor quotes:

**Problem with GPT-4o + OCR:**
```
Text extraction → OCR (Tesseract) → GPT-4 text parsing
```
- OCR frequently misreads quantities (20 squares → 2.0 squares)
- Poor handling of complex layouts (columns, tables)
- Misses fine print and subtotals

**Gemini Vision Direct Processing:**
```
Image → Gemini Vision → Structured JSON
```
- Understands visual layout (tables, columns)
- Reads small text accurately
- Correctly extracts quantities and units
- Handles handwritten notes

**Real example:**
```
Quote line: "20 sq. @ $175/sq = $3,500"

GPT-4o + OCR extracted:
  quantity: 2.0
  unit: "unknown"
  price: 3500

Gemini Vision extracted:
  quantity: 20
  unit: "square"
  price: 175 (per unit)
  total: 3500
```

#### 2. **Cost** (97% Cheaper)

| Provider | Model | Cost per 1M Tokens | Typical Quote Cost |
|----------|-------|-------------------|--------------------|
| OpenAI | GPT-4o | $2.50 | $0.025 |
| Google | Gemini 2.0 Flash | $0.075 | $0.00075 |

**Annual savings at 10,000 quotes:**
- GPT-4o: $250
- Gemini: $7.50
- **Savings: $242.50/year** (irrelevant at this scale, but the accuracy is a dealbreaker)

#### 3. **Speed**

Gemini 2.0 Flash is **optimized for speed**:
- Average response time: 2-3 seconds
- GPT-4o: 5-7 seconds
- **Better user experience** - Faster quote analysis

#### 4. **Vision-Native Architecture**

Gemini was **designed for multimodal input** (text + images):
- Handles PDFs with complex layouts
- Processes multi-page documents
- Understands document context better

### Trade-offs

**What we gave up:**
- ⚠️ **Model maturity** - OpenAI has more public usage/testing
- ⚠️ **Ecosystem** - Fewer third-party tools for Gemini
- ⚠️ **Prompt engineering resources** - Less documentation online

**Why it's worth it:**
For a document-heavy application where **accuracy is critical**, Gemini's vision capabilities are irreplaceable. Wrong quantities = wrong analysis = unhappy customers.

### Implementation

See `backend/services/quote_parser_gemini.py` for implementation details.

**Key features:**
- Direct vision processing (no OCR)
- PDF to image conversion (pdf2image)
- Structured JSON output (Pydantic validation)
- Fallback to text parsing if vision fails

---

## Database Design

### Why PostgreSQL?

**For Production:**
1. **Relational data** - Users, quotes, line items have clear relationships
2. **ACID compliance** - Financial data (payments) needs transactions
3. **JSON support** - Can store flexible data (quote metadata) when needed
4. **Scalability** - Proven at massive scale
5. **Tooling** - Excellent backup, monitoring, and management tools

**Alternatives considered:**
- ❌ **MongoDB** - Overkill for relational data, harder to query
- ❌ **MySQL** - Less powerful JSON support, weaker async support
- ✅ **PostgreSQL** - Best balance of features, performance, reliability

### Why SQLite for Development?

**For Local Development:**
1. **Zero setup** - No database server needed
2. **Fast iteration** - Instant startup, easy to reset
3. **Portable** - Database is a single file
4. **Same SQL** - Same queries work in both SQLite and PostgreSQL

**When to use which:**
- **Local dev:** SQLite (`sqlite+aiosqlite:///./ungouge.db`)
- **Staging:** PostgreSQL (Railway/Supabase)
- **Production:** PostgreSQL (managed service)

### Schema Design

**Key tables:**

#### Users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Quotes
```sql
CREATE TABLE quotes (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    contractor_name VARCHAR(255),
    project_type VARCHAR(100),
    location VARCHAR(255),
    total_amount DECIMAL(10,2),
    status VARCHAR(50),  -- 'processing', 'completed', 'failed'
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Line Items
```sql
CREATE TABLE line_items (
    id UUID PRIMARY KEY,
    quote_id UUID REFERENCES quotes(id) ON DELETE CASCADE,
    item_name VARCHAR(255),
    description TEXT,
    quantity INTEGER,
    unit VARCHAR(50),
    quoted_price DECIMAL(10,2),
    fair_price DECIMAL(10,2),
    analysis_notes TEXT,
    rating VARCHAR(20)  -- 'fair', 'high', 'gouged'
);
```

**Design decisions:**
- **UUIDs over auto-increment IDs** - Better for distributed systems, no enumeration attacks
- **Cascade deletes** - Delete quote → delete line items automatically
- **Separate line items table** - Normalized design, easier to query/analyze
- **DECIMAL for money** - Avoid floating point errors
- **VARCHAR limits** - Prevent abuse, enforce data quality

---

## Authentication Strategy

### Why JWT?

**Chosen approach:** JWT (JSON Web Tokens) with blacklist

**Advantages:**
1. **Stateless** - No server-side session storage needed
2. **Scalable** - Works across multiple backend instances
3. **Mobile-friendly** - Easy to implement in mobile apps
4. **Standard** - Well-understood, many libraries

**Disadvantages:**
- ⚠️ **Can't revoke tokens** - Without blacklist
- ⚠️ **Token size** - Larger than session IDs

**Solution: Token Blacklist**

We implement a **token blacklist** to handle logout:
- When user logs out, token is added to blacklist
- Blacklist stored in-memory (production: Redis)
- Expired tokens automatically cleaned up
- Provides logout functionality without losing JWT benefits

**Alternatives considered:**
- ❌ **Session cookies** - Requires server-side storage, harder to scale
- ❌ **OAuth only** - Too complex for initial MVP, adds third-party dependency
- ✅ **JWT + blacklist** - Best balance of simplicity and security

### Security Measures

1. **Password hashing** - bcrypt with 12 rounds (slow = secure)
2. **Token expiration** - 7 days default (configurable)
3. **Refresh tokens** - Planned for future (rotate tokens without re-login)
4. **Email verification** - Required before full access
5. **Password reset** - Secure token-based flow

See `backend/services/auth.py` for implementation.

---

## Cost Model System

### Architecture

The cost model system is the **core of Ungouge's value proposition**. It determines what a "fair price" is.

### Data Sources

#### 1. BLS Wage Data
**Source:** U.S. Bureau of Labor Statistics  
**What it provides:** Hourly wage rates by trade  
**Update frequency:** Quarterly (manual updates for now)

Example:
```json
{
  "carpenter": {
    "median_hourly_wage": 27.00,
    "mean_hourly_wage": 28.50,
    "source": "BLS Occupational Employment Statistics"
  }
}
```

#### 2. Craftsman Cost Database
**Source:** Craftsman National Construction Estimator API  
**What it provides:** Detailed material + labor costs by project type  
**Update frequency:** Real-time API calls

Example:
```json
{
  "roof_replacement": {
    "line_items": {
      "asphalt_shingles_architectural": {
        "material_cost": 135.00,
        "unit": "square",
        "labor_hours": 2.5,
        "labor_cost": 67.50
      }
    }
  }
}
```

#### 3. Regional Multipliers
**Source:** Manual research + cost-of-living indices  
**What it provides:** Location-based cost adjustments

Example:
```json
{
  "california": {
    "multiplier": 1.35,
    "zip_prefixes": ["9"],
    "notes": "High cost of living, stringent building codes"
  }
}
```

### Analysis Engine

**Location:** `backend/services/analyzer.py`

**Process:**
1. **Parse quote** - Extract line items via Gemini Vision
2. **Categorize items** - Fuzzy match to cost database categories
3. **Look up costs** - Get fair price from Craftsman API + BLS data
4. **Apply regional multiplier** - Adjust for location
5. **Calculate markup** - Compare quoted vs. fair price
6. **Assign rating** - Fair (0-15%), High (15-30%), Gouged (30%+)
7. **Generate report** - Line-by-line analysis + summary

**Key algorithm:**
```python
def calculate_fair_price(item):
    base_cost = craftsman_api.get_cost(item.category)
    labor_cost = bls_rate * hours * regional_multiplier
    material_cost = base_cost * quantity * regional_multiplier
    overhead = (labor_cost + material_cost) * 0.15  # 15% overhead
    profit = (labor_cost + material_cost) * 0.10    # 10% profit
    return labor_cost + material_cost + overhead + profit
```

**Industry-standard markups:**
- Overhead: 12-18% (we use 15%)
- Profit: 8-12% (we use 10%)
- **Total fair markup: 25-30%**

Anything above 30% total markup is flagged as "high" or "gouged."

### Adding New Cost Models

See [README.md - Cost Model System](README.md#cost-model-system) for details.

---

## Security Architecture

### Threat Model

**What we're protecting against:**
1. **Unauthorized access** - Users accessing other users' quotes
2. **Data breaches** - Sensitive quote data leaking
3. **Payment fraud** - Fake payments, stolen cards
4. **DDoS attacks** - Service disruption
5. **Injection attacks** - SQL injection, XSS
6. **CSRF attacks** - Cross-site request forgery
7. **Enumeration attacks** - Guessing user IDs, quote IDs

### Defense Layers

#### Layer 1: Input Validation
- **Pydantic models** - Type validation + sanitization
- **Zod schemas** - Frontend validation
- **File type checking** - Only PDF/images allowed
- **Size limits** - 10MB max upload

#### Layer 2: Authentication & Authorization
- **JWT tokens** - Secure, signed tokens
- **Token blacklist** - Logout support
- **Password hashing** - bcrypt (slow hash)
- **Email verification** - Prevent fake accounts

#### Layer 3: Rate Limiting
- **SlowAPI** - 100 requests/minute default
- **Per-endpoint limits** - Stricter on auth endpoints
- **IP-based tracking** - Block abusive IPs

#### Layer 4: CSRF Protection
- **CSRF tokens** - Required for state-changing requests
- **SameSite cookies** - Prevent cross-site requests
- **Double-submit pattern** - Token in cookie + header

#### Layer 5: Security Headers
- **HSTS** - Force HTTPS
- **X-Frame-Options** - Prevent clickjacking
- **X-Content-Type-Options** - Prevent MIME sniffing
- **CSP** - Content Security Policy

#### Layer 6: Database Security
- **ORM (SQLAlchemy)** - Prevents SQL injection
- **Parameterized queries** - No string concatenation
- **Least privilege** - Database user has minimal permissions
- **Connection pooling** - Prevent connection exhaustion

See `SECURITY_COMPLETE.md` for full security audit.

---

## Deployment Architecture

### Recommended Setup (Railway.app)

```
┌─────────────────────────────────────────────────┐
│                   Internet                       │
└────────────┬────────────────────┬────────────────┘
             │                    │
    ┌────────▼────────┐  ┌────────▼────────┐
    │  Vercel CDN     │  │  Railway Apps   │
    │  (Frontend)     │  │  (Backend)      │
    │                 │  │                 │
    │  Next.js Static │  │  FastAPI Server │
    │  + Edge SSR     │  │  + PostgreSQL   │
    └─────────────────┘  │  + Redis        │
                         └─────────────────┘
```

**Why this setup:**
- **Vercel** - Zero-config Next.js deployment, global CDN
- **Railway** - Easy PostgreSQL + Redis provisioning
- **Redis** - Fast token blacklist (production)
- **PostgreSQL** - Managed database with automated backups

### Alternative: AWS (More Complex)

```
┌─────────────────────────────────────────────────┐
│             Route 53 (DNS)                      │
└────────────┬─────────────────────────────────────┘
             │
    ┌────────▼────────┐
    │  CloudFront     │  (CDN)
    └────┬───────┬────┘
         │       │
         │       └──────────────┐
         │                      │
┌────────▼────────┐    ┌────────▼─────────┐
│  S3 Bucket      │    │  ALB (Load       │
│  (Static)       │    │  Balancer)       │
└─────────────────┘    └────────┬─────────┘
                               │
                      ┌────────▼─────────┐
                      │  ECS/Fargate     │
                      │  (Backend)       │
                      └────────┬─────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
    ┌───────────▼─────┐  ┌────▼─────┐  ┌─────▼─────┐
    │  RDS            │  │ElastiCache│  │  S3       │
    │  (PostgreSQL)   │  │  (Redis)  │  │  (Files)  │
    └─────────────────┘  └───────────┘  └───────────┘
```

**Why AWS is overkill (for now):**
- More expensive ($100+/month vs $20/month)
- More complex setup (days vs hours)
- Over-engineered for current scale

**When to migrate to AWS:**
- 100,000+ users
- Need multi-region deployment
- Require custom infrastructure

---

## Trade-offs & Alternatives

### What We Didn't Choose (And Why)

#### Monolithic Frameworks

**Option:** Django, Ruby on Rails  
**Why not:**
- Python on frontend is not ideal (Django templates)
- Harder to integrate modern React patterns
- Backend + frontend tightly coupled
- Python AI libraries > Ruby ecosystem

#### Serverless (AWS Lambda, Vercel Functions)

**Why not (yet):**
- Cold starts hurt user experience
- More complex state management
- Harder to debug
- Better for high-scale, not early-stage

**When to reconsider:**
- 1M+ users
- Need extreme scalability
- Willing to rewrite parts of the app

#### Microservices

**Why not:**
- Massive overkill for a 2-person team
- Adds operational complexity
- Harder to develop locally
- No performance benefit at this scale

**When to reconsider:**
- Team size 10+
- Clear service boundaries (user service, quote service, etc.)
- Need independent deployment cycles

#### NoSQL (MongoDB, DynamoDB)

**Why not:**
- Relational data (users → quotes → line items)
- Need ACID transactions (payments)
- SQL query flexibility
- Harder to maintain data consistency

**When to reconsider:**
- Need extreme scale (10M+ users)
- Schemaless data (unlikely for our use case)

---

## Future Architecture Considerations

### When to Scale (10,000+ Users)

1. **Add caching** - Redis for frequently accessed data
2. **Horizontal scaling** - Multiple backend instances + load balancer
3. **CDN for uploads** - S3 + CloudFront for quote PDFs
4. **Message queue** - Celery for async quote processing
5. **Read replicas** - PostgreSQL read replicas for analytics

### When to Refactor (100,000+ Users)

1. **Separate services** - User service, quote service, payment service
2. **Event-driven architecture** - Kafka/RabbitMQ for inter-service communication
3. **Dedicated search** - Elasticsearch for quote search
4. **Real-time features** - WebSockets for live quote updates

---

## Questions for Future Developers

**"Why didn't you use X?"**  
→ Check this doc. If it's not here, it probably wasn't considered. Feel free to revisit.

**"Should I rewrite this in Y?"**  
→ Probably not. The current stack works well. Focus on features, not rewrites.

**"Can I add Z dependency?"**  
→ Sure, but ask: Does it solve a real problem? Is it maintained? Does it add significant value?

---

## Conclusion

This architecture prioritizes:
1. **Developer experience** - Fast iteration, good tooling
2. **Accuracy** - Correct analysis is #1 priority
3. **Simplicity** - Prefer boring tech over bleeding edge
4. **Cost-efficiency** - Optimize for $20/month, not $2000/month
5. **Future flexibility** - Easy to scale when needed

**Remember:** Perfect is the enemy of shipped. This architecture gets us to market fast while staying maintainable.

---

**Last updated:** 2024-02-02  
**Next review:** When we hit 10,000 users or someone complains about performance
