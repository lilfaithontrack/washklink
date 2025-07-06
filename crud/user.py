from typing import Optional
from sqlalchemy.orm import Session
from crud.base import CRUDBase
from models.users import DBUser, UserRole
from schemas.users_schema import UserCreate, UserUpdate

class AdminUserCreate:
    def __init__(self, full_name: str, phone_number: str, email: str, role: UserRole, password: str):
        self.full_name = full_name
        self.phone_number = phone_number
        self.email = email
        self.role = role
        self.password = password

class CRUDUser(CRUDBase[DBUser, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[DBUser]:
        return db.query(DBUser).filter(DBUser.email == email).first()

    def get_by_phone(self, db: Session, *, phone_number: str) -> Optional[DBUser]:
        return db.query(DBUser).filter(DBUser.phone_number == phone_number).first()

    def create_user(self, db: Session, *, user_in: UserCreate) -> DBUser:
        """Create regular user (USER role, phone-only)"""
        db_user = DBUser(
            full_name=user_in.full_name,
            phone_number=user_in.phone_number,
            role=UserRole.USER,
            is_active=True
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def create_admin_user(
        self, 
        db: Session, 
        admin_user: AdminUserCreate, 
        hashed_password: str
    ) -> DBUser:
        """Create admin or manager user (with email and password)"""
        db_user = DBUser(
            full_name=admin_user.full_name,
            phone_number=admin_user.phone_number,
            email=admin_user.email,
            role=admin_user.role,
            password=hashed_password,
            is_active=True
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def get_users_by_role(self, db: Session, *, role: UserRole) -> list[DBUser]:
        """Get all users with specific role"""
        return db.query(DBUser).filter(DBUser.role == role).all()

    def get_admin_users(self, db: Session) -> list[DBUser]:
        """Get all admin and manager users"""
        return db.query(DBUser).filter(
            DBUser.role.in_([UserRole.ADMIN, UserRole.MANAGER])
        ).all()

    def get_regular_users(self, db: Session) -> list[DBUser]:
        """Get all regular users"""
        return db.query(DBUser).filter(DBUser.role == UserRole.USER).all()

    def update_user_role(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        new_role: UserRole
    ) -> Optional[DBUser]:
        """Update user role"""
        user = self.get(db, id=user_id)
        if user:
            user.role = new_role
            db.commit()
            db.refresh(user)
        return user

user = CRUDUser(DBUser)