"""
HOMIGO Authentication API - Main Application
Production-ready FastAPI application for user authentication.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from app.config.settings import settings
from app.database.postgres import init_db, close_db
from app.routes.auth import router as auth_router
from app.firebase_auth.routes import router as firebase_router
from app.core.firebase import init_firebase  # Firebase Admin SDK initialization
from app.api.v1.router import router as v1_router  # New v1 API router
import sys


# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.
    Handles startup and shutdown operations.
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}...")
    
    try:
        # Initialize Firebase Admin SDK
        init_firebase()
        logger.info("Firebase Admin SDK initialized")
        
        # Connect to PostgreSQL
        await init_db()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    
    try:
        # Close PostgreSQL connection
        await close_db()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database connection: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-ready authentication API for HOMIGO platform",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors with custom format.
    """
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append({
            "field": field,
            "message": error["msg"]
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation error",
            "errors": errors
        }
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle HTTP exceptions with custom format.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail.get("message", "An error occurred") if isinstance(exc.detail, dict) else str(exc.detail),
            "error_code": exc.detail.get("error_code") if isinstance(exc.detail, dict) else None
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information.
    """
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/api/docs"
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health():
    """
    Application health check.
    """
    return {
        "status": "healthy",
        "service": settings.app_name
    }


# Include routers
app.include_router(v1_router, prefix="/api")  # New v1 API with Firebase auth
app.include_router(auth_router, prefix="/api")
app.include_router(firebase_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )

