import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.routers import api_router
from routes.users_routes import router as legacy_users_router
from database import init_db, close_mongo_connection
from core.config import settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Event handlers for database connection
@app.on_event("startup")
async def startup_event():
    """Initialize MongoDB connection on startup"""
    await init_db()
    logger.info("MongoDB connection initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Close MongoDB connection on shutdown"""
    await close_mongo_connection()
    logger.info("MongoDB connection closed")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Use dynamic origins from settings
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include API router with prefix
app.include_router(api_router, prefix=settings.API_V1_STR)

# Include legacy routes for backward compatibility
app.include_router(legacy_users_router, prefix="", tags=["legacy"])

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )