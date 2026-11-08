"""
LinkForge - URL Shortening Tests
Tests for URL creation, validation, and link management.
"""

import pytest
from datetime import datetime, timedelta, timezone


class TestUrlValidation:
    """Tests for URL validation logic."""

    def test_validate_valid_http_url(self, shortening_service):
        """Test that valid HTTP URLs pass validation."""
        assert shortening_service.validate_url("http://example.com") is True

    def test_validate_valid_https_url(self, shortening_service):
        """Test that valid HTTPS URLs pass validation."""
        assert shortening_service.validate_url("https://example.com/path") is True

    def test_validate_url_with_query_params(self, shortening_service):
        """Test URLs with query parameters."""
        url = "https://example.com/search?q=test&page=1"
        assert shortening_service.validate_url(url) is True

    def test_validate_empty_url_raises(self, shortening_service):
        """Test that empty URLs raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            shortening_service.validate_url("")

    def test_validate_none_url_raises(self, shortening_service):
        """Test that None URLs raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            shortening_service.validate_url(None)

    def test_validate_missing_protocol_raises(self, shortening_service):
        """Test that URLs without protocol raise ValueError."""
        with pytest.raises(ValueError, match="must start with"):
            shortening_service.validate_url("example.com")

    def test_validate_invalid_protocol_raises(self, shortening_service):
        """Test that non-HTTP protocols raise ValueError."""
        with pytest.raises(ValueError, match="must start with"):
            shortening_service.validate_url("ftp://example.com")

    def test_validate_too_long_url_raises(self, shortening_service):
        """Test that URLs over 2048 chars raise ValueError."""
        long_url = "https://example.com/" + "a" * 2048
        with pytest.raises(ValueError, match="exceeds maximum length"):
            shortening_service.validate_url(long_url)

    def test_validate_url_without_domain_raises(self, shortening_service):
        """Test that URLs without valid domain raise ValueError."""
        with pytest.raises(ValueError, match="valid domain"):
            shortening_service.validate_url("https://nodomain")


class TestShortCodeGeneration:
    """Tests for short code generation."""

    def test_generate_short_code_default_length(self, shortening_service):
        """Test default short code length is 6."""
        code = shortening_service.generate_short_code()
        assert len(code) == 6

    def test_generate_short_code_custom_length(self, shortening_service):
        """Test custom short code length."""
        code = shortening_service.generate_short_code(length=8)
        assert len(code) == 8

    def test_generate_short_code_is_alphanumeric(self, shortening_service):
        """Test that short codes contain only alphanumeric chars."""
        for _ in range(100):
            code = shortening_service.generate_short_code()
            assert code.isalnum()

    def test_generate_short_code_randomness(self, shortening_service):
        """Test that generated codes are unique."""
        codes = [shortening_service.generate_short_code() for _ in range(1000)]
        # With 62^6 combinations, duplicates should be extremely rare
        assert len(set(codes)) >= 990

    def test_generate_deterministic_code(self, shortening_service):
        """Test deterministic code generation produces same result."""
        url = "https://example.com/test"
        code1 = shortening_service.generate_deterministic_code(url)
        code2 = shortening_service.generate_deterministic_code(url)
        assert code1 == code2

    def test_deterministic_code_different_for_different_urls(self, shortening_service):
        """Test different URLs produce different deterministic codes."""
        url1 = "https://example.com/test1"
        url2 = "https://example.com/test2"
        code1 = shortening_service.generate_deterministic_code(url1)
        code2 = shortening_service.generate_deterministic_code(url2)
        assert code1 != code2


