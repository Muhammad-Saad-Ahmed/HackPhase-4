"""
Database session management and initialization.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from ..core.config import settings
from typing import AsyncGenerator
import asyncio


# Create the async engine
# For asyncpg, SSL must be configured via connect_args, not URL parameters
engine = create_async_engine(
    settings.database_url,
    connect_args={"ssl": "require"},
    pool_pre_ping=True
)

# Create the async session maker
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get the database session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """
    Initialize the database by creating all tables.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


def sync_init_db():
    """
    Synchronous version of init_db for use in scripts.
    """
    async def _init():
        await init_db()
    
    asyncio.run(_init())


def migrate():
    """
    Run database migrations.
    This is a placeholder function that would typically interface with Alembic.
    """
    # For now, we'll just initialize the database
    sync_init_db()
    print("Database initialized successfully")