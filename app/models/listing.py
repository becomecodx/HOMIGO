"""
Property Listing and Photo models.
"""
import uuid
from datetime import datetime
from typing import Optional, List, Dict

from sqlalchemy import String, Boolean, DateTime, Integer, Date, Text, CheckConstraint, Index, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base

class PropertyListing(Base):
    __tablename__ = "property_listings"

    listing_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    host_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    locality: Mapped[str] = mapped_column(String(255), nullable=False)
    tower_building_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    full_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    coordinates: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True) # Using JSONB for now
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    pincode: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    property_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    configuration: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    floor_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_floors: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    total_area_sqft: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    rentable_area_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    furnishing: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    has_wifi: Mapped[bool] = mapped_column(Boolean, default=False)
    has_fridge: Mapped[bool] = mapped_column(Boolean, default=False)
    has_ac: Mapped[bool] = mapped_column(Boolean, default=False)
    has_fans: Mapped[bool] = mapped_column(Boolean, default=True)
    has_washing_machine: Mapped[bool] = mapped_column(Boolean, default=False)
    has_tv: Mapped[bool] = mapped_column(Boolean, default=False)
    has_gas_connection: Mapped[bool] = mapped_column(Boolean, default=False)

    parking_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    wc_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    total_bathrooms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    water_supply_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    water_supply_hours: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    property_age_years: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    pets_allowed: Mapped[bool] = mapped_column(Boolean, default=False)
    non_veg_allowed: Mapped[bool] = mapped_column(Boolean, default=True)
    drinking_allowed: Mapped[bool] = mapped_column(Boolean, default=True)
    partying_allowed: Mapped[bool] = mapped_column(Boolean, default=True)
    guests_allowed: Mapped[bool] = mapped_column(Boolean, default=True)

    suitable_for: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    open_for_gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    open_for_occupation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    cook_available: Mapped[bool] = mapped_column(Boolean, default=False)
    maid_available: Mapped[bool] = mapped_column(Boolean, default=False)

    distance_to_metro: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    distance_to_train: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    distance_to_bus_stop: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    distance_to_airport: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    distance_to_gym: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    distance_to_hospital: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    distance_to_grocery: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    distance_to_mall: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    distance_to_movie_theatre: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    current_flatmates_count: Mapped[int] = mapped_column(Integer, default=0)
    flatmates_info: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    rent_monthly: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    deposit_amount: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    brokerage_amount: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), default=0)
    maintenance_monthly: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), default=0)
    electricity_charges: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    water_charges: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    wifi_charges: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), default=0)
    other_charges_onetime: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), default=0)
    other_charges_monthly: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), default=0)
    charges_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    possession_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    minimum_lease_months: Mapped[int] = mapped_column(Integer, default=11)

    other_highlights: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(String(20), server_default="draft")
    views_count: Mapped[int] = mapped_column(Integer, default=0)
    likes_count: Mapped[int] = mapped_column(Integer, default=0)
    contact_requests_count: Mapped[int] = mapped_column(Integer, default=0)

    photos_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    photos_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    photos_verified_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)

    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    premium_expires_at: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    payment_amount: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), default=499.00)
    payment_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    expires_at: Mapped[datetime] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    host: Mapped["HostProfile"] = relationship("HostProfile", back_populates="listings")
    photos: Mapped[List["PropertyPhoto"]] = relationship("PropertyPhoto", back_populates="listing", cascade="all, delete-orphan")
    matches: Mapped[List["Match"]] = relationship("Match", back_populates="listing", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("property_type IN ('apartment', 'house', 'pg', 'villa', 'independent_floor')", name="ck_listing_property_type"),
        Index("idx_listing_host_id", "host_id"),
        Index("idx_listing_status", "status"),
        Index("idx_listing_city", "city"),
        Index("idx_listing_rent", "rent_monthly"),
        Index("idx_listing_premium", "is_premium", "is_featured"),
        Index("idx_listing_possession", "possession_date"),
    )


class PropertyPhoto(Base):
    __tablename__ = "property_photos"

    photo_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("property_listings.listing_id", ondelete="CASCADE"), nullable=False)

    photo_url: Mapped[str] = mapped_column(Text, nullable=False)
    photo_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)

    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    caption: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    listing: Mapped["PropertyListing"] = relationship("PropertyListing", back_populates="photos")

    __table_args__ = (
        CheckConstraint("photo_type IN ('room', 'kitchen', 'bathroom', 'hall', 'balcony', 'building_exterior', 'street_view', 'other')", name="ck_photo_type"),
        Index("idx_property_photos_listing", "listing_id", "sequence_order"),
    )
