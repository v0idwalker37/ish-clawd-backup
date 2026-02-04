"""
UnGouge Executive Dashboard - FastAPI Backend
RESTful API for business metrics, projects, tasks, and expenses
"""

from fastapi import FastAPI, HTTPException, Cookie, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import sqlite3
import os

from database import get_connection, init_db
from auth import (
    verify_google_token, 
    create_session, 
    verify_session, 
    delete_session,
    cleanup_expired_sessions
)

# Initialize FastAPI app
app = FastAPI(
    title="UnGouge Executive Dashboard API",
    description="Business metrics and project management API",
    version="1.0.0"
)

# CORS middleware (allow frontend to access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Pydantic models for request/response
class Project(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    status: str = "active"
    progress: int = 0
    category: Optional[str] = None
    priority: str = "medium"
    revenue_current: float = 0
    revenue_goal: float = 0
    health_score: int = 50


class Task(BaseModel):
    id: Optional[int] = None
    project_id: int
    title: str
    description: Optional[str] = None
    status: str = "todo"
    priority: str = "medium"
    due_date: Optional[str] = None
    task_type: str = "action"
    estimated_hours: Optional[float] = None


class Expense(BaseModel):
    id: Optional[int] = None
    project_id: Optional[int] = None
    amount: float
    description: str
    category: str
    date: str
    vendor: Optional[str] = None
    recurring: bool = False


class Milestone(BaseModel):
    id: Optional[int] = None
    project_id: int
    title: str
    description: Optional[str] = None
    target_date: str
    completed: bool = False


# Session verification dependency
async def require_auth(session_token: Optional[str] = Cookie(None, alias="session_token")):
    """
    Dependency for protected routes - verifies session token
    Raises 401 if not authenticated
    """
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_info = verify_session(session_token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    return user_info


# Initialize database on startup
@app.on_event("startup")
async def startup():
    try:
        init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization warning: {e}")


# Periodic cleanup task
@app.on_event("startup")
async def start_cleanup_task():
    """Run session cleanup periodically"""
    import asyncio
    
    async def cleanup_loop():
        while True:
            await asyncio.sleep(3600)  # Every hour
            cleanup_expired_sessions()
    
    asyncio.create_task(cleanup_loop())


# Serve login or dashboard based on auth status
@app.get("/")
def read_root(session_token: Optional[str] = Cookie(None, alias="session_token")):
    """Root route - serve login page or dashboard based on auth"""
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    
    # Debug logging
    print(f"🔍 Root request - Cookie present: {session_token is not None}")
    
    # Check if authenticated
    if session_token:
        user_info = verify_session(session_token)
        if user_info:
            print(f"✅ Authenticated user: {user_info.get('email')}")
            # Serve dashboard
            dashboard_path = os.path.join(static_dir, "dashboard.html")
            if os.path.exists(dashboard_path):
                return FileResponse(dashboard_path)
            # Fallback to index.html if dashboard.html doesn't exist
            index_path = os.path.join(static_dir, "index.html")
            if os.path.exists(index_path):
                return FileResponse(index_path)
        else:
            print(f"❌ Invalid or expired session token")
    else:
        print(f"❌ No session cookie present")
    
    # Not authenticated - serve login page
    login_path = os.path.join(static_dir, "login.html")
    if os.path.exists(login_path):
        return FileResponse(login_path)
    
    # Fallback response if no static files exist
    return {
        "status": "healthy",
        "service": "UnGouge Executive Dashboard API",
        "version": "1.0.0",
        "message": "Please authenticate"
    }


# API Health check (public endpoint, no auth required)
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "UnGouge Executive Dashboard API",
        "version": "1.0.0"
    }


# ===== AUTHENTICATION ENDPOINTS =====

@app.post("/auth/verify")
async def auth_verify(response: Response, token: dict):
    """
    Verify Google ID token and create session
    Called by frontend after Google Sign-In
    
    Request body: {"credential": "google_id_token"}
    """
    google_token = token.get("credential")
    if not google_token:
        raise HTTPException(status_code=400, detail="Missing credential")
    
    # Verify token with Google
    user_info = verify_google_token(google_token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Create session
    session_token = create_session(user_info)
    
    # Set secure cookie (not httpOnly due to OAuth popup issues)
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=False,  # Can't use httpOnly with OAuth popups + SameSite=none
        secure=True,  # HTTPS only
        samesite="none",  # Required for OAuth popup/iframe flow
        max_age=86400,  # 24 hours
        path="/"
    )
    
    return {
        "success": True,
        "user": {
            "email": user_info["email"],
            "name": user_info["name"]
        }
    }


@app.get("/auth/status")
async def auth_status(user_info: dict = Depends(require_auth)):
    """
    Check authentication status
    Returns user info if authenticated, 401 if not
    """
    return {
        "authenticated": True,
        "user": {
            "email": user_info["email"],
            "name": user_info["name"]
        }
    }


@app.post("/auth/logout")
async def auth_logout(
    response: Response,
    session_token: Optional[str] = Cookie(None, alias="session_token")
):
    """
    Logout - invalidate session and clear cookie
    """
    if session_token:
        delete_session(session_token)
    
    # Clear cookie
    response.delete_cookie(key="session_token")
    
    return {"success": True, "message": "Logged out"}


# ===== PROJECTS =====

@app.get("/projects")
def get_projects(user_info: dict = Depends(require_auth)):
    """Get all projects"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, description, status, progress, category, priority,
               revenue_current, revenue_goal, health_score, created_at, updated_at
        FROM projects 
        WHERE status != 'archived'
        ORDER BY priority DESC, name
    """)
    projects = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"projects": projects}


