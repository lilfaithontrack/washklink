from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from enum import Enum
from .order import Order

class DriverStatus(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    SUSPENDED = "suspended"

class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    vehicle_type = Column(String(50), nullable=False)
    vehicle_plate = Column(String(20), unique=True, nullable=False)
    
    # Location and service area
    base_lat = Column(Float, nullable=False)
    base_lng = Column(Float, nullable=False)
    service_radius = Column(Float, nullable=False, default=5000)  # Service radius in meters
    current_lat = Column(Float)
    current_lng = Column(Float)
    last_location_update = Column(DateTime)

    # Status and approval
    status = Column(String(20), nullable=False, default=DriverStatus.OFFLINE)
    is_active = Column(Boolean, default=False)
    approval_status = Column(String(20), nullable=False, default="pending")
    approved_by = Column(Integer, ForeignKey("new_users.id"))
    approved_at = Column(DateTime)
    rejection_reason = Column(String(255))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    approver = relationship("models.users.DBUser", foreign_keys=[approved_by])
    orders = relationship("db.models.order.Order", back_populates="driver")

    @property
    def phone(self):
        return self.phone_number