from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from api.deps import get_db, get_current_active_user
from schemas.users_schema import (
    UserCreate, UserVerify, UserResponse, UserRole
)
from services.auth_service import send_otp, authenticate_user, authenticate_admin_user, AdminUserLogin
from crud.user import user as user_crud, AdminUserCreate
from core.security import create_access_token, hash_password
from core.config import get_settings

router = APIRouter()
settings = get_settings()

class TokenResponse:
    def __init__(self, access_token: str, token_type: str, user: UserResponse, expires_in: int):
        self.access_token = access_token
        self.token_type = token_type
        self.user = user
        self.expires_in = expires_in

@router.post("/request-otp")
def request_otp(user: UserCreate):
    """Request OTP for phone number verification (regular users only)"""
    response = send_otp(user.phone_number)
    if response.get("ResponseCode") != "200":
        raise HTTPException(
            status_code=500, 
            detail=response.get("ResponseMsg", "Failed to send OTP")
        )
    return {"message": "OTP sent successfully"}

@router.post("/login")
def login(user: UserVerify, db: Session = Depends(get_db)):
    """Login with OTP verification (regular users only)"""
    db_user = authenticate_user(db, user)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(db_user.id), "role": db_user.role.value},
        expires_delta=access_token_expires
    )
    
    # Update last login
    db_user.last_login = datetime.utcnow()
    db.commit()
    
    user_response = UserResponse(
        id=db_user.id,
        full_name=db_user.full_name,
        phone_number=db_user.phone_number,
        email=db_user.email,
        is_active=db_user.is_active
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response,
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/admin/login")
def admin_login(admin_user: AdminUserLogin, db: Session = Depends(get_db)):
    """Login for admin and manager users with email and password"""
    db_user = authenticate_admin_user(db, admin_user)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(db_user.id), "role": db_user.role.value},
        expires_delta=access_token_expires
    )
    
    # Update last login
    db_user.last_login = datetime.utcnow()
    db.commit()
    
    user_response = UserResponse(
        id=db_user.id,
        full_name=db_user.full_name,
        phone_number=db_user.phone_number,
        email=db_user.email,
        is_active=db_user.is_active
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response,
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/admin/create")
def create_admin_user(
    admin_user: AdminUserCreate, 
    db: Session = Depends(get_db)
):
    """Create admin or manager user (requires existing admin privileges in production)"""
    
    # Check for existing users
    existing_email = user_crud.get_by_email(db, email=admin_user.email)
    if existing_email:
        raise HTTPException(
            status_code=400, 
            detail="Email already registered"
        )
    
    existing_phone = user_crud.get_by_phone(db, phone_number=admin_user.phone_number)
    if existing_phone:
        raise HTTPException(
            status_code=400, 
            detail="Phone number already registered"
        )
    
    # Validate role
    if admin_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(
            status_code=400,
            detail="Invalid role. Only ADMIN or MANAGER roles can be created through this endpoint"
        )
    
    # Create admin/manager user
    hashed_password = hash_password(admin_user.password)
    db_user = user_crud.create_admin_user(db, admin_user, hashed_password)
    
    return UserResponse(
        id=db_user.id,
        full_name=db_user.full_name,
        phone_number=db_user.phone_number,
        email=db_user.email,
        is_active=db_user.is_active
    )

@router.post("/logout")
def logout():
    """Logout endpoint (client should discard token)"""
    return {"message": "Successfully logged out"}

@router.get("/me")
def get_current_user_info(
    current_user = Depends(get_current_active_user)
):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        full_name=current_user.full_name,
        phone_number=current_user.phone_number,
        email=current_user.email,
        is_active=current_user.is_active
    )