from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, JSON 
from enum import Enum
from sqlalchemy.orm import relationship
from database import Base

class ServiceTypeEnum(enum.Enum):
    BY_HAND = "By Hand Wash"
    MACHINE = "Machine Wash"
    PREMIUM = "Premium Laundry Service"


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("new_users.id"), nullable=False)
    
    # Storing list of items as JSON
    items = Column(JSON, nullable=False) 
    price_tag = Column(Float, nullable=False, default=0.0)
    subtotal = Column(Float, nullable=False)
    payment_option = Column(String(50), nullable=True)
    delivery = Column(Boolean, default=False)
    delivery_km = Column(Float, default=0.0)
    delivery_charge = Column(Float, default=0.0)
    cash_on_delivery = Column(Boolean, default=False)
    note = Column(String(255), nullable=True)
    service_type = Column(Enum(ServiceTypeEnum), nullable=False, default=ServiceTypeEnum.MACHINE)
    # Relationship to user table
    user = relationship("DBUser", back_populates="bookings")
