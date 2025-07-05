from pydantic import BaseModel, StringConstraints, EmailStr
from typing import Optional, Annotated
from enum import Enum
from datetime import datetime

class UserRole(str, Enum):
    USER = "user"
    MANAGER = "manager"
    ADMIN = "admin"

# Phone number validation for Ethiopian numbers
PhoneNumberStr = Annotated[str, StringConstraints(pattern=r'^\+2519\d{8}$')]

# Shared Base
class UserBase(BaseModel):
    full_name: str
    phone_number: PhoneNumberStr

# For requesting OTP (regular users)
class UserCreate(BaseModel):
    phone_number: PhoneNumberStr
    full_name: str

# For verifying OTP and logging in (regular users)
class UserVerify(UserCreate):
    otp_code: str

# For creating admin/manager accounts
class AdminUserCreate(BaseModel):
    full_name: str
    phone_number: PhoneNumberStr
    email: EmailStr
    role: UserRole
    password: str  # Admin/Manager accounts use password instead of OTP

# For admin/manager login
class AdminUserLogin(BaseModel):
    email: EmailStr
    password: str

# For updating user profile
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[PhoneNumberStr] = None
    email: Optional[EmailStr] = None  # Only for admin/manager

# Auth response
class UserResponse(BaseModel):
    id: int
    full_name: str
    phone_number: str
    email: Optional[str] = None
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

# Token response
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
    expires_in: int

# Role check schemas
class RoleCheck(BaseModel):
    required_role: UserRole
    message: str = "Insufficient permissions"