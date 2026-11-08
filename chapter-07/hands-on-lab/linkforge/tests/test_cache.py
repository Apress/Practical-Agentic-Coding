"""
LinkForge - Cache Tests
Tests for the Redis caching layer (singleton, retries, key handling).
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError

from src.cache import RedisCache


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset RedisCache singleton state around every test.

    RedisCache keeps its instance and client as class attributes, so
    without a reset one test's fake client would leak into the next.
    """
    saved_instance = RedisCache._instance
    saved_client = RedisCache._client
    RedisCache._instance = None
    RedisCache._client = None
    yield
    RedisCache._instance = saved_instance
    RedisCache._client = saved_client


@pytest.fixture
def mock_client() -> MagicMock:
    """Create a mock Redis client with async operations."""
    client = MagicMock()
    client.ping = AsyncMock(return_value=True)
    client.get = AsyncMock(return_value=None)
    client.set = AsyncMock(return_value=True)
    client.delete = AsyncMock(return_value=1)
    client.incr = AsyncMock(return_value=1)
    client.lpush = AsyncMock(return_value=1)
    client.close = AsyncMock()
    return client


@pytest.fixture
def cache(mock_client) -> RedisCache:
    """Create a RedisCache wired to the mock client."""
    instance = RedisCache()
    RedisCache._client = mock_client
    return instance


class TestSingleton:
    """Tests for the singleton pattern and client initialization."""

    def test_new_returns_same_instance(self):
        """Test that repeated construction yields one instance."""
        first = RedisCache()
        second = RedisCache()
        assert first is second

    @pytest.mark.asyncio
    async def test_get_instance_initializes_client(self, mock_client):
        """Test that get_instance creates and pings the client."""
        with patch(
            "src.cache.redis.from_url", return_value=mock_client
        ) as from_url:
            instance = await RedisCache.get_instance()

        from_url.assert_called_once()
        mock_client.ping.assert_awaited_once()
        assert instance is RedisCache()
        assert RedisCache._client is mock_client

    @pytest.mark.asyncio
    async def test_get_instance_reuses_existing_client(self, cache, mock_client):
        """Test that an already-initialized client is not recreated."""
        with patch("src.cache.redis.from_url") as from_url:
            instance = await RedisCache.get_instance()

        from_url.assert_not_called()
        assert instance is cache
        assert RedisCache._client is mock_client

    @pytest.mark.asyncio
    async def test_initialize_survives_connection_error(self, mock_client):
        """Test that a failed ping does not break initialization."""
        mock_client.ping.side_effect = RedisConnectionError("refused")

        with patch("src.cache.redis.from_url", return_value=mock_client):
            instance = await RedisCache.get_instance()

        # Cache stays usable; operations will be bypassed or retried
        assert instance is RedisCache()
        assert RedisCache._client is mock_client


class TestRetryLogic:
    """Tests for exponential backoff retry around Redis operations."""

    @pytest.mark.asyncio
    async def test_no_client_returns_none(self):
        """Test that operations short-circuit when Redis is absent."""
        instance = RedisCache()
        result = await instance.get_link("abc123")
        assert result is None

    @pytest.mark.asyncio
    async def test_retry_then_success(self, cache, mock_client):
        """Test that transient connection errors are retried."""
        mock_client.get.side_effect = [
            RedisConnectionError("down"),
            RedisConnectionError("still down"),
            "https://example.com",
        ]

        result = await cache._execute_with_retry(
            "get", "link:abc123", initial_backoff=0.01
        )

        assert result == "https://example.com"
        assert mock_client.get.call_count == 3

    @pytest.mark.asyncio
    async def test_retry_exhausted_returns_none(self, cache, mock_client):
        """Test that persistent failures give up after max retries."""
        mock_client.get.side_effect = RedisConnectionError("down")

        result = await cache._execute_with_retry(
            "get", "link:abc123", max_retries=3, initial_backoff=0.01
        )

        assert result is None
        assert mock_client.get.call_count == 3

    @pytest.mark.asyncio
    async def test_timeout_error_is_retried(self, cache, mock_client):
        """Test that timeouts are treated as retryable."""
        mock_client.get.side_effect = [RedisTimeoutError("slow"), "cached"]

        result = await cache._execute_with_retry(
            "get", "link:abc123", initial_backoff=0.01
        )

        assert result == "cached"
        assert mock_client.get.call_count == 2


