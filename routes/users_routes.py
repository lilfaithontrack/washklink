from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from google.oauth2 import id_token
from google.auth.transport import requests
from database import SessionLocal
from models.users import DBUser
from schemas.users_schema import UserResponse
from utils.otp_service import generate_otp, send_otp_sms, otp_store

router = APIRouter(prefix="/users", tags=["Users"])

# Your Google OAuth 2.0 Client ID here
GOOGLE_CLIENT_ID = "1038087912249-85n553k9b73khia51v7doc6orsau9nov.apps.googleusercontent.com"


# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pydantic models for requests
class UserCreate(BaseModel):
    phone_number: str


class UserVerify(BaseModel):
    phone_number: str
    otp_code: str
    full_name: str = None
    email: EmailStr = None


class GoogleAuthRequest(BaseModel):
    id_token: str


# --- 1. Request OTP ---
@router.post("/request-otp")
def request_otp(data: UserCreate, db: Session = Depends(get_db)):
    otp = generate_otp()
    sent = send_otp_sms(data.phone_number, otp)

    if not sent:
        raise HTTPException(status_code=500, detail="Failed to send OTP")

    otp_store[data.phone_number] = otp
    return {"message": "OTP sent successfully"}


# --- 2. Google Auth ---
@router.post("/google-auth", response_model=UserResponse)
def google_auth(data: GoogleAuthRequest, db: Session = Depends(get_db)):
    try:
        # Verify token with Google
        info = id_token.verify_oauth2_token(
            data.id_token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    email = info.get("email")
    full_name = info.get("name")
    phone_number = None  # Usually not provided by Google

    if not email:
        raise HTTPException(status_code=400, detail="Email not found in token")

    # Check if user exists
    user = db.query(DBUser).filter(DBUser.email == email).first()
    if not user:
        # Create new user
        user = DBUser(full_name=full_name, email=email, phone_number=phone_number)
        db.add(user)
        db.commit()
        db.refresh(user)

    return user


# --- 3. Verify OTP ---
@router.post("/verify-otp", response_model=UserResponse)
def verify_otp(data: UserVerify, db: Session = Depends(get_db)):
    real_otp = otp_store.get(data.phone_number)
    if real_otp != data.otp_code:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    user = db.query(DBUser).filter(DBUser.phone_number == data.phone_number).first()

    if not user:
        user = DBUser(
            phone_number=data.phone_number,
            full_name=data.full_name or "",
            email=data.email or None
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Remove OTP after verification
    del otp_store[data.phone_number]

    return user
