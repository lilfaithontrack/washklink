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
    "http://localhost:5173",         # Vite frontend (local dev)
    "https://washlink.et",         # Your main frontend domain
      # If frontend makes requests from here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(service_provider.router)

