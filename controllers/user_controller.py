from sqlalchemy.orm import Session
from models.user import User
from datetime import datetime
from passlib.context import CryptContext
from fastapi import HTTPException, status

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hash a password for storing."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a stored password against a provided password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user_data):
    """Legacy function maintained for backward compatibility."""
    return register_user(db, user_data)

def register_user(db: Session, user_data):
    """Register a new user with secure password hashing."""
    # Check if user already exists
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email already registered"
        )
    
    # Hash the password
    hashed_password = get_password_hash(user_data.password)
    
    db_user = User(
        name=user_data.name,
        email=user_data.email,
        ccode=user_data.ccode,
        mobile=user_data.mobile,
        refercode=user_data.refercode,
        parentcode=user_data.parentcode,
        password=hashed_password,
        registartion_date=datetime.utcnow(),
        status=user_data.status if hasattr(user_data, "status") else 1,
        wallet=user_data.wallet if hasattr(user_data, "wallet") else 0,
        status_login=user_data.status_login
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def login_user(db: Session, email: str, password: str):
    """Authenticate a user and return the user object if successful."""
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid email or password"
        )
    return user
