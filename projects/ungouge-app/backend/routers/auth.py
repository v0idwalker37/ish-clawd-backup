"""
Authentication router - handles user registration, login, and profile management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
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
        
        # For development, log the token (REMOVE IN PRODUCTION)
        from services.logger import logger
        logger.info(
            "email_verification_sent",
            extra={
                "user_id": user_id,
                "token": verification_token,  # REMOVE IN PRODUCTION
                "note": "Check logs for verification token (dev only)"
            }
        )
    except Exception as e:
        await db.rollback()
        from services.logger import log_error
        log_error("email_verification_error", str(e), {"user_id": user_id})
    
    # Log successful registration
    log_auth_success(user_id, "register", request.client.host if request.client else None)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/auth/login", response_model=TokenResponse)
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
    
    # Generate tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    # Log successful login
    log_auth_success(user.id, "login", request.client.host if request.client else None)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh access token using refresh token
    
    - **refresh_token**: Valid refresh token
    
    Returns new JWT access and refresh tokens
    """
    # Verify refresh token
    payload = verify_token(token_data.refresh_token, token_type="refresh")
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
    access_token = create_access_token(data={"sub": user_id})
    refresh_token = create_refresh_token(data={"sub": user_id})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


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
            
            # For development, log the token (REMOVE IN PRODUCTION)
            from services.logger import logger
            logger.info(
                "password_reset_requested",
                extra={
                    "user_id": user.id,
                    "token": reset_token,  # REMOVE IN PRODUCTION
                    "note": "Check logs for reset token (dev only)"
                }
            )
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
    req: Request,
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
        
        # For development, log the token
        from services.logger import logger
        logger.info(
            "email_verification_resent",
            extra={
                "user_id": current_user.id,
                "token": verification_token,  # REMOVE IN PRODUCTION
            }
        )
        
        return MessageResponse(message="Verification email has been sent")
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email",
        )


@router.post("/auth/logout", response_model=MessageResponse)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: User = Depends(get_current_user),
):
    """
    Logout - revoke current access token
    
    Adds the token to a blacklist so it cannot be used again.
    The token will be blacklisted until its natural expiry.
    
    Note: Refresh tokens are not automatically invalidated.
    For full logout, client should discard refresh token as well.
    """
    token = credentials.credentials
    
    # Calculate remaining validity (token expiry - now)
    try:
        from jose import jwt
        from services.auth import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp_timestamp = payload.get("exp")
        
        if exp_timestamp:
            from datetime import datetime
            exp_datetime = datetime.utcfromtimestamp(exp_timestamp)
            remaining_seconds = int((exp_datetime - datetime.utcnow()).total_seconds())
            
            # Only blacklist if token hasn't already expired
            if remaining_seconds > 0:
                TokenBlacklist.add(token, remaining_seconds)
        
        # Log logout
        from services.logger import log_auth_success
        log_auth_success(current_user.id, "logout", None)
        
        return MessageResponse(message="Logged out successfully")
    except Exception as e:
        # Even if blacklisting fails, return success (token will expire naturally)
        from services.logger import log_error
        log_error("logout_error", str(e), {"user_id": current_user.id})
        return MessageResponse(message="Logged out successfully")
