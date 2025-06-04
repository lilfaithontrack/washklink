from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("new_users.id"))
    item = Column(String, nullable=False)  # e.g., checklist title or item name
    price_tag = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    payment_option = Column(String, nullable=True)  # e.g., '2.5%', 'amount'
    delivery = Column(Boolean, default=False)
    delivery_km = Column(Float, default=0.0)
    delivery_charge = Column(Float, default=0.0)
    cash_on_delivery = Column(Boolean, default=False)
    note = Column(String, nullable=True)

    user = relationship("User", back_populates="bookings")

