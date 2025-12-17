"""
User verification and OTP models.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Boolean, DateTime, Integer, DECIMAL, ForeignKey, Computed, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base

class UserVerification(Base):
    __tablename__ = "user_verifications"

    verification_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, unique=True) # Added unique=True for 1-to-1 logic but schema didn't strictly forbid duplicates, though implied 1-to-1

    phone_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    aadhaar_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    face_id_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    phone_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    aadhaar_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    face_id_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    aadhaar_last_4_digits: Mapped[Optional[str]] = mapped_column(String(4), nullable=True)
    aadhaar_verification_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    face_id_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    face_verification_score: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2), nullable=True)

    is_fully_verified: Mapped[bool] = mapped_column(Boolean, Computed("phone_verified AND email_verified AND aadhaar_verified AND face_id_verified", persisted=True))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="verification")

    __table_args__ = (
        Index("idx_verifications_user_id", "user_id"),
        Index("idx_verifications_status", "is_fully_verified"),
    )


class OTPLog(Base):
    __tablename__ = "otp_logs"

    otp_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True)
    
    contact_method: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    contact_value: Mapped[str] = mapped_column(String(255), nullable=False)
    otp_code: Mapped[str] = mapped_column(String(10), nullable=False)
    otp_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    purpose: Mapped[str] = mapped_column(String(50), nullable=False)
    
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("contact_method IN ('phone', 'email', 'aadhaar')", name="ck_otp_contact_method"),
        Index("idx_otp_user_id", "user_id"),
        Index("idx_otp_contact", "contact_method", "contact_value"),
    )
