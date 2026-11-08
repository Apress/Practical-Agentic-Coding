"""
LinkForge - Analytics Tests
Tests for click tracking and event streaming.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import select

from src.analytics import AnalyticsService
from src.models import AnalyticsEvent, Link


class TestDeviceDetection:
    """Tests for user agent device detection."""

    @pytest.fixture
    def analytics(self, mock_redis_cache):
        """Create analytics service instance."""
        return AnalyticsService(cache=mock_redis_cache)

    def test_detect_iphone(self, analytics):
        """Test iPhone detection."""
        ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
        assert analytics._detect_device(ua) == "mobile"

    def test_detect_android_phone(self, analytics):
        """Test Android phone detection."""
        ua = "Mozilla/5.0 (Linux; Android 11; Pixel 5)"
        assert analytics._detect_device(ua) == "mobile"

    def test_detect_ipad(self, analytics):
        """Test iPad detection."""
        ua = "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X)"
        assert analytics._detect_device(ua) == "tablet"

    def test_detect_android_tablet(self, analytics):
        """Test Android tablet detection."""
        ua = "Mozilla/5.0 (Linux; Android 11; SM-T870 Tablet)"
        assert analytics._detect_device(ua) == "tablet"

    def test_detect_desktop_chrome(self, analytics):
        """Test desktop Chrome detection."""
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0"
        assert analytics._detect_device(ua) == "desktop"

    def test_detect_desktop_firefox(self, analytics):
        """Test desktop Firefox detection."""
        ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0)"
        assert analytics._detect_device(ua) == "desktop"

    def test_detect_unknown_empty_ua(self, analytics):
        """Test empty user agent returns unknown."""
        assert analytics._detect_device("") == "unknown"
        assert analytics._detect_device(None) == "unknown"


class TestIPHashing:
    """Tests for privacy-preserving IP hashing."""

    @pytest.fixture
    def analytics(self, mock_redis_cache):
        """Create analytics service instance."""
        return AnalyticsService(cache=mock_redis_cache)

    def test_hash_ip_returns_string(self, analytics):
        """Test that IP hashing returns a string."""
        result = analytics._hash_ip("192.168.1.1")
        assert isinstance(result, str)

    def test_hash_ip_consistent(self, analytics):
        """Test that same IP always produces same hash."""
        ip = "192.168.1.1"
        hash1 = analytics._hash_ip(ip)
        hash2 = analytics._hash_ip(ip)
        assert hash1 == hash2

    def test_hash_ip_different_ips(self, analytics):
        """Test that different IPs produce different hashes."""
        hash1 = analytics._hash_ip("192.168.1.1")
        hash2 = analytics._hash_ip("192.168.1.2")
        assert hash1 != hash2

    def test_hash_ip_truncated(self, analytics):
        """Test that hash is truncated to 16 characters."""
        result = analytics._hash_ip("192.168.1.1")
        assert len(result) == 16

    def test_hash_ip_none_returns_none(self, analytics):
        """Test that None IP returns None."""
        assert analytics._hash_ip(None) is None

    def test_hash_ip_empty_returns_none(self, analytics):
        """Test that empty IP returns None."""
        assert analytics._hash_ip("") is None


class TestReferrerExtraction:
    """Tests for referrer source extraction."""

    @pytest.fixture
    def analytics(self, mock_redis_cache):
        """Create analytics service instance."""
        return AnalyticsService(cache=mock_redis_cache)

    def test_extract_referrer_with_protocol(self, analytics):
        """Test extraction from URL with protocol."""
        referrer = "https://twitter.com/user/status/123"
        assert analytics._extract_referrer_source(referrer) == "twitter.com"

    def test_extract_referrer_removes_www(self, analytics):
        """Test that www prefix is removed."""
        referrer = "https://www.facebook.com/share"
        assert analytics._extract_referrer_source(referrer) == "facebook.com"

    def test_extract_referrer_http(self, analytics):
        """Test extraction from HTTP URL."""
        referrer = "http://reddit.com/r/test"
        assert analytics._extract_referrer_source(referrer) == "reddit.com"

    def test_extract_referrer_none(self, analytics):
        """Test None referrer returns None."""
        assert analytics._extract_referrer_source(None) is None

    def test_extract_referrer_empty(self, analytics):
        """Test empty referrer returns None."""
        assert analytics._extract_referrer_source("") is None

    def test_extract_referrer_malformed_returns_none(self, analytics):
        """Test that an unparseable referrer value returns None."""
        # A non-string header value trips the parsing guard
        assert analytics._extract_referrer_source(12345) is None


class TestClickLogging:
    """Tests for click event logging."""

    @pytest.fixture
    def analytics(self, mock_redis_cache):
        """Create analytics service instance."""
        return AnalyticsService(cache=mock_redis_cache)

    @pytest.mark.asyncio
    async def test_log_click_success(self, analytics, mock_redis_cache):
        """Test successful click logging."""
        result = await analytics.log_click(
            short_code="abc123",
            referrer="https://twitter.com",
            user_agent="Mozilla/5.0",
            ip_address="192.168.1.1",
        )

        assert result is True
        mock_redis_cache.push_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_log_click_increments_counter(self, analytics, mock_redis_cache):
        """Test that logging click increments counter."""
        await analytics.log_click(
            short_code="abc123",
            referrer=None,
            user_agent=None,
            ip_address=None,
        )

        mock_redis_cache.increment_clicks.assert_called_once_with("abc123")

    @pytest.mark.asyncio
    async def test_log_click_without_cache(self):
        """Test logging without cache returns False."""
        analytics = AnalyticsService(cache=None)
        result = await analytics.log_click(
            short_code="abc123",
            referrer=None,
            user_agent=None,
            ip_address=None,
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_log_click_handles_event_data(self, analytics, mock_redis_cache):
        """Test that event data is properly serialized."""
        await analytics.log_click(
            short_code="abc123",
            referrer="https://google.com/search?q=test",
            user_agent="Mozilla/5.0 (Windows NT 10.0)",
            ip_address="10.0.0.1",
            link_id=42,
        )

        # Verify the pushed event contains expected data
        call_args = mock_redis_cache.push_event.call_args
        event_json = call_args[0][0]

        assert "abc123" in event_json
        assert "google.com" in event_json  # Extracted referrer


class TestRetryLogic:
    """Tests for exponential backoff retry logic."""

    @pytest.mark.asyncio
    async def test_retry_on_failure(self, mock_redis_cache):
        """Test that retries occur on failure."""
        # Make push_event fail twice then succeed
        mock_redis_cache.push_event.side_effect = [False, False, True]

        analytics = AnalyticsService(
            cache=mock_redis_cache,
            max_retries=3,
            initial_backoff=0.01,  # Fast backoff for testing
        )

        result = await analytics.log_click(
            short_code="abc123",
            referrer=None,
            user_agent=None,
            ip_address=None,
        )

        assert result is True
        assert mock_redis_cache.push_event.call_count == 3

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self, mock_redis_cache):
        """Test that max retries is respected."""
        mock_redis_cache.push_event.return_value = False

        analytics = AnalyticsService(
            cache=mock_redis_cache,
            max_retries=3,
            initial_backoff=0.01,
        )

        result = await analytics.log_click(
            short_code="abc123",
            referrer=None,
            user_agent=None,
            ip_address=None,
        )

        assert result is False
        assert mock_redis_cache.push_event.call_count == 3

    @pytest.mark.asyncio
    async def test_push_exception_is_retried(self, mock_redis_cache):
        """Test that a raised exception counts as a failed attempt."""
        mock_redis_cache.push_event.side_effect = [
            RuntimeError("redis exploded"),
            True,
        ]

        analytics = AnalyticsService(
            cache=mock_redis_cache,
            max_retries=3,
            initial_backoff=0.01,
        )

        result = await analytics.log_click(
            short_code="abc123",
            referrer=None,
            user_agent=None,
            ip_address=None,
        )

        assert result is True
        assert mock_redis_cache.push_event.call_count == 2


class TestEventPersistence:
    """Tests for persisting click events to the database."""

    @pytest.fixture
    def analytics(self, db_session):
        """Create an analytics service backed by the test database."""
        return AnalyticsService(cache=None, db=db_session)

    @pytest.mark.asyncio
    async def test_log_click_persists_event(
        self, analytics, db_session, test_link
    ):
        """Test that a click is stored with derived event fields."""
        result = await analytics.log_click(
            short_code=test_link.short_code,
            referrer="https://www.twitter.com/user/status/1",
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)",
            ip_address="192.168.1.1",
        )

        assert result is True

        rows = (
            await db_session.execute(
                select(AnalyticsEvent).where(
                    AnalyticsEvent.link_id == test_link.id
                )
            )
        ).scalars().all()

        assert len(rows) == 1
        event = rows[0]
        assert event.referrer == "twitter.com"
        assert event.device_type == "mobile"
        # IP is stored as a truncated hash, never the raw address
        assert event.ip_address != "192.168.1.1"
        assert len(event.ip_address) == 16

    @pytest.mark.asyncio
    async def test_log_click_unknown_code_not_persisted(
        self, analytics, db_session
    ):
        """Test that clicks on unknown codes are not recorded."""
        result = await analytics.log_click(
            short_code="nosuch",
            referrer=None,
            user_agent=None,
            ip_address=None,
        )

        assert result is False
        count = await db_session.scalar(
            select(AnalyticsEvent.id).limit(1)
        )
        assert count is None

    @pytest.mark.asyncio
    async def test_store_event_failure_rolls_back(self):
        """Test that a database error is swallowed and rolled back."""
        mock_db = MagicMock()
        mock_db.execute = AsyncMock(side_effect=RuntimeError("db down"))
        mock_db.rollback = AsyncMock()

        analytics = AnalyticsService(cache=None, db=mock_db)
        result = await analytics.log_click(
            short_code="abc123",
            referrer=None,
            user_agent=None,
            ip_address=None,
        )

        assert result is False
        mock_db.rollback.assert_awaited_once()


class TestAnalyticsAggregation:
    """Tests for analytics data aggregation."""

    @pytest.fixture
    def analytics(self, mock_redis_cache):
        """Create analytics service instance."""
        return AnalyticsService(cache=mock_redis_cache)

    @pytest.mark.asyncio
    async def test_get_link_analytics_returns_response(self, analytics):
        """Test that get_link_analytics returns proper response."""
        from src.schemas import AnalyticsResponse

        result = await analytics.get_link_analytics(link_id=1)

        assert isinstance(result, AnalyticsResponse)
        assert hasattr(result, "total_clicks")
        assert hasattr(result, "unique_visitors")

    @pytest.mark.asyncio
    async def test_get_realtime_clicks_returns_list(self, analytics):
        """Test that realtime clicks returns a list."""
        result = await analytics.get_realtime_clicks("abc123", minutes=60)
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_get_top_links_returns_list(self, analytics):
        """Test that top links returns a list."""
        result = await analytics.get_top_links(user_id=1, limit=10)
        assert isinstance(result, list)


class TestAnalyticsAggregationWithDb:
    """Tests for aggregation queries against stored events."""

    @pytest.fixture
    def analytics(self, db_session):
        """Create an analytics service backed by the test database."""
        return AnalyticsService(cache=None, db=db_session)

    async def _seed_events(self, db_session, test_link):
        """Insert a small spread of click events for aggregation."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        events = [
            # Two clicks today from the same visitor
            AnalyticsEvent(
                link_id=test_link.id,
                clicked_at=now - timedelta(minutes=5),
                referrer="twitter.com",
                ip_address="hash-visitor-1",
                country_code="US",
                device_type="mobile",
            ),
            AnalyticsEvent(
                link_id=test_link.id,
                clicked_at=now - timedelta(hours=2),
                referrer="twitter.com",
                ip_address="hash-visitor-1",
                country_code="US",
                device_type="desktop",
            ),
            # One click earlier this week from a second visitor
            AnalyticsEvent(
                link_id=test_link.id,
                clicked_at=now - timedelta(days=3),
                referrer="google.com",
                ip_address="hash-visitor-2",
                country_code="IN",
                device_type="desktop",
            ),
            # One old click with no attributes (outside the week window)
            AnalyticsEvent(
                link_id=test_link.id,
                clicked_at=now - timedelta(days=30),
                referrer=None,
                ip_address=None,
                country_code=None,
                device_type=None,
            ),
        ]
        db_session.add_all(events)
        test_link.click_count = 5
        await db_session.commit()

    @pytest.mark.asyncio
    async def test_get_link_analytics_aggregates_events(
        self, analytics, db_session, test_link
    ):
        """Test full aggregation across stored click events."""
        await self._seed_events(db_session, test_link)

        result = await analytics.get_link_analytics(test_link.id)

        assert result.total_clicks == 5  # From the Link counter
        assert result.unique_visitors == 2  # Distinct hashed IPs
        assert result.clicks_today == 2
        assert result.clicks_this_week == 3

        assert result.top_referrers[0] == {
            "source": "twitter.com",
            "clicks": 2,
        }
        assert result.top_referrers[1] == {
            "source": "google.com",
            "clicks": 1,
        }
        assert result.top_countries[0] == {"country": "US", "clicks": 2}
        assert result.device_breakdown == {"desktop": 2, "mobile": 1}

    @pytest.mark.asyncio
    async def test_get_link_analytics_missing_link(self, analytics):
        """Test that an unknown link yields empty analytics."""
        result = await analytics.get_link_analytics(link_id=9999)

        assert result.total_clicks == 0
        assert result.unique_visitors == 0
        assert result.top_referrers == []
        assert result.device_breakdown == {}

    @pytest.mark.asyncio
    async def test_get_realtime_clicks_respects_window(
        self, analytics, db_session, test_link
    ):
        """Test that only events inside the window return, newest first."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        db_session.add_all(
            [
                AnalyticsEvent(
                    link_id=test_link.id,
                    clicked_at=now - timedelta(minutes=1),
                    referrer="twitter.com",
                    device_type="mobile",
                ),
                AnalyticsEvent(
                    link_id=test_link.id,
                    clicked_at=now - timedelta(minutes=30),
                    referrer="google.com",
                    device_type="desktop",
                ),
                AnalyticsEvent(
                    link_id=test_link.id,
                    clicked_at=now - timedelta(hours=2),
                    referrer="reddit.com",
                    device_type="desktop",
                ),
            ]
        )
        await db_session.commit()

        result = await analytics.get_realtime_clicks(
            test_link.short_code, minutes=60
        )

        assert len(result) == 2
        assert result[0]["referrer"] == "twitter.com"
        assert result[1]["referrer"] == "google.com"
        assert result[0]["device_type"] == "mobile"
        assert "clicked_at" in result[0]

    @pytest.mark.asyncio
    async def test_get_top_links_sorted_by_clicks(
        self, analytics, db_session, test_user
    ):
        """Test that top links are ordered by click count and limited."""
        db_session.add_all(
            [
                Link(
                    user_id=test_user.id,
                    original_url="https://example.com/a",
                    short_code="aaa111",
                    click_count=5,
                ),
                Link(
                    user_id=test_user.id,
                    original_url="https://example.com/b",
                    short_code="bbb222",
                    click_count=20,
                ),
                Link(
                    user_id=test_user.id,
                    original_url="https://example.com/c",
                    short_code="ccc333",
                    click_count=1,
                ),
            ]
        )
        await db_session.commit()

        result = await analytics.get_top_links(test_user.id, limit=2)

        assert len(result) == 2
        assert result[0]["short_code"] == "bbb222"
        assert result[0]["clicks"] == 20
        assert result[1]["short_code"] == "aaa111"
        assert result[1]["original_url"] == "https://example.com/a"
