from pydantic import BaseModel, EmailStr, constr, confloat
from typing import Optional
from datetime import datetime
from enum import Enum

class DriverStatus(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    SUSPENDED = "suspended"

class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class DriverBase(BaseModel):
    first_name: constr(min_length=2, max_length=50)
    last_name: constr(min_length=2, max_length=50)
    email: EmailStr
    phone: constr(min_length=10, max_length=15)
    vehicle_type: str
    vehicle_plate: str
    base_lat: confloat(ge=-90, le=90)
    base_lng: confloat(ge=-180, le=180)
    service_radius: confloat(ge=1000, le=20000)  # Service radius in meters (1km to 20km)

class DriverCreate(DriverBase):
    password: str

class DriverUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    vehicle_type: Optional[str] = None
    vehicle_plate: Optional[str] = None
    base_lat: Optional[float] = None
    base_lng: Optional[float] = None
    service_radius: Optional[float] = None
    status: Optional[DriverStatus] = None
    is_active: Optional[bool] = None

class DriverApproval(BaseModel):
    approval_status: str  # "approved" or "rejected"
    rejection_reason: Optional[str] = None

class DriverResponse(DriverBase):
    id: int
    status: DriverStatus
    is_active: bool
    approval_status: str
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class LocationUpdate(BaseModel):
    latitude: float
    longitude: float