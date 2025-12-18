"""
API v1 router aggregator.
Combines all v1 API routers.
"""
from fastapi import APIRouter

# Import all routers
from app.api.v1.auth.routes import router as auth_router
from app.api.v1.tenant.routes import router as tenant_router
from app.api.v1.host.routes import router as host_router
from app.api.v1.listings.routes import router as listings_router
from app.api.v1.feed.routes import router as feed_router
from app.api.v1.matching.routes import router as matching_router


router = APIRouter(prefix="/v1")

# Include all v1 routers
router.include_router(auth_router)
router.include_router(tenant_router)
router.include_router(host_router)
router.include_router(listings_router)
router.include_router(feed_router)
router.include_router(matching_router)
