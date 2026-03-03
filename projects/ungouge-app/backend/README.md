# GougeAlert Backend

FastAPI backend with PostgreSQL database and Stripe integration.

## Getting Started

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your settings

# Run development server
python main.py
```

API will be available at `http://localhost:8000`

- Interactive docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Environment Variables

Create a `.env` file:

```bash
DATABASE_URL=sqlite+aiosqlite:///./ungouge.db
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
FRONTEND_URL=http://localhost:3000
BLS_API_KEY=your_key
OPENAI_API_KEY=sk-...
```

## Project Structure

```
backend/
├── main.py              # FastAPI app entry point
├── routers/             # API route handlers
│   ├── quotes.py        # Quote submission & retrieval
│   └── health.py        # Health checks
├── models/              # Data models
│   ├── database.py      # SQLAlchemy models
│   ├── quote.py         # Quote input schemas
│   └── report.py        # Report output schemas
├── services/            # Business logic
│   ├── analyzer.py      # Quote analysis engine
│   ├── bls_data.py      # BLS data lookup
│   └── payment.py       # Stripe integration
└── data/                # Sample data
    ├── sample_bls_rates.json
    └── material_costs.json
```

## Database

Uses SQLite by default for development. For production, configure PostgreSQL:

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/ungouge
```

Tables are created automatically on startup via SQLAlchemy.

## API Endpoints

### Health
- `GET /health` - Health check with DB status
- `GET /health/ready` - Readiness probe
- `GET /health/live` - Liveness probe

### Quotes
- `POST /api/quotes` - Submit quote for analysis
- `GET /api/quotes/{id}` - Get analysis report
- `GET /api/quotes` - List quotes (paginated)

## Testing

```bash
# Run tests (once implemented)
pytest

# With coverage
pytest --cov=.
```

## Development Notes

### Adding New Trades

Edit `data/sample_bls_rates.json` to add new trade categories.

### Adding Materials

Edit `data/material_costs.json` to add new material categories.

### AI Integration Points

See TODO comments in:
- `services/analyzer.py` - Quote analysis logic
- `services/bls_data.py` - Data lookup service

## Production Deployment

```bash
# Use Gunicorn with Uvicorn workers
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app

# Or Uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [Pydantic](https://docs.pydantic.dev/)
- [Stripe API](https://stripe.com/docs/api)
