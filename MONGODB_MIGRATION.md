# WashLink Backend MongoDB Migration Guide

This guide explains how to migrate the WashLink backend from SQL (SQLite/MySQL) to MongoDB using:
- **Motor**: Async MongoDB driver for Python
- **Beanie**: Async Object Document Mapper (ODM) built on top of Pydantic
- **PyMongo**: MongoDB driver for Python

## Overview

The WashLink backend has been successfully migrated from SQLAlchemy + SQL to MongoDB using:
- **Motor**: Async MongoDB driver for Python
- **Beanie**: Async Object Document Mapper (ODM) built on top of Pydantic
- **PyMongo**: MongoDB driver for Python

## Changes Made

### 1. Dependencies Updated
- ✅ Removed: `sqlalchemy`, `pymysql`, `alembic`
- ✅ Added: `motor`, `pymongo`, `beanie`, `dnspython`

### 2. Database Connection
- ✅ **Old**: SQLAlchemy engine and sessions in `database.py`
- ✅ **New**: Motor async client and Beanie initialization

### 3. Models
- ✅ **Old**: SQLAlchemy models in `models/` and `db/models/`
- ✅ **New**: Beanie Document models in `models/mongo_models.py`

### 4. CRUD Operations
- ✅ **Old**: Synchronous SQLAlchemy CRUD operations
- ✅ **New**: Async MongoDB CRUD operations in `crud/mongo_*.py`

### 5. Application Startup
- ✅ **Old**: Synchronous database initialization
- ✅ **New**: Async startup/shutdown events for MongoDB connection

## Installation & Setup

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Install MongoDB
#### On Ubuntu/Debian:
```bash
sudo apt-get install mongodb-community
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

#### On macOS:
```bash
brew install mongodb-community
brew services start mongodb
```

#### On Windows:
Download and install MongoDB Community Server from the official website.

#### Using Docker:
```bash
docker run -d -p 27017:27017 --name washlink-mongo mongo:latest
```

### 3. Environment Configuration
Copy the new environment template:
```bash
cp env.example.mongodb .env
```

Update your `.env` file with MongoDB settings:
```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=washlink_db
```

### 4. Data Migration
To migrate existing SQL data to MongoDB:

```bash
python migrate_to_mongodb.py
```

This script will:
- Connect to both SQL and MongoDB databases
- Clear existing MongoDB data (optional)
- Migrate all data maintaining relationships
- Provide detailed logging of the migration process

## New MongoDB Models

### Document Structure
All models now inherit from Beanie's `Document` class:

```python
from beanie import Document
from pydantic import Field
from typing import Optional

class User(Document):
    full_name: str
    email: Optional[str] = Field(unique=True)
    # ... other fields
    
    class Settings:
        name = "users"  # Collection name
        indexes = ["email", "phone_number"]  # Database indexes
```

### Key Models:
- **User**: User accounts and authentication
- **ServiceProvider**: Laundry service providers
- **Driver**: Delivery drivers
- **Order**: Customer orders with embedded order items
- **Payment**: Payment transactions
- **Notification**: User notifications
- **Item**: Laundry service items

## New CRUD Operations

All CRUD operations are now async:

```python
from crud.mongo_user import user_mongo_crud

# Get user
user = await user_mongo_crud.get(user_id)

# Create user
new_user = await user_mongo_crud.create(user_data)

# Update user
updated_user = await user_mongo_crud.update(user_id, update_data)

# Delete user
success = await user_mongo_crud.delete(user_id)
```

## Benefits of MongoDB Migration

### 1. Scalability
- Horizontal scaling capabilities
- Better performance with large datasets
- Automatic sharding support

### 2. Flexibility
- Schema-less design allows for easier evolution
- Embedded documents reduce complex joins
- Rich query capabilities

### 3. Performance
- Async operations throughout the stack
- Better handling of concurrent requests
- Optimized for read/write operations

### 4. Modern Stack
- Native JSON document storage
- Better integration with FastAPI
- Simplified data modeling

## Database Schema Changes

### Relationships
MongoDB uses document references instead of foreign keys:

```python
# Old SQL approach
class Order(Base):
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="orders")

# New MongoDB approach
class Order(Document):
    user_id: ObjectId  # Reference to User document
    # Relationships are handled in application logic
```

### Embedded Documents
Order items are now embedded within orders:

```python
class OrderItem(BaseModel):
    product_id: ObjectId
    quantity: int
    price: float

class Order(Document):
    items: List[OrderItem] = []  # Embedded order items
```

## API Changes

### Route Updates
Routes now use async CRUD operations:

```python
@router.get("/users/{user_id}")
async def get_user(user_id: str):
    user = await user_mongo_crud.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### Error Handling
MongoDB-specific error handling:

```python
from pymongo.errors import DuplicateKeyError

try:
    user = await user_mongo_crud.create(user_data)
except DuplicateKeyError:
    raise HTTPException(status_code=400, detail="User already exists")
```

## Testing

### Unit Tests
Update your tests to use async/await:

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    response = await client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201
```

### Database Testing
Use separate test database:

```python
# test_settings.py
MONGODB_DB_NAME = "washlink_test_db"
```

## Performance Optimization

### Indexes
Indexes are defined in model Settings:

```python
class User(Document):
    class Settings:
        name = "users"
        indexes = [
            "email",
            "phone_number",
            [("created_at", -1)],  # Descending index
            [("location.latitude", 1), ("location.longitude", 1)]  # Compound index
        ]
```

### Aggregation Pipelines
Use MongoDB's aggregation framework for complex queries:

```python
async def get_order_statistics():
    pipeline = [
        {"$match": {"status": "completed"}},
        {"$group": {
            "_id": "$service_provider_id",
            "total_orders": {"$sum": 1},
            "total_revenue": {"$sum": "$subtotal"}
        }}
    ]
    
    result = await Order.aggregate(pipeline).to_list()
    return result
```

## Troubleshooting

### Common Issues

1. **Connection Issues**
   ```bash
   # Check MongoDB status
   sudo systemctl status mongodb
   
   # Check connection
   mongo --eval "db.stats()"
   ```

2. **Migration Errors**
   - Ensure MongoDB is running
   - Check database permissions
   - Verify environment variables

3. **Performance Issues**
   - Add appropriate indexes
   - Use aggregation pipelines for complex queries
   - Consider data denormalization

### Logging
Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Rollback Plan

If you need to rollback to SQL:

1. Keep the original SQL database backup
2. Revert `requirements.txt` changes
3. Restore original `database.py`
4. Switch back to SQLAlchemy models
5. Update environment variables

## Next Steps

1. **Update API Routes**: Modify existing routes to use new async CRUD operations
2. **Update Tests**: Convert tests to async and update assertions
3. **Performance Tuning**: Add indexes and optimize queries
4. **Monitoring**: Set up MongoDB monitoring and alerts
5. **Backup Strategy**: Implement MongoDB backup procedures

## Support

For questions or issues with the MongoDB migration:
- Check MongoDB documentation: https://docs.mongodb.com/
- Beanie documentation: https://beanie-odm.dev/
- Motor documentation: https://motor.readthedocs.io/

## Conclusion

The migration to MongoDB provides a modern, scalable foundation for the WashLink backend. The async nature of the new stack improves performance and the flexible document model simplifies data management.

Remember to thoroughly test all functionality after migration and monitor performance in production. 