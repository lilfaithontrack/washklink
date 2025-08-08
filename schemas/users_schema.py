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
    phone_number: str  # Changed from phone to phone_number for consistency
    full_name: str

# For verifying OTP and logging in
class UserVerify(BaseModel):
    phone_number: str  # Changed from phone to phone_number for consistency
    full_name: str
    email: Optional[EmailStr] = None
    otp_code: str

# For updating profile
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None  # Changed from phone to phone_number for consistency
    email: Optional[EmailStr] = None
    password: Optional[str] = None

# Auth response (unified for both v1 and legacy)
class UserResponse(BaseModel):
    id: str
    full_name: str
    phone: Optional[str] = None  # Keep as phone for API response consistency
    email: Optional[str] = None
    role: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True