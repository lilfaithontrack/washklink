from typing import Optional
from sqlalchemy.orm import Session
from crud.base import CRUDBase
from models.users import DBUser, UserRole
from schemas.users_schema import UserCreate, UserUpdate
from pydantic import BaseModel
from core.security import get_password_hash
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdminUserCreate(BaseModel):
    full_name: str
    phone_number: str
    email: str
    role: UserRole
    password: str

class UserCRUD:
    def get(self, db: Session, id: int) -> DBUser:
        """Get user by ID"""
        return db.query(DBUser).filter(DBUser.id == id).first()

    def get_by_email(self, db: Session, email: str) -> DBUser:
        """Get user by email"""
        return db.query(DBUser).filter(DBUser.email == email).first()

    def get_by_phone(self, db: Session, phone: str) -> DBUser:
        """Get user by phone number"""
        return db.query(DBUser).filter(DBUser.phone == phone).first()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100):
        """Get multiple users"""
        return db.query(DBUser).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: UserCreate) -> DBUser:
        """Create new user"""
        try:
            db_obj = DBUser(
                email=obj_in.email,
                phone=obj_in.phone,
                first_name=obj_in.first_name,
                last_name=obj_in.last_name,
                hashed_password=get_password_hash(obj_in.password),
                is_active=True,
                role="user"
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            db.rollback()
            raise

    def update(self, db: Session, *, db_obj: DBUser, obj_in: UserUpdate) -> DBUser:
        """Update user"""
        try:
            update_data = obj_in.dict(exclude_unset=True)
            if "password" in update_data:
                update_data["hashed_password"] = get_password_hash(update_data["password"])
                del update_data["password"]
            
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            db.rollback()
            raise

    def delete(self, db: Session, *, id: int) -> DBUser:
        """Delete user"""
        try:
            obj = db.query(DBUser).get(id)
            if obj:
                db.delete(obj)
                db.commit()
            return obj
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            db.rollback()
            raise

    def create_admin(self, db: Session, email: str, password: str) -> DBUser:
        """Create admin user"""
        try:
            db_obj = DBUser(
                email=email,
                hashed_password=get_password_hash(password),
                is_active=True,
                role="admin",
                first_name="Admin",
                last_name="User"
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            logger.error(f"Error creating admin user: {str(e)}")
            db.rollback()
            raise

user_crud = UserCRUD()