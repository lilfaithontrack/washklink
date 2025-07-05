from app.core.database import Base

# Import all models here to ensure they are registered with SQLAlchemy
from app.db.models.user import DBUser
from app.db.models.laundry_provider import ServiceProvider
from app.db.models.order import Booking
from app.db.models.item import ItemPrice
from app.db.models.driver import Driver
from app.db.models.payment import Payment