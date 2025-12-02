"""
Authentication service.
Handles user authentication business logic.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from app.database.mongodb import get_users_collection
from app.models.user import User, UserCreate
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
    async def create_user(user_data: UserCreate) -> Dict[str, Any]:
        """
        Create a new user account.
        
        Args:
            user_data: User creation data
            
        Returns:
            Dict: Created user data (without password hash)
            
        Raises:
            ValueError: If validation fails
            DuplicateKeyError: If email or phone already exists
        """
        users_collection = get_users_collection()
        
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
        existing_user = await users_collection.find_one({
            "$or": [
                {"email": user_data.email.lower()},
                {"phone_number": sanitize_phone_number(user_data.phone_number)}
            ]
        })
        
        if existing_user:
            if existing_user.get("email") == user_data.email.lower():
                raise ValueError("Email already registered")
            else:
                raise ValueError("Phone number already registered")
        
        # Hash password
        password_hash = hash_password(user_data.password)
        
        # Create user document
        user_doc = {
            "first_name": user_data.first_name.strip(),
            "last_name": user_data.last_name.strip(),
            "email": user_data.email.lower().strip(),
            "phone_number": sanitize_phone_number(user_data.phone_number),
            "password_hash": password_hash,
            "is_active": True,
            "is_verified": False,
            "created_at": datetime.utcnow(),
            "updated_at": None
        }
        
        try:
            # Insert user into database
            result = await users_collection.insert_one(user_doc)
            
            # Retrieve created user (without password hash)
            created_user = await users_collection.find_one({"_id": result.inserted_id})
            
            # Convert ObjectId to string for JSON serialization
            user_dict = {
                "_id": str(created_user["_id"]),
                "first_name": created_user["first_name"],
                "last_name": created_user["last_name"],
                "email": created_user["email"],
                "phone_number": created_user["phone_number"],
                "is_active": created_user["is_active"],
                "is_verified": created_user["is_verified"],
                "created_at": created_user["created_at"]
            }
            
            logger.info(f"User created: {user_dict['email']}")
            
            return user_dict
        
        except DuplicateKeyError as e:
            logger.warning(f"Duplicate key error creating user: {e}")
            raise ValueError("Email or phone number already registered")
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise ValueError("Failed to create user account")
    
    @staticmethod
    async def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user with email and password.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Optional[Dict]: User data if authentication successful, None otherwise
        """
        users_collection = get_users_collection()
        
        # Find user by email
        user = await users_collection.find_one({"email": email.lower().strip()})
        
        if not user:
            logger.warning(f"Login attempt with non-existent email: {email}")
            return None
        
        # Check if user is active
        if not user.get("is_active", True):
            logger.warning(f"Login attempt with inactive account: {email}")
            return None
        
        # Verify password
        if not verify_password(password, user["password_hash"]):
            logger.warning(f"Invalid password for email: {email}")
            return None
        
        # Return user data (without password hash)
        user_dict = {
            "_id": str(user["_id"]),
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "email": user["email"],
            "phone_number": user["phone_number"],
            "is_active": user["is_active"],
            "is_verified": user.get("is_verified", False),
            "created_at": user["created_at"]
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
            "sub": user_data["_id"],  # Subject (user ID)
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
    async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            Optional[Dict]: User data if found, None otherwise
        """
        users_collection = get_users_collection()
        
        try:
            user = await users_collection.find_one({"_id": ObjectId(user_id)})
            
            if not user:
                return None
            
            return {
                "_id": str(user["_id"]),
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "email": user["email"],
                "phone_number": user["phone_number"],
                "is_active": user["is_active"],
                "is_verified": user.get("is_verified", False),
                "created_at": user["created_at"]
            }
        
        except Exception as e:
            logger.error(f"Failed to get user by ID: {e}")
            return None


# Export service instance
auth_service = AuthService()

