"""
Host Profile and Preference models.
"""
import uuid
from datetime import datetime, date
from typing import Optional, List

from sqlalchemy import String, Boolean, DateTime, Integer, Date, Text, CheckConstraint, Index, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base

class HostProfile(Base):
    __tablename__ = "host_profiles"

    host_profile_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, unique=True)

    host_category: Mapped[str] = mapped_column(String(50), nullable=False)
    company_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    company_registration_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    gst_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    response_time_expectation: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    preferred_tenant_types: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    avg_rating: Mapped[float] = mapped_column(DECIMAL(3, 2), default=0.00)
    total_ratings: Mapped[int] = mapped_column(Integer, default=0)
    total_properties_listed: Mapped[int] = mapped_column(Integer, default=0)
    successful_matches: Mapped[int] = mapped_column(Integer, default=0)

    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    premium_expires_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="host_profile")

    __table_args__ = (
        CheckConstraint("host_category IN ('owner', 'broker', 'company', 'future_room_partner', 'flatmate', 'known_of_flatmate', 'known_of_owner')", name="ck_host_category"),
        Index("idx_host_profile_user_id", "user_id"),
        Index("idx_host_profile_category", "host_category"),
    )


class HostPreference(Base):
    __tablename__ = "host_preferences"

    preference_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    host_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, unique=True)

    prefer_non_drinker: Mapped[bool] = mapped_column(Boolean, default=False)
    prefer_non_smoker: Mapped[bool] = mapped_column(Boolean, default=False)
    prefer_vegetarian: Mapped[bool] = mapped_column(Boolean, default=False)
    prefer_working_professional: Mapped[bool] = mapped_column(Boolean, default=False)
    prefer_student: Mapped[bool] = mapped_column(Boolean, default=False)
    
    preferred_gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    preferred_age_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    preferred_age_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    other_preferences: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
