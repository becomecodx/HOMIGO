"""
Tenant API schemas.
"""
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID


# ============ TENANT PROFILE SCHEMAS ============

class TenantProfileCreate(BaseModel):
    """Schema for creating/updating tenant profile."""
    occupation_type: Optional[str] = Field(None, description="working_professional, student, self_employed, etc.")
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    educational_institution: Optional[str] = None
    smoking: Optional[str] = Field(None, description="yes, no, occasionally")
    drinking: Optional[str] = Field(None, description="yes, no, occasionally")
    food_preference: Optional[str] = Field(None, description="veg, non_veg, both, vegan, eggetarian")
    lifestyle_notes: Optional[str] = None
    bio: Optional[str] = None
    hobbies: Optional[str] = None
    languages_spoken: Optional[str] = None


class TenantProfileResponse(BaseModel):
    """Schema for tenant profile response."""
    tenant_profile_id: UUID
    user_id: UUID
    occupation_type: Optional[str] = None
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    educational_institution: Optional[str] = None
    smoking: Optional[str] = None
    drinking: Optional[str] = None
    food_preference: Optional[str] = None
    lifestyle_notes: Optional[str] = None
    bio: Optional[str] = None
    hobbies: Optional[str] = None
    languages_spoken: Optional[str] = None
    profile_completeness: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ TENANT PRIORITIES SCHEMAS ============

class TenantPriorityCreate(BaseModel):
    """Schema for setting tenant priorities."""
    budget_priority: Optional[int] = Field(None, ge=1, le=8)
    occupancy_priority: Optional[int] = Field(None, ge=1, le=8)
    location_priority: Optional[int] = Field(None, ge=1, le=8)
    possession_priority: Optional[int] = Field(None, ge=1, le=8)
    gender_priority: Optional[int] = Field(None, ge=1, le=8)
    property_type_priority: Optional[int] = Field(None, ge=1, le=8)
    lifestyle_priority: Optional[int] = Field(None, ge=1, le=8)
    furnishing_priority: Optional[int] = Field(None, ge=1, le=8)


class TenantPriorityResponse(BaseModel):
    """Schema for tenant priority response."""
    priority_id: UUID
    user_id: UUID
    budget_priority: Optional[int] = None
    occupancy_priority: Optional[int] = None
    location_priority: Optional[int] = None
    possession_priority: Optional[int] = None
    gender_priority: Optional[int] = None
    property_type_priority: Optional[int] = None
    lifestyle_priority: Optional[int] = None
    furnishing_priority: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ TENANT REQUIREMENTS SCHEMAS ============

class TenantRequirementCreate(BaseModel):
    """Schema for creating tenant requirement."""
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    budget_min: float = Field(..., gt=0)
    budget_max: float = Field(..., gt=0)
    preferred_localities: Optional[List[str]] = None
    preferred_coordinates: Optional[Dict[str, float]] = None  # {"latitude": 19.05, "longitude": 72.82}
    occupancy: Optional[str] = Field(None, description="single, shared, any")
    property_type: Optional[str] = Field(None, description="apartment, house, pg, villa, independent_floor")
    furnishing: Optional[str] = Field(None, description="furnished, semi_furnished, unfurnished")
    possession_date: date
    lease_duration_months: Optional[int] = None
    gender_preference: Optional[str] = Field(None, description="male, female, any")
    flatmate_occupation_preference: Optional[str] = None
    want_non_smoker: bool = False
    want_non_drinker: bool = False
    want_vegetarian: bool = False
    want_non_party: bool = False
    other_preferences: Optional[str] = None
    contact_visibility: str = Field(default="verified_hosts_only")


class TenantRequirementUpdate(BaseModel):
    """Schema for updating tenant requirement."""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    budget_min: Optional[float] = Field(None, gt=0)
    budget_max: Optional[float] = Field(None, gt=0)
    preferred_localities: Optional[List[str]] = None
    preferred_coordinates: Optional[Dict[str, float]] = None
    occupancy: Optional[str] = None
    property_type: Optional[str] = None
    furnishing: Optional[str] = None
    possession_date: Optional[date] = None
    lease_duration_months: Optional[int] = None
    gender_preference: Optional[str] = None
    flatmate_occupation_preference: Optional[str] = None
    want_non_smoker: Optional[bool] = None
    want_non_drinker: Optional[bool] = None
    want_vegetarian: Optional[bool] = None
    want_non_party: Optional[bool] = None
    other_preferences: Optional[str] = None
    contact_visibility: Optional[str] = None


class TenantRequirementResponse(BaseModel):
    """Schema for tenant requirement response."""
    requirement_id: UUID
    user_id: UUID
    title: str
    description: Optional[str] = None
    budget_min: float
    budget_max: float
    preferred_localities: Optional[Dict] = None
    preferred_coordinates: Optional[Dict] = None
    occupancy: Optional[str] = None
    property_type: Optional[str] = None
    furnishing: Optional[str] = None
    possession_date: date
    lease_duration_months: Optional[int] = None
    gender_preference: Optional[str] = None
    flatmate_occupation_preference: Optional[str] = None
    want_non_smoker: bool = False
    want_non_drinker: bool = False
    want_vegetarian: bool = False
    want_non_party: bool = False
    other_preferences: Optional[str] = None
    contact_visibility: str
    status: str
    expires_at: date
    views_count: int = 0
    likes_count: int = 0
    is_premium: bool = False
    premium_expires_at: Optional[date] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ API RESPONSE WRAPPERS ============

class TenantProfileAPIResponse(BaseModel):
    """API response for tenant profile."""
    success: bool
    message: str
    data: Optional[TenantProfileResponse] = None


class TenantPriorityAPIResponse(BaseModel):
    """API response for tenant priorities."""
    success: bool
    message: str
    data: Optional[TenantPriorityResponse] = None


class TenantRequirementAPIResponse(BaseModel):
    """API response for single requirement."""
    success: bool
    message: str
    data: Optional[TenantRequirementResponse] = None


class PaginationInfo(BaseModel):
    """Pagination info."""
    current_page: int
    total_pages: int
    total_items: int
    items_per_page: int


class TenantRequirementListResponse(BaseModel):
    """API response for list of requirements."""
    success: bool
    data: Dict[str, Any]  # Contains requirements list and pagination
