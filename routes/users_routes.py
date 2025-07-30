import time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List 
from database import SessionLocal
from models.mongo_models import User
from schemas.users_schema import UserResponse, UserCreate, UserUpdate
from utils.afromessage import send_otp as send_afro_otp, verify_otp

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Legacy endpoints for backward compatibility
@router.post("/auth/request-otp")
def request_otp_legacy(user: UserCreate):
    """Legacy OTP request endpoint - redirects to new API"""
    response = send_afro_otp(user.phone_number)
    if response.get("ResponseCode") != "200":
        raise HTTPException(status_code=500, detail=response.get("ResponseMsg", "Failed to send OTP"))
    return {
        "message": "OTP sent successfully", 
        "note": "This is a legacy endpoint. Please use /api/v1/auth/request-otp for new implementations."
    }

class UserVerify(BaseModel):
    phone_number: str
    otp_code: str
    full_name: str
    email: EmailStr | None = None

@router.post("/auth/login", response_model=UserResponse)
def login_legacy(user: UserVerify, db: Session = Depends(get_db)):
    """Legacy login endpoint - basic functionality maintained"""
    # Step 1: Verify OTP using AfroMessage API
    if not verify_otp(user.phone_number, user.otp_code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP"
        )

    # Step 2: Find or create user
    db_user = db.query(User).filter(User.phone_number == user.phone_number).first()

    if not db_user:
        # Create as regular user (USER role)
        from app.db.models.user import UserRole
        db_user = User(
            full_name=user.full_name,
            phone_number=user.phone_number,
            email=None,  # Regular users don't have email
            role=UserRole.USER,
            is_active=True,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    else:
        updated = False
        if user.full_name != db_user.full_name:
            db_user.full_name = user.full_name
            updated = True
        # Don't update email for regular users
        if updated:
            db.commit()

    # Step 3: Return user response
    return UserResponse(
        id=db_user.id,
        full_name=db_user.full_name,
        phone_number=db_user.phone_number,
        email=db_user.email,
        is_active=db_user.is_active,
    )

@router.get("/users", response_model=List[UserResponse])
def get_all_users_legacy(db: Session = Depends(get_db)):
    """Legacy endpoint - basic functionality maintained"""
    users = db.query(User).all()
    return [
        UserResponse(
            id=user.id,
            full_name=user.full_name,
            phone_number=user.phone_number,
            email=user.email,
            is_active=user.is_active
        ) for user in users
    ]

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id_legacy(user_id: int, db: Session = Depends(get_db)):
    """Legacy endpoint - basic functionality maintained"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user.id,
        full_name=user.full_name,
        phone_number=user.phone_number,
        email=user.email,
        is_active=user.is_active
    )