"""
Authentication router - handles user registration, login, and profile management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import os
from datetime import datetime
from slowapi import Limiter
from slowapi.util import get_remote_address

from models.database import get_db, User
from models.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    RefreshTokenRequest,
    UserProfile,
    UserUpdate,
    ForgotPasswordRequest,
    MessageResponse,
    MFAStatusResponse,
    MFAEnableRequest,
    MFAVerifyRequest,
    MFADisableRequest,
    MFALoginRequest,
    MFARequiredResponse,
    RectificationRequest,
    PrivacyPreferences,
    RestrictionResponse,
)
from models.password_reset import PasswordResetRequest, PasswordResetVerify, PasswordResetResponse
from models.database import PasswordResetToken, EmailVerificationToken
import secrets
from datetime import timedelta
from services.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_current_user,
    security,
)
from services.logger import log_auth_success, log_auth_failure
from services.token_blacklist import TokenBlacklist

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/hour")  # Max 3 registrations per hour per IP
async def register(
    request: Request,
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user account
    
    - **email**: User's email address (must be unique)
    - **password**: Password (minimum 8 characters)
    - **name**: User's full name
    
    Returns JWT access and refresh tokens
    """
    from validators import validate_email, validate_password, sanitize_string
    from exceptions import DuplicateResourceError, ValidationError, UngougeException
    
    try:
        # Validate and normalize email
        normalized_email = validate_email(user_data.email)
        
        # Validate password
        validate_password(user_data.password)
        
        # Sanitize name
        sanitized_name = sanitize_string(user_data.name, 200)
        if not sanitized_name:
            raise ValidationError(
                "Name is required",
                suggestion="Please provide your name."
            )
        
    except UngougeException:
        raise
    
    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == normalized_email)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "An account with this email already exists.",
                "suggestion": (
                    "This email is already registered. Try:\n"
                    "• Log in instead of signing up\n"
                    "• Use the 'Forgot Password' link if you can't remember your password\n"
                    "• Use a different email address"
                )
            }
        )
    
    # Create new user
    user_id = str(uuid.uuid4())
    new_user = User(
        id=user_id,
        email=normalized_email,
        password_hash=hash_password(user_data.password),
        name=sanitized_name,
        is_active=True,
        is_verified=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    db.add(new_user)
    
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        from services.logger import log_error
        from exceptions import DatabaseError
        log_error("user_registration_db_failed", str(e), {"email": normalized_email})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to create your account due to a database error.",
                "suggestion": (
                    "Please try again. If the problem persists, contact support. "
                    "Your information has not been saved."
                )
            }
        )
    
    # Generate tokens
    access_token = create_access_token(data={"sub": user_id})
    refresh_token = create_refresh_token(data={"sub": user_id})
    
    # Generate email verification token
    verification_token = secrets.token_urlsafe(32)
    verification_record = EmailVerificationToken(
        id=str(uuid.uuid4()),
        user_id=user_id,
        token=verification_token,
        expires_at=datetime.utcnow() + timedelta(days=7),  # 7 day expiry
        created_at=datetime.utcnow(),
    )
    db.add(verification_record)
    
    try:
        await db.commit()
        
        # TODO: Send verification email
        # verification_url = f"{os.getenv('FRONTEND_URL')}/verify-email?token={verification_token}"
        # await send_verification_email(new_user.email, new_user.name, verification_url)
        
        # Only log token in development (NEVER in production)
        from services.logger import logger
        if os.getenv("ENVIRONMENT") != "production":
            logger.info(
                "email_verification_sent",
                extra={
                    "user_id": user_id,
                    "token": verification_token,
                    "note": "Dev only - token logged for testing"
                }
            )
        else:
            logger.info("email_verification_sent", extra={"user_id": user_id})
    except Exception as e:
        await db.rollback()
        from services.logger import log_error
        log_error("email_verification_error", str(e), {"user_id": user_id})
    
    # Log successful registration
    log_auth_success(user_id, "register", request.client.host if request.client else None)
    
    # Create response with cookies
    from fastapi.responses import JSONResponse
    is_production = os.getenv("ENVIRONMENT") == "production"
    
    response = JSONResponse(
        content={
            "message": "Registration successful",
            "user": {
                "id": user_id,
                "email": normalized_email,
                "name": sanitized_name,
                "is_verified": False,
            },
            # Also include tokens for backward compatibility / API clients
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        },
        status_code=status.HTTP_201_CREATED,
    )
    
    # Set httpOnly cookies (more secure than localStorage)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=is_production,
        samesite="strict",
        max_age=30 * 60,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=is_production,
        samesite="strict",
        max_age=7 * 24 * 60 * 60,
        path="/",
    )
    
    return response


