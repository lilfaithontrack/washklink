from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.services.tracking_service import tracking_service
from app.db.models.user import DBUser
from app.db.models.driver import Driver, DriverStatus
from app.db.models.order import Booking, OrderStatus
from app.schemas.tracking import TrackingAnalytics, DeliveryTrackingInfo
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/dashboard/live-data")
async def get_live_dashboard_data(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Get live data for admin dashboard"""
    
    # Get all driver locations
    driver_locations = tracking_service.get_all_driver_locations()
    
    # Get order tracking data
    order_tracking = tracking_service.order_tracking
    
    # Get database statistics
    total_drivers = db.query(Driver).count()
    active_drivers = db.query(Driver).filter(
        Driver.status.in_([DriverStatus.AVAILABLE, DriverStatus.BUSY, DriverStatus.ON_DELIVERY])
    ).count()
    
    pending_orders = db.query(Booking).filter(Booking.status == OrderStatus.PENDING).count()
    in_progress_orders = db.query(Booking).filter(
        Booking.status.in_([OrderStatus.ASSIGNED, OrderStatus.IN_PROGRESS, OrderStatus.OUT_FOR_DELIVERY])
    ).count()
    
    return {
        "driver_locations": driver_locations,
        "order_tracking": order_tracking,
        "statistics": {
            "total_drivers": total_drivers,
            "active_drivers": active_drivers,
            "pending_orders": pending_orders,
            "in_progress_orders": in_progress_orders,
            "live_tracking_active": len(driver_locations) > 0
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/orders/active-deliveries")
async def get_active_deliveries(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Get all active deliveries with tracking information"""
    
    active_orders = db.query(Booking).filter(
        Booking.status == OrderStatus.OUT_FOR_DELIVERY
    ).all()
    
    deliveries = []
    for order in active_orders:
        if order.driver_id:
            driver_location = tracking_service.get_driver_location(order.driver_id)
            tracking_info = tracking_service.get_order_tracking_info(order.id)
            
            delivery_info = {
                "order_id": order.id,
                "customer_name": order.user.full_name,
                "customer_phone": order.user.phone_number,
                "driver_id": order.driver_id,
                "driver_name": f"{order.driver.first_name} {order.driver.last_name}",
                "driver_phone": order.driver.phone_number,
                "pickup_address": order.pickup_address,
                "delivery_address": order.delivery_address,
                "estimated_delivery": order.estimated_delivery_time.isoformat() if order.estimated_delivery_time else None,
                "current_location": driver_location,
                "tracking_info": tracking_info
            }
            deliveries.append(delivery_info)
    
    return deliveries

@router.post("/emergency/alert-driver/{driver_id}")
async def send_emergency_alert_to_driver(
    driver_id: int,
    message: str,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Send emergency alert to a specific driver"""
    
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    # Send emergency alert through WebSocket
    alert_message = {
        "type": "emergency_alert",
        "data": {
            "message": message,
            "priority": "high",
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    await tracking_service.broadcast_to_connections("drivers", alert_message)
    
    # Also send SMS notification
    from app.services.notification_service import notification_service
    await notification_service.send_sms(
        driver.phone_number,
        f"EMERGENCY ALERT: {message}"
    )
    
    return {"message": "Emergency alert sent successfully"}

@router.post("/broadcast/message")
async def broadcast_message_to_drivers(
    message: str,
    driver_status: DriverStatus = None,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Broadcast message to all drivers or drivers with specific status"""
    
    broadcast_data = {
        "type": "broadcast_message",
        "data": {
            "message": message,
            "from": "Admin",
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    await tracking_service.broadcast_to_connections("drivers", broadcast_data)
    
    # Also send SMS to drivers if needed
    drivers_query = db.query(Driver).filter(Driver.is_active == True)
    if driver_status:
        drivers_query = drivers_query.filter(Driver.status == driver_status)
    
    drivers = drivers_query.all()
    
    return {
        "message": "Message broadcasted successfully",
        "recipients": len(drivers)
    }

@router.get("/analytics/real-time")
async def get_real_time_analytics(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
) -> TrackingAnalytics:
    """Get real-time analytics for the tracking system"""
    
    driver_locations = tracking_service.get_all_driver_locations()
    
    # Calculate analytics
    total_active_drivers = len(driver_locations)
    drivers_by_status = {}
    speeds = []
    
    for location_data in driver_locations.values():
        status = location_data.get("status", "unknown")
        drivers_by_status[status] = drivers_by_status.get(status, 0) + 1
        
        if location_data.get("speed"):
            speeds.append(location_data["speed"])
    
    average_speed = sum(speeds) / len(speeds) if speeds else 0
    active_deliveries = len(tracking_service.order_tracking)
    
    return TrackingAnalytics(
        total_active_drivers=total_active_drivers,
        drivers_by_status=drivers_by_status,
        average_speed=average_speed,
        active_deliveries=active_deliveries
    )

@router.post("/simulation/driver-movement")
async def simulate_driver_movement(
    driver_id: int,
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    steps: int = 10,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Simulate driver movement for testing (development only)"""
    
    async def simulate_movement():
        import asyncio
        
        lat_step = (end_lat - start_lat) / steps
        lon_step = (end_lon - start_lon) / steps
        
        for i in range(steps + 1):
            current_lat = start_lat + (lat_step * i)
            current_lon = start_lon + (lon_step * i)
            
            await tracking_service.update_driver_location(
                db=SessionLocal(),
                driver_id=driver_id,
                latitude=current_lat,
                longitude=current_lon,
                speed=30.0,  # 30 km/h
                heading=45.0  # Northeast
            )
            
            await asyncio.sleep(2)  # Update every 2 seconds
    
    background_tasks.add_task(simulate_movement)
    
    return {"message": f"Started simulating movement for driver {driver_id}"}

from datetime import datetime
from app.core.database import SessionLocal