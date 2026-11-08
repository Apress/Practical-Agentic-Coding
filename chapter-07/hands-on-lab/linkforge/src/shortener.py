"""
LinkForge - URL Shortening Service
Core business logic for URL shortening and link management.
"""

import hashlib
import re
import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Link
from .schemas import AnalyticsResponse
from .cache import RedisCache
from .analytics import AnalyticsService


# Base62 alphabet for short codes
BASE62_ALPHABET = string.ascii_letters + string.digits

# Custom short codes: letters, digits, hyphen, underscore; 3-30 chars
CUSTOM_CODE_PATTERN = re.compile(r"^[A-Za-z0-9_-]{3,30}$")


class ShorteningService:
    """
    Service for URL shortening operations.

    Handles:
    - Short code generation with collision detection
    - URL validation
    - Link CRUD operations
    - Click logging integration

    Attributes:
        db: Async database session
        cache: Redis cache instance
        analytics: Analytics service for click tracking
    """

    def __init__(
        self,
        db: AsyncSession,
        cache: Optional[RedisCache] = None,
        analytics: Optional[AnalyticsService] = None,
    ):
        """
        Initialize the shortening service.

        Args:
            db: SQLAlchemy async session
            cache: Optional Redis cache for lookups
            analytics: Optional analytics service for click tracking
        """
        self.db = db
        self.cache = cache
        self.analytics = analytics

    def generate_short_code(self, length: int = 6) -> str:
        """
        Generate a random short code using Base62 encoding.

        Args:
            length: Desired length of the short code (default: 6)

        Returns:
            str: A random Base62 encoded string

        Note:
            6 characters provides 62^6 = 56.8 billion combinations
        """
        return ''.join(secrets.choice(BASE62_ALPHABET) for _ in range(length))

    def generate_deterministic_code(self, url: str) -> str:
        """
        Generate a deterministic short code from a URL.

        Uses SHA256 hash truncated to Base62 for consistent codes.

        Args:
            url: The URL to hash

        Returns:
            str: A deterministic 6-character code
        """
        hash_bytes = hashlib.sha256(url.encode()).digest()
        code = []
        for i in range(6):
            idx = hash_bytes[i] % len(BASE62_ALPHABET)
            code.append(BASE62_ALPHABET[idx])
        return ''.join(code)

    def validate_url(self, url: str) -> bool:
        """
        Validate that a URL is well-formed.

        Args:
            url: The URL to validate

        Returns:
            bool: True if URL is valid

        Raises:
            ValueError: If URL is invalid
        """
        if not url:
            raise ValueError("URL cannot be empty")

        if not url.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")

        if len(url) > 2048:
            raise ValueError("URL exceeds maximum length of 2048 characters")

        # Basic structure check
        if "." not in url[8:]:  # After protocol
            raise ValueError("URL must contain a valid domain")

        return True

    def validate_custom_code(self, code: str) -> bool:
        """
        Validate a user-supplied custom short code.

        Args:
            code: The custom short code to validate

        Returns:
            bool: True if the code is valid

        Raises:
            ValueError: If the code is not 3-30 characters of letters,
                digits, hyphens, or underscores
        """
        if not CUSTOM_CODE_PATTERN.fullmatch(code):
            raise ValueError(
                "Custom code must be 3-30 characters long and contain "
                "only letters, digits, hyphens, or underscores"
            )
        return True

    async def create_short_url(
        self,
        original_url: str,
        user_id: int,
        custom_code: Optional[str] = None,
        expires_in_days: Optional[int] = None,
    ) -> Link:
        """
        Create a shortened URL.

        Args:
            original_url: The URL to shorten
            user_id: ID of the user creating the link
            custom_code: Optional custom short code
            expires_in_days: Optional expiration period

        Returns:
            Link: The created link object

        Raises:
            ValueError: If URL is invalid, custom code is malformed,
                or code is taken
        """
        # Validate URL
        self.validate_url(original_url)

        # Generate or validate short code
        if custom_code:
            # Validate format before checking availability
            self.validate_custom_code(custom_code)
            # Check if custom code is already taken
            existing = await self._get_link_by_code(custom_code)
            if existing:
                raise ValueError(f"Short code '{custom_code}' is already in use")
            short_code = custom_code
        else:
            # Generate unique code with collision detection
            short_code = await self._generate_unique_code()

        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

        # Create link
        link = Link(
            user_id=user_id,
            original_url=original_url,
            short_code=short_code,
            expires_at=expires_at,
        )

        self.db.add(link)
        await self.db.commit()
        await self.db.refresh(link)

        # Cache the new link
        if self.cache:
            await self.cache.set_link(short_code, original_url)

        return link

    async def _generate_unique_code(self, max_attempts: int = 10) -> str:
        """
        Generate a unique short code with collision detection.

        Args:
            max_attempts: Maximum generation attempts

        Returns:
            str: A unique short code

        Raises:
            RuntimeError: If unable to generate unique code
        """
        for _ in range(max_attempts):
            code = self.generate_short_code()
            existing = await self._get_link_by_code(code)
            if not existing:
                return code

        # If we can't find a unique 6-char code, try 7 characters
        for _ in range(max_attempts):
            code = self.generate_short_code(length=7)
            existing = await self._get_link_by_code(code)
            if not existing:
                return code

        raise RuntimeError("Unable to generate unique short code")

    async def _get_link_by_code(self, short_code: str) -> Optional[Link]:
        """
        Get a link by its short code from database.

        Args:
            short_code: The short code to look up

        Returns:
            Optional[Link]: The link if found, None otherwise
        """
        result = await self.db.execute(
            select(Link).where(Link.short_code == short_code)
        )
        return result.scalar_one_or_none()

    async def get_link(self, short_code: str) -> Optional[Link]:
        """
        Get a link by its short code, using cache if available.

        Args:
            short_code: The short code to look up

        Returns:
            Optional[Link]: The link if found and not expired
        """
        # Try cache first
        if self.cache:
            cached_url = await self.cache.get_link(short_code)
            if cached_url:
                # Still need to get full link object for analytics
                link = await self._get_link_by_code(short_code)
                if link and not link.is_expired:
                    return link

        # Fall back to database
        link = await self._get_link_by_code(short_code)

        if link and link.is_expired:
            return None

        # Update cache on miss
        if link and self.cache:
            await self.cache.set_link(short_code, link.original_url)

        return link

    async def log_click(
        self,
        short_code: str,
        referrer: Optional[str] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> None:
        """
        Log a click event for analytics.

        Args:
            short_code: The clicked short code
            referrer: HTTP referrer header
            user_agent: Browser user agent
            ip_address: Client IP address
        """
        if self.analytics:
            await self.analytics.log_click(
                short_code=short_code,
                referrer=referrer,
                user_agent=user_agent,
                ip_address=ip_address,
            )

        # Also update database click count
        link = await self._get_link_by_code(short_code)
        if link:
            link.click_count += 1
            await self.db.commit()

    async def get_analytics(self, short_code: str) -> AnalyticsResponse:
        """
        Get analytics for a link.

        Args:
            short_code: The short code to get analytics for

        Returns:
            AnalyticsResponse: Aggregated analytics data
        """
        link = await self._get_link_by_code(short_code)
        if not link:
            return AnalyticsResponse(
                total_clicks=0,
                unique_visitors=0,
            )

        # Get from analytics service if available
        if self.analytics:
            return await self.analytics.get_link_analytics(link.id)

        # Fallback to database query
        return AnalyticsResponse(
            total_clicks=link.click_count,
            unique_visitors=link.click_count,  # Simplified
        )

    async def delete_link(self, short_code: str, user_id: int) -> bool:
        """
        Delete a link if owned by the user.

        Args:
            short_code: The short code to delete
            user_id: ID of the requesting user

        Returns:
            bool: True if deleted, False if not found or not owned
        """
        link = await self._get_link_by_code(short_code)
        if not link or link.user_id != user_id:
            return False

        # Invalidate cache
        if self.cache:
            await self.cache.delete_link(short_code)

        await self.db.delete(link)
        await self.db.commit()
        return True
