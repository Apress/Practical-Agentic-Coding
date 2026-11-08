"""Tests for the ResponseGenerator service."""

from datetime import datetime

import pytest

from models.response import (
    GeneratedResponse,
    ResponseApproval,
    ResponseStatus,
    ResponseTemplate,
    TemplateCategory,
)
from models.ticket_analysis import TicketAnalysisResult, TicketCategory, TicketSentiment, TicketUrgency
from services.response_generator import ResponseGenerator


class TestResponseGenerator:
    """Test suite for ResponseGenerator class."""

    @pytest.fixture
    def generator(self) -> ResponseGenerator:
        """Create a ResponseGenerator instance for testing."""
        return ResponseGenerator()

    @pytest.fixture
    def sample_template(self) -> ResponseTemplate:
        """Create a sample template for testing."""
        return ResponseTemplate(
            template_id="TMPL-TEST-001",
            category=TemplateCategory.BILLING,
            subject="Test Subject",
            body="Hello {customer_name}, regarding {issue}.",
            placeholders=["customer_name", "issue"],
            description="Test template",
        )

    def test_initialization_loads_default_templates(self, generator: ResponseGenerator) -> None:
        """Test that generator initializes with default templates."""
        # Should have templates for all categories
        billing_templates = generator.list_templates_by_category(TemplateCategory.BILLING)
        technical_templates = generator.list_templates_by_category(TemplateCategory.TECHNICAL)
        account_templates = generator.list_templates_by_category(TemplateCategory.ACCOUNT)
        general_templates = generator.list_templates_by_category(TemplateCategory.GENERAL)

        assert len(billing_templates) > 0
        assert len(technical_templates) > 0
        assert len(account_templates) > 0
        assert len(general_templates) > 0

    def test_add_template(self, generator: ResponseGenerator, sample_template: ResponseTemplate) -> None:
        """Test adding a new template to the library."""
        generator.add_template(sample_template)
        retrieved = generator.get_template("TMPL-TEST-001")

        assert retrieved is not None
        assert retrieved.template_id == sample_template.template_id
        assert retrieved.category == sample_template.category

    def test_add_duplicate_template_raises_error(
        self, generator: ResponseGenerator, sample_template: ResponseTemplate
    ) -> None:
        """Test that adding a duplicate template raises ValueError."""
        generator.add_template(sample_template)

        with pytest.raises(ValueError, match="already exists"):
            generator.add_template(sample_template)

    def test_get_template_not_found(self, generator: ResponseGenerator) -> None:
        """Test retrieving non-existent template returns None."""
        result = generator.get_template("NON-EXISTENT")
        assert result is None

    def test_list_templates_by_category(self, generator: ResponseGenerator) -> None:
        """Test filtering templates by category."""
        billing_templates = generator.list_templates_by_category(TemplateCategory.BILLING)

        assert len(billing_templates) > 0
        for template in billing_templates:
            assert template.category == TemplateCategory.BILLING

    def test_generate_response_basic(self, generator: ResponseGenerator) -> None:
        """Test basic response generation."""
        response = generator.generate_response(
            response_id="RESP-001",
            ticket_id="TKT-001",
            template_id="TMPL-BILLING-001",
            substitutions={
                "customer_name": "John Doe",
                "issue_description": "duplicate charge",
                "resolution_details": "processed a full refund",
                "balance_info": "$0.00",
            },
        )

        assert response.response_id == "RESP-001"
        assert response.ticket_id == "TKT-001"
        assert response.template_id == "TMPL-BILLING-001"
        assert "John Doe" in response.body
        assert "duplicate charge" in response.body

    def test_generate_response_always_draft_status(self, generator: ResponseGenerator) -> None:
        """
        Test that generated responses always have DRAFT status.
        This is a CRITICAL constitution requirement.
        """
        response = generator.generate_response(
            response_id="RESP-002",
            ticket_id="TKT-002",
            template_id="TMPL-GENERAL-001",
            substitutions={
                "customer_name": "Jane",
                "response_details": "we will look into this",
            },
        )

        assert response.status == ResponseStatus.DRAFT

    def test_generate_response_always_requires_human_review(
        self, generator: ResponseGenerator
    ) -> None:
        """
        Test that generated responses always require human review.
        This is a CRITICAL constitution requirement.
        """
        response = generator.generate_response(
            response_id="RESP-003",
            ticket_id="TKT-003",
            template_id="TMPL-GENERAL-001",
            substitutions={
                "customer_name": "Bob",
                "response_details": "issue resolved",
            },
        )

        assert response.requires_human_review is True

    def test_generate_response_missing_placeholders(self, generator: ResponseGenerator) -> None:
        """Test that missing placeholders raise ValueError."""
        with pytest.raises(ValueError, match="Missing required placeholders"):
            generator.generate_response(
                response_id="RESP-004",
                ticket_id="TKT-004",
                template_id="TMPL-BILLING-001",
                substitutions={
                    "customer_name": "Alice",
                    # Missing other required placeholders
                },
            )

    def test_generate_response_invalid_template(self, generator: ResponseGenerator) -> None:
        """Test that invalid template ID raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            generator.generate_response(
                response_id="RESP-005",
                ticket_id="TKT-005",
                template_id="INVALID-TEMPLATE",
                substitutions={},
            )

    def test_generate_response_sanitizes_internal_details(
        self, generator: ResponseGenerator
    ) -> None:
        """
        Test that internal details in substitutions are rejected.
        CRITICAL per CLAUDE.md: Never include internal error codes or system details.
        """
        with pytest.raises(ValueError, match="forbidden internal detail"):
            generator.generate_response(
                response_id="RESP-006",
                ticket_id="TKT-006",
                template_id="TMPL-GENERAL-001",
                substitutions={
                    "customer_name": "Charlie",
                    "response_details": "Error Code: 500 - Internal server error",
                },
            )

    def test_generate_response_rejects_sql_terms(self, generator: ResponseGenerator) -> None:
        """Test that SQL-related terms in substitutions are rejected."""
        with pytest.raises(ValueError, match="forbidden internal detail"):
            generator.generate_response(
                response_id="RESP-007",
                ticket_id="TKT-007",
                template_id="TMPL-GENERAL-001",
                substitutions={
                    "customer_name": "David",
                    "response_details": "SQL error occurred while processing",
                },
            )

    def test_generate_from_analysis_billing(self, generator: ResponseGenerator) -> None:
        """Test automatic template selection based on ticket analysis."""
        analysis = TicketAnalysisResult(
            ticket_id="TKT-008",
            category=TicketCategory.BILLING,
            category_confidence=0.9,
            urgency=TicketUrgency.HIGH,
            urgency_confidence=0.8,
            sentiment=TicketSentiment.NEGATIVE,
            sentiment_confidence=0.85,
            extracted_entities=[],
            requires_priority_review=True,
        )

        response = generator.generate_from_analysis(
            response_id="RESP-008",
            ticket_analysis=analysis,
            custom_substitutions={
                "customer_name": "Emma",
                "issue_description": "incorrect charge",
                "resolution_details": "reversed the charge",
                "balance_info": "corrected",
            },
        )

        assert response.ticket_id == "TKT-008"
        assert response.status == ResponseStatus.DRAFT
        assert response.requires_human_review is True
        assert "Emma" in response.body

    def test_generate_from_analysis_technical(self, generator: ResponseGenerator) -> None:
        """Test template selection for technical category."""
        analysis = TicketAnalysisResult(
            ticket_id="TKT-009",
            category=TicketCategory.TECHNICAL,
            category_confidence=0.92,
            urgency=TicketUrgency.MEDIUM,
            urgency_confidence=0.75,
            sentiment=TicketSentiment.NEUTRAL,
            sentiment_confidence=0.7,
            extracted_entities=[],
            requires_priority_review=False,
        )

        response = generator.generate_from_analysis(
            response_id="RESP-009",
            ticket_analysis=analysis,
            custom_substitutions={
                "customer_name": "Frank",
                "issue_summary": "Login page not loading",
                "resolution_action": "cleared your session cache",
            },
        )

        assert response.ticket_id == "TKT-009"
        assert "Frank" in response.body

    def test_approve_response(self, generator: ResponseGenerator) -> None:
        """Test approving a draft response."""
        # Generate a draft response
        draft_response = generator.generate_response(
            response_id="RESP-010",
            ticket_id="TKT-010",
            template_id="TMPL-GENERAL-001",
            substitutions={
                "customer_name": "Grace",
                "response_details": "resolved your issue",
            },
        )

        # Approve it
        approval = ResponseApproval(
            response_id="RESP-010",
            reviewer_id="AGENT-001",
            approved=True,
            feedback="Looks good",
        )

        approved_response = generator.approve_response(draft_response, approval)

        assert approved_response.status == ResponseStatus.APPROVED
        assert approved_response.reviewed_by == "AGENT-001"
        assert approved_response.reviewed_at is not None
        assert approved_response.requires_human_review is False

    def test_reject_response(self, generator: ResponseGenerator) -> None:
        """Test rejecting a draft response."""
        # Generate a draft response
        draft_response = generator.generate_response(
            response_id="RESP-011",
            ticket_id="TKT-011",
            template_id="TMPL-GENERAL-001",
            substitutions={
                "customer_name": "Henry",
                "response_details": "working on your issue",
            },
        )

        # Reject it
        approval = ResponseApproval(
            response_id="RESP-011",
            reviewer_id="AGENT-002",
            approved=False,
            feedback="Needs more detail",
        )

        rejected_response = generator.reject_response(draft_response, approval)

        assert rejected_response.status == ResponseStatus.REJECTED
        assert rejected_response.reviewed_by == "AGENT-002"
        assert rejected_response.reviewed_at is not None
        assert rejected_response.requires_human_review is False

    def test_cannot_approve_non_draft_response(self, generator: ResponseGenerator) -> None:
        """Test that non-draft responses cannot be approved."""
        # Create an already approved response
        approved_response = GeneratedResponse(
            response_id="RESP-012",
            ticket_id="TKT-012",
            template_id="TMPL-GENERAL-001",
            subject="Test",
            body="Test body",
            status=ResponseStatus.APPROVED,
            reviewed_at=datetime.utcnow(),
            reviewed_by="AGENT-003",
            requires_human_review=False,
        )

        approval = ResponseApproval(
            response_id="RESP-012",
            reviewer_id="AGENT-004",
            approved=True,
        )

        with pytest.raises(ValueError, match="Cannot approve response"):
            generator.approve_response(approved_response, approval)

    def test_cannot_reject_non_draft_response(self, generator: ResponseGenerator) -> None:
        """Test that non-draft responses cannot be rejected."""
        # Create an already approved response
        approved_response = GeneratedResponse(
            response_id="RESP-013",
            ticket_id="TKT-013",
            template_id="TMPL-GENERAL-001",
            subject="Test",
            body="Test body",
            status=ResponseStatus.APPROVED,
            reviewed_at=datetime.utcnow(),
            reviewed_by="AGENT-005",
            requires_human_review=False,
        )

        approval = ResponseApproval(
            response_id="RESP-013",
            reviewer_id="AGENT-006",
            approved=False,
        )

        with pytest.raises(ValueError, match="Cannot reject response"):
            generator.reject_response(approved_response, approval)

    def test_template_validates_no_internal_details(self) -> None:
        """Test that templates reject internal system details."""
        with pytest.raises(ValueError, match="forbidden internal detail"):
            ResponseTemplate(
                template_id="TMPL-BAD-001",
                category=TemplateCategory.GENERAL,
                subject="Test",
                body="We encountered error code 500 in the system",
                placeholders=[],
                description="Bad template",
            )

    def test_response_validates_no_internal_details(self) -> None:
        """Test that responses reject internal system details."""
        with pytest.raises(ValueError, match="forbidden internal detail"):
            GeneratedResponse(
                response_id="RESP-BAD-001",
                ticket_id="TKT-001",
                template_id="TMPL-001",
                subject="Test",
                body="Database error: SQL exception occurred",
                status=ResponseStatus.DRAFT,
            )

    def test_placeholder_substitution_works_correctly(
        self, generator: ResponseGenerator, sample_template: ResponseTemplate
    ) -> None:
        """Test that placeholder substitution works correctly."""
        generator.add_template(sample_template)

        response = generator.generate_response(
            response_id="RESP-014",
            ticket_id="TKT-014",
            template_id="TMPL-TEST-001",
            substitutions={
                "customer_name": "Test User",
                "issue": "sample issue",
            },
        )

        assert "{customer_name}" not in response.body
        assert "{issue}" not in response.body
        assert "Test User" in response.body
        assert "sample issue" in response.body

    def test_response_stores_substitutions(self, generator: ResponseGenerator) -> None:
        """Test that generated response stores substitution metadata."""
        substitutions = {
            "customer_name": "Isabel",
            "response_details": "issue is now resolved",
        }

        response = generator.generate_response(
            response_id="RESP-015",
            ticket_id="TKT-015",
            template_id="TMPL-GENERAL-001",
            substitutions=substitutions,
        )

        assert response.substitutions == substitutions

    def test_generated_response_has_timestamp(self, generator: ResponseGenerator) -> None:
        """Test that generated responses include generation timestamp."""
        response = generator.generate_response(
            response_id="RESP-016",
            ticket_id="TKT-016",
            template_id="TMPL-GENERAL-001",
            substitutions={
                "customer_name": "Jack",
                "response_details": "processed",
            },
        )

        assert response.generated_at is not None
        assert isinstance(response.generated_at, datetime)

    def test_approved_response_has_review_timestamp(self, generator: ResponseGenerator) -> None:
        """Test that approved responses include review timestamp."""
        draft = generator.generate_response(
            response_id="RESP-017",
            ticket_id="TKT-017",
            template_id="TMPL-GENERAL-001",
            substitutions={
                "customer_name": "Karen",
                "response_details": "completed",
            },
        )

        approval = ResponseApproval(
            response_id="RESP-017",
            reviewer_id="AGENT-007",
            approved=True,
        )

        approved = generator.approve_response(draft, approval)

        assert approved.reviewed_at is not None
        assert isinstance(approved.reviewed_at, datetime)
