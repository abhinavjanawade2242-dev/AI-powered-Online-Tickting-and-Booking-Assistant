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

    # Business Rules & Pricing Engine Defaults (Configurable by Admin)
    MAX_TICKETS_PER_BOOKING: int = 6       # Maximum tickets allowed in a single reservation
    HOLD_DURATION_MINUTES: int = 10        # Configurable reservation hold duration in minutes
    CANCELLATION_WINDOW_HOURS: int = 24    # 24-hour advance cancellation rule
    DEFAULT_CURRENCY: str = "INR"          # Mandatory platform currency
    GROUP_DISCOUNT_THRESHOLD: int = 4      # Quantity threshold for bulk/team group discount
    GROUP_DISCOUNT_PERCENT: float = 10.0   # 10% discount for group orders (>= 4 tickets)
    ENABLE_CONVENIENCE_FEE: bool = False   # Set True to charge platform convenience fee
    PLATFORM_FEE_AMOUNT: float = 0.00      # Zero convenience fee for student events
    GST_RATE_PERCENT: float = 0.0          # GST percentage (0% for educational/campus events)

    # Celery Background Workers
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # AI & LLM Engine Configuration
    LLM_PROVIDER: str = "gemini"  # "gemini" | "openai" | "mock"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-pro"

    # Authentication & JWT Security
    SECRET_KEY: str = "technovate-super-secret-jwt-key-ps07-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Meta WhatsApp Cloud API Integration
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = None
    WHATSAPP_ACCESS_TOKEN: Optional[str] = None
    WHATSAPP_VERIFY_TOKEN: str = "technovate_whatsapp_verify_token_2026"
    WHATSAPP_APP_SECRET: Optional[str] = None
    WHATSAPP_API_VERSION: str = "v21.0"

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

