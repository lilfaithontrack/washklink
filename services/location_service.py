import math
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from models.service_provider import ServiceProvider
from db.models.driver import Driver, DriverStatus
from models.booking import Booking

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
    def find_nearby_providers(
        db: Session, 
        latitude: float, 
        longitude: float, 
        max_radius: float = 10.0,
        service_type: str = None
    ) -> List[Tuple[ServiceProvider, float]]:
        """
        Find service providers within a given radius, sorted by distance
        Returns list of tuples (provider, distance_km)
        """
        # Get all active providers
        providers = db.query(ServiceProvider).filter(
            ServiceProvider.is_active == True
        ).all()

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
    def find_nearby_drivers(
        db: Session,
        latitude: float,
        longitude: float,
        max_radius: float = 15.0
    ) -> List[Tuple[Driver, float]]:
        """
        Find available drivers within a given radius, sorted by distance
        Returns list of tuples (driver, distance_km)
        """
        # Get all available drivers
        drivers = db.query(Driver).filter(
            Driver.status == DriverStatus.AVAILABLE,
            Driver.is_active == True,
            Driver.current_latitude.isnot(None),
            Driver.current_longitude.isnot(None)
        ).all()

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

location_service = LocationService()