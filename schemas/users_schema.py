from pydantic import BaseModel, StringConstraints, EmailStr
from typing import Optional, Annotated

# Optional phone with +251 validation
PhoneNumberStr = Annotated[str, StringConstraints(pattern=r'^\+2519\d{8}$')]

# Shared Base
class UserBase(BaseModel):
    full_name: str
    phone_number: Optional[PhoneNumberStr]
    email: Optional[EmailStr] = None

# For requesting OTP
class UserCreate(BaseModel):
    phone_number: PhoneNumberStr
    full_name: str

# For verifying OTP and logging in
class UserVerify(UserCreate):  # Inherits full_name, phone_number
    email: Optional[EmailStr] = None
    otp_code: str

# For updating profile
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: PhoneNumberStr
    otp_code: str

# Auth response
class UserResponse(BaseModel):
    id: int
    full_name: str
    phone_number: Optional[str]
    email: Optional[str]
    is_active: bool

    class Config:
        orm_mode = True
