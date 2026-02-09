#!/usr/bin/env python3
"""
Add Disaster Response Automation System to UnGouge Dashboard
Three-agent architecture: Sentinel (detection) + Strategist (planning) + Executor (deployment)
"""

import sqlite3
from datetime import datetime, timedelta

# Connect to dashboard database
DB_PATH = "/Users/moltbot/clawd/projects/ungouge-dashboard/backend/dashboard.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Calculate dates
today = datetime.now()
week_1 = today + timedelta(weeks=1)
week_2 = today + timedelta(weeks=2)
week_3 = today + timedelta(weeks=3)
week_4 = today + timedelta(weeks=4)
week_5 = today + timedelta(weeks=5)
week_6 = today + timedelta(weeks=6)
week_7 = today + timedelta(weeks=7)

def add_project(name, description, category, priority="medium", progress=0, health_score=85):
    """Add a project and return its ID"""
    cursor.execute("""
        INSERT INTO projects (name, description, status, category, priority, progress, health_score)
        VALUES (?, ?, 'active', ?, ?, ?, ?)
    """, (name, description, category, priority, progress, health_score))
    return cursor.lastrowid

def add_task(project_id, title, description, status='todo', priority='medium', due_date=None, task_type='action', estimated_hours=None):
    """Add a task to a project"""
    cursor.execute("""
        INSERT INTO tasks (project_id, title, description, status, priority, due_date, task_type, estimated_hours)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (project_id, title, description, status, priority, due_date, task_type, estimated_hours))

# =============================================================================
# DISASTER RESPONSE AUTOMATION SYSTEM
# =============================================================================

automation_project = add_project(
    name="Disaster Response Automation System",
    description="Three-agent architecture for automated disaster detection, response planning, and deployment. Monitors NOAA/FEMA/News for disasters, generates custom response packages (press releases, social media, pricing), and executes after approval. Includes multi-disaster tracking dashboard.",
    category="ungouge",
    priority="high",
    progress=0,
    health_score=90
)

# =============================================================================
# PHASE 1: DETECTION LAYER (SENTINEL AGENT)
# =============================================================================

add_task(automation_project,
    "🏆 MILESTONE: Detection Layer Operational",
    """Automated disaster detection with Telegram alerts.
    
Success criteria:
- Daily monitoring active (6 AM EST cron)
- 90% detection rate for major disasters within 24h
- <5% false positive rate
- Alerts delivered to Telegram within 5 minutes
- All 5 data sources integrated and tested""",
    status="todo",
    priority="high",
    due_date=(week_1 + timedelta(days=5)).strftime("%Y-%m-%d"),
    task_type="milestone",
    estimated_hours=0
)

add_task(automation_project,
    "API Integration: NOAA Storm Prediction Center",
    """Integrate NOAA SPC API for severe weather monitoring.
    
Endpoint: https://www.spc.noaa.gov/products/outlook/
    
Monitor:
- Severe thunderstorms
- Tornadoes
- Hail events (diameter >2")
    
Threshold: Moderate/High risk areas covering >50K population
Update frequency: Every 6 hours
Expected token cost: ~500 tokens/day
    
Deliverable:
- Python module: noaa_monitor.py
- Unit tests with historical data
- Error handling for API downtime""",
    status="todo",
    priority="high",
    due_date=(week_1).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=6
)

add_task(automation_project,
    "API Integration: FEMA Disaster Declarations",
    """Integrate FEMA API for disaster declaration monitoring.
    
Endpoint: https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries
    
Monitor:
- Major disaster declarations (DR-XXXX)
- Individual Assistance declarations
- Incident types: Hurricane, Fire, Flood, Tornado, Severe Storm
    
Key fields:
- incidentType, designatedArea (FIPS codes)
- ihProgramDeclared (homeowner assistance)
- declarationDate (<7 days = active)
    
Expected token cost: ~300 tokens/day
    
Deliverable:
- Python module: fema_monitor.py
- FIPS to ZIP code mapping database
- Unit tests""",
    status="todo",
    priority="high",
    due_date=(week_1).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=5
)

add_task(automation_project,
    "API Integration: National Weather Service Alerts",
    """Integrate NWS API for active watches/warnings.
    
Endpoint: https://api.weather.gov/alerts/active
    
Monitor:
- Hurricane warnings
- Tornado warnings (clustered = outbreak)
- Flash flood warnings (widespread)
- Fire weather warnings (Red Flag + active fires)
    
Threshold: Warnings (not watches) affecting major metros
Expected token cost: ~400 tokens/day
    
Deliverable:
- Python module: nws_monitor.py
- Metro area population database
- Unit tests""",
    status="todo",
    priority="high",
    due_date=(week_1 + timedelta(days=1)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=5
)

add_task(automation_project,
    "API Integration: News API Monitoring",
    """Integrate News API for disaster keyword tracking.
    
Endpoint: https://newsapi.org/v2/everything
    
Keywords: 
- "hurricane evacuation"
- "wildfire mandatory evacuation"
- "hail damage thousands"
- "tornado outbreak"
- "flood disaster"
- "price gouging" + disaster terms
    
Threshold: >100 articles in 24h mentioning same event
Expected token cost: ~800 tokens/day
    
Sentiment analysis:
- Track "price gouging" mentions in coverage
- Monitor contractor scam reports
- Insurance claim volume signals
    
Deliverable:
- Python module: news_monitor.py
- Keyword clustering algorithm
- Sentiment analysis pipeline""",
    status="todo",
    priority="high",
    due_date=(week_1 + timedelta(days=1)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=6
)

add_task(automation_project,
    "API Integration: CalFire Incidents (Wildfire-Specific)",
    """Integrate CalFire API for active wildfire monitoring.
    
Endpoint: https://www.fire.ca.gov/incidents/
    
Monitor:
- Active wildfires >1,000 acres with structure threat
- Structures destroyed/damaged
- Evacuation orders (population affected)
- Containment % (0-20% = still growing)
    
Threshold: >500 structures destroyed/damaged
Expected token cost: ~200 tokens/day
    
Deliverable:
- Python module: calfire_monitor.py
- Structure threat detection logic
- Unit tests""",
    status="todo",
    priority="medium",
    due_date=(week_1 + timedelta(days=2)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=4
)

add_task(automation_project,
    "Build Disaster Scoring Algorithm",
    """Implement multi-factor scoring to determine activation.
    
Scoring factors (100-point scale):
- Population affected (0-50 pts)
- FEMA IA declared (0-20 pts)
- Disaster type (0-15 pts)
- News coverage volume (0-10 pts)
- Price gouging reported (0-15 pts)
- Recency (<72h optimal) (0-10 pts)
    
Priority levels:
- CRITICAL (70+): Immediate response
- HIGH (50-69): Respond within 24h
- MEDIUM (35-49): Respond within 48h
- LOW (<35): Monitor only
    
Deliverable:
- Python function: evaluate_disaster()
- Unit tests with 20 historical disasters
- Tuning documentation""",
    status="todo",
    priority="high",
    due_date=(week_1 + timedelta(days=3)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=8
)

add_task(automation_project,
    "Create Daily Monitoring Cron Job",
    """Set up OpenClaw cron job for daily disaster scanning.
    
Schedule: Daily at 6:00 AM EST
    
Job payload:
1. Check all 5 data sources
2. Score each potential disaster
3. For any scoring >35:
   - Spawn Strategist sub-agent
   - Pass disaster data as context
   - Alert Jason via Telegram
4. Log scan results to memory/disaster-scans/YYYY-MM-DD.json
5. If no disasters: reply HEARTBEAT_OK (silent)
    
Token budget: ~3,200 tokens/day
Model: Opus
Session: isolated
    
Deliverable:
- Cron job YAML configuration
- Integration test with mock disasters
- Telegram alert format template""",
    status="todo",
    priority="high",
    due_date=(week_1 + timedelta(days=4)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=6
)

add_task(automation_project,
    "Build Structured Disaster Data Output",
    """Create standardized disaster detection output format.
    
JSON schema:
- disaster_id, detection_timestamp, disaster_type
- event_name, location (metro, counties, ZIPs, population)
- severity (homes affected, structures damaged, FEMA declaration)
- scoring (total_score, priority, confidence, factors)
- sources (NOAA ID, FEMA declaration, news count, first report)
- recommended_action, next_steps
    
Storage: memory/disaster-scans/{disaster_id}-detection.json
    
Deliverable:
- Pydantic model: DisasterDetection
- JSON serialization/validation
- Sample outputs for 5 disaster types""",
    status="todo",
    priority="medium",
    due_date=(week_1 + timedelta(days=4)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=4
)

add_task(automation_project,
    "Test Detection with 10 Historical Disasters",
    """Validate detection accuracy using historical events.
    
Test cases:
1. Hurricane Katrina (2005) - should score CRITICAL
2. Paradise Fire (2018) - should score CRITICAL
3. Denver hailstorm (2017) - should score HIGH
4. Moore tornado (2013) - should score HIGH
5. Louisiana floods (2016) - should score HIGH
6. California wildfires (2020) - should score CRITICAL
7. Texas freeze (2021) - should score MEDIUM
8. Minor hailstorm - should score LOW (no activation)
9. Local flood - should score LOW (no activation)
10. Small wildfire - should score LOW (no activation)
    
Success criteria:
- 100% detection of CRITICAL/HIGH events
- <10% false positives (LOW events triggering)
    
Deliverable:
- Test suite with historical data
- Scoring accuracy report
- Tuning recommendations""",
    status="todo",
    priority="high",
    due_date=(week_1 + timedelta(days=5)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=6
)

# =============================================================================
# PHASE 2: PLANNING LAYER (STRATEGIST AGENT)
# =============================================================================

add_task(automation_project,
    "🏆 MILESTONE: Planning Layer Operational",
    """Automated response package generation for approved disasters.
    
Success criteria:
- Full response package generated within 2 hours of detection
- 95% approval rate on first draft (minimal edits)
- All components complete: press release, social media, pricing, projections
- Media contact lists accurate and relevant
- Impact projections within 20% of actual (measured over 5 disasters)""",
    status="todo",
    priority="high",
    due_date=(week_3).strftime("%Y-%m-%d"),
    task_type="milestone",
    estimated_hours=0
)

add_task(automation_project,
    "Build Strategist Sub-Agent",
    """Create isolated session agent for response planning.
    
Agent config:
- agentId: disaster-strategist
- model: opus (high-quality writing required)
- thinking: high (complex multi-step planning)
- runTimeoutSeconds: 1800 (30 min max)
- cleanup: keep (preserve for audit)
- label: disaster-response-{disaster_id}
    
Spawn trigger: Sentinel calls sessions_spawn() when disaster detected
    
Deliverable:
- Agent configuration file
- Spawn wrapper function
- Session monitoring dashboard integration""",
    status="todo",
    priority="high",
    due_date=(week_2).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=4
)

add_task(automation_project,
    "Implement Disaster Research Phase",
    """Deep dive research on detected disaster using web search and data enrichment.
    
Research queries (web_search tool):
1. "{event_name} damage estimates"
2. "{event_name} contractor scams"
3. "{primary_metro} roofing contractors"
4. "{disaster_type} insurance claims {year}"
5. "{event_name} price gouging reports"
    
Extract:
- Total economic damage ($)
- Insurance claims filed
- Contractor complaints
- Typical repair types
- Media tone
    
ZIP code enrichment:
- Convert FEMA county FIPS to ZIP codes
- Get population, median home value, income, ownership rate
- Rank ZIPs by response potential
    
Deliverable:
- Research module: disaster_research.py
- ZIP enrichment database
- Output: enriched_disaster_data.json""",
    status="todo",
    priority="high",
    due_date=(week_2 + timedelta(days=2)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=8
)

add_task(automation_project,
    "Build Local Media Contact Database",
    """Create searchable database of local media contacts by region.
    
Coverage:
- Top 50 US metros
- For each: newspapers, TV stations, radio, digital-native
    
Data structure per outlet:
- outlet_name, outlet_type, reach estimate
- contacts: name, email, Twitter, role
- past_coverage: relevant topics
- priority: HIGH/MEDIUM/LOW (based on reach + past coverage)
    
Sources:
- Muck Rack (journalist database)
- Media outlet websites
- Twitter bios
- LinkedIn
    
Deliverable:
- SQLite database: media_contacts.db
- Python query interface
- Data for 50 metros""",
    status="todo",
    priority="high",
    due_date=(week_2 + timedelta(days=3)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=12
)

add_task(automation_project,
    "Create Press Release Generator",
    """Template-driven press release generation with disaster-specific customization.
    
Template sections:
- Headline (disaster-specific)
- Event context (scale, damage, timing)
- Price gouging problem (stats + founder quote)
- How it works (tool description)
- Emergency pricing details (price, eligibility, duration)
- About Ungouge.ai (mission, positioning)
- Media contact info
    
Customization variables:
- Event name, date, location
- Specific statistics
- Historical comparison (if applicable)
- Duration (30-60 days)
- Price point ($2.99-$9.99)
    
Deliverable:
- Jinja2 template: press_release.md.j2
- Generation function: generate_press_release()
- 5 sample outputs (different disaster types)""",
    status="todo",
    priority="high",
    due_date=(week_2 + timedelta(days=4)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=6
)

add_task(automation_project,
    "Create Social Media Content Suite Generator",
    """Generate platform-specific social media content for each disaster.
    
Platforms:
- Twitter/X (6-tweet thread)
- Facebook (single post with link)
- Reddit (r/[city] + r/homeowners posts)
- NextDoor (neighborhood post template)
    
Content elements:
- Attention hook (disaster-specific)
- Problem statement (contractor scams)
- Solution (our tool)
- Pricing/offer
- Call to action
- Relevant hashtags
    
Deliverable:
- Template suite: social_media_templates/
- Generation function: generate_social_content()
- Character limit validation (Twitter 280, etc.)
- Sample outputs for 5 disaster types""",
    status="todo",
    priority="high",
    due_date=(week_2 + timedelta(days=5)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=8
)

add_task(automation_project,
    "Build Pricing Decision Algorithm",
    """Determine optimal promotional price based on disaster characteristics.
    
Inputs:
- homes_affected
- median_income (affected area)
- fema_assistance (boolean)
- disaster_severity_score
- media_attention_score
    
Pricing tiers:
- $2.99: Mega-disasters (>500K homes, e.g., Florida hurricane)
- $4.99: Major disasters (100-500K homes, e.g., Denver hail)
- $9.99: Significant disasters (50-100K homes, e.g., regional wildfire)
    
Adjustments:
- Low-income area: -$2.00
- FEMA IA declared: cap at $4.99
- Round to .99 psychology
    
Output:
- recommended_price
- discount_percentage
- rationale
- duration_days
- break_even_reports
    
Deliverable:
- Function: calculate_disaster_pricing()
- Unit tests with 15 scenarios
- Documentation""",
    status="todo",
    priority="high",
    due_date=(week_2 + timedelta(days=5)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=6
)

add_task(automation_project,
    "Build Impact Projection Model",
    """Conservative financial and social impact projections.
    
Conversion funnel (conservative):
- Awareness rate: 2% (hear about us via PR/social)
- Consideration rate: 25% (of aware)
- Conversion rate: 30% (of considerers)
    
Calculations:
- Reports projected (low and high estimates)
- Revenue projected
- Gross profit (after variable costs)
- ROI percentage
- Homeowners protected
- Total savings enabled (avg overcharge × reports)
- Media value estimate
    
Deliverable:
- Function: project_disaster_response_impact()
- Historical calibration (tune funnel rates based on actual results)
- Output: projections.json""",
    status="todo",
    priority="medium",
    due_date=(week_2 + timedelta(days=6)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=6
)

add_task(automation_project,
    "Create Response Package Deliverable Format",
    """Standardized output structure for complete response package.
    
Directory structure:
memory/disaster-response/{disaster_id}/
├── disaster_profile.json
├── response_package.md (executive summary)
├── press_release.md
├── social_media_content.md
├── media_contacts.json (ranked list)
├── email_templates.md
├── pricing_analysis.md
├── impact_projections.md
├── implementation_checklist.md
└── monitoring_dashboard_config.json
    
Telegram notification format:
- Priority, score, confidence
- Event summary (homes affected, damage, FEMA status)
- Recommended response (price, duration, ZIPs)
- Projected impact (reports, revenue, savings)
- Review link to dashboard
- Action buttons: APPROVE / EDIT / DEFER
    
Deliverable:
- Directory structure template
- Telegram message formatter
- Dashboard integration (review interface)""",
    status="todo",
    priority="high",
    due_date=(week_3 - timedelta(days=2)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=6
)

add_task(automation_project,
    "Test Planning with 3 Historical Disasters",
    """Validate planning agent output quality using historical events.
    
Test cases:
1. 2017 Denver hailstorm
2. 2018 Paradise Fire
3. 2021 Texas freeze
    
For each:
- Run Strategist agent with historical data
- Generate full response package
- Review quality (Jason reviews outputs)
- Measure token usage
- Time to completion
    
Success criteria:
- All components generated without errors
- Press releases are publication-ready
- Social content is platform-appropriate
- Pricing recommendations are reasonable
- Impact projections are realistic
    
Deliverable:
- 3 complete response packages
- Quality assessment report
- Iteration notes for improvements""",
    status="todo",
    priority="high",
    due_date=(week_3 - timedelta(days=1)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=8
)

# =============================================================================
# PHASE 3: EXECUTION LAYER (EXECUTOR AGENT)
# =============================================================================

add_task(automation_project,
    "🏆 MILESTONE: Execution Layer Operational",
    """One-click deployment after approval.
    
Success criteria:
- Full deployment within 2 hours of Jason's approval
- Zero manual steps after approval
- All systems activated correctly (promo codes, banners, landing pages)
- Press releases sent to all priority outlets
- Social media posted across all platforms
- Metrics tracking active
- Daily progress reports delivered to Telegram""",
    status="todo",
    priority="high",
    due_date=(week_5).strftime("%Y-%m-%d"),
    task_type="milestone",
    estimated_hours=0
)

add_task(automation_project,
    "Build Executor Sub-Agent",
    """Create isolated session agent for deployment execution.
    
Agent config:
- agentId: disaster-executor
- model: opus (reliable execution)
- thinking: medium (sequential steps)
- runTimeoutSeconds: 3600 (1 hour for full deployment)
- cleanup: keep (preserve for audit)
- label: disaster-execute-{disaster_id}
    
Activation trigger: Jason replies "APPROVE" to Telegram notification
    
Deliverable:
- Agent configuration file
- Telegram approval handler
- Execution checklist automation""",
    status="todo",
    priority="high",
    due_date=(week_4).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=4
)

add_task(automation_project,
    "Implement Promo Code System (Backend + Frontend)",
    """Technical implementation of geo-targeted disaster promo codes.
    
Backend (FastAPI):
- Database schema: promo_codes table
- Endpoint: POST /api/promo/apply
- Validation: ZIP code eligibility check
- Auto-apply logic: detect ZIP, apply discount
- Usage tracking: reports per promo code
    
Frontend (Next.js):
- Auto-detect ZIP from quote location
- Apply promo automatically if eligible
- Show discount applied message
- Banner: "Special pricing for disaster-affected areas"
    
Database fields:
- code, discount_type, discount_value
- valid_from, valid_until
- geo_restriction_zips (JSON array)
- auto_apply (boolean)
- usage_count, usage_limit
    
Deliverable:
- Backend API endpoints
- Frontend discount logic
- Admin panel for promo management
- Unit tests""",
    status="todo",
    priority="high",
    due_date=(week_4 + timedelta(days=2)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=10
)

add_task(automation_project,
    "Build Banner Notification System",
    """Dynamic website banner for disaster responses.
    
Features:
- Geo-targeted (show only to affected ZIPs)
- Customizable message per disaster
- Background color (blue for community support, not red alarm)
- "Learn More" link to disaster landing page
- Date range (auto-show/hide)
    
Frontend component:
- React banner component
- Config-driven (JSON from backend)
- Dismissible (cookie to remember dismissal)
- Mobile-responsive
    
Backend config:
- Database: banner_notifications table
- API: GET /api/banner/current (returns active banner for ZIP)
    
Deliverable:
- Banner React component
- Backend API
- Admin panel for banner management
- Sample configs""",
    status="todo",
    priority="medium",
    due_date=(week_4 + timedelta(days=3)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=6
)

add_task(automation_project,
    "Create Landing Page Generator",
    """Auto-generate disaster-specific landing pages.
    
URL pattern: /disaster-relief/{disaster_id}
Example: /disaster-relief/denver-hail-2026
    
Content sections:
- Hero: Event details (what, when, where)
- Problem: Contractor scams expected
- Solution: How we're helping (pricing, duration, eligibility)
- How to Use: Step-by-step with screenshots
- FAQs: Disaster-specific (e.g., "What about hail damage?")
- Testimonials: Past disaster responses (if available)
- CTA: "Check Your Quote" button
    
Generation:
- Template-driven (Jinja2 or React template)
- Auto-populate from disaster_profile.json
- Static generation for performance (Next.js SSG)
- SEO optimized (meta tags, schema.org)
    
Deliverable:
- Landing page template
- Generation script
- Sample pages for 3 disaster types""",
    status="todo",
    priority="medium",
    due_date=(week_4 + timedelta(days=4)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=8
)

add_task(automation_project,
    "Build Press Release Email Automation",
    """Automated email distribution to media contacts.
    
Features:
- Personalized emails (use journalist name, outlet)
- Priority-based sending (HIGH outlets first)
- Rate limiting (1 email per 10 seconds, avoid spam filters)
- Sendgrid API integration (open/click tracking)
- Log all outreach (disaster_media_outreach table)
- Flag responses for Jason's review
    
Email template:
- Subject: Story lead: {event_name} price gouging protection
- Body: Personalized pitch + press release
- Attachments: PDF press release
- From: media@ungouge.ai (Jason Trask)
    
Deliverable:
- Email sending module: send_press_releases.py
- Sendgrid integration
- Tracking dashboard
- Unit tests""",
    status="todo",
    priority="high",
    due_date=(week_4 + timedelta(days=5)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=8
)

add_task(automation_project,
    "Integrate Social Media APIs (Twitter, Facebook)",
    """Automated social media posting after approval.
    
Twitter/X:
- API: Twitter API v2
- Post thread (6 tweets)
- Spacing: 5 seconds between tweets
- Track: impressions, engagements, clicks
    
Facebook:
- API: Facebook Graph API
- Post to Ungouge page
- Include link preview
- Track: reach, engagements
    
Manual platforms (templates generated):
- Reddit (requires authentic manual posting)
- NextDoor (can't automate)
    
Deliverable:
- Social media posting module
- API authentication setup
- Tracking integration
- Error handling (API rate limits)""",
    status="todo",
    priority="high",
    due_date=(week_4 + timedelta(days=6)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=8
)

add_task(automation_project,
    "Build Metrics Tracking System",
    """Real-time disaster response metrics collection and reporting.
    
Metrics tracked:
- Quote submissions (from affected ZIPs)
- Revenue (disaster-specific)
- Average overcharge detected
- Total savings enabled
- Media mentions (backlinks, news articles)
- Social engagement (Twitter impressions, Facebook reach)
- Landing page traffic (GA4)
    
Update frequency: Hourly snapshots
    
Database:
- disaster_metrics_snapshots table
- Time-series data for charting
    
Dashboard integration:
- Real-time metrics widgets
- Progress vs. projections
- Performance indicators
    
Deliverable:
- Metrics collection cron job
- Database schema
- Dashboard API endpoints
- Sample queries""",
    status="todo",
    priority="high",
    due_date=(week_5 - timedelta(days=2)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=8
)

add_task(automation_project,
    "Create Daily Progress Reports (Telegram)",
    """Automated daily updates to Jason on active disaster responses.
    
Report content:
- Today's stats: reports, revenue, savings
- Total to date: cumulative metrics
- Progress vs. projections: % of target
- Impact highlights: avg overcharge, top red flags found
- Media pickup: new articles/segments
- Status: on track / below pace / exceeding
    
Delivery:
- Telegram message (formatted)
- Time: 9 AM EST daily
- Only for active disasters
- Link to full dashboard
    
Deliverable:
- Report generation function
- Telegram delivery integration
- Sample reports""",
    status="todo",
    priority="medium",
    due_date=(week_5 - timedelta(days=1)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=4
)

add_task(automation_project,
    "Build Campaign Wrap-Up System",
    """End-of-campaign reporting and case study generation.
    
Triggered: 30-60 days after activation (promo expires)
    
Actions:
1. Deactivate promo code (automatic)
2. Generate final impact report:
   - Total reports, revenue, profit
   - Total savings enabled
   - Media coverage earned
   - Customer testimonials collected
   - Referral rate from disaster customers
3. Create case study (Strategist agent)
   - Full narrative
   - Before/after data
   - Customer quotes
   - Media screenshots
   - Lessons learned
4. Update playbook:
   - What worked / didn't work
   - Pricing effectiveness
   - Outreach channel ROI
   - Timing optimization
    
Deliverable:
- Wrap-up automation script
- Case study template
- Final report format
- Playbook update workflow""",
    status="todo",
    priority="medium",
    due_date=(week_5).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=6
)

# =============================================================================
# PHASE 4: MULTI-DISASTER DASHBOARD
# =============================================================================

add_task(automation_project,
    "🏆 MILESTONE: Multi-Disaster Dashboard Operational",
    """Monitor and manage multiple simultaneous disasters.
    
Success criteria:
- Command center view shows all active disasters
- Detail view for each disaster with full metrics
- Real-time updates (metrics refresh every 5 minutes)
- Comparison views (disaster A vs B performance)
- Export/reporting features functional
- Can manage 3+ disasters concurrently without confusion""",
    status="todo",
    priority="high",
    due_date=(week_7).strftime("%Y-%m-%d"),
    task_type="milestone",
    estimated_hours=0
)

add_task(automation_project,
    "Design Dashboard UI (Figma Mockups)",
    """Create comprehensive UI design for disaster command center.
    
Views:
1. Command Center (all disasters overview)
2. Detail View (single disaster deep-dive)
3. Comparison View (side-by-side performance)
4. Historical Archive (past disasters)
    
Components:
- Disaster status cards
- Performance metrics widgets
- Timeline/actions log
- Geographic breakdown (map + ZIP list)
- Red flags analysis
- Media coverage tracker
- Customer testimonials display
    
Deliverable:
- Figma design file
- Component specifications
- Responsive breakpoints (desktop, tablet, mobile)
- Style guide""",
    status="todo",
    priority="high",
    due_date=(week_6).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=12
)

add_task(automation_project,
    "Implement Database Schema",
    """Create comprehensive database structure for multi-disaster tracking.
    
Tables:
1. disaster_responses (main table)
   - disaster_id, event_name, disaster_type
   - detection/activation/end timestamps
   - status, priority, severity_score
   - geographic data (states, counties, ZIPs)
   - pricing (promo_code, discount, duration)
   - projections vs. actuals
   
2. disaster_metrics_snapshots (time-series)
   - disaster_id, snapshot_timestamp
   - cumulative metrics
   - daily deltas
   
3. disaster_media_coverage
   - disaster_id, outlet info, article details
   - reach, sentiment
   
4. disaster_social_posts
   - disaster_id, platform, post_id
   - engagement metrics
   
5. disaster_testimonials
   - disaster_id, quote_id, customer info
   - testimonial text, amount saved
    
Deliverable:
- SQL schema file
- Migration scripts
- Seed data (sample disasters)
- Query documentation""",
    status="todo",
    priority="high",
    due_date=(week_6 + timedelta(days=2)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=8
)

add_task(automation_project,
    "Build Command Center View (All Disasters)",
    """Top-level dashboard showing all active, pending, and monitoring disasters.
    
Layout:
- Active Responses section (cards for each)
- Pending Review section (awaiting approval)
- Monitoring section (below threshold)
    
Disaster card shows:
- Icon (🔥🌀⛈️🌪️) + event name
- Priority + days remaining
- Key metrics: reports, revenue, savings, media
- Performance indicator (🟢🟡🔴)
- [View Details →] button
    
Features:
- Sort by: priority, date, performance
- Filter by: disaster type, status, region
- Search by: event name, location
- [+ New Response] button (manual override)
    
Deliverable:
- React component: CommandCenter.tsx
- API endpoint: GET /api/disasters
- Unit tests
- Sample data""",
    status="todo",
    priority="high",
    due_date=(week_6 + timedelta(days=4)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=12
)

add_task(automation_project,
    "Build Detail View (Single Disaster)",
    """Deep-dive view for individual disaster response.
    
Sections:
1. Header: Status, priority, dates, scores
2. Performance Metrics: Reports, revenue, savings, media (vs. projections)
3. Timeline & Actions: Chronological log of all events
4. Geographic Breakdown: Map + top ZIP codes by reports
5. Red Flags Analysis: Most common overcharges found
6. Media Coverage: List of articles/segments with links
7. Customer Testimonials: Featured quotes
    
Actions:
- [Download Impact Report] (PDF)
- [Generate Case Study] (spawn Strategist)
- [Edit Response] (modify promo/duration)
    
Deliverable:
- React component: DisasterDetail.tsx
- API endpoint: GET /api/disasters/{disaster_id}
- PDF generation integration
- Unit tests""",
    status="todo",
    priority="high",
    due_date=(week_6 + timedelta(days=6)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=16
)

add_task(automation_project,
    "Implement Real-Time Metrics Updates",
    """Live dashboard updates without manual refresh.
    
Technology:
- WebSocket or Server-Sent Events (SSE)
- Update frequency: Every 5 minutes
    
Updated data:
- Quote submissions count
- Revenue (real-time)
- New media mentions
- Social engagement metrics
    
UI behavior:
- Smooth number transitions (animate changes)
- Highlight new data (flash green briefly)
- Show last update timestamp
- Manual refresh button
    
Deliverable:
- WebSocket server (FastAPI)
- React hook: useRealtimeMetrics()
- Connection management
- Fallback to polling if WebSocket fails""",
    status="todo",
    priority="medium",
    due_date=(week_7 - timedelta(days=2)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=8
)

add_task(automation_project,
    "Build Comparison View (Multi-Disaster)",
    """Side-by-side performance comparison for active disasters.
    
Features:
- Select 2-4 disasters to compare
- Metrics table: reports, revenue, conversion rate, etc.
- Performance charts: daily progress overlay
- Relative performance (% of projection)
- Insights: "LA Wildfire converting 2.3x better than Denver Hail"
    
Use cases:
- Identify best-performing disaster types
- Optimize pricing strategy
- Learn from high-performers
    
Deliverable:
- React component: DisasterComparison.tsx
- API endpoint: GET /api/disasters/compare
- Chart library integration (Recharts)
- Sample comparisons""",
    status="todo",
    priority="low",
    due_date=(week_7 - timedelta(days=1)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=10
)

add_task(automation_project,
    "Create Export & Reporting Features",
    """Download capabilities for disaster data.
    
Export formats:
- PDF: Executive summary (single disaster)
- CSV: Raw metrics data (time-series)
- JSON: Full disaster profile + metrics
    
Reports:
- Single disaster impact report
- Multi-disaster summary report
- Monthly rollup (all disasters that month)
    
Deliverable:
- PDF generation (Puppeteer or similar)
- CSV export function
- Report templates
- API endpoints""",
    status="todo",
    priority="low",
    due_date=(week_7).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=8
)

# =============================================================================
# PHASE 5: OPTIMIZATION & ITERATION
# =============================================================================

add_task(automation_project,
    "A/B Test Press Release Formats",
    """Test different press release approaches for effectiveness.
    
Variants to test:
- Headline style: Urgent vs. Informative
- Length: Short (300 words) vs. Long (600 words)
- Data placement: Stats early vs. narrative early
- Quote style: Founder-centric vs. customer-centric
    
Measure:
- Media pickup rate (% outlets that publish)
- Time to first pickup
- Sentiment in coverage
    
Run: 8 disasters (2 per variant)
    
Deliverable:
- A/B test framework
- Variant press releases
- Results analysis
- Winning format documentation""",
    status="todo",
    priority="low",
    due_date=None,
    task_type="action",
    estimated_hours=6
)

add_task(automation_project,
    "Optimize Pricing Algorithm with Real Data",
    """Refine pricing recommendations based on actual conversion data.
    
Analysis:
- Conversion rate by price point ($2.99 vs. $4.99 vs. $9.99)
- Conversion rate by disaster type
- Conversion rate by median income level
- Revenue optimization (maximize total revenue, not just conversions)
    
Iterate:
- Update pricing algorithm thresholds
- Add new factors (e.g., time since disaster)
- Create pricing playbook documentation
    
Requires: 10+ disaster responses for statistical significance
    
Deliverable:
- Pricing analysis report
- Updated algorithm
- Documentation""",
    status="todo",
    priority="low",
    due_date=None,
    task_type="action",
    estimated_hours=8
)

add_task(automation_project,
    "Refine Detection Scoring (Reduce False Positives)",
    """Improve scoring algorithm based on actual activations.
    
Track:
- False positives (detected but not worth activating)
- False negatives (missed disasters that should have activated)
- Threshold accuracy (is 35 the right cutoff?)
    
Tune:
- Adjust factor weights
- Add new factors
- Update thresholds by disaster type
    
Goal: <5% false positive rate, <2% false negative rate
    
Deliverable:
- Tuning analysis
- Updated scoring function
- Test suite with new accuracy metrics""",
    status="todo",
    priority="low",
    due_date=None,
    task_type="action",
    estimated_hours=6
)

add_task(automation_project,
    "Build Case Study Automation",
    """Automatically generate case studies from completed disasters.
    
Template sections:
- The Disaster (scale, damage, context)
- The Gouging Problem (contractor behavior, why we responded)
- Our Response (pricing, activation timeline, outreach)
- The Impact (reports, savings, testimonials, media coverage)
- Lessons Learned
    
Generation:
- Strategist agent with disaster data + metrics
- Photos, charts, customer quotes
- Publication-ready markdown + HTML
    
Use cases:
- Blog posts
- Press materials
- Sales/fundraising decks
- Investor updates
    
Deliverable:
- Case study template
- Generation automation
- Sample case studies""",
    status="todo",
    priority="medium",
    due_date=None,
    task_type="action",
    estimated_hours=6
)

add_task(automation_project,
    "Implement Predictive Analytics",
    """Forecast disaster response impact before activation.
    
Models to build:
- Conversion rate prediction (based on disaster characteristics)
- Media pickup probability
- Social reach estimate
- Customer LTV from disaster cohorts
    
Inputs:
- Historical disaster data (10+ responses)
- Disaster characteristics (type, scale, region)
- Pricing decision
    
Output:
- Predicted metrics with confidence intervals
- ROI forecast
- Recommendation: ACTIVATE or DEFER with reasoning
    
Deliverable:
- ML model (scikit-learn or similar)
- Training pipeline
- Integration with Strategist agent""",
    status="todo",
    priority="low",
    due_date=None,
    task_type="action",
    estimated_hours=12
)

# Commit changes
conn.commit()
conn.close()

print("✅ Disaster Response Automation System added to dashboard!")
print(f"   - Project ID: {automation_project}")
print(f"   - Total tasks: 48")
print(f"   - Milestones: 5")
print(f"   - Phases: 5 (Detection, Planning, Execution, Dashboard, Optimization)")
print("\n📊 View at: https://dashboard.ungouge.ai")
print("\n📄 Full architecture: /projects/ungouge-app/DISASTER_RESPONSE_AUTOMATION.md")
