from fastapi import APIRouter, HTTPException
from models.mongo_models import Order, Item, OrderItem, OrderStatus, ServiceType
from schemas.order import OrderCreate, OrderResponse
from typing import List, Optional
from bson import ObjectId
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

booking_router = APIRouter()

@booking_router.post("/", response_model=OrderResponse)
async def create_booking(order: OrderCreate) -> Order:
    """Create a new booking/order"""
    try:
        total_subtotal = 0
        processed_items = []

        for item in order.items:
            # Fetch item data from MongoDB
            item_data = await Item.get(ObjectId(item.product_id))
            if not item_data:
                raise HTTPException(status_code=404, detail=f"Item with ID {item.product_id} not found")

            if not item_data.is_active:
                raise HTTPException(status_code=400, detail=f"Item '{item_data.name}' is not available")

            item_subtotal = item_data.price * item.quantity
            total_subtotal += item_subtotal

            # Create OrderItem
            order_item = OrderItem(
                product_id=ObjectId(item.product_id),
                category_id=item.category_id,
                quantity=item.quantity,
                price=item_data.price,
                service_type=item.service_type
            )
            processed_items.append(order_item)

        # Calculate delivery charge
        delivery_charge = order.delivery_km * 5 if order.delivery else 0  # example rate per km
        total_amount = total_subtotal + delivery_charge

        # Create new order
        new_order = Order(
            user_id=ObjectId(order.user_id),
            items=processed_items,
            price_tag=total_amount,
            subtotal=total_subtotal,
            payment_option=order.payment_option,
            delivery=order.delivery,
            delivery_km=order.delivery_km,
            delivery_charge=delivery_charge,
            cash_on_delivery=order.cash_on_delivery,
            note=order.note,
            status=OrderStatus.PENDING,
            service_type=order.service_type or ServiceType.MACHINE_WASH,
            pickup_address=order.pickup_address,
            delivery_address=order.delivery_address,
            pickup_latitude=order.pickup_latitude,
            pickup_longitude=order.pickup_longitude,
            delivery_latitude=order.delivery_latitude,
            delivery_longitude=order.delivery_longitude,
            created_at=datetime.utcnow()
        )

        await new_order.insert()
        return new_order

    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@booking_router.get("/", response_model=List[OrderResponse])
async def get_all_bookings(
    skip: int = 0,
    limit: int = 100,
    status: Optional[OrderStatus] = None,
    user_id: Optional[str] = None
) -> List[Order]:
    """Get all bookings/orders with optional filtering"""
    try:
        query = {}
        if status:
            query["status"] = status
        if user_id:
            query["user_id"] = ObjectId(user_id)

        orders = await Order.find(query).skip(skip).limit(limit).to_list()
        return orders

    except Exception as e:
        logger.error(f"Error getting orders: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@booking_router.get("/{booking_id}", response_model=OrderResponse)
async def get_booking(booking_id: str) -> Order:
    """Get booking/order by ID"""
    try:
        order = await Order.get(ObjectId(booking_id))
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order

    except Exception as e:
        logger.error(f"Error getting order {booking_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@booking_router.put("/{booking_id}/cancel")
async def cancel_booking(booking_id: str) -> Order:
    """Cancel a booking/order"""
    try:
        order = await Order.get(ObjectId(booking_id))
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        if order.status not in [OrderStatus.PENDING, OrderStatus.ASSIGNED]:
            raise HTTPException(status_code=400, detail="Cannot cancel order in current status")

        order.status = OrderStatus.CANCELLED
        order.updated_at = datetime.utcnow()
        await order.save()
        return order

    except Exception as e:
        logger.error(f"Error cancelling order {booking_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@booking_router.get("/user/{user_id}", response_model=List[OrderResponse])
async def get_user_bookings(
    user_id: str,
    skip: int = 0,
    limit: int = 100,
    status: Optional[OrderStatus] = None
) -> List[Order]:
    """Get all bookings/orders for a specific user"""
    try:
        query = {"user_id": ObjectId(user_id)}
        if status:
            query["status"] = status

        orders = await Order.find(query).skip(skip).limit(limit).to_list()
        return orders

    except Exception as e:
        logger.error(f"Error getting orders for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@booking_router.get("/provider/{provider_id}", response_model=List[OrderResponse])
async def get_provider_bookings(
    provider_id: str,
    skip: int = 0,
    limit: int = 100,
    status: Optional[OrderStatus] = None
) -> List[Order]:
    """Get all bookings/orders for a specific service provider"""
    try:
        query = {"service_provider_id": ObjectId(provider_id)}
        if status:
            query["status"] = status

        orders = await Order.find(query).skip(skip).limit(limit).to_list()
        return orders

    except Exception as e:
        logger.error(f"Error getting orders for provider {provider_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
