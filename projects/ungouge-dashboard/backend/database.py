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
    """Insert sample data for UnGouge business"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if already seeded
    cursor.execute("SELECT COUNT(*) FROM projects")
    if cursor.fetchone()[0] > 0:
        print("Database already has data, skipping seed")
        conn.close()
        return
    
    # Insert UnGouge projects
    cursor.execute("""
        INSERT INTO projects (name, description, status, progress, category, priority, revenue_current, revenue_goal, health_score)
        VALUES 
            ('Quote Analysis Platform', 'UnGouge.ai core product - contractor quote verification', 'active', 78, 'product', 'critical', 3891, 5000, 87),
            ('YouTube Channel', 'UnGouge Digest - homeowner advocacy content', 'active', 60, 'marketing', 'high', 0, 1000, 72)
    """)
    
    project_ids = {
        'platform': cursor.lastrowid - 1,
        'youtube': cursor.lastrowid
    }
    
    # Insert tasks
    cursor.execute("""
        INSERT INTO tasks (project_id, title, status, priority, due_date, task_type, description)
        VALUES 
            (?, 'Blog post #3 - Draft by EOD', 'in_progress', 'high', '2026-02-03', 'action', 'Complete third blog post for content marketing'),
            (?, 'YouTube video rendering', 'in_progress', 'medium', '2026-02-04', 'action', 'Currently 87% complete'),
            (?, 'Cost model v2 - Add 5 project types', 'todo', 'medium', '2026-02-15', 'milestone', 'Expand from 14 to 20 project types'),
            (?, 'Record voice samples', 'todo', 'high', '2026-02-10', 'action', 'Voice recording for ElevenLabs clone'),
            (?, 'Episode 1-3 upload', 'todo', 'urgent', '2026-02-12', 'milestone', 'Launch YouTube channel')
    """, (
        project_ids['platform'], project_ids['platform'], project_ids['platform'],
        project_ids['youtube'], project_ids['youtube']
    ))
    
    # Insert expenses
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute("""
        INSERT INTO expenses (project_id, amount, description, category, date, vendor, recurring)
        VALUES 
            (?, 47.23, 'Google Cloud hosting', 'hosting', ?, 'Google Cloud', 1),
            (?, 22.00, 'ElevenLabs Pro subscription', 'software', ?, 'ElevenLabs', 1),
            (?, 0.12, 'Gemini API usage', 'api', ?, 'Google', 0)
    """, (
        project_ids['platform'], today,
        project_ids['youtube'], today,
        project_ids['platform'], today
    ))
    
    # Insert milestones
    cursor.execute("""
        INSERT INTO milestones (project_id, title, target_date, description)
        VALUES 
            (?, 'YouTube Channel Launch', '2026-02-12', '3 episodes published, channel live'),
            (?, 'Q1 Revenue Goal', '2026-03-31', 'Reach $5,000 in quote analysis revenue'),
            (?, 'Cost Model v2', '2026-02-15', 'Expand to 20 project types')
    """, (
        project_ids['youtube'],
        project_ids['platform'],
        project_ids['platform']
    ))
    
    # Insert revenue tracking
    cursor.execute("""
        INSERT INTO revenue (project_id, amount, date, source, description)
        VALUES 
            (?, 247, '2026-02-02', 'quote_reports', '12 reports sold'),
            (?, 398, '2026-02-01', 'quote_reports', '20 reports sold')
    """, (project_ids['platform'], project_ids['platform']))
    
    # Insert metrics
    cursor.execute("""
        INSERT INTO metrics (project_id, metric_name, metric_value, date)
        VALUES 
            (?, 'youtube_subscribers', 1247, ?),
            (?, 'email_subscribers', 423, ?),
            (?, 'reddit_karma', 2891, ?),
            (?, 'twitter_followers', 892, ?)
    """, (
        project_ids['youtube'], today,
        project_ids['platform'], today,
        project_ids['platform'], today,
        project_ids['youtube'], today
    ))
    
    conn.commit()
    conn.close()
    
    print("✅ Sample data inserted")


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
