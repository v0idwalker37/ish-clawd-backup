"""
Pydantic models for authentication endpoints
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    name: str = Field(..., min_length=1, description="User's full name")
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        # Add more validation as needed (uppercase, numbers, etc.)
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123",
                "name": "John Doe",
            }
        }


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123",
            }
        }


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
            }
        }


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str = Field(..., description="Refresh token")
    
    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            }
        }


class UserProfile(BaseModel):
    """User profile response"""
    id: str
    email: str
    name: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "name": "John Doe",
                "is_active": True,
                "is_verified": False,
                "created_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-01T12:00:00",
            }
        }


class UserUpdate(BaseModel):
    """User profile update request"""
    name: Optional[str] = Field(None, min_length=1, description="User's full name")
    email: Optional[EmailStr] = Field(None, description="User email address")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Jane Doe",
                "email": "newemail@example.com",
            }
        }


class ForgotPasswordRequest(BaseModel):
    """Forgot password request"""
    email: EmailStr = Field(..., description="User email address")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
            }
        }


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operation completed successfully",
            }
        }


# MFA (Email OTP) Models

class MFAStatusResponse(BaseModel):
    """MFA status response"""
    mfa_enabled: bool
    email: str  # Masked email for display
    
    class Config:
        json_schema_extra = {
            "example": {
                "mfa_enabled": True,
                "email": "j***n@example.com",
            }
        }


class MFAEnableRequest(BaseModel):
    """Request to enable MFA - sends verification code"""
    password: str = Field(..., description="Current password for confirmation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "password": "CurrentPassword123",
            }
        }


class MFAVerifyRequest(BaseModel):
    """Verify MFA code"""
    code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")
    
    @validator('code')
    def validate_code(cls, v):
        if not v.isdigit():
            raise ValueError('Code must contain only digits')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "123456",
            }
        }


class MFADisableRequest(BaseModel):
    """Request to disable MFA"""
    password: str = Field(..., description="Current password for confirmation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "password": "CurrentPassword123",
            }
        }


class MFALoginRequest(BaseModel):
    """Complete MFA login with code"""
    email: EmailStr = Field(..., description="User email")
    code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")
    
    @validator('code')
    def validate_code(cls, v):
        if not v.isdigit():
            raise ValueError('Code must contain only digits')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "code": "123456",
            }
        }


class MFARequiredResponse(BaseModel):
    """Response when MFA is required"""
    mfa_required: bool = True
    email: str  # Masked email
    message: str = "Please check your email for the verification code"
    
    class Config:
        json_schema_extra = {
            "example": {
                "mfa_required": True,
                "email": "j***n@example.com",
                "message": "Please check your email for the verification code",
            }
        }


# =============================================================================
# GDPR Data Subject Rights Models (Art. 16, 18, 21)
# =============================================================================


class RectificationRequest(BaseModel):
    """
    GDPR Art. 16 — Right to Rectification
    Allows users to update their personal data.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Updated full name")
    email: Optional[EmailStr] = Field(None, description="Updated email (triggers re-verification)")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Jane Doe",
                "email": "newemail@example.com",
            }
        }


class PrivacyPreferences(BaseModel):
    """
    GDPR Art. 21 — Right to Object
    Privacy and data-processing preferences.
    """
    analytics_opt_out: bool = Field(
        False,
        description="Opt out of service-improvement analytics"
    )
    marketing_emails_opt_out: bool = Field(
        False,
        description="Opt out of non-essential email communications"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "analytics_opt_out": True,
                "marketing_emails_opt_out": False,
            }
        }


class RestrictionResponse(BaseModel):
    """Response for restriction/unrestriction actions"""
    message: str
    is_restricted: bool

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Processing of your data has been restricted.",
                "is_restricted": True,
            }
        }
