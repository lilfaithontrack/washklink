from fastapi import HTTPException
from models.mongo_models import User, UserRole
from schemas.users_schema import UserCreate, UserUpdate, UserResponse
from typing import List, Optional
from bson import ObjectId
from core.security import get_password_hash, verify_password
import logging
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

async def create_user(user: UserCreate) -> User:
    """Create a new user"""
    try:
        # Check for duplicate email or phone
        existing = await User.find_one({
            "$or": [
                {"email": user.email},
                {"phone_number": user.phone_number}
            ]
        })

        if existing:
            raise HTTPException(status_code=400, detail="Email or phone number already registered")

        # Create new user
        db_user = User(
            full_name=user.full_name,
            phone_number=user.phone_number,
            email=user.email,
            hashed_password=get_password_hash(user.password) if user.password else None,
            role=user.role or UserRole.USER,
            is_active=True,
            created_at=datetime.utcnow()
        )

        await db_user.insert()
        return db_user

    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_user_by_id(user_id: str) -> Optional[User]:
    """Get user by ID"""
    try:
        user = await User.get(ObjectId(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    except Exception as e:
        logger.error(f"Error getting user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email"""
    try:
        return await User.find_one(User.email == email)

    except Exception as e:
        logger.error(f"Error getting user by email {email}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_user_by_phone(phone: str) -> Optional[User]:
    """Get user by phone number"""
    try:
        return await User.find_one(User.phone_number == phone)

    except Exception as e:
        logger.error(f"Error getting user by phone {phone}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None
) -> List[User]:
    """Get users with optional filtering"""
    try:
        query = {}
        if role:
            query["role"] = role
        if is_active is not None:
            query["is_active"] = is_active

        return await User.find(query).skip(skip).limit(limit).to_list()

    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def update_user(user_id: str, user_update: UserUpdate) -> User:
    """Update user details"""
    try:
        user = await User.get(ObjectId(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Update only provided fields
        update_data = user_update.dict(exclude_unset=True)
        
        # Handle password update
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = datetime.utcnow()
        await user.save()
        return user

    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def delete_user(user_id: str) -> bool:
    """Delete user"""
    try:
        user = await User.get(ObjectId(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        await user.delete()
        return True

    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def update_user_role(user_id: str, new_role: UserRole) -> User:
    """Update user role"""
    try:
        user = await User.get(ObjectId(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.role = new_role
        user.updated_at = datetime.utcnow()
        await user.save()
        return user

    except Exception as e:
        logger.error(f"Error updating user role {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def deactivate_user(user_id: str) -> User:
    """Deactivate user"""
    try:
        user = await User.get(ObjectId(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.is_active = False
        user.updated_at = datetime.utcnow()
        await user.save()
        return user

    except Exception as e:
        logger.error(f"Error deactivating user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def activate_user(user_id: str) -> User:
    """Activate user"""
    try:
        user = await User.get(ObjectId(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.is_active = True
        user.updated_at = datetime.utcnow()
        await user.save()
        return user

    except Exception as e:
        logger.error(f"Error activating user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def change_password(user_id: str, old_password: str, new_password: str) -> User:
    """Change user password"""
    try:
        user = await User.get(ObjectId(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_password(old_password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Incorrect password")

        user.hashed_password = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        await user.save()
        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def search_users(query: str, limit: int = 10) -> List[User]:
    """Search users by name, email, or phone"""
    try:
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
        raise HTTPException(status_code=500, detail="Internal server error")
