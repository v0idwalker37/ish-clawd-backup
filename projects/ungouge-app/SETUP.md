# Ungouge.ai Development Setup Guide

> **Complete guide for new developers** - Get from zero to running locally in 30 minutes

**Target Audience:** New developers, contractors, future Jason  
**Prerequisites:** Basic command line knowledge, code editor

---

## Table of Contents

- [System Requirements](#system-requirements)
- [Quick Start (TL;DR)](#quick-start-tldr)
- [Detailed Setup](#detailed-setup)
  - [1. Install Prerequisites](#1-install-prerequisites)
  - [2. Clone Repository](#2-clone-repository)
  - [3. Backend Setup](#3-backend-setup)
  - [4. Frontend Setup](#4-frontend-setup)
  - [5. Get API Keys](#5-get-api-keys)
- [Running the Application](#running-the-application)
- [Troubleshooting](#troubleshooting)
- [Development Workflow](#development-workflow)
- [Common Tasks](#common-tasks)

---

## System Requirements

### Minimum Requirements

- **OS:** macOS 10.15+, Ubuntu 20.04+, Windows 10+ (WSL2)
- **RAM:** 4GB (8GB recommended)
- **Disk Space:** 2GB free
- **Internet:** Required for API calls

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| **Python** | 3.11+ | Backend API |
| **Node.js** | 18+ | Frontend app |
| **npm** | 9+ | Package management |
| **Git** | 2.0+ | Version control |

### Optional (Recommended)

- **PostgreSQL** 14+ - Production database (SQLite used for dev)
- **Redis** 7+ - Token blacklist (in-memory used for dev)
- **Postman** - API testing
- **VS Code** - Code editor

---

## Quick Start (TL;DR)

**For experienced developers who want the fast track:**

```bash
# Frontend
cd frontend
npm install
cp .env.local.example .env.local
# Edit .env.local: NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev

# Backend (new terminal)
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: Add JWT_SECRET_KEY, GEMINI_API_KEY
python main.py
```

**URLs:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Done!** *(If this works, you can skip to [Running the Application](#running-the-application))*

---

## Detailed Setup

### 1. Install Prerequisites

#### macOS

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11
brew install python@3.11

# Install Node.js 18+
brew install node

# Verify installations
python3 --version  # Should show 3.11.x
node --version     # Should show 18.x or higher
npm --version      # Should show 9.x or higher
git --version      # Should be installed by default
```

#### Ubuntu/Debian

```bash
# Update package list
sudo apt update

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip

# Install Node.js 18+ (using NodeSource)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installations
python3.11 --version
node --version
npm --version
git --version
```

#### Windows (WSL2 Recommended)

**Option 1: WSL2 (Recommended)**
1. Install WSL2: https://learn.microsoft.com/en-us/windows/wsl/install
2. Install Ubuntu from Microsoft Store
3. Follow Ubuntu instructions above

**Option 2: Native Windows**
1. Install Python: https://www.python.org/downloads/
2. Install Node.js: https://nodejs.org/
3. Install Git: https://git-scm.com/download/win
4. Use PowerShell or Git Bash for commands

---

### 2. Clone Repository

```bash
# Choose a location for the project
cd ~/projects  # or wherever you keep code

# Clone the repository
git clone https://github.com/your-org/ungouge-app.git  # Update with actual repo URL
cd ungouge-app

# View structure
ls -la
```

**Expected structure:**
```
ungouge-app/
├── frontend/
├── backend/
├── README.md
├── SETUP.md (this file)
└── ...
```

---

### 3. Backend Setup

#### Step 1: Create Virtual Environment

```bash
cd backend

# Create virtual environment (isolates Python dependencies)
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

**Why virtual environment?**
- Keeps project dependencies separate from system Python
- Prevents version conflicts between projects
- Easy to delete and recreate

#### Step 2: Install Dependencies

```bash
# Make sure venv is activated (you see (venv) in prompt)
pip install -r requirements.txt

# This installs ~30 packages and takes 2-3 minutes
```

**Common error:** "pip: command not found"
- Solution: Use `python -m pip install -r requirements.txt`

#### Step 3: Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your preferred editor
nano .env  # or: vim .env, code .env, etc.
```

**Required variables:**
```bash
# Database (SQLite for development - no setup needed)
DATABASE_URL=sqlite+aiosqlite:///./ungouge.db

# Security (MUST CHANGE)
JWT_SECRET_KEY=your-secret-key-here  # Generate: openssl rand -hex 32
ENVIRONMENT=development

# Frontend URL
FRONTEND_URL=http://localhost:3000

# AI (Required for quote parsing)
GEMINI_API_KEY=your-gemini-key-here  # See "Get API Keys" section

# Email (Development mode - no real emails sent)
EMAIL_DEV_MODE=true
FROM_EMAIL=noreply@ungouge.local
```

**Generate JWT secret:**
```bash
openssl rand -hex 32
# Copy the output and paste into .env as JWT_SECRET_KEY
```

**Optional (can leave default):**
```bash
# Stripe (for payments - use test keys)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Craftsman API (future integration)
CRAFTSMAN_API_KEY=...
```

#### Step 4: Initialize Database

```bash
# Still in backend/ directory with venv activated

# Run database migrations
python main.py

# You should see:
# INFO:     Database tables created successfully
# INFO:     Starting server...
```

**What happened:**
- SQLAlchemy created `ungouge.db` file
- Tables: users, quotes, line_items, password_reset_tokens, etc.
- You can view with: `sqlite3 ungouge.db` then `.schema`

#### Step 5: Test Backend

```bash
# Start the server (if not already running)
python main.py

# You should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
```

**Test endpoints:**
```bash
# In a new terminal (keep server running):
curl http://localhost:8000/health
# Should return: {"status":"healthy","timestamp":"..."}

# Open interactive API docs in browser:
open http://localhost:8000/docs  # macOS
# Or visit: http://localhost:8000/docs
```

**Success!** Backend is running. Keep this terminal open.

---

### 4. Frontend Setup

#### Step 1: Install Dependencies

```bash
# Open a NEW terminal (keep backend running)
cd frontend  # or: cd ../frontend from backend/

# Install Node.js dependencies (takes 2-3 minutes)
npm install

# This installs React, Next.js, Tailwind, and other packages
```

**Common errors:**
- "EACCES: permission denied" → Use `sudo npm install -g npm` then retry
- "Node version too old" → Upgrade Node.js to 18+

#### Step 2: Configure Environment

```bash
# Copy example environment file
cp .env.local.example .env.local

# Edit .env.local
nano .env.local  # or: code .env.local
```

**Required variables:**
```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Stripe public key (optional - for payments)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

**Important:** `NEXT_PUBLIC_` prefix makes variables available in browser code.

#### Step 3: Test Frontend

```bash
# Start development server
npm run dev

# You should see:
# ✓ Ready in 2.5s
# ○ Local: http://localhost:3000
```

**Open browser:**
```
http://localhost:3000
```

**You should see:**
- Ungouge.ai landing page
- Navigation header
- "Stop getting gouged" hero section

**Success!** Frontend is running.

---

### 5. Get API Keys

#### Gemini API Key (Required)

**Purpose:** AI-powered quote parsing (extracts line items from PDFs/images)

**Steps:**
1. Go to: https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIza...`)
5. Add to `backend/.env`:
   ```bash
   GEMINI_API_KEY=AIzaSyD...your-key-here
   ```

**Free tier:** 60 requests/minute (plenty for development)

**Testing:**
```bash
# In backend/ directory with venv activated
python test_gemini_parser.py path/to/sample_quote.pdf

# Should extract line items and print structured JSON
```

#### Stripe Keys (Optional - For Payments)

**Purpose:** Process payments ($19.99 per report)

**Steps:**
1. Sign up: https://stripe.com
2. Get test API keys from Dashboard → Developers → API Keys
3. Add to `backend/.env`:
   ```bash
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_WEBHOOK_SECRET=whsec_...  # For webhooks (optional)
   ```
4. Add to `frontend/.env.local`:
   ```bash
   NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
   ```

**Testing:** Use test card `4242 4242 4242 4242`, any future expiry, any CVC

#### PostgreSQL (Optional - For Production-Like Setup)

**For development, SQLite is fine.** Skip this unless you want to test with PostgreSQL.

**macOS:**
```bash
brew install postgresql@14
brew services start postgresql@14
createdb ungouge
```

**Ubuntu:**
```bash
sudo apt install postgresql postgresql-contrib
sudo -u postgres createdb ungouge
sudo -u postgres createuser your_username
```

**Update `backend/.env`:**
```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost/ungouge
```

---

## Running the Application

### Start Everything

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Access the App

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:3000 | Main user interface |
| **Backend** | http://localhost:8000 | API server |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **OpenAPI Schema** | http://localhost:8000/openapi.json | API spec |

### Test the Full Flow

1. **Open frontend:** http://localhost:3000
2. **Click "Sign Up"** (top right)
3. **Create account:**
   - Email: test@example.com
   - Password: Test123!
   - Name: Test User
4. **Login** with same credentials
5. **Upload a quote:**
   - Click "Analyze Quote"
   - Upload a sample PDF or image
   - Wait for analysis (~5 seconds)
6. **View results:**
   - See line-by-line breakdown
   - Fair price estimates
   - Potential savings

**Success!** You've completed a full quote analysis cycle.

---

## Troubleshooting

### Backend Won't Start

**Error:** "Address already in use" (port 8000)
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux
```

**Error:** "ModuleNotFoundError: No module named 'fastapi'"
```bash
# Virtual environment not activated
source venv/bin/activate  # Activate it
pip install -r requirements.txt  # Reinstall dependencies
```

**Error:** "GEMINI_API_KEY not found"
```bash
# Check .env file exists
ls -la .env

# Check key is set
cat .env | grep GEMINI_API_KEY

# If missing, add it:
echo "GEMINI_API_KEY=your-key-here" >> .env
```

### Frontend Won't Start

**Error:** "Port 3000 already in use"
```bash
# Option 1: Kill the process
lsof -i :3000
kill -9 <PID>

# Option 2: Use different port
PORT=3001 npm run dev
# Update FRONTEND_URL in backend/.env to http://localhost:3001
```

**Error:** "Cannot connect to backend" (Network error)
```bash
# Check backend is running
curl http://localhost:8000/health

# Check NEXT_PUBLIC_API_URL in .env.local
cat .env.local

# Restart frontend
npm run dev
```

### Database Issues

**Error:** "Database locked" (SQLite)
```bash
# Another process is accessing the database
# Solution: Restart backend server
```

**Error:** "Table already exists"
```bash
# Alembic migration conflict
# Solution: Delete database and start fresh (DEV ONLY)
cd backend
rm ungouge.db
python main.py  # Recreates tables
```

### Gemini API Issues

**Error:** "Gemini API key invalid"
```bash
# Test key manually
curl -X POST \
  'https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash-exp:generateContent?key=YOUR_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}'

# Should return JSON, not an error
```

**Error:** "Rate limit exceeded"
```bash
# Wait 1 minute (free tier: 60 req/min)
# Or upgrade to paid tier at https://ai.google.dev/pricing
```

---

## Development Workflow

### Daily Startup

```bash
# Terminal 1 - Backend
cd backend && source venv/bin/activate && python main.py

# Terminal 2 - Frontend
cd frontend && npm run dev
```

**Pro tip:** Create shell aliases:
```bash
# Add to ~/.bashrc or ~/.zshrc
alias ungouge-backend="cd ~/projects/ungouge-app/backend && source venv/bin/activate && python main.py"
alias ungouge-frontend="cd ~/projects/ungouge-app/frontend && npm run dev"
```

### Making Changes

**Backend changes:**
- Edit files in `backend/` directory
- Server auto-reloads (hot reload enabled)
- Check logs in terminal for errors

**Frontend changes:**
- Edit files in `frontend/src/` directory
- Browser auto-refreshes (Fast Refresh)
- Check browser console for errors

### Running Tests

**Backend tests:**
```bash
cd backend
source venv/bin/activate
pytest  # Runs all tests
pytest tests/test_auth.py  # Run specific test file
```

**Frontend linting:**
```bash
cd frontend
npm run lint  # Check for code issues
npm run build  # Test production build
```

### Database Management

**View database (SQLite):**
```bash
cd backend
sqlite3 ungouge.db
.tables  # List tables
.schema users  # Show table schema
SELECT * FROM users;  # Query data
.quit  # Exit
```

**Reset database (DEV ONLY):**
```bash
cd backend
rm ungouge.db  # Delete database
python main.py  # Recreates tables
```

**Backup database:**
```bash
cd backend
cp ungouge.db ungouge.db.backup
```

---

## Common Tasks

### Add a New API Endpoint

**1. Create endpoint in `backend/routers/quotes.py`:**
```python
@router.get("/api/quotes/{quote_id}/summary")
async def get_quote_summary(
    quote_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Your logic here
    return {"summary": "..."}
```

**2. Test in browser:**
```
http://localhost:8000/docs
# Try the new endpoint in Swagger UI
```

**3. Call from frontend:**
```typescript
// frontend/src/app/dashboard/page.tsx
const response = await fetch(
  `${process.env.NEXT_PUBLIC_API_URL}/api/quotes/${id}/summary`,
  {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  }
);
```

### Add a New React Component

**1. Create component file:**
```bash
cd frontend/src/components
touch NewComponent.tsx
```

**2. Component template:**
```typescript
'use client';
import { useState } from 'react';

export default function NewComponent() {
  const [state, setState] = useState('');
  
  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold">New Component</h2>
    </div>
  );
}
```

**3. Import in page:**
```typescript
// frontend/src/app/page.tsx
import NewComponent from '@/components/NewComponent';

export default function Home() {
  return (
    <div>
      <NewComponent />
    </div>
  );
}
```

### Update Dependencies

**Backend:**
```bash
cd backend
source venv/bin/activate
pip list --outdated  # Check for updates
pip install --upgrade package-name
pip freeze > requirements.txt  # Update requirements
```

**Frontend:**
```bash
cd frontend
npm outdated  # Check for updates
npm update  # Update all packages
npm install package-name@latest  # Update specific package
```

### Deploy to Production

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment guide.

**Quick checklist:**
- [ ] Generate production JWT secret
- [ ] Switch to PostgreSQL database
- [ ] Add production API keys (Gemini, Stripe)
- [ ] Set `ENVIRONMENT=production` in backend
- [ ] Configure CORS for production domain
- [ ] Deploy frontend to Vercel
- [ ] Deploy backend to Railway/AWS
- [ ] Test full flow in production

---

## Environment Variables Reference

### Backend (.env)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | (none) | Database connection string |
| `JWT_SECRET_KEY` | Yes | (none) | Secret for signing JWT tokens |
| `ENVIRONMENT` | Yes | development | Environment (development/production) |
| `FRONTEND_URL` | Yes | http://localhost:3000 | Frontend URL for CORS |
| `GEMINI_API_KEY` | Yes | (none) | Google Gemini API key |
| `STRIPE_SECRET_KEY` | No | (none) | Stripe secret key |
| `EMAIL_DEV_MODE` | No | true | Skip sending real emails |
| `FROM_EMAIL` | No | noreply@ungouge.local | From address for emails |

### Frontend (.env.local)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | (none) | Backend API URL |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | No | (none) | Stripe public key |

---

## Getting Help

### Resources

- **README.md** - Project overview
- **ARCHITECTURE.md** - Tech stack decisions
- **API.md** - API endpoint reference
- **DEPLOYMENT.md** - Production deployment
- **Interactive API Docs** - http://localhost:8000/docs

### Common Questions

**Q: Can I use Python 3.10 or 3.9?**  
A: 3.10 should work, 3.9 might have issues. Upgrade to 3.11+ recommended.

**Q: Do I need Redis for development?**  
A: No, token blacklist uses in-memory storage for dev.

**Q: Can I use Yarn instead of npm?**  
A: Yes, but lock file might conflict. Stick with npm for consistency.

**Q: How do I reset my password in dev?**  
A: Delete the user from database, or check backend logs for reset token.

**Q: The analysis seems wrong, what's happening?**  
A: Check Gemini API logs in backend terminal. Parsing might have failed.

### Contact

**Issues:** Document in project memory or contact:  
**Email:** jasontrask@gmail.com

---

## Next Steps

✅ **Setup complete!** You should now have:
- Backend running on http://localhost:8000
- Frontend running on http://localhost:3000
- Database initialized
- Gemini API configured
- Test account created

**Recommended next steps:**
1. Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand tech decisions
2. Review [API.md](API.md) for endpoint documentation
3. Explore codebase structure in [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
4. Try uploading real contractor quotes
5. Experiment with the analysis engine in `backend/services/analyzer.py`

**Happy coding!** 🚀

---

**Last updated:** 2024-02-02  
**Maintained by:** Jason Trask
