from pydantic import BaseModel
from typing import Optional

# Shared Base
class UserBase(BaseModel):
    full_name: str
    phone_number: Optional[str]
    email: str

# For requesting OTP (basic)
class UserCreate(BaseModel):
    phone_number: str

# For verifying OTP or Google Auth
class UserVerify(BaseModel):
    full_name: str
    phone_number: Optional[str]
    email: str
    otp_code: Optional[str] = None  # Optional for Google Auth

# Response schema
class UserResponse(BaseModel):
    id: int
    full_name: str
    phone_number: str
    email: str
    is_active: bool

    class Config:
        orm_mode = True
