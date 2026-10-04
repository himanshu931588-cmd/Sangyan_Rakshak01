import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from backend.database.models import Base

# Default database connection string (SQLite fallback)
DEFAULT_SQLITE_URL = "sqlite+aiosqlite:///./sangyan_rakshak.db"

# Retrieve DATABASE_URL from environment or fallback to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL)

# Configure engine kwargs depending on dialect
engine_kwargs = {
    "echo": os.getenv("DB_ECHO", "False").lower() in ("true", "1"),
    "future": True,
}

if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

# Initialize Async Engine
engine: AsyncEngine = create_async_engine(DATABASE_URL, **engine_kwargs)

# Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency generator for obtaining an async database session.
    Yields an AsyncSession instance and ensures proper cleanup.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """
    Creates all database tables defined in models.py if they do not already exist.
    Primary use case: testing, local SQLite bootstrapping, and development environments.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db() -> None:
    """
    Drops all database tables.
    Primary use case: test tear-down.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
