from pydantic import BaseModel, Field , EmailStr
from datetime import date
class ServiceProviderCreate(BaseModel) :
    name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    first_name:str
    Middle_name:str
    last_name:str
    address: str = Field(..., min_length=1, max_length=100)
    nearby: str = Field(..., min_length=1, max_length=100)
    phone_number: int
    date_of_birth:date
    washing_machine:boolean 
    longitude: float
    latitude: float
class ServiceProviderResponse(BaseModel) :
    id: int
    name: str
    first_name:str
    Middle_name:str
    last_name:str
    washing_machine:str
    email: EmailStr
    phone_number: int
    address: str
    nearby_nearby_condominum: str
    date_of_birth:date
    washing_machine:boolean
    longitude: float
    latitude: float

    class Config:
        orm_mode = True
