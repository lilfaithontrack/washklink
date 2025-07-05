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

# Import your existing routes to maintain backward compatibility
from routes import service_provider, users_routes, booking
from controllers import item_controller

settings = get_settings()

# Create all DB tables
Base.metadata.create_all(bind=engine)

# FastAPI app instance
app = FastAPI(
    title="Laundry App API",
    description="A comprehensive laundry service management API",
    version="1.0.0"
)

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["HEAD", "GET", "POST", "DELETE", "PUT"],
    allow_headers=["*"],
)

# Include new organized API routes
app.include_router(api_router, prefix="/api/v1")

# Include existing routes for backward compatibility
app.include_router(service_provider.router)
app.include_router(users_routes.router)
app.include_router(booking.router)
app.include_router(item_controller.router, prefix="/api", tags=["Item Price"])

# Startup event to verify DB connection
@app.on_event("startup")
async def startup_event():
    try:
        db: Session = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ Connected to the database and FastAPI is running")
    except OperationalError as e:
        print("❌ Failed to connect to the database.")
        print(str(e))

# Root endpoint supporting GET and HEAD
@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return JSONResponse(content={"message": "Laundry App API is up and running"})

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}