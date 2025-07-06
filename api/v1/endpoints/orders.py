from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from api.deps import get_db, get_current_active_user, get_manager_user
from schemas.booking import BookingCreate, BookingOut
from models.users import DBUser, UserRole
from services.order_service import (
    create_booking_with_items, 
    get_all_bookings, 
    get_booking_by_id,
    get_orders_by_user
)
from services.assignment_service import assignment_service

router = APIRouter()

@router.post("/", response_model=BookingOut)
async def create_booking(
    booking: BookingCreate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Create a new booking with automatic provider assignment"""
    # Ensure the booking is for the current user (regular users can only create orders for themselves)
    if current_user.role == UserRole.USER:
        booking.user_id = current_user.id
    elif not booking.user_id:
        # If admin/manager doesn't specify user_id, use their own
        booking.user_id = current_user.id
    
    return await create_booking_with_items(db, booking)

@router.get("/", response_model=List[BookingOut])
def get_bookings(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Get bookings with role-based filtering"""
    # Role-based access control
    if current_user.role == UserRole.USER:
        # Regular users can only see their own orders
        return get_orders_by_user(db, current_user.id)
    else:
        # Managers and Admins can see all orders
        return get_all_bookings(db)

@router.get("/my-orders", response_model=List[BookingOut])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Get current user's orders"""
    return get_orders_by_user(db, current_user.id)

@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Get booking by ID"""
    booking = get_booking_by_id(db, booking_id)
    
    # Check if user has permission to view this booking
    if current_user.role == UserRole.USER and booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this booking")
    
    return booking