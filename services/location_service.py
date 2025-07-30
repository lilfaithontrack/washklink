import math
from typing import List, Tuple, Optional
from models.mongo_models import ServiceProvider, Driver, DriverStatus, Order
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class LocationService:
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)
        Returns distance in kilometers
        """
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        return c * r

    @staticmethod
    async def find_nearby_providers(
        latitude: float, 
        longitude: float, 
        max_radius: float = 10.0,
        service_type: str = None
    ) -> List[Tuple[ServiceProvider, float]]:
        """
        Find service providers within a given radius, sorted by distance
        Returns list of tuples (provider, distance_km)
        """
        # Use MongoDB's geospatial query to find nearby providers
        providers = await ServiceProvider.find(
            {
                "is_active": True,
                "$and": [
                    {
                        "$expr": {
                            "$lte": [
                                {
                                    "$sqrt": {
                                        "$add": [
                                            {
                                                "$pow": [
                                                    {"$subtract": ["$latitude", latitude]},
                                                    2
                                                ]
                                            },
                                            {
                                                "$pow": [
                                                    {"$subtract": ["$longitude", longitude]},
                                                    2
                                                ]
                                            }
                                        ]
                                    }
                                },
                                max_radius / 111.0  # Convert km to degrees (approximate)
                            ]
                        }
                    }
                ]
            }
        ).to_list()

        nearby_providers = []
        
        for provider in providers:
            distance = LocationService.calculate_distance(
                latitude, longitude,
                provider.latitude, provider.longitude
            )
            
            # Check if provider is within max radius
            if distance <= max_radius:
                nearby_providers.append((provider, distance))

        # Sort by distance
        nearby_providers.sort(key=lambda x: x[1])
        return nearby_providers

    @staticmethod
    async def find_nearby_drivers(
        latitude: float,
        longitude: float,
        max_radius: float = 15.0
    ) -> List[Tuple[Driver, float]]:
        """
        Find available drivers within a given radius, sorted by distance
        Returns list of tuples (driver, distance_km)
        """
        # Use MongoDB's geospatial query to find nearby drivers
        drivers = await Driver.find(
            {
                "status": DriverStatus.AVAILABLE,
                "is_active": True,
                "current_latitude": {"$ne": None},
                "current_longitude": {"$ne": None},
                "$and": [
                    {
                        "$expr": {
                            "$lte": [
                                {
                                    "$sqrt": {
                                        "$add": [
                                            {
                                                "$pow": [
                                                    {"$subtract": ["$current_latitude", latitude]},
                                                    2
                                                ]
                                            },
                                            {
                                                "$pow": [
                                                    {"$subtract": ["$current_longitude", longitude]},
                                                    2
                                                ]
                                            }
                                        ]
                                    }
                                },
                                max_radius / 111.0  # Convert km to degrees (approximate)
                            ]
                        }
                    }
                ]
            }
        ).to_list()

        nearby_drivers = []
        
        for driver in drivers:
            distance = LocationService.calculate_distance(
                latitude, longitude,
                driver.current_latitude, driver.current_longitude
            )
            
            # Check if driver is within their service radius and our max radius
            if distance <= min(driver.service_radius, max_radius):
                nearby_drivers.append((driver, distance))

        # Sort by distance and rating
        nearby_drivers.sort(key=lambda x: (x[1], -x[0].rating))
        return nearby_drivers

    @staticmethod
    async def update_driver_location(
        driver_id: str,
        latitude: float,
        longitude: float
    ) -> Optional[Driver]:
        """Update driver's current location"""
        try:
            driver = await Driver.get(ObjectId(driver_id))
            if not driver:
                return None

            driver.current_latitude = latitude
            driver.current_longitude = longitude
            driver.last_location_update = datetime.utcnow()
            await driver.save()

            return driver
        except Exception as e:
            logger.error(f"Error updating driver location: {str(e)}")
            return None

    @staticmethod
    async def get_active_drivers_in_area(
        latitude: float,
        longitude: float,
        radius: float = 10.0
    ) -> List[Driver]:
        """Get all active drivers in a specific area"""
        try:
            return await Driver.find(
                {
                    "is_active": True,
                    "status": {"$in": [DriverStatus.AVAILABLE, DriverStatus.ON_DELIVERY]},
                    "$and": [
                        {
                            "$expr": {
                                "$lte": [
                                    {
                                        "$sqrt": {
                                            "$add": [
                                                {
                                                    "$pow": [
                                                        {"$subtract": ["$current_latitude", latitude]},
                                                        2
                                                    ]
                                                },
                                                {
                                                    "$pow": [
                                                        {"$subtract": ["$current_longitude", longitude]},
                                                        2
                                                    ]
                                                }
                                            ]
                                        }
                                    },
                                    radius / 111.0  # Convert km to degrees (approximate)
                                ]
                            }
                        }
                    ]
                }
            ).to_list()
        except Exception as e:
            logger.error(f"Error getting active drivers in area: {str(e)}")
            return []

    @staticmethod
    async def get_active_providers_in_area(
        latitude: float,
        longitude: float,
        radius: float = 10.0
    ) -> List[ServiceProvider]:
        """Get all active service providers in a specific area"""
        try:
            return await ServiceProvider.find(
                {
                    "is_active": True,
                    "is_available": True,
                    "$and": [
                        {
                            "$expr": {
                                "$lte": [
                                    {
                                        "$sqrt": {
                                            "$add": [
                                                {
                                                    "$pow": [
                                                        {"$subtract": ["$latitude", latitude]},
                                                        2
                                                    ]
                                                },
                                                {
                                                    "$pow": [
                                                        {"$subtract": ["$longitude", longitude]},
                                                        2
                                                    ]
                                                }
                                            ]
                                        }
                                    },
                                    radius / 111.0  # Convert km to degrees (approximate)
                                ]
                            }
                        }
                    ]
                }
            ).to_list()
        except Exception as e:
            logger.error(f"Error getting active providers in area: {str(e)}")
            return []

location_service = LocationService()