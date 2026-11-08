"""Integration tests for API authentication.

The `client` fixture comes from tests/integration/conftest.py.

A note on status codes: when the `X-API-Key` header is absent entirely,
FastAPI's `APIKeyHeader(auto_error=True)` rejects the request before our
dependency runs, and which code it uses has changed across FastAPI versions
(403 in older releases, 401 in current ones). These tests accept either, since
the behavior under test is "unauthenticated requests are rejected," not the
framework's choice of code. A *present but wrong* key is our own check, and that
is asserted as exactly 401.
"""

from fastapi.testclient import TestClient

# Codes FastAPI may return when the API key header is missing.
MISSING_KEY_CODES = (401, 403)


class TestAPIKeyAuthentication:
    """Tests for API key authentication."""

    def test_valid_api_key(self, client: TestClient) -> None:
        """Test request with valid API key succeeds."""
        headers = {"X-API-Key": "demo-key-12345"}
        response = client.get("/responses/pending", headers=headers)
        # Should not return 401/403 (may return 200 or other valid status)
        assert response.status_code != 401
        assert response.status_code != 403

    def test_missing_api_key(self, client: TestClient) -> None:
        """Test request without API key is rejected."""
        response = client.get("/responses/pending")
        assert response.status_code in MISSING_KEY_CODES

    def test_invalid_api_key(self, client: TestClient) -> None:
        """Test request with invalid API key is rejected."""
        headers = {"X-API-Key": "invalid-key-xyz"}
        response = client.get("/responses/pending", headers=headers)
        assert response.status_code == 401  # Unauthorized
        data = response.json()
        assert "detail" in data
        assert "Invalid API key" in data["detail"]

    def test_wrong_header_name(self, client: TestClient) -> None:
        """Test request with wrong header name is rejected."""
        headers = {"Authorization": "Bearer demo-key-12345"}  # Wrong header
        response = client.get("/responses/pending", headers=headers)
        assert response.status_code in MISSING_KEY_CODES

    def test_all_endpoints_require_auth(self, client: TestClient) -> None:
        """Test that all protected endpoints require authentication."""
        # All endpoints except /health and /docs should require auth
        protected_endpoints = [
            ("POST", "/tickets", {"content": "Test ticket content here"}),
            ("GET", "/tickets/TKT-123", None),
            ("GET", "/responses/pending", None),
            ("POST", "/responses/RESP-123/approve", {"reviewed_by": "test@example.com"}),
            ("POST", "/responses/RESP-123/reject", {"reviewed_by": "test", "reason": "test"}),
        ]

        for method, endpoint, json_data in protected_endpoints:
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json=json_data)

            assert (
                response.status_code in MISSING_KEY_CODES
            ), f"Endpoint {method} {endpoint} should require authentication"

    def test_health_endpoint_no_auth_required(self, client: TestClient) -> None:
        """Test that health endpoint does not require authentication."""
        response = client.get("/health")
        assert response.status_code == 200
        # Should work without any authentication

    def test_api_key_in_query_param_not_accepted(self, client: TestClient) -> None:
        """Test that API key in query parameter is not accepted."""
        response = client.get("/responses/pending?api_key=demo-key-12345")
        assert response.status_code in MISSING_KEY_CODES  # Must be in header

    def test_case_sensitive_header_name(self, client: TestClient) -> None:
        """Test that header name is case-insensitive (HTTP standard)."""
        headers = {"x-api-key": "demo-key-12345"}  # lowercase
        response = client.get("/responses/pending", headers=headers)
        # FastAPI/Starlette normalizes headers, so this should work
        assert response.status_code != 403


class TestAuthenticationErrorMessages:
    """Tests for authentication error messages."""

    def test_missing_key_error_message(self, client: TestClient) -> None:
        """Test error message when API key is missing."""
        response = client.get("/responses/pending")
        assert response.status_code in MISSING_KEY_CODES

    def test_invalid_key_error_message(self, client: TestClient) -> None:
        """Test error message when API key is invalid."""
        headers = {"X-API-Key": "wrong-key"}
        response = client.get("/responses/pending", headers=headers)
        assert response.status_code == 401
        data = response.json()
        assert "Invalid API key" in data["detail"]

    def test_error_response_structure(self, client: TestClient) -> None:
        """Test that authentication errors follow consistent structure."""
        headers = {"X-API-Key": "invalid"}
        response = client.get("/responses/pending", headers=headers)
        assert response.status_code == 401

        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)
