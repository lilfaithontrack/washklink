from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.db.models.driver import Driver
from app.schemas.driver import DriverCreate, DriverUpdate

class CRUDDriver(CRUDBase[Driver, DriverCreate, DriverUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[Driver]:
        return db.query(Driver).filter(Driver.email == email).first()

    def get_by_phone(self, db: Session, *, phone_number: str) -> Optional[Driver]:
        return db.query(Driver).filter(Driver.phone_number == phone_number).first()

    def get_by_license(self, db: Session, *, license_number: str) -> Optional[Driver]:
        return db.query(Driver).filter(Driver.license_number == license_number).first()

    def get_available_drivers(self, db: Session) -> list[Driver]:
        from app.db.models.driver import DriverStatus
        return db.query(Driver).filter(
            Driver.status == DriverStatus.AVAILABLE,
            Driver.is_active == True
        ).all()

driver = CRUDDriver(Driver)