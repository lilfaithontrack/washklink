import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.tracking_service import tracking_service
from app.services.assignment_service import assignment_service
from app.db.models.driver import Driver, DriverStatus
from app.db.models.order import Booking, OrderStatus

logger = logging.getLogger(__name__)

class BackgroundTaskService:
    def __init__(self):
        self.running = False

    async def start_background_tasks(self):
        """Start all background tasks"""
        self.running = True
        
        # Start multiple background tasks concurrently
        await asyncio.gather(
            self.cleanup_stale_tracking_data(),
            self.auto_assign_pending_orders(),
            self.update_driver_statuses(),
            self.monitor_delivery_times()
        )

    async def stop_background_tasks(self):
        """Stop all background tasks"""
        self.running = False

    async def cleanup_stale_tracking_data(self):
        """Clean up stale tracking data every 5 minutes"""
        while self.running:
            try:
                await tracking_service.cleanup_stale_data()
                logger.info("Cleaned up stale tracking data")
            except Exception as e:
                logger.error(f"Error cleaning up tracking data: {e}")
            
            await asyncio.sleep(300)  # 5 minutes

    async def auto_assign_pending_orders(self):
        """Auto-assign pending orders every 2 minutes"""
        while self.running:
            try:
                db = SessionLocal()
                await assignment_service.auto_assign_pending_orders(db)
                db.close()
                logger.info("Processed pending order assignments")
            except Exception as e:
                logger.error(f"Error in auto-assignment: {e}")
            
            await asyncio.sleep(120)  # 2 minutes

    async def update_driver_statuses(self):
        """Update driver statuses based on activity every 10 minutes"""
        while self.running:
            try:
                db = SessionLocal()
                
                # Mark drivers as offline if they haven't been active for 30 minutes
                inactive_threshold = datetime.utcnow() - timedelta(minutes=30)
                inactive_drivers = db.query(Driver).filter(
                    Driver.last_active < inactive_threshold,
                    Driver.status != DriverStatus.OFFLINE
                ).all()
                
                for driver in inactive_drivers:
                    driver.status = DriverStatus.OFFLINE
                    logger.info(f"Marked driver {driver.id} as offline due to inactivity")
                
                db.commit()
                db.close()
                
            except Exception as e:
                logger.error(f"Error updating driver statuses: {e}")
            
            await asyncio.sleep(600)  # 10 minutes

    async def monitor_delivery_times(self):
        """Monitor delivery times and send alerts for delays"""
        while self.running:
            try:
                db = SessionLocal()
                
                # Find orders that are overdue for delivery
                current_time = datetime.utcnow()
                overdue_orders = db.query(Booking).filter(
                    Booking.status == OrderStatus.OUT_FOR_DELIVERY,
                    Booking.estimated_delivery_time < current_time
                ).all()
                
                for order in overdue_orders:
                    # Send delay notification
                    logger.warning(f"Order {order.id} is overdue for delivery")
                    # You can add notification logic here
                
                db.close()
                
            except Exception as e:
                logger.error(f"Error monitoring delivery times: {e}")
            
            await asyncio.sleep(300)  # 5 minutes

# Global instance
background_service = BackgroundTaskService()