@router.post("/auth/login")
@limiter.limit("5/minute")  # Max 5 login attempts per minute per IP
async def login(
    request: Request,
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """
    Login with email and password
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns JWT access and refresh tokens
    """
    from validators import validate_email
    from exceptions import InvalidCredentialsError, AccountInactiveError
    
    # Normalize email
    try:
        normalized_email = validate_email(credentials.email)
    except:
        # Invalid email format, but don't reveal this
        normalized_email = credentials.email.strip().lower()
    
    # Find user by email
    result = await db.execute(
        select(User).where(User.email == normalized_email)
    )
    user = result.scalar_one_or_none()
    
    # SECURITY: Always perform password verification to prevent timing attacks
    # Use dummy hash if user not found (same computational cost)
    password_hash = user.password_hash if user else hash_password("dummy_password_for_timing")
    is_valid = verify_password(credentials.password, password_hash)
    
    # Check if authentication succeeded
    if not user or not is_valid:
        # Log failed login attempt
        log_auth_failure(
            normalized_email,
            "login",
            "invalid_credentials",
            request.client.host if request.client else None
        )
        exc = InvalidCredentialsError()
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()
        )
    
    if not user.is_active:
        # Log attempt to access inactive account
        log_auth_failure(
            normalized_email,
            "login",
            "account_inactive",
            request.client.host if request.client else None
        )
        exc = AccountInactiveError()
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict()
        )
    
    # Check if MFA is enabled
    if user.mfa_enabled:
        from services.mfa_service import create_and_send_mfa_code, mask_email
        
        # Send MFA code
        success, message = await create_and_send_mfa_code(db, user)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": message}
            )
        
        # Return MFA required response (no tokens yet)
        return {
            "mfa_required": True,
            "email": mask_email(user.email),
            "message": "Please check your email for the verification code"
        }
    
    # Generate tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    # Log successful login
    log_auth_success(user.id, "login", request.client.host if request.client else None)
    
    # Create response with cookies
    from fastapi.responses import JSONResponse
    is_production = os.getenv("ENVIRONMENT") == "production"
    
    response = JSONResponse(content={
        "message": "Login successful",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "is_verified": user.is_verified,
        },
        # Also include tokens for backward compatibility / API clients
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    })
    
    # Set httpOnly cookies (more secure than localStorage)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=is_production,  # HTTPS only in production
        samesite="strict",
        max_age=30 * 60,  # 30 minutes (matches ACCESS_TOKEN_EXPIRE_MINUTES)
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=is_production,
        samesite="strict",
        max_age=7 * 24 * 60 * 60,  # 7 days (matches REFRESH_TOKEN_EXPIRE_DAYS)
        path="/",
    )
    
    return response


