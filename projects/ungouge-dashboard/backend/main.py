"""
UnGouge Executive Dashboard - FastAPI Backend
Server-side OAuth 2.0 redirect flow (no popups!)
"""

from fastapi import FastAPI, HTTPException, Cookie, Response, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import sqlite3
import os
import secrets

from database import get_connection, init_db
from api_integrations import initialize_apis, get_all_external_metrics
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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event - initialize database
@app.on_event("startup")
def startup_event():
    """Initialize database on startup"""
    print("🚀 Initializing database...")
    init_db()
    
    print("🔌 Initializing API integrations...")
    initialize_apis()
    print("✅ API integrations ready")
    print("✅ Database initialized")
    
    # Seed with launch plan data if empty
    from database import seed_sample_data
    seed_sample_data()
    print("✅ Launch plan data seeded")

# Static files
static_dir = os.path.join(os.path.dirname(__file__), "static")

# Google OAuth 2.0 configuration
GOOGLE_CLIENT_ID = "1093157467231-3pgo81mrq5rjdvhvaa1uf81pk2ifhka2.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")  # Set via env
REDIRECT_URI = "https://dashboard.ungouge.ai/auth/callback"

# Pydantic models
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


# Session verification dependency
async def require_auth(session_token: Optional[str] = Cookie(None, alias="session_token")):
    """Verify session token from cookie"""
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_info = verify_session(session_token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    return user_info


@app.get("/")
def read_root(
    request: Request,
    response: Response,
    auth_token: Optional[str] = None,
    session_token: Optional[str] = Cookie(None, alias="session_token")
):
    """Root route - serve login page or dashboard based on auth"""
    static_dir_path = os.path.join(os.path.dirname(__file__), "static")
    
    # If auth_token in URL (from OAuth callback), validate and set cookie
    if auth_token:
        print(f"🔍 Received auth_token in URL")
        user_info = verify_session(auth_token)
        if user_info:
            print(f"✅ Valid auth token for {user_info.get('email')}, serving dashboard")
            # Set cookie and serve dashboard DIRECTLY (no redirect - avoids cookie timing issue)
            dashboard_path = os.path.join(static_dir_path, "dashboard-v2.html")
            if os.path.exists(dashboard_path):
                dashboard_response = FileResponse(dashboard_path)
                dashboard_response.set_cookie(
                    key="session_token",
                    value=auth_token,
                    httponly=True,
                    secure=True,
                    samesite="lax",
                    max_age=86400,  # 24 hours
                    path="/"
                )
                return dashboard_response
        else:
            print(f"❌ Invalid auth token")
    
    # Debug: print all cookies
    print(f"🔍 All cookies: {request.cookies}")
    print(f"🔍 Session token from Cookie param: {session_token}")
    
    # Check if authenticated via cookie
    if session_token:
        user_info = verify_session(session_token)
        if user_info:
            print(f"✅ Authenticated user: {user_info.get('email')}")
            dashboard_path = os.path.join(static_dir_path, "dashboard-v2.html")
            if os.path.exists(dashboard_path):
                return FileResponse(dashboard_path)
        else:
            print(f"❌ Invalid or expired session token: {session_token[:20]}...")
    else:
        print(f"❌ No session cookie present")
    
    # Not authenticated - serve login page
    login_path = os.path.join(static_dir_path, "login.html")
    if os.path.exists(login_path):
        return FileResponse(login_path)
    
    return {"status": "healthy", "message": "Please authenticate"}


@app.get("/auth/login")
def auth_login():
    """
    Step 1: Redirect user to Google OAuth consent page
    Server-side redirect flow (no popup!)
    """
    # Generate random state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Build Google OAuth URL
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": REDIRECT_URI,
        "state": state,
        "access_type": "offline",
        "prompt": "select_account"
    }
    
    # Build query string
    query = "&".join([f"{k}={v}" for k, v in params.items()])
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{query}"
    
    # Redirect to Google
    response = RedirectResponse(url=auth_url)
    # Store state in cookie for verification
    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        secure=True,
        max_age=600,  # 10 minutes
        samesite="lax"
    )
    return response


