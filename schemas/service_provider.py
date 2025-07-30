from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime
from enum import Enum

class ProviderStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BUSY = "busy"
    OFFLINE = "offline"
    SUSPENDED = "suspended"

class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class ServiceProviderCreate(BaseModel):
    email: EmailStr
    first_name: str
    middle_name: str
    last_name: str
    address: str = Field(..., min_length=1, max_length=100)
    nearby_condominum: str = Field(..., min_length=1, max_length=100)
    phone_number: int
    date_of_birth: datetime
    washing_machine: bool = True
    has_dryer: bool = False
    has_iron: bool = True
    longitude: float
    latitude: float
    service_radius: Optional[float] = 10.0
    business_name: Optional[str] = None
    business_license: Optional[str] = None
    description: Optional[str] = None

class ServiceProviderUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    address: Optional[str] = None
    nearby_condominum: Optional[str] = None
    phone_number: Optional[int] = None
    washing_machine: Optional[bool] = None
    has_dryer: Optional[bool] = None
    has_iron: Optional[bool] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    service_radius: Optional[float] = None
    business_name: Optional[str] = None
    business_license: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProviderStatus] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    max_daily_orders: Optional[int] = None

class ServiceProviderApproval(BaseModel):
    approval_status: str  # "approved" or "rejected"
    rejection_reason: Optional[str] = None

class ServiceProviderResponse(BaseModel):
    id: str  # MongoDB uses string IDs
    email: EmailStr
    first_name: str
    middle_name: str
    last_name: str
    full_name: str
    address: str
    nearby_condominum: str
    phone_number: int
    date_of_birth: datetime
    washing_machine: bool
    has_dryer: bool
    has_iron: bool
    longitude: float
    latitude: float
    service_radius: float
    status: ProviderStatus
    is_active: bool
    is_available: bool
    is_verified: bool
    business_name: Optional[str]
    business_license: Optional[str]
    description: Optional[str]
    rating: float
    total_orders_completed: int
    max_daily_orders: int
    current_order_count: int
    average_completion_time: float
    created_at: datetime
    updated_at: datetime
    last_active: datetime

    class Config:
        from_attributes = True
