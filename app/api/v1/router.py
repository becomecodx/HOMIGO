"""
API v1 router aggregator.
Combines all v1 API routers.
"""
from fastapi import APIRouter
from app.api.v1.auth.routes import router as auth_router


router = APIRouter(prefix="/v1")

# Include all v1 routers
router.include_router(auth_router)
