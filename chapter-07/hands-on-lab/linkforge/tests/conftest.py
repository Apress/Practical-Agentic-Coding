"""
LinkForge - Pytest Fixtures
Shared test fixtures and mock configurations.
"""

from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.main import app, get_shortening_service
from src.models import Base, User, Link
from src.database import ensure_demo_user, get_db
from src.shortener import ShorteningService
from src.cache import RedisCache
from src.analytics import AnalyticsService


@pytest_asyncio.fixture(scope="function")
async def async_engine(tmp_path):
    """Create a test database engine.

    Uses a file-backed SQLite database in pytest's per-test tmp_path
    rather than ':memory:' so that every session can open its own
    connection to the same database. The concurrency tests open one
    session per task, which a single shared in-memory connection
    cannot support.
    """
    db_path = (tmp_path / "test.db").as_posix()
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")

    # SQLite ignores foreign keys unless asked; enforce them the way
    # PostgreSQL does, so a link that points at a missing user fails here too.
    @event.listens_for(engine.sync_engine, "connect")
    def _enforce_foreign_keys(dbapi_connection, _record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_sessionmaker(engine, class_=AsyncSession)() as session:
        await ensure_demo_user(session)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session_factory(
    async_engine,
) -> async_sessionmaker[AsyncSession]:
    """Create a session factory bound to the test engine.

    Tests that need several independent sessions (one per concurrent
    task, because an AsyncSession must never be shared across tasks)
    call the factory directly. Everything else should use the
    ready-made db_session fixture.
    """
    return async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest_asyncio.fixture(scope="function")
async def db_session(
    db_session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with db_session_factory() as session:
        yield session


@pytest.fixture
def mock_redis_cache() -> MagicMock:
    """Create a mock Redis cache."""
    cache = MagicMock(spec=RedisCache)

    # Configure async mocks
    cache.get_link = AsyncMock(return_value=None)
    cache.set_link = AsyncMock(return_value=True)
    cache.delete_link = AsyncMock(return_value=True)
    cache.increment_clicks = AsyncMock(return_value=1)
    cache.get_clicks = AsyncMock(return_value=0)
    cache.push_event = AsyncMock(return_value=True)
    cache.health_check = AsyncMock(return_value=True)

    return cache


@pytest.fixture
def mock_analytics_service(mock_redis_cache) -> AnalyticsService:
    """Create a mock analytics service."""
    service = AnalyticsService(cache=mock_redis_cache)
    return service


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user in the database."""
    user = User(
        username="testuser",
        email="test@example.com",
        api_key="test-api-key-12345",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_link(db_session: AsyncSession, test_user: User) -> Link:
    """Create a test link in the database."""
    link = Link(
        user_id=test_user.id,
        original_url="https://www.example.com/very/long/url",
        short_code="abc123",
    )
    db_session.add(link)
    await db_session.commit()
    await db_session.refresh(link)
    return link


@pytest_asyncio.fixture
async def shortening_service(
    db_session: AsyncSession,
    mock_redis_cache: MagicMock,
    mock_analytics_service: AnalyticsService,
) -> ShorteningService:
    """Create a shortening service with mocked dependencies."""
    return ShorteningService(
        db=db_session,
        cache=mock_redis_cache,
        analytics=mock_analytics_service,
    )


@pytest_asyncio.fixture
async def async_client(
    db_session: AsyncSession,
    mock_redis_cache: MagicMock,
    mock_analytics_service: AnalyticsService,
) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client with mocked dependencies.

    Uses httpx.ASGITransport to call the FastAPI app in-process;
    httpx 0.28 removed the AsyncClient(app=...) shortcut.
    """

    async def override_get_db():
        yield db_session

    async def override_get_service():
        return ShorteningService(
            db=db_session,
            cache=mock_redis_cache,
            analytics=mock_analytics_service,
        )

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_shortening_service] = override_get_service

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


# Sample test data
@pytest.fixture
def valid_url() -> str:
    """Return a valid URL for testing."""
    return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
