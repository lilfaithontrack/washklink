from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PaymentMethod(str, Enum):
    CHAPA = "chapa"
    TELEBIRR = "telebirr"
    CASH_ON_DELIVERY = "cash_on_delivery"

class PaymentInitiate(BaseModel):
    order_id: int
    amount: float
    payment_method: PaymentMethod
    return_url: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_name: Optional[str] = None

class PaymentCallback(BaseModel):
    transaction_id: str
    status: str
    reference: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = "ETB"

class PaymentResponse(BaseModel):
    id: int
    order_id: int
    user_id: int
    amount: float
    currency: str
    payment_method: PaymentMethod
    status: PaymentStatus
    external_transaction_id: Optional[str]
    gateway_reference: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

class PaymentInitiateResponse(BaseModel):
    status: str
    payment_url: Optional[str] = None
    transaction_reference: str
    message: str
    payment_id: Optional[int] = None