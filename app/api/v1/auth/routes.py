"""
Authentication routes with Firebase integration.
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.v1.auth.schemas import (
    SignupRequest, SignupResponse, 
    LoginRequest, LoginResponse,
    UpdateProfileRequest, UserResponse
)
from app.core.dependencies import get_current_user, get_current_firebase_user
from app.core.firebase import verify_firebase_token
from app.database.postgres import get_db
from app.models.user import User


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignupRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user with Firebase ID.
    
    - **firebase_id**: Firebase UID from Firebase Authentication
    - **full_name**: User's full name
    - **email**: User's email address
    - **phone**: User's phone number
    - **user_type**: 'tenant', 'host', or 'both'
    """
    # Check if user already exists with this firebase_id
    result = await db.execute(
        select(User).where(User.firebase_id == request.firebase_id)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this Firebase ID already exists"
        )
    
    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    existing_email = result.scalar_one_or_none()
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    
    # Check if phone already exists
    result = await db.execute(
        select(User).where(User.phone == request.phone)
    )
    existing_phone = result.scalar_one_or_none()
    
    if existing_phone:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this phone number already exists"
        )
    
    # Validate user_type
    if request.user_type not in ['tenant', 'host', 'both']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_type must be 'tenant', 'host', or 'both'"
        )
    
    # Create new user
    new_user = User(
        firebase_id=request.firebase_id,
        full_name=request.full_name,
        email=request.email,
        phone=request.phone,
        user_type=request.user_type,
        profile_photo_url=request.profile_photo_url,
        device_token=request.device_token,
        fcm_token=request.fcm_token,
        account_status="active",
        created_at=datetime.utcnow(),
        last_login_at=datetime.utcnow()
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return SignupResponse(
        success=True,
        message="User registered successfully",
        user=UserResponse.model_validate(new_user)
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with Firebase ID token.
    
    - **firebase_token**: Firebase ID token from client
    - **device_token**: Optional device token for push notifications
    - **fcm_token**: Optional FCM token for Firebase Cloud Messaging
    
    Returns user data after validating the Firebase token.
    """
    # Verify Firebase token
    decoded_token = verify_firebase_token(request.firebase_token)
    firebase_id = decoded_token.get("uid")
    
    if not firebase_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase token: UID not found"
        )
    
    # Find user by firebase_id
    result = await db.execute(
        select(User).where(User.firebase_id == firebase_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Please complete signup first."
        )
    
    # Update last login time and tokens if provided
    user.last_login_at = datetime.utcnow()
    if request.device_token:
        user.device_token = request.device_token
    if request.fcm_token:
        user.fcm_token = request.fcm_token
    
    await db.commit()
    await db.refresh(user)
    
    return LoginResponse(
        success=True,
        message="Login successful",
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user's information.
    
    Requires valid Firebase Bearer token in Authorization header.
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user's profile.
    
    Requires valid Firebase Bearer token in Authorization header.
    """
    # Update only provided fields
    if request.full_name is not None:
        current_user.full_name = request.full_name
    if request.phone is not None:
        # Check if phone already exists for another user
        result = await db.execute(
            select(User).where(
                User.phone == request.phone,
                User.user_id != current_user.user_id
            )
        )
        existing_phone = result.scalar_one_or_none()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Phone number already in use"
            )
        current_user.phone = request.phone
    
    if request.profile_photo_url is not None:
        current_user.profile_photo_url = request.profile_photo_url
    if request.device_token is not None:
        current_user.device_token = request.device_token
    if request.fcm_token is not None:
        current_user.fcm_token = request.fcm_token
    
    current_user.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)


@router.get("/health")
async def health_check():
    """Health check endpoint for auth API."""
    return {
        "status": "healthy",
        "service": "auth-api",
        "version": "1.0.0"
    }
