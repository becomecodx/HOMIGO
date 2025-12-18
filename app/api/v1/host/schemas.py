"""
Host API schemas.
"""
from datetime import date, datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID


# ============ HOST PROFILE SCHEMAS ============

class HostProfileCreate(BaseModel):
    """Schema for creating/updating host profile."""
    host_category: str = Field(..., description="owner, broker, company, future_room_partner, flatmate, known_of_flatmate, known_of_owner")
    company_name: Optional[str] = None
    company_registration_number: Optional[str] = None
    gst_number: Optional[str] = None
    bio: Optional[str] = None
    response_time_expectation: Optional[str] = Field(None, description="within_1_hour, within_24_hours, 1_to_3_days")
    preferred_tenant_types: Optional[str] = None


class HostProfileResponse(BaseModel):
    """Schema for host profile response."""
    host_profile_id: UUID
    user_id: UUID
    host_category: str
    company_name: Optional[str] = None
    company_registration_number: Optional[str] = None
    gst_number: Optional[str] = None
    bio: Optional[str] = None
    response_time_expectation: Optional[str] = None
    preferred_tenant_types: Optional[str] = None
    avg_rating: float = 0.0
    total_ratings: int = 0
    total_properties_listed: int = 0
    successful_matches: int = 0
    is_premium: bool = False
    premium_expires_at: Optional[date] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ HOST PREFERENCES SCHEMAS ============

class HostPreferenceCreate(BaseModel):
    """Schema for setting host preferences."""
    prefer_non_drinker: bool = False
    prefer_non_smoker: bool = False
    prefer_vegetarian: bool = False
    prefer_working_professional: bool = False
    prefer_student: bool = False
    preferred_gender: Optional[str] = Field(None, description="Male, Female, any")
    preferred_age_min: Optional[int] = Field(None, ge=18, le=100)
    preferred_age_max: Optional[int] = Field(None, ge=18, le=100)
    other_preferences: Optional[str] = None


class HostPreferenceResponse(BaseModel):
    """Schema for host preference response."""
    preference_id: UUID
    host_id: UUID
    prefer_non_drinker: bool = False
    prefer_non_smoker: bool = False
    prefer_vegetarian: bool = False
    prefer_working_professional: bool = False
    prefer_student: bool = False
    preferred_gender: Optional[str] = None
    preferred_age_min: Optional[int] = None
    preferred_age_max: Optional[int] = None
    other_preferences: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ API RESPONSE WRAPPERS ============

class HostProfileAPIResponse(BaseModel):
    """API response for host profile."""
    success: bool
    message: str
    data: Optional[HostProfileResponse] = None


class HostPreferenceAPIResponse(BaseModel):
    """API response for host preferences."""
    success: bool
    message: str
    data: Optional[HostPreferenceResponse] = None
