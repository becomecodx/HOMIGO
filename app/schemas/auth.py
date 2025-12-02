"""
Authentication request and response schemas.
Defines Pydantic models for API request/response validation.
"""

from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


class CaptchaGenerateResponse(BaseModel):
    """Response schema for CAPTCHA generation."""
    
    captcha_id: str = Field(..., description="Unique CAPTCHA identifier")
    captcha_image: str = Field(..., description="Base64-encoded CAPTCHA image")
    
    class Config:
        json_schema_extra = {
            "example": {
                "captcha_id": "123e4567-e89b-12d3-a456-426614174000",
                "captcha_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
            }
        }


class SignupRequest(BaseModel):
    """Request schema for user signup."""
    
    first_name: str = Field(..., min_length=2, max_length=50, description="User's first name")
    last_name: str = Field(..., min_length=2, max_length=50, description="User's last name")
    email: EmailStr = Field(..., description="User's email address")
    phone_number: str = Field(..., description="User's phone number (10-15 digits)")
    password: str = Field(..., min_length=8, description="User's password")
    captcha_id: str = Field(..., description="CAPTCHA identifier from /captcha endpoint")
    captcha_answer: str = Field(..., description="User's answer to CAPTCHA")
    
    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "Ram",
                "last_name": "Harish",
                "email": "ram@homigo.com",
                "phone_number": "9876543210",
                "password": "SecurePass@123",
                "captcha_id": "123e4567-e89b-12d3-a456-426614174000",
                "captcha_answer": "ABC123"
            }
        }


class LoginRequest(BaseModel):
    """Request schema for user login."""
    
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")
    captcha_id: str = Field(..., description="CAPTCHA identifier from /captcha endpoint")
    captcha_answer: str = Field(..., description="User's answer to CAPTCHA")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "ram@homigo.com",
                "password": "SecurePass@123",
                "captcha_id": "123e4567-e89b-12d3-a456-426614174000",
                "captcha_answer": "ABC123"
            }
        }


class TokenResponse(BaseModel):
    """Response schema for JWT token."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 86400
            }
        }


class UserResponse(BaseModel):
    """Response schema for user data (without sensitive information)."""
    
    id: str = Field(..., alias="_id", description="User ID")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    email: str = Field(..., description="User's email address")
    phone_number: str = Field(..., description="User's phone number")
    is_active: bool = Field(..., description="Whether the user account is active")
    is_verified: bool = Field(..., description="Whether the user email is verified")
    created_at: datetime = Field(..., description="Account creation timestamp")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "first_name": "Ram",
                "last_name": "Harish",
                "email": "ram@homigo.com",
                "phone_number": "9876543210",
                "is_active": True,
                "is_verified": False,
                "created_at": "2024-12-02T10:30:00"
            }
        }


class LoginResponse(BaseModel):
    """Response schema for login endpoint."""
    
    message: str = Field(default="Login successful", description="Response message")
    user: UserResponse = Field(..., description="User information")
    token: TokenResponse = Field(..., description="JWT token information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Login successful",
                "user": {
                    "id": "507f1f77bcf86cd799439011",
                    "first_name": "Ram",
                    "last_name": "Harish",
                    "email": "ram@homigo.com",
                    "phone_number": "9876543210",
                    "is_active": True,
                    "is_verified": False,
                    "created_at": "2024-12-02T10:30:00"
                },
                "token": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 86400
                }
            }
        }

