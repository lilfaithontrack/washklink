from fastapi import Depends, HTTPException, status, Request
from crud.mongo_user import user_mongo_crud
from models.mongo_models import User, UserRole
from core.security import verify_token
from typing import Optional
import uuid

async def get_current_user(request: Request) -> User:
    # Check for token in cookies first (web app), then Authorization header (mobile app)
    token = request.cookies.get('access_token')
    
    # If no cookie token, check Authorization header
    if not token:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')
    
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user = await user_mongo_crud.get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

def require_role(required_role: UserRole):
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        user_role = current_user.role
        if required_role == UserRole.ADMIN and user_role != UserRole.ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
        elif required_role == UserRole.MANAGER and user_role not in [UserRole.ADMIN, UserRole.MANAGER]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Manager or Admin access required")
        return current_user
    return role_checker

async def get_admin_user(current_user: User = Depends(require_role(UserRole.ADMIN))) -> User:
    return current_user

async def get_manager_user(current_user: User = Depends(require_role(UserRole.MANAGER))) -> User:
    return current_user

async def get_user_or_higher(current_user: User = Depends(get_current_active_user)) -> User:
    return current_user