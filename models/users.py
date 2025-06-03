from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class DBUser(Base):
    __tablename__ = "new_users"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)  # ← fixed
    is_active = Column(Boolean, default=True)
