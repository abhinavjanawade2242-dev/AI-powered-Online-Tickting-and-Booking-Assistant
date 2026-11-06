from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Create async engine for SQLAlchemy 2.0
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    future=True,
    pool_pre_ping=True,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# SQLAlchemy declarative base for ORM models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides an asynchronous SQLAlchemy session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables asynchronously (creates all models and auto-migrates missing columns)."""
    from sqlalchemy import text

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # Resilient SQLite column migration check for local environments
        if "sqlite" in settings.DATABASE_URL:
            res = await conn.execute(text("PRAGMA table_info(users)"))
            cols = [row[1] for row in res.fetchall()]
            if "password_hash" not in cols:
                await conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)"))
            if "role" not in cols:
                await conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'customer'"))
            if "preferred_language" not in cols:
                await conn.execute(text("ALTER TABLE users ADD COLUMN preferred_language VARCHAR(10) DEFAULT 'en'"))
            if "updated_at" not in cols:
                await conn.execute(text("ALTER TABLE users ADD COLUMN updated_at DATETIME"))

