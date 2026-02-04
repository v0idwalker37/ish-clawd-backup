# UnGouge Dashboard - Complete Rebuild Plan
## Based on ConnectWise Automate Architecture

**Timeline: 6-8 hours continuous work**  
**Target: Tonight (Feb 4, 2026)**  
**Model: Opus 4.5**

---

## 🎯 CORE PHILOSOPHY (ConnectWise Automate)

### Key Principles:
1. **Pod/Widget Architecture** - Modular, drag-and-drop widgets
2. **Real-time Data** - Live API integration, auto-refresh
3. **Drill-through Navigation** - Click any metric → detailed view
4. **Single Source of Truth** - All business data in one dashboard
5. **Actionable Insights** - Not just data, but clear next actions

---

## 📐 ARCHITECTURE

### Frontend Stack:
- Pure HTML5/CSS3/JavaScript (no frameworks - fast, simple)
- Modular widget system (each pod = self-contained component)
- Grid layout with drag-and-drop (future enhancement)
- Real-time WebSocket updates (phase 2)
- Responsive design (desktop + mobile)

### Backend Stack (existing):
- FastAPI (Python)
- SQLite database
- Google OAuth 2.0
- RESTful API

### New Integrations:
1. **YouTube Data API v3** - Channel analytics
2. **Stripe API** - Revenue, customers, subscriptions
3. **Google Analytics 4** - Website traffic, conversions
4. **Google Workspace** - Email metrics (optional)
5. **Time tracking** - Manual entry or Toggl integration

---

## 🧩 DASHBOARD PODS (Widgets)

### 1. **Executive Summary Pod**
- Revenue (MTD, QTD, YTD)
- Expenses (MTD)
- Net income
- Burn rate
- Runway (months)
- Cash on hand

### 2. **Project Health Pod** (for each project)
- Project name + status indicator (red/yellow/green)
- Progress % (visual bar)
- Tasks: Total / Complete / In Progress / Blocked
- Budget: Spent vs. Allocated
- Next deadline
- Click → Project detail view

**Projects:**
- YouTube Channel
- Ungouge.ai Platform
- Content Library (Scripts/Blog)
- Podcast Distribution
- Executive Dashboard
- Business Operations

### 3. **Task Management Pod**
- Urgent tasks (due &lt; 24h)
- Overdue tasks
- Today's tasks
- This week's tasks
- Completed this week
- Click → Full task manager

### 4. **YouTube Analytics Pod** (real data)
- Subscribers (total + growth)
- Views (7d, 30d)
- Watch time
- Avg view duration
- Top video (current)
- Revenue (AdSense)
- Click → YouTube Studio

### 5. **Website Analytics Pod** (ungouge.ai)
- Visitors (7d, 30d)
- Page views
- Conversions (quote submissions)
- Bounce rate
- Top pages
- Click → GA4 dashboard

### 6. **Revenue Pod** (Stripe integration)
- Quotes processed
- Revenue (MTD, total)
- Customers
- Avg order value
- Pending payments
- Click → Stripe dashboard

### 7. **Time Tracking Pod**
- Hours this week (by project)
- Billable vs. non-billable
- Top time consumer
- Weekly goal progress (20h committed)
- Click → Time detail view

### 8. **Content Pipeline Pod**
- Scripts written / published
- Blog posts drafted / live
- Podcast episodes queued
- Next publish date
- Click → Content calendar

### 9. **System Health Pod**
- API status (YouTube, Stripe, GA, etc.)
- Database size
- Last backup
- Error logs
- Click → System logs

### 10. **Goals & Milestones Pod**
- Q1 2026 goals
- Launch checklist progress
- Key milestones
- Days until next milestone
- Click → Full roadmap

---

## 🗂️ DETAILED VIEWS (Drill-through Pages)

### 1. Project Detail View
- Full project info (description, owner, dates)
- Task list (filterable, sortable)
- Budget breakdown
- Time spent chart
- Team members (future)
- Files/attachments (future)

### 2. Task Manager View
- Full task list (all projects)
- Advanced filters (status, priority, project, assignee, due date)
- Bulk actions (mark complete, reassign, delete)
- Create new task
- Kanban board view (phase 2)
- Gantt chart (phase 2)

### 3. Financial Dashboard
- Revenue chart (monthly trend)
- Expense breakdown (by category)
- Profit/loss statement
- Cash flow projection
- Budget vs. actual
- Export reports (PDF, CSV)

### 4. Analytics Hub
- Combined view: YouTube + Website + Social
- Traffic sources
- Conversion funnels
- Audience demographics
- Growth projections

### 5. Content Calendar
- Monthly view of all content
- Filter by type (video, blog, podcast)
- Drag-and-drop scheduling
- Publishing workflow (draft → review → publish)

### 6. Time Tracker
- Weekly timesheet
- Project breakdown
- Daily log
- Export timesheets
- Integrations (Toggl, Harvest)

---

## 🔌 API INTEGRATIONS

### YouTube Data API v3
**Endpoints:**
- Channels: subscribers, views, video count
- Videos: views, likes, comments, watch time
- Analytics: daily stats, demographics, traffic sources

**Setup:**
1. Enable YouTube Data API v3 in Google Cloud Console
2. Add API key to backend `.env`
3. Implement caching (1-hour TTL to avoid quota limits)

**Quota:** 10,000 units/day (sufficient for hourly updates)

### Stripe API
**Endpoints:**
- Charges: list payments, revenue totals
- Customers: count, new this month
- Subscriptions: active, cancelled, MRR
- Balance: available funds

**Setup:**
1. Create Stripe account (when ready)
2. Get API keys (test + live)
3. Webhook for real-time updates

**Security:** Secret key server-side only, publishable key for frontend

