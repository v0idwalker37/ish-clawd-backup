# Ungouge.ai

> **Stop getting gouged on contractor quotes.** Get instant, data-backed analysis using real BLS labor rates and material costs.

[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Next.js](https://img.shields.io/badge/next.js-14-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.109+-green.svg)](https://fastapi.tiangolo.com/)

---

## 🎯 What is Ungouge.ai?

Ungouge.ai brings transparency to home renovation pricing. Upload a contractor quote, get instant analysis showing:

- **Line-by-line breakdown** - See exactly what's overpriced
- **Real BLS wage data** - Compare against actual labor rates
- **Fair price estimates** - Know what you *should* be paying
- **Red flag detection** - Spot suspicious patterns and markups

### Our Promise

- **No Lead Generation** - We NEVER sell your data to contractors
- **No Hidden Fees** - $19.99 per report, no subscriptions
- **Real Data** - Official BLS rates + industry-standard material costs
- **Privacy First** - Your quotes stay yours

---

## 🏗️ Architecture Overview

```
Frontend (Next.js 14)          Backend (FastAPI)           Data Layer
─────────────────────         ──────────────────         ────────────
┌─────────────────┐          ┌──────────────┐           ┌──────────┐
│   React Pages   │──────────│  REST API    │───────────│PostgreSQL│
│   (TypeScript)  │  HTTP    │   Routes     │  SQLAlchemy│          │
└─────────────────┘          └──────────────┘           └──────────┘
        │                             │
        │                             ├───────────┐
        │                             │           │
    ┌───▼────┐                  ┌────▼────┐  ┌──▼─────┐
    │Tailwind│                  │ Gemini  │  │ Stripe │
    │  CSS   │                  │ Vision  │  │Payments│
    └────────┘                  │  API    │  └────────┘
                                └─────────┘
```

**Tech Stack:**
- **Frontend:** Next.js 14 (App Router), TypeScript, Tailwind CSS
- **Backend:** FastAPI, Python 3.11+, Pydantic v2
- **Database:** PostgreSQL (SQLite for dev)
- **AI:** Google Gemini 2.0 Flash (vision-based quote parsing)
- **Payments:** Stripe
- **Data Sources:** BLS wage rates, Craftsman National Construction Estimator

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed tech decisions.

---

## 🚀 Quick Start

**New to the project?** Start here: [SETUP.md](SETUP.md)

**TL;DR:**
```bash
# Frontend
cd frontend
npm install
cp .env.local.example .env.local
# Add your API URL to .env.local
npm run dev

# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your secrets to .env
python main.py
```

**Frontend:** http://localhost:3000  
**Backend:** http://localhost:8000  
**API Docs:** http://localhost:8000/docs

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [SETUP.md](SETUP.md) | Complete setup guide for new developers |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Tech stack decisions & system design |
| [API.md](API.md) | Backend API endpoints & examples |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Production deployment guide |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | File organization |

---

## 🧪 Key Features

### ✅ Implemented
- User authentication (JWT-based)
- Quote upload (PDF/images via Gemini Vision)
- Automated line-item analysis
- BLS wage data integration
- Regional cost adjustments
- Stripe payment integration
- Dashboard with quote history
- Security hardening (rate limiting, CSRF protection)

### 🚧 In Progress
- Craftsman API integration (cost model data)
- Advanced red flag detection
- Quote comparison feature

### 📋 Planned
- Email notifications
- PDF report generation
- Contractor negotiation tips
- Mobile app

---

## 🗄️ Project Structure

```
ungouge-app/
├── frontend/              # Next.js 14 application
│   ├── src/
│   │   ├── app/          # Pages (App Router)
│   │   └── components/   # React components
│   └── package.json
│
├── backend/              # FastAPI application
│   ├── routers/         # API endpoints
│   │   ├── auth.py      # Authentication
│   │   ├── quotes.py    # Quote analysis
│   │   └── health.py    # Health checks
│   ├── services/        # Business logic
│   │   ├── analyzer.py           # Quote analysis engine
│   │   ├── quote_parser_gemini.py # AI-powered parsing
│   │   ├── auth.py               # JWT & password handling
│   │   └── email_service.py      # Email notifications
│   ├── models/          # Data models
│   │   ├── database.py  # SQLAlchemy models
│   │   ├── quote.py     # Quote schemas
│   │   └── report.py    # Report schemas
│   ├── data/            # Cost model datasets
│   └── main.py          # FastAPI app entry
│
├── README.md            # This file
├── SETUP.md             # Setup guide
├── ARCHITECTURE.md      # Tech decisions
├── API.md               # API documentation
└── DEPLOYMENT.md        # Production deployment
```

---

## 🔑 Environment Variables

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/ungouge
# Or SQLite: sqlite+aiosqlite:///./ungouge.db

# Security
JWT_SECRET_KEY=your-secret-key-here
ENVIRONMENT=development

# Payments
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# AI
GEMINI_API_KEY=your-gemini-key

# Email
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
FROM_EMAIL=noreply@ungouge.ai

# Frontend
FRONTEND_URL=http://localhost:3000
```

See [SETUP.md](SETUP.md) for complete setup instructions.

---

## 🧪 Testing

```bash
# Frontend
cd frontend
npm run lint
npm run build  # Test production build

# Backend
cd backend
pytest  # Unit tests
python test_gemini_parser.py  # Test quote parsing
```

---

## 🔒 Security

- ✅ JWT authentication with token blacklist
- ✅ Password hashing (bcrypt)
- ✅ Rate limiting (100 req/min default)
- ✅ CSRF protection
- ✅ Security headers (HSTS, X-Frame-Options, etc.)
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ XSS protection (React + sanitization)
- ✅ CORS restrictions
- ✅ Structured logging
- ✅ Input validation (Pydantic)

See `SECURITY_COMPLETE.md` for full security audit.

---

## 📊 Cost Model System

Ungouge uses comprehensive cost models for accurate analysis:

### Data Sources
1. **BLS Wage Data** - Official U.S. Bureau of Labor Statistics hourly rates
2. **Craftsman Cost Database** - Industry-standard material & labor costs
3. **Regional Multipliers** - Cost-of-living adjustments by ZIP code

### Adding New Models

1. Add cost data to `backend/data/project_cost_models.json`:
```json
{
  "deck_building": {
    "typical_scope": "...",
    "line_items": {
      "pressure_treated_lumber": {
        "typical_unit_cost": 3.50,
        "unit": "linear_foot",
        "fair_range": [3.00, 4.00]
      }
    }
  }
}
```

2. Update category matching in `services/analyzer.py`:
```python
def fuzzy_match_category(item_name: str, categories: Dict):
    # Matching logic will auto-detect new categories
```

3. Test with sample quotes:
```bash
python test_analyzer.py --project-type deck_building
```

See [API.md](API.md) for data model schemas.

---

## 🤝 Contributing

This is a commercial project. External contributions are not currently accepted.

**For internal development:**
1. Create feature branch from `main`
2. Follow conventional commits (`feat:`, `fix:`, `docs:`)
3. Test thoroughly
4. Submit PR for review
5. Merge after approval

---

## 📝 License

Proprietary - All rights reserved © 2024 Ungouge.ai

---

## 💬 Support

- **Email:** jasontrask@gmail.com
- **Docs:** You're reading them!
- **Issues:** Document in memory or contact Jason

---

## 🎯 Development Roadmap

### Phase 1: MVP (✅ Complete)
- Basic quote upload & analysis
- User authentication
- Payment processing
- Dashboard

### Phase 2: Enhanced Analysis (🚧 In Progress)
- Craftsman API integration
- Advanced red flags
- Quote comparison
- Email notifications

### Phase 3: Scale & Polish
- Mobile app
- PDF reports
- Contractor negotiation tips
- Bulk quote analysis

### Phase 4: Advanced Features
- Historical trend analysis
- Machine learning cost predictions
- Contractor reputation tracking
- API for third-party integrations

---

**Built with ❤️ to protect homeowners from price gouging**

For detailed setup instructions, see [SETUP.md](SETUP.md).  
For architecture decisions, see [ARCHITECTURE.md](ARCHITECTURE.md).  
For API reference, see [API.md](API.md).
