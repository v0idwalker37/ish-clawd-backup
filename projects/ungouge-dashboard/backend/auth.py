"""
Google OAuth 2.0 Authentication Module
Verifies Google ID tokens and manages user sessions
"""

from google.oauth2 import id_token
from google.auth.transport import requests
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict

# OAuth Configuration
GOOGLE_CLIENT_ID = "1093157467231-3pgo81mrq5rjdvhvaa1uf81pk2ifhka2.apps.googleusercontent.com"
AUTHORIZED_EMAILS = ["void@ungouge.ai"]  # Only these emails can access

# In-memory session store (sufficient for single-instance MVP)
# Format: {session_token: {"email": str, "expires": datetime, "user_info": dict}}
sessions: Dict[str, dict] = {}

# Session expiration (24 hours)
SESSION_DURATION = timedelta(hours=24)


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
            requests.Request(), 
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
    
    # Store session with expiration
    sessions[session_token] = {
        "email": user_info["email"],
        "user_info": user_info,
        "created": datetime.now(),
        "expires": datetime.now() + SESSION_DURATION
    }
    
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
    session = sessions.get(session_token)
    
    if not session:
        return None
    
    # Check expiration
    if datetime.now() > session["expires"]:
        # Session expired, remove it
        del sessions[session_token]
        return None
    
    return session["user_info"]


def delete_session(session_token: str) -> bool:
    """
    Delete/invalidate a session (logout)
    
    Args:
        session_token: Token to invalidate
        
    Returns:
        True if session existed and was deleted, False otherwise
    """
    if session_token in sessions:
        email = sessions[session_token]["email"]
        del sessions[session_token]
        print(f"✅ Session deleted for {email}")
        return True
    return False


def cleanup_expired_sessions():
    """
    Remove expired sessions from memory
    Call periodically to prevent memory bloat
    """
    now = datetime.now()
    expired = [token for token, session in sessions.items() if now > session["expires"]]
    
    for token in expired:
        del sessions[token]
    
    if expired:
        print(f"🧹 Cleaned up {len(expired)} expired sessions")
