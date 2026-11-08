"""
LinkForge - Redis Caching Layer
Singleton pattern cache implementation with async operations.
"""

import asyncio
import os
from typing import Optional

import redis.asyncio as redis
from redis.exceptions import ConnectionError, TimeoutError


class RedisCache:
    """
    Redis caching layer with singleton pattern.

    Provides async caching for URL lookups with configurable TTL
    and automatic retry logic for resilience.

    Attributes:
        _instance: Singleton instance
        _client: Redis async client
        _default_ttl: Default TTL in seconds (1 hour)
    """

    _instance: Optional["RedisCache"] = None
    _client: Optional[redis.Redis] = None
    _default_ttl: int = 3600  # 1 hour

    def __new__(cls) -> "RedisCache":
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    async def get_instance(cls) -> "RedisCache":
        """
        Get or create the singleton cache instance.

        Returns:
            RedisCache: The singleton instance with initialized client
        """
        instance = cls()
        if cls._client is None:
            await instance._initialize()
        return instance

    async def _initialize(self) -> None:
        """Initialize the Redis client connection."""
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

        RedisCache._client = redis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )

        # Test connection
        try:
            await self._client.ping()
        except (ConnectionError, TimeoutError) as e:
            print(f"Redis connection warning: {e}")
            # Don't fail initialization, cache will be bypassed if unavailable

    async def _execute_with_retry(
        self,
        operation: str,
        *args,
        max_retries: int = 3,
        initial_backoff: float = 0.1,
        **kwargs,
    ):
        """
        Execute a Redis operation with exponential backoff retry.

        Args:
            operation: Name of the Redis operation to call
            *args: Positional arguments for the operation
            max_retries: Maximum number of retry attempts
            initial_backoff: Initial backoff time in seconds
            **kwargs: Keyword arguments for the operation

        Returns:
            The result of the Redis operation, or None on failure
        """
        if self._client is None:
            return None

        backoff = initial_backoff
        last_error = None

        for attempt in range(max_retries):
            try:
                method = getattr(self._client, operation)
                return await method(*args, **kwargs)
            except (ConnectionError, TimeoutError) as e:
                last_error = e
                if attempt < max_retries - 1:
                    await asyncio.sleep(backoff)
                    backoff = min(backoff * 2, 2.0)  # Cap at 2 seconds

        print(f"Redis {operation} failed after {max_retries} retries: {last_error}")
        return None

    async def set_link(
        self,
        short_code: str,
        original_url: str,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Cache a link mapping.

        Args:
            short_code: The short code key
            original_url: The original URL value
            ttl: Optional TTL in seconds (default: 1 hour)

        Returns:
            bool: True if cached successfully
        """
        ttl = ttl or self._default_ttl
        cache_key = f"link:{short_code}"

        result = await self._execute_with_retry(
            "set",
            cache_key,
            original_url,
            ex=ttl,
        )

        return result is not None

    async def get_link(self, short_code: str) -> Optional[str]:
        """
        Get a cached link URL.

        Args:
            short_code: The short code to look up

        Returns:
            Optional[str]: The original URL if cached, None otherwise
        """
        cache_key = f"link:{short_code}"
        return await self._execute_with_retry("get", cache_key)

    async def delete_link(self, short_code: str) -> bool:
        """
        Delete a cached link.

        Args:
            short_code: The short code to delete

        Returns:
            bool: True if deleted
        """
        cache_key = f"link:{short_code}"
        result = await self._execute_with_retry("delete", cache_key)
        return result is not None and result > 0

    async def increment_clicks(self, short_code: str) -> int:
        """
        Increment the click counter for a link.

        Args:
            short_code: The short code

        Returns:
            int: The new click count
        """
        cache_key = f"clicks:{short_code}"
        result = await self._execute_with_retry("incr", cache_key)
        return result or 0

    async def get_clicks(self, short_code: str) -> int:
        """
        Get the click count for a link.

        Args:
            short_code: The short code

        Returns:
            int: The click count
        """
        cache_key = f"clicks:{short_code}"
        result = await self._execute_with_retry("get", cache_key)
        return int(result) if result else 0

    async def push_event(self, event_data: str) -> bool:
        """
        Push an analytics event to the Redis stream.

        Args:
            event_data: JSON serialized event data

        Returns:
            bool: True if pushed successfully
        """
        result = await self._execute_with_retry(
            "lpush",
            "analytics:events",
            event_data,
        )
        return result is not None

    async def health_check(self) -> bool:
        """
        Check if Redis is healthy.

        Returns:
            bool: True if Redis is responding
        """
        result = await self._execute_with_retry("ping")
        return result is True or result == "PONG"

    async def close(self) -> None:
        """Close the Redis connection."""
        if self._client:
            await self._client.close()
            RedisCache._client = None
