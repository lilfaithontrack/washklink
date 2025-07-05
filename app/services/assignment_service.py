from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db.models.order import Booking, OrderStatus
from app.db.models.laundry_provider import ServiceProvider, ProviderStatus
from app.db.models.driver import Driver, DriverStatus
from app.services.location_service import location_service
from app.services.notification_service import notification_service
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
        Assign an order to the best available service provider based on location and capacity
        """
        order = db.query(Booking).filter(Booking.id == order_id).first()
        if not order:
            logger.error(f"Order {order_id} not found")
            return None

        if order.status != OrderStatus.PENDING:
            logger.warning(f"Order {order_id} is not in pending status")
            return None

        # If preferred provider is specified, try to assign to them first
        if preferred_provider_id:
            provider = db.query(ServiceProvider).filter(
                ServiceProvider.id == preferred_provider_id,
                ServiceProvider.status == ProviderStatus.ACTIVE,
                ServiceProvider.is_available == True
            ).first()
            
            if provider and provider.current_order_count < provider.max_daily_orders:
                return await self._assign_to_provider(db, order, provider)

        # Find nearby providers
        search_radius = order.max_assignment_radius
        nearby_providers = location_service.find_nearby_providers(
            db=db,
            latitude=order.pickup_latitude,
            longitude=order.pickup_longitude,
            max_radius=search_radius
        )

        if not nearby_providers:
            # Expand search radius and try again
            order.assignment_attempts += 1
            if order.assignment_attempts < self.max_assignment_attempts:
                order.max_assignment_radius += self.assignment_radius_increment
                db.commit()
                logger.info(f"Expanding search radius for order {order_id} to {order.max_assignment_radius}km")
                return await self.assign_order_to_provider(db, order_id)
            else:
                logger.warning(f"No providers found for order {order_id} after {self.max_assignment_attempts} attempts")
                return None

        # Select the best provider based on multiple criteria
        best_provider = self._select_best_provider(nearby_providers, order)
        
        if best_provider:
            return await self._assign_to_provider(db, order, best_provider[0])
        
        return None

    def _select_best_provider(
        self, 
        nearby_providers: List[tuple], 
        order: Booking
    ) -> Optional[tuple]:
        """
        Select the best provider based on distance, rating, capacity, and service type
        """
        if not nearby_providers:
            return None

        # Score each provider
        scored_providers = []
        for provider, distance in nearby_providers:
            score = self._calculate_provider_score(provider, distance, order)
            scored_providers.append((provider, distance, score))

        # Sort by score (higher is better)
        scored_providers.sort(key=lambda x: x[2], reverse=True)
        
        return (scored_providers[0][0], scored_providers[0][1])

    def _calculate_provider_score(
        self, 
        provider: ServiceProvider, 
        distance: float, 
        order: Booking
    ) -> float:
        """
        Calculate a score for provider selection
        Higher score = better choice
        """
        # Base score starts at 100
        score = 100.0
        
        # Distance penalty (closer is better)
        distance_penalty = distance * 2  # 2 points per km
        score -= distance_penalty
        
        # Rating bonus (max 20 points)
        rating_bonus = provider.rating * 4  # 4 points per rating point
        score += rating_bonus
        
        # Capacity bonus (less busy is better)
        capacity_ratio = provider.current_order_count / provider.max_daily_orders
        capacity_bonus = (1 - capacity_ratio) * 15  # max 15 points
        score += capacity_bonus
        
        # Experience bonus
        if provider.total_orders_completed > 100:
            score += 10
        elif provider.total_orders_completed > 50:
            score += 5
        
        # Service type compatibility
        if order.service_type.value == "Machine Wash" and provider.washing_machine:
            score += 5
        
        # Completion time bonus (faster is better)
        if provider.average_completion_time < 12:  # less than 12 hours
            score += 8
        elif provider.average_completion_time < 24:  # less than 24 hours
            score += 4
        
        return max(score, 0)  # Ensure score is not negative

    async def _assign_to_provider(
        self, 
        db: Session, 
        order: Booking, 
        provider: ServiceProvider
    ) -> ServiceProvider:
        """
        Actually assign the order to the provider and update statuses
        """
        # Update order
        order.service_provider_id = provider.id
        order.status = OrderStatus.ASSIGNED
        order.assigned_at = datetime.utcnow()
        
        # Calculate estimated completion time
        estimated_hours = provider.average_completion_time
        order.estimated_completion_time = datetime.utcnow() + timedelta(hours=estimated_hours)
        
        # Update provider
        provider.current_order_count += 1
        provider.last_active = datetime.utcnow()
        
        # If provider is at capacity, mark as busy
        if provider.current_order_count >= provider.max_daily_orders:
            provider.is_available = False
            provider.status = ProviderStatus.BUSY
        
        db.commit()
        
        # Send notifications
        try:
            await notification_service.send_order_assignment_to_provider(
                provider.phone_number, order.id
            )
            await notification_service.send_order_confirmation(
                order.user.phone_number, order.id
            )
        except Exception as e:
            logger.error(f"Failed to send assignment notifications: {e}")
        
        logger.info(f"Order {order.id} assigned to provider {provider.id}")
        return provider

    async def assign_driver_for_delivery(
        self, 
        db: Session, 
        order_id: int
    ) -> Optional[Driver]:
        """
        Assign a driver for order delivery
        """
        order = db.query(Booking).filter(Booking.id == order_id).first()
        if not order or not order.delivery:
            return None

        # Use delivery location if available, otherwise pickup location
        lat = order.delivery_latitude or order.pickup_latitude
        lon = order.delivery_longitude or order.pickup_longitude
        
        if not lat or not lon:
            logger.error(f"No location data for order {order_id}")
            return None

        # Find nearby drivers
        nearby_drivers = location_service.find_nearby_drivers(
            db=db,
            latitude=lat,
            longitude=lon,
            max_radius=15.0
        )

        if not nearby_drivers:
            logger.warning(f"No drivers available for order {order_id}")
            return None

        # Select the best driver (closest with highest rating)
        best_driver = nearby_drivers[0][0]
        
        # Assign driver
        order.driver_id = best_driver.id
        best_driver.status = DriverStatus.BUSY
        best_driver.current_order_id = order.id
        
        # Calculate estimated delivery time
        distance = nearby_drivers[0][1]
        estimated_minutes = distance * 3 + 15  # 3 min per km + 15 min buffer
        order.estimated_delivery_time = datetime.utcnow() + timedelta(minutes=estimated_minutes)
        
        db.commit()
        
        # Send notifications
        try:
            await notification_service.send_driver_assigned(
                order.user.phone_number, order.id, f"{best_driver.first_name} {best_driver.last_name}"
            )
        except Exception as e:
            logger.error(f"Failed to send driver assignment notification: {e}")
        
        logger.info(f"Driver {best_driver.id} assigned to order {order_id}")
        return best_driver

    async def auto_assign_pending_orders(self, db: Session):
        """
        Background task to automatically assign pending orders
        """
        pending_orders = db.query(Booking).filter(
            Booking.status == OrderStatus.PENDING,
            Booking.assignment_attempts < self.max_assignment_attempts
        ).all()

        for order in pending_orders:
            try:
                await self.assign_order_to_provider(db, order.id)
            except Exception as e:
                logger.error(f"Failed to auto-assign order {order.id}: {e}")

assignment_service = AssignmentService()