from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
from enum import Enum
from datetime import datetime

class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PaymentMethod(Enum):
    CHAPA = "chapa"
    TELEBIRR = "telebirr"
    CASH_ON_DELIVERY = "cash_on_delivery"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("new_users.id"), nullable=False)
    
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="ETB")
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # External payment gateway references
    external_transaction_id = Column(String(255), nullable=True)
    gateway_reference = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    order = relationship("Booking", backref="payments")
    user = relationship("DBUser", backref="payments")