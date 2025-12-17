"""
Matching, swiping and saved items models.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Boolean, DateTime, CheckConstraint, Index, ForeignKey, DECIMAL, UniqueConstraint, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base

class SwipeAction(Base):
    __tablename__ = "swipe_actions"

    swipe_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    swiper_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    swiper_type: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    swiped_listing_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("property_listings.listing_id", ondelete="CASCADE"), nullable=True)
    swiped_requirement_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("tenant_requirements.requirement_id", ondelete="CASCADE"), nullable=True)
    swiped_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    action: Mapped[str] = mapped_column(String(20), nullable=False)
    compatibility_score: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("action IN ('like', 'dislike', 'super_like', 'skip')", name="ck_swipe_action"),
        CheckConstraint("(swiped_listing_id IS NOT NULL AND swiped_requirement_id IS NULL) OR (swiped_listing_id IS NULL AND swiped_requirement_id IS NOT NULL)", name="ck_swipe_target"),
        UniqueConstraint("swiper_id", "swiped_listing_id", name="uq_swipe_listing"),
        UniqueConstraint("swiper_id", "swiped_requirement_id", name="uq_swipe_requirement"),
        Index("idx_swipe_swiper", "swiper_id"),
        Index("idx_swipe_listing", "swiped_listing_id"),
        Index("idx_swipe_requirement", "swiped_requirement_id"),
    )


class Match(Base):
    __tablename__ = "matches"

    match_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    host_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    requirement_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("tenant_requirements.requirement_id", ondelete="SET NULL"), nullable=True)
    listing_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("property_listings.listing_id", ondelete="SET NULL"), nullable=True)

    compatibility_score: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2), nullable=True)
    match_status: Mapped[str] = mapped_column(String(20), server_default="active")

    contact_shared: Mapped[bool] = mapped_column(Boolean, default=False)
    contact_shared_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    chat_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    visit_scheduled: Mapped[bool] = mapped_column(Boolean, default=False)
    visit_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    visit_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True) # 'scheduled', 'completed', 'cancelled', 'rescheduled'

    deal_closed: Mapped[bool] = mapped_column(Boolean, default=False)
    deal_closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deal_amount: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), nullable=True)

    matched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    unmatched_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    tenant: Mapped["User"] = relationship("User", foreign_keys=[tenant_id], back_populates="matches_as_tenant")
    host: Mapped["User"] = relationship("User", foreign_keys=[host_id], back_populates="matches_as_host")
    
    listing: Mapped["PropertyListing"] = relationship("PropertyListing", back_populates="matches")
    requirement: Mapped["TenantRequirement"] = relationship("TenantRequirement", back_populates="matches")
    
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="match", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("tenant_id", "host_id", "listing_id", name="uq_match_unique"),
        Index("idx_match_tenant", "tenant_id"),
        Index("idx_match_host", "host_id"),
        Index("idx_match_status", "match_status"),
        Index("idx_match_listing", "listing_id"),
        Index("idx_match_requirement", "requirement_id"),
    )


class SavedItem(Base):
    __tablename__ = "saved_items"

    saved_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    saved_listing_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("property_listings.listing_id", ondelete="CASCADE"), nullable=True)
    saved_requirement_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("tenant_requirements.requirement_id", ondelete="CASCADE"), nullable=True)

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("(saved_listing_id IS NOT NULL AND saved_requirement_id IS NULL) OR (saved_listing_id IS NULL AND saved_requirement_id IS NOT NULL)", name="ck_saved_target"),
        UniqueConstraint("user_id", "saved_listing_id", name="uq_saved_listing"),
        UniqueConstraint("user_id", "saved_requirement_id", name="uq_saved_requirement"),
        Index("idx_saved_user", "user_id"),
    )
