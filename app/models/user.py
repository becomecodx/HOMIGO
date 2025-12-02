"""
User database model.
Defines the structure of user documents stored in MongoDB.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class User(BaseModel):
    """User model for MongoDB documents."""
    
    id: Optional[str] = Field(default=None, alias="_id")
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr = Field(...)
    phone_number: str = Field(...)
    password_hash: str = Field(...)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "first_name": "Ram",
                "last_name": "Harish",
                "email": "ram@homigo.com",
                "phone_number": "9876543210",
                "is_active": True,
                "is_verified": False,
            }
        },
    }

class UserInDB(User):
    """User model as stored in database."""
    pass


class UserCreate(BaseModel):
    """User creation model."""
    
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

