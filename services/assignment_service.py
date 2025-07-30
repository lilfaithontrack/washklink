from typing import Optional, List
from datetime import datetime, timedelta
from models.mongo_models import (
    Order, ServiceProvider, Driver, 
    DriverStatus, OrderStatus, ProviderStatus
)
from services.location_service import location_service
import logging
from bson import ObjectId

logger = logging.getLogger(__name__)

class AssignmentService:
    def __init__(self):
        self.max_assignment_attempts = 3
        self.assignment_radius_increment = 2.0  # km

    async def assign_order_to_provider(
        self, 
        order_id: str,
        preferred_provider_id: Optional[str] = None
    ) -> Optional[ServiceProvider]:
        """
        Assign an order to the best available service provider based on location
        """
        try:
            order = await Order.get(ObjectId(order_id))
            if not order:
                logger.error(f"Order {order_id} not found")
                return None

            # If preferred provider is specified, try to assign to them first
            if preferred_provider_id:
                provider = await ServiceProvider.get(ObjectId(preferred_provider_id))
                if provider and provider.is_active and provider.is_available:
                    await self._assign_provider(order, provider)
                    return provider

            # Find providers within radius
            base_radius = order.max_assignment_radius or 5.0  # km
            current_radius = base_radius

            for attempt in range(self.max_assignment_attempts):
                # Find available providers within radius
                providers = await ServiceProvider.find(
                    {
                        "is_active": True,
                        "is_available": True,
                        "status": ProviderStatus.ACTIVE,
                        "current_order_count": {"$lt": "$max_daily_orders"},
                        "$and": [
                            {
                                "$expr": {
                                    "$lte": [
                                        {
                                            "$sqrt": {
                                                "$add": [
                                                    {
                                                        "$pow": [
                                                            {"$subtract": ["$latitude", order.pickup_latitude]},
                                                            2
                                                        ]
                                                    },
                                                    {
                                                        "$pow": [
                                                            {"$subtract": ["$longitude", order.pickup_longitude]},
                                                            2
                                                        ]
                                                    }
                                                ]
                                            }
                                        },
                                        current_radius / 111.0  # Convert km to degrees (approximate)
                                    ]
                                }
                            }
                        ]
                    }
                ).sort([
                    ("rating", -1),
                    ("total_orders_completed", -1)
                ]).to_list()

                if providers:
                    # Assign to best matching provider
                    best_provider = providers[0]
                    await self._assign_provider(order, best_provider)
                    return best_provider

                # Increase radius for next attempt
                current_radius += self.assignment_radius_increment
                logger.info(f"No providers found within {current_radius}km, expanding search radius")

            logger.warning(f"Failed to assign order {order_id} after {self.max_assignment_attempts} attempts")
            return None

        except Exception as e:
            logger.error(f"Error assigning order to provider: {str(e)}")
            return None

    async def assign_driver_for_delivery(
        self, 
        order_id: str
    ) -> Optional[Driver]:
        """
        Assign a driver for order delivery
        """
        try:
            order = await Order.get(ObjectId(order_id))
            if not order:
                logger.error(f"Order {order_id} not found")
                return None

            # Find available drivers within radius
            base_radius = 5.0  # km
            drivers = await Driver.find(
                {
                    "status": DriverStatus.AVAILABLE,
                    "is_active": True,
                    "current_order_id": None,
                    "$and": [
                        {
                            "$expr": {
                                "$lte": [
                                    {
                                        "$sqrt": {
                                            "$add": [
                                                {
                                                    "$pow": [
                                                        {"$subtract": ["$current_latitude", order.pickup_latitude]},
                                                        2
                                                    ]
                                                },
                                                {
                                                    "$pow": [
                                                        {"$subtract": ["$current_longitude", order.pickup_longitude]},
                                                        2
                                                    ]
                                                }
                                            ]
                                        }
                                    },
                                    base_radius / 111.0  # Convert km to degrees (approximate)
                                ]
                            }
                        }
                    ]
                }
            ).sort([
                ("rating", -1),
                ("successful_deliveries", -1)
            ]).to_list()

            if drivers:
                # Assign to best matching driver
                best_driver = drivers[0]
                await self._assign_driver(order, best_driver)
                return best_driver

            logger.warning(f"No available drivers found for order {order_id}")
            return None

        except Exception as e:
            logger.error(f"Error assigning driver to order: {str(e)}")
            return None

    async def _assign_provider(self, order: Order, provider: ServiceProvider):
        """Helper method to update order and provider after assignment"""
        try:
            # Update order
            order.service_provider_id = provider.id
            order.status = OrderStatus.ASSIGNED
            order.assigned_at = datetime.utcnow()
            await order.save()

            # Update provider
            provider.current_order_count += 1
            await provider.save()

            logger.info(f"Order {order.id} assigned to provider {provider.id}")

        except Exception as e:
            logger.error(f"Error in _assign_provider: {str(e)}")
            raise

    async def _assign_driver(self, order: Order, driver: Driver):
        """Helper method to update order and driver after assignment"""
        try:
            # Update order
            order.driver_id = driver.id
            order.status = OrderStatus.OUT_FOR_DELIVERY
            await order.save()

            # Update driver
            driver.status = DriverStatus.ON_DELIVERY
            driver.current_order_id = order.id
            await driver.save()

            logger.info(f"Driver {driver.id} assigned to order {order.id}")

        except Exception as e:
            logger.error(f"Error in _assign_driver: {str(e)}")
            raise

assignment_service = AssignmentService()