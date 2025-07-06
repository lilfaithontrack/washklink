from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from models.booking import Booking
from models.service_provider import ServiceProvider
from db.models.driver import Driver, DriverStatus
from services.location_service import location_service
import logging

logger = logging.getLogger(__name__)

class AssignmentService:
    def __init__(self):
        self.max_assignment_attempts = 3
        self.assignment_radius_increment = 2.0  # km

    async def assign_order_to_provider(
        self, 
        db: Session, 
        order_id: int,
        preferred_provider_id: Optional[int] = None
    ) -> Optional[ServiceProvider]:
        """
        Assign an order to the best available service provider based on location
        """
        order = db.query(Booking).filter(Booking.id == order_id).first()
        if not order:
            logger.error(f"Order {order_id} not found")
            return None

        # For now, assign to first available provider
        # You can enhance this with location-based logic later
        provider = db.query(ServiceProvider).filter(
            ServiceProvider.is_active == True
        ).first()
        
        if provider:
            # Update order with provider assignment
            # Note: You'll need to add service_provider_id to Booking model
            logger.info(f"Order {order_id} assigned to provider {provider.id}")
            return provider
        
        return None

    async def assign_driver_for_delivery(
        self, 
        db: Session, 
        order_id: int
    ) -> Optional[Driver]:
        """
        Assign a driver for order delivery
        """
        order = db.query(Booking).filter(Booking.id == order_id).first()
        if not order:
            return None

        # Find available drivers
        available_drivers = db.query(Driver).filter(
            Driver.status == DriverStatus.AVAILABLE,
            Driver.is_active == True
        ).all()

        if available_drivers:
            # Select first available driver (you can enhance this logic)
            best_driver = available_drivers[0]
            
            # Assign driver
            best_driver.status = DriverStatus.BUSY
            best_driver.current_order_id = order.id
            
            db.commit()
            
            logger.info(f"Driver {best_driver.id} assigned to order {order_id}")
            return best_driver
        
        return None

assignment_service = AssignmentService()