@app.get("/projects/{project_id}")
def get_project(project_id: int, user_info: dict = Depends(require_auth)):
    """Get single project with details"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get project
    cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    project = cursor.fetchone()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get project tasks
    cursor.execute("""
        SELECT * FROM tasks 
        WHERE project_id = ? AND status != 'cancelled'
        ORDER BY priority DESC, due_date
    """, (project_id,))
    tasks = [dict(row) for row in cursor.fetchall()]
    
    # Get project expenses
    cursor.execute("""
        SELECT * FROM expenses 
        WHERE project_id = ?
        ORDER BY date DESC
        LIMIT 10
    """, (project_id,))
    expenses = [dict(row) for row in cursor.fetchall()]
    
    # Get project milestones
    cursor.execute("""
        SELECT * FROM milestones 
        WHERE project_id = ?
        ORDER BY target_date
    """, (project_id,))
    milestones = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "project": dict(project),
        "tasks": tasks,
        "expenses": expenses,
        "milestones": milestones
    }


@app.post("/projects")
def create_project(project: Project, user_info: dict = Depends(require_auth)):
    """Create new project"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO projects (name, description, status, progress, category, priority, revenue_current, revenue_goal, health_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        project.name, project.description, project.status, project.progress,
        project.category, project.priority, project.revenue_current,
        project.revenue_goal, project.health_score
    ))
    project_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"id": project_id, "message": "Project created"}


@app.put("/projects/{project_id}")
def update_project(project_id: int, project: Project, user_info: dict = Depends(require_auth)):
    """Update project"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE projects 
        SET name=?, description=?, status=?, progress=?, category=?, priority=?,
            revenue_current=?, revenue_goal=?, health_score=?, updated_at=CURRENT_TIMESTAMP
        WHERE id=?
    """, (
        project.name, project.description, project.status, project.progress,
        project.category, project.priority, project.revenue_current,
        project.revenue_goal, project.health_score, project_id
    ))
    conn.commit()
    conn.close()
    return {"message": "Project updated"}


# ===== TASKS =====

