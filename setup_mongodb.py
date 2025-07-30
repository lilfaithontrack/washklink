#!/usr/bin/env python3
"""
MongoDB Setup Script for WashLink Backend
This script initializes MongoDB connection and creates default admin user
"""

import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from core.config import settings
from models.mongo_models import User, UserRole
from core.security import get_password_hash

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def setup_mongodb():
    """Setup MongoDB connection and create default admin user"""
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        database = client[settings.MONGODB_DB_NAME]
        
        # Test connection
        await client.admin.command('ping')
        logger.info(f"Successfully connected to MongoDB at {settings.MONGODB_URL}")
        
        # Initialize Beanie
        from models.mongo_models import (
            User, ServiceProvider, Driver, Order, 
            OrderItem, Payment, Notification, Item
        )
        
        await init_beanie(
            database=database,
            document_models=[
                User, ServiceProvider, Driver, Order,
                Payment, Notification, Item
            ]
        )
        logger.info("Beanie ODM initialized successfully")
        
        # Create default admin user if it doesn't exist
        admin_email = settings.DEFAULT_ADMIN_EMAIL
        existing_admin = await User.find_one(User.email == admin_email)
        
        if not existing_admin:
            admin_user = User(
                full_name="System Administrator",
                phone_number=settings.DEFAULT_ADMIN_PHONE,
                email=admin_email,
                hashed_password=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
                role=UserRole.ADMIN,
                is_active=True
            )
            
            await admin_user.insert()
            logger.info(f"Created default admin user: {admin_email}")
        else:
            logger.info(f"Admin user already exists: {admin_email}")
        
        # Create some sample items if none exist
        existing_items = await Item.find_all().limit(1).to_list()
        if not existing_items:
            from models.mongo_models import Item
            
            sample_items = [
                Item(name="Shirt", description="Basic shirt laundry", price=50.0, category="Basic", estimated_time="24 hours"),
                Item(name="Pants", description="Basic pants laundry", price=80.0, category="Basic", estimated_time="24 hours"),
                Item(name="Dress", description="Premium dress laundry", price=120.0, category="Premium", estimated_time="48 hours"),
                Item(name="Suit", description="Premium suit laundry", price=200.0, category="Premium", estimated_time="48 hours"),
                Item(name="Jeans", description="Basic jeans laundry", price=90.0, category="Basic", estimated_time="24 hours"),
                Item(name="T-shirt", description="Basic t-shirt laundry", price=40.0, category="Basic", estimated_time="24 hours"),
            ]
            
            for item in sample_items:
                await item.insert()
            
            logger.info(f"Created {len(sample_items)} sample items")
        
        # Show database statistics
        collections = await database.list_collection_names()
        logger.info(f"Available collections: {collections}")
        
        for collection_name in collections:
            collection = database[collection_name]
            count = await collection.count_documents({})
            logger.info(f"  {collection_name}: {count} documents")
        
        logger.info("MongoDB setup completed successfully!")
        
        # Close connection
        client.close()
        
    except Exception as e:
        logger.error(f"Error setting up MongoDB: {str(e)}")
        raise

async def check_mongodb_connection():
    """Check if MongoDB is accessible"""
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        await client.admin.command('ping')
        logger.info("✅ MongoDB connection successful")
        client.close()
        return True
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {str(e)}")
        return False

async def main():
    """Main function"""
    print("🚀 WashLink MongoDB Setup")
    print("=" * 50)
    
    # Check MongoDB connection first
    if not await check_mongodb_connection():
        print("\n❌ Please ensure MongoDB is running and accessible")
        print("💡 Quick start with Docker: docker run -d -p 27017:27017 mongo:latest")
        return
    
    # Run setup
    await setup_mongodb()
    
    print("\n✅ Setup completed successfully!")
    print(f"📧 Admin email: {settings.DEFAULT_ADMIN_EMAIL}")
    print(f"🔑 Admin password: {settings.DEFAULT_ADMIN_PASSWORD}")
    print(f"🗄️  Database: {settings.MONGODB_DB_NAME}")
    print("\n🎉 Your WashLink backend is ready to use with MongoDB!")

if __name__ == "__main__":
    asyncio.run(main()) 