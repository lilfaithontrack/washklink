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
    user_id: Optional[str] = None  # Made optional since backend sets it from current_user
    driver_id: Optional[str] = None  # Changed to string for ObjectId compatibility
    provider_id: Optional[str] = None  # Changed to string for ObjectId compatibility
    status: OrderStatus = OrderStatus.PENDING
    total_amount: float = Field(..., ge=0)
    pickup_address: constr(min_length=1, max_length=255)
    delivery_address: constr(min_length=1, max_length=255)
    pickup_lat: Optional[float] = Field(None, ge=-90, le=90)
    pickup_lng: Optional[float] = Field(None, ge=-180, le=180)
    delivery_lat: Optional[float] = Field(None, ge=-90, le=90)
    delivery_lng: Optional[float] = Field(None, ge=-180, le=180)
    notes: Optional[str] = Field(None, max_length=500)
    # Add payment fields
    payment_method: Optional[str] = None
    cash_on_delivery: bool = False

class OrderItemBase(BaseModel):
    product_id: str  # Changed to string for ObjectId compatibility
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
    user_id: Optional[str] = None  # Changed to string for ObjectId compatibility
    driver_id: Optional[str] = None  # Changed to string for ObjectId compatibility
    provider_id: Optional[str] = None  # Changed to string for ObjectId compatibility
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
    payment_method: Optional[str] = None
    cash_on_delivery: Optional[bool] = None

# Update OrderResponse to include items
class OrderResponse(BaseModel):
    id: str  # Changed to string for ObjectId compatibility
    user_id: str  # Required in response
    driver_id: Optional[str] = None
    provider_id: Optional[str] = None
    status: OrderStatus
    total_amount: float
    pickup_address: str
    delivery_address: str
    pickup_lat: Optional[float] = None
    pickup_lng: Optional[float] = None
    delivery_lat: Optional[float] = None
    delivery_lng: Optional[float] = None
    notes: Optional[str] = None
    payment_method: Optional[str] = None
    cash_on_delivery: bool = False
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