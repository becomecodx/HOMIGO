"""
Feed API routes - Discovery for tenants and hosts.
"""
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.core.dependencies import get_current_user
from app.database.postgres import get_db
from app.models.user import User
from app.models.listing import PropertyListing, PropertyPhoto
from app.models.tenant import TenantRequirement
from app.models.host import HostProfile


router = APIRouter(prefix="/feed", tags=["Feed & Discovery"])


@router.get("/listings")
async def get_listings_feed(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    budget_min: Optional[float] = Query(None),
    budget_max: Optional[float] = Query(None),
    localities: Optional[str] = Query(None, description="Comma-separated localities"),
    occupancy: Optional[str] = Query(None),
    property_type: Optional[str] = Query(None, description="Comma-separated types"),
    furnishing: Optional[str] = Query(None, description="Comma-separated furnishing types"),
    possession_from: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    gender_preference: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    sort: str = Query("newest", description="newest, price_low, price_high")
):
    """
    Get property listings feed for tenants.
    
    Returns active listings matching the filter criteria.
    """
    query = select(PropertyListing).options(
        selectinload(PropertyListing.photos),
        selectinload(PropertyListing.host)
    ).where(PropertyListing.status == "active")
    
    # Apply filters
    if budget_min:
        query = query.where(PropertyListing.rent_monthly >= budget_min)
    if budget_max:
        query = query.where(PropertyListing.rent_monthly <= budget_max)
    
    if city:
        query = query.where(PropertyListing.city.ilike(f"%{city}%"))
    
    if localities:
        locality_list = [l.strip() for l in localities.split(",")]
        locality_conditions = [PropertyListing.locality.ilike(f"%{loc}%") for loc in locality_list]
        query = query.where(or_(*locality_conditions))
    
    if property_type:
        types = [t.strip() for t in property_type.split(",")]
        query = query.where(PropertyListing.property_type.in_(types))
    
    if furnishing:
        furnish_types = [f.strip() for f in furnishing.split(",")]
        query = query.where(PropertyListing.furnishing.in_(furnish_types))
    
    if gender_preference and gender_preference != "any":
        query = query.where(
            or_(
                PropertyListing.open_for_gender == gender_preference,
                PropertyListing.open_for_gender == "any",
                PropertyListing.open_for_gender.is_(None)
            )
        )
    
    # Sorting
    if sort == "price_low":
        query = query.order_by(PropertyListing.rent_monthly.asc())
    elif sort == "price_high":
        query = query.order_by(PropertyListing.rent_monthly.desc())
    else:  # newest
        query = query.order_by(PropertyListing.created_at.desc())
    
    # Get total count
    count_query = select(PropertyListing).where(PropertyListing.status == "active")
    count_result = await db.execute(count_query)
    total_items = len(count_result.scalars().all())
    
    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    listings = result.scalars().all()
    
    total_pages = (total_items + limit - 1) // limit if total_items > 0 else 0
    
    # Format response
    listings_data = []
    for listing in listings:
        # Get primary photo
        primary_photo = None
        if listing.photos:
            primary = next((p for p in listing.photos if p.is_primary), None)
            primary_photo = primary.photo_url if primary else (listing.photos[0].photo_url if listing.photos else None)
        
        # Get host user info (listing.host is now User object)
        host_info = None
        if listing.host:
            host_info = {
                "user_id": str(listing.host.user_id),
                "full_name": listing.host.full_name,
                "profile_photo_url": listing.host.profile_photo_url
            }
        
        listings_data.append({
            "listing_id": str(listing.listing_id),
            "title": listing.title,
            "rent_monthly": float(listing.rent_monthly),
            "deposit_amount": float(listing.deposit_amount),
            "locality": listing.locality,
            "city": listing.city,
            "configuration": listing.configuration,
            "furnishing": listing.furnishing,
            "property_type": listing.property_type,
            "primary_photo": primary_photo,
            "photos_count": len(listing.photos) if listing.photos else 0,
            "host": host_info,
            "views_count": listing.views_count,
            "likes_count": listing.likes_count,
            "is_premium": listing.is_premium,
            "is_featured": listing.is_featured,
            "created_at": listing.created_at.isoformat(),
            "possession_date": listing.possession_date.isoformat()
        })
    
    return {
        "success": True,
        "data": {
            "listings": listings_data,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_items": total_items,
                "items_per_page": limit,
                "has_more": page < total_pages
            }
        }
    }


