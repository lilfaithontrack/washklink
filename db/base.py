from database import Base

# Import all models here to ensure they are registered with SQLAlchemy
from models.users import DBUser
from models.service_provider import ServiceProvider
from models.booking import Booking
from controllers.item_controller import ItemPrice
from db.models.driver import Driver
from db.models.payment import Payment