from fastapi import FastAPI
from database import engine , Base 
from routes  import service_provider 
from routes import user_routes


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(service_provider.router)

app.include_router(user_routes.route)
