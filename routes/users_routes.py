from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.users import DBUser
from schemas.users_schema import UserCreate, UserVerify, UserResponse
from utils.otp_service import generate_otp, send_otp_sms, otp_store

router = APIRouter(prefix="/users", tags=["Users"])

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- 1. Request OTP ---
@router.post("/request-otp")
def request_otp(data: UserCreate, db: Session = Depends(get_db)):
    otp = generate_otp()
    sent = send_otp_sms(data.phone_number, otp)

    if not sent:
        raise HTTPException(status_code=500, detail="Failed to send OTP")

    otp_store[data.phone_number] = otp
    return {"message": "OTP sent successfully"}


# --- 2. Google Auth (OTP Optional) ---
@router.post("/google-auth", response_model=UserResponse)
def google_auth(data: UserVerify, db: Session = Depends(get_db)):
    # You can add token verification here if needed

    user = db.query(DBUser).filter(DBUser.email == data.email).first()

    if not user:
        user = DBUser(
            full_name=data.full_name,
            email=data.email,
            phone_number=data.phone_number
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user  # <-- this was missing!


# --- 3. Verify OTP (Optional path) ---
@router.post("/verify-otp", response_model=UserResponse)
def verify_otp(data: UserVerify, db: Session = Depends(get_db)):
    real_otp = otp_store.get(data.phone_number)

    if real_otp != data.otp_code:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    user = db.query(DBUser).filter(DBUser.phone_number == data.phone_number).first()

    if not user:
        user = DBUser(
            phone_number=data.phone_number,
            full_name=data.full_name,
            email=data.email
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    del otp_store[data.phone]()_
