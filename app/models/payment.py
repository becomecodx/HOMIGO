"""
Payment and Subscription models.
"""
import uuid
from datetime import datetime, date
from typing import Optional, Dict

from sqlalchemy import String, Boolean, DateTime, Integer, Date, Text, CheckConstraint, Index, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base

class Payment(Base):
    __tablename__ = "payments"

    payment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    payment_for: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    related_listing_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("property_listings.listing_id"), nullable=True)
    related_requirement_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("tenant_requirements.requirement_id"), nullable=True)

    amount: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR")

    payment_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    payment_gateway: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    gateway_transaction_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    gateway_order_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    status: Mapped[str] = mapped_column(String(20), server_default="pending")

    initiated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    refunded_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    receipt_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    invoice_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    metadata_info: Mapped[Optional[Dict]] = mapped_column("metadata", JSONB, nullable=True) # Renamed to avoid reserved keyword conflict if any, though metadata is safe in python

    __table_args__ = (
        CheckConstraint("payment_for IN ('tenant_listing', 'host_listing', 'premium_listing', 'tenant_subscription', 'host_subscription', 'verification_badge', 'featured_listing', 'boost')", name="ck_payment_for"),
        CheckConstraint("status IN ('pending', 'processing', 'completed', 'failed', 'refunded', 'cancelled')", name="ck_payment_status"),
        Index("idx_payment_user", "user_id"),
        Index("idx_payment_status", "status"),
        Index("idx_payment_gateway_txn", "gateway_transaction_id"),
    )


class Subscription(Base):
    __tablename__ = "subscriptions"

    subscription_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    subscription_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    duration_months: Mapped[int] = mapped_column(Integer, nullable=False)

    amount: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    discount_applied: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), default=0)
    final_amount: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)

    status: Mapped[str] = mapped_column(String(20), server_default="active")
    
    starts_at: Mapped[date] = mapped_column(Date, nullable=False)
    expires_at: Mapped[date] = mapped_column(Date, nullable=False)

    auto_renew: Mapped[bool] = mapped_column(Boolean, default=False)
    
    payment_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("payments.payment_id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint("subscription_type IN ('tenant_basic', 'tenant_premium', 'host_basic', 'host_premium')", name="ck_subscription_type"),
        CheckConstraint("status IN ('active', 'expired', 'cancelled', 'paused')", name="ck_subscription_status"),
        Index("idx_subscription_user", "user_id"),
        Index("idx_subscription_status", "status", "expires_at"),
    )