### Google Analytics 4
**Endpoints:**
- Realtime: active users
- Reports: sessions, pageviews, conversions
- Events: custom events (quote submissions)

**Setup:**
1. GA4 property already exists (assume yes)
2. Service account for API access
3. Measurement ID + API credentials

### Google Workspace (Optional)
**Endpoints:**
- Gmail: unread count, inbox stats
- Calendar: upcoming events

**Setup:**
1. OAuth 2.0 (already implemented)
2. Gmail API scope
3. Calendar API scope

---

## 🛠️ IMPLEMENTATION PLAN

### PHASE 1: Infrastructure (1 hour)
- [x] Research ConnectWise Automate (DONE)
- [ ] Create new dashboard architecture
- [ ] Build widget base class/template
- [ ] Implement grid layout system
- [ ] Add real-time refresh mechanism

### PHASE 2: Core Pods (2 hours)
- [ ] Executive Summary Pod (hardcoded → real data in Phase 4)
- [ ] Project Health Pods (6 projects)
- [ ] Task Management Pod
- [ ] Goals & Milestones Pod

### PHASE 3: Drill-through Views (2 hours)
- [ ] Project Detail View
- [ ] Task Manager (full CRUD)
- [ ] Financial Dashboard
- [ ] Content Calendar

### PHASE 4: API Integrations (2 hours)
- [ ] YouTube Data API setup + integration
- [ ] Stripe API setup + integration
- [ ] Google Analytics 4 setup + integration
- [ ] Cache layer for API responses
- [ ] Error handling + fallbacks

### PHASE 5: Polish & Testing (1 hour)
- [ ] Responsive design fixes
- [ ] Loading states
- [ ] Error states
- [ ] Smooth animations
- [ ] Cross-browser testing
- [ ] Security audit

### PHASE 6: Deployment
- [ ] Backend environment variables
- [ ] Database migrations
- [ ] Cloud Run deployment
- [ ] DNS + SSL
- [ ] Monitoring setup

---

## 🎨 DESIGN SYSTEM

### Color Palette:
- **Background:** Dark navy (#0f172a, #1e293b)
- **Surface:** Slightly lighter (#1e293b, #2d3748)
- **Primary:** Blue (#3b82f6)
- **Success:** Green (#10b981)
- **Warning:** Yellow (#f59e0b)
- **Danger:** Red (#ef4444)
- **Text:** Light gray (#e2e8f0)
- **Muted:** Mid gray (#94a3b8)

### Typography:
- **Headers:** -apple-system, 'Segoe UI', Roboto
- **Body:** Same
- **Sizes:** 12px (small), 14px (body), 16px (subhead), 20px (h3), 24px (h2), 32px (h1)

### Components:
- **Cards:** 12px border-radius, subtle shadow
- **Buttons:** 6px border-radius, hover states
- **Badges:** Pill-shaped, color-coded
- **Charts:** Minimalist, high contrast
- **Icons:** From Heroicons or similar

---

## 📊 DATABASE SCHEMA UPDATES

### New Tables:

#### `time_entries`
```sql
CREATE TABLE time_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    task_id INTEGER,
    user_id INTEGER,
    hours REAL NOT NULL,
    description TEXT,
    date DATE NOT NULL,
    billable BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);
```

#### `api_cache`
```sql
CREATE TABLE api_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cache_key TEXT UNIQUE NOT NULL,
    data TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `milestones`
```sql
CREATE TABLE milestones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    due_date DATE,
    completed_at TIMESTAMP,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

#### `api_integrations`
```sql
CREATE TABLE api_integrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    api_key TEXT,
    status TEXT DEFAULT 'inactive',
    last_sync TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔐 SECURITY

### API Keys:
- Store in environment variables (never in code)
- Rotate regularly
- Use service accounts where possible
- Limit scopes to minimum required

### Authentication:
- OAuth 2.0 (already implemented)
- Session cookies (httpOnly, secure, SameSite)
- CSRF protection
- Rate limiting

### Data Protection:
- No sensitive data in logs
- Encrypted database backups
- Secure API communication (HTTPS only)
- Input validation + sanitization

---

## 📈 SUCCESS METRICS

### Functional:
- [ ] All 10 pods display real data
- [ ] All drill-through views work
- [ ] API integrations functional
- [ ] <100ms page load
- [ ] Mobile responsive
- [ ] Zero console errors

### User Experience:
- [ ] Intuitive navigation
- [ ] Clear call-to-actions
- [ ] Smooth animations
- [ ] Helpful error messages
- [ ] Professional appearance

### Business:
- [ ] Jason can manage entire business from dashboard
- [ ] All metrics accurate and real-time
- [ ] No manual data entry required
- [ ] Exportable reports
- [ ] Action items clear

---

## 🚀 GO/NO-GO CHECKLIST

Before deployment:
- [ ] All critical pods functional
- [ ] Authentication working
- [ ] Database backups enabled
- [ ] Error monitoring active
- [ ] Mobile tested
- [ ] Security review complete
- [ ] Jason approval obtained

---

## 📝 NOTES

### ConnectWise Automate Key Learnings:
1. **Pods are king** - Every data point should be clickable
2. **Automation value** - Show time saved, value created
3. **Real-time critical** - Stale data = useless dashboard
4. **One-click drill-through** - Never more than 2 clicks to detail
5. **Actionable** - Dashboard should tell you what to do next

### UnGouge-Specific Adaptations:
- No "clients" → Projects
- No "technicians" → Content creators (future)
- No "tickets" → Tasks
- No "endpoints" → Website/YouTube/Social channels
- Focus on content + revenue, not support metrics

---

## 🎬 LET'S GO!

**Starting implementation NOW.**

**Status updates every 30 minutes.**

**No stopping until it's done.**

---

**Built with Opus 4.5 | Feb 4, 2026**
