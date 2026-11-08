"""Integration tests for audit logging.

The `client`, `test_db`, and `api_headers` fixtures come from
tests/integration/conftest.py.
"""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from database.models import AuditLog
from database.repositories import AuditLogRepository



class TestAuditLogging:
    """Tests for audit log creation."""

    def test_ticket_creation_logged(
        self, client: TestClient, test_db: Session, api_headers: dict
    ) -> None:
        """Test that ticket creation is logged to audit trail."""
        # Create a ticket
        response = client.post(
            "/tickets",
            json={"content": "I need help with my account settings and password reset"},
            headers=api_headers,
        )
        assert response.status_code == 201
        ticket_id = response.json()["ticket"]["ticket_id"]

        # Check audit log
        audit_repo = AuditLogRepository(test_db)
        logs = audit_repo.list_by_resource(resource_type="ticket", resource_id=ticket_id)

        # Should have at least ticket.created and ticket.analyzed
        assert len(logs) >= 2

        # Verify ticket.created log
        created_log = next((log for log in logs if log.action == "ticket.created"), None)
        assert created_log is not None
        assert created_log.resource_type == "ticket"
        assert created_log.resource_id == ticket_id
        assert created_log.user_id == api_headers["X-API-Key"]
        assert created_log.timestamp is not None

    def test_response_generation_logged(
        self, client: TestClient, test_db: Session, api_headers: dict
    ) -> None:
        """Test that response generation is logged."""
        # Create a ticket (which generates a response)
        response = client.post(
            "/tickets", json={"content": "Thank you for the great service!"}, headers=api_headers
        )
        assert response.status_code == 201
        response_id = response.json()["draft_response"]["response_id"]

        # Check audit log for response
        audit_repo = AuditLogRepository(test_db)
        logs = audit_repo.list_by_resource(resource_type="response", resource_id=response_id)

        # Should have response.generated log
        assert len(logs) >= 1
        generated_log = logs[0]
        assert generated_log.action == "response.generated"
        assert generated_log.resource_type == "response"
        assert generated_log.resource_id == response_id
        assert generated_log.user_id == "system"

    def test_approval_logged(
        self, client: TestClient, test_db: Session, api_headers: dict
    ) -> None:
        """Test that response approval is logged."""
        # Create a ticket
        create_response = client.post(
            "/tickets", json={"content": "I have a billing question"}, headers=api_headers
        )
        response_id = create_response.json()["draft_response"]["response_id"]

        # Approve the response
        reviewer = "reviewer@example.com"
        approve_response = client.post(
            f"/responses/{response_id}/approve", json={"reviewed_by": reviewer}, headers=api_headers
        )
        assert approve_response.status_code == 200

        # Check audit log
        audit_repo = AuditLogRepository(test_db)
        logs = audit_repo.list_by_resource(resource_type="response", resource_id=response_id)

        # Find approval log
        approval_log = next((log for log in logs if log.action == "response.approved"), None)
        assert approval_log is not None
        assert approval_log.user_id == reviewer
        assert approval_log.resource_id == response_id

    def test_rejection_logged(
        self, client: TestClient, test_db: Session, api_headers: dict
    ) -> None:
        """Test that response rejection is logged with reason."""
        # Create a ticket
        create_response = client.post(
            "/tickets",
            json={"content": "This is absolutely unacceptable! I demand a refund!"},
            headers=api_headers,
        )
        response_id = create_response.json()["draft_response"]["response_id"]

        # Reject the response
        reviewer = "reviewer@example.com"
        reason = "Response doesn't address customer's anger appropriately"
        reject_response = client.post(
            f"/responses/{response_id}/reject",
            json={"reviewed_by": reviewer, "reason": reason},
            headers=api_headers,
        )
        assert reject_response.status_code == 200

        # Check audit log
        audit_repo = AuditLogRepository(test_db)
        logs = audit_repo.list_by_resource(resource_type="response", resource_id=response_id)

        # Find rejection log
        rejection_log = next((log for log in logs if log.action == "response.rejected"), None)
        assert rejection_log is not None
        assert rejection_log.user_id == reviewer
        assert rejection_log.details is not None
        assert rejection_log.details["reason"] == reason

    def test_audit_log_timestamps(
        self, client: TestClient, test_db: Session, api_headers: dict
    ) -> None:
        """Test that all audit logs have valid timestamps."""
        # Create a ticket
        response = client.post(
            "/tickets", json={"content": "General inquiry about services"}, headers=api_headers
        )
        assert response.status_code == 201

        # Get all audit logs
        audit_repo = AuditLogRepository(test_db)
        logs = audit_repo.list_all(limit=100)

        # All logs should have timestamps
        for log in logs:
            assert log.timestamp is not None
            # Timestamp should be a datetime object
            assert hasattr(log.timestamp, "year")
            assert hasattr(log.timestamp, "month")

    def test_audit_log_details_structure(
        self, client: TestClient, test_db: Session, api_headers: dict
    ) -> None:
        """Test that audit log details follow expected structure."""
        # Create a ticket
        response = client.post(
            "/tickets",
            json={"content": "I need assistance with account management features"},
            headers=api_headers,
        )
        assert response.status_code == 201
        ticket_id = response.json()["ticket"]["ticket_id"]

        # Get audit logs
        audit_repo = AuditLogRepository(test_db)
        logs = audit_repo.list_by_resource(resource_type="ticket", resource_id=ticket_id)

        # Check details structure
        for log in logs:
            if log.details:
                assert isinstance(log.details, dict)
                # Details should be JSON-serializable content

    def test_multiple_operations_audit_trail(
        self, client: TestClient, test_db: Session, api_headers: dict
    ) -> None:
        """Test complete audit trail for multiple operations."""
        # Create ticket
        create_response = client.post(
            "/tickets", json={"content": "Help with subscription upgrade"}, headers=api_headers
        )
        ticket_id = create_response.json()["ticket"]["ticket_id"]
        response_id = create_response.json()["draft_response"]["response_id"]

        # Approve response
        client.post(
            f"/responses/{response_id}/approve",
            json={"reviewed_by": "reviewer1@example.com"},
            headers=api_headers,
        )

        # Check complete audit trail
        audit_repo = AuditLogRepository(test_db)
        all_logs = audit_repo.list_all(limit=100)

        # Should have multiple log entries
        assert len(all_logs) >= 4  # created, analyzed, generated, approved

        # Verify action types are present
        actions = [log.action for log in all_logs]
        assert "ticket.created" in actions
        assert "ticket.analyzed" in actions
        assert "response.generated" in actions
        assert "response.approved" in actions
