import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get the database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Create SQLAlchemy engine with timeout-handling settings
engine = create_engine(
    DATABASE_URL,
    pool_recycle=280,      # Recycles old connections every 280 seconds
    pool_pre_ping=True     # Checks if connection is alive before using it
)

# Create a configured "SessionLocal" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the declarative base class
Base = declarative_base()

# Dependency for getting DB session in routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
