"""
LinkForge - Rate Limiting
Redis-backed daily quota for the shortening endpoint.

The free tier allows RATE_LIMIT_PER_DAY shortening requests per caller
per UTC day (default 100). Callers are identified by their API key
header when present, otherwise by client IP. Each identity gets a
day-keyed Redis counter (INCR + EXPIRE), so quotas reset at midnight
UTC with no cleanup job.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Optional

import redis.asyncio as redis
from fastapi import Request

logger = logging.getLogger(__name__)

DEFAULT_DAILY_LIMIT = 100
API_KEY_HEADER = "x-api-key"

# Counters expire 25 hours after first use: long enough to cover the
# whole UTC day they belong to, short enough that stale keys vanish.
COUNTER_TTL_SECONDS = 25 * 3600


def _configured_limit() -> int:
    """Read RATE_LIMIT_PER_DAY from the environment (default 100)."""
    raw = os.getenv("RATE_LIMIT_PER_DAY", str(DEFAULT_DAILY_LIMIT))
    try:
        return int(raw)
    except ValueError:
        logger.warning(
            "Invalid RATE_LIMIT_PER_DAY=%r; using default %d",
            raw,
            DEFAULT_DAILY_LIMIT,
        )
        return DEFAULT_DAILY_LIMIT


class DailyRateLimiter:
    """
    Per-caller daily quota backed by a day-keyed Redis counter.

    Attributes:
        client: Redis-compatible client exposing async incr/expire
        limit: Requests allowed per identity per UTC day
    """

    def __init__(
        self,
        client: "redis.Redis",
        limit: Optional[int] = None,
    ):
        """
        Initialize the limiter.

        Args:
            client: Redis client (or an in-memory stand-in for tests)
            limit: Daily quota; defaults to the RATE_LIMIT_PER_DAY
                environment variable, falling back to 100
        """
        self.client = client
        self.limit = limit if limit is not None else _configured_limit()

    @staticmethod
    def identify(request: Request) -> str:
        """
        Identify the caller for quota accounting.

        Uses the API key header when present (authenticated callers get
        their own quota regardless of network), else the client IP.

        Args:
            request: The incoming FastAPI request

        Returns:
            str: A stable identity string, e.g. "key:abc" or "ip:1.2.3.4"
        """
        api_key = request.headers.get(API_KEY_HEADER)
        if api_key:
            return f"key:{api_key}"
        host = request.client.host if request.client else "unknown"
        return f"ip:{host}"

    async def allow(self, identity: str) -> bool:
        """
        Count one request; report whether it is within the daily quota.

        Fails open: if Redis is unreachable the request is allowed and a
        warning is logged. Briefly losing rate limiting is better than
        taking the whole API down with Redis.

        Args:
            identity: Caller identity from identify()

        Returns:
            bool: True if the request is allowed, False if over quota
        """
        day = datetime.now(timezone.utc).strftime("%Y%m%d")
        key = f"ratelimit:{identity}:{day}"

        try:
            count = await self.client.incr(key)
            if count == 1:
                await self.client.expire(key, COUNTER_TTL_SECONDS)
            return count <= self.limit
        except Exception as exc:
            logger.warning("Rate limiter unavailable, allowing request: %s", exc)
            return True


_limiter: Optional[DailyRateLimiter] = None


async def get_rate_limiter() -> DailyRateLimiter:
    """
    FastAPI dependency provider for the shared limiter.

    Keeps its own Redis connection (same REDIS_URL as the cache) so
    cache.py stays single-purpose. Tests override this dependency with
    a limiter built on an in-memory stub.

    Returns:
        DailyRateLimiter: The process-wide limiter instance
    """
    global _limiter
    if _limiter is None:
        client = redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379"),
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
        _limiter = DailyRateLimiter(client)
    return _limiter
