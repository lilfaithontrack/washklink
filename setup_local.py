#!/usr/bin/env python3
"""
Local Development Setup Script
This script sets up the local development environment with SQLite database.
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv

def setup_local_environment():
    """Set up local development environment"""
    
    # Set environment variable for SQLite
    os.environ["DATABASE_URL"] = "sqlite:///./washlink.db"
    
    print("Setting up local development environment...")
    print("Database URL: sqlite:///./washlink.db")
    
    try:
        # Create engine
        engine = create_engine("sqlite:///./washlink.db")
        
        with engine.connect() as conn:
            # Check if new_users table exists
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='new_users'"))
            table_exists = result.fetchone()
            
            if not table_exists:
                print("Creating new_users table...")
                # Create the table with all required columns
                conn.execute(text("""
                    CREATE TABLE new_users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        full_name VARCHAR(255) NOT NULL,
                        phone_number VARCHAR(20) UNIQUE NOT NULL,
                        email VARCHAR(255) UNIQUE,
                        password VARCHAR(255),
                        role VARCHAR(20) DEFAULT 'user' NOT NULL,
                        is_active BOOLEAN DEFAULT 1,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        last_login DATETIME
                    )
                """))
                conn.commit()
                print("✅ new_users table created successfully")
            else:
                print("✅ new_users table already exists")
                
                # Check if password column exists
                result = conn.execute(text("PRAGMA table_info(new_users)"))
                columns = [row[1] for row in result.fetchall()]
                
                if 'password' not in columns:
                    print("Adding password column to new_users table...")
                    conn.execute(text("ALTER TABLE new_users ADD COLUMN password VARCHAR(255)"))
                    conn.commit()
                    print("✅ Password column added successfully")
                else:
                    print("✅ Password column already exists")
            
            print("Local development environment setup completed!")
            
    except Exception as e:
        print(f"❌ Error setting up local environment: {e}")

if __name__ == "__main__":
    setup_local_environment() 