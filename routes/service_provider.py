from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import controllers.service_provider as controller
from schemas.service_provider import ServiceProviderResponse, ServiceProviderCreate

router = APIRouter(prefix="/service-provider", tags=["Service Providers"])

@router.get("/all", response_model=list[ServiceProviderResponse])
def get_all(db: Session = Depends(get_db)):
    return controller.get_all_service_providers(db)

@router.get("/{service_provider_id}", response_model=ServiceProviderResponse)
def get_by_id(service_provider_id: int, db: Session = Depends(get_db)):
    return controller.get_service_provider_by_id(db, service_provider_id)

@router.post("/", response_model=ServiceProviderResponse)
def create(service_provider: ServiceProviderCreate, db: Session = Depends(get_db)):
    return controller.create_service_provider(db, service_provider)
