"""
UnGouge Executive Dashboard - Database Schema
Cloud SQL (MySQL) database with business metrics, projects, tasks, and expenses
"""

import pymysql
import pymysql.cursors
import os
from datetime import datetime
from typing import Optional

# Cloud SQL connection config
DB_HOST = os.environ.get('DB_HOST', '')  # Empty = use Unix socket
DB_USER = os.environ.get('DB_USER', 'dashboard-user')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_NAME = os.environ.get('DB_NAME', 'dashboard')
DB_UNIX_SOCKET = os.environ.get('DB_UNIX_SOCKET', '/cloudsql/ungouge-dashboard:us-central1:ungouge-dashboard-db')


def get_connection():
    """Get database connection with DictCursor (replaces sqlite3.Row)"""
    connect_args = {
        'user': DB_USER,
        'password': DB_PASSWORD,
        'database': DB_NAME,
        'cursorclass': pymysql.cursors.DictCursor,
        'charset': 'utf8mb4',
        'autocommit': False,
    }

    # Use Unix socket for Cloud Run, TCP for local dev (via Cloud SQL Proxy)
    if DB_HOST:
        connect_args['host'] = DB_HOST
        port = int(os.environ.get('DB_PORT', '3306'))
        connect_args['port'] = port
    else:
        connect_args['unix_socket'] = DB_UNIX_SOCKET

    conn = pymysql.connect(**connect_args)
    return conn


