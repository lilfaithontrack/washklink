from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.schemas.order import BookingCreate, BookingOut
from app.services.order_service import create_booking_with_items, get_all_bookings, get_booking_by_id
from app.db.models.user import DBUser

router = APIRouter()

@router.post("/", response_model=BookingOut)
def create_booking(
    booking: BookingCreate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Create a new booking"""
    return create_booking_with_items(db, booking)

@router.get("/", response_model=List[BookingOut])
def get_bookings(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Get all bookings"""
    return get_all_bookings(db)

@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Get booking by ID"""
    return get_booking_by_id(db, booking_id)