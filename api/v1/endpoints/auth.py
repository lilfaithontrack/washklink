from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from typing import Any
from pydantic import BaseModel
from api.deps import get_current_active_user
from services.auth_service import authenticate_user, authenticate_admin_user
from schemas.auth import AdminLogin
from schemas.user import UserResponse
from models.mongo_models import User
from utils.otp_service import generate_otp, send_otp_sms, save_otp, verify_otp as verify_otp_local, otp_store
from services.auth_service import verify_otp as verify_otp_afromessage
from core.security import get_password_hash
import logging
import uuid

import jwt
from datetime import datetime, timedelta
from core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(redirect_slashes=False)

# Pydantic models for OTP requests
class OTPRequest(BaseModel):
    phone_number: str

class OTPVerifyRequest(BaseModel):
    phone_number: str
    otp_code: str
    full_name: str = ""

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    response: Response = None,
) -> Any:
    try:
        user = await authenticate_user(form_data.username, form_data.password)
        if not user:
            logger.warning(f"Failed login attempt for user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email/phone or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        payload = {
            "user_id": str(user.id),
            "role": user.role,
            "is_active": user.is_active,
            "exp": datetime.utcnow() + timedelta(days=180)  # 6 months
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            secure=settings.COOKIE_SECURE,  # Use setting instead of hardcoded False
            samesite="none" if settings.COOKIE_SECURE else "lax",  # Use 'none' for cross-origin HTTPS
            max_age=60*60*24*180,  # 6 months
            path="/"
        )
        logger.info(f"Successful login for user: {user.email}")
        return {
            "message": "Login successful",
            "user": UserResponse(
                id=str(user.id),
                full_name=user.full_name,
                phone=user.phone_number,
                email=user.email,
                role=user.role,
                is_active=user.is_active
            )
        }
    except Exception as e:
        logger.error(f"Login error for user {form_data.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )

@router.post("/admin/login")
async def admin_login(admin_user: AdminLogin, response: Response = None) -> Any:
    try:
        logger.info(f"Admin login attempt for: {admin_user.email}")
        user = await authenticate_admin_user(admin_user)
        if not user:
            logger.warning(f"Failed admin login attempt for: {admin_user.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        payload = {
            "user_id": str(user.id),
            "role": user.role,
            "is_active": user.is_active,
            "exp": datetime.utcnow() + timedelta(days=180)  # 6 months
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            secure=settings.COOKIE_SECURE,  # Use setting instead of hardcoded False
            samesite="none" if settings.COOKIE_SECURE else "lax",  # Use 'none' for cross-origin HTTPS
            max_age=60*60*24*180,  # 6 months
            path="/"
        )
        logger.info(f"Successful admin login for: {user.email}")
        user_response = UserResponse(
            id=str(user.id),
            full_name=user.full_name,
            phone=user.phone_number,
            email=user.email,
            role=user.role,
            is_active=user.is_active
        )
        return {"message": "Login successful", "user": user_response}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin login error for {admin_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during admin login"
        )

@router.post("/logout")
def logout(request: Request, response: Response):
    response.delete_cookie(
        key="access_token",
        path="/",
        httponly=True,
        secure=settings.COOKIE_SECURE,  # Use setting instead of hardcoded False
        samesite="none" if settings.COOKIE_SECURE else "lax"
    )
    return {"message": "Logged out"}

@router.post("/request-otp")
async def request_otp(request_data: OTPRequest) -> Any:
    """Request OTP for phone number using AfroMessage Challenge API"""
    try:
        logger.info(f"📱 Requesting OTP for phone: {request_data.phone_number}")
        
        # Send OTP via SMS (AfroMessage generates its own OTP)
        sms_success = send_otp_sms(request_data.phone_number, "")  # Empty OTP since AfroMessage generates it
        logger.info(f"SMS send result: {sms_success}")
        
        if sms_success:
            logger.info(f"✅ OTP sent successfully to {request_data.phone_number} via AfroMessage")
            return {"message": "OTP sent successfully to your phone"}
        else:
            logger.error(f"❌ Failed to send OTP to {request_data.phone_number}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send OTP. Please try again."
            )
            
    except Exception as e:
        logger.error(f"Error requesting OTP for {request_data.phone_number}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP"
        )

@router.post("/verify-otp")
async def verify_otp_login(request_data: OTPVerifyRequest, response: Response = None) -> Any:
    """Verify OTP and login/register user"""
    
    try:
        # Log verification attempt
        logger.info(f"🔍 Verifying OTP: {request_data.otp_code} for phone: {request_data.phone_number}")
        
        # Verify OTP using AfroMessage API
        otp_valid = await verify_otp_afromessage(request_data.phone_number, request_data.otp_code)
        logger.info(f"AfroMessage OTP verification result: {otp_valid} for {request_data.phone_number}")
        
        if not otp_valid:
            logger.error(f"❌ Invalid or expired OTP: {request_data.otp_code} for {request_data.phone_number}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired OTP"
            )
        
        # Check if user exists
        user = await User.find_one(User.phone_number == request_data.phone_number)
        
        # If user doesn't exist, create new user
        if not user:
            if not request_data.full_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Full name is required for new user registration"
                )
            
            user = User(
                full_name=request_data.full_name,
                phone_number=request_data.phone_number,
                role="user",
                is_active=True
            )
            await user.save()
            logger.info(f"New user registered: {request_data.phone_number}")
        
        # Update last login
        user.last_login = datetime.utcnow()
        await user.save()
        
        # Generate JWT token - 6 months duration
        payload = {
            "user_id": str(user.id),
            "role": user.role,
            "is_active": user.is_active,
            "exp": datetime.utcnow() + timedelta(days=180)  # 6 months
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        # Set cookie - 6 months duration
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite="none" if settings.COOKIE_SECURE else "lax",
            max_age=60*60*24*180,  # 6 months
            path="/"
        )
        
        logger.info(f"Successful OTP login for user: {request_data.phone_number}")
        return {
            "message": "Login successful",
            "access_token": token,
            "token_type": "bearer",
            "user": UserResponse(
                id=str(user.id),
                full_name=user.full_name,
                phone=user.phone_number,
                email=user.email,
                role=user.role,
                is_active=user.is_active
            )
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying OTP for {request_data.phone_number}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during OTP verification"
        )

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)) -> Any:
    """Get current user profile"""
    return UserResponse(
        id=str(current_user.id),
        full_name=current_user.full_name,
        phone=current_user.phone_number,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active
    )

@router.get("/debug/otp-store")
def debug_otp_store():
    """Debug endpoint to check OTP store contents (remove in production)"""
    import time
    current_time = time.time()
    store_info = {}
    
    for phone, data in otp_store.items():
        time_since = current_time - data["timestamp"]
        store_info[phone] = {
            "otp": data["otp"],
            "age_seconds": round(time_since, 2),
            "expired": time_since > 300,
            "timestamp": data["timestamp"]
        }
    
    return {
        "current_time": current_time,
        "otp_expiry_seconds": 300,
        "store_contents": store_info,
        "total_entries": len(otp_store)
    }