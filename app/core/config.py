# app/core/config.py - Configuration settings for the application.

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional, Dict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Application Settings
    ENV: str = "dev"
    APP_PORT: int = 8000

    # LLM Provider Settings
    LLM_PROVIDER: str = "mock"  # "openai", "gemini", "mock"
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"

    # Embedding Model Settings
    EMBEDDING_MODEL: str = "text-embedding-3-large"
    EMBEDDING_VERSION: str = "1.0"
    EMBEDDING_DIMENSIONS: int = 1536  # OpenAI: 1536, Gemini: 768

    # Database Settings
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/db"

    # Internal Microservice URLs
    BILLING_SERVICE_URL: Optional[str] = None
    CHAT_SERVICE_URL: Optional[str] = None
    PAYMENT_SERVICE_URL: Optional[str] = None
    PROJECT_SERVICE_URL: Optional[str] = None
    USER_SERVICE_URL: Optional[str] = None

    # Recommendation Settings - Feature Flags
    AI_RECOMMENDATIONS_ENABLED: bool = True
    FREELANCER_RECOMMENDATIONS_ENABLED: bool = True
    PROJECT_RECOMMENDATIONS_ENABLED: bool = True
    COLD_START_BOOST_ENABLED: bool = True
    WEIGHT_ADJUSTMENTS_ENABLED: bool = True

    # Recommendation Settings - Score Thresholds
    MINIMUM_SCORE: float = 0.3
    HIGH_CONFIDENCE_THRESHOLD: float = 0.8
    MEDIUM_CONFIDENCE_THRESHOLD: float = 0.6

    # Freelancer Recommendation Weights
    FREELANCER_BIO_SIMILARITY_WEIGHT: float = 0.20
    FREELANCER_PAST_PROJECT_SIMILARITY_WEIGHT: float = 0.20
    FREELANCER_SKILL_OVERLAP_WEIGHT: float = 0.20
    FREELANCER_SUCCESS_RATE_WEIGHT: float = 0.15
    FREELANCER_CLIENT_SATISFACTION_WEIGHT: float = 0.15
    FREELANCER_COMMUNICATION_SCORE_WEIGHT: float = 0.10

    # Project Recommendation Weights
    PROJECT_SIMILARITY_WEIGHT: float = 0.50
    PROJECT_SKILL_OVERLAP_WEIGHT: float = 0.25
    PROJECT_BIO_SIMILARITY_WEIGHT: float = 0.25

    # Cold Start Settings
    COLD_START_BOOST_AMOUNT: float = 0.05
    NEW_FREELANCER_PROJECT_THRESHOLD: int = 3
    LOW_FEEDBACK_THRESHOLD: int = 3

    # Default Metrics for New Freelancers
    DEFAULT_SUCCESS_RATE: float = 0.7
    DEFAULT_CLIENT_SATISFACTION: float = 0.75
    DEFAULT_COMMUNICATION_SCORE: float = 0.7

    # Data Quality Thresholds
    MIN_BIO_LENGTH: int = 100
    MIN_PROJECT_DESCRIPTION_LENGTH: int = 150
    MIN_SKILLS_COUNT: int = 3
    MIN_PROJECT_SKILLS_COUNT: int = 2
    MINIMUM_PROFILE_COMPLETENESS: float = 0.6

@lru_cache()
def get_settings():
    return Settings()
