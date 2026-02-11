# GitHub Backup Setup Guide (Option C)

## Overview
We're creating two separate private GitHub repositories:
1. **ungouge-app** — Next.js frontend + FastAPI backend (quote analysis app)
2. **ungouge-dashboard** — Cloud Run executive dashboard

## Prerequisites
- GitHub account (you have one)
- GitHub CLI installed (check with `gh --version`)

## Step 1: Authenticate GitHub CLI

```bash
gh auth login
```

Follow prompts:
- Choose: GitHub.com
- Protocol: HTTPS
- Authenticate: Login with web browser
- Follow browser prompts to authorize

## Step 2: Create Private Repositories

```bash
# Create ungouge-app repo
gh repo create ungouge-app --private --description "UnGouge quote verification app (Next.js + FastAPI)"

# Create ungouge-dashboard repo  
gh repo create ungouge-dashboard --private --description "UnGouge executive dashboard (Cloud Run)"
```

## Step 3: Prepare Separate Git Repos

Currently everything is in one git repo at `/Users/moltbot/clawd`. We need to extract the two projects.

### For ungouge-app:

```bash
cd /Users/moltbot/clawd/projects
cp -r ungouge-app ~/Desktop/ungouge-app-temp
cd ~/Desktop/ungouge-app-temp
git init
git add .
git commit -m "Initial commit: UnGouge app (Next.js + FastAPI)

Full-stack quote verification app:
- Next.js 14 frontend (12 pages)
- FastAPI backend with auth + quote analysis  
- 14 cost models with material + labor data
- Fuzzy matching analyzer
- Blog content (23 posts)
- Security audit reports"

git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/ungouge-app.git
git push -u origin main
```

### For ungouge-dashboard:

```bash
cd /Users/moltbot/clawd/projects
cp -r ungouge-dashboard ~/Desktop/ungouge-dashboard-temp
cd ~/Desktop/ungouge-dashboard-temp
git init
git add .
git commit -m "Initial commit: UnGouge executive dashboard

Cloud Run dashboard:
- Task management (60 tasks across 13 projects)
- Financial tracking (4-tab dashboard)
- Stripe API integration
- Google OAuth authentication
- YouTube + GA4 integration ready
- CSV export, date range filters, P&L charts"

git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/ungouge-dashboard.git
git push -u origin main
```

## Step 4: Clean Up

```bash
# After verifying GitHub repos look good:
rm -rf ~/Desktop/ungouge-app-temp
rm -rf ~/Desktop/ungouge-dashboard-temp
```

## Step 5: Future Updates

To push updates to GitHub:

```bash
# For app updates:
cd ~/Desktop/ungouge-app-temp
# (or keep this as permanent location)
git add .
git commit -m "Description of changes"
git push

# For dashboard updates:
cd ~/Desktop/ungouge-dashboard-temp
git add .
git commit -m "Description of changes"
git push
```

## Alternative: I Can Do This (If You Give Me Credentials)

If you want me to handle this:
1. Run `gh auth login` yourself
2. Tell me your GitHub username
3. I'll create the repos and push everything

## What Gets Backed Up

### ungouge-app:
- Frontend: `/frontend` directory (Next.js pages, components, styles)
- Backend: `/backend` directory (FastAPI routes, auth, database)
- Cost models: `/cost_models` directory (14 JSON files)
- Blog content: `/content/blog` directory (23 markdown posts)
- Documentation: All markdown files

### ungouge-dashboard:
- Backend: `/backend` directory (FastAPI, SQLite, auth)
- Static files: `/backend/static` (all HTML pages)
- Deploy script: `DEPLOY_DASHBOARD.sh`
- Documentation: Audit reports, deployment notes

## What DOESN'T Get Backed Up (Intentionally)

- API keys / secrets (`.env` files)
- Database files (`.db` files)
- `node_modules` and Python virtual envs
- Temporary files
- Local config

All sensitive data stays local or in environment variables.

---

**Status: Ready to execute**  
**Time estimate: 10 minutes**  
**Risk: None (just creating backups)**
