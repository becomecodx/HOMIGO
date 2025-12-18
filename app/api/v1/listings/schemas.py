"""
Listings API schemas.
"""
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID


# ============ PROPERTY LISTING SCHEMAS ============

class ListingAmenities(BaseModel):
    """Amenities schema."""
    has_wifi: bool = False
    has_fridge: bool = False
    has_ac: bool = False
    has_fans: bool = True
    has_washing_machine: bool = False
    has_tv: bool = False
    has_gas_connection: bool = False


class ListingRestrictions(BaseModel):
    """Restrictions schema."""
    pets_allowed: bool = False
    non_veg_allowed: bool = True
    drinking_allowed: bool = True
    partying_allowed: bool = True
    guests_allowed: bool = True


class ListingServices(BaseModel):
    """Services schema."""
    cook_available: bool = False
    maid_available: bool = False


class ListingDistances(BaseModel):
    """Distances to places schema."""
    distance_to_metro: Optional[int] = None
    distance_to_train: Optional[int] = None
    distance_to_bus_stop: Optional[int] = None
    distance_to_airport: Optional[int] = None
    distance_to_gym: Optional[int] = None
    distance_to_hospital: Optional[int] = None
    distance_to_grocery: Optional[int] = None
    distance_to_mall: Optional[int] = None
    distance_to_movie_theatre: Optional[int] = None


class ListingFinancial(BaseModel):
    """Financial details schema."""
    rent_monthly: float = Field(..., gt=0)
    deposit_amount: float = Field(..., ge=0)
    brokerage_amount: float = 0
    maintenance_monthly: float = 0
    electricity_charges: Optional[str] = None
    water_charges: Optional[str] = None
    wifi_charges: float = 0
    other_charges_onetime: float = 0
    other_charges_monthly: float = 0
    charges_notes: Optional[str] = None


class PropertyListingCreate(BaseModel):
    """Schema for creating property listing."""
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    
    # Location
    locality: str = Field(..., max_length=255)
    tower_building_name: Optional[str] = None
    full_address: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None  # {"latitude": 19.05, "longitude": 72.82}
    city: str = Field(..., max_length=100)
    state: str = Field(..., max_length=100)
    pincode: Optional[str] = None
    
    # Property Details
    property_type: Optional[str] = Field(None, description="apartment, house, pg, villa, independent_floor")
    configuration: Optional[str] = Field(None, description="1bhk, 2bhk, 3bhk, 1rk, etc.")
    floor_number: Optional[int] = None
    total_floors: Optional[int] = None
    total_area_sqft: Optional[int] = None
    rentable_area_type: Optional[str] = None
    furnishing: Optional[str] = Field(None, description="furnished, semi_furnished, unfurnished")
    
    # Amenities
    amenities: Optional[ListingAmenities] = None
    
    # Parking & Bathroom
    parking_type: Optional[str] = None
    wc_type: Optional[str] = None
    total_bathrooms: Optional[int] = None
    
    # Water
    water_supply_type: Optional[str] = None
    water_supply_hours: Optional[str] = None
    property_age_years: Optional[int] = None
    
    # Restrictions
    restrictions: Optional[ListingRestrictions] = None
    
    # Tenant preferences
    suitable_for: Optional[str] = None
    open_for_gender: Optional[str] = None
    open_for_occupation: Optional[str] = None
    
    # Services
    services: Optional[ListingServices] = None
    
    # Distances
    distances: Optional[ListingDistances] = None
    
    # Flatmates
    current_flatmates_count: int = 0
    flatmates_info: Optional[str] = None
    
    # Financial
    financial: ListingFinancial
    
    # Dates
    possession_date: date
    minimum_lease_months: int = 11
    
    # Other
    other_highlights: Optional[str] = None


