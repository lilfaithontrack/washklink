from typing import Optional, List
from models.mongo_models import Order, OrderStatus, ServiceType
from pydantic import BaseModel
import logging
from bson import ObjectId
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrderCreate(BaseModel):
    user_id: str
    service_provider_id: Optional[str] = None
    driver_id: Optional[str] = None
    pickup_latitude: Optional[float] = None
    pickup_longitude: Optional[float] = None
    pickup_address: Optional[str] = None
    delivery_latitude: Optional[float] = None
    delivery_longitude: Optional[float] = None
    delivery_address: Optional[str] = None
    subtotal: float
    delivery: bool = False
    delivery_km: float = 0.0
    delivery_charge: float = 0.0
    service_type: ServiceType = ServiceType.MACHINE_WASH
    note: Optional[str] = None
    payment_method: Optional[str] = None
    cash_on_delivery: bool = False

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    service_provider_id: Optional[str] = None
    driver_id: Optional[str] = None
    delivery_latitude: Optional[float] = None
    delivery_longitude: Optional[float] = None
    delivery_address: Optional[str] = None
    note: Optional[str] = None
    payment_method: Optional[str] = None
    cash_on_delivery: Optional[bool] = None
    estimated_pickup_time: Optional[datetime] = None
    estimated_completion_time: Optional[datetime] = None
    estimated_delivery_time: Optional[datetime] = None

