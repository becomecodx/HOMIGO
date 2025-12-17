"""FastAPI routes for Firebase-related auth endpoints."""
from fastapi import APIRouter, HTTPException, status
from .models import (
    ProjectVerifyRequest,
    ProjectVerifyResponse,
    FirebaseSignupRequest,
    FirebaseSignupResponse,
    FirebaseLoginRequest,
    FirebaseLoginResponse,
)
from . import service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/firebase", tags=["Firebase"])


@router.post(
    "/verify_project",
    response_model=ProjectVerifyResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify Firebase project metadata",
)
def verify_project_endpoint(request: ProjectVerifyRequest):
    try:
        result = service.verify_project(request)
        return result
    except Exception as e:
        logger.error("Error verifying project: %s", e)
        raise HTTPException(status_code=500, detail={"success": False, "message": "Internal server error"})


@router.post(
    "/signup",
    response_model=FirebaseSignupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Simulated Firebase signup",
)
def firebase_signup(request: FirebaseSignupRequest):
    try:
        result = service.signup(request)
        return result
    except Exception as e:
        logger.error("Signup error: %s", e)
        raise HTTPException(status_code=500, detail={"success": False, "message": "Internal server error"})


@router.post(
    "/login",
    response_model=FirebaseLoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Simulated Firebase login",
)
def firebase_login(request: FirebaseLoginRequest):
    try:
        result = service.login(request)
        return result
    except Exception as e:
        logger.error("Login error: %s", e)
        raise HTTPException(status_code=500, detail={"success": False, "message": "Internal server error"})
