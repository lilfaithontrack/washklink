#!/usr/bin/env python3
"""
Database Schema Fix Script
This script fixes the database schema by adding required columns.
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv
import sqlite3
from datetime import datetime
import logging
from sqlalchemy import create_engine, text
from core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def fix_database_schema():
    """Fix the database schema by adding missing columns"""
    
    # Get database URL
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./washlink.db")
    
    print(f"Connecting to database: {DATABASE_URL}")
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Check if we're using SQLite or MySQL
            if DATABASE_URL.startswith("sqlite"):
                print("Using SQLite database")
                
                # Add columns to drivers table
                print("\nChecking drivers table...")
                result = conn.execute(text("PRAGMA table_info(drivers)"))
                columns = [row[1] for row in result.fetchall()]
                
                if 'approval_status' not in columns:
                    print("Adding approval columns to drivers table...")
                    conn.execute(text("ALTER TABLE drivers ADD COLUMN approval_status VARCHAR(20) DEFAULT 'PENDING'"))
                    conn.execute(text("ALTER TABLE drivers ADD COLUMN approved_at DATETIME"))
                    conn.execute(text("ALTER TABLE drivers ADD COLUMN approved_by INTEGER"))
                    conn.execute(text("ALTER TABLE drivers ADD COLUMN rejection_reason VARCHAR(500)"))
                    print("✅ Approval columns added to drivers table")
                else:
                    print("✅ Approval columns already exist in drivers table")
                
                # Add columns to service_provider table
                print("\nChecking service_provider table...")
                result = conn.execute(text("PRAGMA table_info(service_provider)"))
                columns = [row[1] for row in result.fetchall()]
                
                if 'approval_status' not in columns:
                    print("Adding approval columns to service_provider table...")
                    conn.execute(text("ALTER TABLE service_provider ADD COLUMN approval_status VARCHAR(20) DEFAULT 'PENDING'"))
                    conn.execute(text("ALTER TABLE service_provider ADD COLUMN approved_at DATETIME"))
                    conn.execute(text("ALTER TABLE service_provider ADD COLUMN approved_by INTEGER"))
                    conn.execute(text("ALTER TABLE service_provider ADD COLUMN rejection_reason VARCHAR(500)"))
                    print("✅ Approval columns added to service_provider table")
                else:
                    print("✅ Approval columns already exist in service_provider table")
                    
            else:
                print("Using MySQL database")
                
                # Add columns to drivers table
                print("\nChecking drivers table...")
                result = conn.execute(text("SHOW COLUMNS FROM drivers LIKE 'approval_status'"))
                if not result.fetchone():
                    print("Adding approval columns to drivers table...")
                    conn.execute(text("""
                        ALTER TABLE drivers 
                        ADD COLUMN approval_status VARCHAR(20) DEFAULT 'PENDING',
                        ADD COLUMN approved_at DATETIME,
                        ADD COLUMN approved_by INTEGER,
                        ADD COLUMN rejection_reason VARCHAR(500)
                    """))
                    print("✅ Approval columns added to drivers table")
                else:
                    print("✅ Approval columns already exist in drivers table")
                
                # Add columns to service_provider table
                print("\nChecking service_provider table...")
                result = conn.execute(text("SHOW COLUMNS FROM service_provider LIKE 'approval_status'"))
                if not result.fetchone():
                    print("Adding approval columns to service_provider table...")
                    conn.execute(text("""
                        ALTER TABLE service_provider 
                        ADD COLUMN approval_status VARCHAR(20) DEFAULT 'PENDING',
                        ADD COLUMN approved_at DATETIME,
                        ADD COLUMN approved_by INTEGER,
                        ADD COLUMN rejection_reason VARCHAR(500)
                    """))
                    print("✅ Approval columns added to service_provider table")
                else:
                    print("✅ Approval columns already exist in service_provider table")
            
            conn.commit()
            print("\nDatabase schema fix completed!")
            
    except OperationalError as e:
        print(f"❌ Database connection error: {e}")
        print("Please check your DATABASE_URL in the .env file")
    except Exception as e:
        print(f"❌ Error fixing database schema: {e}")

def safe_alter(connection, statement):
    try:
        connection.execute(text(statement))
        logger.info(f"Executed: {statement}")
    except Exception as e:
        if "Duplicate column name" in str(e) or "already exists" in str(e):
            logger.info(f"Column already exists, skipping: {statement}")
        else:
            logger.error(f"Error executing: {statement}\n{e}")

def fix_database():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as connection:
        # Add columns one by one, ignore if already exists
        safe_alter(connection, "ALTER TABLE new_users ADD COLUMN phone VARCHAR(255) NULL;")
        safe_alter(connection, "ALTER TABLE new_users ADD COLUMN first_name VARCHAR(255) NULL;")
        safe_alter(connection, "ALTER TABLE new_users ADD COLUMN last_name VARCHAR(255) NULL;")
        safe_alter(connection, "ALTER TABLE new_users ADD COLUMN hashed_password VARCHAR(255) NULL;")
        safe_alter(connection, "ALTER TABLE new_users ADD COLUMN role VARCHAR(50) DEFAULT 'user';")
        safe_alter(connection, "ALTER TABLE new_users ADD COLUMN is_active BOOLEAN DEFAULT TRUE;")
        safe_alter(connection, "ALTER TABLE new_users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")
        safe_alter(connection, "ALTER TABLE new_users ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;")
        logger.info("All user columns checked/added.")

if __name__ == "__main__":
    fix_database() 