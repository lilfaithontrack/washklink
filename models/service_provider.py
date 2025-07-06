from sqlalchemy import Column, Integer, String, Boolean, Float, Date, Enum as SQLEnum, DateTime, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import date, datetime
from enum import Enum

class ProviderStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BUSY = "busy"
    OFFLINE = "offline"
    SUSPENDED = "suspended"

class ServiceProvider(Base):
    __tablename__ = "service_provider"

    id = Column(Integer, unique=True, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    phone_number = Column(Integer, unique=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=True)
    
    # Status and availability
    status = Column(SQLEnum(ProviderStatus), default=ProviderStatus.ACTIVE)
    is_active = Column(Boolean, default=True)
    is_available = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Location details
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    service_radius = Column(Float, default=10.0)  # km radius they serve
    nearby_condominum = Column(String, nullable=False)
    
    # Service details
    date_of_birth = Column(Date, nullable=False, default=date(2000, 1, 1))
    washing_machine = Column(Boolean, default=True)
    has_dryer = Column(Boolean, default=False)
    has_iron = Column(Boolean, default=True)
    
    # Capacity and performance
    max_daily_orders = Column(Integer, default=20)
    current_order_count = Column(Integer, default=0)
    average_completion_time = Column(Float, default=24.0)  # hours
    rating = Column(Float, default=0.0)
    total_orders_completed = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    # Business details
    business_name = Column(String, nullable=True)
    business_license = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    
    # Relationships
    orders = relationship("Booking", back_populates="service_provider")