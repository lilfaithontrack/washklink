import json
import asyncio
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import WebSocket
from app.db.models.driver import Driver, DriverStatus
from app.db.models.order import Booking, OrderStatus
from app.services.location_service import location_service
import logging

logger = logging.getLogger(__name__)

class LiveTrackingService:
    def __init__(self):
        # Store active WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "drivers": set(),
            "customers": set(),
            "admin": set()
        }
        # Store driver locations in memory for real-time access
        self.driver_locations: Dict[int, Dict] = {}
        # Store order tracking data
        self.order_tracking: Dict[int, Dict] = {}

    async def connect_websocket(self, websocket: WebSocket, connection_type: str, user_id: Optional[int] = None):
        """Connect a WebSocket client for live tracking"""
        await websocket.accept()
        
        if connection_type in self.active_connections:
            self.active_connections[connection_type].add(websocket)
            logger.info(f"WebSocket connected: {connection_type}, user_id: {user_id}")
            
            # Send initial data based on connection type
            if connection_type == "drivers" and user_id:
                await self.send_driver_initial_data(websocket, user_id)
            elif connection_type == "customers" and user_id:
                await self.send_customer_initial_data(websocket, user_id)

    async def disconnect_websocket(self, websocket: WebSocket, connection_type: str):
        """Disconnect a WebSocket client"""
        if connection_type in self.active_connections:
            self.active_connections[connection_type].discard(websocket)
            logger.info(f"WebSocket disconnected: {connection_type}")

    async def update_driver_location(
        self, 
        db: Session, 
        driver_id: int, 
        latitude: float, 
        longitude: float,
        heading: Optional[float] = None,
        speed: Optional[float] = None
    ):
        """Update driver location and broadcast to connected clients"""
        # Update database
        driver = db.query(Driver).filter(Driver.id == driver_id).first()
        if not driver:
            return False

        driver.current_latitude = latitude
        driver.current_longitude = longitude
        driver.last_location_update = datetime.utcnow()
        driver.last_active = datetime.utcnow()
        db.commit()

        # Update in-memory cache
        location_data = {
            "driver_id": driver_id,
            "latitude": latitude,
            "longitude": longitude,
            "heading": heading,
            "speed": speed,
            "timestamp": datetime.utcnow().isoformat(),
            "status": driver.status.value
        }
        self.driver_locations[driver_id] = location_data

        # Broadcast to connected clients
        await self.broadcast_driver_location(location_data)

        # Update order tracking if driver is on delivery
        if driver.current_order_id:
            await self.update_order_tracking(db, driver.current_order_id, location_data)

        return True

    async def broadcast_driver_location(self, location_data: Dict):
        """Broadcast driver location to all connected clients"""
        message = {
            "type": "driver_location_update",
            "data": location_data
        }
        
        # Send to admin connections
        await self.broadcast_to_connections("admin", message)
        
        # Send to specific customer if driver is on delivery
        driver_id = location_data["driver_id"]
        if driver_id in self.order_tracking:
            order_data = self.order_tracking[driver_id]
            customer_message = {
                "type": "delivery_location_update",
                "data": {
                    "order_id": order_data["order_id"],
                    "driver_location": location_data,
                    "estimated_arrival": order_data.get("estimated_arrival")
                }
            }
            await self.broadcast_to_connections("customers", customer_message)

    async def update_order_tracking(self, db: Session, order_id: int, driver_location: Dict):
        """Update order tracking information"""
        order = db.query(Booking).filter(Booking.id == order_id).first()
        if not order or order.status != OrderStatus.OUT_FOR_DELIVERY:
            return

        # Calculate estimated arrival time
        if order.delivery_latitude and order.delivery_longitude:
            distance = location_service.calculate_distance(
                driver_location["latitude"], driver_location["longitude"],
                order.delivery_latitude, order.delivery_longitude
            )
            
            # Estimate arrival time (assuming 30 km/h average speed)
            estimated_minutes = (distance / 30) * 60
            estimated_arrival = datetime.utcnow() + timedelta(minutes=estimated_minutes)
            
            self.order_tracking[order_id] = {
                "order_id": order_id,
                "driver_id": driver_location["driver_id"],
                "customer_id": order.user_id,
                "estimated_arrival": estimated_arrival.isoformat(),
                "distance_remaining": distance
            }

    async def broadcast_to_connections(self, connection_type: str, message: Dict):
        """Broadcast message to all connections of a specific type"""
        if connection_type not in self.active_connections:
            return

        disconnected = set()
        for websocket in self.active_connections[connection_type]:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {e}")
                disconnected.add(websocket)

        # Remove disconnected WebSockets
        for websocket in disconnected:
            self.active_connections[connection_type].discard(websocket)

    async def send_driver_initial_data(self, websocket: WebSocket, driver_id: int):
        """Send initial data to a driver connection"""
        if driver_id in self.driver_locations:
            message = {
                "type": "initial_location",
                "data": self.driver_locations[driver_id]
            }
            await websocket.send_text(json.dumps(message))

    async def send_customer_initial_data(self, websocket: WebSocket, user_id: int):
        """Send initial tracking data to a customer"""
        # Find active orders for this customer
        for order_id, tracking_data in self.order_tracking.items():
            if tracking_data["customer_id"] == user_id:
                driver_id = tracking_data["driver_id"]
                if driver_id in self.driver_locations:
                    message = {
                        "type": "initial_tracking",
                        "data": {
                            "order_id": order_id,
                            "driver_location": self.driver_locations[driver_id],
                            "estimated_arrival": tracking_data.get("estimated_arrival")
                        }
                    }
                    await websocket.send_text(json.dumps(message))

    async def start_driver_delivery(self, db: Session, order_id: int, driver_id: int):
        """Start tracking for a delivery"""
        order = db.query(Booking).filter(Booking.id == order_id).first()
        driver = db.query(Driver).filter(Driver.id == driver_id).first()
        
        if not order or not driver:
            return False

        # Update order status
        order.status = OrderStatus.OUT_FOR_DELIVERY
        driver.status = DriverStatus.ON_DELIVERY
        driver.current_order_id = order_id
        db.commit()

        # Initialize tracking
        if driver_id in self.driver_locations:
            await self.update_order_tracking(db, order_id, self.driver_locations[driver_id])

        # Notify customer
        message = {
            "type": "delivery_started",
            "data": {
                "order_id": order_id,
                "driver_id": driver_id,
                "driver_name": f"{driver.first_name} {driver.last_name}",
                "driver_phone": driver.phone_number,
                "vehicle_info": f"{driver.vehicle_color} {driver.vehicle_model} ({driver.vehicle_plate})"
            }
        }
        await self.broadcast_to_connections("customers", message)
        return True

    async def complete_delivery(self, db: Session, order_id: int):
        """Complete delivery and stop tracking"""
        order = db.query(Booking).filter(Booking.id == order_id).first()
        if not order:
            return False

        driver = db.query(Driver).filter(Driver.id == order.driver_id).first()
        if driver:
            driver.status = DriverStatus.AVAILABLE
            driver.current_order_id = None
            driver.total_deliveries += 1
            driver.successful_deliveries += 1

        order.status = OrderStatus.DELIVERED
        order.completed_at = datetime.utcnow()
        db.commit()

        # Remove from tracking
        if order_id in self.order_tracking:
            del self.order_tracking[order_id]

        # Notify customer
        message = {
            "type": "delivery_completed",
            "data": {
                "order_id": order_id,
                "completed_at": order.completed_at.isoformat()
            }
        }
        await self.broadcast_to_connections("customers", message)
        return True

    def get_driver_location(self, driver_id: int) -> Optional[Dict]:
        """Get current driver location from cache"""
        return self.driver_locations.get(driver_id)

    def get_all_driver_locations(self) -> Dict[int, Dict]:
        """Get all driver locations"""
        return self.driver_locations.copy()

    def get_order_tracking_info(self, order_id: int) -> Optional[Dict]:
        """Get tracking information for an order"""
        return self.order_tracking.get(order_id)

    async def cleanup_stale_data(self):
        """Clean up stale tracking data (run periodically)"""
        current_time = datetime.utcnow()
        stale_threshold = timedelta(minutes=10)

        # Remove stale driver locations
        stale_drivers = []
        for driver_id, location_data in self.driver_locations.items():
            last_update = datetime.fromisoformat(location_data["timestamp"])
            if current_time - last_update > stale_threshold:
                stale_drivers.append(driver_id)

        for driver_id in stale_drivers:
            del self.driver_locations[driver_id]
            logger.info(f"Removed stale location data for driver {driver_id}")

# Global instance
tracking_service = LiveTrackingService()