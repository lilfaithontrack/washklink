from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
from app.core.database import engine, SessionLocal
from app.core.config import get_settings
from app.db.base import Base
from app.api.v1.routers import api_router
from app.services.background_tasks import background_service
import asyncio

# Import your existing routes to maintain backward compatibility
from routes import service_provider, users_routes, booking
from controllers import item_controller

settings = get_settings()

# Create all DB tables
Base.metadata.create_all(bind=engine)

# FastAPI app instance
app = FastAPI(
    title="Laundry App API",
    description="A comprehensive laundry service management API with role-based access, live tracking, and automated assignment",
    version="2.0.0"
)

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["HEAD", "GET", "POST", "DELETE", "PUT"],
    allow_headers=["*"],
)

# Include new organized API routes (v1)
app.include_router(api_router, prefix="/api/v1")

# Include existing routes for backward compatibility
app.include_router(service_provider.router)
app.include_router(users_routes.router)
app.include_router(booking.router)
app.include_router(item_controller.router, prefix="/api", tags=["Item Price"])

# Startup event to verify DB connection and start background tasks
@app.on_event("startup")
async def startup_event():
    try:
        db: Session = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ Connected to the database and FastAPI is running")
        
        # Start background tasks
        asyncio.create_task(background_service.start_background_tasks())
        print("✅ Background tasks started")
        
        # Create default admin user if none exists
        await create_default_admin()
        
    except OperationalError as e:
        print("❌ Failed to connect to the database.")
        print(str(e))

# Shutdown event to stop background tasks
@app.on_event("shutdown")
async def shutdown_event():
    await background_service.stop_background_tasks()
    print("✅ Background tasks stopped")

async def create_default_admin():
    """Create default admin user if no admin exists"""
    try:
        from app.crud.user import user as user_crud
        from app.schemas.user import AdminUserCreate, UserRole
        from app.core.security import hash_password
        
        db = SessionLocal()
        
        # Check if any admin users exist
        admin_users = user_crud.get_users_by_role(db, role=UserRole.ADMIN)
        
        if not admin_users:
            # Create default admin
            default_admin = AdminUserCreate(
                full_name="System Administrator",
                phone_number="+251911000000",
                email="admin@washlink.com",
                role=UserRole.ADMIN,
                password="admin123"  # Change this in production!
            )
            
            hashed_password = hash_password(default_admin.password)
            admin_user = user_crud.create_admin_user(db, default_admin, hashed_password)
            
            print(f"✅ Default admin user created: {admin_user.email}")
            print("⚠️  Default password is 'admin123' - Please change it immediately!")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Failed to create default admin user: {e}")

# Root endpoint supporting GET and HEAD
@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return JSONResponse(content={
        "message": "Laundry App API with Role-Based Access & Live Tracking is up and running",
        "version": "2.0.0",
        "features": [
            "role_based_access",
            "live_tracking", 
            "auto_assignment",
            "phone_authentication",
            "admin_management"
        ]
    })

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "version": "2.0.0", 
        "features": [
            "role_based_access",
            "live_tracking", 
            "auto_assignment",
            "phone_authentication",
            "admin_management"
        ]
    }

# API Info endpoint
@app.get("/api/info")
async def api_info():
    return {
        "title": "Laundry App API",
        "version": "2.0.0",
        "description": "A comprehensive laundry service management API",
        "authentication": {
            "regular_users": "Phone + OTP",
            "admin_manager": "Email + Password"
        },
        "roles": ["USER", "MANAGER", "ADMIN"],
        "endpoints": {
            "v1": "/api/v1/",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }