from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    CHAPA_SECRET_KEY: str = ""
    PROJECT_NAME: str = "WashLink API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    # MongoDB settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "washlink_db"
    # Legacy SQL database URL (for migration purposes)
    DATABASE_URL: str = "sqlite:///./washlink.db"
    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    # CORS settings
    CORS_ORIGINS: list = ["http://localhost:3000"]
    # JWT
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    # Admin user
    DEFAULT_ADMIN_EMAIL: str = "admin@washlink.com"
    DEFAULT_ADMIN_PHONE: str = "+251911000000"
    DEFAULT_ADMIN_PASSWORD: str = "admin123"
    # AfroMessage/OTP
    AFRO_MESSAGE_API_KEY: str = ""
    AFRO_MESSAGE_SENDER_NAME: str = ""
    AFRO_MESSAGE_IDENTIFIER_ID: str = ""
    AFRO_MESSAGE_BASE_URL: str = ""
    AFRO_MESSAGE_SB: str = ""
    AFRO_MESSAGE_SA: str = ""
    AFRO_MESSAGE_TTL: str = ""
    AFRO_MESSAGE_LEN: str = ""
    AFRO_MESSAGE_T: str = ""
    # Google Auth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    # Misc
    ALLOWED_ORIGINS: str = ""
    APP_NAME: str = ""
    APP_VERSION: str = ""
    DEBUG: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()