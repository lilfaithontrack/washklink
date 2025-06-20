from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float, Date
from database import Base
from datetime import date  # ✅ import the date class

class ServiceProvider(Base):
    __tablename__ = "service_provider"

    id = Column(Integer, unique=True, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    phone_number = Column(Integer, unique=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    date_of_birth = Column(Date, nullable=False, default=date(2000, 1, 1))  # ✅ fixed
    washing_machine = Column(Boolean, default=True)
    nearby_condominum = Column(String, nullable=False)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
