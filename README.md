# Laundry App Backend

A comprehensive FastAPI-based backend for a laundry service management application with role-based access control, live tracking, and automated assignment.

## 🚀 Features

### 🔐 **Authentication & Authorization**
- **Role-Based Access Control**: USER, MANAGER, ADMIN roles
- **Phone-Only Authentication**: Regular users authenticate with phone + OTP
- **Email Authentication**: Admin/Manager users use email + password
- **JWT Token Security**: Secure token-based authentication

### 📱 **User Management**
- **Regular Users**: Phone number + OTP authentication
- **Admin/Manager Users**: Email + password authentication
- **Role-Based Permissions**: Different access levels for different user types

### 🧺 **Order Management**
- **Complete Booking System**: Order creation and processing
- **Automatic Provider Assignment**: Location-based provider matching
- **Status Tracking**: Real-time order status updates
- **Payment Integration**: Chapa and Telebirr payment gateways

### 🚚 **Live Tracking & Delivery**
- **Real-Time Driver Tracking**: WebSocket-based live location updates
- **Delivery Management**: Driver assignment and route optimization
- **Customer Notifications**: SMS notifications for order updates

### 🏪 **Service Provider Management**
- **Provider Registration**: Complete provider onboarding
- **Location-Based Assignment**: Automatic order assignment based on proximity
- **Capacity Management**: Order load balancing

### 📊 **Admin Dashboard**
- **Real-Time Analytics**: Live tracking dashboard
- **User Management**: Role-based user administration
- **Order Monitoring**: Complete order lifecycle management

## 🏗️ Project Structure

```
laundry_app_backend/
├── app/
│   ├── core/             # Core configurations and utilities
│   │   ├── config.py     # Application settings
│   │   ├── database.py   # Database connection
│   │   ├── security.py   # JWT & password hashing
│   │   └── exceptions.py # Custom exceptions
│   ├── db/               # Database models and migrations
│   │   ├── models/       # SQLAlchemy ORM models
│   │   │   ├── user.py   # User model with roles
│   │   │   ├── order.py  # Order/booking models
│   │   │   ├── driver.py # Driver management
│   │   │   └── ...
│   ├── schemas/          # Pydantic models for validation
│   ├── crud/             # Database operations
│   ├── services/         # Business logic
│   │   ├── auth_service.py      # Authentication logic
│   │   ├── order_service.py     # Order processing
│   │   ├── tracking_service.py  # Live tracking
│   │   ├── assignment_service.py # Auto-assignment
│   │   └── payment_gateways/    # Payment integrations
│   └── api/              # FastAPI endpoints
│       └── v1/           # API version 1
│           ├── endpoints/
│           │   ├── auth.py      # Authentication endpoints
│           │   ├── users.py     # User management
│           │   ├── orders.py    # Order management
│           │   ├── tracking.py  # Live tracking
│           │   └── ...
├── controllers/          # Legacy controllers (backward compatibility)
├── models/              # Legacy models (backward compatibility)
├── routes/              # Legacy routes (backward compatibility)
└── main.py              # Legacy main file (backward compatibility)
```

## 🔧 Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL database
- AfroMessage API credentials (for SMS)

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd laundry_app_backend
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Create a `.env` file:**
```env
DATABASE_URL=postgresql://username:password@localhost/database_name
AFRO_MESSAGE_API_KEY=your_afromessage_api_key
AFRO_MESSAGE_SENDER_NAME=your_sender_name
AFRO_MESSAGE_IDENTIFIER_ID=your_identifier_id
SECRET_KEY=your_jwt_secret_key
```

5. **Run the application:**
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### 🐳 Docker Setup

1. **Build the Docker image:**
```bash
docker build -t laundry-app-backend .
```

2. **Run the container:**
```bash
docker run -p 8000:8000 --env-file .env laundry-app-backend
```

## 📚 API Documentation

Once running, access:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔐 Authentication Guide

### **Regular Users (USER Role)**

**Request OTP:**
```bash
POST /api/v1/auth/request-otp
{
    "phone_number": "+251912345678",
    "full_name": "John Doe"
}
```

**Login with OTP:**
```bash
POST /api/v1/auth/login
{
    "phone_number": "+251912345678",
    "full_name": "John Doe",
    "otp_code": "123456"
}
```

### **Admin/Manager Users**

**Login:**
```bash
POST /api/v1/auth/admin/login
{
    "email": "admin@washlink.com",
    "password": "your_password"
}
```

**Create Admin Account:**
```bash
POST /api/v1/auth/admin/create
{
    "full_name": "Admin User",
    "phone_number": "+251911111111",
    "email": "admin@washlink.com",
    "role": "admin",
    "password": "secure_password"
}
```

## 🛡️ Role-Based Access Control

### **USER Role**
- Create and view own orders
- Update own profile
- Track own deliveries

### **MANAGER Role**
- All USER permissions
- View all orders and users
- Update order statuses
- Assign drivers and providers

### **ADMIN Role**
- All MANAGER permissions
- Create/delete users
- Manage user roles
- System administration

## 📱 API Endpoints

### **Authentication**
- `POST /api/v1/auth/request-otp` - Request OTP for regular users
- `POST /api/v1/auth/login` - Login with OTP
- `POST /api/v1/auth/admin/login` - Admin/Manager login
- `POST /api/v1/auth/admin/create` - Create admin accounts
- `GET /api/v1/auth/me` - Get current user info

### **Users**
- `GET /api/v1/users/` - Get all users (Manager/Admin)
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/{id}` - Update user
- `PUT /api/v1/users/{id}/role` - Update user role (Admin)

### **Orders**
- `POST /api/v1/orders/` - Create new order
- `GET /api/v1/orders/` - Get orders (role-based filtering)
- `GET /api/v1/orders/my-orders` - Get current user's orders
- `PUT /api/v1/orders/{id}/status` - Update order status

### **Live Tracking**
- `WebSocket /api/v1/tracking/ws/driver/{id}` - Driver tracking
- `WebSocket /api/v1/tracking/ws/customer/{id}` - Customer tracking
- `WebSocket /api/v1/tracking/ws/admin` - Admin dashboard
- `GET /api/v1/tracking/order/{id}/tracking` - Get order tracking

### **Legacy Endpoints** (Backward Compatibility)
- `/auth/request-otp` - Legacy OTP request
- `/auth/login` - Legacy login
- `/users/` - Legacy user endpoints
- `/bookings/` - Legacy booking endpoints

## 🌍 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `AFRO_MESSAGE_API_KEY` | AfroMessage API key for SMS | Yes |
| `AFRO_MESSAGE_SENDER_NAME` | SMS sender name | Yes |
| `AFRO_MESSAGE_IDENTIFIER_ID` | AfroMessage identifier | Yes |
| `SECRET_KEY` | JWT secret key | Yes |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | No (default: 1440) |

## 🚀 Default Admin Account

On first startup, a default admin account is created:
- **Email**: `admin@washlink.com`
- **Password**: `admin123`
- **Phone**: `+251911000000`

⚠️ **Important**: Change the default password immediately in production!

## 🔄 Migration from Legacy

The application maintains full backward compatibility with existing endpoints while providing new role-based functionality. Existing clients can continue using legacy endpoints while new implementations should use the `/api/v1/` endpoints.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

