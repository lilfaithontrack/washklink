# WashLink Backend - MongoDB Edition

WashLink is a modern laundry service platform that connects customers with service providers and delivery drivers. This backend is built with FastAPI and MongoDB, providing a scalable and flexible solution.

## 🚀 Features

- **Async Operations**: Built with FastAPI and Motor for high-performance async I/O
- **MongoDB Integration**: Uses Beanie ODM for elegant MongoDB document mapping
- **Real-time Location**: Geospatial queries for finding nearby service providers and drivers
- **Authentication**: JWT-based authentication with role-based access control
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation
- **Automated Assignment**: Smart order assignment to service providers and drivers

## 🛠️ Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **MongoDB**: NoSQL database for flexible data storage
- **Motor**: Async MongoDB driver for Python
- **Beanie**: Async ODM (Object Document Mapper) for MongoDB
- **PyJWT**: JSON Web Token implementation
- **Pydantic**: Data validation using Python type annotations

## 📋 Prerequisites

- Python 3.8+
- MongoDB 4.4+
- Redis (for caching and sessions)

## 🔧 Installation

1. **Clone the repository**:
```bash
git clone https://github.com/your-repo/washlink-backend.git
cd washlink-backend
```

2. **Create and activate virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up MongoDB**:
   - Install MongoDB locally or use Docker:
   ```bash
   docker run -d -p 27017:27017 --name washlink-mongo mongo:latest
   ```

5. **Configure environment**:
```bash
cp env.example.mongodb .env
# Update .env with your settings
```

6. **Initialize database**:
```bash
python setup_mongodb.py
```

## 🏃‍♂️ Running the Application

1. **Start the server**:
```bash
uvicorn main:app --reload
```

2. **Access the API**:
- API: http://localhost:8000/api/v1
- Documentation: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## 📚 API Documentation

The API is organized around the following main resources:

### Users
- `POST /api/v1/auth/login`: User login
- `POST /api/v1/auth/admin/login`: Admin login
- `GET /api/v1/users/me`: Get current user profile
- `GET /api/v1/users`: List users (admin only)

### Orders
- `POST /api/v1/orders`: Create new order
- `GET /api/v1/orders`: List orders
- `GET /api/v1/orders/{id}`: Get order details
- `PUT /api/v1/orders/{id}`: Update order
- `DELETE /api/v1/orders/{id}`: Delete order

### Service Providers
- `GET /api/v1/providers/nearby`: Find nearby providers
- `POST /api/v1/providers`: Register new provider
- `GET /api/v1/providers/{id}/orders`: Get provider's orders

### Drivers
- `GET /api/v1/drivers/nearby`: Find nearby drivers
- `POST /api/v1/drivers/location`: Update driver location
- `GET /api/v1/drivers/{id}/orders`: Get driver's orders

## 🗄️ Database Structure

### Collections
- **users**: User accounts and authentication
- **service_providers**: Laundry service providers
- **drivers**: Delivery drivers
- **orders**: Customer orders with embedded items
- **payments**: Payment transactions
- **notifications**: User notifications

### Indexes
Each collection has optimized indexes for common queries:
- Geospatial indexes for location-based queries
- Text indexes for search functionality
- Compound indexes for complex queries

## 🔒 Security

- JWT-based authentication
- Role-based access control (User, Manager, Admin)
- Password hashing with bcrypt
- CORS protection
- Rate limiting
- Input validation with Pydantic

## 🧪 Testing

Run the test suite:
```bash
pytest
```

For coverage report:
```bash
pytest --cov=app tests/
```

## 🔄 Data Migration

If you're migrating from the SQL version:

1. Keep your SQL database running
2. Update environment variables:
```env
DATABASE_URL=your-old-sql-url
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=washlink_db
```

3. Run migration script:
```bash
python migrate_to_mongodb.py
```

## 📈 Monitoring

Monitor your MongoDB deployment:
- Use MongoDB Compass for visual exploration
- Set up MongoDB Atlas monitoring
- Configure logging and alerts

## 🚀 Deployment

1. **Docker**:
```bash
docker-compose up -d
```

2. **Manual**:
- Set up MongoDB replica set
- Configure environment variables
- Use process manager (e.g., Supervisor)
- Set up reverse proxy (e.g., Nginx)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support:
- Create an issue
- Contact: support@washlink.com
- Documentation: [docs/](docs/)

