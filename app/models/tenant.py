"""
Tenant Profile, Requirements and Priorities models.
"""
import uuid
from datetime import datetime, date
from typing import Optional, List, Dict

from sqlalchemy import String, Boolean, DateTime, Integer, Date, Text, CheckConstraint, Index, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base

class TenantProfile(Base):
    __tablename__ = "tenant_profiles"

    tenant_profile_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, unique=True)

    occupation_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    job_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    company_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    educational_institution: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    smoking: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    drinking: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    food_preference: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    lifestyle_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hobbies: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    languages_spoken: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    profile_completeness: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="tenant_profile")

    __table_args__ = (
        CheckConstraint("occupation_type IN ('working_professional', 'student', 'self_employed', 'actor', 'actress', 'freelancer', 'other')", name="ck_tenant_occupation"),
        CheckConstraint("smoking IN ('yes', 'no', 'occasionally')", name="ck_tenant_smoking"),
        CheckConstraint("drinking IN ('yes', 'no', 'occasionally')", name="ck_tenant_drinking"),
        CheckConstraint("food_preference IN ('veg', 'non_veg', 'both', 'vegan', 'eggetarian')", name="ck_tenant_food"),
        Index("idx_tenant_profile_user_id", "user_id"),
    )


class TenantRequirement(Base):
    __tablename__ = "tenant_requirements"

    requirement_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    budget_min: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    budget_max: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)

    preferred_localities: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)
    # preferred_coordinates GEOGRAPHY(POINT) - using JSONB for now as per previous plan to avoid GeoAlchemy dependency if not needed yet
    preferred_coordinates: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)

    occupancy: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    property_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    furnishing: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    possession_date: Mapped[date] = mapped_column(Date, nullable=False)
    lease_duration_months: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    gender_preference: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    flatmate_occupation_preference: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    want_non_smoker: Mapped[bool] = mapped_column(Boolean, default=False)
    want_non_drinker: Mapped[bool] = mapped_column(Boolean, default=False)
    want_vegetarian: Mapped[bool] = mapped_column(Boolean, default=False)
    want_non_party: Mapped[bool] = mapped_column(Boolean, default=False)
    other_preferences: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    contact_visibility: Mapped[str] = mapped_column(String(50), server_default="verified_hosts_only")
    status: Mapped[str] = mapped_column(String(20), server_default="active")
    
    expires_at: Mapped[date] = mapped_column(Date, nullable=False)
    views_count: Mapped[int] = mapped_column(Integer, default=0)
    likes_count: Mapped[int] = mapped_column(Integer, default=0)

    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    premium_expires_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    payment_amount: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), default=250.00)
    payment_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="tenant_requirements")
    
    # Interactions
    matches: Mapped[List["Match"]] = relationship("Match", back_populates="requirement", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("status IN ('draft', 'active', 'paused', 'expired', 'fulfilled', 'deleted')", name="ck_tenant_req_status"),
        Index("idx_tenant_req_user_id", "user_id"),
        Index("idx_tenant_req_status", "status"),
        Index("idx_tenant_req_budget", "budget_min", "budget_max"),
        Index("idx_tenant_req_possession", "possession_date"),
        Index("idx_tenant_req_premium", "is_premium", "expires_at"),
    )


class TenantPriority(Base):
    __tablename__ = "tenant_priorities"

    priority_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, unique=True)

    budget_priority: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    occupancy_priority: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    location_priority: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    possession_priority: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gender_priority: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    property_type_priority: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    lifestyle_priority: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    furnishing_priority: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
