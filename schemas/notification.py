from pydantic import BaseModel
from typing import Optional
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

class NotificationCreate(BaseModel):
    title: str
    message: str
    type: NotificationType = NotificationType.INFO
    category: NotificationCategory = NotificationCategory.SYSTEM
    link: Optional[str] = None
    reference_id: Optional[int] = None

class NotificationUpdate(BaseModel):
    is_read: bool = True

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    type: NotificationType
    category: NotificationCategory
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime]
    link: Optional[str]
    reference_id: Optional[int]

    class Config:
        from_attributes = True 