@router.post("/auth/refresh")
async def refresh_token_endpoint(
    request: Request,
    token_data: Optional[RefreshTokenRequest] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh access token using refresh token
    
    Accepts refresh token from:
    - Request body (token_data.refresh_token)
    - httpOnly cookie (refresh_token)
    
    Returns new JWT tokens and sets new cookies
    """
    # Get refresh token from body or cookie
    refresh_token_value = None
    if token_data and token_data.refresh_token:
        refresh_token_value = token_data.refresh_token
    elif request.cookies.get("refresh_token"):
        refresh_token_value = request.cookies.get("refresh_token")
    
    if not refresh_token_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required",
        )
    
    # Verify refresh token
    payload = verify_token(refresh_token_value, token_type="refresh")
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    # Verify user still exists and is active
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    # Generate new tokens
    new_access_token = create_access_token(data={"sub": user_id})
    new_refresh_token = create_refresh_token(data={"sub": user_id})
    
    # Create response with new cookies
    from fastapi.responses import JSONResponse
    is_production = os.getenv("ENVIRONMENT") == "production"
    
    response = JSONResponse(content={
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    })
    
    # Set new cookies
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=is_production,
        samesite="strict",
        max_age=30 * 60,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=is_production,
        samesite="strict",
        max_age=7 * 24 * 60 * 60,
        path="/",
    )
    
    return response


@router.get("/auth/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """
    Get current authenticated user's profile
    
    Requires: Bearer token in Authorization header
    """
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )


@router.put("/auth/me", response_model=UserProfile)
async def update_user_profile(
    updates: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update current user's profile
    
    - **name**: New name (optional)
    - **email**: New email (optional, must be unique)
    
    Requires: Bearer token in Authorization header
    """
    # Check if email is being changed and if it's already taken
    if updates.email and updates.email != current_user.email:
        result = await db.execute(
            select(User).where(User.email == updates.email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use",
            )
        
        current_user.email = updates.email
    
    # Update name if provided
    if updates.name:
        current_user.name = updates.name
    
    # Update timestamp
    current_user.updated_at = datetime.utcnow()
    
    try:
        await db.commit()
        await db.refresh(current_user)
    except Exception as e:
        await db.rollback()
        from services.logger import log_error
        log_error("profile_update_failed", str(e), {"user_id": current_user.id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile",
        )
    
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )


@router.post("/auth/forgot-password", response_model=PasswordResetResponse)
@limiter.limit("3/hour")  # Max 3 password reset requests per hour
async def forgot_password(
    req: Request,
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Request password reset email
    
    - **email**: User's email address
    
    Generates a time-limited reset token and sends email with reset link.
    For security, always returns success message (don't reveal if email exists).
    """
    # Find user by email
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    user = result.scalar_one_or_none()
    
    if user:
        # Generate secure random token
        reset_token = secrets.token_urlsafe(32)
        
        # Create password reset token record
        token_record = PasswordResetToken(
            id=str(uuid.uuid4()),
            user_id=user.id,
            token=reset_token,
            expires_at=datetime.utcnow() + timedelta(minutes=15),  # 15 minute expiry
            created_at=datetime.utcnow(),
        )
        db.add(token_record)
        
        try:
            await db.commit()
            
            # TODO: Send email with reset link
            # In production, use email service (SendGrid, AWS SES, Mailgun)
            # reset_url = f"{os.getenv('FRONTEND_URL')}/reset-password?token={reset_token}"
            # await send_password_reset_email(user.email, user.name, reset_url)
            
            # Only log token in development (NEVER in production)
            from services.logger import logger
            if os.getenv("ENVIRONMENT") != "production":
                logger.info(
                    "password_reset_requested",
                    extra={
                        "user_id": user.id,
                        "token": reset_token,
                        "note": "Dev only - token logged for testing"
                    }
                )
            else:
                logger.info("password_reset_requested", extra={"user_id": user.id})
        except Exception as e:
            await db.rollback()
            # Don't reveal error to user for security
            from services.logger import log_error
            log_error("password_reset_error", str(e), {"user_id": user.id})
    
    # SECURITY: Always return success (don't reveal if email exists)
    return PasswordResetResponse(
        message="If the email exists, a password reset link has been sent",
        expires_in_minutes=15
    )


@router.post("/auth/reset-password", response_model=MessageResponse)
@limiter.limit("5/hour")  # Max 5 reset attempts per hour
async def reset_password(
    req: Request,
    request: PasswordResetVerify,
    db: AsyncSession = Depends(get_db),
):
    """
    Reset password using token
    
    - **token**: Password reset token from email
    - **new_password**: New password (minimum 8 characters)
    """
    # Find token
    result = await db.execute(
        select(PasswordResetToken).where(PasswordResetToken.token == request.token)
    )
    token_record = result.scalar_one_or_none()
    
    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )
    
    # Check if token is expired
    if datetime.utcnow() > token_record.expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired",
        )
    
    # Check if token was already used
    if token_record.used_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has already been used",
        )
    
    # Get user
    result = await db.execute(
        select(User).where(User.id == token_record.user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # SECURITY: Validate password strength (same rules as registration)
    from validators import validate_password
    from exceptions import ValidationError
    try:
        validate_password(request.new_password)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.to_dict()
        )
    
    # Update password
    user.password_hash = hash_password(request.new_password)
    user.updated_at = datetime.utcnow()
    
    # Mark token as used
    token_record.used_at = datetime.utcnow()
    
    try:
        await db.commit()
        
        # Log password reset
        from services.logger import log_auth_success
        log_auth_success(user.id, "password_reset", req.client.host if req.client else None)
        
        return MessageResponse(message="Password has been reset successfully")
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password",
        )


@router.post("/auth/verify-email", response_model=MessageResponse)
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Verify email address using token
    
    - **token**: Email verification token from registration email
    """
    # Find token
    result = await db.execute(
        select(EmailVerificationToken).where(EmailVerificationToken.token == token)
    )
    token_record = result.scalar_one_or_none()
    
    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )
    
    # Check if token is expired
    if datetime.utcnow() > token_record.expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired",
        )
    
    # Check if token was already used
    if token_record.used_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email has already been verified",
        )
    
    # Get user
    result = await db.execute(
        select(User).where(User.id == token_record.user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Mark email as verified
    user.is_verified = True
    user.updated_at = datetime.utcnow()
    
    # Mark token as used
    token_record.used_at = datetime.utcnow()
    
    try:
        await db.commit()
        
        # Log email verification
        from services.logger import log_auth_success
        log_auth_success(user.id, "email_verification", None)
        
        return MessageResponse(message="Email verified successfully")
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify email",
        )


@router.post("/auth/resend-verification", response_model=MessageResponse)
@limiter.limit("3/hour")  # Max 3 resend requests per hour
async def resend_verification(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Resend email verification token
    
    Requires authentication. Only works if email is not already verified.
    """
    if current_user.is_verified:
        return MessageResponse(message="Email is already verified")
    
    # Generate new verification token
    verification_token = secrets.token_urlsafe(32)
    verification_record = EmailVerificationToken(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        token=verification_token,
        expires_at=datetime.utcnow() + timedelta(days=7),
        created_at=datetime.utcnow(),
    )
    db.add(verification_record)
    
    try:
        await db.commit()
        
        # TODO: Send verification email
        # verification_url = f"{os.getenv('FRONTEND_URL')}/verify-email?token={verification_token}"
        # await send_verification_email(current_user.email, current_user.name, verification_url)
        
        # Only log token in development (NEVER in production)
        from services.logger import logger
        if os.getenv("ENVIRONMENT") != "production":
            logger.info(
                "email_verification_resent",
                extra={
                    "user_id": current_user.id,
                    "token": verification_token,
                    "note": "Dev only - token logged for testing"
                }
            )
        else:
            logger.info("email_verification_resent", extra={"user_id": current_user.id})
        
        return MessageResponse(message="Verification email has been sent")
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email",
        )


@router.post("/auth/logout")
async def logout(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    current_user: User = Depends(get_current_user),
):
    """
    Logout - revoke current access token and clear cookies
    
    Adds the token to a blacklist so it cannot be used again.
    The token will be blacklisted until its natural expiry.
    Also clears httpOnly cookies.
    """
    from fastapi.responses import JSONResponse
    from fastapi.security import HTTPBearer
    
    # Get token from cookie or header
    token = None
    if request.cookies.get("access_token"):
        token = request.cookies.get("access_token")
    elif credentials:
        token = credentials.credentials
    
    # Calculate remaining validity and blacklist token
    try:
        if token:
            from jose import jwt
            from services.auth import SECRET_KEY, ALGORITHM
            
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            exp_timestamp = payload.get("exp")
            
            if exp_timestamp:
                exp_datetime = datetime.utcfromtimestamp(exp_timestamp)
                remaining_seconds = int((exp_datetime - datetime.utcnow()).total_seconds())
                
                # Only blacklist if token hasn't already expired
                if remaining_seconds > 0:
                    await TokenBlacklist.add(token, remaining_seconds)
            
            # Also blacklist refresh token if present in cookies
            refresh_token = request.cookies.get("refresh_token")
            if refresh_token:
                try:
                    refresh_payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
                    refresh_exp = refresh_payload.get("exp")
                    if refresh_exp:
                        refresh_remaining = int((datetime.utcfromtimestamp(refresh_exp) - datetime.utcnow()).total_seconds())
                        if refresh_remaining > 0:
                            await TokenBlacklist.add(refresh_token, refresh_remaining)
                except:
                    pass  # If refresh token is invalid, just ignore
        
        # Log logout
        from services.logger import log_auth_success
        log_auth_success(current_user.id, "logout", None)
        
    except Exception as e:
        # Even if blacklisting fails, continue with logout
        from services.logger import log_error
        log_error("logout_blacklist_error", str(e), {"user_id": current_user.id})
    
    # Create response that clears cookies
    is_production = os.getenv("ENVIRONMENT") == "production"
    response = JSONResponse(content={"message": "Logged out successfully"})
    
    # Clear cookies by setting them with expired max_age
    response.delete_cookie(key="access_token", path="/", secure=is_production, samesite="strict")
    response.delete_cookie(key="refresh_token", path="/", secure=is_production, samesite="strict")
    
    return response


# =============================================================================
# GDPR / CCPA Data Rights Endpoints
# =============================================================================

@router.get("/auth/my-data")
async def export_my_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Export all user data (GDPR data portability)
    
    Returns a JSON download of all user data including:
    - Profile information
    - All submitted quotes and analysis reports
    - Account activity
    """
    from middleware.data_retention import export_user_data
    from fastapi.responses import JSONResponse
    
    data = await export_user_data(db, current_user.id)
    
    return JSONResponse(
        content=data,
        headers={
            "Content-Disposition": f"attachment; filename=ungouge-data-export-{current_user.id[:8]}.json"
        }
    )


@router.delete("/auth/my-data")
async def delete_my_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete all user data (GDPR right to erasure)
    
    WARNING: This permanently deletes:
    - Your account
    - All submitted quotes
    - All analysis reports
    - All associated tokens
    
    This action cannot be undone.
    """
    from middleware.data_retention import delete_user_data
    from fastapi.responses import JSONResponse
    
    result = await delete_user_data(db, current_user.id)
    
    # Clear auth cookies
    is_production = os.getenv("ENVIRONMENT") == "production"
    response = JSONResponse(
        content={
            "message": "All your data has been permanently deleted",
            "deleted": result,
        }
    )
    response.delete_cookie(key="access_token", path="/", secure=is_production, samesite="strict")
    response.delete_cookie(key="refresh_token", path="/", secure=is_production, samesite="strict")
    
    return response


# =============================================================================
# GDPR Art. 16 — Right to Rectification (R-06)
# =============================================================================

@router.put("/auth/my-data")
async def rectify_my_data(
    updates: RectificationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update (rectify) personal data — GDPR Art. 16

    Allows users to correct their stored personal information:
    - **name**: Update display name
    - **email**: Update email address (resets verification; user must re-verify)

    At least one field must be provided.
    """
    from validators import validate_email, sanitize_string
    from exceptions import ValidationError
    from services.logger import logger

    if updates.name is None and updates.email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "No fields provided for update.",
                "suggestion": "Supply at least 'name' or 'email'.",
            },
        )

    changes: dict = {}

    # --- Name rectification ---
    if updates.name is not None:
        sanitized_name = sanitize_string(updates.name, 200)
        if not sanitized_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Name cannot be empty after sanitization."},
            )
        current_user.name = sanitized_name
        changes["name"] = sanitized_name

    # --- Email rectification (triggers re-verification) ---
    if updates.email is not None:
        normalized_email = validate_email(updates.email)

        if normalized_email != current_user.email:
            # Check uniqueness
            result = await db.execute(
                select(User).where(User.email == normalized_email)
            )
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "error": "An account with this email already exists.",
                        "suggestion": "Use a different email address.",
                    },
                )

            current_user.email = normalized_email
            current_user.is_verified = False  # Must re-verify new email
            changes["email"] = normalized_email
            changes["is_verified"] = False

            # Generate new verification token for the changed email
            verification_token = secrets.token_urlsafe(32)
            verification_record = EmailVerificationToken(
                id=str(uuid.uuid4()),
                user_id=current_user.id,
                token=verification_token,
                expires_at=datetime.utcnow() + timedelta(days=7),
                created_at=datetime.utcnow(),
            )
            db.add(verification_record)

    current_user.updated_at = datetime.utcnow()

    try:
        await db.commit()
        await db.refresh(current_user)
    except Exception as e:
        await db.rollback()
        from services.logger import log_error
        log_error("rectification_failed", str(e), {"user_id": current_user.id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update your data. Please try again.",
        )

    logger.info(
        "gdpr_rectification",
        extra={"user_id": current_user.id, "fields_changed": list(changes.keys())},
    )

    return {
        "message": "Your data has been updated.",
        "changes": changes,
        "re_verification_required": "email" in changes,
    }


# =============================================================================
# GDPR Art. 18 — Right to Restriction of Processing (R-07)
# =============================================================================

@router.post("/auth/restrict", response_model=RestrictionResponse)
async def restrict_processing(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Restrict processing of personal data — GDPR Art. 18

    When restricted:
    - Your data is **retained** but **not processed** (e.g. no new quote analysis).
    - Existing reports remain accessible to you.
    - You can lift the restriction at any time via POST /auth/unrestrict.
    """
    from services.logger import logger

    if current_user.is_restricted:
        return RestrictionResponse(
            message="Your data processing is already restricted.",
            is_restricted=True,
        )

    current_user.is_restricted = True
    current_user.updated_at = datetime.utcnow()

    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        from services.logger import log_error
        log_error("restriction_failed", str(e), {"user_id": current_user.id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to restrict processing. Please try again.",
        )

    logger.info(
        "gdpr_restriction_applied",
        extra={"user_id": current_user.id},
    )

    return RestrictionResponse(
        message="Processing of your data has been restricted. Your data is retained but will not be processed.",
        is_restricted=True,
    )


@router.post("/auth/unrestrict", response_model=RestrictionResponse)
async def unrestrict_processing(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Lift restriction on data processing — GDPR Art. 18

    Resumes normal processing of your data (e.g. quote analysis).
    """
    from services.logger import logger

    if not current_user.is_restricted:
        return RestrictionResponse(
            message="Your data processing is not currently restricted.",
            is_restricted=False,
        )

    current_user.is_restricted = False
    current_user.updated_at = datetime.utcnow()

    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        from services.logger import log_error
        log_error("unrestriction_failed", str(e), {"user_id": current_user.id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to lift restriction. Please try again.",
        )

    logger.info(
        "gdpr_restriction_lifted",
        extra={"user_id": current_user.id},
    )

    return RestrictionResponse(
        message="Restriction has been lifted. Normal data processing has resumed.",
        is_restricted=False,
    )


# =============================================================================
# GDPR Art. 21 — Right to Object / Privacy Preferences (R-08)
# =============================================================================

@router.put("/auth/preferences", response_model=PrivacyPreferences)
async def update_privacy_preferences(
    prefs: PrivacyPreferences,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update privacy and data-processing preferences — GDPR Art. 21

    Allows opting out of:
    - **analytics_opt_out**: Service-improvement analytics
    - **marketing_emails_opt_out**: Non-essential email communications

    Preferences take effect immediately.
    """
    from services.logger import logger

    current_user.privacy_preferences = prefs.dict()
    current_user.updated_at = datetime.utcnow()

    try:
        await db.commit()
        await db.refresh(current_user)
    except Exception as e:
        await db.rollback()
        from services.logger import log_error
        log_error("preferences_update_failed", str(e), {"user_id": current_user.id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preferences. Please try again.",
        )

    logger.info(
        "gdpr_preferences_updated",
        extra={"user_id": current_user.id, "preferences": prefs.dict()},
    )

    return prefs


@router.get("/auth/preferences", response_model=PrivacyPreferences)
async def get_privacy_preferences(
    current_user: User = Depends(get_current_user),
):
    """
    Get current privacy preferences — GDPR Art. 21

    Returns the user's current opt-out preferences.
    """
    stored = current_user.privacy_preferences or {}
    return PrivacyPreferences(
        analytics_opt_out=stored.get("analytics_opt_out", False),
        marketing_emails_opt_out=stored.get("marketing_emails_opt_out", False),
    )


# =============================================================================
# MFA (Email OTP) Endpoints
# =============================================================================

@router.get("/auth/mfa/status", response_model=MFAStatusResponse)
async def get_mfa_status(
    current_user: User = Depends(get_current_user),
):
    """
    Get current MFA status for authenticated user
    """
    from services.mfa_service import mask_email
    
    return MFAStatusResponse(
        mfa_enabled=current_user.mfa_enabled,
        email=mask_email(current_user.email),
    )


@router.post("/auth/mfa/enable")
@limiter.limit("3/hour")  # Max 3 MFA enable requests per hour
async def enable_mfa_start(
    request: Request,
    data: MFAEnableRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Start MFA enable process - verify password and send verification code
    
    - **password**: Current password for confirmation
    
    After calling this, user must verify the code with /auth/mfa/verify-enable
    """
    # Verify current password
    if not verify_password(data.password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    # Check if MFA is already enabled
    if current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Two-factor authentication is already enabled"
        )
    
    # Send verification code
    from services.mfa_service import create_and_send_mfa_code, mask_email
    
    success, message = await create_and_send_mfa_code(db, current_user)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
    
    return {
        "message": message,
        "email": mask_email(current_user.email),
    }


@router.post("/auth/mfa/verify-enable")
async def enable_mfa_verify(
    data: MFAVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Verify code and enable MFA
    
    - **code**: 6-digit verification code from email
    """
    from services.mfa_service import verify_mfa_code, enable_mfa
    
    # Verify the code
    valid, message = await verify_mfa_code(db, current_user, data.code)
    
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Enable MFA
    success, enable_message = await enable_mfa(db, current_user)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=enable_message
        )
    
    return {"message": enable_message}


@router.post("/auth/mfa/disable")
async def disable_mfa_endpoint(
    data: MFADisableRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Disable MFA
    
    - **password**: Current password for confirmation
    """
    # Verify current password
    if not verify_password(data.password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    # Check if MFA is enabled
    if not current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Two-factor authentication is not enabled"
        )
    
    # Disable MFA
    from services.mfa_service import disable_mfa
    
    success, message = await disable_mfa(db, current_user)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
    
    return {"message": message}


@router.post("/auth/mfa/resend")
@limiter.limit("3/minute")  # Max 3 resend requests per minute
async def resend_mfa_code(
    request: Request,
    data: MFALoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Resend MFA verification code during login
    
    - **email**: User's email address
    - **code**: Not required for resend (can be empty "000000")
    """
    from services.mfa_service import get_user_by_email, create_and_send_mfa_code, mask_email
    
    # Get user
    user = await get_user_by_email(db, data.email)
    
    if not user or not user.mfa_enabled:
        # Don't reveal if user exists
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request"
        )
    
    # Send new code
    success, message = await create_and_send_mfa_code(db, user)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
    
    return {
        "message": "New verification code sent",
        "email": mask_email(user.email),
    }


@router.post("/auth/mfa/verify-login")
@limiter.limit("5/minute")  # Max 5 MFA verify attempts per minute
async def verify_mfa_login(
    request: Request,
    data: MFALoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Complete MFA login by verifying code
    
    - **email**: User's email address
    - **code**: 6-digit verification code from email
    
    Returns JWT tokens and sets cookies on success
    """
    from services.mfa_service import get_user_by_email, verify_mfa_code
    
    # Get user
    user = await get_user_by_email(db, data.email)
    
    if not user or not user.mfa_enabled:
        # Don't reveal if user exists
        log_auth_failure(
            data.email,
            "mfa_login",
            "invalid_user",
            request.client.host if request.client else None
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid verification code"
        )
    
    # Verify the code
    valid, message = await verify_mfa_code(db, user, data.code)
    
    if not valid:
        log_auth_failure(
            data.email,
            "mfa_login",
            "invalid_code",
            request.client.host if request.client else None
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message
        )
    
    # Generate tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    # Log successful MFA login
    log_auth_success(user.id, "mfa_login", request.client.host if request.client else None)
    
    # Create response with cookies
    from fastapi.responses import JSONResponse
    is_production = os.getenv("ENVIRONMENT") == "production"
    
    response = JSONResponse(content={
        "message": "Login successful",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "is_verified": user.is_verified,
        },
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    })
    
    # Set httpOnly cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=is_production,
        samesite="strict",
        max_age=30 * 60,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=is_production,
        samesite="strict",
        max_age=7 * 24 * 60 * 60,
        path="/",
    )
    
    return response
