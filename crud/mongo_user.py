from typing import Optional, List
from models.mongo_models import User, UserRole
from schemas.users_schema import UserCreate, UserUpdate
from pydantic import BaseModel
from core.security import get_password_hash
import logging
from bson import ObjectId

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdminUserCreate(BaseModel):
    full_name: str
    phone_number: str
    email: str
    role: UserRole
    password: str

class UserMongoCRUD:
    async def get(self, id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            return await User.get(ObjectId(id))
        except Exception as e:
            logger.error(f"Error getting user by ID {id}: {str(e)}")
            return None

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            return await User.find_one(User.email == email)
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {str(e)}")
            return None

    async def get_by_phone(self, phone: str) -> Optional[User]:
        """Get user by phone number"""
        try:
            return await User.find_one(User.phone_number == phone)
        except Exception as e:
            logger.error(f"Error getting user by phone {phone}: {str(e)}")
            return None

    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get multiple users"""
        try:
            return await User.find_all().skip(skip).limit(limit).to_list()
        except Exception as e:
            logger.error(f"Error getting multiple users: {str(e)}")
            return []

    async def create(self, obj_in: UserCreate) -> Optional[User]:
        """Create new user"""
        try:
            # Check if user already exists
            existing_user = await self.get_by_email(obj_in.email)
            if existing_user:
                logger.error(f"User with email {obj_in.email} already exists")
                return None
            
            existing_phone = await self.get_by_phone(obj_in.phone)
            if existing_phone:
                logger.error(f"User with phone {obj_in.phone} already exists")
                return None

            # Create new user
            user_data = obj_in.dict()
            user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
            user_data["role"] = UserRole.USER
            
            user = User(**user_data)
            await user.insert()
            return user
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return None

    async def update(self, user_id: str, obj_in: UserUpdate) -> Optional[User]:
        """Update user"""
        try:
            user = await self.get(user_id)
            if not user:
                logger.error(f"User with ID {user_id} not found")
                return None
            
            update_data = obj_in.dict(exclude_unset=True)
            if "password" in update_data:
                update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
            
            for field, value in update_data.items():
                setattr(user, field, value)
            
            await user.save()
            return user
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            return None

    async def delete(self, user_id: str) -> bool:
        """Delete user"""
        try:
            user = await self.get(user_id)
            if not user:
                logger.error(f"User with ID {user_id} not found")
                return False
            
            await user.delete()
            return True
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            return False

    async def create_admin(self, email: str, password: str, full_name: str = "Admin User", phone_number: str = "+251911000000") -> Optional[User]:
        """Create admin user"""
        try:
            # Check if admin already exists
            existing_admin = await self.get_by_email(email)
            if existing_admin:
                logger.error(f"Admin with email {email} already exists")
                return None

            user = User(
                email=email,
                hashed_password=get_password_hash(password),
                is_active=True,
                role=UserRole.ADMIN,
                full_name=full_name,
                phone_number=phone_number
            )
            await user.insert()
            return user
        except Exception as e:
            logger.error(f"Error creating admin user: {str(e)}")
            return None

    async def get_admins(self) -> List[User]:
        """Get all admin users"""
        try:
            return await User.find(User.role == UserRole.ADMIN).to_list()
        except Exception as e:
            logger.error(f"Error getting admin users: {str(e)}")
            return []

    async def get_active_users(self) -> List[User]:
        """Get all active users"""
        try:
            return await User.find(User.is_active == True).to_list()
        except Exception as e:
            logger.error(f"Error getting active users: {str(e)}")
            return []

    async def search_users(self, query: str, limit: int = 10) -> List[User]:
        """Search users by name, email, or phone"""
        try:
            # MongoDB text search or regex search
            users = await User.find({
                "$or": [
                    {"full_name": {"$regex": query, "$options": "i"}},
                    {"email": {"$regex": query, "$options": "i"}},
                    {"phone_number": {"$regex": query, "$options": "i"}}
                ]
            }).limit(limit).to_list()
            return users
        except Exception as e:
            logger.error(f"Error searching users: {str(e)}")
            return []

    async def count_users(self) -> int:
        """Count total users"""
        try:
            return await User.count()
        except Exception as e:
            logger.error(f"Error counting users: {str(e)}")
            return 0

    async def count_active_users(self) -> int:
        """Count active users"""
        try:
            return await User.find(User.is_active == True).count()
        except Exception as e:
            logger.error(f"Error counting active users: {str(e)}")
            return 0

# Create instance
user_mongo_crud = UserMongoCRUD() 