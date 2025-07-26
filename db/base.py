from database import Base

# Import all models here to ensure they are registered with SQLAlchemy
from models.users import DBUser
from db.models.service_provider import ServiceProvider
from db.models.driver import Driver
from db.models.payment import Payment
from db.models.order_item import OrderItem