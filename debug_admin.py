from sqlalchemy.orm import Session
from database import SessionLocal
from crud.user import user_crud
from core.security import verify_password, get_password_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_admin():
    """Debug admin user authentication"""
    db = SessionLocal()
    try:
        # Check if admin exists
        admin_email = "admin@washlink.com"
        admin = user_crud.get_by_email(db, email=admin_email)
        
        if not admin:
            logger.error(f"Admin user not found with email: {admin_email}")
            return
        
        # Print admin details
        logger.info(f"Admin user found:")
        logger.info(f"ID: {admin.id}")
        logger.info(f"Email: {admin.email}")
        logger.info(f"Role: {admin.role}")
        logger.info(f"Is Active: {admin.is_active}")
        logger.info(f"Has password hash: {'Yes' if admin.hashed_password else 'No'}")
        
        # Test password verification
        test_password = "admin123"
        if admin.hashed_password:
            is_valid = verify_password(test_password, admin.hashed_password)
            logger.info(f"Password 'admin123' verification result: {is_valid}")
            
            # Generate new hash for comparison
            new_hash = get_password_hash(test_password)
            logger.info(f"New hash for 'admin123': {new_hash}")
            logger.info(f"Existing hash: {admin.hashed_password}")
        else:
            logger.error("No password hash found for admin user")
            
            # Generate new hash
            new_hash = get_password_hash(test_password)
            logger.info(f"Generated new hash for 'admin123': {new_hash}")
            
            # Update admin password
            admin.hashed_password = new_hash
            db.commit()
            logger.info("Updated admin password with new hash")
    
    finally:
        db.close()

if __name__ == "__main__":
    debug_admin() 