from sqlalchemy import Column, Integer, String, Boolean, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import date

class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False)
    license_number = Column(String(50), unique=True, nullable=False)
    vehicle_type = Column(String(50), nullable=False)  # motorcycle, car, van
    vehicle_plate = Column(String(20), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    is_available = Column(Boolean, default=True)
    current_latitude = Column(Float, nullable=True)
    current_longitude = Column(Float, nullable=True)
    rating = Column(Float, default=0.0)
    total_deliveries = Column(Integer, default=0)
    date_joined = Column(Date, default=date.today)