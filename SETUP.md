# WashLink Backend Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Environment
```bash
# Run the setup script
python setup.py

# Or manually copy env.example to .env
cp env.example .env
```

### 3. Start the Backend
```bash
# Navigate to backend directory
cd backend

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access the API
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Default Admin Credentials
- **Email**: admin@washlink.com
- **Password**: admin123

## Database Configuration

### Development (SQLite - Recommended)
The backend is configured to use SQLite by default for easy local development. No additional setup required.

### Production (MySQL)
If you want to use MySQL for production:

1. Update the `.env` file:
```env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/washlink_db
```

2. Create the MySQL database:
```sql
CREATE DATABASE washlink_db;
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/admin/login` - Admin login
- `POST /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/logout` - Logout

### Users
- `GET /api/v1/users/` - Get all users
- `GET /api/v1/users/{id}` - Get user by ID
- `PUT /api/v1/users/{id}/role` - Update user role
- `DELETE /api/v1/users/{id}` - Delete user

### Orders
- `GET /api/v1/orders/` - Get all orders
- `GET /api/v1/orders/{id}` - Get order by ID
- `POST /api/v1/orders/` - Create new order

## Troubleshooting

### Database Connection Issues
If you get database connection errors:
1. Make sure you're using SQLite for development
2. Check that the `.env` file exists and has the correct DATABASE_URL
3. Run `python setup.py` to create the .env file

### Import Errors
If you get import errors:
1. Make sure you're in the backend directory
2. Install dependencies: `pip install -r requirements.txt`
3. Check that all required packages are installed

### Port Already in Use
If port 8000 is already in use:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

## Development

### File Structure
```
backend/
├── api/           # API routes and endpoints
├── core/          # Core configuration and security
├── crud/          # Database operations
├── db/            # Database models
├── models/        # Pydantic schemas
├── services/      # Business logic
├── utils/         # Utility functions
├── main.py        # FastAPI application
├── database.py    # Database configuration
└── requirements.txt
```

### Adding New Endpoints
1. Create endpoint in `api/v1/endpoints/`
2. Add route to `api/v1/routers.py`
3. Update schemas in `models/` if needed
4. Add CRUD operations in `crud/` if needed

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | Database connection string | sqlite:///./washlink.db |
| SECRET_KEY | JWT secret key | your-secret-key-change-in-production |
| ACCESS_TOKEN_EXPIRE_MINUTES | JWT token expiry | 1440 (24 hours) |
| DEBUG | Debug mode | true |
| ALLOWED_ORIGINS | CORS allowed origins | ["http://localhost:3000", "http://localhost:5173"] | 