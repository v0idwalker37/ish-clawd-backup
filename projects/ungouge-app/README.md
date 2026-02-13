<p align="center">
  <!-- Replace with actual logo when available -->
  <img src="frontend/public/android-chrome-512x512.png" alt="UnGouge.ai Logo" width="120" />
</p>

<h1 align="center">UnGouge.ai</h1>
<p align="center"><strong>Independent Quote Verification for Homeowners</strong></p>
<p align="center">
  <em>Pay $19.99. Get the truth about your contractor's quote. No lead gen. No hidden agenda.</em>
</p>

<p align="center">
  <a href="https://ungouge.ai">Website</a> •
  <a href="#getting-started">Getting Started</a> •
  <a href="#api-endpoints">API Docs</a> •
  <a href="DEPLOY_CHECKLIST.md">Deploy</a> •
  <a href="SECURITY_PENTEST_REPORT.md">Security</a>
</p>

---

## What is UnGouge?

UnGouge.ai is a **data-driven contractor quote analysis service** that helps homeowners answer one simple question: *"Is this quote fair?"*

You upload or enter your contractor's quote — materials, labor, line items, the whole thing — and UnGouge analyzes it against real-world cost data from RSMeans, BLS labor rates, and regional pricing models. Within minutes you get a detailed report showing where you're getting a fair deal, where you're overpaying, and what to negotiate. It costs **$19.99 per report**, and that's the entire business model.

Unlike every other tool in this space, UnGouge doesn't sell your data to contractors, doesn't generate "leads," and doesn't take referral fees. The free quote-comparison sites make money by selling your phone number to five contractors who call you relentlessly. We make money when you pay us $19.99 for an honest analysis. Our incentives are aligned with yours: giving you accurate information so you come back next time and tell your friends.

The platform is built for transparency and privacy. GDPR-compliant by design, with PII encryption at rest, automatic data retention cleanup, and full data portability. Your quote data belongs to you.

---

## Tech Stack

| Layer | Technology | Details |
|-------|-----------|---------|
| **Frontend** | Next.js 14 + React 18 | TypeScript, Tailwind CSS, Framer Motion |
| **Backend** | FastAPI (Python 3.11) | Async, Pydantic v2, SQLAlchemy 2.0 |
| **Database** | SQLite (dev) / PostgreSQL 15 (prod) | asyncpg, Alembic migrations |
| **AI / Analysis** | OpenAI · Anthropic Claude · Google Gemini | Multi-provider with fallback chain |
| **OCR** | Tesseract + pdf2image | Quote upload parsing from PDF/images |
| **Payments** | Stripe Checkout | $19.99 per report, webhook-driven |
| **Auth** | JWT (httpOnly cookies) | Access + refresh tokens, MFA (email OTP) |
| **Email** | aiosmtplib | SendGrid / SES / Mailgun compatible |
| **Hosting** | GCP Cloud Run (API) · Vercel (Frontend) | Docker, auto-scaling, managed SSL |
| **Security** | CSRF · CSP · Rate Limiting · AES-256 encryption | See [Security](#security) |
| **Cost Data** | RSMeans · BLS · HomeAdvisor · Census | Calibrated regional pricing models |

---

## Architecture

```
┌─────────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│                     │     │                      │     │                 │
│   Next.js Frontend  │────▶│   FastAPI Backend     │────▶│  PostgreSQL     │
│   (Vercel)          │     │   (GCP Cloud Run)    │     │  (Cloud SQL)    │
│                     │     │                      │     │                 │
└─────────────────────┘     └──────────┬───────────┘     └─────────────────┘
                                       │
                            ┌──────────┴───────────┐
                            │                      │
                    ┌───────▼──────┐   ┌───────────▼────────┐
                    │              │   │                    │
                    │  AI Analysis │   │  Stripe Payments   │
                    │  (OpenAI /   │   │  (Checkout +       │
                    │   Claude /   │   │   Webhooks)        │
                    │   Gemini)    │   │                    │
                    │              │   │                    │
                    └──────────────┘   └────────────────────┘
```

**Flow:** User submits quote → quote saved (unpaid) → user pays $19.99 via Stripe Checkout → Stripe webhook confirms payment → AI analysis runs → report generated and available.

---

## Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** (with npm)
- **Tesseract OCR** — `brew install tesseract` (macOS) or `apt install tesseract-ocr`
- **libmagic** — `brew install libmagic` (macOS) or `apt install libmagic1`
- **Poppler** — `brew install poppler` (macOS) or `apt install poppler-utils`

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-security.txt

# Configure environment
cp .env.example .env
# Edit .env — set at minimum:
#   JWT_SECRET_KEY, CSRF_SECRET_KEY, STRIPE_SECRET_KEY,
#   STRIPE_WEBHOOK_SECRET, OPENAI_API_KEY, ENCRYPTION_KEY

# Run development server
uvicorn main:app --reload --port 8000
```

The API is now running at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local:
#   NEXT_PUBLIC_API_URL=http://localhost:8000
#   NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...

# Run development server
npm run dev
```

The frontend is now running at `http://localhost:3000`.

### Database

- **Development:** SQLite — auto-created as `backend/ungouge.db` on first run. Zero config.
- **Production:** PostgreSQL 15+ via Cloud SQL. Set `DATABASE_URL` to an `asyncpg` connection string. See [DEPLOY_CHECKLIST.md](DEPLOY_CHECKLIST.md#2-database-setup--migrations).

### Stripe (Local Testing)

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Forward webhooks to local server
stripe listen --forward-to localhost:8000/api/payments/webhook

# In another terminal, trigger test events
stripe trigger checkout.session.completed
```

---

## Project Structure

```
ungouge-app/
├── backend/
│   ├── main.py                  # FastAPI app, middleware, startup
│   ├── requirements.txt         # Python dependencies
│   ├── requirements-security.txt
│   ├── routers/
│   │   ├── auth.py              # Authentication & GDPR endpoints
│   │   ├── quotes.py            # Quote submission, retrieval, PDF
│   │   ├── payments.py          # Stripe checkout & webhooks
│   │   └── health.py            # Health / readiness / liveness probes
│   ├── models/
│   │   ├── database.py          # SQLAlchemy models (User, Quote, Payment, etc.)
│   │   ├── auth.py              # Pydantic request/response schemas
│   │   ├── quote.py             # Quote schemas
│   │   └── report.py            # Analysis report schemas
│   ├── services/
│   │   ├── analyzer_v2.py       # Quote analysis engine (67.7% accuracy, 87% match)
│   │   ├── auth.py              # JWT, password hashing, token management
│   │   ├── payment.py           # Stripe integration
│   │   ├── email_service.py     # Transactional email (SMTP)
│   │   ├── encryption.py        # AES-256 PII encryption
│   │   ├── pdf_generator.py     # Report PDF generation (ReportLab)
│   │   ├── quote_parser.py      # OCR + file parsing for uploads
│   │   ├── quote_parser_gemini.py # Gemini-powered quote parsing
│   │   ├── mfa_service.py       # Multi-factor authentication (email OTP)
│   │   ├── bls_data.py          # BLS labor rate lookups
│   │   ├── synonym_matcher.py   # Line item → cost model matching
│   │   └── token_blacklist.py   # JWT revocation (logout)
│   ├── middleware/
│   │   ├── csrf.py              # CSRF protection
│   │   ├── rate_limit.py        # Rate limiting (slowapi)
│   │   ├── input_validation.py  # Input sanitization
│   │   ├── file_security.py     # Upload security (magic bytes, metadata strip)
│   │   ├── data_retention.py    # GDPR auto-cleanup (30-day TTL)
│   │   ├── dnt.py               # Do Not Track signal handling
│   │   └── security_logging.py  # Structured security audit logs
│   ├── data/
│   │   ├── project_cost_models.json    # RSMeans-calibrated pricing
│   │   ├── material_costs.json         # Material cost database
│   │   └── sample_bls_rates.json       # BLS labor rates
│   ├── templates/               # Email templates (HTML)
│   └── tests/                   # pytest test suite
│
├── frontend/
│   ├── package.json
│   ├── next.config.js           # CSP headers, security config
│   ├── tailwind.config.js
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx         # Landing page
│   │   │   ├── login/           # Login page
│   │   │   ├── register/        # Registration page
│   │   │   ├── analyze/         # Quote submission form
│   │   │   ├── report/[id]/     # Analysis report view
│   │   │   ├── dashboard/       # User dashboard (quotes, settings, account)
│   │   │   ├── pricing/         # Pricing page
│   │   │   ├── privacy/         # Privacy policy
│   │   │   └── terms/           # Terms of service
│   │   ├── components/
│   │   │   ├── QuoteForm.tsx    # Main quote input form
│   │   │   ├── FileUpload.tsx   # Drag-and-drop quote upload
│   │   │   ├── PriceGauge.tsx   # Visual price fairness gauge
│   │   │   ├── ReportCard.tsx   # Report display component
│   │   │   ├── Header.tsx       # Navigation header
│   │   │   ├── Footer.tsx       # Site footer
│   │   │   └── CookieConsent.tsx # GDPR cookie consent banner
│   │   └── middleware.ts        # Next.js middleware (auth, redirects)
│   └── public/                  # Static assets, favicons, sitemap
│
├── legal/                       # Legal documents
│   ├── PRIVACY_POLICY.md        # Full privacy policy
│   ├── TERMS_OF_SERVICE.md      # Terms of service
│   ├── GDPR_AUDIT_REPORT.md     # GDPR compliance audit
│   ├── ROPA.md                  # Records of Processing Activities
│   ├── DPA_REGISTER.md          # Data Processing Agreements
│   ├── INCIDENT_RESPONSE_PLAN.md
│   └── BACKUP_RECOVERY_PLAN.md
│
├── cost-data/                   # Pricing reference data
│   ├── rsmeans_extracted_data.json
│   ├── rsmeans_location_factors.json
│   ├── bls-labor-rates.json
│   ├── real-quotes.json
│   └── homeadvisor-cost-guides.json
│
├── content/                     # Marketing & blog content
│   ├── blog/                    # SEO blog posts (30+)
│   ├── marketing/               # Ad copy, email sequences
│   └── legal/                   # Content versions of legal pages
│
├── Dockerfile                   # Multi-stage production build
├── .dockerignore
├── .env.production.example      # All env vars documented
├── DEPLOY_CHECKLIST.md          # Full deployment guide
├── SECURITY_PENTEST_REPORT.md   # Security audit results
└── SECURITY_FIXES_SUMMARY.md    # Security implementation status
```

---

## API Endpoints

All API routes are prefixed with `/api` except health checks.

### Health

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/health` | — | Health check + DB status + version |
| `GET` | `/health/ready` | — | Readiness probe (DB connection) |
| `GET` | `/health/live` | — | Liveness probe |
| `GET` | `/api/health/detailed` | — | Full system status |

### Authentication

| Method | Endpoint | Auth | Rate Limit | Description |
|--------|----------|------|------------|-------------|
| `POST` | `/api/auth/register` | — | 3/hour | Create account |
| `POST` | `/api/auth/login` | — | — | Login (returns JWT) |
| `POST` | `/api/auth/refresh` | — | — | Refresh access token |
| `POST` | `/api/auth/logout` | ✅ | — | Logout (blacklist token) |
| `GET` | `/api/auth/me` | ✅ | — | Get current user profile |
| `PUT` | `/api/auth/me` | ✅ | — | Update user profile |
| `POST` | `/api/auth/forgot-password` | — | — | Request password reset email |
| `POST` | `/api/auth/reset-password` | — | — | Reset password with token |
| `POST` | `/api/auth/verify-email` | — | — | Verify email address |
| `POST` | `/api/auth/resend-verification` | — | — | Resend verification email |

### MFA (Multi-Factor Authentication)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/auth/mfa/status` | ✅ | Get MFA status |
| `POST` | `/api/auth/mfa/enable` | ✅ | Enable MFA (sends OTP) |
| `POST` | `/api/auth/mfa/verify-enable` | ✅ | Confirm MFA enable with OTP |
| `POST` | `/api/auth/mfa/disable` | ✅ | Disable MFA |
| `POST` | `/api/auth/mfa/resend` | — | Resend MFA OTP code |
| `POST` | `/api/auth/mfa/verify-login` | — | Verify MFA during login |

### GDPR / Privacy

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/auth/my-data` | ✅ | Data export (GDPR Art. 20) |
| `DELETE` | `/api/auth/my-data` | ✅ | Delete all data (GDPR Art. 17) |
| `PUT` | `/api/auth/my-data` | ✅ | Rectify personal data (GDPR Art. 16) |
| `POST` | `/api/auth/restrict` | ✅ | Restrict processing (GDPR Art. 18) |
| `POST` | `/api/auth/unrestrict` | ✅ | Lift restriction |
| `GET` | `/api/auth/preferences` | ✅ | Get privacy preferences |
| `PUT` | `/api/auth/preferences` | ✅ | Update privacy preferences (GDPR Art. 21) |

### Quotes

| Method | Endpoint | Auth | Rate Limit | Description |
|--------|----------|------|------------|-------------|
| `POST` | `/api/quotes` | ✅ | 10/hour | Submit a quote for analysis |
| `GET` | `/api/quotes` | ✅ | — | List all user's quotes |
| `GET` | `/api/quotes/my` | ✅ | — | Get user's quotes (alternate) |
| `GET` | `/api/quotes/{id}` | ✅ | — | Get quote + analysis report |
| `GET` | `/api/quotes/{id}/report` | ✅ | — | Get analysis report only |
| `GET` | `/api/quotes/{id}/pdf` | ✅ | — | Download report as PDF |
| `POST` | `/api/quotes/parse-upload` | ✅ | — | Upload quote file (PDF/image) for parsing |

### Payments

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/payments/create-checkout` | ✅ | Create Stripe Checkout Session ($19.99) |
| `POST` | `/api/payments/webhook` | — | Stripe webhook (signature-verified) |

### Root

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API info + version |

Interactive API docs available at `/docs` (Swagger UI) and `/redoc` (ReDoc).

---

## Environment Variables

All environment variables are fully documented in [`.env.production.example`](.env.production.example).

**Quick reference:**

| Category | Key Variables |
|----------|--------------|
| **General** | `ENVIRONMENT`, `FRONTEND_URL` |
| **Database** | `DATABASE_URL`, `DATABASE_ECHO` |
| **Auth** | `JWT_SECRET_KEY`, `CSRF_SECRET_KEY` |
| **Stripe** | `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET` |
| **Email** | `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `EMAIL_DEV_MODE` |
| **AI** | `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY` |
| **Security** | `ENCRYPTION_KEY`, `REDIS_URL`, `VIRUSTOTAL_API_KEY` |
| **Frontend** | `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` |

Generate secrets:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Deployment

See **[DEPLOY_CHECKLIST.md](DEPLOY_CHECKLIST.md)** for the full production deployment guide, including:

- GCP Cloud Run backend deployment (Docker)
- Vercel / Cloudflare Pages frontend deployment
- Cloud SQL PostgreSQL provisioning
- GCP Secret Manager setup
- DNS configuration (`ungouge.ai`, `api.ungouge.ai`)
- SSL/TLS verification
- Stripe production webhook setup
- Email service (SMTP) configuration
- Health checks & monitoring
- Rollback procedures
- Launch day runbook

**Quick deploy:**

```bash
# Backend → Cloud Run
docker build -t gcr.io/PROJECT/ungouge-api:v1.0.0 .
docker push gcr.io/PROJECT/ungouge-api:v1.0.0
gcloud run deploy ungouge-api --image=gcr.io/PROJECT/ungouge-api:v1.0.0 --region=us-east1

# Frontend → Vercel
cd frontend && vercel --prod
```

---

## Security

UnGouge.ai is built with security and privacy as first-class concerns.

| Protection | Implementation |
|------------|----------------|
| **GDPR Compliance** | Full Art. 15–22 implementation: data export, deletion, rectification, restriction, portability, right to object |
| **PII Encryption** | AES-256 encryption at rest for all personal data |
| **Authentication** | JWT in httpOnly, Secure, SameSite=Strict cookies |
| **MFA** | Email-based OTP, mandatory for sensitive actions |
| **CSRF Protection** | Double-submit cookie pattern with signed tokens |
| **Content Security Policy** | Strict CSP on both frontend and backend |
| **Rate Limiting** | Per-IP limits on all sensitive endpoints (slowapi) |
| **Input Validation** | Schema validation (Pydantic) + sanitization middleware |
| **File Upload Security** | Magic byte verification, metadata stripping, size limits |
| **SQL Injection** | 100% parameterized queries via SQLAlchemy ORM |
| **XSS Prevention** | React auto-escaping + CSP headers |
| **HTTPS / HSTS** | Enforced redirect + HSTS preload header |
| **Security Headers** | `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy` |
| **Token Blacklisting** | JWT revocation on logout |
| **Data Retention** | Automatic 30-day cleanup of expired data (GDPR) |
| **Do Not Track** | DNT signal respected per user preference |
| **Audit Logging** | Structured JSON security event logs |
| **Error Handling** | Generic client errors, full server-side logging |

For the full security audit and penetration test results, see **[SECURITY_PENTEST_REPORT.md](SECURITY_PENTEST_REPORT.md)**.

For implementation details and current status, see **[SECURITY_FIXES_SUMMARY.md](SECURITY_FIXES_SUMMARY.md)**.

---

## Legal

All legal documents are in the [`legal/`](legal/) directory:

- **[Privacy Policy](legal/PRIVACY_POLICY.md)** — What data we collect, how we use it, your rights
- **[Terms of Service](legal/TERMS_OF_SERVICE.md)** — Usage terms and conditions
- **[GDPR Audit Report](legal/GDPR_AUDIT_REPORT.md)** — Compliance assessment
- **[ROPA](legal/ROPA.md)** — Records of Processing Activities (GDPR Art. 30)
- **[DPA Register](legal/DPA_REGISTER.md)** — Data Processing Agreements with third parties
- **[Incident Response Plan](legal/INCIDENT_RESPONSE_PLAN.md)** — Data breach response procedures
- **[Backup & Recovery Plan](legal/BACKUP_RECOVERY_PLAN.md)** — Business continuity

---

## Testing

```bash
cd backend

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_auth.py

# Run with coverage
pytest --cov=. --cov-report=html
```

---

## License

**Proprietary — All Rights Reserved**

© 2026 UnGouge LLC. This software and its source code are proprietary and confidential. Unauthorized copying, distribution, or use of this software, in whole or in part, is strictly prohibited.

For licensing inquiries, contact: hello@ungouge.ai
