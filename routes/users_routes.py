import time
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from google.oauth2 import id_token
from google.auth.transport import requests

from database import SessionLocal
from models.users import DBUser
from schemas.users_schema import UserResponse, UserUpdate
from utils.otp_service import generate_otp, otp_store
from utils.afromessage import send_otp as send_afro_otp  # Note: renamed here for clarity

router = APIRouter(prefix="/users", tags=["Users"])

# Google OAuth 2.0 Client ID
GOOGLE_CLIENT_ID = "1038087912249-85n553k9b73khia51v7doc6orsau9nov.apps.googleusercontent.com"

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models for request bodies
class UserCreate(BaseModel):
    phone_number: str

class UserVerify(BaseModel):
    phone_number: str
    otp_code: str
    full_name: str = None
    email: EmailStr = None

class GoogleAuthRequest(BaseModel):
    id_token: str

# 1. Request OTP
@router.post("/request-otp")
def request_otp(data: UserCreate, db: Session = Depends(get_db)):
    otp = generate_otp()

    # Pass both phone_number and otp here
    result = send_afro_otp(data.phone_number, otp)

    if result.get("Result") != "true":
        raise HTTPException(status_code=500, detail=result.get("ResponseMsg", "Failed to send OTP"))

    # Store OTP with metadata and expiry
    otp_store[data.phone_number] = json.dumps({
        "otp": otp,
        "action": "verify_login",
        "expires_at": time.time() + 300  # 5 minutes expiry
    })

    return {"message": "OTP sent successfully"}

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

# 3. Verify OTP
@router.post("/verify-otp", response_model=UserResponse)
def verify_otp(data: UserVerify, db: Session = Depends(get_db)):
    otp_entry_raw = otp_store.get(data.phone_number)

    if not otp_entry_raw:
        raise HTTPException(status_code=400, detail="OTP not found")

    try:
        otp_entry = json.loads(otp_entry_raw) if isinstance(otp_entry_raw, str) else otp_entry_raw
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Corrupted OTP format")

    if otp_entry.get("otp") != data.otp_code or otp_entry.get("expires_at", 0) < time.time():
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

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

# 4. Update Profile (Send OTP Verification)
@router.put("/send-otp", response_model=UserResponse)
def send_otp_profile_update(data: UserUpdate, db: Session = Depends(get_db)):
    otp_entry_raw = otp_store.get(data.phone_number)

    if not otp_entry_raw:
        raise HTTPException(status_code=400, detail="OTP not found")

    try:
        otp_entry = json.loads(otp_entry_raw) if isinstance(otp_entry_raw, str) else otp_entry_raw
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Corrupted OTP format")

    if (
        otp_entry.get("otp") != data.otp_code or
        otp_entry.get("action") != "update_profile" or
        otp_entry.get("expires_at", 0) < time.time()
    ):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    user = db.query(DBUser).filter(DBUser.phone_number == data.phone_number).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.full_name:
        user.full_name = data.full_name

    db.commit()
    db.refresh(user)

    otp_store.pop(data.phone_number, None)

    return user
