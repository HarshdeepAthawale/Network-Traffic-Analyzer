"""
Configuration settings for the application
"""
from pathlib import Path
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

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

    # MongoDB Settings
    MONGODB_URI: str = "mongodb://localhost:27017/"
    MONGODB_DATABASE: str = "network_analyzer"
    MONGODB_PACKETS_COLLECTION: str = "packets"
    MONGODB_STATS_COLLECTION: str = "file_stats"
    MONGODB_FILES_COLLECTION: str = "files"

    # Cache Settings
    CACHE_TTL: int = 300  # 5 minutes

    # Processing Settings
    MAX_PACKETS_PER_PAGE: int = 100
    DEFAULT_PACKETS_PER_PAGE: int = 25

    model_config = SettingsConfigDict(
        env_prefix="NTA_",
        case_sensitive=False,
        env_file=env_path if env_path.exists() else None,
        env_file_encoding="utf-8",
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
