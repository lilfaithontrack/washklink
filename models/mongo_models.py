from beanie import Document, Link, before_event, Replace, Insert, PydanticObjectId
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List, Literal, Any
from datetime import datetime
from enum import Enum
import pymongo

# Note: Using Document directly instead of custom base class to avoid version compatibility issues

# Enums
class UserRole(str, Enum):
    USER = "user"
    MANAGER = "manager"
    ADMIN = "admin"

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

class ProviderStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BUSY = "busy"
    OFFLINE = "offline"
    SUSPENDED = "suspended"

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
    FOOT = "foot"

class ServiceType(str, Enum):
    BY_HAND_WASH = "By Hand Wash"
    PREMIUM_LAUNDRY = "Premium Laundry Service"
    MACHINE_WASH = "Machine Wash"

class PaymentMethod(str, Enum):
    CHAPA = "chapa"
    TELEBIRR = "telebirr"
    CASH_ON_DELIVERY = "cash_on_delivery"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# User Model
class User(Document):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    full_name: str
    phone_number: str = Field(unique=True)
    email: Optional[EmailStr] = Field(unique=True, default=None)
    hashed_password: Optional[str] = None
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    @before_event([Replace, Insert])
    def update_timestamp(self):
        self.updated_at = datetime.utcnow()

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    @property
    def is_manager(self) -> bool:
        return self.role == UserRole.MANAGER

    @property
    def has_admin_access(self) -> bool:
        return self.role in [UserRole.ADMIN, UserRole.MANAGER]

    class Settings:
        name = "users"
        indexes = [
            "email",
            "phone_number",
            "role",
            "is_active",
        ]

# Service Provider Model
class ServiceProvider(Document):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    first_name: str
    middle_name: str
    last_name: str
    address: str
    phone_number: int = Field(unique=True)
    email: EmailStr = Field(unique=True)
    hashed_password: Optional[str] = None
    status: ProviderStatus = ProviderStatus.OFFLINE
    is_active: bool = True
    is_available: bool = True
    is_verified: bool = False
    
    # Location
    latitude: float
    longitude: float
    service_radius: float = 10.0
    nearby_condominum: str
    
    # Personal info
    date_of_birth: datetime = Field(default=datetime(2000, 1, 1))
    
    # Equipment
    washing_machine: bool = True
    has_dryer: bool = False
    has_iron: bool = True
    
    # Service capacity
    max_daily_orders: int = 20
    current_order_count: int = 0
    average_completion_time: float = 24.0  # hours
    rating: float = 0.0
    total_orders_completed: int = 0
    
    # Business details
    business_name: Optional[str] = None
    business_license: Optional[str] = None
    description: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)

    @before_event([Replace, Insert])
    def update_timestamp(self):
        self.updated_at = datetime.utcnow()

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.middle_name} {self.last_name}".strip()

    class Settings:
        name = "service_providers"
        indexes = [
            "email",
            "phone_number",
            "status",
            [("latitude", pymongo.ASCENDING), ("longitude", pymongo.ASCENDING)],
            [("is_active", pymongo.ASCENDING), ("is_available", pymongo.ASCENDING)],
        ]

# Driver Model
class Driver(Document):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    first_name: str
    last_name: str
    email: EmailStr = Field(unique=True)
    phone_number: str = Field(unique=True)
    license_number: str = Field(unique=True)
    
    # Vehicle details
    vehicle_type: VehicleType
    vehicle_plate: str = Field(unique=True)
    vehicle_model: Optional[str] = None
    vehicle_color: Optional[str] = None
    
    # Status and verification
    status: DriverStatus = DriverStatus.AVAILABLE
    is_active: bool = True
    is_verified: bool = False
    
    # Location
    current_latitude: Optional[float] = None
    current_longitude: Optional[float] = None
    last_location_update: Optional[datetime] = None
    service_radius: float = 15.0
    base_latitude: Optional[float] = None
    base_longitude: Optional[float] = None
    
    # Performance metrics
    rating: float = 0.0
    total_deliveries: int = 0
    successful_deliveries: int = 0
    average_delivery_time: float = 30.0  # minutes
    
    # Current assignment
    current_order_id: Optional[PydanticObjectId] = None
    
    # Timestamps
    date_joined: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)

    @before_event([Replace, Insert])
    def update_timestamp(self):
        self.updated_at = datetime.utcnow()

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    class Settings:
        name = "drivers"
        indexes = [
            "email",
            "phone_number",
            "license_number",
            "vehicle_plate",
            "status",
            [("current_latitude", pymongo.ASCENDING), ("current_longitude", pymongo.ASCENDING)],
            [("is_active", pymongo.ASCENDING), ("status", pymongo.ASCENDING)],
        ]