@app.get("/auth/callback")
async def auth_callback(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    oauth_state: Optional[str] = Cookie(None)
):
    """
    Step 2: Handle OAuth callback from Google
    Exchange authorization code for tokens
    """
    if error:
        return RedirectResponse(url=f"/?error={error}")
    
    if not code:
        return RedirectResponse(url="/?error=no_code")
    
    # Verify state (CSRF protection)
    if not state or not oauth_state or state != oauth_state:
        return RedirectResponse(url="/?error=state_mismatch")
    
    # Exchange authorization code for access token
    import requests
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    
    try:
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        tokens = token_response.json()
        
        # Verify ID token
        id_token = tokens.get("id_token")
        if not id_token:
            return RedirectResponse(url="/?error=no_id_token")
        
        user_info = verify_google_token(id_token)
        if not user_info:
            return RedirectResponse(url="/?error=unauthorized")
        
        # Create session
        session_token = create_session(user_info)
        
        # Redirect with token in URL, then set cookie on next page load
        # This avoids SameSite cookie issues with redirects
        response = RedirectResponse(url=f"/?auth_token={session_token}", status_code=302)
        
        # Clear state cookie
        response.delete_cookie(key="oauth_state")
        
        print(f"✅ Session created for {user_info['email']}, redirecting with token")
        return response
        
    except Exception as e:
        print(f"❌ OAuth callback error: {e}")
        return RedirectResponse(url=f"/?error=token_exchange_failed")


@app.get("/auth/status")
async def auth_status(user_info: dict = Depends(require_auth)):
    """Check authentication status"""
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
    """Logout - invalidate session"""
    if session_token:
        delete_session(session_token)
    
    response.delete_cookie(key="session_token")
    return {"success": True}


# API Health check
@app.get("/api/health")
def health_check():
    return {"status": "healthy", "version": "2.0.0"}


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
    
    projects = []
    for row in cursor.fetchall():
        projects.append({
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "status": row[3],
            "progress": row[4],
            "category": row[5],
            "priority": row[6],
            "revenue_current": row[7],
            "revenue_goal": row[8],
            "health_score": row[9],
            "created_at": row[10],
            "updated_at": row[11]
        })
    
    conn.close()
    return {"projects": projects}


