"""
FastAPI dependencies for authentication and authorization.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.firebase import verify_firebase_token
from app.database.postgres import get_db
from app.models.user import User


security = HTTPBearer()


async def get_current_firebase_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Extract and verify Firebase Bearer token from Authorization header.
    
    Args:
        credentials: HTTP Bearer credentials from request header
        
    Returns:
        Dict containing decoded Firebase token claims (includes 'uid' as firebase_id)
        
    Raises:
        HTTPException: If token is missing or invalid
    """
    token = credentials.credentials
    decoded_token = verify_firebase_token(token)
    return decoded_token


async def get_current_user(
    firebase_user: dict = Depends(get_current_firebase_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Full authentication flow: verify Firebase token → get firebase_id → lookup user in DB.
    
    Args:
        firebase_user: Decoded Firebase token from get_current_firebase_user
        db: Database session
        
    Returns:
        User object from database
        
    Raises:
        HTTPException: If user not found in database
    """
    firebase_id = firebase_user.get("uid")
    
    if not firebase_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase UID not found in token"
        )
    
    user = db.query(User).filter(User.firebase_id == firebase_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Please complete signup first."
        )
    
    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Optional authentication - returns User if valid token provided, None otherwise.
    Useful for endpoints that work both authenticated and unauthenticated.
    
    Args:
        credentials: Optional HTTP Bearer credentials
        db: Database session
        
    Returns:
        User object if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        decoded_token = verify_firebase_token(token)
        firebase_id = decoded_token.get("uid")
        
        if not firebase_id:
            return None
        
        user = db.query(User).filter(User.firebase_id == firebase_id).first()
        return user
    except:
        return None
