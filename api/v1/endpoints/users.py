from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from api.deps import (
    get_db, get_current_active_user, get_admin_user, 
    get_manager_user, require_role
)
from schemas.users_schema import UserResponse, UserUpdate, UserRole
from crud.user import user as user_crud
from models.users import DBUser

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_manager_user),  # Manager or Admin access
    role: UserRole = Query(None, description="Filter by user role"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all users (Manager/Admin only) with optional role filtering"""
    if role:
        users = user_crud.get_users_by_role(db, role=role)
    else:
        users = user_crud.get_multi(db, skip=skip, limit=limit)
    
    return [UserResponse(
        id=user.id,
        full_name=user.full_name,
        phone_number=user.phone_number,
        email=user.email,
        is_active=user.is_active
    ) for user in users]

@router.get("/regular-users", response_model=List[UserResponse])
def get_regular_users(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_manager_user)
):
    """Get all regular users (Manager/Admin only)"""
    users = user_crud.get_regular_users(db)
    return [UserResponse(
        id=user.id,
        full_name=user.full_name,
        phone_number=user.phone_number,
        email=user.email,
        is_active=user.is_active
    ) for user in users]

@router.get("/admin-users", response_model=List[UserResponse])
def get_admin_users(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_admin_user)  # Admin only
):
    """Get all admin and manager users (Admin only)"""
    users = user_crud.get_admin_users(db)
    return [UserResponse(
        id=user.id,
        full_name=user.full_name,
        phone_number=user.phone_number,
        email=user.email,
        is_active=user.is_active
    ) for user in users]

@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Get user by ID (users can only see their own profile, managers/admins can see any)"""
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Regular users can only see their own profile
    if current_user.role == UserRole.USER and current_user.id != user_id:
        raise HTTPException(
            status_code=403, 
            detail="You can only view your own profile"
        )
    
    return UserResponse(
        id=user.id,
        full_name=user.full_name,
        phone_number=user.phone_number,
        email=user.email,
        is_active=user.is_active
    )

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: DBUser = Depends(get_current_active_user)
):
    """Get current user profile"""
    return UserResponse(
        id=current_user.id,
        full_name=current_user.full_name,
        phone_number=current_user.phone_number,
        email=current_user.email,
        is_active=current_user.is_active
    )

@router.put("/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    new_role: UserRole,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_admin_user)  # Admin only
):
    """Update user role (Admin only)"""
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent admin from demoting themselves
    if current_user.id == user_id and new_role != UserRole.ADMIN:
        raise HTTPException(
            status_code=400,
            detail="You cannot change your own admin role"
        )
    
    updated_user = user_crud.update_user_role(db, user_id=user_id, new_role=new_role)
    return UserResponse(
        id=updated_user.id,
        full_name=updated_user.full_name,
        phone_number=updated_user.phone_number,
        email=updated_user.email,
        is_active=updated_user.is_active
    )

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_admin_user)  # Admin only
):
    """Delete user (Admin only)"""
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent admin from deleting themselves
    if current_user.id == user_id:
        raise HTTPException(
            status_code=400,
            detail="You cannot delete your own account"
        )
    
    user_crud.remove(db, id=user_id)
    return {"message": "User deleted successfully"}