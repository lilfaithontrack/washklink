from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("new_users.id"))
    items = Column(JSON)
    price_tag = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    payment_option = Column(String(50), nullable=True)
    delivery = Column(Boolean, default=False)
    delivery_km = Column(Float, default=0.0)
    delivery_charge = Column(Float, default=0.0)
    cash_on_delivery = Column(Boolean, default=False)
    note = Column(String(255), nullable=True)

    user = relationship("DBUser", back_populates="bookings")
