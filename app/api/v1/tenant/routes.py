"""
Tenant API routes.
"""
from datetime import datetime, date, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.v1.tenant.schemas import (
    TenantProfileCreate, TenantProfileResponse, TenantProfileAPIResponse,
    TenantPriorityCreate, TenantPriorityResponse, TenantPriorityAPIResponse,
    TenantRequirementCreate, TenantRequirementUpdate, TenantRequirementResponse,
    TenantRequirementAPIResponse, TenantRequirementListResponse
)
from app.core.dependencies import get_current_user
from app.database.postgres import get_db
from app.models.user import User
from app.models.tenant import TenantProfile, TenantPriority, TenantRequirement


router = APIRouter(prefix="/tenant", tags=["Tenant"])


# ============ TENANT PROFILE ============

@router.put("/profile", response_model=TenantProfileAPIResponse)
async def create_or_update_tenant_profile(
    request: TenantProfileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create or update tenant profile.
    
    User must be registered as tenant or both.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    if current_user.user_type not in ["tenant", "both"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must be registered as tenant to create tenant profile"
        )
    
    try:
        # Check if profile exists
        result = await db.execute(
            select(TenantProfile).where(TenantProfile.user_id == current_user.user_id)
        )
        profile = result.scalar_one_or_none()
        
        if profile:
            # Update existing
            for key, value in request.model_dump(exclude_unset=True).items():
                setattr(profile, key, value)
            profile.updated_at = datetime.utcnow()
        else:
            # Create new - ensure profile_completeness is set initially
            profile = TenantProfile(
                user_id=current_user.user_id,
                profile_completeness=0,  # Set explicitly to avoid NOT NULL issues
                **request.model_dump(exclude_unset=True)
            )
            db.add(profile)
        
        # Calculate and set profile completeness
        profile.profile_completeness = calculate_profile_completeness(profile)
        
        await db.commit()
        await db.refresh(profile)
        
        return TenantProfileAPIResponse(
            success=True,
            message="Tenant profile updated",
            data=TenantProfileResponse.model_validate(profile)
        )
    except Exception as e:
        logger.error(f"Error creating/updating tenant profile: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create/update profile: {str(e)}"
        )


@router.get("/profile", response_model=TenantProfileAPIResponse)
async def get_tenant_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's tenant profile."""
    result = await db.execute(
        select(TenantProfile).where(TenantProfile.user_id == current_user.user_id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant profile not found. Please create one first."
        )
    
    return TenantProfileAPIResponse(
        success=True,
        message="Profile retrieved",
        data=TenantProfileResponse.model_validate(profile)
    )


def calculate_profile_completeness(profile: TenantProfile) -> int:
    """Calculate profile completeness percentage."""
    fields = [
        profile.occupation_type,
        profile.job_title or profile.educational_institution,
        profile.smoking,
        profile.drinking,
        profile.food_preference,
        profile.bio,
        profile.hobbies,
        profile.languages_spoken
    ]
    filled = sum(1 for f in fields if f)
    return int((filled / len(fields)) * 100)


# ============ TENANT PRIORITIES ============

@router.put("/priorities", response_model=TenantPriorityAPIResponse)
async def set_tenant_priorities(
    request: TenantPriorityCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Set tenant search priorities (1 = highest priority)."""
    result = await db.execute(
        select(TenantPriority).where(TenantPriority.user_id == current_user.user_id)
    )
    priority = result.scalar_one_or_none()
    
    if priority:
        for key, value in request.model_dump(exclude_unset=True).items():
            setattr(priority, key, value)
        priority.updated_at = datetime.utcnow()
    else:
        priority = TenantPriority(
            user_id=current_user.user_id,
            **request.model_dump(exclude_unset=True)
        )
        db.add(priority)
    
    await db.commit()
    await db.refresh(priority)
    
    return TenantPriorityAPIResponse(
        success=True,
        message="Priorities updated successfully",
        data=TenantPriorityResponse.model_validate(priority)
    )


@router.get("/priorities", response_model=TenantPriorityAPIResponse)
async def get_tenant_priorities(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get tenant search priorities."""
    result = await db.execute(
        select(TenantPriority).where(TenantPriority.user_id == current_user.user_id)
    )
    priority = result.scalar_one_or_none()
    
    if not priority:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Priorities not set yet"
        )
    
    return TenantPriorityAPIResponse(
        success=True,
        message="Priorities retrieved",
        data=TenantPriorityResponse.model_validate(priority)
    )


# ============ TENANT REQUIREMENTS ============

@router.post("/requirements", response_model=TenantRequirementAPIResponse, status_code=status.HTTP_201_CREATED)
async def create_requirement(
    request: TenantRequirementCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new tenant requirement/post.
    
    Requirement will be in 'draft' status until payment is completed.
    """
    if current_user.user_type not in ["tenant", "both"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only tenants can post requirements"
        )
    
    # Set expiry date (30 days from now)
    expires_at = date.today() + timedelta(days=30)
    
    # Convert localities list to JSONB format
    preferred_localities = None
    if request.preferred_localities:
        preferred_localities = {"localities": request.preferred_localities}
    
    requirement = TenantRequirement(
        user_id=current_user.user_id,
        title=request.title,
        description=request.description,
        budget_min=request.budget_min,
        budget_max=request.budget_max,
        preferred_localities=preferred_localities,
        preferred_coordinates=request.preferred_coordinates,
        occupancy=request.occupancy,
        property_type=request.property_type,
        furnishing=request.furnishing,
        possession_date=request.possession_date,
        lease_duration_months=request.lease_duration_months,
        gender_preference=request.gender_preference,
        flatmate_occupation_preference=request.flatmate_occupation_preference,
        want_non_smoker=request.want_non_smoker,
        want_non_drinker=request.want_non_drinker,
        want_vegetarian=request.want_vegetarian,
        want_non_party=request.want_non_party,
        other_preferences=request.other_preferences,
        contact_visibility=request.contact_visibility,
        status="draft",
        expires_at=expires_at,
        payment_status="pending"
    )
    
    db.add(requirement)
    await db.commit()
    await db.refresh(requirement)
    
    return TenantRequirementAPIResponse(
        success=True,
        message="Requirement created successfully",
        data=TenantRequirementResponse.model_validate(requirement)
    )


@router.get("/requirements/my", response_model=TenantRequirementListResponse)
async def get_my_requirements(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50)
):
    """Get all requirements posted by current user."""
    query = select(TenantRequirement).where(TenantRequirement.user_id == current_user.user_id)
    
    if status_filter:
        query = query.where(TenantRequirement.status == status_filter)
    
    query = query.order_by(TenantRequirement.created_at.desc())
    
    # Get total count
    count_result = await db.execute(
        select(TenantRequirement).where(TenantRequirement.user_id == current_user.user_id)
    )
    total_items = len(count_result.scalars().all())
    
    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    requirements = result.scalars().all()
    
    total_pages = (total_items + limit - 1) // limit
    
    return TenantRequirementListResponse(
        success=True,
        data={
            "requirements": [TenantRequirementResponse.model_validate(r) for r in requirements],
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_items": total_items,
                "items_per_page": limit
            }
        }
    )


@router.get("/requirements/{requirement_id}", response_model=TenantRequirementAPIResponse)
async def get_requirement(
    requirement_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get requirement by ID."""
    result = await db.execute(
        select(TenantRequirement).where(TenantRequirement.requirement_id == requirement_id)
    )
    requirement = result.scalar_one_or_none()
    
    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found"
        )
    
    # Increment view count if not owner
    if requirement.user_id != current_user.user_id:
        requirement.views_count += 1
        await db.commit()
    
    return TenantRequirementAPIResponse(
        success=True,
        message="Requirement retrieved",
        data=TenantRequirementResponse.model_validate(requirement)
    )


@router.put("/requirements/{requirement_id}", response_model=TenantRequirementAPIResponse)
async def update_requirement(
    requirement_id: UUID,
    request: TenantRequirementUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a requirement (owner only)."""
    result = await db.execute(
        select(TenantRequirement).where(
            TenantRequirement.requirement_id == requirement_id,
            TenantRequirement.user_id == current_user.user_id
        )
    )
    requirement = result.scalar_one_or_none()
    
    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found or not owned by you"
        )
    
    update_data = request.model_dump(exclude_unset=True)
    
    # Handle localities conversion
    if "preferred_localities" in update_data and update_data["preferred_localities"]:
        update_data["preferred_localities"] = {"localities": update_data["preferred_localities"]}
    
    for key, value in update_data.items():
        setattr(requirement, key, value)
    
    requirement.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(requirement)
    
    return TenantRequirementAPIResponse(
        success=True,
        message="Requirement updated successfully",
        data=TenantRequirementResponse.model_validate(requirement)
    )


@router.delete("/requirements/{requirement_id}")
async def delete_requirement(
    requirement_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a requirement (owner only)."""
    result = await db.execute(
        select(TenantRequirement).where(
            TenantRequirement.requirement_id == requirement_id,
            TenantRequirement.user_id == current_user.user_id
        )
    )
    requirement = result.scalar_one_or_none()
    
    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found or not owned by you"
        )
    
    await db.delete(requirement)
    await db.commit()
    
    return {"success": True, "message": "Requirement deleted successfully"}


@router.post("/requirements/{requirement_id}/activate")
async def activate_requirement(
    requirement_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Activate a requirement (simulates payment completion).
    In production, this would be called after payment webhook.
    """
    result = await db.execute(
        select(TenantRequirement).where(
            TenantRequirement.requirement_id == requirement_id,
            TenantRequirement.user_id == current_user.user_id
        )
    )
    requirement = result.scalar_one_or_none()
    
    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found"
        )
    
    requirement.status = "active"
    requirement.payment_status = "paid"
    requirement.expires_at = date.today() + timedelta(days=30)
    requirement.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(requirement)
    
    return {
        "success": True,
        "message": "Requirement activated successfully",
        "data": TenantRequirementResponse.model_validate(requirement)
    }
