from fastapi import HTTPException
from models.mongo_models import ServiceProvider, ProviderStatus
from schemas.service_provider import ServiceProviderCreate, ServiceProviderUpdate, ServiceProviderResponse
from core.security import get_password_hash as hash_password
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
import logging

# Set up logging
logger = logging.getLogger(__name__)

async def create_service_provider(provider: ServiceProviderCreate) -> ServiceProvider:
    """Create a new service provider"""
    try:
        # Check for duplicate email or phone
        existing = await ServiceProvider.find_one({
            "$or": [
                {"email": provider.email},
                {"phone_number": provider.phone_number}
            ]
        })

        if existing:
            raise HTTPException(status_code=400, detail="Phone or email already registered")

        # Create new service provider
        db_provider = ServiceProvider(
            first_name=provider.first_name,
            middle_name=provider.middle_name,
            last_name=provider.last_name,
            email=provider.email,
            address=provider.address,
            nearby_condominum=provider.nearby_condominum,
            longitude=provider.longitude,
            latitude=provider.latitude,
            phone_number=provider.phone_number,
            washing_machine=provider.washing_machine,
            date_of_birth=provider.date_of_birth,
            status=ProviderStatus.OFFLINE,
            is_active=True,
            is_available=True,
            service_radius=provider.service_radius or 5.0,
            business_name=provider.business_name,
            description=provider.description
        )

        await db_provider.insert()
        return db_provider

    except Exception as e:
        logger.error(f"Error creating service provider: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_all_service_providers(
    skip: int = 0,
    limit: int = 100,
    status: Optional[ProviderStatus] = None,
    is_active: Optional[bool] = None
) -> List[ServiceProvider]:
    """Get all service providers with optional filtering"""
    try:
        query = {}
        if status:
            query["status"] = status
        if is_active is not None:
            query["is_active"] = is_active

        providers = await ServiceProvider.find(query).skip(skip).limit(limit).to_list()
        return providers

    except Exception as e:
        logger.error(f"Error getting service providers: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_service_provider_by_id(provider_id: str) -> ServiceProvider:
    """Get service provider by ID"""
    try:
        provider = await ServiceProvider.get(ObjectId(provider_id))
        if not provider:
            raise HTTPException(status_code=404, detail="Service provider not found")
        return provider

    except Exception as e:
        logger.error(f"Error getting service provider {provider_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def update_service_provider(
    provider_id: str,
    provider_update: ServiceProviderUpdate
) -> ServiceProvider:
    """Update service provider details"""
    try:
        provider = await ServiceProvider.get(ObjectId(provider_id))
        if not provider:
            raise HTTPException(status_code=404, detail="Service provider not found")

        # Update only provided fields
        update_data = provider_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(provider, field, value)

        provider.updated_at = datetime.utcnow()
        await provider.save()
        return provider

    except Exception as e:
        logger.error(f"Error updating service provider {provider_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def delete_service_provider(provider_id: str) -> bool:
    """Delete service provider"""
    try:
        provider = await ServiceProvider.get(ObjectId(provider_id))
        if not provider:
            raise HTTPException(status_code=404, detail="Service provider not found")

        await provider.delete()
        return True

    except Exception as e:
        logger.error(f"Error deleting service provider {provider_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def update_provider_status(
    provider_id: str,
    status: ProviderStatus,
    is_available: Optional[bool] = None
) -> ServiceProvider:
    """Update service provider status"""
    try:
        provider = await ServiceProvider.get(ObjectId(provider_id))
        if not provider:
            raise HTTPException(status_code=404, detail="Service provider not found")

        provider.status = status
        if is_available is not None:
            provider.is_available = is_available
        provider.updated_at = datetime.utcnow()

        await provider.save()
        return provider

    except Exception as e:
        logger.error(f"Error updating provider status {provider_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_nearby_providers(
    latitude: float,
    longitude: float,
    max_distance: float = 5.0,
    limit: int = 10
) -> List[ServiceProvider]:
    """Get nearby service providers using geospatial query"""
    try:
        providers = await ServiceProvider.find({
            "is_active": True,
            "is_available": True,
            "status": ProviderStatus.ACTIVE,
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
                            max_distance / 111.0  # Convert km to degrees (approximate)
                        ]
                    }
                }
            ]
        }).sort([
            ("rating", -1),
            ("total_orders_completed", -1)
        ]).limit(limit).to_list()

        return providers

    except Exception as e:
        logger.error(f"Error finding nearby providers: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def update_provider_location(
    provider_id: str,
    latitude: float,
    longitude: float
) -> ServiceProvider:
    """Update service provider location"""
    try:
        provider = await ServiceProvider.get(ObjectId(provider_id))
        if not provider:
            raise HTTPException(status_code=404, detail="Service provider not found")

        provider.latitude = latitude
        provider.longitude = longitude
        provider.updated_at = datetime.utcnow()

        await provider.save()
        return provider

    except Exception as e:
        logger.error(f"Error updating provider location {provider_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
