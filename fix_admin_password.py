#!/usr/bin/env python3

from core.security import hash_password
from database import SessionLocal
from models.users import DBUser

def fix_admin_password():
    db = SessionLocal()
    try:
        # Create or update the first admin
        admin_user = db.query(DBUser).filter(DBUser.email == 'admin@washlink.com').first()
        if admin_user:
            admin_user.hashed_password = hash_password('admin123')
            db.commit()
            print('✅ Admin password updated successfully')
            print(f'   Email: {admin_user.email}')
            print(f'   Role: {admin_user.role}')
        else:
            new_admin = DBUser(
                email='admin@washlink.com',
                hashed_password=hash_password('admin123'),
                is_active=True,
                role='admin',
                first_name='Admin',
                last_name='User',
                phone='+251911000000'
            )
            db.add(new_admin)
            db.commit()
            print('✅ Admin user created successfully')
            print(f'   Email: {new_admin.email}')
            print(f'   Role: {new_admin.role}')

        # Create or update the second admin
        admin2_user = db.query(DBUser).filter(DBUser.email == 'admin2@washlink.com').first()
        if admin2_user:
            admin2_user.hashed_password = hash_password('admin1234')
            db.commit()
            print('✅ Admin2 password updated successfully')
            print(f'   Email: {admin2_user.email}')
            print(f'   Role: {admin2_user.role}')
        else:
            new_admin2 = DBUser(
                email='admin2@washlink.com',
                hashed_password=hash_password('admin1234'),
                is_active=True,
                role='admin',
                first_name='Admin2',
                last_name='User',
                phone='+251911000001'
            )
            db.add(new_admin2)
            db.commit()
            print('✅ Admin2 user created successfully')
            print(f'   Email: {new_admin2.email}')
            print(f'   Role: {new_admin2.role}')
    except Exception as e:
        print(f'❌ Error: {e}')
    finally:
        db.close()

if __name__ == "__main__":
    fix_admin_password() 