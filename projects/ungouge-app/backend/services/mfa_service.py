"""
MFA (Multi-Factor Authentication) Service
Email OTP implementation for Ungouge.ai

SECURITY FIXES:
  HIGH-2: MFA codes hashed with HMAC-SHA256 (server-side secret key) instead of plain SHA-256
  HIGH-3: Brute-force protection with attempt counter and 15-minute lockout after 5 failures
"""

import hmac
import hashlib
import secrets
import os
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.database import User
from services.email_service import send_mfa_code

# MFA Configuration
MFA_CODE_LENGTH = 6
MFA_CODE_EXPIRY_MINUTES = 10
MFA_MAX_ATTEMPTS = 5           # HIGH-3: max failed attempts before lockout
MFA_LOCKOUT_MINUTES = 15       # HIGH-3: lockout duration after max attempts

# HIGH-2: Server-side secret key for HMAC — falls back to JWT secret if not set
MFA_HMAC_SECRET = os.getenv("MFA_HMAC_SECRET", os.getenv("JWT_SECRET_KEY", "")).encode("utf-8")


def generate_mfa_code() -> str:
    """Generate a secure 6-digit numeric code"""
    return ''.join([str(secrets.randbelow(10)) for _ in range(MFA_CODE_LENGTH)])


def hash_mfa_code(code: str) -> str:
    """
    HIGH-2: Hash an MFA code with HMAC-SHA256 using a server-side secret key.
    
    This prevents rainbow table attacks — even with DB read access, an attacker
    cannot reverse the 1M possible 6-digit codes without the HMAC secret.
    """
    return hmac.new(MFA_HMAC_SECRET, code.encode('utf-8'), hashlib.sha256).hexdigest()


def mask_email(email: str) -> str:
    """
    Mask email for display (e.g., j***n@example.com)
    """
    if not email or '@' not in email:
        return '***@***.***'
    
    local, domain = email.split('@', 1)
    
    if len(local) <= 2:
        masked_local = local[0] + '***'
    else:
        masked_local = local[0] + '***' + local[-1]
    
    return f"{masked_local}@{domain}"


async def create_and_send_mfa_code(
    db: AsyncSession,
    user: User
) -> Tuple[bool, str]:
    """
    Generate MFA code, save to user, and send via email.
    
    HIGH-3: Also resets the attempt counter when a new code is issued.
    
    Args:
        db: Database session
        user: User object
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Generate code
    code = generate_mfa_code()
    expires_at = datetime.utcnow() + timedelta(minutes=MFA_CODE_EXPIRY_MINUTES)
    
    # Save HMAC-hashed code to user (HIGH-2: never store plaintext or plain hash)
    user.mfa_code = hash_mfa_code(code)
    user.mfa_code_expires = expires_at
    # HIGH-3: Reset attempt counter when new code is issued
    user.mfa_attempts = 0
    user.mfa_locked_until = None
    
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        return False, f"Failed to save MFA code: {str(e)}"
    
    # Send email
    email_sent = send_mfa_code(
        to_email=user.email,
        user_name=user.name,
        code=code,
        expiry_minutes=MFA_CODE_EXPIRY_MINUTES
    )
    
    if not email_sent:
        return False, "Failed to send verification email"
    
    return True, "Verification code sent to your email"


async def verify_mfa_code(
    db: AsyncSession,
    user: User,
    code: str
) -> Tuple[bool, str]:
    """
    Verify the MFA code entered by user.
    
    HIGH-3: Enforces brute-force protection:
      - Max 5 failed attempts per code
      - 15-minute lockout after exceeding max attempts
      - Counter resets on successful verification
    
    Args:
        db: Database session
        user: User object
        code: Code entered by user
        
    Returns:
        Tuple of (valid: bool, message: str)
    """
    # HIGH-3: Check if account is locked out
    if user.mfa_locked_until and datetime.utcnow() < user.mfa_locked_until:
        remaining = int((user.mfa_locked_until - datetime.utcnow()).total_seconds() / 60) + 1
        return False, f"Too many failed attempts. Please try again in {remaining} minutes."
    
    # If lockout has expired, reset
    if user.mfa_locked_until and datetime.utcnow() >= user.mfa_locked_until:
        user.mfa_locked_until = None
        user.mfa_attempts = 0
    
    # Check if code exists
    if not user.mfa_code:
        return False, "No verification code found. Please request a new one."
    
    # Check if code expired
    if user.mfa_code_expires and datetime.utcnow() > user.mfa_code_expires:
        # Clear expired code
        user.mfa_code = None
        user.mfa_code_expires = None
        user.mfa_attempts = 0
        await db.commit()
        return False, "Verification code has expired. Please request a new one."
    
    # HIGH-2: Verify code using HMAC (constant-time comparison via hmac.compare_digest)
    if not hmac.compare_digest(user.mfa_code, hash_mfa_code(code)):
        # HIGH-3: Increment attempt counter
        user.mfa_attempts = (user.mfa_attempts or 0) + 1
        
        if user.mfa_attempts >= MFA_MAX_ATTEMPTS:
            # Lock the account for MFA
            user.mfa_locked_until = datetime.utcnow() + timedelta(minutes=MFA_LOCKOUT_MINUTES)
            # Invalidate the current code
            user.mfa_code = None
            user.mfa_code_expires = None
            await db.commit()
            return False, f"Too many failed attempts. MFA locked for {MFA_LOCKOUT_MINUTES} minutes. Please request a new code after the lockout."
        
        remaining_attempts = MFA_MAX_ATTEMPTS - user.mfa_attempts
        await db.commit()
        return False, f"Invalid verification code. {remaining_attempts} attempt(s) remaining."
    
    # Success — clear the code and reset attempts
    user.mfa_code = None
    user.mfa_code_expires = None
    user.mfa_attempts = 0
    user.mfa_locked_until = None
    await db.commit()
    
    return True, "Code verified successfully"


async def enable_mfa(
    db: AsyncSession,
    user: User
) -> Tuple[bool, str]:
    """
    Enable MFA for user after code verification.
    
    Args:
        db: Database session
        user: User object
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    user.mfa_enabled = True
    
    try:
        await db.commit()
        return True, "Two-factor authentication enabled successfully"
    except Exception as e:
        await db.rollback()
        return False, f"Failed to enable MFA: {str(e)}"


async def disable_mfa(
    db: AsyncSession,
    user: User
) -> Tuple[bool, str]:
    """
    Disable MFA for user.
    
    Args:
        db: Database session
        user: User object
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    user.mfa_enabled = False
    user.mfa_code = None
    user.mfa_code_expires = None
    user.mfa_attempts = 0
    user.mfa_locked_until = None
    
    try:
        await db.commit()
        return True, "Two-factor authentication disabled"
    except Exception as e:
        await db.rollback()
        return False, f"Failed to disable MFA: {str(e)}"


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email address"""
    result = await db.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()
