"""Shared fixtures for SupportFlow integration tests.

Two details matter and are easy to get wrong:

1. In-memory SQLite gives each *connection* its own empty database unless the
   engine reuses a single connection. `poolclass=StaticPool` does that, so the
   tables created here are the tables the API sees.
2. `TestClient(app)` only runs the app's startup handler when it is used as a
   context manager. The fixture below does that, so tests get a fully started app.
"""

from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from api.dependencies import get_database
from api.main import app
from database.models import Base


@pytest.fixture(scope="module")
def test_db() -> Generator[Session, None, None]:
    """One in-memory database shared by the test session and the app."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


@pytest.fixture(scope="module")
def client(test_db: Session) -> Generator[TestClient, None, None]:
    """Test client wired to the test database, with the app fully started."""

    def override_get_database() -> Generator[Session, None, None]:
        yield test_db

    app.dependency_overrides[get_database] = override_get_database
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def api_headers() -> dict:
    """Headers carrying a valid API key."""
    return {"X-API-Key": "demo-key-12345"}
