from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from enum import Enum

class NotificationType(str, Enum):
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"

class NotificationCategory(str, Enum):
    DRIVER = "driver"
    PROVIDER = "provider"
    ORDER = "order"
    PAYMENT = "payment"
    SYSTEM = "system"

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("new_users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(20), nullable=False, default=NotificationType.INFO)
    category = Column(String(20), nullable=False, default=NotificationCategory.SYSTEM)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)
    link = Column(String(255), nullable=True)  # Optional link to related content
    reference_id = Column(Integer, nullable=True)  # ID of related item (order, driver, etc.)

    # Relationships
    user = relationship("models.users.DBUser", back_populates="notifications") 