"""
UnGouge Executive Dashboard - FastAPI Backend
Server-side OAuth 2.0 redirect flow (no popups!)
Build: 2026-02-09-1439 - Forces cache bust
"""

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("ungouge-dashboard")

from fastapi import FastAPI, HTTPException, Cookie, Response, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
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
    allow_origins=["https://dashboard.ungouge.ai"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    # CSP: Allow inline scripts (needed for current architecture) but restrict sources
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://accounts.google.com; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https://accounts.google.com https://oauth2.googleapis.com; "
        "frame-ancestors 'none'; "
        "form-action 'self' https://accounts.google.com;"
    )
    return response

# Startup event - initialize database
@app.on_event("startup")
def startup_event():
    """Initialize database on startup"""
    logger.info("🚀 Initializing database...")
    init_db()
    
    logger.info("🔌 Initializing API integrations...")
    initialize_apis()
    logger.info("✅ API integrations ready")
    logger.info("✅ Database initialized")
    
    # Seed with launch plan data if empty
    from database import seed_sample_data
    seed_sample_data()
    logger.info("✅ Launch plan data seeded")
    
    # Clean up expired sessions on startup
    cleanup_expired_sessions()
    logger.info("✅ Expired sessions cleaned up")

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


# Track last cleanup time for periodic session cleanup
_last_cleanup_time = None

# Session verification dependency
# TODO [HIGH-01]: Add rate limiting to auth endpoints using slowapi
# e.g. @limiter.limit("5/minute") on /auth/login, /auth/callback
async def require_auth(request: Request):
    """Verify session token from cookie"""
    # Periodically clean up expired sessions (at most once per hour)
    global _last_cleanup_time
    now = datetime.now()
    if _last_cleanup_time is None or (now - _last_cleanup_time) > timedelta(hours=1):
        _last_cleanup_time = now
        cleanup_expired_sessions()

    session_token = request.cookies.get("session_token")
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
    auth_token: Optional[str] = None
):
    """Root route - serve login page or dashboard based on auth"""
    static_dir_path = os.path.join(os.path.dirname(__file__), "static")
    
    # If auth_token in URL (from OAuth callback), validate and set cookie
    if auth_token:
        logger.info("🔍 Received auth_token in URL")
        user_info = verify_session(auth_token)
        if user_info:
            logger.info(f"✅ Valid auth token for {user_info.get('email')}, serving dashboard")
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
            logger.warning("❌ Invalid auth token")
    
    # Read cookie directly from request (more reliable than Cookie parameter)
    session_token = request.cookies.get("session_token")
    
    # Check if authenticated via cookie
    if session_token:
        user_info = verify_session(session_token)
        if user_info:
            logger.info(f"✅ Authenticated user: {user_info.get('email')}")
            dashboard_path = os.path.join(static_dir_path, "dashboard-v2.html")
            if os.path.exists(dashboard_path):
                return FileResponse(dashboard_path)
        else:
            # Session invalid/expired - clear the stale cookie to prevent loops
            logger.warning("❌ Invalid or expired session token - clearing cookie")
            login_path = os.path.join(static_dir_path, "login.html")
            if os.path.exists(login_path):
                login_response = FileResponse(login_path)
                login_response.delete_cookie(key="session_token", path="/")
                return login_response
    else:
        logger.warning("❌ No session cookie present")
    
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
        
        # Set session cookie directly on the redirect response
        # This avoids exposing the token in the URL (HIGH-09)
        response = RedirectResponse(url="/dashboard-v2.html", status_code=302)
        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=86400,  # 24 hours
            path="/"
        )
        
        # Clear state cookie
        response.delete_cookie(key="oauth_state")
        
        logger.info(f"✅ Session created for {user_info['email']}, redirecting to dashboard")
        return response
        
    except Exception as e:
        logger.error(f"❌ OAuth callback error: {e}")
        return RedirectResponse(url=f"/login.html?error=token_exchange_failed")


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


