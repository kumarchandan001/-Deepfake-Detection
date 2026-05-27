import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
from ai_engine.utils.logger import setup_logger

logger = setup_logger("db_config")

# Production PostgreSQL target vs. local SQLite testing fallback
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite+aiosqlite:///C:/Users/Chandan Kumar/Desktop/Deepfake-Detection/forensics.db"
)

logger.info(f"Targeting asynchronous database connection profile: {DATABASE_URL}")

# Create async engine with robust pool bounds
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,  # Automatically tests connection health
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# SQLAlchemy declarative base mapper
Base = declarative_base()

async def init_database() -> None:
    """
    Programmatically creates all tables in database environment.
    """
    try:
        async with engine.begin() as conn:
            # Recreate all metadata schemas
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schemas compiled and verified successfully.")
    except Exception as e:
        logger.error(f"Failed to compile database relational metadata tables: {e}")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency injecting async db session profiles on routed scopes.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
