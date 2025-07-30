from typing import List, Optional
from fastapi import APIRouter, HTTPException
from models.mongo_models import Item
from pydantic import BaseModel, Field
from bson import ObjectId
import logging

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic schemas
class ItemResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    price: float
    currency: str = "ETB"
    category: Optional[str] = None
    is_active: bool = True
    estimated_time: Optional[str] = None

    class Config:
        json_encoders = {ObjectId: str}

class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(gt=0)
    currency: str = "ETB"
    category: Optional[str] = None
    estimated_time: Optional[str] = None

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(gt=0)
    currency: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None
    estimated_time: Optional[str] = None

# Controller Routes
@router.get("/items", response_model=List[ItemResponse])
async def get_all_items(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    active_only: bool = True
):
    """Get all items with optional filtering"""
    try:
        query = {}
        if category:
            query["category"] = category
        if active_only:
            query["is_active"] = True

        items = await Item.find(query).skip(skip).limit(limit).to_list()
        if not items:
            raise HTTPException(status_code=404, detail="No items found")
        return items
    except Exception as e:
        logger.error(f"Error getting items: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: str):
    """Get item by ID"""
    try:
        item = await Item.get(ObjectId(item_id))
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return item
    except Exception as e:
        logger.error(f"Error getting item {item_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/items", response_model=ItemResponse)
async def create_item(item: ItemCreate):
    """Create new item"""
    try:
        new_item = Item(
            name=item.name,
            description=item.description,
            price=item.price,
            currency=item.currency,
            category=item.category,
            estimated_time=item.estimated_time,
            is_active=True
        )
        await new_item.insert()
        return new_item
    except Exception as e:
        logger.error(f"Error creating item: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(item_id: str, item_update: ItemUpdate):
    """Update item"""
    try:
        item = await Item.get(ObjectId(item_id))
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        # Update only provided fields
        update_data = item_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)

        await item.save()
        return item
    except Exception as e:
        logger.error(f"Error updating item {item_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/items/{item_id}")
async def delete_item(item_id: str):
    """Delete item"""
    try:
        item = await Item.get(ObjectId(item_id))
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        await item.delete()
        return {"message": "Item deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting item {item_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/items/category/{category}", response_model=List[ItemResponse])
async def get_items_by_category(
    category: str,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True
):
    """Get items by category"""
    try:
        query = {"category": category}
        if active_only:
            query["is_active"] = True

        items = await Item.find(query).skip(skip).limit(limit).to_list()
        if not items:
            raise HTTPException(status_code=404, detail=f"No items found in category: {category}")
        return items
    except Exception as e:
        logger.error(f"Error getting items by category {category}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/items/{item_id}/toggle-status", response_model=ItemResponse)
async def toggle_item_status(item_id: str):
    """Toggle item active status"""
    try:
        item = await Item.get(ObjectId(item_id))
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        item.is_active = not item.is_active
        await item.save()
        return item
    except Exception as e:
        logger.error(f"Error toggling item status {item_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
