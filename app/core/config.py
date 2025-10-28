# app/core/config.py - Configuration settings for the application.

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENV: str = "dev"
    APP_PORT: int = 8000
    LLM_PROVIDER: str = "mock"
    GOOGLE_API_KEY: str | None = None
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_REGION: str = "us-east-1"
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/db"

    # Internal Microservice URLs
    BILLING_SERVICE_URL: Optional[str] = None
    CHAT_SERVICE_URL: Optional[str] = None
    PAYMENT_SERVICE_URL: Optional[str] = None
    PROJECT_SERVICE_URL: Optional[str] = None
    USER_SERVICE_URL: Optional[str] = None

@lru_cache()
def get_settings():
    return Settings()
