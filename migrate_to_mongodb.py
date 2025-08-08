#!/usr/bin/env python3
"""
Data Migration Script: SQL to MongoDB
This script migrates data from the existing SQL database to MongoDB
"""

import asyncio
import os
import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# MongoDB imports
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

# Model imports
from models.mongo_models import (
    User, ServiceProvider, Driver, Order, 
    Payment, Notification, Item, UserRole,
    OrderStatus, ProviderStatus, DriverStatus,
    VehicleType, ServiceType, PaymentMethod, PaymentStatus
)
from core.config import settings
from core.security import get_password_hash

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SQLToMongoMigrator:
    def __init__(self):
        self.sql_engine = None
        self.sql_session = None
        self.mongo_client = None
        self.mongo_db = None

    async def connect_databases(self):
        """Connect to both SQL and MongoDB databases"""
        try:
            # Connect to SQL database
            self.sql_engine = create_engine(settings.DATABASE_URL)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.sql_engine)
            self.sql_session = SessionLocal()
            logger.info("Connected to SQL database")

            # Connect to MongoDB
            self.mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
            self.mongo_db = self.mongo_client[settings.MONGODB_DB_NAME]
            
            # Initialize Beanie
            await init_beanie(
                database=self.mongo_db,
                document_models=[
                    User, ServiceProvider, Driver, Order,
                    Payment, Notification, Item
                ]
            )
            logger.info("Connected to MongoDB and initialized Beanie")
            
        except Exception as e:
            logger.error(f"Error connecting to databases: {str(e)}")
            raise

    async def close_connections(self):
        """Close database connections"""
        if self.sql_session:
            self.sql_session.close()
        if self.mongo_client:
            self.mongo_client.close()

    def fetch_sql_data(self, query: str) -> List[Dict[str, Any]]:
        """Fetch data from SQL database"""
        try:
            result = self.sql_session.execute(text(query))
            columns = result.keys()
            rows = result.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching SQL data: {str(e)}")
            return []

    async def migrate_users(self):
        """Migrate users from SQL to MongoDB"""
        logger.info("Starting user migration...")
        
        query = """
        SELECT id, full_name, phone_number, email, password, role, 
               is_active, created_at, updated_at, last_login
        FROM new_users
        """
        
        sql_users = self.fetch_sql_data(query)
        
        migrated_count = 0
        for sql_user in sql_users:
            try:
                # Map SQL user role to MongoDB enum
                role_mapping = {
                    'user': UserRole.USER,
                    'admin': UserRole.ADMIN,
                    'manager': UserRole.MANAGER
                }
                
                user = User(
                    full_name=sql_user['full_name'] or "",
                    phone_number=sql_user['phone_number'] or "",
                    email=sql_user['email'],
                    hashed_password=sql_user['password'],
                    role=role_mapping.get(sql_user['role'], UserRole.USER),
                    is_active=bool(sql_user['is_active']),
                    created_at=sql_user['created_at'] or datetime.utcnow(),
                    updated_at=sql_user['updated_at'] or datetime.utcnow(),
                    last_login=sql_user['last_login']
                )
                
                await user.insert()
                migrated_count += 1
                
            except Exception as e:
                logger.error(f"Error migrating user {sql_user.get('id')}: {str(e)}")
        
        logger.info(f"Migrated {migrated_count} users")

    async def migrate_service_providers(self):
        """Migrate service providers from SQL to MongoDB"""
        logger.info("Starting service provider migration...")
        
        query = """
        SELECT id, first_name, middle_name, last_name, address, phone_number, 
               email, password, status, is_active, is_available, is_verified,
               latitude, longitude, service_radius, nearby_condominum,
               date_of_birth, washing_machine, has_dryer, has_iron,
               max_daily_orders, current_order_count, average_completion_time,
               rating, total_orders_completed, business_name, business_license,
               description, created_at, updated_at, last_active
        FROM service_provider
        """
        
        sql_providers = self.fetch_sql_data(query)
        
        migrated_count = 0
        for sql_provider in sql_providers:
            try:
                # Map SQL status to MongoDB enum
                status_mapping = {
                    'active': ProviderStatus.ACTIVE,
                    'inactive': ProviderStatus.INACTIVE,
                    'busy': ProviderStatus.BUSY,
                    'offline': ProviderStatus.OFFLINE,
                    'suspended': ProviderStatus.SUSPENDED
                }
                
                provider = ServiceProvider(
                    first_name=sql_provider['first_name'] or "",
                    middle_name=sql_provider['middle_name'] or "",
                    last_name=sql_provider['last_name'] or "",
                    address=sql_provider['address'] or "",
                    phone_number=sql_provider['phone_number'] or 0,
                    email=sql_provider['email'] or "",
                    hashed_password=sql_provider['password'],
                    status=status_mapping.get(sql_provider['status'], ProviderStatus.OFFLINE),
                    is_active=bool(sql_provider['is_active']),
                    is_available=bool(sql_provider['is_available']),
                    is_verified=bool(sql_provider['is_verified']),
                    latitude=float(sql_provider['latitude'] or 0.0),
                    longitude=float(sql_provider['longitude'] or 0.0),
                    service_radius=float(sql_provider['service_radius'] or 10.0),
                    nearby_condominum=sql_provider['nearby_condominum'] or "",
                    date_of_birth=sql_provider['date_of_birth'] or datetime(2000, 1, 1),
                    washing_machine=bool(sql_provider['washing_machine']),
                    has_dryer=bool(sql_provider['has_dryer']),
                    has_iron=bool(sql_provider['has_iron']),
                    max_daily_orders=sql_provider['max_daily_orders'] or 20,
                    current_order_count=sql_provider['current_order_count'] or 0,
                    average_completion_time=float(sql_provider['average_completion_time'] or 24.0),
                    rating=float(sql_provider['rating'] or 0.0),
                    total_orders_completed=sql_provider['total_orders_completed'] or 0,
                    business_name=sql_provider['business_name'],
                    business_license=sql_provider['business_license'],
                    description=sql_provider['description'],
                    created_at=sql_provider['created_at'] or datetime.utcnow(),
                    updated_at=sql_provider['updated_at'] or datetime.utcnow(),
                    last_active=sql_provider['last_active'] or datetime.utcnow()
                )
                
                await provider.insert()
                migrated_count += 1
                
            except Exception as e:
                logger.error(f"Error migrating service provider {sql_provider.get('id')}: {str(e)}")
        
        logger.info(f"Migrated {migrated_count} service providers")

    async def migrate_drivers(self):
        """Migrate drivers from SQL to MongoDB"""
        logger.info("Starting driver migration...")
        
        query = """
        SELECT id, first_name, last_name, email, phone_number, license_number,
               vehicle_type, vehicle_plate, vehicle_model, vehicle_color,
               status, is_active, is_verified, current_latitude, current_longitude,
               last_location_update, service_radius, base_latitude, base_longitude,
               rating, total_deliveries, successful_deliveries, average_delivery_time,
               date_joined, created_at, updated_at, last_active, current_order_id
        FROM drivers
        """
        
        sql_drivers = self.fetch_sql_data(query)
        
        migrated_count = 0
        for sql_driver in sql_drivers:
            try:
                # Map SQL status and vehicle type to MongoDB enums
                status_mapping = {
                    'available': DriverStatus.AVAILABLE,
                    'busy': DriverStatus.BUSY,
                    'offline': DriverStatus.OFFLINE,
                    'on_delivery': DriverStatus.ON_DELIVERY,
                    'suspended': DriverStatus.SUSPENDED
                }
                
                vehicle_mapping = {
                    'motorcycle': VehicleType.MOTORCYCLE,
                    'car': VehicleType.CAR,
                    'van': VehicleType.VAN,
                    'bicycle': VehicleType.BICYCLE,
                    'foot': VehicleType.FOOT
                }
                
                driver = Driver(
                    first_name=sql_driver['first_name'] or "",
                    last_name=sql_driver['last_name'] or "",
                    email=sql_driver['email'] or "",
                    phone_number=sql_driver['phone_number'] or "",
                    license_number=sql_driver['license_number'] or "",
                    vehicle_type=vehicle_mapping.get(sql_driver['vehicle_type'], VehicleType.MOTORCYCLE),
                    vehicle_plate=sql_driver['vehicle_plate'] or "",
                    vehicle_model=sql_driver['vehicle_model'],
                    vehicle_color=sql_driver['vehicle_color'],
                    status=status_mapping.get(sql_driver['status'], DriverStatus.AVAILABLE),
                    is_active=bool(sql_driver['is_active']),
                    is_verified=bool(sql_driver['is_verified']),
                    current_latitude=sql_driver['current_latitude'],
                    current_longitude=sql_driver['current_longitude'],
                    last_location_update=sql_driver['last_location_update'],
                    service_radius=float(sql_driver['service_radius'] or 15.0),
                    base_latitude=sql_driver['base_latitude'],
                    base_longitude=sql_driver['base_longitude'],
                    rating=float(sql_driver['rating'] or 0.0),
                    total_deliveries=sql_driver['total_deliveries'] or 0,
                    successful_deliveries=sql_driver['successful_deliveries'] or 0,
                    average_delivery_time=float(sql_driver['average_delivery_time'] or 30.0),
                    date_joined=sql_driver['date_joined'] or datetime.utcnow(),
                    created_at=sql_driver['created_at'] or datetime.utcnow(),
                    updated_at=sql_driver['updated_at'] or datetime.utcnow(),
                    last_active=sql_driver['last_active'] or datetime.utcnow()
                )
                
                await driver.insert()
                migrated_count += 1
                
            except Exception as e:
                logger.error(f"Error migrating driver {sql_driver.get('id')}: {str(e)}")
        
        logger.info(f"Migrated {migrated_count} drivers")

    async def migrate_items(self):
        """Migrate items from SQL to MongoDB"""
        logger.info("Starting item migration...")
        
        query = """
        SELECT id, name, description, price, currency, category, 
               is_active, estimated_time, created_at, updated_at
        FROM items
        """
        
        sql_items = self.fetch_sql_data(query)
        
        migrated_count = 0
        for sql_item in sql_items:
            try:
                item = Item(
                    name=sql_item['name'] or "",
                    description=sql_item['description'],
                    price=float(sql_item['price'] or 0.0),
                    currency=sql_item['currency'] or "ETB",
                    category=sql_item['category'],
                    is_active=bool(sql_item['is_active']),
                    estimated_time=sql_item['estimated_time'],
                    created_at=sql_item['created_at'] or datetime.utcnow(),
                    updated_at=sql_item['updated_at'] or datetime.utcnow()
                )
                
                await item.insert()
                migrated_count += 1
                
            except Exception as e:
                logger.error(f"Error migrating item {sql_item.get('id')}: {str(e)}")
        
        logger.info(f"Migrated {migrated_count} items")

    async def migrate_orders(self):
        """Migrate orders from SQL to MongoDB"""
        logger.info("Starting order migration...")
        
        # First, get ID mappings for foreign keys
        user_mapping = await self.get_id_mapping("new_users", User)
        provider_mapping = await self.get_id_mapping("service_provider", ServiceProvider)
        driver_mapping = await self.get_id_mapping("drivers", Driver)
        
        query = """
        SELECT id, user_id, service_provider_id, driver_id, pickup_latitude,
               pickup_longitude, pickup_address, delivery_latitude, delivery_longitude,
               delivery_address, price_tag, subtotal, payment_option, delivery,
               delivery_km, delivery_charge, cash_on_delivery, note, status,
               service_type, created_at, updated_at, assigned_at, accepted_at,
               completed_at, estimated_pickup_time, estimated_completion_time,
               estimated_delivery_time, assignment_attempts, max_assignment_radius,
               special_instructions, priority_level
        FROM orders
        """
        
        sql_orders = self.fetch_sql_data(query)
        
        migrated_count = 0
        for sql_order in sql_orders:
            try:
                # Map SQL status and service type to MongoDB enums
                status_mapping = {
                    'pending': OrderStatus.PENDING,
                    'assigned': OrderStatus.ASSIGNED,
                    'accepted': OrderStatus.ACCEPTED,
                    'rejected': OrderStatus.REJECTED,
                    'in_progress': OrderStatus.IN_PROGRESS,
                    'ready_for_pickup': OrderStatus.READY_FOR_PICKUP,
                    'out_for_delivery': OrderStatus.OUT_FOR_DELIVERY,
                    'delivered': OrderStatus.DELIVERED,
                    'completed': OrderStatus.COMPLETED,
                    'cancelled': OrderStatus.CANCELLED
                }
                
                service_mapping = {
                    'By Hand Wash': ServiceType.BY_HAND_WASH,
                    'Premium Laundry Service': ServiceType.PREMIUM_LAUNDRY,
                    'Machine Wash': ServiceType.MACHINE_WASH
                }
                
                order = Order(
                    user_id=user_mapping.get(sql_order['user_id']),
                    service_provider_id=provider_mapping.get(sql_order['service_provider_id']) if sql_order['service_provider_id'] else None,
                    driver_id=driver_mapping.get(sql_order['driver_id']) if sql_order['driver_id'] else None,
                    pickup_latitude=sql_order['pickup_latitude'],
                    pickup_longitude=sql_order['pickup_longitude'],
                    pickup_address=sql_order['pickup_address'],
                    delivery_latitude=sql_order['delivery_latitude'],
                    delivery_longitude=sql_order['delivery_longitude'],
                    delivery_address=sql_order['delivery_address'],
                    price_tag=float(sql_order['price_tag'] or 0.0),
                    subtotal=float(sql_order['subtotal'] or 0.0),
                    payment_option=sql_order['payment_option'],
                    delivery=bool(sql_order['delivery']),
                    delivery_km=float(sql_order['delivery_km'] or 0.0),
                    delivery_charge=float(sql_order['delivery_charge'] or 0.0),
                    cash_on_delivery=bool(sql_order['cash_on_delivery']),
                    note=sql_order['note'],
                    status=status_mapping.get(sql_order['status'], OrderStatus.PENDING),
                    service_type=service_mapping.get(sql_order['service_type'], ServiceType.MACHINE_WASH),
                    created_at=sql_order['created_at'] or datetime.utcnow(),
                    updated_at=sql_order['updated_at'] or datetime.utcnow(),
                    assigned_at=sql_order['assigned_at'],
                    accepted_at=sql_order['accepted_at'],
                    completed_at=sql_order['completed_at'],
                    estimated_pickup_time=sql_order['estimated_pickup_time'],
                    estimated_completion_time=sql_order['estimated_completion_time'],
                    estimated_delivery_time=sql_order['estimated_delivery_time'],
                    assignment_attempts=sql_order['assignment_attempts'] or 0,
                    max_assignment_radius=float(sql_order['max_assignment_radius'] or 5.0),
                    special_instructions=sql_order['special_instructions'],
                    priority_level=sql_order['priority_level'] or 1
                )
                
                await order.insert()
                migrated_count += 1
                
            except Exception as e:
                logger.error(f"Error migrating order {sql_order.get('id')}: {str(e)}")
        
        logger.info(f"Migrated {migrated_count} orders")

    async def get_id_mapping(self, sql_table: str, mongo_model) -> Dict[int, str]:
        """Get mapping between SQL IDs and MongoDB ObjectIds"""
        mapping = {}
        
        # Get SQL IDs in order
        query = f"SELECT id FROM {sql_table} ORDER BY id"
        sql_records = self.fetch_sql_data(query)
        
        # Get MongoDB records in same order
        mongo_records = await mongo_model.find_all().to_list()
        
        for i, sql_record in enumerate(sql_records):
            if i < len(mongo_records):
                mapping[sql_record['id']] = mongo_records[i].id
        
        return mapping

    async def run_migration(self):
        """Run the complete migration process"""
        try:
            await self.connect_databases()
            
            logger.info("Starting SQL to MongoDB migration...")
            
            # SAFETY CHECK: Only clear data if explicitly requested
            clear_data = os.getenv("CLEAR_MONGODB_DATA", "false").lower() == "true"
            if clear_data:
                logger.warning("CLEARING EXISTING MONGODB DATA - This will delete all existing data!")
                logger.info("Clearing existing MongoDB collections...")
                await User.delete_all()
                await ServiceProvider.delete_all()
                await Driver.delete_all()
                await Item.delete_all()
                await Order.delete_all()
                await Payment.delete_all()
                await Notification.delete_all()
            else:
                logger.info("Preserving existing MongoDB data (set CLEAR_MONGODB_DATA=true to clear)")
            
            # Run migrations in dependency order
            await self.migrate_users()
            await self.migrate_service_providers()
            await self.migrate_drivers()
            await self.migrate_items()
            await self.migrate_orders()
            
            logger.info("Migration completed successfully!")
            
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            raise
        finally:
            await self.close_connections()

async def main():
    """Main function to run the migration"""
    migrator = SQLToMongoMigrator()
    await migrator.run_migration()

if __name__ == "__main__":
    asyncio.run(main()) 