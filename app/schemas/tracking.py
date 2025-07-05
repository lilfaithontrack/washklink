from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class TrackingEventType(str, Enum):
    LOCATION_UPDATE = "location_update"
    STATUS_CHANGE = "status_change"
    DELIVERY_START = "delivery_start"
    DELIVERY_COMPLETE = "delivery_complete"
    ORDER_ASSIGNED = "order_assigned"

class LocationData(BaseModel):
    latitude: float
    longitude: float
    heading: Optional[float] = None
    speed: Optional[float] = None
    accuracy: Optional[float] = None
    timestamp: datetime

class TrackingEvent(BaseModel):
    event_type: TrackingEventType
    driver_id: Optional[int] = None
    order_id: Optional[int] = None
    location_data: Optional[LocationData] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime

class DeliveryTrackingInfo(BaseModel):
    order_id: int
    driver_id: int
    driver_name: str
    driver_phone: str
    vehicle_info: str
    current_location: Optional[LocationData] = None
    estimated_arrival: Optional[datetime] = None
    distance_remaining: Optional[float] = None
    status: str

class DriverLocationResponse(BaseModel):
    driver_id: int
    latitude: float
    longitude: float
    heading: Optional[float] = None
    speed: Optional[float] = None
    timestamp: datetime
    status: str
    is_on_delivery: bool
    current_order_id: Optional[int] = None

class TrackingAnalytics(BaseModel):
    total_active_drivers: int
    drivers_by_status: Dict[str, int]
    average_speed: float
    active_deliveries: int
    total_distance_covered: Optional[float] = None
    average_delivery_time: Optional[float] = None