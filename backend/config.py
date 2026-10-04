from typing import List
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application Configuration using Pydantic Settings."""

    APP_NAME: str = "Sangyan Rakshak Backend"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite+aiosqlite:///./sangyan_rakshak.db"
    SECRET_KEY: str = "sangyan-rakshak-super-secret-key-2026"
    CORS_ORIGINS: List[str] = ["*"]

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
