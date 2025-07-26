from pydantic import BaseModel, StringConstraints, EmailStr
from typing import Optional, Annotated

# Optional phone with +251 validation
PhoneStr = Annotated[str, StringConstraints(pattern=r'^\+2519\d{8}$')]

# Shared Base
class UserBase(BaseModel):
    full_name: str
    phone: Optional[PhoneStr]
    email: Optional[EmailStr] = None

# For requesting OTP
class UserCreate(BaseModel):
    phone: PhoneStr
    full_name: str

# For verifying OTP and logging in
class UserVerify(UserCreate):  # Inherits full_name, phone
    email: Optional[EmailStr] = None
    otp_code: str

# For updating profile
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: PhoneStr
    otp_code: str

# Auth response (simplified for legacy compatibility)
class UserResponse(BaseModel):
    id: int
    full_name: str
    phone: Optional[str]
    email: Optional[str]
    role: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True