@app.delete("/auth/account")
async def delete_account(
    response: Response,
    user_info: dict = Depends(require_auth)
):
    """
    Delete user account and all associated data
    
    WARNING: This is permanent and cannot be undone
    Deletes: user sessions, tasks, projects, expenses, timeclock entries
    """
    user_email = user_info.get("email")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Delete all user data in order (respecting foreign keys)
        # 1. Delete timeclock entries
        cursor.execute("DELETE FROM timeclock WHERE user_email = %s", (user_email,))
        
        # 2. Delete expenses for user's projects
        cursor.execute("""
            DELETE FROM expenses WHERE project_id IN (
                SELECT id FROM projects WHERE created_by = %s
            )
        """, (user_email,))
        
        # 3. Delete tasks for user's projects
        cursor.execute("""
            DELETE FROM tasks WHERE project_id IN (
                SELECT id FROM projects WHERE created_by = %s
            )
        """, (user_email,))
        
        # 4. Delete projects
        cursor.execute("DELETE FROM projects WHERE created_by = %s", (user_email,))
        
        # 5. Delete all sessions for this user
        cursor.execute("DELETE FROM sessions WHERE user_email = %s", (user_email,))
        
        conn.commit()
        
        # Clear session cookie
        response.delete_cookie(key="session_token")
        
        rows_affected = cursor.rowcount
        conn.close()
        
        return {
            "success": True, 
            "message": f"Account deleted. Removed {rows_affected} records.",
            "deleted_email": user_email
        }
    
    except Exception as e:
        conn.rollback()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Failed to delete account: {str(e)}")


# Debug: list static files (protected — requires auth)
@app.get("/api/debug/static")
def debug_static(user_info: dict = Depends(require_auth)):
    """List files in static directory"""
    import glob
    files = glob.glob(os.path.join(static_dir, "*.html"))
    return {
        "static_dir": static_dir,
        "files": [os.path.basename(f) for f in files],
        "exists": os.path.exists(static_dir)
    }

# API Health check
@app.get("/api/health")
def health_check():
    """Health check with database stats"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS cnt FROM tasks")
        task_count = cursor.fetchone()["cnt"]
        cursor.execute("SELECT COUNT(*) AS cnt FROM projects")
        # Debug marker - if you see this in /api/health, new code is deployed
        BUILD_VERSION = "2026-02-11-0610"
        project_count = cursor.fetchone()["cnt"]
        conn.close()
        return {
            "status": "healthy", 
            "version": "2.0.0",
            "build": BUILD_VERSION,
            "db": {
                "tasks": task_count,
                "projects": project_count
            }
        }
    except Exception as e:
        return {"status": "error", "version": "2.0.0", "error": str(e)}


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
            "id": row["id"],
            "name": row["name"],
            "description": row["description"],
            "status": row["status"],
            "progress": row["progress"],
            "category": row["category"],
            "priority": row["priority"],
            "revenue_current": row["revenue_current"],
            "revenue_goal": row["revenue_goal"],
            "health_score": row["health_score"],
            "created_at": str(row["created_at"]) if row["created_at"] else None,
            "updated_at": str(row["updated_at"]) if row["updated_at"] else None
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
            WHERE status = %s
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
            "id": row["id"],
            "project_id": row["project_id"],
            "title": row["title"],
            "description": row["description"],
            "status": row["status"],
            "priority": row["priority"],
            "due_date": row["due_date"],
            "task_type": row["task_type"],
            "estimated_hours": row["estimated_hours"],
            "created_at": str(row["created_at"]) if row["created_at"] else None,
            "updated_at": str(row["updated_at"]) if row["updated_at"] else None
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
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
            updates.append(f"{field} = %s")
            values.append(task_data[field])
    
    if 'status' in task_data and task_data['status'] == 'done' and 'completed_at' not in task_data:
        updates.append("completed_at = %s")
        values.append(datetime.now().isoformat())
    
    if not updates:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    
    updates.append("updated_at = %s")
    values.append(datetime.now().isoformat())
    values.append(task_id)
    
    cursor.execute(f"""
        UPDATE tasks 
        SET {', '.join(updates)}
        WHERE id = %s
    """, values)
    
    conn.commit()
    conn.close()
    
    return {"success": True, "updated": cursor.rowcount}


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, user_info: dict = Depends(require_auth)):
    """Delete a task"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    
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
            "id": row["id"],
            "project_id": row["project_id"],
            "amount": row["amount"],
            "description": row["description"],
            "category": row["category"],
            "date": row["date"],
            "vendor": row["vendor"],
            "recurring": bool(row["recurring"])
        })
    
    conn.close()
    return {"expenses": expenses}


