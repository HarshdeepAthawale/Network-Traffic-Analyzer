"""
Configuration settings for the application
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    CORS_ORIGINS: str = "*"  # Comma-separated list of allowed origins
    
    # Upload Settings
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    UPLOAD_CHUNK_SIZE: int = 1024 * 1024  # 1MB
    
    # Storage Settings
    STORAGE_TYPE: str = "memory"  # memory or sqlite
    DATABASE_URL: str = "sqlite:///./network_analyzer.db"
    
    # Cache Settings
    CACHE_TTL: int = 300  # 5 minutes
    
    # Processing Settings
    MAX_PACKETS_PER_PAGE: int = 100
    DEFAULT_PACKETS_PER_PAGE: int = 25
    
    model_config = {
        "env_prefix": "NTA_",
        "case_sensitive": False
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
