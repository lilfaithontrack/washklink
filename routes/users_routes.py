import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, validator
from google.oauth2 import id_token
from google.auth.transport import requests

from database import SessionLocal
from models.users import DBUser
from schemas.users_schema import UserResponse
from utils.otp_service import generate_otp
from utils.afromessage import send_otp as send_afro_otp

router = APIRouter(prefix="/users", tags=["Users"])

# Configuration
GOOGLE_CLIENT_ID = "1038087912249-85n553k9b73khia51v7doc6orsau9nov.apps.googleusercontent.com"
OTP_EXPIRATION_MINUTES = 5

# In-memory OTP store with expiration handling
otp_store: Dict[str, Dict[str, Any]] = {}

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models with validation
class UserCreate(BaseModel):
    phone_number: str
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        if not v.startswith('+'):
            raise ValueError("Phone number must start with country code (e.g., +1)")
        return v

class UserVerify(BaseModel):
    phone_number: str
    otp_code: str
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

class GoogleAuthRequest(BaseModel):
    id_token: str

class UserUpdate(BaseModel):
    phone_number: str
    otp_code: str
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

class OrgUpdate(BaseModel):
    phone_number: str
    otp_code: str
    org_code: str  # Can be string or JSON

    @validator('org_code')
    def validate_org_code(cls, v):
        try:
            json.loads(v)  # Try to parse if it's JSON
        except json.JSONDecodeError:
            pass  # It's a regular string
        return v

# Helper functions
def store_otp(phone_number: str, action: str = "authentication") -> str:
    """Generate and store OTP with expiration"""
    otp = generate_otp()
    expires_at = datetime.now() + timedelta(minutes=OTP_EXPIRATION_MINUTES)
    
    otp_store[phone_number] = {
        'otp': otp,
        'action': action,
        'created_at': datetime.now().isoformat(),
        'expires_at': expires_at.isoformat()
    }
    return otp

def verify_otp(phone_number: str, otp_code: str, action: str = None) -> bool:
    """Verify OTP with optional action check"""
    otp_entry = otp_store.get(phone_number)
    
    if not otp_entry:
        return False
    
    # Check expiration
    expires_at = datetime.fromisoformat(otp_entry['expires_at'])
    if datetime.now() > expires_at:
        otp_store.pop(phone_number, None)
        return False
    
    # Check action if specified
    if action and otp_entry.get('action') != action:
        return False
    
    # Check OTP code
    if otp_entry['otp'] != otp_code:
        return False
    
    return True

# 1. Request OTP
@router.post("/request-otp", status_code=status.HTTP_200_OK)
async def request_otp(data: UserCreate, db: Session = Depends(get_db)):
    otp = store_otp(data.phone_number)
    
    # Send OTP via SMS
    result = send_afro_otp(data.phone_number, otp)
    
    if not result.get("Result") == "true":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("ResponseMsg", "Failed to send OTP")
        )
    
    return {"message": "OTP sent successfully", "expires_in": f"{OTP_EXPIRATION_MINUTES} minutes"}

# 2. Google Authentication
@router.post("/google-auth", response_model=UserResponse)
async def google_auth(data: GoogleAuthRequest, db: Session = Depends(get_db)):
    try:
        info = id_token.verify_oauth2_token(
            data.id_token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )

    email = info.get("email")
    full_name = info.get("name")
    phone_number = None  # Usually not provided by Google

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not found in token"
        )

    # Check if user exists or create new
    user = db.query(DBUser).filter(DBUser.email == email).first()
    if not user:
        user = DBUser(
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            is_verified=True  # Google-authenticated users are considered verified
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user

# 3. Verify OTP
@router.post("/verify-otp", response_model=UserResponse)
async def verify_otp_endpoint(data: UserVerify, db: Session = Depends(get_db)):
    if not verify_otp(data.phone_number, data.otp_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )

    # Find or create user
    user = db.query(DBUser).filter(DBUser.phone_number == data.phone_number).first()
    
    if not user:
        user = DBUser(
            phone_number=data.phone_number,
            full_name=data.full_name or "",
            email=data.email or None,
            is_verified=True
        )
        db.add(user)
    else:
        # Update existing user if new info provided
        if data.full_name:
            user.full_name = data.full_name
        if data.email:
            user.email = data.email
        user.is_verified = True
    
    db.commit()
    db.refresh(user)

    # Clean up OTP
    otp_store.pop(data.phone_number, None)

    return user

# 4. Update Profile with OTP
@router.put("/update-profile", response_model=UserResponse)
async def update_profile(data: UserUpdate, db: Session = Depends(get_db)):
    if not verify_otp(data.phone_number, data.otp_code, "update_profile"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )

    user = db.query(DBUser).filter(DBUser.phone_number == data.phone_number).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update fields if provided
    if data.full_name:
        user.full_name = data.full_name
    if data.email:
        user.email = data.email

    db.commit()
    db.refresh(user)

    # Clean up OTP
    otp_store.pop(data.phone_number, None)

    return user

# 5. Update Organization Profile
@router.put("/org-profile", response_model=UserResponse)
async def send_org_profile_update(data: OrgUpdate, db: Session = Depends(get_db)):
    if not verify_otp(data.phone_number, data.otp_code, "org_update"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )

    user = db.query(DBUser).filter(DBUser.phone_number == data.phone_number).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Handle org code (string or JSON)
    try:
        org_data = json.loads(data.org_code) if isinstance(data.org_code, str) else data.org_code
    except json.JSONDecodeError:
        org_data = data.org_code  # Use as plain string if not JSON

    # Update organization info
    user.org_data = org_data if isinstance(org_data, dict) else {"code": org_data}
    db.commit()
    db.refresh(user)

    # Clean up OTP
    otp_store.pop(data.phone_number, None)

    return user
