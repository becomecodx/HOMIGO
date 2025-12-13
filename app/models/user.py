"""
User database model.
Defines the structure of user table in PostgreSQL.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel, Field, EmailStr

from app.database.postgres import Base


class User(Base):
    """User model for PostgreSQL database."""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"


class UserCreate(BaseModel):
    """User creation schema."""
    
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr = Field(...)
    phone_number: str = Field(...)
    password: str = Field(...)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "first_name": "Ram",
                "last_name": "Harish",
                "email": "ram@homigo.com",
                "phone_number": "9876543210",
                "password": "SecurePass@123"
            }
        }
    }


class UserResponse(BaseModel):
    """User response schema."""
    
    id: int
    first_name: str
    last_name: str
    email: str
    phone_number: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {
        "from_attributes": True
    }


