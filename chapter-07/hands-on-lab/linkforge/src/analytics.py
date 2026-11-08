"""
LinkForge - Analytics Service
Async event tracking and analytics aggregation.
"""

import asyncio
import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from .cache import RedisCache
from .models import AnalyticsEvent, Link
from .schemas import AnalyticsResponse, ClickEvent

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Service for tracking and aggregating link analytics.

    Handles:
    - Async click event logging to Redis stream and database
    - Analytics aggregation and reporting
    - Device detection from user agent
    - Privacy-preserving IP hashing

    Both dependencies are optional, matching how the service is used:
    without a cache, events are not streamed; without a database
    session, events are not persisted and aggregation queries return
    empty results (unit tests exercise each path in isolation).

    Attributes:
        cache: Redis cache instance for event streaming
        max_retries: Maximum retries for event pushing
        initial_backoff: Initial backoff time for retries
        db: Async database session for persistence and aggregation
    """

    def __init__(
        self,
        cache: Optional[RedisCache] = None,
        max_retries: int = 3,
        initial_backoff: float = 0.1,
        db: Optional[AsyncSession] = None,
    ):
        """
        Initialize the analytics service.

        Args:
            cache: Redis cache for event streaming
            max_retries: Max retries for push operations
            initial_backoff: Initial retry backoff in seconds
            db: Database session for event persistence and aggregation
        """
        self.cache = cache
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff
        self.db = db

    def _hash_ip(self, ip_address: Optional[str]) -> Optional[str]:
        """
        Hash an IP address for privacy.

        Args:
            ip_address: The IP address to hash

        Returns:
            Optional[str]: SHA256 hash of the IP, or None
        """
        if not ip_address:
            return None

        # Use a salt for additional privacy
        salt = "linkforge_analytics_salt"
        salted = f"{salt}:{ip_address}"
        return hashlib.sha256(salted.encode()).hexdigest()[:16]

    def _detect_device(self, user_agent: Optional[str]) -> str:
        """
        Detect device type from user agent string.

        Args:
            user_agent: Browser user agent string

        Returns:
            str: Device type (mobile, tablet, desktop, or unknown)
        """
        if not user_agent:
            return "unknown"

        ua_lower = user_agent.lower()

        # Mobile detection
        mobile_keywords = [
            "iphone", "android", "mobile", "blackberry",
            "windows phone", "opera mini", "iemobile"
        ]
        if any(kw in ua_lower for kw in mobile_keywords):
            # Check if it's a tablet
            if "ipad" in ua_lower or "tablet" in ua_lower:
                return "tablet"
            return "mobile"

        # Tablet detection
        tablet_keywords = ["ipad", "tablet", "kindle", "silk"]
        if any(kw in ua_lower for kw in tablet_keywords):
            return "tablet"

        # Default to desktop
        return "desktop"

    def _extract_referrer_source(self, referrer: Optional[str]) -> Optional[str]:
        """
        Extract the source domain from a referrer URL.

        Args:
            referrer: Full referrer URL

        Returns:
            Optional[str]: Domain name or None
        """
        if not referrer:
            return None

        try:
            # Remove protocol
            if "://" in referrer:
                referrer = referrer.split("://", 1)[1]

            # Get domain
            domain = referrer.split("/")[0]

            # Remove www prefix
            if domain.startswith("www."):
                domain = domain[4:]

            return domain
        except Exception:
            return None

    async def log_click(
        self,
        short_code: str,
        referrer: Optional[str] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        link_id: Optional[int] = None,
    ) -> bool:
        """
        Log a click event asynchronously.

        Args:
            short_code: The clicked short code
            referrer: HTTP referrer header
            user_agent: Browser user agent
            ip_address: Client IP address
            link_id: Optional link ID

        Returns:
            bool: True if the event was recorded (streamed or persisted)
        """
        # Create event
        event = ClickEvent(
            link_id=link_id or 0,
            short_code=short_code,
            clicked_at=datetime.now(timezone.utc),
            referrer=self._extract_referrer_source(referrer),
            user_agent=user_agent,
            ip_address=self._hash_ip(ip_address),
        )

        recorded = False

        # Try to push to Redis with retries
        if self.cache:
            event_json = event.model_dump_json()
            recorded = await self._push_with_retry(event_json)
            if recorded:
                # Also increment click counter
                await self.cache.increment_clicks(short_code)

        # Persist the event row that get_link_analytics aggregates
        if self.db is not None:
            stored = await self._store_event(event, user_agent, link_id)
            recorded = recorded or stored

        return recorded

    async def _store_event(
        self,
        event: ClickEvent,
        raw_user_agent: Optional[str],
        link_id: Optional[int],
    ) -> bool:
        """
        Persist a click event to the analytics_events table.

        A failed insert must never break the redirect that triggered it,
        so errors are logged and swallowed.

        Args:
            event: The validated click event
            raw_user_agent: Original user agent (for device detection)
            link_id: Link ID if the caller already knows it

        Returns:
            bool: True if the row was written
        """
        try:
            if not link_id:
                result = await self.db.execute(
                    select(Link.id).where(Link.short_code == event.short_code)
                )
                link_id = result.scalar_one_or_none()
            if not link_id:
                return False

            self.db.add(
                AnalyticsEvent(
                    link_id=link_id,
                    clicked_at=event.clicked_at,
                    referrer=event.referrer,
                    user_agent=raw_user_agent[:512] if raw_user_agent else None,
                    ip_address=event.ip_address,
                    device_type=self._detect_device(raw_user_agent),
                )
            )
            await self.db.commit()
            return True
        except Exception:
            logger.warning("Failed to persist analytics event", exc_info=True)
            await self.db.rollback()
            return False

    async def _push_with_retry(self, event_data: str) -> bool:
        """
        Push event to Redis with exponential backoff retry.

        Args:
            event_data: JSON serialized event

        Returns:
            bool: True if pushed successfully
        """
        backoff = self.initial_backoff

        for attempt in range(self.max_retries):
            try:
                success = await self.cache.push_event(event_data)
                if success:
                    return True
            except Exception as e:
                logger.warning(
                    "Analytics push attempt %d failed: %s", attempt + 1, e
                )

            if attempt < self.max_retries - 1:
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 2.0)  # Cap at 2 seconds

        return False

    async def get_link_analytics(self, link_id: int) -> AnalyticsResponse:
        """
        Get aggregated analytics for a link.

        Total clicks come from the Link.click_count counter (updated on
        every redirect); visitor, time-window, referrer, country, and
        device figures are aggregated from stored AnalyticsEvent rows.
        Unique visitors are counted as distinct hashed IPs.

        Args:
            link_id: The link ID to get analytics for

        Returns:
            AnalyticsResponse: Aggregated analytics data (empty when the
                service has no database session)
        """
        if self.db is None:
            return AnalyticsResponse(total_clicks=0, unique_visitors=0)

        link = await self.db.get(Link, link_id)
        now = datetime.now(timezone.utc)

        def _count(*criteria):
            return (
                select(func.count())
                .select_from(AnalyticsEvent)
                .where(AnalyticsEvent.link_id == link_id, *criteria)
            )

        unique_visitors = await self.db.scalar(
            select(func.count(AnalyticsEvent.ip_address.distinct())).where(
                AnalyticsEvent.link_id == link_id,
                AnalyticsEvent.ip_address.is_not(None),
            )
        )
        clicks_today = await self.db.scalar(
            _count(AnalyticsEvent.clicked_at >= now - timedelta(days=1))
        )
        clicks_this_week = await self.db.scalar(
            _count(AnalyticsEvent.clicked_at >= now - timedelta(days=7))
        )
        top_referrers = await self._grouped_counts(
            link_id, AnalyticsEvent.referrer, "source", limit=5
        )
        top_countries = await self._grouped_counts(
            link_id, AnalyticsEvent.country_code, "country", limit=5
        )
        devices = await self._grouped_counts(
            link_id, AnalyticsEvent.device_type, "device", limit=10
        )

        return AnalyticsResponse(
            total_clicks=link.click_count if link else 0,
            unique_visitors=unique_visitors or 0,
            clicks_today=clicks_today or 0,
            clicks_this_week=clicks_this_week or 0,
            top_referrers=top_referrers,
            top_countries=top_countries,
            device_breakdown={d["device"]: d["clicks"] for d in devices},
        )

    async def _grouped_counts(
        self,
        link_id: int,
        column,
        label: str,
        limit: int,
    ) -> list[dict]:
        """
        Count a link's events grouped by one column, most clicks first.

        Args:
            link_id: The link whose events to aggregate
            column: The AnalyticsEvent column to group by
            label: Dict key to report the column value under
            limit: Maximum number of groups to return

        Returns:
            list[dict]: e.g. [{"source": "twitter.com", "clicks": 12}]
        """
        result = await self.db.execute(
            select(column, func.count().label("clicks"))
            .where(AnalyticsEvent.link_id == link_id, column.is_not(None))
            .group_by(column)
            .order_by(func.count().desc())
            .limit(limit)
        )
        return [{label: value, "clicks": clicks} for value, clicks in result.all()]

    async def get_realtime_clicks(
        self,
        short_code: str,
        minutes: int = 60,
    ) -> list[dict]:
        """
        Get click events for a link within the last N minutes.

        Args:
            short_code: The short code to get data for
            minutes: Time window in minutes

        Returns:
            list[dict]: Click events, newest first (empty when the
                service has no database session)
        """
        if self.db is None:
            return []

        cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        result = await self.db.execute(
            select(AnalyticsEvent)
            .join(Link)
            .where(
                Link.short_code == short_code,
                AnalyticsEvent.clicked_at >= cutoff,
            )
            .order_by(AnalyticsEvent.clicked_at.desc())
        )
        return [
            {
                "clicked_at": event.clicked_at.isoformat(),
                "referrer": event.referrer,
                "device_type": event.device_type,
            }
            for event in result.scalars()
        ]

    async def get_top_links(
        self,
        user_id: int,
        limit: int = 10,
    ) -> list[dict]:
        """
        Get the top performing links for a user by click count.

        Args:
            user_id: The user ID
            limit: Maximum number of links to return

        Returns:
            list[dict]: Top links sorted by click count (empty when the
                service has no database session)
        """
        if self.db is None:
            return []

        result = await self.db.execute(
            select(Link)
            .where(Link.user_id == user_id)
            .order_by(Link.click_count.desc())
            .limit(limit)
        )
        return [
            {
                "short_code": link.short_code,
                "original_url": link.original_url,
                "clicks": link.click_count,
            }
            for link in result.scalars()
        ]
