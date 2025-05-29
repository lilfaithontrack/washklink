from pydantic import BaseModel, Field , EmailStr
class ServiceProviderCreate(BaseModel) :
    name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=50)
    address: str = Field(..., min_length=1, max_length=100)
    nearby: str = Field(..., min_length=1, max_length=100)
    phone_number: int
    longitude: float
    latitude: float
class ServiceProviderResponse(BaseModel) :
    id: int
    name: str
    email: EmailStr
    phone_number: int
    address: str
    nearby: str
    longitude: float
    latitude: float

    class Config:
        orm_mode = True
