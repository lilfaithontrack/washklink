import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from google.oauth2 import id_token
from google.auth.transport import requests

from database import SessionLocal
from models.users import DBUser
from schemas.users_schema import UserResponse, UserUpdate
from utils.otp_service import generate_otp, otp_store
from utils.afromessage import send_otp as send_afro_otp

router = APIRouter(prefix="/users", tags=["Users"])

GOOGLE_CLIENT_ID = "1038087912249-85n553k9b73khia51v7doc6orsau9nov.apps.googleusercontent.com"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Schemas (adjusted for OTP usage)
class UserCreate(BaseModel):
    phone_number: str

class UserVerify(BaseModel):
    phone_number: str
    otp_code: str
    full_name: str | None = None
    email: EmailStr | None = None

class UserUpdate(BaseModel):
    phone_number: str
    otp_code: str
    full_name: str | None = None

class GoogleAuthRequest(BaseModel):
    id_token: str

# Helper function: store OTP as dict (not JSON string)
def store_otp(phone_number: str, otp: str, action: str, expiry_seconds: int = 300):
    otp_store[phone_number] = {
        "otp": otp,
        "action": action,
        "expires_at": time.time() + expiry_seconds
    }

# 1. Request OTP for login
@router.post("/request-otp")
def request_otp(data: UserCreate):
    otp = generate_otp()
    result = send_afro_otp(data.phone_number, otp)

    if result.get("Result") != "true":
        raise HTTPException(status_code=500, detail=result.get("ResponseMsg", "Failed to send OTP"))

    store_otp(data.phone_number, otp, "verify_login")

    return {"message": "OTP sent successfully"}

# 1b. Request OTP for profile update (new endpoint)
@router.post("/request-otp-profile-update")
def request_otp_profile_update(data: UserCreate):
    otp = generate_otp()
    result = send_afro_otp(data.phone_number, otp)

    if result.get("Result") != "true":
        raise HTTPException(status_code=500, detail=result.get("ResponseMsg", "Failed to send OTP"))

    store_otp(data.phone_number, otp, "update_profile")

    return {"message": "OTP for profile update sent successfully"}

# 2. Google Authentication
@router.post("/google-auth", response_model=UserResponse)
def google_auth(data: GoogleAuthRequest, db: Session = Depends(get_db)):
    try:
        info = id_token.verify_oauth2_token(
            data.id_token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    email = info.get("email")
    full_name = info.get("name")

    if not email:
        raise HTTPException(status_code=400, detail="Email not found in token")

    user = db.query(DBUser).filter(DBUser.email == email).first()
    if not user:
        user = DBUser(full_name=full_name, email=email, phone_number=None)
        db.add(user)
        db.commit()
        db.refresh(user)

    return user

# 3. Verify OTP (login)
@router.post("/verify-otp", response_model=UserResponse)
def verify_otp(data: UserVerify, db: Session = Depends(get_db)):
    otp_entry = otp_store.get(data.phone_number)

    if not otp_entry:
        raise HTTPException(status_code=400, detail="OTP not found")

    if otp_entry.get("otp") != data.otp_code:
        raise HTTPException(status_code=400, detail="Incorrect OTP")

    if otp_entry.get("action") != "verify_login":
        raise HTTPException(status_code=400, detail="OTP not valid for login")

    if otp_entry.get("expires_at", 0) < time.time():
        raise HTTPException(status_code=400, detail="OTP expired")

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

    otp_store.pop(data.phone_number, None)
    return user

# 4. Update Profile (Verify OTP and update)
@router.put("/send-otp", response_model=UserResponse)
def send_otp_profile_update(data: UserUpdate, db: Session = Depends(get_db)):
    otp_entry = otp_store.get(data.phone_number)

    if not otp_entry:
        raise HTTPException(status_code=400, detail="OTP not found")

    if otp_entry.get("otp") != data.otp_code:
        raise HTTPException(status_code=400, detail="Incorrect OTP")

    if otp_entry.get("action") != "update_profile":
        raise HTTPException(status_code=400, detail="OTP not valid for profile update")

    if otp_entry.get("expires_at", 0) < time.time():
        raise HTTPException(status_code=400, detail="OTP expired")

    user = db.query(DBUser).filter(DBUser.phone_number == data.phone_number).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.full_name:
        user.full_name = data.full_name

    db.commit()
    db.refresh(user)

    otp_store.pop(data.phone_number, None)

    return user
