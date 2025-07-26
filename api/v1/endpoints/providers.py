from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Form, UploadFile, File
from sqlalchemy.orm import Session
from api.deps import get_db, get_admin_user, get_manager_user
from db.models.service_provider import ServiceProvider
from models.users import DBUser
from datetime import date, datetime
import json
from schemas.service_provider import ServiceProviderApproval

router = APIRouter(redirect_slashes=False)

@router.get("/", response_model=List[dict])
def get_all_providers(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_manager_user),
    status: Optional[str] = Query(None, description="Filter by status"),
    approval_status: Optional[str] = Query(None, description="Filter by approval status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all service providers (Manager/Admin only)"""
    query = db.query(ServiceProvider)
    
    if status:
        query = query.filter(ServiceProvider.status == status)
    
    if approval_status:
        query = query.filter(ServiceProvider.approval_status == approval_status)
    
    providers = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": provider.id,
            "first_name": provider.first_name,
            "middle_name": provider.middle_name,
            "last_name": provider.last_name,
            "full_name": f"{provider.first_name} {provider.middle_name} {provider.last_name}",
            "email": provider.email,
            "phone_number": provider.phone_number,
            "address": provider.address,
            "status": provider.status,
            "is_active": provider.is_active,
            "is_verified": provider.is_verified,
            "approval_status": provider.approval_status,
            "approved_at": provider.approved_at.isoformat() if provider.approved_at else None,
            "rejection_reason": provider.rejection_reason,
            "business_name": provider.business_name,
            "rating": provider.rating,
            "total_orders_completed": provider.total_orders_completed,
            "max_daily_orders": provider.max_daily_orders,
            "current_order_count": provider.current_order_count,
            "created_at": provider.created_at.isoformat() if provider.created_at else None,
            "last_active": provider.last_active.isoformat() if provider.last_active else None
        }
        for provider in providers
    ]

