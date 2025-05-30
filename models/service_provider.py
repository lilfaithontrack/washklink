from sqlalchemy  import Column , Integer ,String , ForeignKey, Boolean,Float 
from database import Base

class ServiceProvider(Base) :
    __tablename__ = "service_provider"
    id = Column(Integer, unique=True, primary_key=True, index=True)
    first_name=Column(String, nullable=False)
    Middle_name= Column(String, nullable=False)
    last_name= Column(String, nullable=False)
    name = Column(String,  nullable=False)
    phone_number=Column(Integer, unique=True, nullable=False) 
    email = Column(String,unique=True, index=True , nullable=False)
    password = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    Date_of_Birth=Column(Date, nullable=False)
    address= Column(String, nullable=False)
    washing_machine=(Boolean, default=True)
    nearby = Column(String, nullable=False)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)


