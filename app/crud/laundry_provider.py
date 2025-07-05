from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.db.models.laundry_provider import ServiceProvider
from app.schemas.laundry_provider import ServiceProviderCreate, ServiceProviderResponse

class CRUDServiceProvider(CRUDBase[ServiceProvider, ServiceProviderCreate, ServiceProviderResponse]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[ServiceProvider]:
        return db.query(ServiceProvider).filter(ServiceProvider.email == email).first()

    def get_by_phone(self, db: Session, *, phone_number: int) -> Optional[ServiceProvider]:
        return db.query(ServiceProvider).filter(ServiceProvider.phone_number == phone_number).first()

service_provider = CRUDServiceProvider(ServiceProvider)