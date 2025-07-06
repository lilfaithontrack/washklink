from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException
from schemas.booking import BookingCreate, BookingOut
from models.booking import Booking
from services.assignment_service import assignment_service
from typing import List
import logging

logger = logging.getLogger(__name__)

async def create_booking_with_items(db: Session, booking: BookingCreate) -> Booking:
    total_subtotal = 0
    processed_items = []

    for item in booking.items:
        # Fetch item data from pricing table
        item_data = db.execute(
            text("""
                SELECT * FROM tbl_item_price_with_catagory 
                WHERE product_id = :product_id AND catagory_id = :category_id
            """),
            {"product_id": item.product_id, "category_id": item.category_id}
        ).fetchone()

        if not item_data:
            raise HTTPException(
                status_code=404, 
                detail=f"Item with product ID {item.product_id} not found"
            )

        if item_data.out_of_stock:
            raise HTTPException(
                status_code=400, 
                detail=f"Item '{item_data.title}' is out of stock"
            )

        item_subtotal = (item_data.normal_price - item_data.discount) * item.quantity
        total_subtotal += item_subtotal

        processed_items.append({
            "product_id": item.product_id,
            "category_id": item.category_id,
            "title": item_data.title,
            "price": item_data.normal_price,
            "quantity": item.quantity,
            "subtotal": item_subtotal,
            "service_type": item.service_type.value if item.service_type else None
        })

    delivery_charge = booking.delivery_km * 5 if booking.delivery else 0
    total_amount = total_subtotal + delivery_charge

    new_booking = Booking(
        user_id=booking.user_id,
        items=processed_items,
        price_tag=total_amount,
        subtotal=total_subtotal,
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

    # Auto-assign to service provider
    try:
        assigned_provider = await assignment_service.assign_order_to_provider(
            db, new_booking.id
        )
        if assigned_provider:
            logger.info(f"Order {new_booking.id} automatically assigned to provider {assigned_provider.id}")
        else:
            logger.warning(f"Could not auto-assign order {new_booking.id}")
    except Exception as e:
        logger.error(f"Failed to auto-assign order {new_booking.id}: {e}")

    return new_booking

def get_all_bookings(db: Session) -> List[Booking]:
    return db.query(Booking).all()

def get_booking_by_id(db: Session, booking_id: int) -> Booking:
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

def get_orders_by_user(db: Session, user_id: int) -> List[Booking]:
    """Get all orders for a specific user"""
    return db.query(Booking).filter(Booking.user_id == user_id).all()