from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: str
    ccode: str
    mobile: str
    refercode: int
    parentcode: Optional[int] = None
    password: str
    status: Optional[int] = 1
    wallet: Optional[float] = 0
    status_login: int

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    registartion_date: datetime

    class Config:
        orm_mode = True