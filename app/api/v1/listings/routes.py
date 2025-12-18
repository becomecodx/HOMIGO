"""
Listings API routes.
"""
from datetime import datetime, date, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.v1.listings.schemas import (
    PropertyListingCreate, PropertyListingUpdate, PropertyListingResponse,
    ListingAPIResponse, ListingCreateResponse, ListingListResponse,
    ListingStatusUpdate, MarkRentedRequest, PropertyPhotoResponse
)
from app.core.dependencies import get_current_user
from app.database.postgres import get_db
from app.models.user import User
from app.models.host import HostProfile
from app.models.listing import PropertyListing, PropertyPhoto


router = APIRouter(prefix="/listings", tags=["Listings"])


# ============ CREATE LISTING ============

@router.post("", response_model=ListingCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_listing(
    request: PropertyListingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new property listing.
    
    Host profile must exist. Listing starts in 'draft' status.
    """
    if current_user.user_type not in ["host", "both"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only hosts can create listings"
        )
    
    # Get host profile
    result = await db.execute(
        select(HostProfile).where(HostProfile.user_id == current_user.user_id)
    )
    host_profile = result.scalar_one_or_none()
    
    if not host_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please create host profile first"
        )
    
    # Set expiry date (30 days from now)
    expires_at = date.today() + timedelta(days=30)
    
    # Flatten amenities, restrictions, services, distances
    # Note: host_id references users.user_id in the database
    listing_data = {
        "host_id": current_user.user_id,
        "title": request.title,
        "description": request.description,
        "locality": request.locality,
        "tower_building_name": request.tower_building_name,
        "full_address": request.full_address,
        "coordinates": request.coordinates,
        "city": request.city,
        "state": request.state,
        "pincode": request.pincode,
        "property_type": request.property_type,
        "configuration": request.configuration,
        "floor_number": request.floor_number,
        "total_floors": request.total_floors,
        "total_area_sqft": request.total_area_sqft,
        "rentable_area_type": request.rentable_area_type,
        "furnishing": request.furnishing,
        "parking_type": request.parking_type,
        "wc_type": request.wc_type,
        "total_bathrooms": request.total_bathrooms,
        "water_supply_type": request.water_supply_type,
        "water_supply_hours": request.water_supply_hours,
        "property_age_years": request.property_age_years,
        "suitable_for": request.suitable_for,
        "open_for_gender": request.open_for_gender,
        "open_for_occupation": request.open_for_occupation,
        "current_flatmates_count": request.current_flatmates_count,
        "flatmates_info": request.flatmates_info,
        "possession_date": request.possession_date,
        "minimum_lease_months": request.minimum_lease_months,
        "other_highlights": request.other_highlights,
        "status": "draft",
        "expires_at": expires_at,
        "payment_status": "pending"
    }
    
    # Add amenities
    if request.amenities:
        for key, value in request.amenities.model_dump().items():
            listing_data[key] = value
    
    # Add restrictions
    if request.restrictions:
        for key, value in request.restrictions.model_dump().items():
            listing_data[key] = value
    
    # Add services
    if request.services:
        for key, value in request.services.model_dump().items():
            listing_data[key] = value
    
    # Add distances
    if request.distances:
        for key, value in request.distances.model_dump().items():
            if value is not None:
                listing_data[key] = value
    
    # Add financial
    for key, value in request.financial.model_dump().items():
        if key in ["rent_monthly", "deposit_amount", "brokerage_amount", 
                   "maintenance_monthly", "electricity_charges", "water_charges",
                   "wifi_charges", "other_charges_onetime", "other_charges_monthly", "charges_notes"]:
            listing_data[key] = value
    
    listing = PropertyListing(**listing_data)
    db.add(listing)
    
    # Update host stats
    host_profile.total_properties_listed += 1
    
    await db.commit()
    await db.refresh(listing)
    
    return ListingCreateResponse(
        success=True,
        message="Listing created successfully",
        data={
            "listing_id": str(listing.listing_id),
            "status": listing.status,
            "payment_required": True,
            "payment_amount": 499.00,
            "next_steps": [
                "Upload minimum 3 photos in sequence",
                "Complete payment to publish"
            ]
        }
    )


# ============ GET MY LISTINGS ============

@router.get("/my", response_model=ListingListResponse)
async def get_my_listings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50)
):
    """Get all listings created by current user."""
    # Get host profile
    result = await db.execute(
        select(HostProfile).where(HostProfile.user_id == current_user.user_id)
    )
    host_profile = result.scalar_one_or_none()
    
    if not host_profile:
        return ListingListResponse(
            success=True,
            data={
                "listings": [],
                "pagination": {
                    "current_page": page,
                    "total_pages": 0,
                    "total_items": 0,
                    "items_per_page": limit
                }
            }
        )
    
    query = select(PropertyListing).options(
        selectinload(PropertyListing.photos)
    ).where(PropertyListing.host_id == current_user.user_id)
    
    if status_filter:
        query = query.where(PropertyListing.status == status_filter)
    
    query = query.order_by(PropertyListing.created_at.desc())
    
    # Get total count
    count_query = select(PropertyListing).where(PropertyListing.host_id == current_user.user_id)
    if status_filter:
        count_query = count_query.where(PropertyListing.status == status_filter)
    count_result = await db.execute(count_query)
    total_items = len(count_result.scalars().all())
    
    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    listings = result.scalars().all()
    
    total_pages = (total_items + limit - 1) // limit if total_items > 0 else 0
    
    listings_data = []
    for listing in listings:
        listing_dict = PropertyListingResponse.model_validate(listing).model_dump()
        listing_dict["photos"] = [PropertyPhotoResponse.model_validate(p).model_dump() for p in listing.photos] if listing.photos else []
        listings_data.append(listing_dict)
    
    return ListingListResponse(
        success=True,
        data={
            "listings": listings_data,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_items": total_items,
                "items_per_page": limit
            }
        }
    )


# ============ GET LISTING BY ID ============

@router.get("/{listing_id}", response_model=ListingAPIResponse)
async def get_listing(
    listing_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get listing by ID."""
    result = await db.execute(
        select(PropertyListing).options(
            selectinload(PropertyListing.photos)
        ).where(PropertyListing.listing_id == listing_id)
    )
    listing = result.scalar_one_or_none()
    
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )
    
    # Increment view count if not owner
    host_result = await db.execute(
        select(HostProfile).where(HostProfile.host_profile_id == listing.host_id)
    )
    host = host_result.scalar_one_or_none()
    
    if host and host.user_id != current_user.user_id:
        listing.views_count += 1
        await db.commit()
    
    listing_response = PropertyListingResponse.model_validate(listing)
    listing_response.photos = [PropertyPhotoResponse.model_validate(p) for p in listing.photos] if listing.photos else []
    
    return ListingAPIResponse(
        success=True,
        message="Listing retrieved",
        data=listing_response
    )


# ============ UPDATE LISTING ============

@router.put("/{listing_id}", response_model=ListingAPIResponse)
async def update_listing(
    listing_id: UUID,
    request: PropertyListingUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a listing (owner only)."""
    # Get host profile
    result = await db.execute(
        select(HostProfile).where(HostProfile.user_id == current_user.user_id)
    )
    host_profile = result.scalar_one_or_none()
    
    if not host_profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Host profile not found"
        )
    
    # Get listing
    result = await db.execute(
        select(PropertyListing).where(
            PropertyListing.listing_id == listing_id,
            PropertyListing.host_id == current_user.user_id
        )
    )
    listing = result.scalar_one_or_none()
    
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found or not owned by you"
        )
    
    # Update fields
    update_data = request.model_dump(exclude_unset=True)
    
    # Handle nested objects
    if "amenities" in update_data and update_data["amenities"]:
        for key, value in update_data["amenities"].items():
            setattr(listing, key, value)
        del update_data["amenities"]
    
    if "restrictions" in update_data and update_data["restrictions"]:
        for key, value in update_data["restrictions"].items():
            setattr(listing, key, value)
        del update_data["restrictions"]
    
    if "services" in update_data and update_data["services"]:
        for key, value in update_data["services"].items():
            setattr(listing, key, value)
        del update_data["services"]
    
    if "distances" in update_data and update_data["distances"]:
        for key, value in update_data["distances"].items():
            if value is not None:
                setattr(listing, key, value)
        del update_data["distances"]
    
    if "financial" in update_data and update_data["financial"]:
        for key, value in update_data["financial"].items():
            setattr(listing, key, value)
        del update_data["financial"]
    
    # Update remaining fields
    for key, value in update_data.items():
        setattr(listing, key, value)
    
    listing.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(listing)
    
    return ListingAPIResponse(
        success=True,
        message="Listing updated successfully",
        data=PropertyListingResponse.model_validate(listing)
    )


# ============ UPDATE LISTING STATUS ============

@router.patch("/{listing_id}/status")
async def update_listing_status(
    listing_id: UUID,
    request: ListingStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Pause or resume a listing."""
    # Get host profile
    result = await db.execute(
        select(HostProfile).where(HostProfile.user_id == current_user.user_id)
    )
    host_profile = result.scalar_one_or_none()
    
    if not host_profile:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Host profile not found")
    
    result = await db.execute(
        select(PropertyListing).where(
            PropertyListing.listing_id == listing_id,
            PropertyListing.host_id == current_user.user_id
        )
    )
    listing = result.scalar_one_or_none()
    
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    
    if request.status not in ["active", "paused"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
    
    listing.status = request.status
    listing.updated_at = datetime.utcnow()
    await db.commit()
    
    return {"success": True, "message": "Listing status updated", "data": {"listing_id": str(listing_id), "status": request.status}}


# ============ PUBLISH LISTING ============

@router.post("/{listing_id}/publish")
async def publish_listing(
    listing_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Publish a listing (activates after payment simulation)."""
    result = await db.execute(
        select(HostProfile).where(HostProfile.user_id == current_user.user_id)
    )
    host_profile = result.scalar_one_or_none()
    
    if not host_profile:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Host profile not found")
    
    result = await db.execute(
        select(PropertyListing).options(
            selectinload(PropertyListing.photos)
        ).where(
            PropertyListing.listing_id == listing_id,
            PropertyListing.host_id == current_user.user_id
        )
    )
    listing = result.scalar_one_or_none()
    
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    
    # Check minimum photos (for now, skip this check or make it optional)
    # if len(listing.photos) < 3:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Minimum 3 photos required")
    
    listing.status = "active"
    listing.payment_status = "paid"
    listing.published_at = datetime.utcnow()
    listing.expires_at = date.today() + timedelta(days=30)
    listing.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Listing published successfully",
        "data": {
            "listing_id": str(listing_id),
            "status": "active",
            "published_at": listing.published_at.isoformat(),
            "expires_at": listing.expires_at.isoformat()
        }
    }


# ============ MARK AS RENTED ============

@router.post("/{listing_id}/mark-rented")
async def mark_as_rented(
    listing_id: UUID,
    request: MarkRentedRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark listing as rented."""
    result = await db.execute(
        select(HostProfile).where(HostProfile.user_id == current_user.user_id)
    )
    host_profile = result.scalar_one_or_none()
    
    if not host_profile:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Host profile not found")
    
    result = await db.execute(
        select(PropertyListing).where(
            PropertyListing.listing_id == listing_id,
            PropertyListing.host_id == current_user.user_id
        )
    )
    listing = result.scalar_one_or_none()
    
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    
    listing.status = "rented"
    listing.updated_at = datetime.utcnow()
    
    # Update host stats
    host_profile.successful_matches += 1
    
    await db.commit()
    
    return {"success": True, "message": "Listing marked as rented"}


# ============ DELETE LISTING ============

@router.delete("/{listing_id}")
async def delete_listing(
    listing_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a listing."""
    result = await db.execute(
        select(HostProfile).where(HostProfile.user_id == current_user.user_id)
    )
    host_profile = result.scalar_one_or_none()
    
    if not host_profile:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Host profile not found")
    
    result = await db.execute(
        select(PropertyListing).where(
            PropertyListing.listing_id == listing_id,
            PropertyListing.host_id == current_user.user_id
        )
    )
    listing = result.scalar_one_or_none()
    
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    
    await db.delete(listing)
    host_profile.total_properties_listed = max(0, host_profile.total_properties_listed - 1)
    await db.commit()
    
    return {"success": True, "message": "Listing deleted successfully"}
