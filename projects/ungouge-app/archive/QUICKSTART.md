# Ungouge.ai - Quick Start Guide

Get up and running in 5 minutes.

## Prerequisites

- Node.js 18+
- Python 3.11+
- npm or yarn

## Step 1: Clone & Setup

```bash
cd /Users/moltbot/clawd/projects/ungouge-app
```

## Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (SQLite by default)
cp .env.example .env

# Start the backend
python main.py
```

Backend running at: **http://localhost:8000**  
API Docs at: **http://localhost:8000/docs**

## Step 3: Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.local.example .env.local

# Start the dev server
npm run dev
```

Frontend running at: **http://localhost:3000**

## Step 4: Test It Out

1. Open **http://localhost:3000** in your browser
2. Click "Analyze a Quote"
3. Fill out the form:
   - Project Type: Kitchen Remodel
   - Location: Denver, CO
   - Add a line item: "Cabinet Installation" - $4500
4. Click through to see the analysis report

## What You Should See

- ✅ Landing page with hero, features, CTA
- ✅ Multi-step quote form
- ✅ Analysis report with fair price ranges
- ✅ Visual price gauge showing if quote is fair/high/gouging
- ✅ Line-by-line breakdown with BLS data

## Project Structure

```
ungouge-app/
├── frontend/          # Next.js 14 + TypeScript + Tailwind
│   ├── src/app/      # App Router pages
│   ├── src/components/  # React components
│   └── package.json
├── backend/           # FastAPI + Python
│   ├── routers/      # API endpoints
│   ├── models/       # Data models
│   ├── services/     # Business logic
│   ├── data/         # Sample BLS & material data
│   └── requirements.txt
└── README.md
```

## Key Files to Explore

### Frontend
- `src/app/page.tsx` - Landing page
- `src/components/QuoteForm.tsx` - Multi-step form with validation
- `src/components/PriceGauge.tsx` - Visual price assessment
- `src/components/ReportCard.tsx` - Individual line item display

### Backend
- `main.py` - FastAPI app entry
- `routers/quotes.py` - Quote submission & retrieval
- `services/analyzer.py` - Quote analysis logic (with AI TODO comments)
- `services/bls_data.py` - BLS wage lookup
- `data/sample_bls_rates.json` - Sample labor rates for 15 trades
- `data/material_costs.json` - Sample material costs

## Common Issues

### Port already in use?

**Frontend:**
```bash
# Use a different port
npm run dev -- -p 3001
```

**Backend:**
```bash
# Edit main.py and change port=8000 to port=8001
```

### Python module not found?

Make sure you activated the virtual environment:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### Database errors?

Delete the SQLite database and restart:
```bash
rm backend/ungouge.db
python main.py
```

## Next Steps

1. **Customize branding** - Update colors in `frontend/tailwind.config.js`
2. **Add Stripe keys** - Get test keys from https://dashboard.stripe.com
3. **Configure database** - Switch to PostgreSQL for production
4. **Enable AI** - Add OpenAI key for enhanced explanations
5. **Connect BLS API** - Get real-time wage data

## Need Help?

- 📖 Full docs: `README.md`
- 🐛 Issues: Check logs in terminal
- 💬 Questions: support@ungouge.ai

---

**You're all set! 🎉 Start building the features that will protect homeowners from price gouging.**
