"""
LinkForge - Database Configuration
SQLAlchemy async session setup and dependency injection.
"""

import os
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .models import Base, User

# Until authentication exists, create_short_url assigns every link to this
# user (see the TODO in main.py). links.user_id is a non-null foreign key, so
# the user has to exist or every insert fails on PostgreSQL.
DEMO_USER_ID = 1

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/linkforge"
)

# Create async engine with connection pooling
engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("DEBUG", "false").lower() == "true",
    pool_size=20,        # persistent connections held by the pool
    max_overflow=10,     # extra connections allowed under burst load
    pool_pre_ping=True,  # validate connections before handing them out
)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db() -> None:
    """
    Initialize the database by creating all tables.

    This should be called once during application startup.
    In production, use Alembic migrations instead.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_maker() as session:
        await ensure_demo_user(session)


async def ensure_demo_user(session: AsyncSession) -> None:
    """Create the placeholder link owner (DEMO_USER_ID) if it is missing."""
    if await session.get(User, DEMO_USER_ID) is not None:
        return
    session.add(User(id=DEMO_USER_ID, username="demo", email="demo@example.com"))
    await session.commit()
    if session.bind.dialect.name == "postgresql":
        # An explicit id does not advance the SERIAL sequence; move it past
        # the demo user so the next user insert does not collide with it.
        await session.execute(
            text(
                "SELECT setval(pg_get_serial_sequence('users', 'id'), "
                "(SELECT MAX(id) FROM users))"
            )
        )
        await session.commit()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injection for database sessions.

    Yields:
        AsyncSession: An async database session

    Example:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_db() -> None:
    """
    Close all database connections.

    Call this during application shutdown.
    """
    await engine.dispose()
