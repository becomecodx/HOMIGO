"""
MongoDB database connection and management.
Handles async database connections using Motor driver.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)


class MongoDB:
    """MongoDB database client manager."""
    
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None


# Global database instance
mongodb = MongoDB()


async def connect_to_mongo() -> None:
    """
    Create database connection.
    Called during application startup.
    """
    try:
        mongodb.client = AsyncIOMotorClient(settings.mongodb_url)
        mongodb.database = mongodb.client[settings.mongodb_db_name]
        
        # Test connection
        await mongodb.client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {settings.mongodb_db_name}")
        
        # Create indexes for users collection
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection() -> None:
    """
    Close database connection.
    Called during application shutdown.
    """
    if mongodb.client:
        mongodb.client.close()
        logger.info("Disconnected from MongoDB")


async def create_indexes() -> None:
    """
    Create database indexes for optimal query performance.
    Creates unique indexes on email and phone_number fields.
    """
    try:
        users_collection = mongodb.database.users
        
        # Create unique index on email
        await users_collection.create_index("email", unique=True)
        
        # Create unique index on phone_number
        await users_collection.create_index("phone_number", unique=True)
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.warning(f"Failed to create indexes: {e}")


def get_database() -> AsyncIOMotorDatabase:
    """
    Get the database instance.
    
    Returns:
        AsyncIOMotorDatabase: The database instance
        
    Raises:
        RuntimeError: If database is not initialized
    """
    if mongodb.database is None:
        raise RuntimeError("Database not initialized. Call connect_to_mongo() first.")
    return mongodb.database


def get_users_collection():
    """
    Get the users collection.
    
    Returns:
        Collection: The users collection
    """
    database = get_database()
    return database.users

