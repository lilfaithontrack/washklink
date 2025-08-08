#!/usr/bin/env python3
"""
Clean Sample Data Script for WashLink Backend
This script ONLY removes the sample items that were automatically created,
leaving all other data (users, orders, payments, etc.) intact.
"""

import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from core.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# List of sample item names that were automatically created
SAMPLE_ITEM_NAMES = [
    "Shirt",
    "Pants", 
    "Dress",
    "Suit",
    "Jeans",
    "T-shirt"
]

async def clean_sample_items():
    """Remove only the sample items that were automatically created"""
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        database = client[settings.MONGODB_DB_NAME]
        
        # Test connection
        await client.admin.command('ping')
        logger.info(f"Successfully connected to MongoDB at {settings.MONGODB_URL}")
        
        # Initialize Beanie
        from models.mongo_models import Item
        
        await init_beanie(
            database=database,
            document_models=[Item]
        )
        logger.info("Beanie ODM initialized successfully")
        
        # Count total items before cleanup
        total_items_before = await Item.count()
        logger.info(f"Total items before cleanup: {total_items_before}")
        
        # Find and delete only the sample items
        deleted_count = 0
        for item_name in SAMPLE_ITEM_NAMES:
            sample_items = await Item.find(Item.name == item_name).to_list()
            
            for item in sample_items:
                # Additional check to make sure it's a sample item
                # (basic prices and categories that match our samples)
                if (item.category in ["Basic", "Premium"] and 
                    item.estimated_time in ["24 hours", "48 hours"]):
                    
                    logger.info(f"Deleting sample item: {item.name} (Price: {item.price}, Category: {item.category})")
                    await item.delete()
                    deleted_count += 1
                else:
                    logger.info(f"Skipping item '{item.name}' - doesn't match sample item pattern")
        
        # Count total items after cleanup
        total_items_after = await Item.count()
        logger.info(f"Total items after cleanup: {total_items_after}")
        logger.info(f"Deleted {deleted_count} sample items")
        logger.info(f"Preserved {total_items_after} custom items")
        
        if deleted_count == 0:
            logger.info("No sample items found to delete")
        else:
            logger.info(f"✅ Successfully removed {deleted_count} sample items")
        
        # Close connection
        client.close()
        
    except Exception as e:
        logger.error(f"Error cleaning sample items: {str(e)}")
        raise

async def list_all_items():
    """List all items in the database for verification"""
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        database = client[settings.MONGODB_DB_NAME]
        
        # Initialize Beanie
        from models.mongo_models import Item
        
        await init_beanie(
            database=database,
            document_models=[Item]
        )
        
        # Get all items
        all_items = await Item.find_all().to_list()
        
        logger.info(f"📋 Current items in database ({len(all_items)} total):")
        for item in all_items:
            logger.info(f"  - {item.name}: ${item.price} ({item.category}) - {item.estimated_time}")
        
        # Close connection
        client.close()
        
    except Exception as e:
        logger.error(f"Error listing items: {str(e)}")

async def main():
    """Main function"""
    print("🧹 WashLink Sample Data Cleaner")
    print("This script will ONLY delete sample items, preserving all other data")
    print()
    
    # Show current items
    print("📋 Listing current items...")
    await list_all_items()
    print()
    
    # Ask for confirmation
    response = input("Do you want to delete sample items? (yes/no): ").lower().strip()
    
    if response in ['yes', 'y']:
        print("🗑️  Cleaning sample items...")
        await clean_sample_items()
        print()
        print("📋 Items after cleanup:")
        await list_all_items()
    else:
        print("❌ Cleanup cancelled")

if __name__ == "__main__":
    asyncio.run(main())