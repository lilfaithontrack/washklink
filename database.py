import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from core.config import settings

# Load environment variables from .env
load_dotenv()

# Create database URL from settings
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Create SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for declarative models
Base = declarative_base()

# Import all models here to ensure they are registered with SQLAlchemy
from db.models.driver import Driver
from db.models.order import Order
from db.models.service_provider import ServiceProvider
from db.models.notification import Notification
from db.models.payment import Payment
from models.users import DBUser

# Create all tables
def init_db():
    Base.metadata.create_all(bind=engine)

# Dependency for getting DB session in routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
