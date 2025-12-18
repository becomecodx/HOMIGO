"""
Matching API routes - Swipe, Match, and Interactions.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.api.v1.matching.schemas import (
    SwipeRequest, SwipeResponse, MatchResponse,
    ScheduleVisitRequest, CloseDealRequest
)
from app.core.dependencies import get_current_user
from app.database.postgres import get_db
from app.models.user import User
from app.models.interaction import SwipeAction, Match, SavedItem
from app.models.listing import PropertyListing
from app.models.tenant import TenantRequirement
from app.models.host import HostProfile


router = APIRouter(prefix="/matching", tags=["Matching"])


# ============ SWIPE ACTION ============

@router.post("/swipe", response_model=SwipeResponse)
async def swipe_action(
    request: SwipeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Record a swipe action (like, dislike, super_like, skip).
    
    If mutual like exists, creates a match.
    """
    if request.action not in ["like", "dislike", "super_like", "skip"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid action. Must be: like, dislike, super_like, or skip"
        )
    
    # Validate that exactly one target is provided
    if request.swiped_listing_id and request.swiped_requirement_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide either swiped_listing_id or swiped_requirement_id, not both"
        )
    
    if not request.swiped_listing_id and not request.swiped_requirement_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either swiped_listing_id or swiped_requirement_id"
        )
    
    # Check for existing swipe
    existing_query = select(SwipeAction).where(SwipeAction.swiper_id == current_user.user_id)
    
    if request.swiped_listing_id:
        existing_query = existing_query.where(SwipeAction.swiped_listing_id == request.swiped_listing_id)
    else:
        existing_query = existing_query.where(SwipeAction.swiped_requirement_id == request.swiped_requirement_id)
    
    existing_result = await db.execute(existing_query)
    existing_swipe = existing_result.scalar_one_or_none()
    
    if existing_swipe:
        # Update existing swipe
        existing_swipe.action = request.action
        await db.commit()
        
        return SwipeResponse(
            success=True,
            message="Swipe updated",
            data={
                "swipe_id": str(existing_swipe.swipe_id),
                "action": request.action,
                "is_match": False
            }
        )
    
    # Create new swipe
    swipe = SwipeAction(
        swiper_id=current_user.user_id,
        swiper_type=request.swiper_type,
        swiped_listing_id=request.swiped_listing_id,
        swiped_requirement_id=request.swiped_requirement_id,
        swiped_user_id=request.swiped_user_id,
        action=request.action
    )
    db.add(swipe)
    await db.commit()
    await db.refresh(swipe)
    
    # Check for mutual like (match)
    is_match = False
    match_data = None
    
    if request.action in ["like", "super_like"]:
        # Check if the other user also liked
        reverse_query = select(SwipeAction).where(
            SwipeAction.swiper_id == request.swiped_user_id,
            SwipeAction.swiped_user_id == current_user.user_id,
            SwipeAction.action.in_(["like", "super_like"])
        )
        reverse_result = await db.execute(reverse_query)
        reverse_swipe = reverse_result.scalar_one_or_none()
        
        if reverse_swipe:
            # Create match!
            is_match = True
            
            # Determine tenant and host
            if request.swiper_type == "tenant":
                tenant_id = current_user.user_id
                host_id = request.swiped_user_id
            else:
                tenant_id = request.swiped_user_id
                host_id = current_user.user_id
            
            # Check if match already exists
            existing_match_query = select(Match).where(
                Match.tenant_id == tenant_id,
                Match.host_id == host_id
            )
            if request.swiped_listing_id:
                existing_match_query = existing_match_query.where(Match.listing_id == request.swiped_listing_id)
            
            existing_match_result = await db.execute(existing_match_query)
            existing_match = existing_match_result.scalar_one_or_none()
            
            if not existing_match:
                match = Match(
                    tenant_id=tenant_id,
                    host_id=host_id,
                    listing_id=request.swiped_listing_id,
                    requirement_id=request.swiped_requirement_id,
                    match_status="active",
                    contact_shared=True,  # Auto-share on match
                    contact_shared_at=datetime.utcnow()
                )
                db.add(match)
                await db.commit()
                await db.refresh(match)
                
                match_data = {
                    "match_id": str(match.match_id),
                    "matched_at": match.matched_at.isoformat(),
                    "contact_shared": match.contact_shared
                }
    
    return SwipeResponse(
        success=True,
        message="It's a Match! 🎉" if is_match else "Action recorded",
        data={
            "swipe_id": str(swipe.swipe_id),
            "action": request.action,
            "is_match": is_match,
            "match": match_data
        }
    )


# ============ GET MATCHES ============

