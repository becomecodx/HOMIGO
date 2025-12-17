"""Pydantic models for Firebase auth endpoints."""
from pydantic import BaseModel, Field
from typing import Optional


class ProjectVerifyRequest(BaseModel):
    """Request body for verifying Firebase project metadata."""
    project_name: str = Field(..., description="Public project name")
    project_id: str = Field(..., description="Firebase project id")
    project_number: str = Field(..., description="Firebase project number")
    environment_type: Optional[str] = Field(None, description="Environment type")
    public_facing_name: Optional[str] = Field(None, description="Public facing name")


class ProjectVerifyResponse(BaseModel):
    success: bool
    message: str
    matched: bool
    project_name: Optional[str] = None
    project_id: Optional[str] = None
    project_number: Optional[str] = None


class FirebaseSignupRequest(BaseModel):
    email: str
    password: str


class FirebaseSignupResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[str] = None


class FirebaseLoginRequest(BaseModel):
    email: str
    password: str


class FirebaseLoginResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None
