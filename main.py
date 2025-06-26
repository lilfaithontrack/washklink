from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
from database import engine, Base, SessionLocal
from routes import service_provider, users_routes, booking
from pprint import pprint
from dotenv import load_dotenv
from controllers import item_controller 

load_dotenv()

# Create all DB tables
Base.metadata.create_all(bind=engine)

# FastAPI app instance
app = FastAPI()

# Allowed CORS origins
origins = [
    "http://localhost:5173",
    "https://washlinnk.com",
    "https://washlink.et",
    "https://admin.washlinnk.com",    
]

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["HEAD", "GET", "POST", "DELETE", "PUT"],
    allow_headers=["*"],
)

# Include routers
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
        pprint("✅ Connected to the database and FastAPI is running at https://api.washlinnk.com")
    except OperationalError as e:
        pprint("❌ Failed to connect to the database.")
        pprint(str(e))

# Root endpoint supporting GET and HEAD
@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return JSONResponse(content={"message": "API is up and running"})
