import httpx
import requests
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from jose import jwt
from core.config import settings
from core.security import verify_password
from crud.mongo_user import user_mongo_crud
from schemas.users_schema import UserCreate, UserVerify
from models.mongo_models import User, UserRole
from pydantic import BaseModel
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdminUserLogin(BaseModel):
    email: str
    password: str

async def send_otp(mobile: str) -> dict:
    """Send OTP to phone number using AfroMessage API"""
    if not mobile:
        return {
            "ResponseCode": "401",
            "Result": "false",
            "ResponseMsg": "Mobile number is required!"
        }

    params = {
        "from": settings.AFRO_MESSAGE_IDENTIFIER_ID,
        "sender": settings.AFRO_MESSAGE_SENDER_NAME,
        "to": mobile,
        "ps": "",
        "sb": settings.AFRO_MESSAGE_SB,
        "sa": settings.AFRO_MESSAGE_SA,
        "ttl": settings.AFRO_MESSAGE_TTL,
        "len": settings.AFRO_MESSAGE_LEN,
        "t": settings.AFRO_MESSAGE_T,
        "callback": settings.AFRO_MESSAGE_CALLBACK,
    }

    headers = {
        "Authorization": f"Bearer {settings.AFRO_MESSAGE_API_KEY}"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.AFRO_MESSAGE_BASE_URL}/challenge",
                headers=headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()

            try:
                data = response.json()
            except ValueError:
                return {
                    "ResponseCode": "500",
                    "Result": "false",
                    "ResponseMsg": "Invalid JSON response from OTP provider"
                }

            if data.get("acknowledge") == "success":
                return {
                    "ResponseCode": "200",
                    "Result": "true",
                    "ResponseMsg": "Check your message!"
                }
            else:
                return {
                    "ResponseCode": "200",
                    "Result": "false",
                    "ResponseMsg": "Please try again!"
                }

    except httpx.HTTPError as e:
        logger.error(f"OTP sending failed: {e}")
        return {
            "ResponseCode": "500",
            "Result": "false",
            "ResponseMsg": f"HTTP error occurred: {str(e)}"
        }

async def verify_otp(to: str, code: str) -> bool:
    """Verify OTP using AfroMessage API"""
    base_url = 'https://api.afromessage.com/api/verify'
    headers = {'Authorization': f'Bearer {settings.AFRO_MESSAGE_API_KEY}'}
    url = f'{base_url}?to={to}&code={code}'

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('acknowledge') == 'success':
                    return True
                else:
                    logger.warning(f"OTP verification failed: {data}")
                    return False
            else:
                logger.error(f"HTTP error verifying OTP: {response.status_code} {response.text}")
                return False
    except Exception as e:
        logger.error(f"Exception during OTP verification: {e}")
        return False

def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

async def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate a regular user"""
    try:
        user = await user_mongo_crud.get_by_email(email)
        if not user:
            logger.warning(f"User not found: {email}")
            return None
        
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Invalid password for user: {email}")
            return None
        
        if not user.is_active:
            logger.warning(f"Inactive user attempted login: {email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        return user
    except Exception as e:
        logger.error(f"Error in authenticate_user: {str(e)}")
        raise

async def authenticate_admin_user(admin_login: AdminUserLogin) -> Optional[User]:
    """Authenticate an admin user"""
    try:
        user = await user_mongo_crud.get_by_email(admin_login.email)
        if not user:
            logger.warning(f"Admin user not found: {admin_login.email}")
            return None

        if not verify_password(admin_login.password, user.hashed_password):
            logger.warning(f"Invalid password for admin: {admin_login.email}")
            return None

        if not user.is_active:
            logger.warning(f"Inactive admin attempted login: {admin_login.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )

        # Check if user has admin role
        if user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            logger.warning(f"Non-admin user attempted admin login: {admin_login.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have admin privileges"
            )

        return user
    except Exception as e:
        logger.error(f"Error in authenticate_admin_user: {str(e)}")
        raise