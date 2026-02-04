#!/usr/bin/env python3
"""
Add Launch Plan tasks to UnGouge Dashboard
Organizes Week 1-3 tasks by project area
"""

import sqlite3
from datetime import datetime, timedelta

# Connect to dashboard database
DB_PATH = "/tmp/dashboard.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Calculate dates
today = datetime.now()
week_1_start = today
week_2_start = today + timedelta(weeks=1)
week_3_start = today + timedelta(weeks=2)

def add_project(name, description, category, priority="medium", progress=0):
    """Add a project and return its ID"""
    cursor.execute("""
        INSERT INTO projects (name, description, status, category, priority, progress, health_score)
        VALUES (?, ?, 'active', ?, ?, ?, 70)
    """, (name, description, category, priority, progress))
    return cursor.lastrowid

def add_task(project_id, title, description, status='todo', priority='medium', due_date=None, task_type='action', estimated_hours=None):
    """Add a task to a project"""
    cursor.execute("""
        INSERT INTO tasks (project_id, title, description, status, priority, due_date, task_type, estimated_hours)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (project_id, title, description, status, priority, due_date, task_type, estimated_hours))

# Clear existing sample data
cursor.execute("DELETE FROM tasks")
cursor.execute("DELETE FROM projects")
cursor.execute("DELETE FROM expenses")

# =============================================================================
# WEEK 1: Platform Accounts & Content Setup
# =============================================================================

# YouTube Channel Project
yt_project = add_project(
    name="YouTube Channel",
    description="UnGouge Digest - Homeowner advocacy channel with data-driven content",
    category="content",
    priority="high",
    progress=20
)

add_task(yt_project, 
    "Create YouTube Channel",
    "Create 'UnGouge Digest' channel, configure branding, set up channel art",
    priority="high",
    due_date=(week_1_start + timedelta(days=1)).strftime("%Y-%m-%d"),
    estimated_hours=0.5
)

add_task(yt_project,
    "Set Up Channel Branding",
    "Upload logo, banner, write description, configure channel settings",
    priority="medium",
    due_date=(week_1_start + timedelta(days=1)).strftime("%Y-%m-%d"),
    estimated_hours=0.5
)

add_task(yt_project,
    "Connect YouTube Analytics to Dashboard",
    "Set up YouTube Data API v3, configure dashboard integration",
    priority="medium",
    due_date=(week_3_start + timedelta(days=3)).strftime("%Y-%m-%d"),
    estimated_hours=2
)

add_task(yt_project,
    "Record Episode 1 Voiceover",
    "Use ElevenLabs voice clone to record 'How Contractors Are Ripping You Off'",
    priority="high",
    due_date=(week_3_start).strftime("%Y-%m-%d"),
    estimated_hours=2
)

add_task(yt_project,
    "Edit & Upload Episode 1",
    "Edit video, add graphics, upload with optimized title/description/tags",
    priority="high",
    due_date=(week_3_start + timedelta(days=2)).strftime("%Y-%m-%d"),
    estimated_hours=3
)

# Content Organization Project
content_project = add_project(
    name="Content Library",
    description="Scripts, blog posts, and marketing materials ready for publication",
    category="content",
    priority="high",
    progress=60
)

add_task(content_project,
    "Organize YouTube Scripts in Dashboard",
    "Move 3 episode scripts to dashboard for easy access and production tracking",
    priority="medium",
    due_date=(week_1_start + timedelta(days=2)).strftime("%Y-%m-%d"),
    estimated_hours=1
)

add_task(content_project,
    "Create Content Calendar",
    "Set up upload schedule tracker in dashboard (weekly YouTube, 2-3 blog posts/month)",
    priority="medium",
    due_date=(week_1_start + timedelta(days=2)).strftime("%Y-%m-%d"),
    estimated_hours=1
)

add_task(content_project,
    "Publish First Blog Post",
    "Publish 'Why Free Contractor Quote Sites Are Expensive' with SEO optimization",
    priority="medium",
    due_date=(week_3_start + timedelta(days=4)).strftime("%Y-%m-%d"),
    estimated_hours=1
)

# Podcast Platforms Project
podcast_project = add_project(
    name="Podcast Distribution",
    description="Multi-platform podcast presence (Spotify, Apple Podcasts, YouTube)",
    category="content",
    priority="medium",
    progress=0
)

add_task(podcast_project,
    "Create Spotify for Podcasters Account",
    "Set up Spotify hosting (free) with RSS feed for distribution",
    priority="medium",
    due_date=(week_1_start + timedelta(days=3)).strftime("%Y-%m-%d"),
    estimated_hours=1
)

add_task(podcast_project,
    "Submit to Apple Podcasts",
    "Submit RSS feed to Apple Podcasts Connect",
    priority="medium",
    due_date=(week_1_start + timedelta(days=4)).strftime("%Y-%m-%d"),
    estimated_hours=0.5
)

add_task(podcast_project,
    "Configure YouTube as Podcast",
    "Enable podcast features on YouTube channel",
    priority="low",
    due_date=(week_2_start).strftime("%Y-%m-%d"),
    estimated_hours=0.5
)

# =============================================================================
# WEEK 2: Ungouge.ai Deployment
# =============================================================================

ungouge_project = add_project(
    name="Ungouge.ai Platform",
    description="Quote analysis web app - main revenue driver ($19.99/report)",
    category="product",
    priority="critical",
    progress=85
)

add_task(ungouge_project,
    "Review Codebase Status",
    "Audit current state of Next.js frontend + FastAPI backend, identify any gaps",
    priority="high",
    due_date=(week_2_start).strftime("%Y-%m-%d"),
    estimated_hours=2
)

add_task(ungouge_project,
    "Deploy Frontend to Vercel",
    "Deploy Next.js app with environment variables configured",
    priority="critical",
    due_date=(week_2_start + timedelta(days=2)).strftime("%Y-%m-%d"),
    estimated_hours=2
)

add_task(ungouge_project,
    "Deploy Backend to Cloud Run",
    "Deploy FastAPI backend with PostgreSQL, configure domain",
    priority="critical",
    due_date=(week_2_start + timedelta(days=2)).strftime("%Y-%m-%d"),
    estimated_hours=2
)

add_task(ungouge_project,
    "Set Up Stripe Payment Processing",
    "Create Stripe account, integrate payment flow, configure $19.99 pricing",
    priority="critical",
    due_date=(week_2_start + timedelta(days=3)).strftime("%Y-%m-%d"),
    estimated_hours=2
)

add_task(ungouge_project,
    "Configure Email Notifications",
    "Set up SendGrid/Gmail API for quote submission confirmations",
    priority="high",
    due_date=(week_2_start + timedelta(days=4)).strftime("%Y-%m-%d"),
    estimated_hours=1
)

add_task(ungouge_project,
    "End-to-End Testing",
    "Test full flow: submit quote → AI analysis → payment → email → PDF report",
    priority="critical",
    due_date=(week_2_start + timedelta(days=4)).strftime("%Y-%m-%d"),
    estimated_hours=2
)

add_task(ungouge_project,
    "Install Google Analytics 4",
    "Add GA4 tracking code to frontend, configure goals/conversions",
    priority="medium",
    due_date=(week_2_start + timedelta(days=3)).strftime("%Y-%m-%d"),
    estimated_hours=0.5
)

# =============================================================================
# WEEK 3: Launch & Integration
# =============================================================================

dashboard_project = add_project(
    name="Executive Dashboard",
    description="Business metrics command center - real-time tracking of all operations",
    category="operations",
    priority="high",
    progress=70
)

add_task(dashboard_project,
    "Connect YouTube Analytics API",
    "Integrate real subscriber count, views, watch time into dashboard",
    priority="high",
    due_date=(week_3_start + timedelta(days=3)).strftime("%Y-%m-%d"),
    estimated_hours=2
)

add_task(dashboard_project,
    "Connect Google Analytics API",
    "Pull website traffic, conversion rate into dashboard",
    priority="high",
    due_date=(week_3_start + timedelta(days=3)).strftime("%Y-%m-%d"),
    estimated_hours=2
)

add_task(dashboard_project,
    "Connect Stripe Revenue API",
    "Real-time revenue tracking, MRR calculations",
    priority="high",
    due_date=(week_3_start + timedelta(days=4)).strftime("%Y-%m-%d"),
    estimated_hours=1
)

add_task(dashboard_project,
    "Set Up Email Monitoring",
    "Monitor *@ungouge.ai inbox, alert on customer inquiries",
    priority="medium",
    due_date=(week_3_start + timedelta(days=4)).strftime("%Y-%m-%d"),
    estimated_hours=2
)

add_task(dashboard_project,
    "Add Real Expense Tracking",
    "Seed dashboard with current expenses, add entry form",
    priority="medium",
    due_date=(week_1_start + timedelta(days=5)).strftime("%Y-%m-%d"),
    estimated_hours=1
)

# =============================================================================
# Credentials & Prerequisites
# =============================================================================

ops_project = add_project(
    name="Business Operations",
    description="Accounts, credentials, and operational setup tasks",
    category="operations",
    priority="high",
    progress=30
)

add_task(ops_project,
    "Obtain Gemini API Key",
    "Get Google Gemini API key for AI quote analysis (required for ungouge.ai)",
    priority="critical",
    due_date=(week_2_start - timedelta(days=1)).strftime("%Y-%m-%d"),
    estimated_hours=0.5
)

add_task(ops_project,
    "Create Stripe Account",
    "Sign up for Stripe, complete verification, get API keys",
    priority="critical",
    due_date=(week_2_start).strftime("%Y-%m-%d"),
    estimated_hours=1
)

add_task(ops_project,
    "Set Up ElevenLabs Voice",
    "Verify ElevenLabs subscription active, test voice clone quality",
    priority="high",
    due_date=(week_2_start + timedelta(days=6)).strftime("%Y-%m-%d"),
    estimated_hours=0.5
)

# =============================================================================
# Add Current Expenses
# =============================================================================

cursor.execute("""
    INSERT INTO expenses (project_id, amount, description, category, date, recurring, vendor)
    VALUES 
        (?, 22.00, 'Voice cloning subscription', 'software', ?, 1, 'ElevenLabs'),
        (?, 5.00, 'Dashboard hosting (estimated)', 'hosting', ?, 1, 'Google Cloud Run'),
        (?, 0.10, 'Memory system (OpenAI + Gemini)', 'api', ?, 1, 'OpenAI/Google'),
        (NULL, 1.00, 'Domain registration (annual)', 'hosting', ?, 0, 'Google Domains')
""", (
    yt_project, today.strftime("%Y-%m-%d"),
    dashboard_project, today.strftime("%Y-%m-%d"),
    dashboard_project, today.strftime("%Y-%m-%d"),
    today.strftime("%Y-%m-%d")
))

# Commit all changes
conn.commit()
conn.close()

print("✅ Launch plan tasks added to dashboard!")
print(f"📊 Projects created: 6")
print(f"✅ Tasks added: 30+")
print(f"💰 Expenses tracked: 4")
print(f"\n🌐 View at: https://dashboard.ungouge.ai")
