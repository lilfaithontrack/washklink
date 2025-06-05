from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str 
    AFRO_MESSAGE_API_KEY: str
    AFRO_MESSAGE_SENDER_NAME: str
    AFRO_MESSAGE_IDENTIFIER_ID: Optional[str] = None
    AFRO_MESSAGE_BASE_URL: str = "https://api.afromessage.com/api"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
