from sqlalchemy import Column, Integer, Boolean, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class DBUser(Base):
    __tablename__ = "new_users"
    
    id = Column(Integer, primary_key=True, index=True, unique=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    phone_number = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)

    # One-to-many: one user can have many bookings
    bookings = relationship("Booking", back_populates="user")

# Legacy user model (keeping for backward compatibility)
class User(Base):
    __tablename__ = "tbl_user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    ccode = Column(String, nullable=False)
    mobile = Column(String, nullable=False)
    refercode = Column(Integer, nullable=False)
    parentcode = Column(Integer, nullable=True)
    password = Column(String, nullable=False)
    registartion_date = Column(String, nullable=False)
    status = Column(Integer, nullable=False, default=1)
    wallet = Column(Integer, nullable=False, default=0)
    status_login = Column(Integer, nullable=False)