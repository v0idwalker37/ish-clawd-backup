# UnGouge Dashboard → Real Business Operations
## Integration Plan

*Created: 2026-02-04*

---

## Current State ✅

**What Works:**
- ✅ Authentication (Google OAuth)
- ✅ Dashboard UI loading
- ✅ Database structure (SQLite)
- ✅ Sample data displaying

**What's Missing:**
- ❌ Real data from actual business operations
- ❌ Automated data feeds
- ❌ Live metrics updating

---

## Data Sources to Integrate

### 1. **YouTube Channel** (UnGouge Digest)
**Current:** Sample data (1,247 subs hardcoded)  
**Need:** Real-time YouTube Analytics

**Data Points:**
- Subscriber count (live)
- Video views (per video + total)
- Watch time
- Revenue (if monetized)
- Comments/engagement
- Upload schedule compliance

**Integration Method:**
- YouTube Data API v3 (free)
- OAuth with Jason's Google account
- Update every 6-24 hours (API quota limits)

**Priority:** HIGH (you check this daily)

---

### 2. **Ungouge.ai Website Analytics**
**Current:** Not tracked  
**Need:** Traffic, conversions, user behavior

**Data Points:**
- Daily visitors
- Quote submissions
- Conversion rate (visitor → quote submission)
- Bounce rate
- Top pages
- Traffic sources

**Integration Method:**
- Google Analytics 4 (free) - install tracking code
- Analytics API for dashboard display
- OR Plausible/Simple Analytics (privacy-focused alternatives)

**Priority:** HIGH (need to know if marketing works)

---

### 3. **Quote Analysis Revenue**
**Current:** Sample $0  
**Need:** Actual Stripe transactions

**Data Points:**
- Daily/monthly revenue
- Number of quotes analyzed
- Customer acquisition cost (CAC)
- Average revenue per user (ARPU)
- Churn rate
- MRR/ARR tracking

**Integration Method:**
- Stripe API (when payments go live)
- Webhook for real-time updates
- Store transactions in dashboard DB

**Priority:** MEDIUM (not launched yet, but prepare infrastructure)

---

### 4. **Business Expenses**
**Current:** Sample $69.35/month  
**Need:** Real expense tracking

**Current Known Expenses:**
- ElevenLabs: $22/mo (voice cloning)
- Google Cloud Run: ~$0-5/mo (dashboard hosting)
- Domain: ~$12/year (ungouge.ai)
- Email hosting: $? (if separate from domain)
- OpenAI API: ~$0.10/mo (memory system)

**Integration Method:**
- Manual entry for now (simple form in dashboard)
- Future: Plaid API for bank account connection (if needed)
- Categorize: hosting, API, software, marketing, etc.

**Priority:** MEDIUM (need accurate burn rate tracking)

---

### 5. **Email Monitoring**
**Current:** Not connected  
**Need:** Customer inquiries, important emails

