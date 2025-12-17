"""
Rating and Report models.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Boolean, DateTime, Text, CheckConstraint, Index, ForeignKey, DECIMAL, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base

class Rating(Base):
    __tablename__ = "ratings"

    rating_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    rater_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    rated_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    match_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("matches.match_id", ondelete="SET NULL"), nullable=True)
    listing_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("property_listings.listing_id", ondelete="SET NULL"), nullable=True)

    rating_value: Mapped[Optional[float]] = mapped_column(DECIMAL(2, 1), nullable=True)

    review_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    review_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    communication_rating: Mapped[Optional[float]] = mapped_column(DECIMAL(2, 1), nullable=True)
    accuracy_rating: Mapped[Optional[float]] = mapped_column(DECIMAL(2, 1), nullable=True)
    responsiveness_rating: Mapped[Optional[float]] = mapped_column(DECIMAL(2, 1), nullable=True)

    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True)
    is_reported: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("rating_value >= 1.0 AND rating_value <= 5.0", name="ck_rating_value"),
        UniqueConstraint("rater_id", "rated_user_id", "match_id", name="uq_rating_unique"),
        Index("idx_rating_rated_user", "rated_user_id"),
        Index("idx_rating_match", "match_id"),
    )


class Report(Base):
    __tablename__ = "reports"

    report_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reporter_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    reported_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True)
    reported_listing_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("property_listings.listing_id", ondelete="CASCADE"), nullable=True)
    reported_requirement_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("tenant_requirements.requirement_id", ondelete="CASCADE"), nullable=True)
    reported_message_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("messages.message_id", ondelete="CASCADE"), nullable=True)
    
    # Adding fields typically needed for reports even if not in snippet, safe guesses based on context
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), server_default="pending")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_report_reporter", "reporter_id"),
    )
