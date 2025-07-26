# WashLink Admin Panel Setup Guide

This guide explains how to set up admin users for the WashLink admin panel with properly hashed passwords.

## 🔐 Password Security

All admin passwords are automatically hashed using bcrypt before being stored in the database. This ensures:
- Passwords are never stored in plain text
- Each password hash is unique (even for identical passwords)
- Industry-standard security practices

## 🚀 Quick Setup Methods

### Method 1: Using the Python Script (Recommended)

1. **Start the backend server:**
   ```bash
   cd backend
   python main.py
   ```

2. **Register an admin user:**
   ```bash
   # Interactive mode
   python register_admin.py
   
   # Or with command line arguments
   python register_admin.py admin@washlink.com mypassword "Admin User" +251911000000
   ```

### Method 2: Using Curl Commands

1. **Start the backend server:**
   ```bash
   cd backend
   python main.py
   ```

2. **Run the registration script:**
   ```bash
   chmod +x register_admin_curl.sh
   ./register_admin_curl.sh
   ```

3. **Or use curl manually:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/admin/create" \
     -H "Content-Type: application/json" \
     -d '{
       "full_name": "Admin User",
       "phone_number": "+251911000000",
       "email": "admin@washlink.com",
       "role": "admin",
       "password": "admin123"
     }'
   ```

### Method 3: Using the API Directly

The admin creation endpoint is available at:
```
POST /api/v1/auth/admin/create
```

**Request Body:**
```json
{
  "full_name": "Admin User",
  "phone_number": "+251911000000",
  "email": "admin@washlink.com",
  "role": "admin",
  "password": "admin123"
}
```

## 🔍 Verifying Password Security

To check if all admin passwords are properly hashed:

```bash
python verify_password_security.py verify
```

This will:
- List all admin users
- Check if passwords are properly hashed
- Identify any security issues

## 🔄 Changing Passwords

### Via API
```bash
curl -X POST "http://localhost:8000/api/v1/auth/change-password" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "current_password": "oldpassword",
    "new_password": "newpassword"
  }'
```

### Via Script
```bash
python verify_password_security.py update USER_ID newpassword
```

## 🛡️ Security Best Practices

1. **Use Strong Passwords:**
   - Minimum 6 characters
   - Mix of letters, numbers, and symbols
   - Avoid common passwords

2. **Change Default Passwords:**
   - The default admin password is `admin123`
   - Change it immediately after first login

3. **Regular Password Updates:**
   - Update passwords regularly
   - Use unique passwords for different accounts

4. **Access Control:**
   - Only give admin access to trusted users
   - Monitor admin user activities

## 🔧 Troubleshooting

### Common Issues

1. **Connection Error:**
   ```
   ❌ Connection error: Could not connect to http://localhost:8000
   ```
   **Solution:** Make sure the backend server is running on port 8000

2. **Email Already Exists:**
   ```
   ❌ Registration failed: Email already registered
   ```
   **Solution:** Use a different email or delete the existing user

3. **Invalid Role:**
   ```
   ❌ Registration failed: Invalid role
   ```
   **Solution:** Use "admin" or "manager" as the role

4. **Password Too Short:**
   ```
   ❌ Password must be at least 6 characters long
   ```
   **Solution:** Use a longer password

### Database Issues

If you need to reset the database:

1. **Delete the database file:**
   ```bash
   rm washlink.db
   ```

2. **Restart the server:**
   ```bash
   python main.py
   ```

3. **Register a new admin user:**
   ```bash
   python register_admin.py
   ```

## 📋 Default Admin User

When the server starts for the first time, it automatically creates a default admin user:

- **Email:** admin@washlink.com
- **Password:** admin123
- **Role:** ADMIN
- **Phone:** +251911000000

⚠️ **Important:** Change this default password immediately!

## 🌐 Admin Panel Access

After registering an admin user:

1. **Start the admin panel:**
   ```bash
   cd admin-panel
   npm run dev
   ```

2. **Open in browser:**
   ```
   http://localhost:3000
   ```

3. **Login with your credentials**

4. **Change your password** in the Settings page

## 📞 Support

If you encounter any issues:

1. Check the server logs for error messages
2. Verify the database connection
3. Ensure all required dependencies are installed
4. Check that the API endpoints are accessible

## 🔒 Security Notes

- All passwords are hashed using bcrypt
- Passwords are never logged or stored in plain text
- API tokens expire after a configurable time period
- Failed login attempts are logged for security monitoring 