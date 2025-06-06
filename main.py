from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes import service_provider
from routes import users_routes
from routes import booking
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

# Startup event to print status
@app.on_event("startup")
async def startup_event():
    pprint("🚀 FastAPI is running and connected to https://api.washlink.com")
