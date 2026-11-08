"""
LinkForge - Security Tests
Tests for input validation, authorization, concurrency safety,
and secure error handling.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock


class TestInputValidation:
    """Tests for input validation and sanitization."""

    @pytest.mark.asyncio
    async def test_reject_javascript_url(self, shortening_service):
        """Test that JavaScript URLs are rejected."""
        with pytest.raises(ValueError):
            await shortening_service.create_short_url(
                original_url="javascript:alert('xss')",
                user_id=1,
            )

    @pytest.mark.asyncio
    async def test_reject_data_url(self, shortening_service):
        """Test that data URLs are rejected."""
        with pytest.raises(ValueError):
            await shortening_service.create_short_url(
                original_url="data:text/html,<script>alert('xss')</script>",
                user_id=1,
            )

    @pytest.mark.asyncio
    async def test_reject_file_url(self, shortening_service):
        """Test that file URLs are rejected."""
        with pytest.raises(ValueError):
            await shortening_service.create_short_url(
                original_url="file:///etc/passwd",
                user_id=1,
            )

    @pytest.mark.asyncio
    async def test_reject_extremely_long_url(self, shortening_service):
        """Test that extremely long URLs are rejected."""
        long_url = "https://example.com/" + "a" * 3000
        with pytest.raises(ValueError, match="exceeds maximum length"):
            await shortening_service.create_short_url(
                original_url=long_url,
                user_id=1,
            )

    @pytest.mark.asyncio
    async def test_accept_url_at_max_length(self, shortening_service):
        """Test that URLs at exactly max length are accepted."""
        # 2048 - len("https://example.com/") = 2028 characters for path
        path = "a" * 2020
        url = f"https://example.com/{path}"
        assert len(url) <= 2048

        link = await shortening_service.create_short_url(
            original_url=url,
            user_id=1,
        )
        assert link is not None


class TestCustomCodeValidation:
    """Tests for custom short code validation."""

    @pytest.mark.asyncio
    async def test_reject_code_with_special_chars(self, shortening_service, valid_url):
        """Test that codes with special characters are handled."""
        # The schema should validate this, but test service layer too
        with pytest.raises(ValueError):
            await shortening_service.create_short_url(
                original_url=valid_url,
                user_id=1,
                custom_code="<script>",
            )

    @pytest.mark.asyncio
    async def test_reject_duplicate_custom_code(
        self,
        shortening_service,
        test_link,
        valid_url,
    ):
        """Test that duplicate custom codes are rejected."""
        with pytest.raises(ValueError, match="already in use"):
            await shortening_service.create_short_url(
                original_url=valid_url,
                user_id=1,
                custom_code=test_link.short_code,
            )


class TestAuthorizationLogic:
    """Tests for authorization and ownership validation."""

    @pytest.mark.asyncio
    async def test_user_can_delete_own_link(
        self,
        shortening_service,
        test_link,
        test_user,
    ):
        """Test that users can delete their own links."""
        result = await shortening_service.delete_link(
            short_code=test_link.short_code,
            user_id=test_user.id,
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_user_cannot_delete_others_link(
        self,
        shortening_service,
        test_link,
    ):
        """Test that users cannot delete others' links."""
        result = await shortening_service.delete_link(
            short_code=test_link.short_code,
            user_id=999,  # Different user
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_nonexistent_user_cannot_delete(self, shortening_service, test_link):
        """Test that non-existent users cannot delete links."""
        result = await shortening_service.delete_link(
            short_code=test_link.short_code,
            user_id=-1,
        )
        assert result is False


class TestAPIEndpointSecurity:
    """Tests for API endpoint security."""

    @pytest.mark.asyncio
    async def test_create_link_requires_valid_url(self, async_client):
        """Test that create endpoint validates URL at both layers."""
        # Malformed URL: rejected by the Pydantic request schema (422)
        response = await async_client.post(
            "/api/v1/links",
            json={"original_url": "not-a-url"},
        )
        assert response.status_code == 422

        # Well-formed but invalid URL (no domain): passes the schema,
        # rejected by the service layer (400)
        response = await async_client.post(
            "/api/v1/links",
            json={"original_url": "https://nodomain"},
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_get_nonexistent_link_returns_404(self, async_client):
        """Test that getting non-existent link returns 404."""
        response = await async_client.get("/api/v1/links/nonexistent")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_redirect_nonexistent_returns_404(self, async_client):
        """Test that redirecting non-existent code returns 404."""
        response = await async_client.get(
            "/nonexistent",
            follow_redirects=False,
        )
        assert response.status_code == 404


class TestConcurrentRequests:
    """Tests for concurrent request handling."""

    @pytest.mark.asyncio
    async def test_concurrent_shortening_unique_codes(
        self,
        db_session_factory,
        mock_redis_cache,
        mock_analytics_service,
    ):
        """Test that concurrent requests get unique codes."""
        import asyncio
        from src.shortener import ShorteningService

        async def shorten(i: int) -> str:
            # Each concurrent task gets its own session: an
            # AsyncSession must never be shared across tasks.
            async with db_session_factory() as session:
                service = ShorteningService(
                    db=session,
                    cache=mock_redis_cache,
                    analytics=mock_analytics_service,
                )
                link = await service.create_short_url(
                    original_url=f"https://example.com/page{i}",
                    user_id=1,
                )
                return link.short_code

        # Create 10 concurrent shortening requests
        codes = await asyncio.gather(*(shorten(i) for i in range(10)))

        # All codes should be unique
        assert len(set(codes)) == 10


class TestCacheSecurityBehavior:
    """Tests for cache-related security behavior."""

    @pytest.mark.asyncio
    async def test_cache_miss_falls_back_to_db(
        self,
        shortening_service,
        test_link,
        mock_redis_cache,
    ):
        """Test that cache miss correctly falls back to database."""
        mock_redis_cache.get_link.return_value = None

        link = await shortening_service.get_link(test_link.short_code)

        assert link is not None
        assert link.short_code == test_link.short_code

    @pytest.mark.asyncio
    async def test_cache_invalidated_on_delete(
        self,
        shortening_service,
        test_link,
        test_user,
        mock_redis_cache,
    ):
        """Test that cache is invalidated when link is deleted."""
        await shortening_service.delete_link(
            short_code=test_link.short_code,
            user_id=test_user.id,
        )

        mock_redis_cache.delete_link.assert_called_once_with(test_link.short_code)


class TestErrorHandling:
    """Tests for secure error handling."""

    @pytest.mark.asyncio
    async def test_database_error_does_not_leak_info(self):
        """Test that database errors don't leak sensitive info."""
        from httpx import ASGITransport, AsyncClient
        from sqlalchemy.exc import SQLAlchemyError

        from src.main import app, get_shortening_service

        # Simulate a database failure inside the service layer with
        # driver detail that must never reach the client
        failing_service = MagicMock()
        failing_service.get_link = AsyncMock(
            side_effect=SQLAlchemyError(
                "connection to server at localhost:5432 failed while "
                "running SELECT links.short_code FROM links"
            )
        )

        async def override_get_service():
            return failing_service

        app.dependency_overrides[get_shortening_service] = override_get_service
        try:
            # raise_app_exceptions=False returns the app's 500 response
            # instead of re-raising the exception into the test
            transport = ASGITransport(app=app, raise_app_exceptions=False)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                response = await client.get("/api/v1/links/abc123")
        finally:
            app.dependency_overrides.pop(get_shortening_service, None)

        assert response.status_code == 500
        body = response.text
        # The response must not echo SQL, driver detail, or stack traces
        assert "SELECT" not in body
        assert "sqlalchemy" not in body.lower()
        assert "5432" not in body
        assert "Traceback" not in body

    @pytest.mark.asyncio
    async def test_validation_error_message_is_safe(self, async_client):
        """Test that validation errors are informative but safe."""
        response = await async_client.post(
            "/api/v1/links",
            json={"original_url": "invalid"},
        )

        # Should return a schema validation error, not an internal error
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        # Should not contain stack traces
        assert "Traceback" not in str(data)
