from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    PICKED_UP = "picked_up"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("new_users.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id"))
    provider_id = Column(Integer, ForeignKey("service_providers.id"))
    
    # Order details
    status = Column(String(20), nullable=False, default=OrderStatus.PENDING)
    total_amount = Column(Float, nullable=False)
    pickup_address = Column(String(255), nullable=False)
    delivery_address = Column(String(255), nullable=False)
    pickup_lat = Column(Float)
    pickup_lng = Column(Float)
    delivery_lat = Column(Float)
    delivery_lng = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    accepted_at = Column(DateTime)
    picked_up_at = Column(DateTime)
    completed_at = Column(DateTime)
    cancelled_at = Column(DateTime)
    
    # Additional info
    cancellation_reason = Column(String(255))
    notes = Column(String(500))

    # Relationships
    user = relationship("models.users.DBUser", back_populates="orders")
    driver = relationship("db.models.driver.Driver", back_populates="orders")
    provider = relationship("db.models.service_provider.ServiceProvider", back_populates="orders")
    payments = relationship("db.models.payment.Payment", back_populates="order")
    items = relationship("db.models.order_item.OrderItem", back_populates="order", cascade="all, delete-orphan") 