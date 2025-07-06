from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional, List

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

    # Payment Gateway Settings
    CHAPA_SECRET_KEY: Optional[str] = "your-chapa-secret-key"
    CHAPA_PUBLIC_KEY: Optional[str] = "your-chapa-public-key"
    TELEBIRR_APP_ID: Optional[str] = "your-telebirr-app-id"
    TELEBIRR_APP_KEY: Optional[str] = "your-telebirr-app-key"
    TELEBIRR_BASE_URL: Optional[str] = "https://196.188.120.3:38443/apiaccess"

    # Google Auth (Optional)
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    
    # JWT Settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours for better UX
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://washlinnk.com",
        "https://washlink.et",
        "https://admin.washlinnk.com",
        "https://app.washlink.et"
    ]
    
    # App Settings
    APP_NAME: str = "Laundry App API"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    
    # Default Admin Settings (for initial setup)
    DEFAULT_ADMIN_EMAIL: str = "admin@washlink.com"
    DEFAULT_ADMIN_PHONE: str = "+251911000000"
    DEFAULT_ADMIN_PASSWORD: str = "admin123"  # Change in production!

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()