"""
CSRF Protection Middleware for FastAPI
Generates and validates CSRF tokens for state-changing operations
"""

import secrets
import hashlib
import time
from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import Response

# Token lifetime: 1 hour
CSRF_TOKEN_LIFETIME = 3600

class CSRFProtection:
    """CSRF token generator and validator"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def generate_token(self) -> str:
        """Generate a new CSRF token"""
        # Token format: {random_bytes}:{timestamp}:{signature}
        random_bytes = secrets.token_urlsafe(32)
        timestamp = str(int(time.time()))
        
        # Sign the token
        message = f"{random_bytes}:{timestamp}"
        signature = hashlib.sha256(
            f"{message}:{self.secret_key}".encode()
        ).hexdigest()[:16]
        
        return f"{random_bytes}:{timestamp}:{signature}"
    
    def validate_token(self, token: str) -> bool:
        """Validate a CSRF token"""
        if not token:
            return False
        
        parts = token.split(':')
        if len(parts) != 3:
            return False
        
        random_bytes, timestamp_str, signature = parts
        
        # Check expiration
        try:
            timestamp = int(timestamp_str)
            if time.time() - timestamp > CSRF_TOKEN_LIFETIME:
                return False
        except ValueError:
            return False
        
        # Verify signature
        message = f"{random_bytes}:{timestamp_str}"
        expected_signature = hashlib.sha256(
            f"{message}:{self.secret_key}".encode()
        ).hexdigest()[:16]
        
        return signature == expected_signature


async def csrf_protect(request: Request):
    """
    CSRF protection middleware
    Validates CSRF token on POST/PUT/DELETE/PATCH requests
    """
    # Skip CSRF for safe methods
    if request.method in ['GET', 'HEAD', 'OPTIONS']:
        return
    
    # Skip CSRF for API key authenticated requests
    if request.headers.get('X-API-Key'):
        return
    
    # Get token from header or form data
    token = request.headers.get('X-CSRF-Token')
    if not token and request.method == 'POST':
        # Try to get from form data
        try:
            form = await request.form()
            token = form.get('csrf_token')
        except:
            pass
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token missing"
        )
    
    # Validate token
    csrf = CSRFProtection(request.app.state.csrf_secret)
    if not csrf.validate_token(token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token invalid or expired"
        )


def set_csrf_cookie(response: Response, token: str):
    """Set CSRF token in cookie for client-side access"""
    response.set_cookie(
        key="csrf_token",
        value=token,
        httponly=False,  # JavaScript needs to read this
        secure=True,     # HTTPS only
        samesite="strict",
        max_age=CSRF_TOKEN_LIFETIME
    )
