from sqlalchemy.orm import Session
from database import SessionLocal
from crud.user import user_crud
from core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_admin(db: Session) -> None:
    """Create admin user if it doesn't exist"""
    try:
        # Check if admin exists
        admin = user_crud.get_by_email(db, email=settings.ADMIN_EMAIL)
        if not admin:
            logger.info("Creating admin user...")
            user_crud.create_admin(
                db=db,
                email=settings.ADMIN_EMAIL,
                password=settings.ADMIN_PASSWORD
            )
            logger.info("Admin user created successfully")
        else:
            logger.info("Admin user already exists")
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        raise

def main() -> None:
    """Main function"""
    logger.info("Creating admin user...")
    db = SessionLocal()
    try:
        init_admin(db)
    finally:
        db.close()

if __name__ == "__main__":
    main() 