from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Form, UploadFile, File
from api.deps import get_admin_user, get_manager_user
from models.mongo_models import ServiceProvider, ProviderStatus
from controllers.service_provider import (
    get_all_service_providers,
    get_service_provider_by_id,
    create_service_provider,
    update_service_provider,
    delete_service_provider
)
from datetime import date, datetime
import json
from schemas.service_provider import ServiceProviderApproval, ServiceProviderCreate, ServiceProviderUpdate

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_all_providers(
    current_user: ServiceProvider = Depends(get_manager_user),
    status: Optional[ProviderStatus] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    Get all service providers with optional filtering.
    Requires manager or admin permissions.
    """
    try:
        providers = await get_all_service_providers(
            skip=skip,
            limit=limit,
            status=status
        )
        
        # Convert to dict format for response
        provider_list = []
        for provider in providers:
            provider_dict = {
                "id": str(provider.id),
                "first_name": provider.first_name,
                "middle_name": provider.middle_name,
                "last_name": provider.last_name,
                "full_name": provider.full_name,
                "email": provider.email,
                "phone_number": provider.phone_number,
                "address": provider.address,
                "latitude": provider.latitude,
                "longitude": provider.longitude,
                "nearby_condominum": provider.nearby_condominum,
                "status": provider.status,
                "is_active": provider.is_active,
                "is_available": provider.is_available,
                "is_verified": provider.is_verified,
                "washing_machine": provider.washing_machine,
                "has_dryer": provider.has_dryer,
                "has_iron": provider.has_iron,
                "max_daily_orders": provider.max_daily_orders,
                "current_order_count": provider.current_order_count,
                "rating": provider.rating,
                "total_orders_completed": provider.total_orders_completed,
                "business_name": provider.business_name,
                "business_license": provider.business_license,
                "description": provider.description,
                "created_at": provider.created_at,
                "updated_at": provider.updated_at,
                "last_active": provider.last_active
            }
            provider_list.append(provider_dict)
        
        return provider_list
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving providers: {str(e)}")

@router.get("/{provider_id}")
async def get_provider_by_id(
    provider_id: str,
    current_user: ServiceProvider = Depends(get_manager_user)
):
    """
    Get a specific service provider by ID.
    Requires manager or admin permissions.
    """
    try:
        provider = await get_service_provider_by_id(provider_id)
        return {
            "id": str(provider.id),
            "first_name": provider.first_name,
            "middle_name": provider.middle_name,
            "last_name": provider.last_name,
            "full_name": provider.full_name,
            "email": provider.email,
            "phone_number": provider.phone_number,
            "address": provider.address,
            "latitude": provider.latitude,
            "longitude": provider.longitude,
            "nearby_condominum": provider.nearby_condominum,
            "status": provider.status,
            "is_active": provider.is_active,
            "is_available": provider.is_available,
            "is_verified": provider.is_verified,
            "washing_machine": provider.washing_machine,
            "has_dryer": provider.has_dryer,
            "has_iron": provider.has_iron,
            "max_daily_orders": provider.max_daily_orders,
            "current_order_count": provider.current_order_count,
            "rating": provider.rating,
            "total_orders_completed": provider.total_orders_completed,
            "business_name": provider.business_name,
            "business_license": provider.business_license,
            "description": provider.description,
            "created_at": provider.created_at,
            "updated_at": provider.updated_at,
            "last_active": provider.last_active
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving provider: {str(e)}")

@router.post("/")
async def create_service_provider_endpoint(
    first_name: str = Form(...),
    middle_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone_number: int = Form(...),
    address: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    nearby_condominum: str = Form(...),
    washing_machine: bool = Form(True),
    has_dryer: bool = Form(False),
    has_iron: bool = Form(True),
    service_radius: Optional[float] = Form(10.0),
    business_name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    date_of_birth: Optional[date] = Form(None),
    current_user: ServiceProvider = Depends(get_admin_user)
):
    """
    Create a new service provider.
    Requires admin permissions.
    """
    try:
        # Convert date to datetime if provided
        date_of_birth_dt = None
        if date_of_birth:
            date_of_birth_dt = datetime.combine(date_of_birth, datetime.min.time())
        
        provider_data = ServiceProviderCreate(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            address=address,
            latitude=latitude,
            longitude=longitude,
            nearby_condominum=nearby_condominum,
            washing_machine=washing_machine,
            has_dryer=has_dryer,
            has_iron=has_iron,
            service_radius=service_radius,
            business_name=business_name,
            description=description,
            date_of_birth=date_of_birth_dt or datetime(2000, 1, 1)
        )
        
        provider = await create_service_provider(provider_data)
        
        return {
            "message": "Service provider created successfully",
            "provider_id": str(provider.id),
            "provider": {
                "id": str(provider.id),
                "full_name": provider.full_name,
                "email": provider.email,
                "phone_number": provider.phone_number,
                "status": provider.status
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating provider: {str(e)}")

@router.put("/{provider_id}")
async def update_service_provider_endpoint(
    provider_id: str,
    first_name: Optional[str] = Form(None),
    middle_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone_number: Optional[int] = Form(None),
    address: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    nearby_condominum: Optional[str] = Form(None),
    washing_machine: Optional[bool] = Form(None),
    has_dryer: Optional[bool] = Form(None),
    has_iron: Optional[bool] = Form(None),
    service_radius: Optional[float] = Form(None),
    business_name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    max_daily_orders: Optional[int] = Form(None),
    current_user: ServiceProvider = Depends(get_admin_user)
):
    """
    Update a service provider.
    Requires admin permissions.
    """
    try:
        # Create update data dict with only provided fields
        update_data = {}
        if first_name is not None:
            update_data["first_name"] = first_name
        if middle_name is not None:
            update_data["middle_name"] = middle_name
        if last_name is not None:
            update_data["last_name"] = last_name
        if email is not None:
            update_data["email"] = email
        if phone_number is not None:
            update_data["phone_number"] = phone_number
        if address is not None:
            update_data["address"] = address
        if latitude is not None:
            update_data["latitude"] = latitude
        if longitude is not None:
            update_data["longitude"] = longitude
        if nearby_condominum is not None:
            update_data["nearby_condominum"] = nearby_condominum
        if washing_machine is not None:
            update_data["washing_machine"] = washing_machine
        if has_dryer is not None:
            update_data["has_dryer"] = has_dryer
        if has_iron is not None:
            update_data["has_iron"] = has_iron
        if service_radius is not None:
            update_data["service_radius"] = service_radius
        if business_name is not None:
            update_data["business_name"] = business_name
        if description is not None:
            update_data["description"] = description
        if max_daily_orders is not None:
            update_data["max_daily_orders"] = max_daily_orders
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")
        
        provider_update = ServiceProviderUpdate(**update_data)
        updated_provider = await update_service_provider(provider_id, provider_update)
        
        return {
            "message": "Service provider updated successfully",
            "provider": {
                "id": str(updated_provider.id),
                "full_name": updated_provider.full_name,
                "email": updated_provider.email,
                "phone_number": updated_provider.phone_number,
                "status": updated_provider.status,
                "updated_at": updated_provider.updated_at
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating provider: {str(e)}")

@router.post("/{provider_id}/approve")
async def update_provider_approval(
    provider_id: str,
    approval: ServiceProviderApproval,
    current_user: ServiceProvider = Depends(get_admin_user)
):
    """
    Approve or reject a service provider.
    Requires admin permissions.
    """
    try:
        # Update provider verification status
        is_approved = approval.approval_status.lower() == "approved"
        update_data = {"is_verified": is_approved}
        
        if not is_approved and approval.rejection_reason:
            # For now, we'll store rejection reason in description
            # You might want to add a specific field for this in the model
            update_data["description"] = f"Rejected: {approval.rejection_reason}"
        
        provider_update = ServiceProviderUpdate(**update_data)
        updated_provider = await update_service_provider(provider_id, provider_update)
        
        action = approval.approval_status.lower()
        return {
            "message": f"Service provider {action} successfully",
            "provider_id": str(updated_provider.id),
            "is_verified": updated_provider.is_verified
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating provider approval: {str(e)}")

@router.delete("/{provider_id}")
async def delete_provider(
    provider_id: str,
    current_user: ServiceProvider = Depends(get_admin_user)
):
    """
    Delete a service provider.
    Requires admin permissions.
    """
    try:
        success = await delete_service_provider(provider_id)
        if success:
            return {"message": "Service provider deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Service provider not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting provider: {str(e)}")

@router.get("/stats/summary", response_model=dict)
async def get_providers_summary(
    current_user: ServiceProvider = Depends(get_manager_user)
):
    """Get service providers summary statistics"""
    try:
        # Get all providers for counting (we'll use large limit to get all)
        all_providers = await get_all_service_providers(limit=10000)
        
        total_providers = len(all_providers)
        active_providers = len([p for p in all_providers if p.is_active])
        verified_providers = len([p for p in all_providers if p.is_verified])
        busy_providers = len([p for p in all_providers if p.status == ProviderStatus.BUSY])
        
        return {
            "total_providers": total_providers,
            "active_providers": active_providers,
            "verified_providers": verified_providers,
            "busy_providers": busy_providers,
            "inactive_providers": total_providers - active_providers
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving providers summary: {str(e)}") 