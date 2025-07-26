from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, JSON, Enum as SQLEnum, DateTime, Text
from enum import Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from models.users import DBUser
from db.models.service_provider import ServiceProvider
from db.models.driver import Driver

class ServiceTypeEnum(Enum):
    BY_HAND = "BY_HAND"
    PREMIUM = "PREMIUM"
    MACHINE_WASH = "MACHINE_WASH"

class OrderStatus(Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    IN_PROGRESS = "IN_PROGRESS"
    READY_FOR_PICKUP = "READY_FOR_PICKUP"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("new_users.id"), nullable=False)
    service_provider_id = Column(Integer, ForeignKey("service_providers.id"), nullable=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)
    
    # Customer location
    pickup_latitude = Column(Float, nullable=True)
    pickup_longitude = Column(Float, nullable=True)
    pickup_address = Column(String(500), nullable=True)
    
    # Delivery location (if different from pickup)
    delivery_latitude = Column(Float, nullable=True)
    delivery_longitude = Column(Float, nullable=True)
    delivery_address = Column(String(500), nullable=True)
    
    # Order details
    items = Column(JSON, nullable=False) 
    price_tag = Column(Float, nullable=False, default=0.0)
    subtotal = Column(Float, nullable=False)
    payment_option = Column(String(50), nullable=True)
    delivery = Column(Boolean, default=False)
    delivery_km = Column(Float, default=0.0)
    delivery_charge = Column(Float, default=0.0)
    cash_on_delivery = Column(Boolean, default=False)
    note = Column(Text, nullable=True)
    
    # Status and timing
    status = Column(String(20), default=OrderStatus.PENDING.value)
    service_type = Column(String(50), nullable=False, default=ServiceTypeEnum.MACHINE_WASH.value)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    assigned_at = Column(DateTime, nullable=True)
    accepted_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Estimated times
    estimated_pickup_time = Column(DateTime, nullable=True)
    estimated_completion_time = Column(DateTime, nullable=True)
    estimated_delivery_time = Column(DateTime, nullable=True)
    
    # Assignment tracking
    assignment_attempts = Column(Integer, default=0)
    max_assignment_radius = Column(Float, default=5.0)  # km
    
    # Special instructions
    special_instructions = Column(Text, nullable=True)
    priority_level = Column(Integer, default=1)  # 1=normal, 2=high, 3=urgent
    
    # Relationships
    user = relationship("models.users.DBUser", foreign_keys=[user_id])
    service_provider = relationship("db.models.service_provider.ServiceProvider", foreign_keys=[service_provider_id])
    driver = relationship("db.models.driver.Driver", foreign_keys=[driver_id])