@router.get("/matches")
async def get_matches(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50)
):
    """Get all matches for current user."""
    query = select(Match).options(
        selectinload(Match.tenant),
        selectinload(Match.host),
        selectinload(Match.listing),
        selectinload(Match.requirement)
    ).where(
        or_(
            Match.tenant_id == current_user.user_id,
            Match.host_id == current_user.user_id
        )
    )
    
    if status_filter:
        query = query.where(Match.match_status == status_filter)
    
    query = query.order_by(Match.matched_at.desc())
    
    # Get total count
    count_query = select(Match).where(
        or_(
            Match.tenant_id == current_user.user_id,
            Match.host_id == current_user.user_id
        )
    )
    if status_filter:
        count_query = count_query.where(Match.match_status == status_filter)
    count_result = await db.execute(count_query)
    total_items = len(count_result.scalars().all())
    
    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    matches = result.scalars().all()
    
    total_pages = (total_items + limit - 1) // limit if total_items > 0 else 0
    
    # Format response
    matches_data = []
    for match in matches:
        # Determine matched user (the other party)
        if match.tenant_id == current_user.user_id:
            matched_user = match.host
            user_role = "tenant"
        else:
            matched_user = match.tenant
            user_role = "host"
        
        matched_user_data = None
        if matched_user:
            matched_user_data = {
                "user_id": str(matched_user.user_id),
                "full_name": matched_user.full_name,
                "profile_photo_url": matched_user.profile_photo_url,
                "user_type": matched_user.user_type
            }
        
        listing_data = None
        if match.listing:
            listing_data = {
                "listing_id": str(match.listing.listing_id),
                "title": match.listing.title,
                "rent_monthly": float(match.listing.rent_monthly),
                "locality": match.listing.locality
            }
        
        requirement_data = None
        if match.requirement:
            requirement_data = {
                "requirement_id": str(match.requirement.requirement_id),
                "title": match.requirement.title,
                "budget_min": float(match.requirement.budget_min),
                "budget_max": float(match.requirement.budget_max)
            }
        
        matches_data.append({
            "match_id": str(match.match_id),
            "my_role": user_role,
            "matched_user": matched_user_data,
            "listing": listing_data,
            "requirement": requirement_data,
            "compatibility_score": float(match.compatibility_score) if match.compatibility_score else None,
            "match_status": match.match_status,
            "contact_shared": match.contact_shared,
            "chat_enabled": match.chat_enabled,
            "visit_scheduled": match.visit_scheduled,
            "visit_date": match.visit_date.isoformat() if match.visit_date else None,
            "visit_status": match.visit_status,
            "deal_closed": match.deal_closed,
            "matched_at": match.matched_at.isoformat()
        })
    
    return {
        "success": True,
        "data": {
            "matches": matches_data,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_items": total_items,
                "items_per_page": limit
            }
        }
    }


# ============ GET MATCH DETAILS ============

@router.get("/matches/{match_id}")
async def get_match_details(
    match_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed match information."""
    result = await db.execute(
        select(Match).options(
            selectinload(Match.tenant),
            selectinload(Match.host),
            selectinload(Match.listing),
            selectinload(Match.requirement)
        ).where(
            Match.match_id == match_id,
            or_(
                Match.tenant_id == current_user.user_id,
                Match.host_id == current_user.user_id
            )
        )
    )
    match = result.scalar_one_or_none()
    
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    # Build response with full details
    tenant_data = None
    if match.tenant:
        tenant_data = {
            "user_id": str(match.tenant.user_id),
            "full_name": match.tenant.full_name,
            "email": match.tenant.email if match.contact_shared else None,
            "phone": match.tenant.phone if match.contact_shared else None,
            "profile_photo_url": match.tenant.profile_photo_url
        }
    
    host_data = None
    if match.host:
        host_data = {
            "user_id": str(match.host.user_id),
            "full_name": match.host.full_name,
            "email": match.host.email if match.contact_shared else None,
            "phone": match.host.phone if match.contact_shared else None,
            "profile_photo_url": match.host.profile_photo_url
        }
    
    return {
        "success": True,
        "data": {
            "match_id": str(match.match_id),
            "tenant": tenant_data,
            "host": host_data,
            "listing_id": str(match.listing_id) if match.listing_id else None,
            "requirement_id": str(match.requirement_id) if match.requirement_id else None,
            "compatibility_score": float(match.compatibility_score) if match.compatibility_score else None,
            "match_status": match.match_status,
            "contact_shared": match.contact_shared,
            "chat_enabled": match.chat_enabled,
            "visit_scheduled": match.visit_scheduled,
            "visit_date": match.visit_date.isoformat() if match.visit_date else None,
            "visit_status": match.visit_status,
            "deal_closed": match.deal_closed,
            "deal_amount": float(match.deal_amount) if match.deal_amount else None,
            "matched_at": match.matched_at.isoformat()
        }
    }


# ============ SCHEDULE VISIT ============

@router.post("/matches/{match_id}/schedule-visit")
async def schedule_visit(
    match_id: UUID,
    request: ScheduleVisitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Schedule a property visit."""
    result = await db.execute(
        select(Match).where(
            Match.match_id == match_id,
            or_(
                Match.tenant_id == current_user.user_id,
                Match.host_id == current_user.user_id
            )
        )
    )
    match = result.scalar_one_or_none()
    
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    
    match.visit_scheduled = True
    match.visit_date = request.visit_date
    match.visit_status = "scheduled"
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Visit scheduled successfully",
        "data": {
            "match_id": str(match_id),
            "visit_date": request.visit_date.isoformat(),
            "visit_status": "scheduled"
        }
    }


# ============ CLOSE DEAL ============

@router.post("/matches/{match_id}/close-deal")
async def close_deal(
    match_id: UUID,
    request: CloseDealRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark a deal as closed."""
    result = await db.execute(
        select(Match).where(
            Match.match_id == match_id,
            or_(
                Match.tenant_id == current_user.user_id,
                Match.host_id == current_user.user_id
            )
        )
    )
    match = result.scalar_one_or_none()
    
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    
    match.deal_closed = True
    match.deal_closed_at = datetime.utcnow()
    match.deal_amount = request.deal_amount
    match.match_status = "deal_closed"
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Deal closed successfully! 🎉",
        "data": {
            "match_id": str(match_id),
            "deal_amount": request.deal_amount,
            "deal_closed_at": match.deal_closed_at.isoformat()
        }
    }


# ============ UNMATCH ============

@router.post("/matches/{match_id}/unmatch")
async def unmatch(
    match_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Unmatch with a user."""
    result = await db.execute(
        select(Match).where(
            Match.match_id == match_id,
            or_(
                Match.tenant_id == current_user.user_id,
                Match.host_id == current_user.user_id
            )
        )
    )
    match = result.scalar_one_or_none()
    
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    
    match.match_status = "unmatched"
    match.unmatched_at = datetime.utcnow()
    
    await db.commit()
    
    return {"success": True, "message": "Unmatched successfully"}


# ============ SAVED ITEMS ============

@router.post("/save")
async def save_item(
    listing_id: Optional[UUID] = None,
    requirement_id: Optional[UUID] = None,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Save a listing or requirement for later."""
    if not listing_id and not requirement_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either listing_id or requirement_id"
        )
    
    if listing_id and requirement_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide only one: listing_id or requirement_id"
        )
    
    # Check if already saved
    existing_query = select(SavedItem).where(SavedItem.user_id == current_user.user_id)
    if listing_id:
        existing_query = existing_query.where(SavedItem.saved_listing_id == listing_id)
    else:
        existing_query = existing_query.where(SavedItem.saved_requirement_id == requirement_id)
    
    existing_result = await db.execute(existing_query)
    if existing_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already saved")
    
    saved = SavedItem(
        user_id=current_user.user_id,
        saved_listing_id=listing_id,
        saved_requirement_id=requirement_id,
        notes=notes
    )
    db.add(saved)
    await db.commit()
    await db.refresh(saved)
    
    return {
        "success": True,
        "message": "Item saved successfully",
        "data": {"saved_id": str(saved.saved_id)}
    }


@router.get("/saved")
async def get_saved_items(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50)
):
    """Get all saved items."""
    query = select(SavedItem).where(
        SavedItem.user_id == current_user.user_id
    ).order_by(SavedItem.created_at.desc())
    
    # Get total count
    count_result = await db.execute(query)
    total_items = len(count_result.scalars().all())
    
    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    saved_items = result.scalars().all()
    
    total_pages = (total_items + limit - 1) // limit if total_items > 0 else 0
    
    items_data = []
    for item in saved_items:
        items_data.append({
            "saved_id": str(item.saved_id),
            "saved_listing_id": str(item.saved_listing_id) if item.saved_listing_id else None,
            "saved_requirement_id": str(item.saved_requirement_id) if item.saved_requirement_id else None,
            "notes": item.notes,
            "created_at": item.created_at.isoformat()
        })
    
    return {
        "success": True,
        "data": {
            "saved_items": items_data,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_items": total_items,
                "items_per_page": limit
            }
        }
    }


@router.delete("/saved/{saved_id}")
async def unsave_item(
    saved_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a saved item."""
    result = await db.execute(
        select(SavedItem).where(
            SavedItem.saved_id == saved_id,
            SavedItem.user_id == current_user.user_id
        )
    )
    saved = result.scalar_one_or_none()
    
    if not saved:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved item not found")
    
    await db.delete(saved)
    await db.commit()
    
    return {"success": True, "message": "Item unsaved successfully"}
