"""
Matching API schemas.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID


class SwipeRequest(BaseModel):
    """Schema for swipe action."""
    swiper_type: str = Field(..., description="tenant or host")
    action: str = Field(..., description="like, dislike, super_like, skip")
    swiped_listing_id: Optional[UUID] = None  # If tenant swiping on listing
    swiped_requirement_id: Optional[UUID] = None  # If host swiping on requirement
    swiped_user_id: UUID


class SwipeResponse(BaseModel):
    """Schema for swipe response."""
    success: bool
    message: str
    data: Dict[str, Any]


class MatchResponse(BaseModel):
    """Schema for match details."""
    match_id: UUID
    tenant_id: UUID
    host_id: UUID
    requirement_id: Optional[UUID] = None
    listing_id: Optional[UUID] = None
    compatibility_score: Optional[float] = None
    match_status: str
    contact_shared: bool = False
    chat_enabled: bool = True
    visit_scheduled: bool = False
    deal_closed: bool = False
    matched_at: datetime

    class Config:
        from_attributes = True


class ScheduleVisitRequest(BaseModel):
    """Schema for scheduling a visit."""
    visit_date: datetime
    notes: Optional[str] = None


class CloseDealRequest(BaseModel):
    """Schema for closing a deal."""
    deal_amount: Optional[float] = None
    notes: Optional[str] = None