# Item Model
class Item(Document):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str
    description: Optional[str] = None
    price: float
    currency: str = "ETB"
    category: Optional[str] = None
    is_active: bool = True
    estimated_time: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @before_event([Replace, Insert])
    def update_timestamp(self):
        self.updated_at = datetime.utcnow()

    class Settings:
        name = "items"
        indexes = [
            "category",
            "is_active",
        ]

# Order Item Model - This is a BaseModel, not a Document
class OrderItem(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    product_id: str  # Changed to string to handle both ObjectId and integer IDs
    category_id: int
    quantity: int
    price: float
    service_type: Optional[str] = None

# Order Model
class Order(Document):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    user_id: PydanticObjectId
    service_provider_id: Optional[PydanticObjectId] = None
    driver_id: Optional[PydanticObjectId] = None
    
    # Location details
    pickup_latitude: Optional[float] = None
    pickup_longitude: Optional[float] = None
    pickup_address: Optional[str] = None
    delivery_latitude: Optional[float] = None
    delivery_longitude: Optional[float] = None
    delivery_address: Optional[str] = None
    
    # Order details
    price_tag: float = 0.0
    subtotal: float
    payment_option: Optional[str] = None
    delivery: bool = False
    delivery_km: float = 0.0
    delivery_charge: float = 0.0
    cash_on_delivery: bool = False
    note: Optional[str] = None
    
    # Status and service
    status: OrderStatus = OrderStatus.PENDING
    service_type: ServiceType = ServiceType.MACHINE_WASH
    
    # Order items
    items: List[OrderItem] = []
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    assigned_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_pickup_time: Optional[datetime] = None
    estimated_completion_time: Optional[datetime] = None
    estimated_delivery_time: Optional[datetime] = None
    
    # Assignment details
    assignment_attempts: int = 0
    max_assignment_radius: float = 5.0
    special_instructions: Optional[str] = None
    priority_level: int = 1

    @before_event([Replace, Insert])
    def update_timestamp(self):
        self.updated_at = datetime.utcnow()

    class Settings:
        name = "orders"
        indexes = [
            "user_id",
            "service_provider_id",
            "driver_id",
            "status",
            "created_at",
            [("pickup_latitude", pymongo.ASCENDING), ("pickup_longitude", pymongo.ASCENDING)],
            [("delivery_latitude", pymongo.ASCENDING), ("delivery_longitude", pymongo.ASCENDING)],
        ]

# Payment Model
class Payment(Document):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    order_id: PydanticObjectId
    user_id: PydanticObjectId
    amount: float
    currency: str = "ETB"
    payment_method: PaymentMethod
    status: PaymentStatus = PaymentStatus.PENDING
    external_transaction_id: Optional[str] = None
    gateway_reference: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    @before_event([Replace, Insert])
    def update_timestamp(self):
        self.updated_at = datetime.utcnow()

    class Settings:
        name = "payments"
        indexes = [
            "order_id",
            "user_id",
            "status",
            "payment_method",
            "created_at",
            "external_transaction_id",
        ]

# Notification Model
class Notification(Document):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    user_id: PydanticObjectId
    title: str
    message: str
    type: str  # e.g., 'order_update', 'payment_confirmation', etc.
    is_read: bool = False
    data: Optional[dict] = None  # Additional data for the notification
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

    class Settings:
        name = "notifications"
        indexes = [
            "user_id",
            "is_read",
            "created_at",
            "expires_at",
        ] 