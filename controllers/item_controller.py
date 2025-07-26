from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Integer, Float, Text
from sqlalchemy.orm import Session, declarative_base

from database import Base, get_db  # your existing database.py with Base and get_db session dependency

router = APIRouter()

# SQLAlchemy model
class ItemPrice(Base):
    __tablename__ = "tbl_item_price_with_catagory"

    id = Column(Integer, primary_key=True, index=True)
    catagory_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    normal_price = Column(Float, nullable=False)
    title = Column(Text, nullable=False)
    discount = Column(Float, nullable=False)
    out_of_stock = Column(Integer, nullable=False)

# Pydantic schema
class ItemPriceSchema(BaseModel):
    id: int
    catagory_id: int
    product_id: int
    normal_price: float
    title: str
    discount: float
    out_of_stock: int

    class Config:
        from_attributes = True  # Pydantic V2: replaces orm_mode

# Controller + Route
@router.get("/items", response_model=List[ItemPriceSchema])
def get_all_items(db: Session = Depends(get_db)):
    items = db.query(ItemPrice).all()
    if not items:
        raise HTTPException(status_code=404, detail="No items found")
    return items
