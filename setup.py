#!/usr/bin/env python3
"""
Setup script for WashLink Backend
This script helps initialize the backend with proper configuration
"""

import os
import shutil
from pathlib import Path

def create_env_file():
    """Create .env file from env.example if it doesn't exist"""
    env_example = Path("env.example")
    env_file = Path(".env")
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from env.example")
        print("📝 Please review and update the .env file with your configuration")
    elif env_file.exists():
        print("✅ .env file already exists")
    else:
        print("❌ env.example not found")

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import pydantic
        print("✅ All required dependencies are installed")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Please run: pip install -r requirements.txt")

def main():
    print("🚀 WashLink Backend Setup")
    print("=" * 40)
    
    # Create .env file
    create_env_file()
    
    # Check dependencies
    check_dependencies()
    
    print("\n📋 Next steps:")
    print("1. Review and update the .env file if needed")
    print("2. Run the backend: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    print("3. Access the API docs at: http://localhost:8000/docs")
    print("4. Default admin credentials: admin@washlink.com / admin123")

if __name__ == "__main__":
    main() 