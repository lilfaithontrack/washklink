from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.laundry_provider import ServiceProviderResponse, ServiceProviderCreate
from app.crud.laundry_provider import service_provider as service_provider_crud

router = APIRouter()

@router.get("/", response_model=List[ServiceProviderResponse])
def get_all_service_providers(db: Session = Depends(get_db)):
    """Get all service providers"""
    return service_provider_crud.get_multi(db)

@router.get("/{provider_id}", response_model=ServiceProviderResponse)
def get_service_provider(provider_id: int, db: Session = Depends(get_db)):
    """Get service provider by ID"""
    provider = service_provider_crud.get(db, id=provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Service provider not found")
    return provider

@router.post("/", response_model=ServiceProviderResponse)
def create_service_provider(
    provider: ServiceProviderCreate,
    db: Session = Depends(get_db)
):
    """Create new service provider"""
    # Check for duplicates
    existing_email = service_provider_crud.get_by_email(db, email=provider.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    existing_phone = service_provider_crud.get_by_phone(db, phone_number=provider.phone_number)
    if existing_phone:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    return service_provider_crud.create(db, obj_in=provider)