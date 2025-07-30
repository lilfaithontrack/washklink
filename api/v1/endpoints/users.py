from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from api.deps import (
    get_current_active_user, get_admin_user, 
    get_manager_user, require_role
)
from schemas.users_schema import UserResponse, UserUpdate
from models.mongo_models import User, UserRole
from crud.mongo_user import user_mongo_crud

router = APIRouter(redirect_slashes=False)

@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    current_user: User = Depends(get_manager_user),  # Manager or Admin access
    role: UserRole = Query(None, description="Filter by user role"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all users (Manager/Admin only) with optional role filtering"""
    if role:
        users = await User.find(User.role == role).skip(skip).limit(limit).to_list()
    else:
        users = await User.find_all().skip(skip).limit(limit).to_list()
    
    return [UserResponse(
        id=str(user.id),
        full_name=user.full_name,
        phone=user.phone_number,
        email=user.email,
        role=user.role,
        is_active=user.is_active
    ) for user in users]

@router.get("/regular-users", response_model=List[UserResponse])
async def get_regular_users(
    current_user: User = Depends(get_manager_user)
):
    """Get all regular users (Manager/Admin only)"""
    users = await User.find(User.role == UserRole.USER).to_list()
    return [UserResponse(
        id=str(user.id),
        full_name=user.full_name,
        phone=user.phone_number,
        email=user.email,
        role=user.role,
        is_active=user.is_active
    ) for user in users]

@router.get("/admin-users", response_model=List[UserResponse])
async def get_admin_users(
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """Get all admin and manager users (Admin only)"""
    users = await User.find({"role": {"$in": [UserRole.ADMIN, UserRole.MANAGER]}}).to_list()
    return [UserResponse(
        id=str(user.id),
        full_name=user.full_name,
        phone=user.phone_number,
        email=user.email,
        role=user.role,
        is_active=user.is_active
    ) for user in users]

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get user by ID (users can only see their own profile, managers/admins can see any)"""
    user = await user_mongo_crud.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Regular users can only see their own profile
    if current_user.role == UserRole.USER and str(current_user.id) != user_id:
        raise HTTPException(
            status_code=403, 
            detail="You can only view your own profile"
        )
    
    return UserResponse(
        id=str(user.id),
        full_name=user.full_name,
        phone=user.phone_number,
        email=user.email,
        role=user.role,
        is_active=user.is_active
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user profile"""
    return UserResponse(
        id=str(current_user.id),
        full_name=current_user.full_name,
        phone=current_user.phone_number,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active
    )

@router.put("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: str,
    role_data: dict,
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """Update user role (Admin only)"""
    user = await user_mongo_crud.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_role = UserRole(role_data.get("new_role"))
    
    # Prevent admin from demoting themselves
    if str(current_user.id) == user_id and new_role != UserRole.ADMIN:
        raise HTTPException(
            status_code=400,
            detail="You cannot change your own admin role"
        )
    
    user.role = new_role
    await user.save()
    
    return UserResponse(
        id=str(user.id),
        full_name=user.full_name,
        phone=user.phone_number,
        email=user.email,
        role=user.role,
        is_active=user.is_active
    )

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """Delete user (Admin only)"""
    user = await user_mongo_crud.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent admin from deleting themselves
    if str(current_user.id) == user_id:
        raise HTTPException(
            status_code=400,
            detail="You cannot delete your own account"
        )
    
    await user_mongo_crud.delete(user_id)
    return {"message": "User deleted successfully"}