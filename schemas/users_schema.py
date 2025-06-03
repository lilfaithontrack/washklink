from pydantic import BaseModel

class UserBase(BaseModel):
    phone_number: str

class UserCreate(UserBase):
    pass  # Used when requesting OTP (registration or login)

class UserVerify(BaseModel):
    phone_number: str
    otp_code: str

class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True
