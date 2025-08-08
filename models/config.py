from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # Database settings - make optional for backward compatibility
    DATABASE_URL: Optional[str] = "sqlite:///./washlink.db"
    MONGODB_URL: Optional[str] = "mongodb://localhost:27017"

    # AfroMessage settings
    AFRO_MESSAGE_API_KEY: str = ""
    AFRO_MESSAGE_SENDER_NAME: str = ""
    AFRO_MESSAGE_IDENTIFIER_ID: str = ""
    AFRO_MESSAGE_BASE_URL: str = "https://api.afromessage.com/api"
    
    AFRO_MESSAGE_CALLBACK: Optional[str] = ""
    AFRO_MESSAGE_SB: int = 0
    AFRO_MESSAGE_SA: int = 0
    AFRO_MESSAGE_TTL: int = 0
    AFRO_MESSAGE_LEN: int = 6
    AFRO_MESSAGE_T: int = 0

    # Google Auth fields as optional
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None

    # Allow extra fields to prevent validation errors
    model_config = {"extra": "allow"}

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