class PropertyListingUpdate(BaseModel):
    """Schema for updating property listing."""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    locality: Optional[str] = None
    tower_building_name: Optional[str] = None
    full_address: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    property_type: Optional[str] = None
    configuration: Optional[str] = None
    floor_number: Optional[int] = None
    total_floors: Optional[int] = None
    total_area_sqft: Optional[int] = None
    furnishing: Optional[str] = None
    amenities: Optional[ListingAmenities] = None
    restrictions: Optional[ListingRestrictions] = None
    services: Optional[ListingServices] = None
    distances: Optional[ListingDistances] = None
    financial: Optional[ListingFinancial] = None
    possession_date: Optional[date] = None
    minimum_lease_months: Optional[int] = None
    other_highlights: Optional[str] = None


class PropertyPhotoResponse(BaseModel):
    """Schema for property photo response."""
    photo_id: UUID
    photo_url: str
    photo_type: Optional[str] = None
    sequence_order: int
    is_primary: bool = False
    caption: Optional[str] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True


class PropertyListingResponse(BaseModel):
    """Schema for property listing response."""
    listing_id: UUID
    host_id: UUID
    title: str
    description: Optional[str] = None
    
    # Location
    locality: str
    tower_building_name: Optional[str] = None
    full_address: Optional[str] = None
    coordinates: Optional[Dict] = None
    city: str
    state: str
    pincode: Optional[str] = None
    
    # Property Details
    property_type: Optional[str] = None
    configuration: Optional[str] = None
    floor_number: Optional[int] = None
    total_floors: Optional[int] = None
    total_area_sqft: Optional[int] = None
    rentable_area_type: Optional[str] = None
    furnishing: Optional[str] = None
    
    # Amenities
    has_wifi: bool = False
    has_fridge: bool = False
    has_ac: bool = False
    has_fans: bool = True
    has_washing_machine: bool = False
    has_tv: bool = False
    has_gas_connection: bool = False
    
    # Parking & Bathroom
    parking_type: Optional[str] = None
    wc_type: Optional[str] = None
    total_bathrooms: Optional[int] = None
    
    # Water
    water_supply_type: Optional[str] = None
    water_supply_hours: Optional[str] = None
    property_age_years: Optional[int] = None
    
    # Restrictions
    pets_allowed: bool = False
    non_veg_allowed: bool = True
    drinking_allowed: bool = True
    partying_allowed: bool = True
    guests_allowed: bool = True
    
    # Tenant preferences
    suitable_for: Optional[str] = None
    open_for_gender: Optional[str] = None
    open_for_occupation: Optional[str] = None
    
    # Services
    cook_available: bool = False
    maid_available: bool = False
    
    # Flatmates
    current_flatmates_count: int = 0
    flatmates_info: Optional[str] = None
    
    # Financial
    rent_monthly: float
    deposit_amount: float
    brokerage_amount: float = 0
    maintenance_monthly: float = 0
    
    # Dates
    possession_date: date
    minimum_lease_months: int = 11
    
    # Status & Stats
    status: str
    views_count: int = 0
    likes_count: int = 0
    contact_requests_count: int = 0
    is_premium: bool = False
    is_featured: bool = False
    
    # Photos
    photos: Optional[List[PropertyPhotoResponse]] = None
    
    # Timestamps
    expires_at: date
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ListingStatusUpdate(BaseModel):
    """Schema for updating listing status."""
    status: str = Field(..., description="active, paused, rented")


class MarkRentedRequest(BaseModel):
    """Schema for marking listing as rented."""
    rented_to_match_id: Optional[UUID] = None
    rent_amount: Optional[float] = None
    notes: Optional[str] = None


# ============ API RESPONSE WRAPPERS ============

class ListingAPIResponse(BaseModel):
    """API response for single listing."""
    success: bool
    message: str
    data: Optional[PropertyListingResponse] = None


class ListingCreateResponse(BaseModel):
    """API response for listing creation."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class ListingListResponse(BaseModel):
    """API response for list of listings."""
    success: bool
    data: Dict[str, Any]  # Contains listings list and pagination
