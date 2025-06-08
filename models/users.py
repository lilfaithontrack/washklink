from sqlalchemy import Column, Integer, Boolean, String
from sqlalchemy.orm import relationship
from database import Base

class DBUser(Base):
    __tablename__ = "new_users"
    
    id = Column(Integer, primary_key=True, index=True, unique=True)
    full_name = Column(String(255), nullable=False)  # full name from Google
    email = Column(String(255), unique=True, nullable=False)  # email from Google Auth
    phone_number = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)

    # One-to-many: one user can have many bookings
    bookings = relationship("Booking", back_populates="user")
