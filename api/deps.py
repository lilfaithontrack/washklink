from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from database import SessionLocal
from crud.user import user_crud
from models.users import DBUser, UserRole
from core.security import verify_token
import uuid


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(request: Request, db: Session = Depends(get_db)) -> DBUser:
    token = request.cookies.get('access_token')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = user_crud.get(db, id=int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def get_current_active_user(current_user: DBUser = Depends(get_current_user)) -> DBUser:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


def require_role(required_role: UserRole):
    def role_checker(current_user: DBUser = Depends(get_current_active_user)) -> DBUser:
        user_role = current_user.role.lower() if current_user.role else ''
        if required_role == UserRole.ADMIN and user_role != UserRole.ADMIN.value.lower():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
        elif required_role == UserRole.MANAGER and user_role not in [UserRole.ADMIN.value.lower(), UserRole.MANAGER.value.lower()]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Manager or Admin access required")
        return current_user
    return role_checker

def get_admin_user(current_user: DBUser = Depends(require_role(UserRole.ADMIN))) -> DBUser:
    return current_user

def get_manager_user(current_user: DBUser = Depends(require_role(UserRole.MANAGER))) -> DBUser:
    return current_user

def get_user_or_higher(current_user: DBUser = Depends(get_current_active_user)) -> DBUser:
    return current_user