@app.get("/tasks")
def get_tasks(project_id: Optional[int] = None, status: Optional[str] = None, user_info: dict = Depends(require_auth)):
    """Get tasks with optional filters"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM tasks WHERE 1=1"
    params = []
    
    if project_id:
        query += " AND project_id = ?"
        params.append(project_id)
    if status:
        query += " AND status = ?"
        params.append(status)
    
    query += " ORDER BY priority DESC, due_date"
    
    cursor.execute(query, params)
    tasks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"tasks": tasks}


@app.post("/tasks")
def create_task(task: Task, user_info: dict = Depends(require_auth)):
    """Create new task"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (project_id, title, description, status, priority, due_date, task_type, estimated_hours)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        task.project_id, task.title, task.description, task.status,
        task.priority, task.due_date, task.task_type, task.estimated_hours
    ))
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"id": task_id, "message": "Task created"}


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: Task, user_info: dict = Depends(require_auth)):
    """Update task"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tasks 
        SET title=?, description=?, status=?, priority=?, due_date=?, task_type=?, estimated_hours=?, updated_at=CURRENT_TIMESTAMP
        WHERE id=?
    """, (
        task.title, task.description, task.status, task.priority,
        task.due_date, task.task_type, task.estimated_hours, task_id
    ))
    conn.commit()
    conn.close()
    return {"message": "Task updated"}


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, user_info: dict = Depends(require_auth)):
    """Delete task"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    return {"message": "Task deleted"}


# ===== EXPENSES =====

@app.get("/expenses")
def get_expenses(project_id: Optional[int] = None, user_info: dict = Depends(require_auth)):
    """Get expenses with optional project filter"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if project_id:
        cursor.execute("""
            SELECT * FROM expenses 
            WHERE project_id = ?
            ORDER BY date DESC
        """, (project_id,))
    else:
        cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
    
    expenses = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"expenses": expenses}


@app.post("/expenses")
def create_expense(expense: Expense, user_info: dict = Depends(require_auth)):
    """Create new expense"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO expenses (project_id, amount, description, category, date, vendor, recurring)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        expense.project_id, expense.amount, expense.description,
        expense.category, expense.date, expense.vendor, expense.recurring
    ))
    expense_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"id": expense_id, "message": "Expense logged"}


# ===== DASHBOARD SUMMARY =====

@app.get("/dashboard/summary")
def get_dashboard_summary(user_info: dict = Depends(require_auth)):
    """Get high-level dashboard overview"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Project counts by status
    cursor.execute("""
        SELECT status, COUNT(*) as count 
        FROM projects 
        GROUP BY status
    """)
    project_stats = {row["status"]: row["count"] for row in cursor.fetchall()}
    
    # Task counts by status
    cursor.execute("""
        SELECT status, COUNT(*) as count 
        FROM tasks 
        WHERE status != 'cancelled'
        GROUP BY status
    """)
    task_stats = {row["status"]: row["count"] for row in cursor.fetchall()}
    
    # Total expenses this month
    cursor.execute("""
        SELECT SUM(amount) as total 
        FROM expenses 
        WHERE date >= date('now', 'start of month')
    """)
    monthly_expenses = cursor.fetchone()["total"] or 0
    
    # Total revenue this quarter
    cursor.execute("""
        SELECT SUM(amount) as total 
        FROM revenue 
        WHERE date >= date('now', 'start of month', '-2 months')
    """)
    quarterly_revenue = cursor.fetchone()["total"] or 0
    
    # Overdue tasks
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM tasks 
        WHERE due_date < date('now') AND status NOT IN ('done', 'cancelled')
    """)
    overdue_tasks = cursor.fetchone()["count"]
    
    conn.close()
    
    return {
        "projects": project_stats,
        "tasks": task_stats,
        "monthly_expenses": monthly_expenses,
        "quarterly_revenue": quarterly_revenue,
        "overdue_tasks": overdue_tasks
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting UnGouge Dashboard API on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