@app.post("/expenses")
def create_expense(expense_data: dict, user_info: dict = Depends(require_auth)):
    """Create a new expense"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Required fields
    description = expense_data.get('description')
    amount = expense_data.get('amount')
    
    if not description or amount is None:
        raise HTTPException(status_code=400, detail="description and amount are required")
    
    # Optional fields
    project_id = expense_data.get('project_id')
    category = expense_data.get('category', 'other')
    date = expense_data.get('date', datetime.now().strftime('%Y-%m-%d'))
    vendor = expense_data.get('vendor', '')
    recurring = expense_data.get('recurring', False)
    
    cursor.execute("""
        INSERT INTO expenses (project_id, amount, description, category, date, vendor, recurring, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (project_id, amount, description, category, date, vendor, 1 if recurring else 0, datetime.now().isoformat()))
    
    expense_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {"success": True, "expense_id": expense_id}


@app.put("/expenses/{expense_id}")
def update_expense(expense_id: int, expense_data: dict, user_info: dict = Depends(require_auth)):
    """Update an expense"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Build update query dynamically based on provided fields
    allowed_fields = ['amount', 'description', 'category', 'date', 'vendor', 'recurring']
    updates = []
    values = []
    
    for field in allowed_fields:
        if field in expense_data:
            if field == 'recurring':
                updates.append(f"{field} = %s")
                values.append(1 if expense_data[field] else 0)
            else:
                updates.append(f"{field} = %s")
                values.append(expense_data[field])
    
    if not updates:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    
    values.append(expense_id)
    
    cursor.execute(f"""
        UPDATE expenses
        SET {', '.join(updates)}
        WHERE id = %s
    """, values)
    
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    
    if affected == 0:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    return {"success": True, "updated": affected}


@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, user_info: dict = Depends(require_auth)):
    """Delete an expense"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
    
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    if affected == 0:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    return {"success": True, "deleted": affected}


@app.get("/dashboard/summary")
def get_dashboard_summary(user_info: dict = Depends(require_auth)):
    """Get dashboard summary statistics"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Project counts
    cursor.execute("SELECT COUNT(*) AS cnt FROM projects WHERE status = 'active'")
    active_projects = cursor.fetchone()["cnt"]
    
    # Task stats
    cursor.execute("SELECT status, COUNT(*) AS cnt FROM tasks GROUP BY status")
    task_stats = {}
    for row in cursor.fetchall():
        task_stats[row["status"]] = row["cnt"]
    
    # Monthly expenses
    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0) AS total FROM expenses 
        WHERE date >= DATE_FORMAT(CURDATE(), '%%Y-%%m-01')
    """)
    monthly_expenses = cursor.fetchone()["total"] or 0
    
    # Quarterly revenue
    cursor.execute("""
        SELECT COALESCE(SUM(revenue_current), 0) AS total FROM projects
    """)
    quarterly_revenue = cursor.fetchone()["total"] or 0
    
    # Overdue tasks
    cursor.execute("""
        SELECT COUNT(*) AS cnt FROM tasks 
        WHERE status != 'done' 
        AND due_date < CURDATE()
    """)
    overdue_tasks = cursor.fetchone()["cnt"]
    
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
        logger.error(f"❌ Error fetching external metrics: {e}")
        return {
            "youtube": {"error": "Not configured"},
            "stripe": {"error": "Not configured"},
            "analytics": {"error": "Not configured"}
        }


# ===== STRIPE REVENUE =====

