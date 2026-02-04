"""
Google OAuth 2.0 Authentication Module
Verifies Google ID tokens and manages user sessions
"""

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import secrets
from datetime import datetime, timedelta
from typing import Optional
import sqlite3
import os

# OAuth Configuration
GOOGLE_CLIENT_ID = "1093157467231-3pgo81mrq5rjdvhvaa1uf81pk2ifhka2.apps.googleusercontent.com"
AUTHORIZED_EMAILS = ["void@ungouge.ai"]  # Only these emails can access

# Session expiration (24 hours)
SESSION_DURATION = timedelta(hours=24)

# Database path - must match database.py
DB_PATH = os.environ.get("DATABASE_PATH", "/tmp/dashboard.db")


def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_sessions_table():
    """Initialize sessions table if it doesn't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            name TEXT,
            picture TEXT,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# Initialize table on module load
init_sessions_table()


def verify_google_token(token: str) -> Optional[dict]:
    """
    Verify Google ID token and return user info if valid
    
    Args:
        token: Google ID token from OAuth flow
        
    Returns:
        dict with user info (email, name, picture) if valid, None otherwise
    """
    try:
        # Verify token with Google
        idinfo = id_token.verify_oauth2_token(
            token, 
            google_requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        # Check email authorization
        email = idinfo.get("email")
        if email not in AUTHORIZED_EMAILS:
            print(f"❌ Unauthorized email attempted access: {email}")
            return None
        
        # Return user info
        return {
            "email": email,
            "name": idinfo.get("name"),
            "picture": idinfo.get("picture"),
            "sub": idinfo.get("sub")  # Google user ID
        }
        
    except ValueError as e:
        # Invalid token
        print(f"❌ Token verification failed: {e}")
        return None


def create_session(user_info: dict) -> str:
    """
    Create a new session for authenticated user
    
    Args:
        user_info: Dict with email, name, picture from Google
        
    Returns:
        session_token: Secure random token for this session
    """
    # Generate secure random session token
    session_token = secrets.token_urlsafe(32)
    
    # Calculate expiration
    created_at = datetime.now()
    expires_at = created_at + SESSION_DURATION
    
    # Store in database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sessions (token, email, name, picture, created_at, expires_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        session_token,
        user_info["email"],
        user_info.get("name"),
        user_info.get("picture"),
        created_at.isoformat(),
        expires_at.isoformat()
    ))
    conn.commit()
    conn.close()
    
    print(f"✅ Session created for {user_info['email']}")
    return session_token


def verify_session(session_token: str) -> Optional[dict]:
    """
    Verify session token and return user info if valid
    
    Args:
        session_token: Token from cookie/header
        
    Returns:
        dict with user info if session valid and not expired, None otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT email, name, picture, expires_at
        FROM sessions
        WHERE token = ?
    """, (session_token,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    # Check expiration
    expires_at = datetime.fromisoformat(row["expires_at"])
    if datetime.now() > expires_at:
        # Session expired, delete it
        delete_session(session_token)
        return None
    
    return {
        "email": row["email"],
        "name": row["name"],
        "picture": row["picture"]
    }


def delete_session(session_token: str) -> bool:
    """
    Delete/invalidate a session (logout)
    
    Args:
        session_token: Token to invalidate
        
    Returns:
        True if session existed and was deleted, False otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM sessions WHERE token = ?", (session_token,))
    deleted = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    if deleted:
        print(f"✅ Session deleted")
    
    return deleted


def cleanup_expired_sessions():
    """
    Remove expired sessions from database
    Call periodically to prevent bloat
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        DELETE FROM sessions
        WHERE expires_at < ?
    """, (datetime.now().isoformat(),))
    
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    if deleted > 0:
        print(f"🧹 Cleaned up {deleted} expired sessions")
