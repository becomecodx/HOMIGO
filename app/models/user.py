"""
User database model.
"""
import uuid
from datetime import datetime, date
from typing import Optional, List

from sqlalchemy import String, Boolean, DateTime, Integer, Date, Text, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base

class User(Base):
    """User model for PostgreSQL database."""
    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # NOTE: age is not a computed column in PostgreSQL because AGE() is not immutable
    # Compute age at query time: EXTRACT(YEAR FROM AGE(date_of_birth))
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    user_type: Mapped[str] = mapped_column(String(20), nullable=False)
    profile_photo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    account_status: Mapped[str] = mapped_column(String(20), server_default="active")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    device_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fcm_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    verification: Mapped["UserVerification"] = relationship("UserVerification", back_populates="user", uselist=False, cascade="all, delete-orphan")
    tenant_profile: Mapped["TenantProfile"] = relationship("TenantProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    host_profile: Mapped["HostProfile"] = relationship("HostProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    tenant_requirements: Mapped[List["TenantRequirement"]] = relationship("TenantRequirement", back_populates="user", cascade="all, delete-orphan")
    
    # Matching
    matches_as_tenant: Mapped[List["Match"]] = relationship("Match", foreign_keys="[Match.tenant_id]", back_populates="tenant", cascade="all, delete-orphan")
    matches_as_host: Mapped[List["Match"]] = relationship("Match", foreign_keys="[Match.host_id]", back_populates="host", cascade="all, delete-orphan")
    
    # Notifications
    notifications: Mapped[List["Notification"]] = relationship("Notification", foreign_keys="[Notification.user_id]", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("gender IN ('Male', 'Female', 'Other', 'Prefer not to say')", name="ck_users_gender"),
        CheckConstraint("user_type IN ('tenant', 'host', 'both')", name="ck_users_user_type"),
        CheckConstraint("account_status IN ('active', 'suspended', 'deleted', 'pending')", name="ck_users_account_status"),
        Index("idx_users_email", "email"),
        Index("idx_users_phone", "phone"),
        Index("idx_users_user_type", "user_type"),
        Index("idx_users_account_status", "account_status"),
    )

    def __repr__(self) -> str:
        return f"<User(user_id={self.user_id}, email={self.email})>"
