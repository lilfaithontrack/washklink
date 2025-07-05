from sqlalchemy import Column, Integer, String, Boolean, Float, Date, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import date, datetime
from enum import Enum

class DriverStatus(Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    ON_DELIVERY = "on_delivery"
    SUSPENDED = "suspended"

class VehicleType(Enum):
    MOTORCYCLE = "motorcycle"
    CAR = "car"
    VAN = "van"
    BICYCLE = "bicycle"

class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False)
    
    # License and vehicle info
    license_number = Column(String(50), unique=True, nullable=False)
    vehicle_type = Column(SQLEnum(VehicleType), nullable=False)
    vehicle_plate = Column(String(20), unique=True, nullable=False)
    vehicle_model = Column(String(100), nullable=True)
    vehicle_color = Column(String(50), nullable=True)
    
    # Status and availability
    status = Column(SQLEnum(DriverStatus), default=DriverStatus.AVAILABLE)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Location tracking
    current_latitude = Column(Float, nullable=True)
    current_longitude = Column(Float, nullable=True)
    last_location_update = Column(DateTime, nullable=True)
    
    # Service area
    service_radius = Column(Float, default=15.0)  # km radius they serve
    base_latitude = Column(Float, nullable=True)  # home base location
    base_longitude = Column(Float, nullable=True)
    
    # Performance metrics
    rating = Column(Float, default=0.0)
    total_deliveries = Column(Integer, default=0)
    successful_deliveries = Column(Integer, default=0)
    average_delivery_time = Column(Float, default=30.0)  # minutes
    
    # Timestamps
    date_joined = Column(Date, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    # Current assignment
    current_order_id = Column(Integer, ForeignKey("bookings.id"), nullable=True)
    
    # Relationships
    orders = relationship("Booking", back_populates="driver", foreign_keys="Booking.driver_id")
    current_order = relationship("Booking", foreign_keys=[current_order_id])