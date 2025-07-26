#!/bin/bash

# WashLink Admin Registration - Curl Commands
# Make sure the backend server is running on port 8000

echo "🔐 WashLink Admin Registration - Curl Commands"
echo "=============================================="

# Set your admin details here
EMAIL="admin@washlink.com"
PASSWORD="admin123"
FULL_NAME="System Administrator"
PHONE="+251911000000"

echo "📧 Email: $EMAIL"
echo "🔑 Password: $PASSWORD"
echo "👤 Full Name: $FULL_NAME"
echo "📱 Phone: $PHONE"
echo ""

# Register admin user
echo "🚀 Registering admin user..."
curl -X POST "http://localhost:8000/api/v1/auth/admin/create" \
  -H "Content-Type: application/json" \
  -d "{
    \"full_name\": \"$FULL_NAME\",
    \"phone_number\": \"$PHONE\",
    \"email\": \"$EMAIL\",
    \"role\": \"admin\",
    \"password\": \"$PASSWORD\"
  }"

echo ""
echo ""

# Test login
echo "🧪 Testing admin login..."
curl -X POST "http://localhost:8000/api/v1/auth/admin/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\"
  }"

echo ""
echo ""
echo "✅ Registration complete!"
echo "🌐 You can now login at: http://localhost:3000" 