class OrderMongoCRUD:
    async def get(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        try:
            return await Order.get(ObjectId(order_id))
        except Exception as e:
            logger.error(f"Error getting order by ID {order_id}: {str(e)}")
            return None

    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get all orders with pagination"""
        try:
            return await Order.find().skip(skip).limit(limit).sort("-created_at").to_list()
        except Exception as e:
            logger.error(f"Error getting all orders: {str(e)}")
            return []

    async def get_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get orders by user ID"""
        try:
            return await Order.find(Order.user_id == ObjectId(user_id)).skip(skip).limit(limit).to_list()
        except Exception as e:
            logger.error(f"Error getting orders for user {user_id}: {str(e)}")
            return []

    async def get_by_provider(self, provider_id: str, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get orders by service provider ID"""
        try:
            return await Order.find(Order.service_provider_id == ObjectId(provider_id)).skip(skip).limit(limit).to_list()
        except Exception as e:
            logger.error(f"Error getting orders for provider {provider_id}: {str(e)}")
            return []

    async def get_by_driver(self, driver_id: str, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get orders by driver ID"""
        try:
            return await Order.find(Order.driver_id == ObjectId(driver_id)).skip(skip).limit(limit).to_list()
        except Exception as e:
            logger.error(f"Error getting orders for driver {driver_id}: {str(e)}")
            return []

    async def get_by_status(self, status: OrderStatus, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get orders by status"""
        try:
            return await Order.find(Order.status == status).skip(skip).limit(limit).to_list()
        except Exception as e:
            logger.error(f"Error getting orders by status {status}: {str(e)}")
            return []

    async def get_active_orders(self, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get active orders (not completed, cancelled, or delivered)"""
        try:
            active_statuses = [
                OrderStatus.PENDING,
                OrderStatus.ASSIGNED,
                OrderStatus.ACCEPTED,
                OrderStatus.IN_PROGRESS,
                OrderStatus.READY_FOR_PICKUP,
                OrderStatus.OUT_FOR_DELIVERY
            ]
            return await Order.find({"status": {"$in": active_statuses}}).skip(skip).limit(limit).to_list()
        except Exception as e:
            logger.error(f"Error getting active orders: {str(e)}")
            return []

    async def create(self, obj_in: OrderCreate) -> Optional[Order]:
        """Create new order"""
        try:
            order_data = obj_in.dict()
            # Convert string IDs to ObjectId
            order_data["user_id"] = ObjectId(order_data["user_id"])
            if order_data["service_provider_id"]:
                order_data["service_provider_id"] = ObjectId(order_data["service_provider_id"])
            if order_data["driver_id"]:
                order_data["driver_id"] = ObjectId(order_data["driver_id"])
            
            order = Order(**order_data)
            await order.insert()
            return order
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            return None

    async def update(self, order_id: str, obj_in: OrderUpdate) -> Optional[Order]:
        """Update order"""
        try:
            order = await self.get(order_id)
            if not order:
                logger.error(f"Order with ID {order_id} not found")
                return None
            
            update_data = obj_in.dict(exclude_unset=True)
            
            # Handle timestamp updates based on status
            if "status" in update_data:
                status = update_data["status"]
                now = datetime.utcnow()
                
                if status == OrderStatus.ASSIGNED:
                    update_data["assigned_at"] = now
                elif status == OrderStatus.ACCEPTED:
                    update_data["accepted_at"] = now
                elif status in [OrderStatus.COMPLETED, OrderStatus.DELIVERED]:
                    update_data["completed_at"] = now
            
            # Convert string IDs to ObjectId
            if "service_provider_id" in update_data and update_data["service_provider_id"]:
                update_data["service_provider_id"] = ObjectId(update_data["service_provider_id"])
            if "driver_id" in update_data and update_data["driver_id"]:
                update_data["driver_id"] = ObjectId(update_data["driver_id"])
            
            for field, value in update_data.items():
                setattr(order, field, value)
            
            await order.save()
            return order
        except Exception as e:
            logger.error(f"Error updating order: {str(e)}")
            return None

    async def delete(self, order_id: str) -> bool:
        """Delete order"""
        try:
            order = await self.get(order_id)
            if not order:
                logger.error(f"Order with ID {order_id} not found")
                return False
            
            await order.delete()
            return True
        except Exception as e:
            logger.error(f"Error deleting order: {str(e)}")
            return False

    async def assign_to_provider(self, order_id: str, provider_id: str) -> Optional[Order]:
        """Assign order to service provider"""
        try:
            order = await self.get(order_id)
            if not order:
                return None
            
            order.service_provider_id = ObjectId(provider_id)
            order.status = OrderStatus.ASSIGNED
            order.assigned_at = datetime.utcnow()
            order.assignment_attempts += 1
            
            await order.save()
            return order
        except Exception as e:
            logger.error(f"Error assigning order to provider: {str(e)}")
            return None

    async def assign_to_driver(self, order_id: str, driver_id: str) -> Optional[Order]:
        """Assign order to driver"""
        try:
            order = await self.get(order_id)
            if not order:
                return None
            
            order.driver_id = ObjectId(driver_id)
            order.status = OrderStatus.OUT_FOR_DELIVERY
            
            await order.save()
            return order
        except Exception as e:
            logger.error(f"Error assigning order to driver: {str(e)}")
            return None

    async def get_pending_orders(self, limit: int = 100) -> List[Order]:
        """Get all pending orders"""
        try:
            return await Order.find(Order.status == OrderStatus.PENDING).limit(limit).to_list()
        except Exception as e:
            logger.error(f"Error getting pending orders: {str(e)}")
            return []

    async def search_orders(self, query: str, limit: int = 10) -> List[Order]:
        """Search orders by address or notes"""
        try:
            orders = await Order.find({
                "$or": [
                    {"pickup_address": {"$regex": query, "$options": "i"}},
                    {"delivery_address": {"$regex": query, "$options": "i"}},
                    {"note": {"$regex": query, "$options": "i"}},
                    {"special_instructions": {"$regex": query, "$options": "i"}}
                ]
            }).limit(limit).to_list()
            return orders
        except Exception as e:
            logger.error(f"Error searching orders: {str(e)}")
            return []

    async def count_orders(self) -> int:
        """Count total orders"""
        try:
            return await Order.count()
        except Exception as e:
            logger.error(f"Error counting orders: {str(e)}")
            return 0

    async def count_orders_by_status(self, status: OrderStatus) -> int:
        """Count orders by status"""
        try:
            return await Order.find(Order.status == status).count()
        except Exception as e:
            logger.error(f"Error counting orders by status: {str(e)}")
            return 0

# Create instance
order_mongo_crud = OrderMongoCRUD() 