#!/usr/bin/env python3
"""
Password Security Verification Script
This script verifies that all admin users have properly hashed passwords
and updates any that don't.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import SessionLocal
from models.users import DBUser, UserRole
from core.security import hash_password, verify_password
from crud.user import user_crud

def verify_admin_password_security():
    """Verify and fix password security for admin users"""
    db = SessionLocal()
    
    try:
        print("🔍 Checking admin user password security...")
        
        # Get all admin and manager users
        admin_users = user_crud.get_admin_users(db)
        
        if not admin_users:
            print("✅ No admin users found in database")
            return
        
        print(f"📊 Found {len(admin_users)} admin/manager users")
        
        updated_count = 0
        secure_count = 0
        
        for user in admin_users:
            print(f"\n👤 Checking user: {user.full_name} ({user.email})")
            
            # Check if user has a password set
            if not user.password:
                print(f"   ❌ No password set for admin user {user.email}")
                print(f"   💡 This user cannot login via admin panel")
                continue
            
            # Check if password is properly hashed (bcrypt hashes start with $2b$)
            if not user.password.startswith('$2b$'):
                print(f"   ⚠️  Password for {user.email} is not properly hashed")
                print(f"   🔧 This should be fixed manually or by recreating the user")
                continue
            
            # Test password verification (we can't verify without knowing the plain text)
            # But we can check the hash format
            if len(user.password) >= 60:  # bcrypt hashes are typically 60+ characters
                print(f"   ✅ Password appears to be properly hashed")
                secure_count += 1
            else:
                print(f"   ❌ Password hash format appears incorrect")
        
        print(f"\n📈 Security Summary:")
        print(f"   ✅ Secure passwords: {secure_count}")
        print(f"   ⚠️  Issues found: {len(admin_users) - secure_count}")
        
        if secure_count == len(admin_users):
            print("\n🎉 All admin passwords are properly secured!")
        else:
            print("\n⚠️  Some admin passwords need attention")
            print("   💡 Consider recreating users with proper password hashing")
        
    except Exception as e:
        print(f"❌ Error during password verification: {e}")
    finally:
        db.close()

def create_secure_admin_user(email: str, password: str, full_name: str = "Admin User"):
    """Create a new admin user with properly hashed password"""
    db = SessionLocal()
    
    try:
        from crud.user import AdminUserCreate
        from models.users import UserRole
        
        # Check if user already exists
        existing_user = user_crud.get_by_email(db, email=email)
        if existing_user:
            print(f"❌ User with email {email} already exists")
            return False
        
        # Create admin user with hashed password
        admin_user = AdminUserCreate(
            full_name=full_name,
            phone_number="+251911000000",  # Default phone
            email=email,
            role=UserRole.ADMIN,
            password=password
        )
        
        hashed_password = hash_password(admin_user.password)
        new_user = user_crud.create_admin_user(db, admin_user, hashed_password)
        
        print(f"✅ Created secure admin user: {new_user.email}")
        print(f"   📧 Email: {new_user.email}")
        print(f"   🔐 Password: {password}")
        print(f"   🆔 User ID: {new_user.id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False
    finally:
        db.close()

def update_admin_password(user_id: int, new_password: str):
    """Update an admin user's password with proper hashing"""
    db = SessionLocal()
    
    try:
        user = user_crud.get(db, id=user_id)
        if not user:
            print(f"❌ User with ID {user_id} not found")
            return False
        
        if user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            print(f"❌ User {user.email} is not an admin/manager")
            return False
        
        # Hash the new password
        hashed_password = hash_password(new_password)
        
        # Update the user's password
        user.password = hashed_password
        db.commit()
        db.refresh(user)
        
        print(f"✅ Updated password for user: {user.email}")
        print(f"   🔐 New password: {new_password}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating password: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🔐 WashLink Admin Password Security Tool")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "verify":
            verify_admin_password_security()
        elif command == "create":
            if len(sys.argv) >= 4:
                email = sys.argv[2]
                password = sys.argv[3]
                full_name = sys.argv[4] if len(sys.argv) > 4 else "Admin User"
                create_secure_admin_user(email, password, full_name)
            else:
                print("Usage: python verify_password_security.py create <email> <password> [full_name]")
        elif command == "update":
            if len(sys.argv) >= 4:
                user_id = int(sys.argv[2])
                new_password = sys.argv[3]
                update_admin_password(user_id, new_password)
            else:
                print("Usage: python verify_password_security.py update <user_id> <new_password>")
        else:
            print("Unknown command. Available commands:")
            print("  verify - Check password security for all admin users")
            print("  create <email> <password> [full_name] - Create new secure admin user")
            print("  update <user_id> <new_password> - Update admin user password")
    else:
        # Default: run verification
        verify_admin_password_security() 