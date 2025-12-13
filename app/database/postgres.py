"""
PostgreSQL database connection and management.
Handles async database connections using SQLAlchemy with asyncpg.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass


# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.
    Yields a session and ensures it's closed after use.
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database.
    Called during application startup.
    """
    try:
        # Test connection
        async with engine.begin() as conn:
            await conn.run_sync(lambda _: None)
        logger.info("Connected to PostgreSQL database")
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        raise


async def close_db() -> None:
    """
    Close database connection.
    Called during application shutdown.
    """
    await engine.dispose()
    logger.info("Closed PostgreSQL connection")
