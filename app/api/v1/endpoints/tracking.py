from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.services.tracking_service import tracking_service
from app.services.location_service import location_service
from app.db.models.user import DBUser
from app.db.models.driver import Driver
from app.db.models.order import Booking, OrderStatus
from app.schemas.driver import LocationUpdate
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/ws/driver/{driver_id}")
async def driver_tracking_websocket(
    websocket: WebSocket,
    driver_id: int,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for driver live tracking"""
    await tracking_service.connect_websocket(websocket, "drivers", driver_id)
    
    try:
        while True:
            # Receive location updates from driver
            data = await websocket.receive_json()
            
            if data.get("type") == "location_update":
                location_data = data.get("data", {})
                await tracking_service.update_driver_location(
                    db=db,
                    driver_id=driver_id,
                    latitude=location_data.get("latitude"),
                    longitude=location_data.get("longitude"),
                    heading=location_data.get("heading"),
                    speed=location_data.get("speed")
                )
            elif data.get("type") == "status_update":
                # Handle driver status updates
                status_data = data.get("data", {})
                driver = db.query(Driver).filter(Driver.id == driver_id).first()
                if driver:
                    from app.db.models.driver import DriverStatus
                    new_status = DriverStatus(status_data.get("status"))
                    driver.status = new_status
                    db.commit()
                    
    except WebSocketDisconnect:
        await tracking_service.disconnect_websocket(websocket, "drivers")
    except Exception as e:
        logger.error(f"WebSocket error for driver {driver_id}: {e}")
        await tracking_service.disconnect_websocket(websocket, "drivers")

@router.websocket("/ws/customer/{user_id}")
async def customer_tracking_websocket(
    websocket: WebSocket,
    user_id: int,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for customer order tracking"""
    await tracking_service.connect_websocket(websocket, "customers", user_id)
    
    try:
        while True:
            # Keep connection alive and handle any customer requests
            data = await websocket.receive_json()
            
            if data.get("type") == "track_order":
                order_id = data.get("order_id")
                tracking_info = tracking_service.get_order_tracking_info(order_id)
                if tracking_info:
                    await websocket.send_json({
                        "type": "tracking_info",
                        "data": tracking_info
                    })
                    
    except WebSocketDisconnect:
        await tracking_service.disconnect_websocket(websocket, "customers")
    except Exception as e:
        logger.error(f"WebSocket error for customer {user_id}: {e}")
        await tracking_service.disconnect_websocket(websocket, "customers")

@router.websocket("/ws/admin")
async def admin_tracking_websocket(websocket: WebSocket):
    """WebSocket endpoint for admin dashboard live tracking"""
    await tracking_service.connect_websocket(websocket, "admin")
    
    try:
        while True:
            # Send all driver locations periodically
            data = await websocket.receive_json()
            
            if data.get("type") == "get_all_locations":
                all_locations = tracking_service.get_all_driver_locations()
                await websocket.send_json({
                    "type": "all_driver_locations",
                    "data": all_locations
                })
                
    except WebSocketDisconnect:
        await tracking_service.disconnect_websocket(websocket, "admin")
    except Exception as e:
        logger.error(f"WebSocket error for admin: {e}")
        await tracking_service.disconnect_websocket(websocket, "admin")

@router.post("/driver/{driver_id}/location")
async def update_driver_location_http(
    driver_id: int,
    location: LocationUpdate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """HTTP endpoint for updating driver location (alternative to WebSocket)"""
    success = await tracking_service.update_driver_location(
        db=db,
        driver_id=driver_id,
        latitude=location.latitude,
        longitude=location.longitude
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    return {"message": "Location updated successfully"}

@router.get("/driver/{driver_id}/location")
def get_driver_location(
    driver_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Get current driver location"""
    location = tracking_service.get_driver_location(driver_id)
    if not location:
        raise HTTPException(status_code=404, detail="Driver location not found")
    
    return location

@router.get("/drivers/locations")
def get_all_driver_locations(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Get all driver locations (admin only)"""
    return tracking_service.get_all_driver_locations()

@router.get("/order/{order_id}/tracking")
def get_order_tracking(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Get tracking information for an order"""
    # Verify user has permission to track this order
    order = db.query(Booking).filter(Booking.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to track this order")
    
    tracking_info = tracking_service.get_order_tracking_info(order_id)
    if not tracking_info:
        return {"message": "Order is not currently being tracked"}
    
    # Add driver location if available
    driver_id = tracking_info.get("driver_id")
    if driver_id:
        driver_location = tracking_service.get_driver_location(driver_id)
        if driver_location:
            tracking_info["driver_location"] = driver_location
    
    return tracking_info

@router.post("/order/{order_id}/start-delivery")
async def start_delivery_tracking(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Start delivery tracking for an order"""
    order = db.query(Booking).filter(Booking.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if not order.driver_id:
        raise HTTPException(status_code=400, detail="No driver assigned to this order")
    
    success = await tracking_service.start_driver_delivery(db, order_id, order.driver_id)
    if not success:
        raise HTTPException(status_code=400, detail="Could not start delivery tracking")
    
    return {"message": "Delivery tracking started"}

@router.post("/order/{order_id}/complete-delivery")
async def complete_delivery_tracking(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Complete delivery and stop tracking"""
    success = await tracking_service.complete_delivery(db, order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {"message": "Delivery completed"}

@router.get("/drivers/nearby")
def get_nearby_drivers_with_tracking(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude"),
    radius: float = Query(10.0, description="Search radius in kilometers"),
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Get nearby drivers with their current locations"""
    nearby_drivers = location_service.find_nearby_drivers(
        db=db,
        latitude=latitude,
        longitude=longitude,
        max_radius=radius
    )
    
    result = []
    for driver, distance in nearby_drivers:
        driver_data = {
            "id": driver.id,
            "name": f"{driver.first_name} {driver.last_name}",
            "phone": driver.phone_number,
            "vehicle_type": driver.vehicle_type.value,
            "vehicle_plate": driver.vehicle_plate,
            "rating": driver.rating,
            "distance": distance,
            "status": driver.status.value
        }
        
        # Add live location if available
        live_location = tracking_service.get_driver_location(driver.id)
        if live_location:
            driver_data["current_location"] = live_location
        
        result.append(driver_data)
    
    return result

@router.get("/analytics/driver-activity")
def get_driver_activity_analytics(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Get driver activity analytics"""
    all_locations = tracking_service.get_all_driver_locations()
    
    analytics = {
        "total_active_drivers": len(all_locations),
        "drivers_by_status": {},
        "average_speed": 0,
        "active_deliveries": len(tracking_service.order_tracking)
    }
    
    speeds = []
    for location_data in all_locations.values():
        status = location_data.get("status", "unknown")
        analytics["drivers_by_status"][status] = analytics["drivers_by_status"].get(status, 0) + 1
        
        if location_data.get("speed"):
            speeds.append(location_data["speed"])
    
    if speeds:
        analytics["average_speed"] = sum(speeds) / len(speeds)
    
    return analytics