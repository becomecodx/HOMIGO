"""
Authentication routes.
Defines API endpoints for authentication operations.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    CaptchaGenerateResponse,
    LoginResponse,
    UserResponse
)
from app.schemas.response import SuccessResponse, ErrorResponse, HealthResponse
from app.services.auth_service import auth_service
from app.services.captcha_service import create_captcha, get_active_captcha_count
from app.utils.validators import validate_password_strength, validate_name, validate_phone_number
from app.database.postgres import get_db
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get(
    "/captcha",
    response_model=CaptchaGenerateResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate CAPTCHA",
    description="Generate a new CAPTCHA challenge. Returns a CAPTCHA ID and base64-encoded image."
)
async def generate_captcha():
    """
    Generate a new CAPTCHA challenge.
    
    Returns:
        CaptchaGenerateResponse: CAPTCHA ID and image
    """
    try:
        captcha_id, captcha_image = create_captcha()
        
        return CaptchaGenerateResponse(
            captcha_id=captcha_id,
            captcha_image=captcha_image
        )
    
    except Exception as e:
        logger.error(f"Failed to generate CAPTCHA: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Failed to generate CAPTCHA",
                "error_code": "INTERNAL_ERROR"
            }
        )


@router.post(
    "/signup",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User Signup",
    description="Create a new user account. Requires CAPTCHA verification."
)
async def signup(request: SignupRequest):
    """
    Register a new user.
    
    Args:
        request: Signup request data
        
    Returns:
        SuccessResponse: Created user data
        
    Raises:
        HTTPException: If validation fails, CAPTCHA invalid, or user exists
    """
    validation_errors = []
    
    # Validate inputs
    first_name_valid, first_name_error = validate_name(request.first_name)
    if not first_name_valid:
        validation_errors.append({"field": "first_name", "message": first_name_error})
    
    last_name_valid, last_name_error = validate_name(request.last_name)
    if not last_name_valid:
        validation_errors.append({"field": "last_name", "message": last_name_error})
    
    phone_valid, phone_error = validate_phone_number(request.phone_number)
    if not phone_valid:
        validation_errors.append({"field": "phone_number", "message": phone_error})
    
    password_valid, password_error = validate_password_strength(request.password)
    if not password_valid:
        validation_errors.append({"field": "password", "message": password_error})
    
    if validation_errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "success": False,
                "message": "Validation error",
                "errors": validation_errors
            }
        )
    
    # Verify CAPTCHA
    captcha_valid = await auth_service.verify_user_captcha(
        request.captcha_id,
        request.captcha_answer
    )
    
    if not captcha_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "message": "Invalid or expired CAPTCHA",
                "error_code": "INVALID_CAPTCHA"
            }
        )
    
    # Create user
    try:
        from app.models.user import UserCreate
        
        user_data = UserCreate(
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            phone_number=request.phone_number,
            password=request.password
        )
        
        created_user = await auth_service.create_user(user_data)
        
        return SuccessResponse(
            success=True,
            message="Account created successfully",
            data=created_user
        )
    
    except ValueError as e:
        error_message = str(e)
        
        # Check if it's a duplicate user error
        if "already registered" in error_message.lower() or "already exists" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "success": False,
                    "message": error_message,
                    "error_code": "USER_EXISTS"
                }
            )
        
        # Other validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "message": error_message,
                "error_code": "VALIDATION_ERROR"
            }
        )
    
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Failed to create account",
                "error_code": "INTERNAL_ERROR"
            }
        )


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticate user and return JWT token. Requires CAPTCHA verification."
)
async def login(request: LoginRequest):
    """
    Authenticate user and return JWT token.
    
    Args:
        request: Login request data
        
    Returns:
        LoginResponse: User data and JWT token
        
    Raises:
        HTTPException: If CAPTCHA invalid or credentials incorrect
    """
    # Verify CAPTCHA
    captcha_valid = await auth_service.verify_user_captcha(
        request.captcha_id,
        request.captcha_answer
    )
    
    if not captcha_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "message": "Invalid or expired CAPTCHA",
                "error_code": "INVALID_CAPTCHA"
            }
        )
    
    # Authenticate user
    user_data = await auth_service.authenticate_user(request.email, request.password)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "message": "Invalid email or password",
                "error_code": "INVALID_CREDENTIALS"
            }
        )
    
    # Create JWT token
    token_data = auth_service.create_user_token(user_data)
    
    # Build response
    return LoginResponse(
        message="Login successful",
        user=UserResponse(**user_data),
        token=token_data
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check authentication service health status."
)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        HealthResponse: Service health status
    """
    active_captchas = get_active_captcha_count()
    
    return HealthResponse(
        status="healthy",
        service="HOMIGO Authentication API",
        active_captchas=active_captchas
    )

