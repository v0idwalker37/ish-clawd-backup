#!/usr/bin/env python3
"""
Add Disaster Response Pricing Program to UnGouge Dashboard
Community support pricing for disaster-affected areas
"""

import sqlite3
from datetime import datetime, timedelta

# Connect to dashboard database
DB_PATH = "/Users/moltbot/clawd/projects/ungouge-dashboard/backend/dashboard.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Calculate dates
today = datetime.now()
week_2 = today + timedelta(weeks=2)
week_4 = today + timedelta(weeks=4)

def add_project(name, description, category, priority="medium", progress=0):
    """Add a project and return its ID"""
    cursor.execute("""
        INSERT INTO projects (name, description, status, category, priority, progress, health_score)
        VALUES (?, ?, 'active', ?, ?, ?, 85)
    """, (name, description, category, priority, progress))
    return cursor.lastrowid

def add_task(project_id, title, description, status='todo', priority='medium', due_date=None, task_type='action', estimated_hours=None):
    """Add a task to a project"""
    cursor.execute("""
        INSERT INTO tasks (project_id, title, description, status, priority, due_date, task_type, estimated_hours)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (project_id, title, description, status, priority, due_date, task_type, estimated_hours))

# =============================================================================
# DISASTER RESPONSE PRICING PROGRAM
# =============================================================================

disaster_project = add_project(
    name="Disaster Response Pricing Program",
    description="Community support pricing for disaster-affected areas. Deploy rapid-response $4.99 pricing when major disasters strike (hurricanes, wildfires, hailstorms). Position Ungouge as consumer advocate during peak gouging season.",
    category="ungouge",
    priority="medium",
    progress=0
)

# MILESTONE 1: Build Playbook & Infrastructure
add_task(disaster_project,
    "MILESTONE: Playbook & Infrastructure Complete",
    "All systems ready to activate disaster response within 48 hours of major event",
    status="todo",
    priority="high",
    due_date=(week_2).strftime("%Y-%m-%d"),
    task_type="milestone",
    estimated_hours=0
)

add_task(disaster_project,
    "Create Disaster Response Playbook",
    """Document step-by-step activation process:
    
1. Trigger criteria (what qualifies as disaster?)
2. Pricing decision tree ($2.99 vs $4.99)
3. Geographic targeting (ZIP code lists)
4. Timeline (activate within 48 hours)
5. Duration (30-60 day windows)
6. Deactivation process

Include real examples: hurricanes, wildfires, hailstorms, tornadoes, floods.""",
    status="todo",
    priority="high",
    due_date=(week_2 - timedelta(days=4)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=3
)

add_task(disaster_project,
    "Build Geo-Targeted Promo Code System",
    """Technical implementation:
    
- Auto-detect ZIP code from quote location
- Match against disaster-affected ZIP list
- Auto-apply promo code (e.g., DENVER_HAIL_2026)
- Banner: 'Special pricing for disaster-affected areas'
- Time-limited (configurable end date)
- Admin panel to activate/deactivate

Backend endpoint: /api/promo/check-disaster-eligibility""",
    status="todo",
    priority="high",
    due_date=(week_2 - timedelta(days=2)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=4
)

add_task(disaster_project,
    "Create Press Release Template",
    """Reusable template for rapid deployment:
    
'[Company] Offers $X.XX Quote Verification to [Disaster] Victims'

Sections:
- Headline
- Context (disaster details, # affected)
- Our response (pricing, duration, eligibility)
- Quote from founder (Jason)
- Anti-gouging mission statement
- Contact info

2-3 versions: hurricane, wildfire, hailstorm""",
    status="todo",
    priority="medium",
    due_date=(week_2 - timedelta(days=3)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=2
)

add_task(disaster_project,
    "Build Social Media Content Kit",
    """Templates for rapid deployment across platforms:
    
- Twitter/X thread (4-6 tweets)
- Facebook post
- Reddit post (r/[city], r/homeowners)
- NextDoor template
- Instagram story/post
- LinkedIn announcement

All variations of 'We stand with [city]' messaging.
Include image templates with pricing.""",
    status="todo",
    priority="medium",
    due_date=(week_2 - timedelta(days=1)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=3
)

add_task(disaster_project,
    "Create Media Contact Database",
    """Build searchable database of local media by region:
    
- Top 50 US metros
- For each: newspapers, TV stations, radio
- Contact emails, Twitter handles
- Beat reporters (consumer affairs, business)
- Submission forms for press releases

Use when disaster strikes specific region.""",
    status="todo",
    priority="low",
    due_date=(week_4).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=4
)

# MILESTONE 2: First Response Executed
add_task(disaster_project,
    "MILESTONE: First Disaster Response Deployed",
    "Successfully activated pricing program for first major disaster event",
    status="todo",
    priority="high",
    due_date=None,  # TBD based on when disaster occurs
    task_type="milestone",
    estimated_hours=0
)

add_task(disaster_project,
    "Monitor NOAA/FEMA Alerts",
    """Set up monitoring for disaster events:
    
Sources:
- NOAA weather alerts (hurricanes, tornadoes)
- FEMA disaster declarations
- News alerts for major events
- Insurance industry reports (hailstorms)

Create Slack/email alert when major event detected.
Trigger: >50K homes affected""",
    status="todo",
    priority="medium",
    due_date=(week_2).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=2
)

add_task(disaster_project,
    "Activate First Disaster Response",
    """When major disaster hits:
    
1. Review playbook (confirm eligibility)
2. Decide pricing ($2.99-$4.99) based on scale
3. Get affected ZIP codes from FEMA/insurance data
4. Activate promo code in system
5. Customize press release for event
6. Send to local media (within 48h of disaster)
7. Deploy social media campaign
8. Monitor engagement/conversions

Document everything for case study.""",
    status="todo",
    priority="high",
    due_date=None,  # When disaster occurs
    task_type="action",
    estimated_hours=6
)

# MILESTONE 3: Impact Report Published
add_task(disaster_project,
    "MILESTONE: Impact Report & Case Study Complete",
    "Published success story showing homes protected and savings generated",
    status="todo",
    priority="medium",
    due_date=None,  # 30-60 days after first response
    task_type="milestone",
    estimated_hours=0
)

add_task(disaster_project,
    "Track Impact Metrics",
    """For each disaster response, track:
    
- # of reports submitted from affected area
- Total savings vs. inflated quotes
- Average overcharge detected (%)
- Media coverage (articles, TV segments)
- Social media reach/engagement
- Customer testimonials collected
- Referral rate from affected customers

Dashboard widget: 'Disaster Response Impact'""",
    status="todo",
    priority="medium",
    due_date=None,
    task_type="action",
    estimated_hours=2
)

add_task(disaster_project,
    "Create Case Study Template",
    """Reusable format for success stories:
    
Title: 'How Ungouge Protected [City] Homeowners After [Disaster]'

Sections:
- The disaster (scale, damage)
- The gouging problem (contractor behavior)
- Our response (pricing, activation timeline)
- The impact (# reports, $ saved, testimonials)
- Media coverage earned
- Lessons learned

Photos, charts, quotes from real customers.
Use for blog, press, sales materials.""",
    status="todo",
    priority="low",
    due_date=None,
    task_type="action",
    estimated_hours=3
)

add_task(disaster_project,
    "Publish First Case Study",
    """Turn first disaster response into compelling story:
    
- Write 1,500-2,000 word case study
- Include real customer quotes/testimonials
- Create infographic (savings, # protected)
- Publish on blog
- Share to social media
- Pitch to industry publications
- Use as sales/fundraising material

This becomes proof of concept for the program.""",
    status="todo",
    priority="medium",
    due_date=None,
    task_type="action",
    estimated_hours=4
)

# Additional Strategic Tasks
add_task(disaster_project,
    "Partner Outreach: Community Organizations",
    """Build partnerships for faster activation:
    
Potential partners:
- Local disaster relief nonprofits
- Consumer protection agencies
- BBB chapters
- Homeowner advocacy groups
- Insurance consumer advocates

Offer to co-brand disaster response.
They get tool for constituents, we get distribution.""",
    status="todo",
    priority="low",
    due_date=(week_4 + timedelta(weeks=2)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=4
)

add_task(disaster_project,
    "Legal Review: Disaster Pricing Compliance",
    """Ensure program complies with anti-gouging laws:
    
Research:
- State price-gouging laws (are we exempt as protector?)
- FTC guidelines on disaster advertising
- Insurance industry coordination (NAIC)
- Tax implications of discounted services

Consult attorney if needed. Document compliance.""",
    status="todo",
    priority="medium",
    due_date=(week_4).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=3
)

add_task(disaster_project,
    "Revenue Model Analysis",
    """Financial projections for disaster response:
    
Model scenarios:
- Hurricane (500K affected, 5% conversion)
- Wildfire (100K affected, 3% conversion)
- Major hailstorm (250K affected, 5% conversion)

At $4.99 pricing:
- Revenue per event
- Cost (tokens, infrastructure)
- Gross margin
- Customer LTV (post-disaster)
- Brand equity value

Justify program to investors/board.""",
    status="todo",
    priority="low",
    due_date=(week_4 + timedelta(weeks=1)).strftime("%Y-%m-%d"),
    task_type="action",
    estimated_hours=2
)

# Commit changes
conn.commit()
conn.close()

print("✅ Disaster Response Pricing Program added to dashboard!")
print(f"   - Project ID: {disaster_project}")
print(f"   - Total tasks: 13")
print(f"   - Milestones: 3")
print("\n📊 View at: https://dashboard.ungouge.ai")
