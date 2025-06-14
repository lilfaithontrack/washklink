import time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from database import SessionLocal
from models.users import DBUser
from schemas.users_schema import UserResponse, UserCreate, UserVerify, UserUpdate
from utils.afromessage import send_otp as send_afro_otp, verify_otp  # You must implement verify_otp

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/auth/request-otp")
def request_otp(user: UserCreate):
    response = send_afro_otp(user.phone_number)
    if response.get("ResponseCode") != "200":
        raise HTTPException(status_code=500, detail=response.get("ResponseMsg", "Failed to send OTP"))
    return {"message": "OTP sent successfully"}

@router.post("/auth/login", response_model=UserResponse)
def login(user: UserVerify, db: Session = Depends(get_db)):
    phone = user.phone_number
    otp_code = user.otp_code

    if not verify_otp(phone, otp_code):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid OTP")

    db_user = db.query(DBUser).filter(DBUser.phone_number == phone).first()

    if not db_user:
        db_user = DBUser(
            full_name=user.full_name,
            phone_number=phone,
            email=user.email,
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
        if user.email and user.email != db_user.email:
            db_user.email = user.email
            updated = True
        if updated:
            db.commit()

    return UserResponse(
        id=db_user.id,
        full_name=db_user.full_name,
        phone_number=db_user.phone_number,
        email=db_user.email,
        is_active=db_user.is_active,
    )
