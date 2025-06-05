from pydantic import BaseModel

class UserBase(BaseModel):
    sender_name: str
    phone_number: str

class UserCreate(UserBase):
     sender_name: str
     pass 

class UserVerify(BaseModel):
    phone_number: str
    otp_code: str

class UserResponse(UserBase):
    id: int
    sender_name:str
    phone_number:str
    is_active: bool

    class Config:
        orm_mode = True
