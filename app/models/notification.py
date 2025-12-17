"""
Notification models.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Boolean, DateTime, Text, CheckConstraint, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base

class Notification(Base):
    __tablename__ = "notifications"

    notification_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    notification_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    related_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    related_listing_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("property_listings.listing_id"), nullable=True)
    related_requirement_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("tenant_requirements.requirement_id"), nullable=True)
    related_match_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("matches.match_id"), nullable=True)

    sent_via_app: Mapped[bool] = mapped_column(Boolean, default=True)
    sent_via_email: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_via_whatsapp: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_via_sms: Mapped[bool] = mapped_column(Boolean, default=False)

    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    action_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="notifications")

    __table_args__ = (
        CheckConstraint("notification_type IN ('like_received', 'match_made', 'message_received', 'visit_scheduled', 'visit_reminder', 'listing_expiring', 'requirement_expiring', 'payment_reminder', 'verification_pending', 'new_matching_listing', 'new_matching_requirement', 'system_announcement')", name="ck_notif_type"),
        Index("idx_notif_user", "user_id", "created_at"),
        Index("idx_notif_type", "notification_type"),
        Index("idx_notif_read", "is_read"),
    )


class WhatsappNotification(Base):
    __tablename__ = "whatsapp_notifications"

    whatsapp_notif_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notification_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("notifications.notification_id"), nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    message_template: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    message_body: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    whatsapp_message_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    failed_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint("status IN ('pending', 'sent', 'delivered', 'read', 'failed')", name="ck_whatsapp_status"),
        Index("idx_whatsapp_user", "user_id"),
        Index("idx_whatsapp_status", "status"),
    )
