"""
Host API routes.
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.v1.host.schemas import (
    HostProfileCreate, HostProfileResponse, HostProfileAPIResponse,
    HostPreferenceCreate, HostPreferenceResponse, HostPreferenceAPIResponse
)
from app.core.dependencies import get_current_user
from app.database.postgres import get_db
from app.models.user import User
from app.models.host import HostProfile, HostPreference


router = APIRouter(prefix="/host", tags=["Host"])


# ============ HOST PROFILE ============

@router.put("/profile", response_model=HostProfileAPIResponse)
async def create_or_update_host_profile(
    request: HostProfileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create or update host profile.
    
    User must be registered as host or both.
    """
    if current_user.user_type not in ["host", "both"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must be registered as host to create host profile"
        )
    
    # Check if profile exists
    result = await db.execute(
        select(HostProfile).where(HostProfile.user_id == current_user.user_id)
    )
    profile = result.scalar_one_or_none()
    
    if profile:
        # Update existing
        for key, value in request.model_dump(exclude_unset=True).items():
            setattr(profile, key, value)
        profile.updated_at = datetime.utcnow()
    else:
        # Create new
        profile = HostProfile(
            user_id=current_user.user_id,
            **request.model_dump(exclude_unset=True)
        )
        db.add(profile)
    
    await db.commit()
    await db.refresh(profile)
    
    return HostProfileAPIResponse(
        success=True,
        message="Host profile updated",
        data=HostProfileResponse.model_validate(profile)
    )


@router.get("/profile", response_model=HostProfileAPIResponse)
async def get_host_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's host profile."""
    result = await db.execute(
        select(HostProfile).where(HostProfile.user_id == current_user.user_id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Host profile not found. Please create one first."
        )
    
    return HostProfileAPIResponse(
        success=True,
        message="Profile retrieved",
        data=HostProfileResponse.model_validate(profile)
    )


# ============ HOST PREFERENCES ============

@router.put("/preferences", response_model=HostPreferenceAPIResponse)
async def set_host_preferences(
    request: HostPreferenceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Set host tenant preferences."""
    if current_user.user_type not in ["host", "both"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only hosts can set preferences"
        )
    
    result = await db.execute(
        select(HostPreference).where(HostPreference.host_id == current_user.user_id)
    )
    preference = result.scalar_one_or_none()
    
    if preference:
        for key, value in request.model_dump(exclude_unset=True).items():
            setattr(preference, key, value)
        preference.updated_at = datetime.utcnow()
    else:
        preference = HostPreference(
            host_id=current_user.user_id,
            **request.model_dump(exclude_unset=True)
        )
        db.add(preference)
    
    await db.commit()
    await db.refresh(preference)
    
    return HostPreferenceAPIResponse(
        success=True,
        message="Preferences updated successfully",
        data=HostPreferenceResponse.model_validate(preference)
    )


@router.get("/preferences", response_model=HostPreferenceAPIResponse)
async def get_host_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get host tenant preferences."""
    result = await db.execute(
        select(HostPreference).where(HostPreference.host_id == current_user.user_id)
    )
    preference = result.scalar_one_or_none()
    
    if not preference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preferences not set yet"
        )
    
    return HostPreferenceAPIResponse(
        success=True,
        message="Preferences retrieved",
        data=HostPreferenceResponse.model_validate(preference)
    )