class TestLinkOperations:
    """Tests for link cache get/set/delete."""

    @pytest.mark.asyncio
    async def test_set_link_uses_prefixed_key_and_default_ttl(
        self, cache, mock_client
    ):
        """Test that set_link namespaces the key and applies the TTL."""
        result = await cache.set_link("abc123", "https://example.com")

        assert result is True
        mock_client.set.assert_awaited_once_with(
            "link:abc123", "https://example.com", ex=3600
        )

    @pytest.mark.asyncio
    async def test_set_link_custom_ttl(self, cache, mock_client):
        """Test that an explicit TTL overrides the default."""
        await cache.set_link("abc123", "https://example.com", ttl=60)

        mock_client.set.assert_awaited_once_with(
            "link:abc123", "https://example.com", ex=60
        )

    @pytest.mark.asyncio
    async def test_set_link_without_client_returns_false(self):
        """Test that set_link reports failure when Redis is absent."""
        instance = RedisCache()
        result = await instance.set_link("abc123", "https://example.com")
        assert result is False

    @pytest.mark.asyncio
    async def test_get_link_returns_cached_url(self, cache, mock_client):
        """Test cache hit returns the original URL."""
        mock_client.get.return_value = "https://example.com"

        result = await cache.get_link("abc123")

        assert result == "https://example.com"
        mock_client.get.assert_awaited_once_with("link:abc123")

    @pytest.mark.asyncio
    async def test_get_link_miss_returns_none(self, cache, mock_client):
        """Test cache miss returns None."""
        mock_client.get.return_value = None
        assert await cache.get_link("missing") is None

    @pytest.mark.asyncio
    async def test_delete_link_removes_key(self, cache, mock_client):
        """Test that deleting an existing key reports success."""
        mock_client.delete.return_value = 1

        result = await cache.delete_link("abc123")

        assert result is True
        mock_client.delete.assert_awaited_once_with("link:abc123")

    @pytest.mark.asyncio
    async def test_delete_link_missing_key_returns_false(
        self, cache, mock_client
    ):
        """Test that deleting a missing key reports failure."""
        mock_client.delete.return_value = 0
        assert await cache.delete_link("missing") is False


class TestClickCounters:
    """Tests for the click counter helpers."""

    @pytest.mark.asyncio
    async def test_increment_clicks_returns_new_count(self, cache, mock_client):
        """Test that increment_clicks returns the updated count."""
        mock_client.incr.return_value = 5

        result = await cache.increment_clicks("abc123")

        assert result == 5
        mock_client.incr.assert_awaited_once_with("clicks:abc123")

    @pytest.mark.asyncio
    async def test_increment_clicks_failure_returns_zero(self):
        """Test that increment falls back to zero without Redis."""
        instance = RedisCache()
        assert await instance.increment_clicks("abc123") == 0

    @pytest.mark.asyncio
    async def test_get_clicks_parses_count(self, cache, mock_client):
        """Test that a stored count string is returned as an int."""
        mock_client.get.return_value = "7"

        result = await cache.get_clicks("abc123")

        assert result == 7
        mock_client.get.assert_awaited_once_with("clicks:abc123")

    @pytest.mark.asyncio
    async def test_get_clicks_missing_returns_zero(self, cache, mock_client):
        """Test that a missing counter reads as zero."""
        mock_client.get.return_value = None
        assert await cache.get_clicks("abc123") == 0


class TestEventsAndHealth:
    """Tests for event streaming and health checks."""

    @pytest.mark.asyncio
    async def test_push_event_uses_stream_key(self, cache, mock_client):
        """Test that events land on the analytics stream."""
        result = await cache.push_event('{"short_code": "abc123"}')

        assert result is True
        mock_client.lpush.assert_awaited_once_with(
            "analytics:events", '{"short_code": "abc123"}'
        )

    @pytest.mark.asyncio
    async def test_push_event_without_client_returns_false(self):
        """Test that push_event reports failure without Redis."""
        instance = RedisCache()
        assert await instance.push_event("{}") is False

    @pytest.mark.asyncio
    async def test_health_check_true_response(self, cache, mock_client):
        """Test health check with a boolean PING response."""
        mock_client.ping.return_value = True
        assert await cache.health_check() is True

    @pytest.mark.asyncio
    async def test_health_check_pong_response(self, cache, mock_client):
        """Test health check with a decoded string PONG response."""
        mock_client.ping.return_value = "PONG"
        assert await cache.health_check() is True

    @pytest.mark.asyncio
    async def test_health_check_without_client_returns_false(self):
        """Test health check reports unhealthy without Redis."""
        instance = RedisCache()
        assert await instance.health_check() is False


class TestClose:
    """Tests for connection shutdown."""

    @pytest.mark.asyncio
    async def test_close_shuts_down_client(self, cache, mock_client):
        """Test that close closes the client and clears the reference."""
        await cache.close()

        mock_client.close.assert_awaited_once()
        assert RedisCache._client is None

    @pytest.mark.asyncio
    async def test_close_without_client_is_noop(self):
        """Test that close is safe when no client exists."""
        instance = RedisCache()
        await instance.close()
        assert RedisCache._client is None
