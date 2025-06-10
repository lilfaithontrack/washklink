from pydantic import BaseModel, StringConstraints
from typing import Optional, Annotated

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

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Annotated[str, StringConstraints(pattern=r'^\+2519\d{8}$')]
    otp_code: str
# Response schema
class UserResponse(BaseModel):
    id: int
    full_name: str
    phone_number: Optional[str]
    email: str
    is_active: bool

    class Config:
        orm_mode = True
