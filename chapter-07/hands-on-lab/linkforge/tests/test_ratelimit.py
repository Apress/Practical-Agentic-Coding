"""
LinkForge - Rate Limiting Tests
Tests for the free-tier daily quota (RATE_LIMIT_PER_DAY, default 100).

Uses an in-memory Redis stand-in; no live Redis is needed.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from src.ratelimit import DailyRateLimiter, get_rate_limiter


class FakeRedis:
    """Minimal in-memory stand-in for redis.asyncio.Redis."""

    def __init__(self):
        self.counters: dict[str, int] = {}
        self.expirations: dict[str, int] = {}

    async def incr(self, key: str) -> int:
        self.counters[key] = self.counters.get(key, 0) + 1
        return self.counters[key]

    async def expire(self, key: str, seconds: int) -> bool:
        self.expirations[key] = seconds
        return True


class TestDailyRateLimiter:
    """Tests for the day-keyed INCR + EXPIRE quota logic."""

    @pytest.mark.asyncio
    async def test_allows_requests_up_to_the_daily_limit(self):
        """Every request within the quota is allowed."""
        limiter = DailyRateLimiter(FakeRedis(), limit=3)

        results = [await limiter.allow("key:abc") for _ in range(3)]

        assert results == [True, True, True]

    @pytest.mark.asyncio
    async def test_blocks_over_limit_per_identity_with_expiring_counter(self):
        """Requests past the quota are blocked, per identity, and the
        day-keyed counter carries an expiry so quotas reset."""
        fake = FakeRedis()
        limiter = DailyRateLimiter(fake, limit=2)

        assert await limiter.allow("ip:1.2.3.4") is True
        assert await limiter.allow("ip:1.2.3.4") is True
        assert await limiter.allow("ip:1.2.3.4") is False

        # A different caller still has their own quota
        assert await limiter.allow("key:other-user") is True

        # Counters are keyed by identity and day, and expire on their own
        assert len(fake.counters) == 2
        assert all(":ip:1.2.3.4:" in key or ":key:other-user:" in key
                   for key in fake.counters)
        assert all(ttl > 0 for ttl in fake.expirations.values())


class TestRateLimitedEndpoint:
    """Tests for the quota wired into POST /api/v1/links."""

    @pytest.mark.asyncio
    async def test_endpoint_returns_429_once_quota_is_spent(self):
        """The shortening endpoint returns 429 past the daily limit."""
        from src.main import app, get_shortening_service
        from src.models import Link

        # Service layer mocked out: this test isolates the limiter
        created = Link(
            user_id=1,
            original_url="https://example.com/page",
            short_code="abc123",
            created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        service = MagicMock()
        service.create_short_url = AsyncMock(return_value=created)

        limiter = DailyRateLimiter(FakeRedis(), limit=1)
        app.dependency_overrides[get_shortening_service] = lambda: service
        app.dependency_overrides[get_rate_limiter] = lambda: limiter

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                payload = {"original_url": "https://example.com/page"}
                first = await client.post("/api/v1/links", json=payload)
                second = await client.post("/api/v1/links", json=payload)
        finally:
            app.dependency_overrides.pop(get_shortening_service, None)
            app.dependency_overrides.pop(get_rate_limiter, None)

        assert first.status_code == 201
        assert second.status_code == 429
        assert "Daily limit" in second.json()["detail"]
