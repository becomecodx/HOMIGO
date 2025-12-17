"""
Application settings and configuration management.
Loads environment variables and provides type-safe configuration.
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    # Allow extra environment variables (e.g., POSTGRES_HOST/PORT) without failing validation
    model_config = {
        "extra": "ignore",
        # load .env automatically when creating Settings
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }
    
    # PostgreSQL Configuration
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/homigo_db",
        alias="DATABASE_URL",
        description="PostgreSQL connection URL"
    )
    
    # JWT Configuration
    jwt_secret_key: str = Field(
        default="your-super-secret-jwt-key-min-32-characters-long-change-in-production",
        alias="JWT_SECRET_KEY",
        description="Secret key for JWT token signing"
    )
    jwt_algorithm: str = Field(
        default="HS256",
        alias="JWT_ALGORITHM",
        description="JWT algorithm for token signing"
    )
    jwt_access_token_expire_minutes: int = Field(
        default=1440,  # 24 hours
        alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
        description="JWT access token expiration time in minutes"
    )
    
    # Application Configuration
    app_name: str = Field(
        default="HOMIGO",
        alias="APP_NAME",
        description="Application name"
    )
    app_version: str = Field(
        default="1.0.0",
        alias="APP_VERSION",
        description="Application version"
    )
    debug: bool = Field(
        default=True,
        alias="DEBUG",
        description="Debug mode flag"
    )
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        alias="ALLOWED_ORIGINS",
        description="Comma-separated list of allowed CORS origins"
    )
    
    # CAPTCHA Configuration
    captcha_expiry_seconds: int = Field(
        default=300,  # 5 minutes
        alias="CAPTCHA_EXPIRY_SECONDS",
        description="CAPTCHA expiration time in seconds"
    )

    # Firebase configuration (metadata and optional service account path)
    firebase_project_name: str = Field(
        default="",
        alias="FIREBASE_PROJECT_NAME",
        description="Firebase project public name"
    )
    firebase_project_id: str = Field(
        default="",
        alias="FIREBASE_PROJECT_ID",
        description="Firebase project id"
    )
    firebase_project_number: str = Field(
        default="",
        alias="FIREBASE_PROJECT_NUMBER",
        description="Firebase project number"
    )
    firebase_environment_type: str = Field(
        default="",
        alias="FIREBASE_ENVIRONMENT_TYPE",
        description="Environment type for the project"
    )
    firebase_public_facing_name: str = Field(
        default="",
        alias="FIREBASE_PUBLIC_FACING_NAME",
        description="Public-facing name for the Firebase project"
    )
    firebase_service_account_path: str = Field(
        default="",
        alias="FIREBASE_SERVICE_ACCOUNT_PATH",
        description="Path to Firebase service account JSON file (optional)"
    )
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Return allowed origins as a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    # Note: env loading and other settings are configured in `model_config` for pydantic v2


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses LRU cache to ensure only one instance is created.
    """
    return Settings()


# Export settings instance
settings = get_settings()

# Convenience helper: get firebase project metadata as dict
def get_firebase_project_metadata() -> dict:
    """Return configured Firebase project metadata from settings."""
    return {
        "project_name": settings.firebase_project_name,
        "project_id": settings.firebase_project_id,
        "project_number": settings.firebase_project_number,
        "environment_type": settings.firebase_environment_type,
        "public_facing_name": settings.firebase_public_facing_name,
        "service_account_path": settings.firebase_service_account_path,
    }

