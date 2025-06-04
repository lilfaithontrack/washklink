from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import booking as models
from schemas import booking as schemas
from typing import List

router = APIRouter()

@router.post("/", response_model=schemas.BookingOut)
def create_booking(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    delivery_charge = 0.0
    if booking.delivery:
        delivery_charge = booking.delivery_km * 5  # 1km = 5 ETB

    new_booking = models.Booking(
        user_id=booking.user_id,
        item=booking.item,
        price_tag=booking.price_tag,
        subtotal=booking.subtotal,
        payment_option=booking.payment_option,
        delivery=booking.delivery,
        delivery_km=booking.delivery_km,
        delivery_charge=delivery_charge,
        cash_on_delivery=booking.cash_on_delivery,
        note=booking.note
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking

@router.get("/", response_model=List[schemas.BookingOut])
def get_all_bookings(db: Session = Depends(get_db)):
    bookings = db.query(models.Booking).all()
    return bookings

@router.get("/{booking_id}", response_model=schemas.BookingOut)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking
