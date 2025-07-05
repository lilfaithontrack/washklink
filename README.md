# Laundry App Backend

A comprehensive FastAPI-based backend for a laundry service management application.

## Features

- **User Authentication**: OTP-based authentication using AfroMessage SMS API
- **Order Management**: Complete booking and order processing system
- **Service Provider Management**: Registration and management of laundry service providers
- **Payment Integration**: Support for Chapa and Telebirr payment gateways
- **Item Management**: Pricing and inventory management for laundry items
- **Notification Service**: SMS notifications for order updates
- **Driver Management**: Delivery driver assignment and tracking

## Project Structure

```
laundry_app_backend/
├── app/
│   ├── core/             # Core configurations and utilities
│   ├── db/               # Database models and migrations
│   ├── schemas/          # Pydantic models for request/response validation
│   ├── crud/             # CRUD operations for database models
│   ├── services/         # Business logic and external API integrations
│   └── api/              # FastAPI routers (API endpoints)
├── controllers/          # Legacy controllers (maintained for compatibility)
├── models/              # Legacy models (maintained for compatibility)
├── routes/              # Legacy routes (maintained for compatibility)
├── schemas/             # Legacy schemas (maintained for compatibility)
├── utils/               # Legacy utilities (maintained for compatibility)
├── main.py              # Legacy main file (maintained for compatibility)
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker configuration
└── README.md           # This file
```

## Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL database
- AfroMessage API credentials (for SMS)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd laundry_app_backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with the following variables:
```env
DATABASE_URL=postgresql://username:password@localhost/database_name
AFRO_MESSAGE_API_KEY=your_afromessage_api_key
AFRO_MESSAGE_SENDER_NAME=your_sender_name
AFRO_MESSAGE_IDENTIFIER_ID=your_identifier_id
SECRET_KEY=your_jwt_secret_key
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Docker Setup

1. Build the Docker image:
```bash
docker build -t laundry-app-backend .
```

2. Run the container:
```bash
docker run -p 8000:8000 --env-file .env laundry-app-backend
```

## API Documentation

Once the application is running, you can access:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- `POST /api/v1/auth/request-otp` - Request OTP for phone verification
- `POST /api/v1/auth/login` - Login with OTP verification

### Users
- `GET /api/v1/users/` - Get all users
- `GET /api/v1/users/{user_id}` - Get user by ID
- `GET /api/v1/users/me` - Get current user profile

### Orders
- `POST /api/v1/orders/` - Create new booking
- `GET /api/v1/orders/` - Get all bookings
- `GET /api/v1/orders/{booking_id}` - Get booking by ID

### Laundry Providers
- `GET /api/v1/laundry-providers/` - Get all service providers
- `GET /api/v1/laundry-providers/{provider_id}` - Get provider by ID
- `POST /api/v1/laundry-providers/` - Create new service provider

### Payments
- `POST /api/v1/payments/initiate` - Initiate payment
- `POST /api/v1/payments/chapa/callback` - Chapa payment callback
- `POST /api/v1/payments/telebirr/callback` - Telebirr payment callback
- `GET /api/v1/payments/verify/{transaction_id}` - Verify payment

### Items
- `GET /api/v1/items/` - Get all items with pricing
- `GET /api/v1/items/{item_id}` - Get item by ID

## Legacy Compatibility

The application maintains backward compatibility with existing endpoints:

- `/service-provider/` - Legacy service provider endpoints
- `/bookings/` - Legacy booking endpoints
- `/users/` - Legacy user endpoints
- `/api/items/` - Legacy item endpoints

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `AFRO_MESSAGE_API_KEY` | AfroMessage API key for SMS | Yes |
| `AFRO_MESSAGE_SENDER_NAME` | SMS sender name | Yes |
| `AFRO_MESSAGE_IDENTIFIER_ID` | AfroMessage identifier | Yes |
| `SECRET_KEY` | JWT secret key | Yes |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | No |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | No |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.