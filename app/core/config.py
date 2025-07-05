from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # AfroMessage SMS API
    AFRO_MESSAGE_API_KEY: str
    AFRO_MESSAGE_SENDER_NAME: str
    AFRO_MESSAGE_IDENTIFIER_ID: str
    AFRO_MESSAGE_BASE_URL: str = "https://api.afromessage.com/api"
    AFRO_MESSAGE_CALLBACK: Optional[str] = ""
    AFRO_MESSAGE_SB: int = 0
    AFRO_MESSAGE_SA: int = 0
    AFRO_MESSAGE_TTL: int = 0
    AFRO_MESSAGE_LEN: int = 6
    AFRO_MESSAGE_T: int = 0

    # Google Auth (Optional)
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    
    # JWT Settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Settings
    ALLOWED_ORIGINS: list = [
        "http://localhost:5173",
        "https://washlinnk.com",
        "https://washlink.et",
        "https://admin.washlinnk.com"
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()