class TestCreateShortUrl:
    """Tests for URL shortening operations."""

    @pytest.mark.asyncio
    async def test_create_short_url_success(self, shortening_service, valid_url):
        """Test successful URL shortening."""
        link = await shortening_service.create_short_url(
            original_url=valid_url,
            user_id=1,
        )

        assert link is not None
        assert link.original_url == valid_url
        assert len(link.short_code) == 6
        assert link.user_id == 1

    @pytest.mark.asyncio
    async def test_create_short_url_with_custom_code(
        self, shortening_service, valid_url
    ):
        """Test URL shortening with custom code."""
        custom_code = "mycode"
        link = await shortening_service.create_short_url(
            original_url=valid_url,
            user_id=1,
            custom_code=custom_code,
        )

        assert link.short_code == custom_code

    @pytest.mark.asyncio
    async def test_create_short_url_with_expiration(
        self, shortening_service, valid_url
    ):
        """Test URL shortening with expiration."""
        link = await shortening_service.create_short_url(
            original_url=valid_url,
            user_id=1,
            expires_in_days=30,
        )

        assert link.expires_at is not None
        # Naive UTC, which is what SQLite hands back for expires_at
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        expected_expiry = now + timedelta(days=30)
        # Allow 1 minute tolerance
        assert abs((link.expires_at - expected_expiry).total_seconds()) < 60

    @pytest.mark.asyncio
    async def test_create_short_url_invalid_url_raises(self, shortening_service):
        """Test that invalid URLs raise ValueError."""
        with pytest.raises(ValueError):
            await shortening_service.create_short_url(
                original_url="invalid-url",
                user_id=1,
            )

    @pytest.mark.asyncio
    async def test_create_short_url_caches_result(
        self,
        shortening_service,
        valid_url,
        mock_redis_cache,
    ):
        """Test that created URLs are cached."""
        link = await shortening_service.create_short_url(
            original_url=valid_url,
            user_id=1,
        )

        mock_redis_cache.set_link.assert_called_once_with(
            link.short_code,
            valid_url,
        )


class TestGetLink:
    """Tests for link retrieval."""

    @pytest.mark.asyncio
    async def test_get_link_from_database(
        self,
        shortening_service,
        test_link,
    ):
        """Test getting a link from the database."""
        link = await shortening_service.get_link(test_link.short_code)

        assert link is not None
        assert link.short_code == test_link.short_code

    @pytest.mark.asyncio
    async def test_get_link_from_cache(
        self,
        shortening_service,
        test_link,
        mock_redis_cache,
    ):
        """Test that cache is checked first."""
        mock_redis_cache.get_link.return_value = test_link.original_url

        link = await shortening_service.get_link(test_link.short_code)

        mock_redis_cache.get_link.assert_called_once()
        assert link is not None

    @pytest.mark.asyncio
    async def test_get_link_not_found(self, shortening_service):
        """Test getting a non-existent link returns None."""
        link = await shortening_service.get_link("nonexistent")
        assert link is None

    @pytest.mark.asyncio
    async def test_get_expired_link_returns_none(
        self,
        db_session,
        test_user,
        shortening_service,
    ):
        """Test that expired links return None."""
        from src.models import Link

        expired_link = Link(
            user_id=test_user.id,
            original_url="https://example.com",
            short_code="expired1",
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        )
        db_session.add(expired_link)
        await db_session.commit()

        link = await shortening_service.get_link("expired1")
        assert link is None


class TestDeleteLink:
    """Tests for link deletion."""

    @pytest.mark.asyncio
    async def test_delete_link_success(
        self,
        shortening_service,
        test_link,
        test_user,
    ):
        """Test successful link deletion."""
        result = await shortening_service.delete_link(
            short_code=test_link.short_code,
            user_id=test_user.id,
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_link_wrong_user(
        self,
        shortening_service,
        test_link,
    ):
        """Test deletion by wrong user returns False."""
        result = await shortening_service.delete_link(
            short_code=test_link.short_code,
            user_id=999,  # Wrong user
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_nonexistent_link(self, shortening_service):
        """Test deleting non-existent link returns False."""
        result = await shortening_service.delete_link(
            short_code="nonexistent",
            user_id=1,
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_link_invalidates_cache(
        self,
        shortening_service,
        test_link,
        test_user,
        mock_redis_cache,
    ):
        """Test that deletion invalidates cache."""
        await shortening_service.delete_link(
            short_code=test_link.short_code,
            user_id=test_user.id,
        )

        mock_redis_cache.delete_link.assert_called_once_with(test_link.short_code)
