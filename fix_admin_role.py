#!/usr/bin/env python3
"""
Admin Role Fix Script
This script ensures the admin user has the correct role and access.
"""

from database import SessionLocal
from models.users import DBUser, UserRole
from core.security import hash_password

def fix_admin_role():
    """Fix admin user role and access"""
    db = SessionLocal()
    try:
        # Find the admin user
        admin_user = db.query(DBUser).filter(DBUser.email == 'admin@washlink.com').first()
        
        if admin_user:
            # Update role to ensure it's admin in lowercase
            admin_user.role = UserRole.ADMIN.value.lower()
            # Update password
            admin_user.password = hash_password('admin123')
            # Ensure user is active
            admin_user.is_active = True
            
            db.commit()
            
            print('✅ Admin user updated successfully')
            print(f'   Email: {admin_user.email}')
            print(f'   Role: {admin_user.role}')
            print(f'   Active: {admin_user.is_active}')
            print('\nYou can now log in with:')
            print('Email: admin@washlink.com')
            print('Password: admin123')
        else:
            print('❌ Admin user not found')
            
    except Exception as e:
        print(f'❌ Error: {e}')
    finally:
        db.close()

if __name__ == "__main__":
    fix_admin_role() 