from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException
from schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderItemCreate
from db.models.order import Order
from db.models.order_item import OrderItem
from services.assignment_service import assignment_service
from typing import List
import logging
from models.booking import Booking

logger = logging.getLogger(__name__)

async def create_order_with_items(db: Session, order: OrderCreate) -> Order:
    # Create the order
    new_order = Order(
        user_id=order.user_id,
        driver_id=order.driver_id,
        provider_id=order.provider_id,
        status=order.status.value if hasattr(order.status, 'value') else order.status,
        total_amount=order.total_amount,
        pickup_address=order.pickup_address,
        delivery_address=order.delivery_address,
        pickup_lat=order.pickup_lat,
        pickup_lng=order.pickup_lng,
        delivery_lat=order.delivery_lat,
        delivery_lng=order.delivery_lng,
        notes=order.notes
    )
    db.add(new_order)
    db.flush()  # Get new_order.id before committing

    # Create OrderItem records
    for item in order.items:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            category_id=item.category_id,
            quantity=item.quantity,
            price=item.price,
            service_type=item.service_type
        )
        db.add(order_item)

    db.commit()
    db.refresh(new_order)

    # Auto-assign to service provider (if needed)
    try:
        assigned_provider = await assignment_service.assign_order_to_provider(
            db, new_order.id
        )
        if assigned_provider:
            logger.info(f"Order {new_order.id} automatically assigned to provider {assigned_provider.id}")
        else:
            logger.warning(f"Could not auto-assign order {new_order.id}")
    except Exception as e:
        logger.error(f"Failed to auto-assign order {new_order.id}: {e}")

    return new_order

def get_all_orders(db: Session) -> List[Order]:
    return db.query(Order).all()

def get_order_by_id(db: Session, order_id: int) -> Order:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

def get_orders_by_user(db: Session, user_id: int) -> List[Order]:
    """Get all orders for a specific user"""
    return db.query(Order).filter(Order.user_id == user_id).all()

def get_all_bookings(db: Session):
    return db.query(Booking).all()