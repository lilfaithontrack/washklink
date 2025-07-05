import httpx
import requests
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.core.config import get_settings
from app.core.security import verify_password
from app.crud.user import user as user_crud
from app.schemas.user import UserCreate, UserVerify, AdminUserLogin, UserRole
from app.db.models.user import DBUser
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

def send_otp(mobile: str) -> dict:
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
        response = httpx.get(
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

def verify_otp(to: str, code: str) -> bool:
    """Verify OTP using AfroMessage API"""
    base_url = 'https://api.afromessage.com/api/verify'
    headers = {'Authorization': f'Bearer {settings.AFRO_MESSAGE_API_KEY}'}
    url = f'{base_url}?to={to}&code={code}'

    try:
        response = requests.get(url, headers=headers, timeout=10)
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

def authenticate_user(db: Session, user_verify: UserVerify) -> DBUser:
    """Authenticate regular user with OTP"""
    # Step 1: Verify OTP
    if not verify_otp(user_verify.phone_number, user_verify.otp_code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP"
        )

    # Step 2: Find or create user
    db_user = user_crud.get_by_phone(db, phone_number=user_verify.phone_number)

    if not db_user:
        user_create = UserCreate(
            full_name=user_verify.full_name,
            phone_number=user_verify.phone_number
        )
        db_user = user_crud.create_user(db, user_in=user_create)
    else:
        # Update existing user if needed
        if user_verify.full_name != db_user.full_name:
            db_user.full_name = user_verify.full_name
            db.commit()

    # Ensure user has USER role
    if db_user.role != UserRole.USER:
        db_user.role = UserRole.USER
        db.commit()

    return db_user

def authenticate_admin_user(db: Session, admin_login: AdminUserLogin) -> DBUser:
    """Authenticate admin/manager user with email and password"""
    # Find user by email
    db_user = user_crud.get_by_email(db, email=admin_login.email)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is admin or manager
    if db_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin or Manager role required."
        )
    
    # Verify password (admin/manager users should have password set)
    if not db_user.password or not verify_password(admin_login.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    return db_user