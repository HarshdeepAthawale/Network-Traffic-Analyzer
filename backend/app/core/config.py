"""
Configuration settings for the application
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from urllib.parse import urlparse
from typing import Optional
from dotenv import load_dotenv

# Load .env file from the backend directory
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    CORS_ORIGINS: str = "*"  # Comma-separated list of allowed origins (use * for all or specific domains)
    
    # Upload Settings
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024  # 500MB
    UPLOAD_CHUNK_SIZE: int = 1024 * 1024  # 1MB
    
    # Cloudinary Settings (Required)
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""
    CLOUDINARY_URL: Optional[str] = None  # Alternative: cloudinary://api_key:api_secret@cloud_name
    
    # Cache Settings
    CACHE_TTL: int = 300  # 5 minutes
    
    # Processing Settings
    MAX_PACKETS_PER_PAGE: int = 100
    DEFAULT_PACKETS_PER_PAGE: int = 25
    
    model_config = SettingsConfigDict(
        env_prefix="NTA_",
        case_sensitive=False,
        env_file=env_path if env_path.exists() else None,
        env_file_encoding="utf-8"
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Parse CLOUDINARY_URL if provided
        if self.CLOUDINARY_URL and not (self.CLOUDINARY_CLOUD_NAME and self.CLOUDINARY_API_KEY and self.CLOUDINARY_API_SECRET):
            try:
                parsed = urlparse(self.CLOUDINARY_URL)
                if parsed.scheme == "cloudinary" and parsed.hostname:
                    # Format: cloudinary://api_key:api_secret@cloud_name
                    self.CLOUDINARY_CLOUD_NAME = parsed.hostname
                    if parsed.username:
                        self.CLOUDINARY_API_KEY = parsed.username
                    if parsed.password:
                        self.CLOUDINARY_API_SECRET = parsed.password
            except Exception as e:
                pass


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
