from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user, get_manager_user
from app.schemas.order import BookingCreate, BookingOut, OrderStatusUpdate, OrderStatus
from app.schemas.user import UserRole
from app.services.order_service import (
    create_booking_with_items, 
    get_all_bookings, 
    get_booking_by_id,
    update_order_status,
    get_orders_by_provider,
    get_orders_by_status,
    get_orders_by_user
)
from app.services.assignment_service import assignment_service
from app.db.models.user import DBUser

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
    current_user: DBUser = Depends(get_current_active_user),
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    provider_id: Optional[int] = Query(None, description="Filter by provider ID"),
    user_id: Optional[int] = Query(None, description="Filter by user ID")
):
    """Get bookings with optional filters"""
    # Role-based access control
    if current_user.role == UserRole.USER:
        # Regular users can only see their own orders
        return get_orders_by_user(db, current_user.id)
    
    # Managers and Admins can see all orders with filters
    if status:
        return get_orders_by_status(db, status)
    elif provider_id:
        return get_orders_by_provider(db, provider_id)
    elif user_id:
        return get_orders_by_user(db, user_id)
    else:
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

@router.put("/{booking_id}/status", response_model=BookingOut)
async def update_booking_status(
    booking_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Update booking status (for managers/admins and service providers)"""
    # Only managers/admins can update order status
    if current_user.role == UserRole.USER:
        raise HTTPException(
            status_code=403, 
            detail="Only managers and admins can update order status"
        )
    
    return await update_order_status(db, booking_id, status_update.status, status_update.notes)

@router.post("/{booking_id}/assign-provider")
async def manually_assign_provider(
    booking_id: int,
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_manager_user)  # Manager or Admin only
):
    """Manually assign order to a specific provider (Manager/Admin only)"""
    provider = await assignment_service.assign_order_to_provider(
        db, booking_id, provider_id
    )
    if not provider:
        raise HTTPException(status_code=400, detail="Could not assign order to provider")
    
    return {"message": f"Order {booking_id} assigned to provider {provider.id}"}

@router.post("/{booking_id}/assign-driver")
async def assign_driver_to_order(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_manager_user)  # Manager or Admin only
):
    """Assign driver for delivery (Manager/Admin only)"""
    driver = await assignment_service.assign_driver_for_delivery(db, booking_id)
    if not driver:
        raise HTTPException(status_code=400, detail="Could not assign driver to order")
    
    return {"message": f"Driver {driver.id} assigned to order {booking_id}"}

@router.get("/provider/{provider_id}", response_model=List[BookingOut])
def get_provider_orders(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_manager_user)  # Manager or Admin only
):
    """Get all orders for a specific provider (Manager/Admin only)"""
    return get_orders_by_provider(db, provider_id)

@router.get("/status/{status}", response_model=List[BookingOut])
def get_orders_by_status_endpoint(
    status: OrderStatus,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_manager_user)  # Manager or Admin only
):
    """Get all orders with specific status (Manager/Admin only)"""
    return get_orders_by_status(db, status)

@router.get("/stats/summary")
def get_order_statistics(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_manager_user)  # Manager or Admin only
):
    """Get order statistics (Manager/Admin only)"""
    all_orders = get_all_bookings(db)
    
    stats = {
        "total_orders": len(all_orders),
        "pending_orders": len([o for o in all_orders if o.status == OrderStatus.PENDING]),
        "in_progress_orders": len([o for o in all_orders if o.status == OrderStatus.IN_PROGRESS]),
        "completed_orders": len([o for o in all_orders if o.status == OrderStatus.COMPLETED]),
        "cancelled_orders": len([o for o in all_orders if o.status == OrderStatus.CANCELLED])
    }
    
    return stats