@app.get("/api/stripe/summary")
def get_stripe_summary(user_info: dict = Depends(require_auth)):
    """Get Stripe revenue summary — MTD, 30d, balances, customer count"""
    import stripe as stripe_sdk
    import time

    api_key = os.environ.get("STRIPE_API_KEY", "")
    if not api_key:
        return {
            "revenue_mtd": 0.0,
            "revenue_30d": 0.0,
            "total_charges": 0,
            "successful_charges": 0,
            "total_customers": 0,
            "balance": {"available": 0, "pending": 0},
            "currency": "usd",
            "error": "Stripe API key not configured"
        }

    stripe_sdk.api_key = api_key

    try:
        now = int(time.time())

        # Start of current month (UTC)
        from datetime import timezone
        now_dt = datetime.now(timezone.utc)
        start_of_month = int(datetime(now_dt.year, now_dt.month, 1, tzinfo=timezone.utc).timestamp())
        thirty_days_ago = now - (30 * 24 * 60 * 60)

        # Balance
        try:
            balance = stripe_sdk.Balance.retrieve()
            available = sum(b.amount for b in balance.available) / 100.0
            pending = sum(b.amount for b in balance.pending) / 100.0
        except Exception as e:
            logger.warning(f"Stripe balance fetch failed: {e}")
            available = 0.0
            pending = 0.0

        # MTD charges
        revenue_mtd = 0.0
        total_charges_mtd = 0
        successful_charges_mtd = 0
        try:
            charges_mtd = stripe_sdk.Charge.list(created={"gte": start_of_month}, limit=100)
            for charge in charges_mtd.auto_paging_iter():
                total_charges_mtd += 1
                if charge.status == "succeeded":
                    successful_charges_mtd += 1
                    revenue_mtd += charge.amount / 100.0
        except Exception as e:
            logger.warning(f"Stripe MTD charges fetch failed: {e}")

        # 30-day charges
        revenue_30d = 0.0
        try:
            charges_30d = stripe_sdk.Charge.list(created={"gte": thirty_days_ago}, limit=100)
            for charge in charges_30d.auto_paging_iter():
                if charge.status == "succeeded":
                    revenue_30d += charge.amount / 100.0
        except Exception as e:
            logger.warning(f"Stripe 30d charges fetch failed: {e}")

        # Customer count
        total_customers = 0
        try:
            customers = stripe_sdk.Customer.list(limit=1)
            total_customers = customers.total_count if hasattr(customers, 'total_count') else len(customers.data)
        except Exception as e:
            logger.warning(f"Stripe customer count fetch failed: {e}")

        return {
            "revenue_mtd": round(revenue_mtd, 2),
            "revenue_30d": round(revenue_30d, 2),
            "total_charges": total_charges_mtd,
            "successful_charges": successful_charges_mtd,
            "total_customers": total_customers,
            "balance": {"available": round(available, 2), "pending": round(pending, 2)},
            "currency": "usd",
            "last_updated": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Stripe summary error: {e}")
        return {
            "revenue_mtd": 0.0,
            "revenue_30d": 0.0,
            "total_charges": 0,
            "successful_charges": 0,
            "total_customers": 0,
            "balance": {"available": 0, "pending": 0},
            "currency": "usd",
            "error": str(e)
        }


# ===== TIME CLOCK =====

@app.post("/api/timeclock/in")
def clock_in(user_info: dict = Depends(require_auth)):
    """Clock in - create new time entry"""
    conn = get_connection()
    cursor = conn.cursor()
    
    user_email = user_info.get('email')
    
    # Check if already clocked in
    cursor.execute("""
        SELECT id FROM timeclock 
        WHERE user_email = %s AND clock_out IS NULL
        ORDER BY clock_in DESC LIMIT 1
    """, (user_email,))
    
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Already clocked in")
    
    # Create new clock-in entry
    clock_in_time = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO timeclock (user_email, clock_in, created_at)
        VALUES (%s, %s, %s)
    """, (user_email, clock_in_time, datetime.now().isoformat()))
    
    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "id": entry_id,
        "clock_in": clock_in_time
    }


@app.post("/api/timeclock/out")
def clock_out(user_info: dict = Depends(require_auth)):
    """Clock out - close current time entry"""
    conn = get_connection()
    cursor = conn.cursor()
    
    user_email = user_info.get('email')
    
    # Find active clock-in entry
    cursor.execute("""
        SELECT id, clock_in FROM timeclock 
        WHERE user_email = %s AND clock_out IS NULL
        ORDER BY clock_in DESC LIMIT 1
    """, (user_email,))
    
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=400, detail="Not clocked in")
    
    entry_id = row["id"]
    clock_in_time = datetime.fromisoformat(str(row["clock_in"]))
    clock_out_time = datetime.now()
    
    # Calculate duration in minutes
    duration = (clock_out_time - clock_in_time).total_seconds() / 60
    
    # Update entry
    cursor.execute("""
        UPDATE timeclock 
        SET clock_out = %s, duration_minutes = %s
        WHERE id = %s
    """, (clock_out_time.isoformat(), duration, entry_id))
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "id": entry_id,
        "clock_out": clock_out_time.isoformat(),
        "duration_minutes": duration
    }


@app.get("/api/timeclock/stats")
def get_timeclock_stats(user_info: dict = Depends(require_auth)):
    """Get aggregated time clock statistics"""
    conn = get_connection()
    cursor = conn.cursor()
    
    user_email = user_info.get('email')
    now = datetime.now()
    
    # Check if currently clocked in
    cursor.execute("""
        SELECT id, clock_in FROM timeclock 
        WHERE user_email = %s AND clock_out IS NULL
        ORDER BY clock_in DESC LIMIT 1
    """, (user_email,))
    
    active_entry = cursor.fetchone()
    is_clocked_in = active_entry is not None
    current_session_start = active_entry["clock_in"] if active_entry else None
    
    # Today's hours (completed + current session)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    cursor.execute("""
        SELECT COALESCE(SUM(duration_minutes), 0) AS total FROM timeclock
        WHERE user_email = %s AND clock_in >= %s
    """, (user_email, today_start))
    today_minutes = cursor.fetchone()["total"]
    
    # Add current session if clocked in
    if is_clocked_in:
        current_duration = (now - datetime.fromisoformat(str(current_session_start))).total_seconds() / 60
        today_minutes += current_duration
    
    # This week's hours
    week_start = (now - timedelta(days=now.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    ).isoformat()
    cursor.execute("""
        SELECT COALESCE(SUM(duration_minutes), 0) AS total FROM timeclock
        WHERE user_email = %s AND clock_in >= %s
    """, (user_email, week_start))
    week_minutes = cursor.fetchone()["total"]
    
    if is_clocked_in:
        week_minutes += current_duration
    
    # This month's hours
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    cursor.execute("""
        SELECT COALESCE(SUM(duration_minutes), 0) AS total FROM timeclock
        WHERE user_email = %s AND clock_in >= %s
    """, (user_email, month_start))
    month_minutes = cursor.fetchone()["total"]
    
    if is_clocked_in:
        month_minutes += current_duration
    
    conn.close()
    
    return {
        "is_clocked_in": is_clocked_in,
        "current_session_start": current_session_start,
        "today_hours": round(today_minutes / 60, 2),
        "week_hours": round(week_minutes / 60, 2),
        "month_hours": round(month_minutes / 60, 2)
    }


# Serve HTML pages explicitly (more reliable than StaticFiles mount)
static_dir = os.path.join(os.path.dirname(__file__), "static")

def _require_session_or_redirect(request: Request):
    """Helper: check session cookie, redirect to login if invalid."""
    session_token = request.cookies.get("session_token")
    if not session_token or not verify_session(session_token):
        return RedirectResponse(url="/login.html")
    return None

def _serve_static_no_cache(filepath):
    """Serve a static file with no-cache headers to prevent stale content."""
    response = FileResponse(filepath)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.get("/tasks.html")
def serve_tasks_page(request: Request):
    redirect = _require_session_or_redirect(request)
    if redirect:
        return redirect
    return _serve_static_no_cache(os.path.join(static_dir, "tasks.html"))

@app.get("/expenses.html")
def serve_expenses_page(request: Request):
    redirect = _require_session_or_redirect(request)
    if redirect:
        return redirect
    return _serve_static_no_cache(os.path.join(static_dir, "expenses.html"))

@app.get("/project-detail.html")
def serve_project_detail_page(request: Request):
    redirect = _require_session_or_redirect(request)
    if redirect:
        return redirect
    return _serve_static_no_cache(os.path.join(static_dir, "project-detail.html"))

@app.get("/settings.html")
def serve_settings_page(request: Request):
    redirect = _require_session_or_redirect(request)
    if redirect:
        return redirect
    return _serve_static_no_cache(os.path.join(static_dir, "settings.html"))

@app.get("/projects.html")
def serve_projects_page(request: Request):
    redirect = _require_session_or_redirect(request)
    if redirect:
        return redirect
    return _serve_static_no_cache(os.path.join(static_dir, "projects.html"))

@app.get("/projects-ungouge.html")
def serve_projects_ungouge_page(request: Request):
    redirect = _require_session_or_redirect(request)
    if redirect:
        return redirect
    return _serve_static_no_cache(os.path.join(static_dir, "projects-ungouge.html"))

@app.get("/projects-youtube.html")
def serve_projects_youtube_page(request: Request):
    redirect = _require_session_or_redirect(request)
    if redirect:
        return redirect
    return _serve_static_no_cache(os.path.join(static_dir, "projects-youtube.html"))

@app.get("/finances.html")
def serve_finances_page(request: Request):
    redirect = _require_session_or_redirect(request)
    if redirect:
        return redirect
    return _serve_static_no_cache(os.path.join(static_dir, "finances.html"))

@app.get("/dashboard-v2.html")
def serve_dashboard_v2_page(request: Request):
    redirect = _require_session_or_redirect(request)
    if redirect:
        return redirect
    return _serve_static_no_cache(os.path.join(static_dir, "dashboard-v2.html"))

@app.get("/login.html")
def serve_login_page():
    return FileResponse(os.path.join(static_dir, "login.html"))


if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting UnGouge Dashboard API on http://localhost:8000")
    init_db()
    uvicorn.run(app, host="0.0.0.0", port=8000)
