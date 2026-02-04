"""
UnGouge Executive Dashboard - Database Schema
SQLite database with business metrics, projects, tasks, and expenses
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

# Use /tmp for Cloud Run ephemeral storage
DB_PATH = Path(os.environ.get('DATABASE_PATH', '/tmp/dashboard.db'))


def get_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database with schema"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Projects table (Quote Platform, YouTube Channel, etc.)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL DEFAULT 'active',
            progress INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            
            -- Project metadata
            category TEXT,
            priority TEXT DEFAULT 'medium',
            
            -- Financial tracking
            revenue_current REAL DEFAULT 0,
            revenue_goal REAL DEFAULT 0,
            
            -- Status indicators (for color-coding)
            health_score INTEGER DEFAULT 50,
            
            CONSTRAINT status_check CHECK (status IN ('active', 'paused', 'completed', 'archived')),
            CONSTRAINT priority_check CHECK (priority IN ('low', 'medium', 'high', 'critical'))
        )
    """)
    
    # Tasks table (next actions, milestones)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL DEFAULT 'todo',
            priority TEXT NOT NULL DEFAULT 'medium',
            due_date TEXT,
            completed_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            
            -- Task metadata
            task_type TEXT DEFAULT 'action',
            estimated_hours REAL,
            
            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
            CONSTRAINT status_check CHECK (status IN ('todo', 'in_progress', 'blocked', 'done', 'cancelled')),
            CONSTRAINT priority_check CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
            CONSTRAINT type_check CHECK (task_type IN ('action', 'milestone', 'blocker'))
        )
    """)
    
    # Expenses table (business expenses by project)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            amount REAL NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            recurring BOOLEAN DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            
            -- Expense metadata
            vendor TEXT,
            invoice_number TEXT,
            payment_method TEXT,
            
            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE SET NULL,
            CONSTRAINT category_check CHECK (category IN (
                'hosting', 'api', 'software', 'marketing', 'consulting', 
                'tools', 'design', 'legal', 'other'
            ))
        )
    """)
    
    # Milestones table (major project goals)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS milestones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            target_date TEXT NOT NULL,
            completed BOOLEAN DEFAULT 0,
            completed_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
        )
    """)
    
    # Revenue tracking table (for UnGouge business metrics)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS revenue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            source TEXT,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
        )
    """)
    
    # Metrics table (YouTube subs, email list, etc.)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            date TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
            UNIQUE(project_id, metric_name, date)
        )
    """)
    
    # Create indexes for performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_expenses_project ON expenses(project_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_milestones_project ON milestones(project_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_revenue_project ON revenue(project_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_project_name ON metrics(project_id, metric_name)")
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized: {DB_PATH}")


def seed_sample_data():
    """Insert real launch plan data for UnGouge business"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if already seeded
    cursor.execute("SELECT COUNT(*) FROM projects")
    if cursor.fetchone()[0] > 0:
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
            ('YouTube Channel', 'UnGouge Digest - Homeowner advocacy channel with data-driven content', 'active', 20, 'content', 'high', 70),
            ('Content Library', 'Scripts, blog posts, and marketing materials ready for publication', 'active', 60, 'content', 'high', 75),
            ('Podcast Distribution', 'Multi-platform podcast presence (Spotify, Apple Podcasts, YouTube)', 'active', 0, 'content', 'medium', 65),
            ('Ungouge.ai Platform', 'Quote analysis web app - main revenue driver ($19.99/report)', 'active', 85, 'product', 'critical', 90),
            ('Executive Dashboard', 'Business metrics command center - real-time tracking of all operations', 'active', 70, 'operations', 'high', 80),
            ('Business Operations', 'Accounts, credentials, and operational setup tasks', 'active', 30, 'operations', 'high', 70)
    """)
    
    # Get project IDs
    cursor.execute("SELECT id, name FROM projects ORDER BY id")
    projects = {row[1]: row[0] for row in cursor.fetchall()}
    
    yt = projects['YouTube Channel']
    content = projects['Content Library']
    podcast = projects['Podcast Distribution']
    ungouge = projects['Ungouge.ai Platform']
    dashboard = projects['Executive Dashboard']
    ops = projects['Business Operations']
    
    # YouTube Channel tasks
    cursor.execute("""
        INSERT INTO tasks (project_id, title, description, status, priority, due_date, task_type, estimated_hours)
        VALUES 
            (?, 'Create YouTube Channel', 'Create UnGouge Digest channel, configure branding, set up channel art', 'todo', 'high', ?, 'action', 0.5),
            (?, 'Set Up Channel Branding', 'Upload logo, banner, write description, configure channel settings', 'todo', 'medium', ?, 'action', 0.5),
            (?, 'Connect YouTube Analytics to Dashboard', 'Set up YouTube Data API v3, configure dashboard integration', 'todo', 'medium', ?, 'action', 2),
            (?, 'Record Episode 1 Voiceover', 'Use ElevenLabs voice clone to record How Contractors Are Ripping You Off', 'todo', 'high', ?, 'action', 2),
            (?, 'Edit & Upload Episode 1', 'Edit video, add graphics, upload with optimized title/description/tags', 'todo', 'high', ?, 'action', 3)
    """, (
        yt, (week_1 + timedelta(days=1)).strftime('%Y-%m-%d'),
        yt, (week_1 + timedelta(days=1)).strftime('%Y-%m-%d'),
        yt, (week_3 + timedelta(days=3)).strftime('%Y-%m-%d'),
        yt, week_3.strftime('%Y-%m-%d'),
        yt, (week_3 + timedelta(days=2)).strftime('%Y-%m-%d')
    ))
    
    # Content Library tasks
    cursor.execute("""
        INSERT INTO tasks (project_id, title, description, status, priority, due_date, task_type, estimated_hours)
        VALUES 
            (?, 'Organize YouTube Scripts in Dashboard', 'Move 3 episode scripts to dashboard for easy access and production tracking', 'todo', 'medium', ?, 'action', 1),
            (?, 'Create Content Calendar', 'Set up upload schedule tracker in dashboard (weekly YouTube, 2-3 blog posts/month)', 'todo', 'medium', ?, 'action', 1),
            (?, 'Publish First Blog Post', 'Publish Why Free Contractor Quote Sites Are Expensive with SEO optimization', 'todo', 'medium', ?, 'action', 1)
    """, (
        content, (week_1 + timedelta(days=2)).strftime('%Y-%m-%d'),
        content, (week_1 + timedelta(days=2)).strftime('%Y-%m-%d'),
        content, (week_3 + timedelta(days=4)).strftime('%Y-%m-%d')
    ))
    
    # Podcast tasks
    cursor.execute("""
        INSERT INTO tasks (project_id, title, description, status, priority, due_date, task_type, estimated_hours)
        VALUES 
            (?, 'Create Spotify for Podcasters Account', 'Set up Spotify hosting (free) with RSS feed for distribution', 'todo', 'medium', ?, 'action', 1),
            (?, 'Submit to Apple Podcasts', 'Submit RSS feed to Apple Podcasts Connect', 'todo', 'medium', ?, 'action', 0.5),
            (?, 'Configure YouTube as Podcast', 'Enable podcast features on YouTube channel', 'todo', 'low', ?, 'action', 0.5)
    """, (
        podcast, (week_1 + timedelta(days=3)).strftime('%Y-%m-%d'),
        podcast, (week_1 + timedelta(days=4)).strftime('%Y-%m-%d'),
        podcast, week_2.strftime('%Y-%m-%d')
    ))
    
    # Ungouge.ai tasks
    cursor.execute("""
        INSERT INTO tasks (project_id, title, description, status, priority, due_date, task_type, estimated_hours)
        VALUES 
            (?, 'Review Codebase Status', 'Audit current state of Next.js frontend + FastAPI backend, identify any gaps', 'todo', 'high', ?, 'action', 2),
            (?, 'Deploy Frontend to Vercel', 'Deploy Next.js app with environment variables configured', 'todo', 'urgent', ?, 'milestone', 2),
            (?, 'Deploy Backend to Cloud Run', 'Deploy FastAPI backend with PostgreSQL, configure domain', 'todo', 'urgent', ?, 'milestone', 2),
            (?, 'Set Up Stripe Payment Processing', 'Create Stripe account, integrate payment flow, configure $19.99 pricing', 'todo', 'urgent', ?, 'action', 2),
            (?, 'Configure Email Notifications', 'Set up SendGrid/Gmail API for quote submission confirmations', 'todo', 'high', ?, 'action', 1),
            (?, 'End-to-End Testing', 'Test full flow: submit quote → AI analysis → payment → email → PDF report', 'todo', 'urgent', ?, 'milestone', 2),
            (?, 'Install Google Analytics 4', 'Add GA4 tracking code to frontend, configure goals/conversions', 'todo', 'medium', ?, 'action', 0.5)
    """, (
        ungouge, week_2.strftime('%Y-%m-%d'),
        ungouge, (week_2 + timedelta(days=2)).strftime('%Y-%m-%d'),
        ungouge, (week_2 + timedelta(days=2)).strftime('%Y-%m-%d'),
        ungouge, (week_2 + timedelta(days=3)).strftime('%Y-%m-%d'),
        ungouge, (week_2 + timedelta(days=4)).strftime('%Y-%m-%d'),
        ungouge, (week_2 + timedelta(days=4)).strftime('%Y-%m-%d'),
        ungouge, (week_2 + timedelta(days=3)).strftime('%Y-%m-%d')
    ))
    
    # Dashboard tasks
    cursor.execute("""
        INSERT INTO tasks (project_id, title, description, status, priority, due_date, task_type, estimated_hours)
        VALUES 
            (?, 'Connect YouTube Analytics API', 'Integrate real subscriber count, views, watch time into dashboard', 'todo', 'high', ?, 'action', 2),
            (?, 'Connect Google Analytics API', 'Pull website traffic, conversion rate into dashboard', 'todo', 'high', ?, 'action', 2),
            (?, 'Connect Stripe Revenue API', 'Real-time revenue tracking, MRR calculations', 'todo', 'high', ?, 'action', 1),
            (?, 'Set Up Email Monitoring', 'Monitor *@ungouge.ai inbox, alert on customer inquiries', 'todo', 'medium', ?, 'action', 2),
            (?, 'Add Real Expense Tracking', 'Seed dashboard with current expenses, add entry form', 'todo', 'medium', ?, 'action', 1)
    """, (
        dashboard, (week_3 + timedelta(days=3)).strftime('%Y-%m-%d'),
        dashboard, (week_3 + timedelta(days=3)).strftime('%Y-%m-%d'),
        dashboard, (week_3 + timedelta(days=4)).strftime('%Y-%m-%d'),
        dashboard, (week_3 + timedelta(days=4)).strftime('%Y-%m-%d'),
        dashboard, (week_1 + timedelta(days=5)).strftime('%Y-%m-%d')
    ))
    
    # Operations tasks
    cursor.execute("""
        INSERT INTO tasks (project_id, title, description, status, priority, due_date, task_type, estimated_hours)
        VALUES 
            (?, 'Obtain Gemini API Key', 'Get Google Gemini API key for AI quote analysis (required for ungouge.ai)', 'todo', 'urgent', ?, 'action', 0.5),
            (?, 'Create Stripe Account', 'Sign up for Stripe, complete verification, get API keys', 'todo', 'urgent', ?, 'action', 1),
            (?, 'Set Up ElevenLabs Voice', 'Verify ElevenLabs subscription active, test voice clone quality', 'todo', 'high', ?, 'action', 0.5)
    """, (
        ops, (week_2 - timedelta(days=1)).strftime('%Y-%m-%d'),
        ops, week_2.strftime('%Y-%m-%d'),
        ops, (week_2 + timedelta(days=6)).strftime('%Y-%m-%d')
    ))
    
    # Insert current expenses
    today_str = today.strftime('%Y-%m-%d')
    cursor.execute("""
        INSERT INTO expenses (project_id, amount, description, category, date, vendor, recurring)
        VALUES 
            (?, 22.00, 'Voice cloning subscription', 'software', ?, 'ElevenLabs', 1),
            (?, 5.00, 'Dashboard hosting (estimated)', 'hosting', ?, 'Google Cloud Run', 1),
            (?, 0.10, 'Memory system (OpenAI + Gemini)', 'api', ?, 'OpenAI/Google', 1),
            (NULL, 1.00, 'Domain registration (annual)', 'hosting', ?, 'Google Domains', 0)
    """, (
        yt, today_str,
        dashboard, today_str,
        dashboard, today_str,
        today_str
    ))
    
    conn.commit()
    conn.close()
    
    print("✅ Launch plan tasks and projects inserted")


if __name__ == "__main__":
    print("Initializing UnGouge Executive Dashboard database...")
    init_db()
    seed_sample_data()
    print("\n✅ Database ready!")
    print(f"📍 Location: {DB_PATH}")
    print("\nSchema:")
    print("  • projects - Main business projects")
    print("  • tasks - Action items and next steps")
    print("  • expenses - Business costs by project")
    print("  • milestones - Major goals and deadlines")
    print("  • revenue - Income tracking")
    print("  • metrics - KPIs (YouTube, email, social)")
