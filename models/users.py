from sqlalchemy import Column, Integer, Boolean, String, Enum as SQLEnum, DateTime, ForeignKey
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
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")  # admin, manager, user
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    orders = relationship("Order", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    payments = relationship("Payment", back_populates="user")

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

    @property
    def full_name(self) -> str:
        """Returns the user's full name by combining first_name and last_name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return ""