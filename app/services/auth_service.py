"""
Authentication service.
Handles user authentication business logic.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.schemas.auth import SignupRequest
from app.utils.security import hash_password, verify_password
from app.utils.validators import (
    validate_name,
    validate_phone_number,
    validate_password_strength,
    sanitize_phone_number
)
from app.services.jwt_service import create_access_token, get_token_expiration_seconds
from app.services.captcha_service import verify_captcha
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication operations."""
    
    @staticmethod
    async def create_user(db: AsyncSession, user_data: SignupRequest) -> Dict[str, Any]:
        """
        Create a new user account.
        
        Args:
            db: Database session
            user_data: User creation data
            
        Returns:
            Dict: Created user data (without password hash)
            
        Raises:
            ValueError: If validation fails
        """
        # Validate inputs
        first_name_valid, first_name_error = validate_name(user_data.first_name)
        if not first_name_valid:
            raise ValueError(f"First name: {first_name_error}")
        
        last_name_valid, last_name_error = validate_name(user_data.last_name)
        if not last_name_valid:
            raise ValueError(f"Last name: {last_name_error}")
        
        phone_valid, phone_error = validate_phone_number(user_data.phone_number)
        if not phone_valid:
            raise ValueError(f"Phone number: {phone_error}")
        
        password_valid, password_error = validate_password_strength(user_data.password)
        if not password_valid:
            raise ValueError(f"Password: {password_error}")
        
        # Check if user already exists
        email_lower = user_data.email.lower().strip()
        phone_sanitized = sanitize_phone_number(user_data.phone_number)
        
        result = await db.execute(
            select(User).where(
                or_(
                    User.email == email_lower,
                    User.phone_number == phone_sanitized
                )
            )
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            if existing_user.email == email_lower:
                raise ValueError("Email already registered")
            else:
                raise ValueError("Phone number already registered")
        
        # Hash password
        password_hash = hash_password(user_data.password)
        
        # Create user
        new_user = User(
            first_name=user_data.first_name.strip(),
            last_name=user_data.last_name.strip(),
            email=email_lower,
            phone_number=phone_sanitized,
            password_hash=password_hash,
            is_active=True,
            is_verified=False,
            created_at=datetime.utcnow()
        )
        
        try:
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
            user_dict = {
                "id": new_user.id,
                "first_name": new_user.first_name,
                "last_name": new_user.last_name,
                "email": new_user.email,
                "phone_number": new_user.phone_number,
                "is_active": new_user.is_active,
                "is_verified": new_user.is_verified,
                "created_at": new_user.created_at
            }
            
            logger.info(f"User created: {user_dict['email']}")
            
            return user_dict
        
        except IntegrityError as e:
            await db.rollback()
            logger.warning(f"Integrity error creating user: {e}")
            raise ValueError("Email or phone number already registered")
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create user: {e}")
            raise ValueError("Failed to create user account")
    
    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user with email and password.
        
        Args:
            db: Database session
            email: User's email address
            password: User's password
            
        Returns:
            Optional[Dict]: User data if authentication successful, None otherwise
        """
        # Find user by email
        result = await db.execute(
            select(User).where(User.email == email.lower().strip())
        )
        user = result.scalar_one_or_none()
        
        if not user:
            logger.warning(f"Login attempt with non-existent email: {email}")
            return None
        
        # Check if user is active
        if not user.is_active:
            logger.warning(f"Login attempt with inactive account: {email}")
            return None
        
        # Verify password
        if not verify_password(password, user.password_hash):
            logger.warning(f"Invalid password for email: {email}")
            return None
        
        # Return user data (without password hash)
        user_dict = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone_number": user.phone_number,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at
        }
        
        logger.info(f"User authenticated: {email}")
        
        return user_dict
    
    @staticmethod
    async def verify_user_captcha(captcha_id: str, captcha_answer: str) -> bool:
        """
        Verify CAPTCHA for user action.
        
        Args:
            captcha_id: CAPTCHA identifier
            captcha_answer: User's CAPTCHA answer
            
        Returns:
            bool: True if CAPTCHA is valid, False otherwise
        """
        return verify_captcha(captcha_id, captcha_answer)
    
    @staticmethod
    def create_user_token(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create JWT token for authenticated user.
        
        Args:
            user_data: User data dictionary
            
        Returns:
            Dict: Token information
        """
        # Prepare token claims
        token_data = {
            "sub": str(user_data["id"]),  # Subject (user ID)
            "email": user_data["email"],
            "first_name": user_data["first_name"],
            "last_name": user_data["last_name"]
        }
        
        # Create access token
        access_token = create_access_token(token_data)
        
        # Return token response
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": get_token_expiration_seconds()
        }
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user by ID.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Optional[Dict]: User data if found, None otherwise
        """
        try:
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            return {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone_number": user.phone_number,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "created_at": user.created_at
            }
        
        except Exception as e:
            logger.error(f"Failed to get user by ID: {e}")
            return None


# Export service instance
auth_service = AuthService()

