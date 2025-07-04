from pydantic import BaseModel, Field, EmailStr
from datetime import date

class ServiceProviderCreate(BaseModel):
    email: EmailStr
    first_name: str
    middle_name: str
    last_name: str
    address: str = Field(..., min_length=1, max_length=100)
    nearby_condominum: str = Field(..., min_length=1, max_length=100)
    phone_number: int
    date_of_birth: date
    washing_machine: bool
    longitude: float
    latitude: float

class ServiceProviderResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    middle_name: str
    last_name: str
    address: str
    nearby_condominum: str
    phone_number: int
    date_of_birth: date
    washing_machine: bool
    longitude: float
    latitude: float

    class Config:
        from_attributes = True