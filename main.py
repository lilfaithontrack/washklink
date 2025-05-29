from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes import service_provider

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
    allow_origins=origins,  # <-- use the defined list
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE" ,"PUT"],
    allow_headers=["*"],
)

# Routers
app.include_router(service_provider.router)

