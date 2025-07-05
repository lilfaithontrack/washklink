from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from datetime import datetime

class ServiceTypeEnum(str, Enum):
    BY_HAND = "By Hand Wash"
    MACHINE = "Machine Wash"
    PREMIUM = "Premium Laundry Service"
    MACHINE_WASH = "Machine Wash"

class OrderStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    READY_FOR_PICKUP = "ready_for_pickup"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class BookingItem(BaseModel):
    product_id: int
    category_id: int
    quantity: int
    price: float
    service_type: Optional[ServiceTypeEnum] = None 
    
    class Config:
        from_attributes = True

class BookingCreate(BaseModel):
    user_id: int
    items: Optional[List[BookingItem]] = []
    payment_option: Optional[str]
    delivery: bool = False
    delivery_km: float = 0.0
    cash_on_delivery: bool = False
    note: Optional[str] = None
    
    # Location data
    pickup_latitude: Optional[float] = None
    pickup_longitude: Optional[float] = None
    pickup_address: Optional[str] = None
    delivery_latitude: Optional[float] = None
    delivery_longitude: Optional[float] = None
    delivery_address: Optional[str] = None
    
    # Assignment preferences
    preferred_provider_id: Optional[int] = None
    special_instructions: Optional[str] = None
    priority_level: int = 1  # 1=normal, 2=high, 3=urgent

class BookingOut(BaseModel):
    id: int
    user_id: int
    service_provider_id: Optional[int] = None
    driver_id: Optional[int] = None
    
    items: Optional[List[BookingItem]] = []
    price_tag: float
    subtotal: float
    payment_option: Optional[str]
    delivery: bool
    delivery_km: float
    delivery_charge: float
    cash_on_delivery: bool
    note: Optional[str]
    
    # Location data
    pickup_latitude: Optional[float] = None
    pickup_longitude: Optional[float] = None
    pickup_address: Optional[str] = None
    delivery_latitude: Optional[float] = None
    delivery_longitude: Optional[float] = None
    delivery_address: Optional[str] = None
    
    # Status and timing
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    assigned_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Estimates
    estimated_pickup_time: Optional[datetime] = None
    estimated_completion_time: Optional[datetime] = None
    estimated_delivery_time: Optional[datetime] = None
    
    # Additional info
    special_instructions: Optional[str] = None
    priority_level: int = 1
    assignment_attempts: int = 0

    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    notes: Optional[str] = None

class LocationUpdate(BaseModel):
    latitude: float
    longitude: float
    address: Optional[str] = None