"""
MFA (Multi-Factor Authentication) Service
Email OTP implementation for Ungouge.ai
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.database import User
from services.email_service import send_mfa_code

# MFA Configuration
MFA_CODE_LENGTH = 6
MFA_CODE_EXPIRY_MINUTES = 10


def generate_mfa_code() -> str:
    """Generate a secure 6-digit numeric code"""
    return ''.join([str(secrets.randbelow(10)) for _ in range(MFA_CODE_LENGTH)])


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
    
    Args:
        db: Database session
        user: User object
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Generate code
    code = generate_mfa_code()
    expires_at = datetime.utcnow() + timedelta(minutes=MFA_CODE_EXPIRY_MINUTES)
    
    # Save to user
    user.mfa_code = code
    user.mfa_code_expires = expires_at
    
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
    
    Args:
        db: Database session
        user: User object
        code: Code entered by user
        
    Returns:
        Tuple of (valid: bool, message: str)
    """
    # Check if code exists
    if not user.mfa_code:
        return False, "No verification code found. Please request a new one."
    
    # Check if code expired
    if user.mfa_code_expires and datetime.utcnow() > user.mfa_code_expires:
        # Clear expired code
        user.mfa_code = None
        user.mfa_code_expires = None
        await db.commit()
        return False, "Verification code has expired. Please request a new one."
    
    # Verify code (constant-time comparison for security)
    if not secrets.compare_digest(user.mfa_code, code):
        return False, "Invalid verification code"
    
    # Clear the code after successful verification
    user.mfa_code = None
    user.mfa_code_expires = None
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
