from typing import List, Optional
from sqlalchemy.orm import Session
from crud.base import CRUDBase
from models.booking import Booking
from schemas.booking import BookingCreate, BookingOut

class CRUDOrder(CRUDBase[Booking, BookingCreate, BookingOut]):
    def get_by_user(self, db: Session, *, user_id: int) -> List[Booking]:
        return db.query(Booking).filter(Booking.user_id == user_id).all()

    def get_active_orders(self, db: Session) -> List[Booking]:
        return db.query(Booking).all()

order = CRUDOrder(Booking)