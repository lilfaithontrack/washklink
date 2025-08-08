from fastapi import HTTPException
from schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderItemCreate
from models.mongo_models import Order, OrderItem, OrderStatus
from services.assignment_service import assignment_service
from typing import List
import logging
from bson import ObjectId

logger = logging.getLogger(__name__)

async def create_order_with_items(order: OrderCreate) -> Order:
    """Create a new order with items"""
    try:
        # Ensure user_id is set (should be set by the endpoint)
        if not order.user_id:
            raise HTTPException(status_code=400, detail="User ID is required")
        
        # Create the order
        new_order = Order(
            user_id=ObjectId(order.user_id),
            driver_id=ObjectId(order.driver_id) if order.driver_id else None,
            service_provider_id=ObjectId(order.provider_id) if order.provider_id else None,
            status=order.status if order.status else OrderStatus.PENDING,
            subtotal=order.total_amount,
            pickup_address=order.pickup_address,
            delivery_address=order.delivery_address,
            pickup_latitude=order.pickup_lat,
            pickup_longitude=order.pickup_lng,
            delivery_latitude=order.delivery_lat,
            delivery_longitude=order.delivery_lng,
            note=order.notes,
            payment_option=order.payment_method,
            cash_on_delivery=order.cash_on_delivery,
            items=[]  # Initialize empty items list
        )

        # Add order items
        for item in order.items:
            order_item = OrderItem(
                product_id=item.product_id,  # Now accepts string directly
                category_id=item.category_id,
                quantity=item.quantity,
                price=item.price,
                service_type=item.service_type
            )
            new_order.items.append(order_item)

        # Save the order
        await new_order.insert()

        # Auto-assign to service provider (if needed)
        try:
            assigned_provider = await assignment_service.assign_order_to_provider(
                str(new_order.id)
            )
            if assigned_provider:
                logger.info(f"Order {new_order.id} automatically assigned to provider {assigned_provider.id}")
            else:
                logger.warning(f"Could not auto-assign order {new_order.id}")
        except Exception as e:
            logger.error(f"Failed to auto-assign order {new_order.id}: {e}")
            # Don't fail the entire order creation if assignment fails

        return new_order
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")

async def get_all_orders(skip: int = 0, limit: int = 100) -> List[Order]:
    """Get all orders with pagination"""
    try:
        return await Order.find_all().skip(skip).limit(limit).to_list()
    except Exception as e:
        logger.error(f"Error getting all orders: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch orders")

async def get_order_by_id(order_id: str) -> Order:
    """Get order by ID"""
    try:
        order = await Order.get(ObjectId(order_id))
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except Exception as e:
        logger.error(f"Error getting order by ID {order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch order")

async def get_orders_by_user(user_id: str, skip: int = 0, limit: int = 100) -> List[Order]:
    """Get all orders for a specific user with pagination"""
    try:
        return await Order.find(Order.user_id == ObjectId(user_id)).skip(skip).limit(limit).to_list()
    except Exception as e:
        logger.error(f"Error getting orders for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch user orders")

async def get_orders_by_provider(provider_id: str, skip: int = 0, limit: int = 100) -> List[Order]:
    """Get all orders for a specific service provider with pagination"""
    try:
        return await Order.find(Order.service_provider_id == ObjectId(provider_id)).skip(skip).limit(limit).to_list()
    except Exception as e:
        logger.error(f"Error getting orders for provider {provider_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch provider orders")

async def get_orders_by_driver(driver_id: str, skip: int = 0, limit: int = 100) -> List[Order]:
    """Get all orders for a specific driver with pagination"""
    try:
        return await Order.find(Order.driver_id == ObjectId(driver_id)).skip(skip).limit(limit).to_list()
    except Exception as e:
        logger.error(f"Error getting orders for driver {driver_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch driver orders")

async def get_orders_by_status(status: OrderStatus, skip: int = 0, limit: int = 100) -> List[Order]:
    """Get all orders with a specific status with pagination"""
    try:
        return await Order.find(Order.status == status).skip(skip).limit(limit).to_list()
    except Exception as e:
        logger.error(f"Error getting orders with status {status}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch orders by status")

async def update_order_status(order_id: str, new_status: OrderStatus) -> Order:
    """Update order status"""
    try:
        order = await get_order_by_id(order_id)
        order.status = new_status
        await order.save()
        return order
    except Exception as e:
        logger.error(f"Error updating order status for {order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update order status")

async def assign_order_to_provider(order_id: str, provider_id: str) -> Order:
    """Assign order to a service provider"""
    try:
        order = await get_order_by_id(order_id)
        order.service_provider_id = ObjectId(provider_id)
        order.status = OrderStatus.ASSIGNED
        await order.save()
        return order
    except Exception as e:
        logger.error(f"Error assigning order {order_id} to provider {provider_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to assign order to provider")

async def assign_order_to_driver(order_id: str, driver_id: str) -> Order:
    """Assign order to a driver"""
    try:
        order = await get_order_by_id(order_id)
        order.driver_id = ObjectId(driver_id)
        order.status = OrderStatus.OUT_FOR_DELIVERY
        await order.save()
        return order
    except Exception as e:
        logger.error(f"Error assigning order {order_id} to driver {driver_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to assign order to driver")