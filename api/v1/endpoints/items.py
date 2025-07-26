from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Form
from sqlalchemy.orm import Session
from api.deps import get_db, get_admin_user, get_manager_user
from models.users import DBUser
from datetime import datetime
import json

router = APIRouter(redirect_slashes=False)

# In-memory storage for items (in a real app, this would be a database table)
ITEMS_STORAGE = [
    {
        "id": 1,
        "name": "Wash & Fold",
        "description": "Basic washing and folding service",
        "price": 150.0,
        "currency": "ETB",
        "category": "Basic",
        "is_active": True,
        "estimated_time": "24 hours",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
    },
    {
        "id": 2,
        "name": "Dry Clean",
        "description": "Professional dry cleaning service",
        "price": 300.0,
        "currency": "ETB",
        "category": "Premium",
        "is_active": True,
        "estimated_time": "48 hours",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
    },
    {
        "id": 3,
        "name": "Iron & Press",
        "description": "Professional ironing and pressing service",
        "price": 200.0,
        "currency": "ETB",
        "category": "Premium",
        "is_active": True,
        "estimated_time": "24 hours",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
    },
    {
        "id": 4,
        "name": "Express Service",
        "description": "Same day service for urgent orders",
        "price": 500.0,
        "currency": "ETB",
        "category": "Express",
        "is_active": True,
        "estimated_time": "6 hours",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
    }
]

@router.get("/", response_model=List[dict])
def get_all_items(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_manager_user),
    category: Optional[str] = Query(None, description="Filter by category"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all items/services (Manager/Admin only)"""
    items = ITEMS_STORAGE.copy()
    
    # Apply filters
    if category:
        items = [item for item in items if item["category"] == category]
    
    if is_active is not None:
        items = [item for item in items if item["is_active"] == is_active]
    
    # Apply pagination
    items = items[skip:skip + limit]
    
    return items

@router.get("/{item_id}", response_model=dict)
def get_item_by_id(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_manager_user)
):
    """Get item/service by ID"""
    item = next((item for item in ITEMS_STORAGE if item["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item

@router.post("/", response_model=dict)
def create_item(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    currency: str = Form("ETB"),
    category: str = Form(...),
    estimated_time: str = Form("24 hours"),
    is_active: bool = Form(True),
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_admin_user)
):
    """Create a new item/service (Admin only)"""
    
    # Check if item name already exists
    existing_item = next((item for item in ITEMS_STORAGE if item["name"].lower() == name.lower()), None)
    if existing_item:
        raise HTTPException(status_code=400, detail="Item name already exists")
    
    # Generate new ID
    new_id = max([item["id"] for item in ITEMS_STORAGE], default=0) + 1
    
    # Create new item
    new_item = {
        "id": new_id,
        "name": name,
        "description": description,
        "price": price,
        "currency": currency,
        "category": category,
        "is_active": is_active,
        "estimated_time": estimated_time,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    ITEMS_STORAGE.append(new_item)
    
    return {
        **new_item,
        "message": "Item created successfully"
    }

@router.put("/{item_id}", response_model=dict)
def update_item(
    item_id: int,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    currency: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    estimated_time: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_admin_user)
):
    """Update item/service (Admin only)"""
    
    item_index = next((i for i, item in enumerate(ITEMS_STORAGE) if item["id"] == item_id), None)
    if item_index is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Check if new name already exists (if being updated)
    if name and name.lower() != ITEMS_STORAGE[item_index]["name"].lower():
        existing_item = next((item for item in ITEMS_STORAGE if item["name"].lower() == name.lower()), None)
        if existing_item:
            raise HTTPException(status_code=400, detail="Item name already exists")
    
    # Update fields
    if name is not None:
        ITEMS_STORAGE[item_index]["name"] = name
    if description is not None:
        ITEMS_STORAGE[item_index]["description"] = description
    if price is not None:
        ITEMS_STORAGE[item_index]["price"] = price
    if currency is not None:
        ITEMS_STORAGE[item_index]["currency"] = currency
    if category is not None:
        ITEMS_STORAGE[item_index]["category"] = category
    if estimated_time is not None:
        ITEMS_STORAGE[item_index]["estimated_time"] = estimated_time
    if is_active is not None:
        ITEMS_STORAGE[item_index]["is_active"] = is_active
    
    ITEMS_STORAGE[item_index]["updated_at"] = datetime.utcnow().isoformat()
    
    return {
        **ITEMS_STORAGE[item_index],
        "message": "Item updated successfully"
    }

@router.delete("/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_admin_user)
):
    """Delete item/service (Admin only)"""
    item_index = next((i for i, item in enumerate(ITEMS_STORAGE) if item["id"] == item_id), None)
    if item_index is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    deleted_item = ITEMS_STORAGE.pop(item_index)
    
    return {
        "message": "Item deleted successfully",
        "deleted_item": deleted_item
    }

@router.get("/categories/list", response_model=List[str])
def get_item_categories(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_manager_user)
):
    """Get all available item categories"""
    categories = list(set([item["category"] for item in ITEMS_STORAGE]))
    return categories

@router.get("/stats/summary", response_model=dict)
def get_items_summary(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_manager_user)
):
    """Get items summary statistics"""
    total_items = len(ITEMS_STORAGE)
    active_items = len([item for item in ITEMS_STORAGE if item["is_active"]])
    categories = list(set([item["category"] for item in ITEMS_STORAGE]))
    
    # Calculate average price
    total_price = sum([item["price"] for item in ITEMS_STORAGE])
    average_price = total_price / total_items if total_items > 0 else 0
    
    return {
        "total_items": total_items,
        "active_items": active_items,
        "inactive_items": total_items - active_items,
        "categories": categories,
        "average_price": round(average_price, 2),
        "total_price": total_price
    } 