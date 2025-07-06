# Laundry App Backend

A comprehensive FastAPI-based backend for a laundry service management application with role-based access control, live tracking, automated assignment, and integrated payment processing.

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

### 💳 **Payment Processing**
- **Multiple Payment Gateways**: Chapa and Telebirr integration
- **Secure Transactions**: End-to-end payment security
- **Payment Verification**: Automatic payment status verification
- **Webhook Support**: Real-time payment status updates
- **Cash on Delivery**: Traditional payment option

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
- **Payment Analytics**: Transaction monitoring and reporting

## 🏗️ Project Structure

```
laundry_app_backend/
├── core/                 # Core configurations and utilities
│   ├── config.py         # Application settings with payment configs
│   ├── security.py       # JWT & password hashing
│   └── exceptions.py     # Custom exceptions
├── db/                   # Database models and migrations
│   └── models/           # SQLAlchemy ORM models
│       ├── payment.py    # Payment model
│       └── ...
├── schemas/              # Pydantic models for validation
│   ├── payment.py        # Payment schemas
│   └── ...
├── services/             # Business logic
│   ├── payment_service.py           # Payment processing logic
│   ├── payment_gateways/            # Payment gateway integrations
│   │   ├── base_payment.py          # Abstract payment gateway
│   │   ├── chapa.py                 # Chapa payment gateway
│   │   └── telebirr.py              # Telebirr payment gateway
│   └── ...
└── api/                  # FastAPI endpoints
    └── v1/               # API version 1
        ├── endpoints/
        │   ├── payments.py          # Payment endpoints
        │   └── ...
```

## 🔧 Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL database
- AfroMessage API credentials (for SMS)
- Chapa API credentials (for Chapa payments)
- Telebirr API credentials (for Telebirr payments)

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

# SMS API
AFRO_MESSAGE_API_KEY=your_afromessage_api_key
AFRO_MESSAGE_SENDER_NAME=your_sender_name
AFRO_MESSAGE_IDENTIFIER_ID=your_identifier_id

# Payment Gateways
CHAPA_SECRET_KEY=your_chapa_secret_key
CHAPA_PUBLIC_KEY=your_chapa_public_key
TELEBIRR_APP_ID=your_telebirr_app_id
TELEBIRR_APP_KEY=your_telebirr_app_key

# Security
SECRET_KEY=your_jwt_secret_key
```

5. **Run the application:**
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## 💳 Payment Integration

### **Supported Payment Methods**

1. **Chapa Payment Gateway**
   - Credit/Debit Cards
   - Mobile Money
   - Bank Transfers
   - Ethiopian Birr (ETB)

2. **Telebirr Mobile Wallet**
   - Telebirr mobile payments
   - Ethiopian Birr (ETB)

3. **Cash on Delivery**
   - Traditional payment method
   - Pay when order is delivered

### **Payment Flow**

1. **Initiate Payment**
```bash
POST /api/v1/payments/initiate
{
    "order_id": 123,
    "amount": 150.00,
    "payment_method": "chapa",
    "return_url": "https://yourapp.com/payment-success"
}
```

2. **Redirect to Payment Gateway**
- User is redirected to Chapa/Telebirr payment page
- Complete payment on gateway

3. **Payment Verification**
```bash
GET /api/v1/payments/verify/{transaction_id}?payment_method=chapa
```

4. **Webhook Callbacks**
- Automatic payment status updates
- Order status progression

### **Payment Security**

- **Secure API Keys**: Environment-based configuration
- **Transaction Verification**: Double verification of payments
- **Webhook Validation**: Secure callback handling
- **PCI Compliance**: Following payment industry standards

## 📚 API Documentation

Once running, access:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 💳 Payment API Endpoints

### **Payment Management**
- `POST /api/v1/payments/initiate` - Initiate payment
- `GET /api/v1/payments/verify/{transaction_id}` - Verify payment
- `GET /api/v1/payments/order/{order_id}` - Get order payment info
- `GET /api/v1/payments/my-payments` - Get user payment history
- `GET /api/v1/payments/methods` - Get available payment methods

### **Payment Callbacks**
- `POST /api/v1/payments/chapa/callback` - Chapa webhook
- `POST /api/v1/payments/telebirr/callback` - Telebirr webhook

## 🌍 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `AFRO_MESSAGE_API_KEY` | AfroMessage API key for SMS | Yes |
| `CHAPA_SECRET_KEY` | Chapa payment gateway secret key | Yes |
| `CHAPA_PUBLIC_KEY` | Chapa payment gateway public key | Yes |
| `TELEBIRR_APP_ID` | Telebirr application ID | Yes |
| `TELEBIRR_APP_KEY` | Telebirr application key | Yes |
| `SECRET_KEY` | JWT secret key | Yes |

## 🔄 Payment Gateway Setup

### **Chapa Setup**
1. Register at [Chapa.co](https://chapa.co)
2. Get your API keys from dashboard
3. Add keys to environment variables
4. Configure webhook URLs

### **Telebirr Setup**
1. Contact Telebirr for merchant account
2. Get application credentials
3. Add credentials to environment variables
4. Configure callback URLs

## 🚀 Default Admin Account

On first startup, a default admin account is created:
- **Email**: `admin@washlink.com`
- **Password**: `admin123`
- **Phone**: `+251911000000`

⚠️ **Important**: Change the default password immediately in production!

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

