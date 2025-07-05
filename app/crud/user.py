from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.db.models.user import DBUser
from app.schemas.user import UserCreate, UserUpdate

class CRUDUser(CRUDBase[DBUser, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[DBUser]:
        return db.query(DBUser).filter(DBUser.email == email).first()

    def get_by_phone(self, db: Session, *, phone_number: str) -> Optional[DBUser]:
        return db.query(DBUser).filter(DBUser.phone_number == phone_number).first()

    def create_user(self, db: Session, *, user_in: UserCreate) -> DBUser:
        db_user = DBUser(
            full_name=user_in.full_name,
            phone_number=user_in.phone_number,
            is_active=True
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

user = CRUDUser(DBUser)