from sqlalchemy import Column, Integer, Boolean, String, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from database import Base
from enum import Enum
from datetime import datetime

class UserRole(Enum):
    USER = "user"
    MANAGER = "manager"
    ADMIN = "admin"

class DBUser(Base):
    __tablename__ = "new_users"
    
    id = Column(Integer, primary_key=True, index=True, unique=True)
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False)  # Required for all users
    email = Column(String(255), unique=True, nullable=True)  # Only for admin/manager
    password = Column(String(255), nullable=True)  # Only for admin/manager
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # One-to-many: one user can have many bookings
    bookings = relationship("Booking", back_populates="user")

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    @property
    def is_manager(self) -> bool:
        return self.role == UserRole.MANAGER

    @property
    def is_user(self) -> bool:
        return self.role == UserRole.USER

    @property
    def has_admin_access(self) -> bool:
        return self.role in [UserRole.ADMIN, UserRole.MANAGER]