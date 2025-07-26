from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from enum import Enum

class ProviderStatus(str, Enum):
    ACTIVE = "active"
    OFFLINE = "offline"
    BUSY = "busy"
    SUSPENDED = "suspended"

class ServiceProvider(Base):
    __tablename__ = "service_providers"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50))
    last_name = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(15), unique=True, nullable=False)
    address = Column(String(255), nullable=False)
    
    # Business details
    business_name = Column(String(100))
    business_license = Column(String(50), unique=True)
    description = Column(String(500))
    
    # Location
    latitude = Column(Float)
    longitude = Column(Float)
    service_radius = Column(Float, default=5.0)  # Service radius in kilometers
    nearby_condominum = Column(String(255))
    
    # Equipment
    washing_machine = Column(Boolean, default=True)
    has_dryer = Column(Boolean, default=False)
    has_iron = Column(Boolean, default=True)
    
    # Service capacity
    max_daily_orders = Column(Integer, default=20)
    current_order_count = Column(Integer, default=0)
    total_orders_completed = Column(Integer, default=0)
    average_completion_time = Column(Float)  # in hours
    rating = Column(Float, default=0.0)
    
    # Status and verification
    status = Column(String(20), nullable=False, default=ProviderStatus.OFFLINE.value)
    is_active = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    approval_status = Column(String(20), nullable=False, default="pending")
    approved_by = Column(Integer, ForeignKey("new_users.id"))
    approved_at = Column(DateTime)
    rejection_reason = Column(String(255))
    
    # Personal info
    date_of_birth = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active = Column(DateTime)

    # Relationships
    approver = relationship("DBUser", foreign_keys=[approved_by])
    orders = relationship("Order", back_populates="provider")
    
    @property
    def full_name(self) -> str:
        """Returns the provider's full name"""
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.middle_name:
            parts.append(self.middle_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts) if parts else "" 