@app.get("/tasks")
def get_tasks(
    status: Optional[str] = None,
    user_info: dict = Depends(require_auth)
):
    """Get tasks with optional status filter"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if status:
        cursor.execute("""
            SELECT id, project_id, title, description, status, priority,
                   due_date, task_type, estimated_hours, created_at, updated_at
            FROM tasks
            WHERE status = ?
            ORDER BY priority DESC, due_date ASC
        """, (status,))
    else:
        cursor.execute("""
            SELECT id, project_id, title, description, status, priority,
                   due_date, task_type, estimated_hours, created_at, updated_at
            FROM tasks
            ORDER BY priority DESC, due_date ASC
        """)
    
    tasks = []
    for row in cursor.fetchall():
        tasks.append({
            "id": row[0],
            "project_id": row[1],
            "title": row[2],
            "description": row[3],
            "status": row[4],
            "priority": row[5],
            "due_date": row[6],
            "task_type": row[7],
            "estimated_hours": row[8],
            "created_at": row[9],
            "updated_at": row[10]
        })
    
    conn.close()
    return {"tasks": tasks}


@app.post("/tasks")
def create_task(task_data: dict, user_info: dict = Depends(require_auth)):
    """Create a new task"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Required fields
    project_id = task_data.get('project_id')
    title = task_data.get('title')
    
    if not project_id or not title:
        raise HTTPException(status_code=400, detail="project_id and title are required")
    
    # Optional fields
    description = task_data.get('description', '')
    status = task_data.get('status', 'todo')
    priority = task_data.get('priority', 'medium')
    due_date = task_data.get('due_date')
    task_type = task_data.get('task_type', 'feature')
    estimated_hours = task_data.get('estimated_hours')
    
    cursor.execute("""
        INSERT INTO tasks (project_id, title, description, status, priority, due_date, task_type, estimated_hours, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (project_id, title, description, status, priority, due_date, task_type, estimated_hours, 
          datetime.now().isoformat(), datetime.now().isoformat()))
    
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {"success": True, "task_id": task_id}


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task_data: dict, user_info: dict = Depends(require_auth)):
    """Update a task"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Build update query dynamically based on provided fields
    allowed_fields = ['title', 'description', 'status', 'priority', 'due_date', 'estimated_hours']
    updates = []
    values = []
    
    for field in allowed_fields:
        if field in task_data:
            updates.append(f"{field} = ?")
            values.append(task_data[field])
    
    if 'status' in task_data and task_data['status'] == 'done' and 'completed_at' not in task_data:
        updates.append("completed_at = ?")
        values.append(datetime.now().isoformat())
    
    if not updates:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    
    updates.append("updated_at = ?")
    values.append(datetime.now().isoformat())
    values.append(task_id)
    
    cursor.execute(f"""
        UPDATE tasks 
        SET {', '.join(updates)}
        WHERE id = ?
    """, values)
    
    conn.commit()
    conn.close()
    
    return {"success": True, "updated": cursor.rowcount}


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, user_info: dict = Depends(require_auth)):
    """Delete a task"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    
    conn.commit()
    conn.close()
    
    return {"success": True, "deleted": cursor.rowcount}


@app.get("/expenses")
def get_expenses(user_info: dict = Depends(require_auth)):
    """Get all expenses"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, project_id, amount, description, category, date, vendor, recurring
        FROM expenses
        ORDER BY date DESC
        LIMIT 100
    """)
    
    expenses = []
    for row in cursor.fetchall():
        expenses.append({
            "id": row[0],
            "project_id": row[1],
            "amount": row[2],
            "description": row[3],
            "category": row[4],
            "date": row[5],
            "vendor": row[6],
            "recurring": bool(row[7])
        })
    
    conn.close()
    return {"expenses": expenses}


@app.get("/dashboard/summary")
def get_dashboard_summary(user_info: dict = Depends(require_auth)):
    """Get dashboard summary statistics"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Project counts
    cursor.execute("SELECT COUNT(*) FROM projects WHERE status = 'active'")
    active_projects = cursor.fetchone()[0]
    
    # Task stats
    cursor.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
    task_stats = {}
    for status, count in cursor.fetchall():
        task_stats[status] = count
    
    # Monthly expenses
    cursor.execute("""
        SELECT SUM(amount) FROM expenses 
        WHERE date >= date('now', 'start of month')
    """)
    monthly_expenses = cursor.fetchone()[0] or 0
    
    # Quarterly revenue
    cursor.execute("""
        SELECT SUM(revenue_current) FROM projects
    """)
    quarterly_revenue = cursor.fetchone()[0] or 0
    
    # Overdue tasks
    cursor.execute("""
        SELECT COUNT(*) FROM tasks 
        WHERE status != 'done' 
        AND due_date < date('now')
    """)
    overdue_tasks = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "projects": {"active": active_projects},
        "tasks": task_stats,
        "monthly_expenses": monthly_expenses,
        "quarterly_revenue": quarterly_revenue,
        "overdue_tasks": overdue_tasks
    }


@app.get("/external/metrics")
async def get_external_metrics(user_info: dict = Depends(require_auth)):
    """Get metrics from external APIs (YouTube, Stripe, Google Analytics)"""
    try:
        metrics = await get_all_external_metrics()
        return metrics
    except Exception as e:
        print(f"Error fetching external metrics: {e}")
        return {
            "youtube": {"error": "Not configured"},
            "stripe": {"error": "Not configured"},
            "analytics": {"error": "Not configured"}
        }


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting UnGouge Dashboard API on http://localhost:8000")
    init_db()
    uvicorn.run(app, host="0.0.0.0", port=8000)
