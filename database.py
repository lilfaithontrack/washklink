import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from dotenv import load_dotenv
from core.config import settings
import logging
from urllib.parse import urlparse

# Load environment variables from .env
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

# MongoDB client and database
client: AsyncIOMotorClient = None
database = None

def get_database_name_from_url(url: str) -> str:
    """Extract database name from MongoDB connection URL"""
    parsed = urlparse(url)
    # The path in the URL contains the database name (removing the leading '/')
    db_name = parsed.path.lstrip('/') if parsed.path else 'washlink_db'
    # If no database in URL, return default
    return db_name if db_name else 'washlink_db'

# MongoDB connection
async def connect_to_mongo():
    """Create database connection"""
    global client, database
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db_name = get_database_name_from_url(settings.MONGODB_URL)
        database = client[db_name]
        
        # Import all models for beanie initialization
        from models.mongo_models import (
            User, ServiceProvider, Driver, Order, 
            Item, Payment, Notification
        )
        
        # Initialize beanie with all models
        await init_beanie(
            database=database,
            document_models=[
                User, ServiceProvider, Driver, Order,
                Item, Payment, Notification
            ]
        )
        
        logger.info(f"Connected to MongoDB database: {db_name}")
        
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {str(e)}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    global client
    if client:
        client.close()
        logger.info("Disconnected from MongoDB")

# Initialize database
async def init_db():
    """Initialize the database connection"""
    await connect_to_mongo()

# Get database instance
def get_database():
    """Get database instance"""
    return database
