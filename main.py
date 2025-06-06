from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from sqlalchemy import text  # ✅ Needed for raw SQL
from database import engine, Base, SessionLocal
from routes import service_provider, users_routes, booking
from pprint import pprint

# Create all DB tables
Base.metadata.create_all(bind=engine)

# FastAPI instance
app = FastAPI()

# CORS setup
origins = [
    "http://localhost:5173",
    "https://washlink.et",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PUT"],
    allow_headers=["*"],
)

# Routers
app.include_router(service_provider.router)
app.include_router(users_routes.router)
app.include_router(booking.router)

# Startup event to verify DB connection
@app.on_event("startup")
async def startup_event():
    try:
        db: Session = SessionLocal()
        db.execute(text("SELECT 1"))  # ✅ Check DB connection
        db.close()
        pprint("✅ Connected to the database and FastAPI is running at https://api.washlinnk.com")
    except OperationalError as e:
        pprint("❌ Failed to connect to the database.")
        pprint(str(e))

# <-- This is at the top level, NOT indented under except or any function
@app.get("/")
async def root():
    return {"message": "API is up and running"}