@router.get("/requirements")
async def get_requirements_feed(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    budget_min: Optional[float] = Query(None),
    budget_max: Optional[float] = Query(None),
    localities: Optional[str] = Query(None, description="Comma-separated localities"),
    occupancy: Optional[str] = Query(None),
    property_type: Optional[str] = Query(None),
    gender_preference: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    sort: str = Query("newest", description="newest, budget_low, budget_high")
):
    """
    Get tenant requirements feed for hosts.
    
    Returns active requirements matching the filter criteria.
    """
    query = select(TenantRequirement).options(
        selectinload(TenantRequirement.user)
    ).where(TenantRequirement.status == "active")
    
    # Apply filters
    if budget_min:
        query = query.where(TenantRequirement.budget_max >= budget_min)
    if budget_max:
        query = query.where(TenantRequirement.budget_min <= budget_max)
    
    if occupancy:
        query = query.where(TenantRequirement.occupancy == occupancy)
    
    if property_type:
        query = query.where(TenantRequirement.property_type == property_type)
    
    if gender_preference and gender_preference != "any":
        query = query.where(
            or_(
                TenantRequirement.gender_preference == gender_preference,
                TenantRequirement.gender_preference == "any",
                TenantRequirement.gender_preference.is_(None)
            )
        )
    
    # Sorting
    if sort == "budget_low":
        query = query.order_by(TenantRequirement.budget_min.asc())
    elif sort == "budget_high":
        query = query.order_by(TenantRequirement.budget_max.desc())
    else:  # newest
        query = query.order_by(TenantRequirement.created_at.desc())
    
    # Get total count
    count_query = select(TenantRequirement).where(TenantRequirement.status == "active")
    count_result = await db.execute(count_query)
    total_items = len(count_result.scalars().all())
    
    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    requirements = result.scalars().all()
    
    total_pages = (total_items + limit - 1) // limit if total_items > 0 else 0
    
    # Format response
    requirements_data = []
    for req in requirements:
        # Get localities from JSONB
        localities_list = []
        if req.preferred_localities and isinstance(req.preferred_localities, dict):
            localities_list = req.preferred_localities.get("localities", [])
        
        user_info = None
        if req.user:
            user_info = {
                "user_id": str(req.user.user_id),
                "full_name": req.user.full_name,
                "profile_photo_url": req.user.profile_photo_url
            }
        
        requirements_data.append({
            "requirement_id": str(req.requirement_id),
            "user": user_info,
            "title": req.title,
            "description": req.description,
            "budget_min": float(req.budget_min),
            "budget_max": float(req.budget_max),
            "preferred_localities": localities_list,
            "occupancy": req.occupancy,
            "property_type": req.property_type,
            "furnishing": req.furnishing,
            "possession_date": req.possession_date.isoformat(),
            "gender_preference": req.gender_preference,
            "preferences": {
                "want_non_smoker": req.want_non_smoker,
                "want_non_drinker": req.want_non_drinker,
                "want_vegetarian": req.want_vegetarian,
                "want_non_party": req.want_non_party
            },
            "views_count": req.views_count,
            "likes_count": req.likes_count,
            "is_premium": req.is_premium,
            "created_at": req.created_at.isoformat(),
            "expires_at": req.expires_at.isoformat()
        })
    
    return {
        "success": True,
        "data": {
            "requirements": requirements_data,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_items": total_items,
                "items_per_page": limit,
                "has_more": page < total_pages
            }
        }
    }


@router.get("/search/listings")
async def search_listings(
    q: str = Query(..., min_length=2, description="Search query"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50)
):
    """
    Search listings by text query.
    
    Searches in title, description, locality, and city.
    """
    search_term = f"%{q}%"
    
    query = select(PropertyListing).options(
        selectinload(PropertyListing.photos)
    ).where(
        and_(
            PropertyListing.status == "active",
            or_(
                PropertyListing.title.ilike(search_term),
                PropertyListing.description.ilike(search_term),
                PropertyListing.locality.ilike(search_term),
                PropertyListing.city.ilike(search_term)
            )
        )
    ).order_by(PropertyListing.created_at.desc())
    
    # Get total count
    count_result = await db.execute(query)
    total_items = len(count_result.scalars().all())
    
    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    listings = result.scalars().all()
    
    total_pages = (total_items + limit - 1) // limit if total_items > 0 else 0
    
    listings_data = []
    for listing in listings:
        primary_photo = None
        if listing.photos:
            primary = next((p for p in listing.photos if p.is_primary), None)
            primary_photo = primary.photo_url if primary else (listing.photos[0].photo_url if listing.photos else None)
        
        listings_data.append({
            "listing_id": str(listing.listing_id),
            "title": listing.title,
            "rent_monthly": float(listing.rent_monthly),
            "locality": listing.locality,
            "city": listing.city,
            "configuration": listing.configuration,
            "primary_photo": primary_photo,
            "is_premium": listing.is_premium
        })
    
    return {
        "success": True,
        "data": {
            "listings": listings_data,
            "query": q,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_items": total_items,
                "items_per_page": limit
            }
        }
    }
