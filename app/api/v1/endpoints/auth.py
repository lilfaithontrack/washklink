from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.user import UserCreate, UserVerify, UserResponse
from app.services.auth_service import send_otp, authenticate_user

router = APIRouter()

@router.post("/request-otp")
def request_otp(user: UserCreate):
    """Request OTP for phone number verification"""
    response = send_otp(user.phone_number)
    if response.get("ResponseCode") != "200":
        raise HTTPException(
            status_code=500, 
            detail=response.get("ResponseMsg", "Failed to send OTP")
        )
    return {"message": "OTP sent successfully"}

@router.post("/login", response_model=UserResponse)
def login(user: UserVerify, db: Session = Depends(get_db)):
    """Login with OTP verification"""
    db_user = authenticate_user(db, user)
    return UserResponse(
        id=db_user.id,
        full_name=db_user.full_name,
        phone_number=db_user.phone_number,
        email=db_user.email,
        is_active=db_user.is_active,
    )