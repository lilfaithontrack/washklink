from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class ServiceTypeEnum(str, Enum):
    BY_HAND = "BY_HAND"
    MACHINE_WASH = "MACHINE_WASH"
    PREMIUM = "PREMIUM"

class BookingItem(BaseModel):
    product_id: int
    category_id: int
    quantity: int
    price: float
    service_type: Optional[ServiceTypeEnum] = None 
    class Config:
        from_attributes = True  # Pydantic V2: replaces orm_mode

class BookingCreate(BaseModel):
    user_id: int
    items: Optional[List[BookingItem]] = []
    payment_option: Optional[str]
    delivery: bool = False
    delivery_km: float = 0.0
    cash_on_delivery: bool = False
    note: Optional[str] = None

class BookingOut(BaseModel):
    id: int
    user_id: int
    items: Optional[List[dict]] = []  # Changed to dict to handle JSON data
    price_tag: float
    subtotal: float
    payment_option: Optional[str]
    delivery: bool
    delivery_km: float
    delivery_charge: float
    cash_on_delivery: bool
    note: Optional[str]

    class Config:
        from_attributes = True  # Pydantic V2: replaces orm_mode
