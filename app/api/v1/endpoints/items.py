from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.item import ItemPriceSchema
from app.db.models.item import ItemPrice

router = APIRouter()

@router.get("/", response_model=List[ItemPriceSchema])
def get_all_items(db: Session = Depends(get_db)):
    """Get all items with pricing"""
    items = db.query(ItemPrice).all()
    if not items:
        raise HTTPException(status_code=404, detail="No items found")
    return items

@router.get("/{item_id}", response_model=ItemPriceSchema)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get item by ID"""
    item = db.query(ItemPrice).filter(ItemPrice.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item