from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, JSON, Enum as SQLEnum, DateTime, Text
from enum import Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class ServiceTypeEnum(Enum):
    BY_HAND = "By Hand Wash"
    MACHINE = "Machine Wash"
    PREMIUM = "Premium Laundry Service"
    MACHINE_WASH = 'Machine Wash'

class OrderStatus(Enum):
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

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("new_users.id"), nullable=False)
    service_provider_id = Column(Integer, ForeignKey("service_provider.id"), nullable=True)
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
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)
    service_type = Column(SQLEnum(ServiceTypeEnum), nullable=False, default=ServiceTypeEnum.MACHINE)
    
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
    user = relationship("DBUser", back_populates="bookings")
    service_provider = relationship("ServiceProvider", back_populates="orders")
    driver = relationship("Driver", back_populates="orders")