**Accounts to Monitor:**
- Gmail: jasontrask@gmail.com
- iCloud: (Jason's iCloud email)
- Business email: void@ungouge.ai (if separate)

**Data Points:**
- Unread count
- Important emails flagged
- Customer support queue
- Time to first response

**Integration Method:**
- Gmail API (OAuth already configured for auth)
- IMAP for iCloud (app-specific password)
- Check every 30-60 min
- Alert on important emails

**Priority:** HIGH (customer communication = revenue)

---

### 6. **Calendar & Deadlines**
**Current:** Not connected  
**Need:** Upcoming milestones, content schedule

**Data Points:**
- YouTube upload schedule (weekly? bi-weekly?)
- Product launch dates
- Marketing campaign deadlines
- Important meetings/appointments

**Integration Method:**
- Apple Calendar API (iCloud)
- OR Google Calendar API
- Show next 7 days on dashboard
- Alert on approaching deadlines

**Priority:** MEDIUM (helps with accountability)

---

### 7. **Task Management**
**Current:** Sample tasks in database  
**Need:** Real project tasks

**Categories:**
- Ungouge.ai development (features, fixes)
- YouTube production (scripts, editing, uploads)
- Marketing (blog posts, social media)
- Business operations (accounting, legal, etc.)

**Integration Method:**
- Use dashboard's built-in task system
- Migrate existing todos from wherever Jason tracks them now
- Add task creation UI to dashboard
- Daily/weekly review workflow

**Priority:** HIGH (clear next actions = progress)

---

## Implementation Phases

### **Phase 1: Critical Dashboards (Week 1)**
*Get the metrics you check daily*

1. **YouTube Analytics Integration** (2-3 hours)
   - Set up YouTube Data API credentials
   - Build backend endpoint: `/api/youtube/stats`
   - Update dashboard to fetch real data
   - Test: See real subscriber count

2. **Email Monitoring Setup** (2-3 hours)
   - Gmail API: Read-only access, fetch unread
   - iCloud IMAP: App-specific password
   - Dashboard widget: "X unread emails, Y important"
   - Heartbeat check every 30 min

3. **Real Expense Tracking** (1 hour)
   - Add expense entry form to dashboard
   - Seed database with current known expenses
   - Monthly total calculation
   - Burn rate calculation (expenses - revenue)

**Deliverable:** Dashboard shows real YouTube stats, email status, actual expenses

---

### **Phase 2: Website & Revenue (Week 2)**
*Set up for when Ungouge.ai goes live*

4. **Google Analytics Integration** (1-2 hours)
   - Install GA4 on ungouge.ai
   - Analytics API for dashboard
   - Track: visitors, quote submissions, conversions
   - Daily stats widget

5. **Stripe Revenue Tracking** (2 hours)
   - Stripe API integration (test mode first)
   - Webhook endpoint for new payments
   - Revenue dashboard card
   - MRR calculation

**Deliverable:** Ready to track website traffic and revenue when launched

---

### **Phase 3: Productivity & Planning (Week 3)**
*Help you stay organized*

6. **Calendar Integration** (1-2 hours)
   - Apple Calendar or Google Calendar API
   - Next 7 days widget on dashboard
   - Upload schedule compliance tracker

7. **Task System Activation** (1 hour)
   - Add "Create Task" button to dashboard
   - Migrate existing todos from wherever Jason has them
   - Daily standup view: "What's due today?"

**Deliverable:** Dashboard becomes your daily command center

---

## Technical Requirements

### APIs Needed
- ✅ Google OAuth (already working)
- ⏳ YouTube Data API v3
- ⏳ Gmail API
- ⏳ Google Analytics API
- ⏳ Stripe API (when ready)
- ⏳ Apple Calendar API OR Google Calendar API

### Credentials Needed from Jason
1. YouTube channel access (same Google account as dashboard login?)
2. Gmail read-only access (already have Google OAuth)
3. iCloud app-specific password (for email)
4. Stripe API keys (when ready to go live)
5. Google Analytics property ID (after installing GA4)

### Infrastructure Changes
- Database schema additions (new tables for emails, analytics history)
- Background jobs for data fetching (every 30 min - 24 hours depending on source)
- Caching layer (don't hit APIs too often, respect rate limits)

---

## Success Metrics

**Dashboard is "operating the business" when:**
1. ✅ You open it every morning and see REAL numbers
2. ✅ Email alerts work (you know about customer inquiries within 30 min)
3. ✅ YouTube stats update automatically (no manual checking)
4. ✅ Revenue is tracked accurately (every payment logged)
5. ✅ You can answer "How's the business doing?" with 3 numbers from dashboard

**Goal:** Dashboard replaces:
- Checking YouTube Studio manually
- Checking email manually
- Spreadsheet for expense tracking
- Mental todo list
- Calendar app for upcoming deadlines

---

## Timeline Estimate

**Aggressive (focused work):** 2-3 days  
**Realistic (with other priorities):** 1-2 weeks  
**Per-phase:** 1 week each (but can start using after Phase 1)

---

## Questions for Jason

1. **YouTube Analytics:** Is UnGouge Digest on the same Google account as void@ungouge.ai?
2. **Email Priority:** Which email gets customer inquiries? Gmail, iCloud, or void@ungouge.ai?
3. **Calendar:** Apple Calendar or Google Calendar? (or both?)
4. **Analytics:** Have you installed Google Analytics on ungouge.ai yet? (if not, I can do it)
5. **Current Todo System:** Where do you track tasks now? (notes app, paper, memory?)

---

## Next Immediate Action

**I recommend:** Start with Phase 1, Step 1 - YouTube Analytics integration.

**Why:** 
- You check YouTube stats anyway
- Quick win (2-3 hours)
- Validates the integration pattern
- Shows real business metric immediately

**What I need to start:**
- Confirm YouTube channel is on same Google account as dashboard login
- OR provide YouTube channel ID if different account

Sound good?