@router.get("/{provider_id}", response_model=dict)
def get_provider_by_id(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_manager_user)
):
    """Get service provider by ID"""
    provider = db.query(ServiceProvider).filter(ServiceProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Service provider not found")
    
    return {
        "id": provider.id,
        "first_name": provider.first_name,
        "middle_name": provider.middle_name,
        "last_name": provider.last_name,
        "full_name": f"{provider.first_name} {provider.middle_name} {provider.last_name}",
        "email": provider.email,
        "phone_number": provider.phone_number,
        "address": provider.address,
        "status": provider.status,
        "is_active": provider.is_active,
        "is_verified": provider.is_verified,
        "business_name": provider.business_name,
        "business_license": provider.business_license,
        "description": provider.description,
        "latitude": provider.latitude,
        "longitude": provider.longitude,
        "service_radius": provider.service_radius,
        "nearby_condominum": provider.nearby_condominum,
        "date_of_birth": provider.date_of_birth.isoformat() if provider.date_of_birth else None,
        "washing_machine": provider.washing_machine,
        "has_dryer": provider.has_dryer,
        "has_iron": provider.has_iron,
        "max_daily_orders": provider.max_daily_orders,
        "current_order_count": provider.current_order_count,
        "average_completion_time": provider.average_completion_time,
        "rating": provider.rating,
        "total_orders_completed": provider.total_orders_completed,
        "created_at": provider.created_at.isoformat() if provider.created_at else None,
        "updated_at": provider.updated_at.isoformat() if provider.updated_at else None,
        "last_active": provider.last_active.isoformat() if provider.last_active else None
    }

@router.post("/", response_model=dict)
def create_service_provider(
    first_name: str = Form(...),
    middle_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone_number: int = Form(...),
    address: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    nearby_condominum: str = Form(...),
    business_name: Optional[str] = Form(None),
    business_license: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    date_of_birth: Optional[str] = Form(None),
    washing_machine: bool = Form(True),
    has_dryer: bool = Form(False),
    has_iron: bool = Form(True),
    max_daily_orders: int = Form(20),
    service_radius: float = Form(10.0),
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_admin_user)
):
    """Create a new service provider (Admin only)"""
    
    # Check if email already exists
    existing_email = db.query(ServiceProvider).filter(ServiceProvider.email == email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if phone number already exists
    existing_phone = db.query(ServiceProvider).filter(ServiceProvider.phone_number == phone_number).first()
    if existing_phone:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    # Parse date of birth
    dob = None
    if date_of_birth:
        try:
            dob = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Create new provider
    new_provider = ServiceProvider(
        first_name=first_name,
        middle_name=middle_name,
        last_name=last_name,
        email=email,
        phone_number=phone_number,
        address=address,
        latitude=latitude,
        longitude=longitude,
        nearby_condominum=nearby_condominum,
        business_name=business_name,
        business_license=business_license,
        description=description,
        date_of_birth=dob,
        washing_machine=washing_machine,
        has_dryer=has_dryer,
        has_iron=has_iron,
        max_daily_orders=max_daily_orders,
        service_radius=service_radius,
        status=ProviderStatus.OFFLINE.value,
        is_active=False,
        is_verified=False,
        approval_status='pending'
    )
    
    db.add(new_provider)
    db.commit()
    db.refresh(new_provider)
    
    return {
        "id": new_provider.id,
        "first_name": new_provider.first_name,
        "middle_name": new_provider.middle_name,
        "last_name": new_provider.last_name,
        "full_name": f"{new_provider.first_name} {new_provider.middle_name} {new_provider.last_name}",
        "email": new_provider.email,
        "phone_number": new_provider.phone_number,
        "address": new_provider.address,
        "status": new_provider.status,
        "is_active": new_provider.is_active,
        "is_verified": new_provider.is_verified,
        "approval_status": new_provider.approval_status,
        "business_name": new_provider.business_name,
        "message": "Service provider created successfully"
    }

@router.put("/{provider_id}", response_model=dict)
def update_service_provider(
    provider_id: int,
    first_name: Optional[str] = Form(None),
    middle_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone_number: Optional[int] = Form(None),
    address: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    nearby_condominum: Optional[str] = Form(None),
    business_name: Optional[str] = Form(None),
    business_license: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
    is_verified: Optional[bool] = Form(None),
    washing_machine: Optional[bool] = Form(None),
    has_dryer: Optional[bool] = Form(None),
    has_iron: Optional[bool] = Form(None),
    max_daily_orders: Optional[int] = Form(None),
    service_radius: Optional[float] = Form(None),
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_admin_user)
):
    """Update service provider (Admin only)"""
    
    provider = db.query(ServiceProvider).filter(ServiceProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Service provider not found")
    
    # Check if email already exists (if being updated)
    if email and email != provider.email:
        existing_email = db.query(ServiceProvider).filter(ServiceProvider.email == email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if phone number already exists (if being updated)
    if phone_number and phone_number != provider.phone_number:
        existing_phone = db.query(ServiceProvider).filter(ServiceProvider.phone_number == phone_number).first()
        if existing_phone:
            raise HTTPException(status_code=400, detail="Phone number already registered")
    
    # Update fields
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
    if business_name is not None:
        update_data["business_name"] = business_name
    if business_license is not None:
        update_data["business_license"] = business_license
    if description is not None:
        update_data["description"] = description
    if status is not None:
        update_data["status"] = status
    if is_active is not None:
        update_data["is_active"] = is_active
    if is_verified is not None:
        update_data["is_verified"] = is_verified
    if washing_machine is not None:
        update_data["washing_machine"] = washing_machine
    if has_dryer is not None:
        update_data["has_dryer"] = has_dryer
    if has_iron is not None:
        update_data["has_iron"] = has_iron
    if max_daily_orders is not None:
        update_data["max_daily_orders"] = max_daily_orders
    if service_radius is not None:
        update_data["service_radius"] = service_radius
    
    update_data["updated_at"] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(provider, field, value)
    
    db.commit()
    db.refresh(provider)
    
    return {
        "id": provider.id,
        "first_name": provider.first_name,
        "middle_name": provider.middle_name,
        "last_name": provider.last_name,
        "full_name": f"{provider.first_name} {provider.middle_name} {provider.last_name}",
        "email": provider.email,
        "phone_number": provider.phone_number,
        "address": provider.address,
        "status": provider.status,
        "is_active": provider.is_active,
        "is_verified": provider.is_verified,
        "business_name": provider.business_name,
        "message": "Service provider updated successfully"
    }

@router.delete("/{provider_id}")
def delete_service_provider(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_admin_user)
):
    """Delete service provider (Admin only)"""
    provider = db.query(ServiceProvider).filter(ServiceProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Service provider not found")
    
    db.delete(provider)
    db.commit()
    
    return {"message": "Service provider deleted successfully"}

@router.post("/{provider_id}/approve", response_model=dict)
def approve_provider(
    provider_id: int,
    approval: ServiceProviderApproval,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_admin_user)
):
    """Approve or reject a service provider (Admin only)"""
    provider = db.query(ServiceProvider).filter(ServiceProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Service provider not found")
    
    # Normalize to lowercase
    provider.approval_status = approval.approval_status.lower()
    provider.approved_by = current_user.id
    provider.approved_at = datetime.utcnow()
    
    if provider.approval_status == "approved":
        provider.is_active = True
        provider.status = ProviderStatus.ACTIVE.value
        provider.rejection_reason = None
    else:
        provider.is_active = False
        provider.status = ProviderStatus.SUSPENDED.value
        provider.rejection_reason = approval.rejection_reason
    
    db.commit()
    db.refresh(provider)
    
    return {
        "id": provider.id,
        "first_name": provider.first_name,
        "middle_name": provider.middle_name,
        "last_name": provider.last_name,
        "full_name": f"{provider.first_name} {provider.middle_name} {provider.last_name}",
        "email": provider.email,
        "phone_number": provider.phone_number,
        "address": provider.address,
        "status": provider.status,
        "is_active": provider.is_active,
        "is_verified": provider.is_verified,
        "approval_status": provider.approval_status,
        "approved_at": provider.approved_at.isoformat() if provider.approved_at else None,
        "rejection_reason": provider.rejection_reason,
        "business_name": provider.business_name,
        "message": f"Service provider {approval.approval_status}"
    }

@router.get("/stats/summary", response_model=dict)
def get_providers_summary(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_manager_user)
):
    """Get service providers summary statistics"""
    total_providers = db.query(ServiceProvider).count()
    active_providers = db.query(ServiceProvider).filter(ServiceProvider.is_active == True).count()
    verified_providers = db.query(ServiceProvider).filter(ServiceProvider.is_verified == True).count()
    busy_providers = db.query(ServiceProvider).filter(ServiceProvider.status == ProviderStatus.BUSY.value).count()
    
    return {
        "total_providers": total_providers,
        "active_providers": active_providers,
        "verified_providers": verified_providers,
        "busy_providers": busy_providers,
        "inactive_providers": total_providers - active_providers
    } 