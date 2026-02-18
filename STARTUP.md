# STARTUP.md — Session Quick-Start

*Read this FIRST every session. It's the fastest path to context.*

## What's Happening Right Now

### Ungouge.ai — LAUNCH DAY (Feb 18, 2026)
- **Status:** Deployed and functional, awaiting Jason's live E2E test
- **Frontend:** https://ungouge.ai (Vercel)
- **Backend:** https://ungouge-backend-1934459654.us-central1.run.app (Cloud Run, revision 00014-9xm)
- **Database:** Cloud SQL PostgreSQL 15, instance `ungouge-app-db`, GCP project `ungouge-app`
- **Stripe:** LIVE mode (real money), account acct_1SxXkARvF6kxKwkL
- **Webhook:** we_1T20MLRvF6kxKwkLjduCZSzH → backend /api/payments/webhook

### User Flow (verified E2E)
1. Visit ungouge.ai → Homepage
2. Click "Analyze My Quote" → Quote form
3. Fill out details → Submit → Auth gate (must register/login)
4. After auth → Quote saved → Stripe checkout redirect
5. Pay $19.99 → Redirect to /report/{id}?payment=success
6. Report loads on screen immediately + receipt email sent
7. Dashboard → My Quotes shows all historical reports

### HDD Consolidation — COMPLETE ✅
- 247,233 unique files processed, 0 errors
- ~40,059 files copied (~383 GB) to Blackhole01
- Source drives (BOH2, Number_2) untouched
- Project files: `projects/hdd-consolidate/`

## Key Files
- `SOUL.md` — Who I am (Ish)
- `USER.md` — Who Jason is
- `MEMORY.md` — Long-term memory (main session only)
- `memory/YYYY-MM-DD.md` — Daily logs
- `TOOLS.md` — Local setup notes, model preferences
- `HEARTBEAT.md` — Periodic check instructions
- `projects/ungouge-app/` — The product
- `projects/hdd-consolidate/` — HDD project (complete)

## Critical Rules (learned the hard way)
1. **NEVER** read config files with secrets using `read` tool
2. **NEVER** output secrets/credentials to chat
3. **ALWAYS** use Opus 4.6 for coding tasks
4. **ALWAYS** read memory files before responding (don't make Jason repeat context)
5. **NEVER** put unverifiable stats on the website
6. **NEVER** spend money without explicit approval

## What to Do on Session Start
1. Read this file ✅
2. Read `SOUL.md` (who I am)
3. Read `USER.md` (who Jason is)
4. Read `memory/YYYY-MM-DD.md` (today + yesterday)
5. If main session: Read `MEMORY.md`
6. Check for active tasks or blockers
7. Get to work
