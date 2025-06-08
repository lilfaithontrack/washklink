from pydantic import BaseModel
from typing import List, Optional

class BookingItem(BaseModel):
    product_id: int
    category_id: int
    quantity: int
    price: float
    
class BookingCreate(BaseModel):
    user_id: int
    items: List[BookingItem]
    payment_option: Optional[str]
    delivery: bool = False
    delivery_km: float = 0.0
    cash_on_delivery: bool = False
    note: Optional[str] = None


class BookingOut(BaseModel):
    id: int
    user_id: int
    items: List[BookingItem]
    price_tag: float
    subtotal: float
    payment_option: Optional[str]
    delivery: bool
    delivery_km: float
    delivery_charge: float
    cash_on_delivery: bool
    note: Optional[str]

    class Config:
        orm_mode = True
