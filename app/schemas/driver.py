from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime
from enum import Enum

class DriverStatus(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    ON_DELIVERY = "on_delivery"
    SUSPENDED = "suspended"

class VehicleType(str, Enum):
    MOTORCYCLE = "motorcycle"
    CAR = "car"
    VAN = "van"
    BICYCLE = "bicycle"

class DriverCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    license_number: str
    vehicle_type: VehicleType
    vehicle_plate: str
    vehicle_model: Optional[str] = None
    vehicle_color: Optional[str] = None
    service_radius: float = 15.0
    base_latitude: Optional[float] = None
    base_longitude: Optional[float] = None

class DriverUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    vehicle_type: Optional[VehicleType] = None
    vehicle_plate: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_color: Optional[str] = None
    service_radius: Optional[float] = None
    status: Optional[DriverStatus] = None
    is_active: Optional[bool] = None

class DriverResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone_number: str
    license_number: str
    vehicle_type: VehicleType
    vehicle_plate: str
    vehicle_model: Optional[str]
    vehicle_color: Optional[str]
    status: DriverStatus
    is_active: bool
    is_verified: bool
    current_latitude: Optional[float]
    current_longitude: Optional[float]
    last_location_update: Optional[datetime]
    service_radius: float
    base_latitude: Optional[float]
    base_longitude: Optional[float]
    rating: float
    total_deliveries: int
    successful_deliveries: int
    average_delivery_time: float
    date_joined: date
    created_at: datetime
    updated_at: datetime
    last_active: datetime
    current_order_id: Optional[int]

    class Config:
        from_attributes = True

class LocationUpdate(BaseModel):
    latitude: float
    longitude: float