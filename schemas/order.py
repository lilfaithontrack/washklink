from pydantic import BaseModel, Field, condecimal, constr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    PICKED_UP = "picked_up"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class OrderBase(BaseModel):
    user_id: int
    driver_id: Optional[int] = None
    provider_id: Optional[int] = None
    status: OrderStatus = OrderStatus.PENDING
    total_amount: float = Field(..., ge=0)
    pickup_address: constr(min_length=1, max_length=255)
    delivery_address: constr(min_length=1, max_length=255)
    pickup_lat: Optional[float] = Field(None, ge=-90, le=90)
    pickup_lng: Optional[float] = Field(None, ge=-180, le=180)
    delivery_lat: Optional[float] = Field(None, ge=-90, le=90)
    delivery_lng: Optional[float] = Field(None, ge=-180, le=180)
    notes: Optional[str] = Field(None, max_length=500)

class OrderItemBase(BaseModel):
    product_id: int
    category_id: int
    quantity: int
    price: float
    service_type: str

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: int
    class Config:
        from_attributes = True

# Update OrderCreate to include items
class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    user_id: Optional[int] = None
    driver_id: Optional[int] = None
    provider_id: Optional[int] = None
    status: Optional[OrderStatus] = None
    total_amount: Optional[float] = Field(None, ge=0)
    pickup_address: Optional[constr(min_length=1, max_length=255)] = None
    delivery_address: Optional[constr(min_length=1, max_length=255)] = None
    pickup_lat: Optional[float] = Field(None, ge=-90, le=90)
    pickup_lng: Optional[float] = Field(None, ge=-180, le=180)
    delivery_lat: Optional[float] = Field(None, ge=-90, le=90)
    delivery_lng: Optional[float] = Field(None, ge=-180, le=180)
    notes: Optional[str] = Field(None, max_length=500)
    cancellation_reason: Optional[str] = Field(None, max_length=255)
    accepted_at: Optional[datetime] = None
    picked_up_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

# Update OrderResponse to include items
class OrderResponse(OrderBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    picked_up_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True 