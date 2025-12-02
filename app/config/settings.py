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
    
    # MongoDB Configuration
    mongodb_url: str = Field(
        default="mongodb://localhost:27017",
        alias="MONGODB_URL",
        description="MongoDB connection URL"
    )
    mongodb_db_name: str = Field(
        default="homigo_db",
        alias="MONGODB_DB_NAME",
        description="MongoDB database name"
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
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Return allowed origins as a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses LRU cache to ensure only one instance is created.
    """
    return Settings()


# Export settings instance
settings = get_settings()