def init_db():
    """Initialize database with schema"""
    conn = get_connection()
    cursor = conn.cursor()

    # Projects table (Quote Platform, YouTube Channel, etc.)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            status VARCHAR(20) NOT NULL DEFAULT 'active',
            progress INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

            -- Project metadata
            category VARCHAR(50),
            priority VARCHAR(20) DEFAULT 'medium',

            -- Financial tracking
            revenue_current DOUBLE DEFAULT 0,
            revenue_goal DOUBLE DEFAULT 0,

            -- Status indicators (for color-coding)
            health_score INT DEFAULT 50,

            -- Owner tracking (for account deletion)
            created_by VARCHAR(255)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # Tasks table (next actions, milestones)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            project_id INT NOT NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            status VARCHAR(20) NOT NULL DEFAULT 'todo',
            priority VARCHAR(20) NOT NULL DEFAULT 'medium',
            due_date VARCHAR(20),
            completed_at VARCHAR(30),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

            -- Task metadata
            task_type VARCHAR(20) DEFAULT 'action',
            estimated_hours DOUBLE,

            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
            INDEX idx_tasks_project (project_id),
            INDEX idx_tasks_status (status),
            INDEX idx_tasks_due_date (due_date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # Expenses table (business expenses by project)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            project_id INT,
            amount DOUBLE NOT NULL,
            description TEXT NOT NULL,
            category VARCHAR(30) NOT NULL,
            date VARCHAR(20) NOT NULL,
            recurring TINYINT(1) DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            -- Expense metadata
            vendor VARCHAR(255),
            invoice_number VARCHAR(100),
            payment_method VARCHAR(50),

            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE SET NULL,
            INDEX idx_expenses_project (project_id),
            INDEX idx_expenses_date (date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # Milestones table (major project goals)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS milestones (
            id INT AUTO_INCREMENT PRIMARY KEY,
            project_id INT NOT NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            target_date VARCHAR(20) NOT NULL,
            completed TINYINT(1) DEFAULT 0,
            completed_at VARCHAR(30),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
            INDEX idx_milestones_project (project_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # Revenue tracking table (for UnGouge business metrics)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS revenue (
            id INT AUTO_INCREMENT PRIMARY KEY,
            project_id INT NOT NULL,
            amount DOUBLE NOT NULL,
            date VARCHAR(20) NOT NULL,
            source VARCHAR(100),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
            INDEX idx_revenue_project (project_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # Metrics table (YouTube subs, email list, etc.)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INT AUTO_INCREMENT PRIMARY KEY,
            project_id INT NOT NULL,
            metric_name VARCHAR(100) NOT NULL,
            metric_value DOUBLE NOT NULL,
            date VARCHAR(20) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
            UNIQUE KEY uq_metrics_project_name_date (project_id, metric_name, date),
            INDEX idx_metrics_project_name (project_id, metric_name)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # Time clock table (employee time tracking)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS timeclock (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_email VARCHAR(255) NOT NULL,
            clock_in DATETIME NOT NULL,
            clock_out DATETIME,
            duration_minutes DOUBLE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            INDEX idx_timeclock_user (user_email),
            INDEX idx_timeclock_clock_in (clock_in)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # Sessions table (auth sessions — previously in auth.py)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token VARCHAR(255) PRIMARY KEY,
            email VARCHAR(255) NOT NULL,
            name VARCHAR(255),
            picture TEXT,
            created_at VARCHAR(30) NOT NULL,
            expires_at VARCHAR(30) NOT NULL,
            user_email VARCHAR(255),

            INDEX idx_sessions_email (email),
            INDEX idx_sessions_expires (expires_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    conn.commit()
    conn.close()

    print(f"✅ Database initialized (Cloud SQL: {DB_NAME})")


def seed_sample_data():
    """Insert real launch plan data for UnGouge business"""
    conn = get_connection()
    cursor = conn.cursor()

    # Check if already seeded
    cursor.execute("SELECT COUNT(*) AS cnt FROM projects")
    if cursor.fetchone()['cnt'] > 0:
        print("Database already has data, skipping seed")
        conn.close()
        return

    from datetime import timedelta
    today = datetime.now()
    week_1 = today
    week_2 = today + timedelta(weeks=1)
    week_3 = today + timedelta(weeks=2)

    # WEEK 1: Platform Accounts & Content Setup
    cursor.execute("""
        INSERT INTO projects (name, description, status, progress, category, priority, health_score)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s)
    """, (
        'YouTube Channel', 'UnGouge Digest - Homeowner advocacy channel with data-driven content', 'active', 20, 'youtube', 'high', 70,
        'Content Library', 'Scripts, blog posts, and marketing materials ready for publication', 'active', 60, 'youtube', 'high', 75,
        'Podcast Distribution', 'Multi-platform podcast presence (Spotify, Apple Podcasts, YouTube)', 'active', 0, 'youtube', 'medium', 65,
        'Ungouge.ai Platform', 'Quote analysis web app - main revenue driver ($19.99/report)', 'active', 85, 'ungouge', 'critical', 90,
        'Executive Dashboard', 'Business metrics command center - real-time tracking of all operations', 'active', 70, 'ungouge', 'high', 80,
        'Business Operations', 'Accounts, credentials, and operational setup tasks', 'active', 30, 'ungouge', 'high', 70,
        'Coming Soon Page', 'Landing page at ungouge.ai - LIVE on Cloudflare Pages, all domains connected', 'completed', 95, 'ungouge', 'high', 95,
        'UnGouge GPT Kit', 'Custom GPT for ChatGPT Store - system prompt + 4 knowledge files ready', 'active', 95, 'ungouge', 'medium', 90,
        'SEO & Blog Content', '23 blog posts covering home improvement costs - SEO keyword targeting', 'active', 90, 'ungouge', 'high', 90,
        'Disaster Response System', '3-agent automation (Sentinel/Strategist/Executor) for disaster pricing', 'active', 15, 'ungouge', 'medium', 60,
        'Data Partnerships', '1build.com API inquiry (68M data points) - waiting for response', 'active', 10, 'ungouge', 'medium', 50,
        'Social Media Presence', 'YouTube @ungouge, Instagram @ungouge.ai, TikTok @ungouge.ai, X @Ungouge', 'active', 40, 'social', 'medium', 65,
        'GPT to Web Funnel', 'ChatGPT custom GPT in-app experience funneling to ungouge.ai web app', 'active', 5, 'youtube', 'medium', 50,
        'Social Media Management', 'Managing all social media accounts - scheduling, engagement, analytics', 'active', 20, 'social', 'medium', 60,
        'Blog Distribution', 'Tracking blog posts across platforms - Website, Medium, LinkedIn', 'active', 10, 'social', 'medium', 55,
    ))

    # Get project IDs
    cursor.execute("SELECT id, name FROM projects ORDER BY id")
    projects = {row['name']: row['id'] for row in cursor.fetchall()}

    yt = projects['YouTube Channel']
    content = projects['Content Library']
    podcast = projects['Podcast Distribution']
    ungouge = projects['Ungouge.ai Platform']
    dashboard = projects['Executive Dashboard']
    ops = projects['Business Operations']
    coming_soon = projects.get('Coming Soon Page')
    gpt_kit = projects.get('UnGouge GPT Kit')
    seo_blog = projects.get('SEO & Blog Content')
    disaster = projects.get('Disaster Response System')
    data_partner = projects.get('Data Partnerships')
    social = projects.get('Social Media Presence')
    gpt_funnel = projects.get('GPT to Web Funnel')
    social_mgmt = projects.get('Social Media Management')
    blog_dist = projects.get('Blog Distribution')

    # YouTube Channel tasks
    cursor.execute("""
        INSERT INTO tasks (project_id, title, description, status, priority, due_date, task_type, estimated_hours)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        yt, 'Create YouTube Channel', 'Create UnGouge Digest channel, configure branding, set up channel art', 'todo', 'high', (week_1 + timedelta(days=1)).strftime('%Y-%m-%d'), 'action', 0.5,
        yt, 'Set Up Channel Branding', 'Upload logo, banner, write description, configure channel settings', 'todo', 'medium', (week_1 + timedelta(days=1)).strftime('%Y-%m-%d'), 'action', 0.5,
        yt, 'Connect YouTube Analytics to Dashboard', 'Set up YouTube Data API v3, configure dashboard integration', 'todo', 'medium', (week_3 + timedelta(days=3)).strftime('%Y-%m-%d'), 'action', 2,
        yt, 'Record Episode 1 Voiceover', 'Use ElevenLabs voice clone to record How Contractors Are Ripping You Off', 'todo', 'high', week_3.strftime('%Y-%m-%d'), 'action', 2,
        yt, 'Edit & Upload Episode 1', 'Edit video, add graphics, upload with optimized title/description/tags', 'todo', 'high', (week_3 + timedelta(days=2)).strftime('%Y-%m-%d'), 'action', 3,
    ))

    # Content Library tasks
    cursor.execute("""
        INSERT INTO tasks (project_id, title, description, status, priority, due_date, task_type, estimated_hours)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        content, 'Organize YouTube Scripts in Dashboard', 'Move 3 episode scripts to dashboard for easy access and production tracking', 'todo', 'medium', (week_1 + timedelta(days=2)).strftime('%Y-%m-%d'), 'action', 1,
        content, 'Create Content Calendar', 'Set up upload schedule tracker in dashboard (weekly YouTube, 2-3 blog posts/month)', 'todo', 'medium', (week_1 + timedelta(days=2)).strftime('%Y-%m-%d'), 'action', 1,
        content, 'Publish First Blog Post', 'Publish Why Free Contractor Quote Sites Are Expensive with SEO optimization', 'todo', 'medium', (week_3 + timedelta(days=4)).strftime('%Y-%m-%d'), 'action', 1,
    ))

    # Podcast tasks
    cursor.execute("""
        INSERT INTO tasks (project_id, title, description, status, priority, due_date, task_type, estimated_hours)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        podcast, 'Create Spotify for Podcasters Account', 'Set up Spotify hosting (free) with RSS feed for distribution', 'todo', 'medium', (week_1 + timedelta(days=3)).strftime('%Y-%m-%d'), 'action', 1,
        podcast, 'Submit to Apple Podcasts', 'Submit RSS feed to Apple Podcasts Connect', 'todo', 'medium', (week_1 + timedelta(days=4)).strftime('%Y-%m-%d'), 'action', 0.5,
        podcast, 'Configure YouTube as Podcast', 'Enable podcast features on YouTube channel', 'todo', 'low', week_2.strftime('%Y-%m-%d'), 'action', 0.5,
    ))

    # Ungouge.ai tasks
    cursor.execute("""
        INSERT INTO tasks (project_id, title, description, status, priority, due_date, task_type, estimated_hours)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        ungouge, 'Review Codebase Status', 'Audit current state of Next.js frontend + FastAPI backend, identify any gaps', 'todo', 'high', week_2.strftime('%Y-%m-%d'), 'action', 2,
        ungouge, 'Deploy Frontend to Vercel', 'Deploy Next.js app with environment variables configured', 'todo', 'urgent', (week_2 + timedelta(days=2)).strftime('%Y-%m-%d'), 'milestone', 2,
        ungouge, 'Deploy Backend to Cloud Run', 'Deploy FastAPI backend with PostgreSQL, configure domain', 'todo', 'urgent', (week_2 + timedelta(days=2)).strftime('%Y-%m-%d'), 'milestone', 2,
        ungouge, 'Set Up Stripe Payment Processing', 'Create Stripe account, integrate payment flow, configure $19.99 pricing', 'todo', 'urgent', (week_2 + timedelta(days=3)).strftime('%Y-%m-%d'), 'action', 2,
        ungouge, 'Configure Email Notifications', 'Set up SendGrid/Gmail API for quote submission confirmations', 'todo', 'high', (week_2 + timedelta(days=4)).strftime('%Y-%m-%d'), 'action', 1,
        ungouge, 'End-to-End Testing', 'Test full flow: submit quote → AI analysis → payment → email → PDF report', 'todo', 'urgent', (week_2 + timedelta(days=4)).strftime('%Y-%m-%d'), 'milestone', 2,
        ungouge, 'Install Google Analytics 4', 'Add GA4 tracking code to frontend, configure goals/conversions', 'todo', 'medium', (week_2 + timedelta(days=3)).strftime('%Y-%m-%d'), 'action', 0.5,
    ))

    # Dashboard tasks
    cursor.execute("""
        INSERT INTO tasks (project_id, title, description, status, priority, due_date, task_type, estimated_hours)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        dashboard, 'Connect YouTube Analytics API', 'Integrate real subscriber count, views, watch time into dashboard', 'todo', 'high', (week_3 + timedelta(days=3)).strftime('%Y-%m-%d'), 'action', 2,
        dashboard, 'Connect Google Analytics API', 'Pull website traffic, conversion rate into dashboard', 'todo', 'high', (week_3 + timedelta(days=3)).strftime('%Y-%m-%d'), 'action', 2,
        dashboard, 'Connect Stripe Revenue API', 'Real-time revenue tracking, MRR calculations', 'todo', 'high', (week_3 + timedelta(days=4)).strftime('%Y-%m-%d'), 'action', 1,
        dashboard, 'Set Up Email Monitoring', 'Monitor *@ungouge.ai inbox, alert on customer inquiries', 'todo', 'medium', (week_3 + timedelta(days=4)).strftime('%Y-%m-%d'), 'action', 2,
        dashboard, 'Add Real Expense Tracking', 'Seed dashboard with current expenses, add entry form', 'todo', 'medium', (week_1 + timedelta(days=5)).strftime('%Y-%m-%d'), 'action', 1,
    ))

    # Operations tasks
    cursor.execute("""
        INSERT INTO tasks (project_id, title, description, status, priority, due_date, task_type, estimated_hours)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        ops, 'Obtain Gemini API Key', 'Get Google Gemini API key for AI quote analysis (required for ungouge.ai)', 'todo', 'urgent', (week_2 - timedelta(days=1)).strftime('%Y-%m-%d'), 'action', 0.5,
        ops, 'Create Stripe Account', 'Sign up for Stripe, complete verification, get API keys', 'todo', 'urgent', week_2.strftime('%Y-%m-%d'), 'action', 1,
        ops, 'Set Up ElevenLabs Voice', 'Verify ElevenLabs subscription active, test voice clone quality', 'todo', 'high', (week_2 + timedelta(days=6)).strftime('%Y-%m-%d'), 'action', 0.5,
    ))

    # New project tasks (added Feb 9, 2026)
    if coming_soon:
        cursor.execute("""
            INSERT INTO tasks (project_id, title, description, status, priority, due_date, task_type, estimated_hours)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            coming_soon, 'Deploy coming soon page', 'Single-page HTML on Cloudflare Pages with email capture', 'done', 'high', today.strftime('%Y-%m-%d'), 'milestone', 2,
            coming_soon, 'Connect all domain variants', 'ungouge.com, ungoug.app, ungoug.com → Cloudflare Pages', 'done', 'medium', today.strftime('%Y-%m-%d'), 'action', 1,
            coming_soon, 'Add OG image for social previews', '1200x630 preview image for link sharing', 'done', 'medium', today.strftime('%Y-%m-%d'), 'action', 1,
            coming_soon, 'Add email signup form', 'Collect early interest emails before full launch', 'todo', 'high', week_2.strftime('%Y-%m-%d'), 'action', 2,
        ))

    if gpt_kit:
        cursor.execute("""
            INSERT INTO tasks (project_id, title, description, status, priority, due_date, task_type, estimated_hours)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            gpt_kit, 'Create system prompt', '~5.8KB system prompt for GPT Store listing', 'done', 'high', today.strftime('%Y-%m-%d'), 'action', 3,
            gpt_kit, 'Build knowledge files', '4 files (~28KB): pricing guidelines, red flags, negotiation tips', 'done', 'high', today.strftime('%Y-%m-%d'), 'action', 4,
            gpt_kit, 'Write GPT Store metadata', 'Name, description, conversation starters', 'done', 'medium', today.strftime('%Y-%m-%d'), 'action', 1,
            gpt_kit, 'Publish to GPT Store', 'Submit for review and publish when site launches', 'todo', 'high', week_2.strftime('%Y-%m-%d'), 'milestone', 1,
        ))

    if seo_blog:
        cursor.execute("""
            INSERT INTO tasks (project_id, title, description, status, priority, due_date, task_type, estimated_hours)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            seo_blog, 'Write 23 blog posts', 'Covering major home improvement categories with cost breakdowns', 'done', 'high', today.strftime('%Y-%m-%d'), 'action', 30,
            seo_blog, 'SEO keyword research', 'Target low-difficulty, high-volume keywords per category', 'done', 'high', today.strftime('%Y-%m-%d'), 'action', 3,
            seo_blog, 'Create regional guides', 'Central Vermont specific pricing for bathroom, roof, kitchen', 'done', 'medium', today.strftime('%Y-%m-%d'), 'action', 6,
            seo_blog, 'Deploy blog to website', 'Integrate blog posts into Next.js app with proper routing', 'todo', 'high', week_2.strftime('%Y-%m-%d'), 'milestone', 4,
            seo_blog, 'Write fence cost guide', 'Comprehensive fence installation cost breakdown', 'done', 'medium', today.strftime('%Y-%m-%d'), 'action', 2,
            seo_blog, 'Write flooring cost guide', 'Comprehensive flooring installation cost breakdown', 'done', 'medium', today.strftime('%Y-%m-%d'), 'action', 2,
            seo_blog, 'Write siding cost guide', 'Vinyl, fiber cement, wood, metal - 5,500 words', 'done', 'medium', today.strftime('%Y-%m-%d'), 'action', 2,
            seo_blog, 'Write electrical work guide', 'Panel upgrades, outlets, EV chargers - 5,000 words', 'done', 'medium', today.strftime('%Y-%m-%d'), 'action', 2,
        ))

    if disaster:
        cursor.execute("""
            INSERT INTO tasks (project_id, title, description, status, priority, due_date, task_type, estimated_hours)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            disaster, 'Design 3-agent architecture', 'Sentinel (detect) → Strategist (plan) → Executor (deploy)', 'done', 'high', today.strftime('%Y-%m-%d'), 'milestone', 8,
            disaster, 'Build Sentinel agent', 'NOAA/FEMA/News monitoring with daily cron', 'todo', 'medium', week_3.strftime('%Y-%m-%d'), 'action', 6,
            disaster, 'Build Strategist agent', 'Generate response packages (press, social, pricing)', 'todo', 'medium', (week_3 + timedelta(days=3)).strftime('%Y-%m-%d'), 'action', 6,
            disaster, 'Build Executor agent', 'One-click activation after human approval', 'todo', 'medium', (week_3 + timedelta(days=5)).strftime('%Y-%m-%d'), 'action', 4,
            disaster, 'Build dashboard monitoring panel', 'Active disasters, pricing zones, impact metrics', 'todo', 'low', (week_3 + timedelta(days=7)).strftime('%Y-%m-%d'), 'action', 4,
        ))

    if data_partner:
        cursor.execute("""
            INSERT INTO tasks (project_id, title, description, status, priority, due_date, task_type, estimated_hours)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data_partner, 'Research 1build.com API', '68M data points, 3000+ US counties, GraphQL API', 'done', 'high', today.strftime('%Y-%m-%d'), 'action', 2,
            data_partner, 'Send API inquiry email', 'Request pricing and partnership info', 'done', 'high', today.strftime('%Y-%m-%d'), 'action', 0.5,
            data_partner, 'Evaluate API response', 'Compare pricing vs Craftsman data, assess integration effort', 'todo', 'high', week_2.strftime('%Y-%m-%d'), 'action', 2,
            data_partner, 'Build API integration', 'GraphQL client for real-time county-level pricing', 'todo', 'medium', week_3.strftime('%Y-%m-%d'), 'action', 8,
        ))

    if social:
        cursor.execute("""
            INSERT INTO tasks (project_id, title, description, status, priority, due_date, task_type, estimated_hours)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            social, 'Secure @Ungouge on X/Twitter', 'Handle secured for brand consistency', 'done', 'high', today.strftime('%Y-%m-%d'), 'action', 0.5,
            social, 'Create Instagram @ungouge.ai', 'Set up business profile with brand assets', 'done', 'medium', today.strftime('%Y-%m-%d'), 'action', 0.5,
            social, 'Create TikTok @ungouge.ai', 'Set up creator account', 'done', 'medium', today.strftime('%Y-%m-%d'), 'action', 0.5,
            social, 'Create YouTube @ungouge', 'Channel created and configured', 'done', 'high', today.strftime('%Y-%m-%d'), 'action', 1,
            social, 'Post first YouTube video', 'Record, edit, upload Episode 1', 'todo', 'high', week_3.strftime('%Y-%m-%d'), 'milestone', 6,
        ))

    if gpt_funnel:
        cursor.execute("""
            INSERT INTO tasks (project_id, title, description, status, priority, due_date, task_type, estimated_hours)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            gpt_funnel, 'Design GPT in-app experience', 'Create conversational flow for quote analysis within ChatGPT', 'todo', 'medium', (week_2 + timedelta(days=2)).strftime('%Y-%m-%d'), 'action', 3,
            gpt_funnel, 'Add web app funnel CTA', 'Prompt users to visit ungouge.ai for full report after GPT preview', 'todo', 'medium', (week_2 + timedelta(days=3)).strftime('%Y-%m-%d'), 'action', 2,
            gpt_funnel, 'Track GPT to web conversion', 'Add analytics to measure how many GPT users convert to web app', 'todo', 'low', week_3.strftime('%Y-%m-%d'), 'action', 2,
            gpt_funnel, 'Test GPT quote preview', 'Ensure GPT can provide useful preview without full paid report', 'todo', 'medium', (week_2 + timedelta(days=4)).strftime('%Y-%m-%d'), 'action', 1,
        ))

    if social_mgmt:
        cursor.execute("""
            INSERT INTO tasks (project_id, title, description, status, priority, due_date, task_type, estimated_hours)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            social_mgmt, 'Create content calendar', 'Plan weekly posting schedule across all platforms', 'todo', 'high', week_2.strftime('%Y-%m-%d'), 'action', 2,
            social_mgmt, 'Set up scheduling tool', 'Evaluate and configure Buffer/Later for multi-platform posting', 'todo', 'medium', week_2.strftime('%Y-%m-%d'), 'action', 1,
            social_mgmt, 'Design brand templates', 'Create consistent visual templates for Instagram/TikTok/X posts', 'todo', 'medium', week_3.strftime('%Y-%m-%d'), 'action', 3,
            social_mgmt, 'First cross-platform post', 'Publish coordinated launch content across all social accounts', 'todo', 'high', week_3.strftime('%Y-%m-%d'), 'milestone', 2,
        ))

    if blog_dist:
        cursor.execute("""
            INSERT INTO tasks (project_id, title, description, status, priority, due_date, task_type, estimated_hours)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            blog_dist, 'Set up Medium publication', 'Create UnGouge publication on Medium for blog syndication', 'todo', 'medium', week_2.strftime('%Y-%m-%d'), 'action', 1,
            blog_dist, 'Create LinkedIn company page', 'Set up UnGouge LinkedIn page for blog cross-posting', 'todo', 'medium', week_2.strftime('%Y-%m-%d'), 'action', 1,
            blog_dist, 'Publish first 5 blogs to website', 'Deploy top-priority blog posts to ungouge.ai/blog', 'todo', 'high', week_3.strftime('%Y-%m-%d'), 'milestone', 4,
            blog_dist, 'Cross-post to Medium and LinkedIn', 'Syndicate published blogs to Medium and LinkedIn', 'todo', 'medium', (week_3 + timedelta(days=2)).strftime('%Y-%m-%d'), 'action', 2,
        ))

    # Insert all expenses (deduplicated, normalized categories)
    today_str = today.strftime('%Y-%m-%d')
    cursor.execute("""
        INSERT INTO expenses (project_id, amount, description, category, date, vendor, recurring)
        VALUES
            (NULL, %s, %s, %s, %s, %s, %s),
            (NULL, %s, %s, %s, %s, %s, %s),
            (NULL, %s, %s, %s, %s, %s, %s),
            (NULL, %s, %s, %s, %s, %s, %s),
            (NULL, %s, %s, %s, %s, %s, %s),
            (NULL, %s, %s, %s, %s, %s, %s),
            (NULL, %s, %s, %s, %s, %s, %s),
            (NULL, %s, %s, %s, %s, %s, %s),
            (NULL, %s, %s, %s, %s, %s, %s),
            (NULL, %s, %s, %s, %s, %s, %s)
    """, (
        125.00, 'Claude Max 5x', 'tools_subscriptions', today_str, 'Anthropic', 1,
        20.00, 'ChatGPT Plus', 'tools_subscriptions', today_str, 'OpenAI', 1,
        20.00, 'Gemini Pro', 'tools_subscriptions', today_str, 'Google', 1,
        22.00, 'ElevenLabs Creator', 'tools_subscriptions', today_str, 'ElevenLabs', 1,
        5.00, 'Google Cloud Run (App)', 'infrastructure', today_str, 'Google Cloud', 1,
        5.00, 'Google Cloud Run (Dashboard)', 'infrastructure', today_str, 'Google Cloud', 1,
        0.10, 'Memory System (OpenAI + Gemini)', 'tools_subscriptions', today_str, 'OpenAI/Google', 1,
        0.00, 'Cloudflare (Free Plan)', 'infrastructure', today_str, 'Cloudflare', 1,
        0.00, 'OpenClaw (Self-hosted)', 'tools_subscriptions', today_str, 'OpenClaw', 1,
        1.00, 'Domain Registration (annual)', 'infrastructure', today_str, 'Google Domains', 0,
    ))

    conn.commit()
    conn.close()

    print("✅ Launch plan tasks and projects inserted")


if __name__ == "__main__":
    print("Initializing UnGouge Executive Dashboard database...")
    init_db()
    seed_sample_data()
    print("\n✅ Database ready!")
    print(f"📍 Cloud SQL: {DB_NAME}")
    print("\nSchema:")
    print("  • projects - Main business projects")
    print("  • tasks - Action items and next steps")
    print("  • expenses - Business costs by project")
    print("  • milestones - Major goals and deadlines")
    print("  • revenue - Income tracking")
    print("  • metrics - KPIs (YouTube, email, social)")
    print("  • sessions - Auth sessions")
    print("  • timeclock - Time tracking")
