from pydantic import BaseModel
from typing import Optional

class BookingCreate(BaseModel):
    user_id: int
    item: str
    price_tag: float
    subtotal: float
    payment_option: Optional[str]
    delivery: bool = False
    delivery_km: float = 0.0
    delivery_charge: float = 0.0
    cash_on_delivery: bool = False
    note: Optional[str] = None

class BookingOut(BookingCreate):
    id: int

    class Config:
        orm_mode = True
