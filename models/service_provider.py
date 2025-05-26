from sqlalchemy  import Column , Integer ,String , ForeignKey, Boolean,Float 
from database import Base

class ServiceProvider(Base) :
    __tablename__ = "service_provider"
    id = Column(Integer, unique=True, primary_key=True, index=True)
    name = Column(String,  nullable=False)
    email = Column(String,unique=True, index=True , nullable=False)
    password = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    address= Column(String, nullable=False)
    nearby = Column(String, nullable=False)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)


