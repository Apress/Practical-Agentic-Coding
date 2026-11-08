"""Integration tests for complete SupportFlow API workflows.

The `client`, `test_db`, and `api_headers` fixtures come from
tests/integration/conftest.py.
"""

from fastapi.testclient import TestClient



class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self, client: TestClient) -> None:
        """Test health check endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "unhealthy"]
        assert "timestamp" in data
        assert "database" in data


class TestTicketSubmission:
    """Tests for ticket submission workflow."""

    def test_submit_ticket_success(self, client: TestClient, api_headers: dict) -> None:
        """Test successful ticket submission with analysis and response."""
        ticket_data = {
            "content": "I'm very angry! I was charged twice for order #12345. This is unacceptable!"
        }

        response = client.post("/tickets", json=ticket_data, headers=api_headers)
        assert response.status_code == 201

        data = response.json()

        # Verify ticket structure
        assert "ticket" in data
        assert "draft_response" in data

        ticket = data["ticket"]
        assert "ticket_id" in ticket
        assert ticket["content"] == ticket_data["content"]
        assert "created_at" in ticket

        # Verify analysis
        assert "analysis" in ticket
        analysis = ticket["analysis"]
        assert "category" in analysis
        assert "sentiment" in analysis
        assert "urgency" in analysis
        assert "requires_priority_review" in analysis
        assert isinstance(analysis["extracted_entities"], list)

        # Verify escalation
        assert "escalation" in ticket
        escalation = ticket["escalation"]
        assert "should_escalate" in escalation
        assert "priority" in escalation
        assert isinstance(escalation["reasons"], list)

        # Verify draft response
        draft = data["draft_response"]
        assert "response_id" in draft
        assert draft["status"] == "DRAFT"
        assert draft["requires_human_review"] is True
        assert len(draft["body"]) > 0
        assert draft["reviewed_by"] is None

    def test_submit_ticket_without_auth(self, client: TestClient) -> None:
        """Test ticket submission without authentication fails."""
        ticket_data = {"content": "I need help with my account"}

        response = client.post("/tickets", json=ticket_data)
        # FastAPI's APIKeyHeader rejects a missing header before our dependency
        # runs; the code it uses has changed across versions (403 then 401).
        assert response.status_code in (401, 403)

    def test_submit_ticket_invalid_content(self, client: TestClient, api_headers: dict) -> None:
        """Test ticket submission with invalid content fails validation."""
        # Content too short
        ticket_data = {"content": "Help"}

        response = client.post("/tickets", json=ticket_data, headers=api_headers)
        assert response.status_code == 422  # Validation error


class TestTicketRetrieval:
    """Tests for ticket retrieval."""

    def test_get_ticket_success(self, client: TestClient, api_headers: dict) -> None:
        """Test retrieving a ticket with full details."""
        # First create a ticket
        create_response = client.post(
            "/tickets",
            json={"content": "I have a question about billing and my account settings"},
            headers=api_headers,
        )
        assert create_response.status_code == 201
        ticket_id = create_response.json()["ticket"]["ticket_id"]

        # Retrieve the ticket
        response = client.get(f"/tickets/{ticket_id}", headers=api_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["ticket_id"] == ticket_id
        assert "content" in data
        assert "analysis" in data
        assert "responses" in data
        assert isinstance(data["responses"], list)
        assert len(data["responses"]) >= 1  # Should have draft response

    def test_get_nonexistent_ticket(self, client: TestClient, api_headers: dict) -> None:
        """Test retrieving a non-existent ticket returns 404."""
        response = client.get("/tickets/TKT-NONEXISTENT", headers=api_headers)
        assert response.status_code == 404


class TestPendingResponses:
    """Tests for pending responses list."""

    def test_list_pending_responses(self, client: TestClient, api_headers: dict) -> None:
        """Test listing responses awaiting review."""
        # Create a ticket with draft response
        create_response = client.post(
            "/tickets",
            json={"content": "I need assistance with my subscription renewal process"},
            headers=api_headers,
        )
        assert create_response.status_code == 201

        # List pending responses
        response = client.get("/responses/pending", headers=api_headers)
        assert response.status_code == 200

        data = response.json()
        assert "responses" in data
        assert "total" in data
        assert isinstance(data["responses"], list)
        assert data["total"] >= 1

        # Verify response structure
        if data["responses"]:
            resp = data["responses"][0]
            assert "response_id" in resp
            assert "ticket_id" in resp
            assert resp["status"] == "DRAFT"
            assert resp["requires_human_review"] is True


class TestResponseApproval:
    """Tests for response approval workflow."""

    def test_approve_response_success(self, client: TestClient, api_headers: dict) -> None:
        """Test successfully approving a draft response."""
        # Create a ticket with draft response
        create_response = client.post(
            "/tickets",
            json={"content": "Thank you for your help! I just need to update my email address."},
            headers=api_headers,
        )
        assert create_response.status_code == 201
        response_id = create_response.json()["draft_response"]["response_id"]

        # Approve the response
        approval_data = {"reviewed_by": "reviewer@example.com"}
        response = client.post(
            f"/responses/{response_id}/approve", json=approval_data, headers=api_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["response_id"] == response_id
        assert data["status"] == "APPROVED"
        assert data["reviewed_by"] == "reviewer@example.com"
        assert data["reviewed_at"] is not None

    def test_approve_nonexistent_response(self, client: TestClient, api_headers: dict) -> None:
        """Test approving a non-existent response returns 404."""
        approval_data = {"reviewed_by": "reviewer@example.com"}
        response = client.post(
            "/responses/RESP-NONEXISTENT/approve", json=approval_data, headers=api_headers
        )
        assert response.status_code == 404

    def test_approve_already_approved_response(
        self, client: TestClient, api_headers: dict
    ) -> None:
        """Test approving an already-approved response returns error."""
        # Create and approve a response
        create_response = client.post(
            "/tickets",
            json={"content": "I need help with password reset procedure"},
            headers=api_headers,
        )
        response_id = create_response.json()["draft_response"]["response_id"]

        approval_data = {"reviewed_by": "reviewer1@example.com"}
        client.post(f"/responses/{response_id}/approve", json=approval_data, headers=api_headers)

        # Try to approve again
        response = client.post(
            f"/responses/{response_id}/approve",
            json={"reviewed_by": "reviewer2@example.com"},
            headers=api_headers,
        )
        assert response.status_code == 400  # Bad request - already reviewed


class TestResponseRejection:
    """Tests for response rejection workflow."""

    def test_reject_response_success(self, client: TestClient, api_headers: dict) -> None:
        """Test successfully rejecting a draft response."""
        # Create a ticket with draft response
        create_response = client.post(
            "/tickets",
            json={"content": "This service is terrible! I want a full refund immediately!"},
            headers=api_headers,
        )
        assert create_response.status_code == 201
        response_id = create_response.json()["draft_response"]["response_id"]

        # Reject the response
        rejection_data = {
            "reviewed_by": "reviewer@example.com",
            "reason": "Response tone doesn't match customer's angry sentiment",
        }
        response = client.post(
            f"/responses/{response_id}/reject", json=rejection_data, headers=api_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["response_id"] == response_id
        assert data["status"] == "REJECTED"
        assert data["reviewed_by"] == "reviewer@example.com"
        assert data["reviewed_at"] is not None
        assert data["rejection_reason"] == rejection_data["reason"]

    def test_reject_without_reason_fails(self, client: TestClient, api_headers: dict) -> None:
        """Test rejecting without reason fails validation."""
        create_response = client.post(
            "/tickets", json={"content": "I have a general inquiry"}, headers=api_headers
        )
        response_id = create_response.json()["draft_response"]["response_id"]

        # Try to reject without reason
        rejection_data = {"reviewed_by": "reviewer@example.com", "reason": ""}
        response = client.post(
            f"/responses/{response_id}/reject", json=rejection_data, headers=api_headers
        )
        assert response.status_code == 422  # Validation error


class TestCompleteWorkflow:
    """Tests for complete end-to-end workflows."""

    def test_complete_happy_path(self, client: TestClient, api_headers: dict) -> None:
        """Test complete workflow: submit → analyze → generate → approve."""
        # Step 1: Submit ticket
        submit_response = client.post(
            "/tickets",
            json={
                "content": "I really appreciate your excellent customer service! "
                "Could you help me upgrade my subscription plan?"
            },
            headers=api_headers,
        )
        assert submit_response.status_code == 201

        ticket_data = submit_response.json()
        ticket_id = ticket_data["ticket"]["ticket_id"]
        response_id = ticket_data["draft_response"]["response_id"]

        # Verify sentiment is positive
        assert ticket_data["ticket"]["analysis"]["sentiment"] == "positive"

        # Step 2: Verify ticket exists
        get_response = client.get(f"/tickets/{ticket_id}", headers=api_headers)
        assert get_response.status_code == 200

        # Step 3: Check pending responses
        pending_response = client.get("/responses/pending", headers=api_headers)
        assert pending_response.status_code == 200
        assert any(r["response_id"] == response_id for r in pending_response.json()["responses"])

        # Step 4: Approve response
        approve_response = client.post(
            f"/responses/{response_id}/approve",
            json={"reviewed_by": "qa-reviewer@example.com"},
            headers=api_headers,
        )
        assert approve_response.status_code == 200
        assert approve_response.json()["status"] == "APPROVED"

        # Step 5: Verify response no longer in pending
        pending_after = client.get("/responses/pending", headers=api_headers)
        assert not any(
            r["response_id"] == response_id for r in pending_after.json()["responses"]
        )

    def test_angry_customer_workflow(self, client: TestClient, api_headers: dict) -> None:
        """Test workflow for angry customer requiring escalation."""
        # Submit angry ticket
        submit_response = client.post(
            "/tickets",
            json={
                "content": "This is OUTRAGEOUS! I've been waiting for 3 weeks and nothing! "
                "I demand to speak to your supervisor immediately! "
                "I will contact my lawyer if this isn't resolved TODAY!"
            },
            headers=api_headers,
        )
        assert submit_response.status_code == 201

        ticket_data = submit_response.json()

        # Verify angry sentiment detected
        analysis = ticket_data["ticket"]["analysis"]
        assert analysis["sentiment"] == "angry"
        assert analysis["requires_priority_review"] is True

        # Verify escalation triggered
        escalation = ticket_data["ticket"]["escalation"]
        assert escalation["should_escalate"] is True
        assert escalation["priority"] in ["HIGH", "CRITICAL"]
        assert len(escalation["reasons"]) > 0

        # Response still requires human review
        draft = ticket_data["draft_response"]
        assert draft["status"] == "DRAFT"
        assert draft["requires_human_review"] is True
