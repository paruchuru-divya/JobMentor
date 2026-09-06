import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "JobMentor AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # Gemini AI
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    # Google Cloud & Firestore
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    FIRESTORE_DATABASE: str = "(default)"
    USE_FIRESTORE_EMULATOR: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 15
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

# Ensure uploads directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
