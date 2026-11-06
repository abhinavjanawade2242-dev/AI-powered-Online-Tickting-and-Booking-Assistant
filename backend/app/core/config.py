from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Ticketing & Booking Assistant"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database Configuration
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ticketing_db"
    SYNC_DATABASE_URL: Optional[str] = "postgresql+psycopg2://postgres:postgres@localhost:5432/ticketing_db"
    DB_ECHO: bool = False

    # Redis Cache & Distributed Locks (Anti-Overbooking)
    REDIS_URL: str = "redis://localhost:6379/0"
    LOCK_EXPIRY_SECONDS: int = 10
    RESERVATION_HOLD_TTL_SECONDS: int = 600  # 10 minutes temporary hold

    # Celery Background Workers
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # AI & LLM Engine Configuration
    LLM_PROVIDER: str = "gemini"  # "gemini" | "openai" | "mock"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-pro"

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()

