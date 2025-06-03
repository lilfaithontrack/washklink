# config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    AFRO MESSAGE_API_KEY: str
    AFRO MESSAGE_SENDER_NAME: str
    AFRO MESSAGE_IDENTIFIER_ID: Optional[str] = None # Or your default identifier
    AFRO MESSAGE_BASE_URL: str = "https://api.afromessage.com/api"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
