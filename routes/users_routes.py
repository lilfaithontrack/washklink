import time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from database import SessionLocal
from models.users import DBUser
from schemas.users_schema import UserResponse, UserCreate, UserUpdate
from utils.afromessage import send_otp as send_afro_otp, verify_otp

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

class UserVerify(BaseModel):
    phone_number: str
    otp_code: str
    full_name: str
    email: EmailStr | None = None

@router.post("/auth/login", response_model=UserResponse)
def login(user: UserVerify, db: Session = Depends(get_db)):
    # Step 1: Verify OTP using AfroMessage API
    if not verify_otp(user.phone_number, user.otp_code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP"
        )

    # Step 2: Find or create user
    db_user = db.query(DBUser).filter(DBUser.phone_number == user.phone_number).first()

    if not db_user:
        db_user = DBUser(
            full_name=user.full_name,
            phone_number=user.phone_number,
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

    # Step 3: Return user response
    return UserResponse(
        id=db_user.id,
        full_name=db_user.full_name,
        phone_number=db_user.phone_number,
        email=db_user.email,
        is_active=db_user.is_active,
    )
