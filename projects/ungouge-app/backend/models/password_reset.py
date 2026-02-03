"""
Password reset models
"""
from pydantic import BaseModel, EmailStr, Field

class PasswordResetRequest(BaseModel):
    """Request password reset"""
    email: EmailStr = Field(..., description="Email address")

class PasswordResetVerify(BaseModel):
    """Verify reset token and set new password"""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")

class PasswordResetResponse(BaseModel):
    """Response for password reset request"""
    message: str
    expires_in_minutes: int = 15
