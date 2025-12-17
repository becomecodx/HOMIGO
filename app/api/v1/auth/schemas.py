"""
Pydantic schemas for authentication endpoints.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


# ============================================================================
# Request Schemas
# ============================================================================

class SignupRequest(BaseModel):
    """Request schema for user signup."""
    firebase_id: str = Field(..., description="Firebase UID from Firebase Authentication")
    full_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    user_type: str = Field(..., description="User type: 'tenant', 'host', or 'both'")
    profile_photo_url: Optional[str] = None
    device_token: Optional[str] = None
    fcm_token: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "firebase_id": "firebase_uid_123456",
                "full_name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1234567890",
                "user_type": "tenant",
                "profile_photo_url": "https://example.com/photo.jpg",
                "fcm_token": "fcm_token_here"
            }
        }


class LoginRequest(BaseModel):
    """Request schema for Firebase token login."""
    firebase_token: str = Field(..., description="Firebase ID token from client")
    device_token: Optional[str] = None
    fcm_token: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "firebase_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6...",
                "fcm_token": "fcm_token_here"
            }
        }


class UpdateProfileRequest(BaseModel):
    """Request schema for updating user profile."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    profile_photo_url: Optional[str] = None
    device_token: Optional[str] = None
    fcm_token: Optional[str] = None


# ============================================================================
# Response Schemas
# ============================================================================

class UserResponse(BaseModel):
    """Response schema for user data."""
    user_id: UUID
    full_name: str
    email: str
    phone: str
    user_type: str
    profile_photo_url: Optional[str] = None
    account_status: str
    created_at: datetime
    last_login_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SignupResponse(BaseModel):
    """Response schema for signup endpoint."""
    success: bool = True
    message: str = "User registered successfully"
    user: UserResponse


class LoginResponse(BaseModel):
    """Response schema for login endpoint."""
    success: bool = True
    message: str = "Login successful"
    user: UserResponse
    access_token: Optional[str] = None  # Optional: if you want to issue your own JWT


class MessageResponse(BaseModel):
    """Generic message response."""
    success: bool
    message: str
