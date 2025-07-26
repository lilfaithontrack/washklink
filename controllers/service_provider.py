from sqlalchemy.orm import Session
from fastapi import HTTPException
from db.models.service_provider import ServiceProvider
from schemas.service_provider import ServiceProviderCreate
from utils.hashing import hash_password

def create_service_provider(db: Session, service_provider: ServiceProviderCreate):
    # Check for duplicate email or phone
    existing = db.query(ServiceProvider).filter(
        (ServiceProvider.email == service_provider.email) |
        (ServiceProvider.phone_number == service_provider.phone_number)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Phone or email already registered")

    # Create new service provider
    db_service_provider = ServiceProvider(
        first_name=service_provider.first_name,
        middle_name=service_provider.middle_name,
        last_name=service_provider.last_name,
        email=service_provider.email,
        address=service_provider.address,
        nearby_condominum =service_provider. nearby_condominum ,
        longitude=service_provider.longitude,
        latitude=service_provider.latitude,
        phone_number=service_provider.phone_number,
        washing_machine=service_provider.washing_machine,
        date_of_birth=service_provider.date_of_birth
        
    )

    db.add(db_service_provider)
    db.commit()
    db.refresh(db_service_provider)
    return db_service_provider

def get_all_service_providers(db:Session):
    return db.query (ServiceProvider).all()
def get_service_provider_by_id(db:Session , service_provider_id: int):
    service_provider = db.query(ServiceProvider).filter (ServiceProvider.id == service_provider_id).first()
    if not service_provider:
        raise HTTPException ( status_code= 401 , detail="service provider not found ")
    return service_provider
