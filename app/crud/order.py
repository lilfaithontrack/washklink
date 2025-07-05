from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.db.models.order import Booking
from app.schemas.order import BookingCreate, BookingOut

class CRUDOrder(CRUDBase[Booking, BookingCreate, BookingOut]):
    def get_by_user(self, db: Session, *, user_id: int) -> List[Booking]:
        return db.query(Booking).filter(Booking.user_id == user_id).all()

    def get_active_orders(self, db: Session) -> List[Booking]:
        # Add your logic for active orders
        return db.query(Booking).all()

order = CRUDOrder(Booking)