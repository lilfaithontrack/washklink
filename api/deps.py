from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import SessionLocal
from core.security import verify_token
from crud.user import user as user_crud
from models.users import DBUser, UserRole

security = HTTPBearer()

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> DBUser:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = user_crud.get(db, id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

def get_current_active_user(
    current_user: DBUser = Depends(get_current_user),
) -> DBUser:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def require_role(required_role: UserRole):
    """Dependency factory for role-based access control"""
    def role_checker(current_user: DBUser = Depends(get_current_active_user)) -> DBUser:
        if required_role == UserRole.ADMIN and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        elif required_role == UserRole.MANAGER and not current_user.has_admin_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Manager or Admin access required"
            )
        return current_user
    return role_checker

def get_admin_user(current_user: DBUser = Depends(require_role(UserRole.ADMIN))) -> DBUser:
    """Get current user with admin role"""
    return current_user

def get_manager_user(current_user: DBUser = Depends(require_role(UserRole.MANAGER))) -> DBUser:
    """Get current user with manager or admin role"""
    return current_user

def get_user_or_higher(current_user: DBUser = Depends(get_current_active_user)) -> DBUser:
    """Get any authenticated user (USER, MANAGER, or ADMIN)"""
    return current_user