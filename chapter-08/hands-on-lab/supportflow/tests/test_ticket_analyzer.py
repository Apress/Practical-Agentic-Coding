"""Tests for the TicketAnalyzer service."""

import pytest

from models.ticket_analysis import (
    EntityType,
    TicketCategory,
    TicketSentiment,
    TicketUrgency,
)
from services.ticket_analyzer import TicketAnalyzer


class TestTicketAnalyzer:
    """Test suite for TicketAnalyzer class."""

    @pytest.fixture
    def analyzer(self) -> TicketAnalyzer:
        """Create a TicketAnalyzer instance for testing."""
        return TicketAnalyzer()

    def test_billing_category_classification(self, analyzer: TicketAnalyzer) -> None:
        """Test that billing-related tickets are correctly classified."""
        content = "I was overcharged on my invoice. Please refund the extra payment."
        result = analyzer.analyze("TKT-001", content)

        assert result.category == TicketCategory.BILLING
        assert result.category_confidence > 0.6

    def test_technical_category_classification(self, analyzer: TicketAnalyzer) -> None:
        """Test that technical issues are correctly classified."""
        content = "The application keeps crashing with an error message. This bug is blocking my work."
        result = analyzer.analyze("TKT-002", content)

        assert result.category == TicketCategory.TECHNICAL
        assert result.category_confidence > 0.6

    def test_account_category_classification(self, analyzer: TicketAnalyzer) -> None:
        """Test that account-related tickets are correctly classified."""
        content = "I need to reset my password and update my email address in my account settings."
        result = analyzer.analyze("TKT-003", content)

        assert result.category == TicketCategory.ACCOUNT
        assert result.category_confidence > 0.6

    def test_general_category_fallback(self, analyzer: TicketAnalyzer) -> None:
        """Test that tickets with no clear category default to GENERAL."""
        content = "Hello, I have a question about your services."
        result = analyzer.analyze("TKT-004", content)

        assert result.category == TicketCategory.GENERAL
        assert result.category_confidence == 0.5

    def test_critical_urgency_assessment(self, analyzer: TicketAnalyzer) -> None:
        """Test that critical urgency is correctly detected."""
        content = "CRITICAL: Security breach detected! System is down. Need help IMMEDIATELY!"
        result = analyzer.analyze("TKT-005", content)

        assert result.urgency == TicketUrgency.CRITICAL
        assert result.urgency_confidence > 0.75

    def test_high_urgency_assessment(self, analyzer: TicketAnalyzer) -> None:
        """Test that high urgency is correctly detected."""
        content = "This is important and blocking our business. Need help soon."
        result = analyzer.analyze("TKT-006", content)

        assert result.urgency == TicketUrgency.HIGH
        assert result.urgency_confidence > 0.65

    def test_medium_urgency_assessment(self, analyzer: TicketAnalyzer) -> None:
        """Test that medium urgency is correctly detected."""
        content = "I have a problem that needs attention."
        result = analyzer.analyze("TKT-007", content)

        assert result.urgency == TicketUrgency.MEDIUM
        assert result.urgency_confidence > 0.6

    def test_low_urgency_default(self, analyzer: TicketAnalyzer) -> None:
        """Test that tickets with no urgency keywords default to LOW."""
        content = "Just wondering about something."
        result = analyzer.analyze("TKT-008", content)

        assert result.urgency == TicketUrgency.LOW
        assert result.urgency_confidence == 0.6

    def test_angry_sentiment_detection(self, analyzer: TicketAnalyzer) -> None:
        """Test that angry sentiment is correctly detected."""
        content = "This is absolutely unacceptable! Your service is terrible and pathetic!"
        result = analyzer.analyze("TKT-009", content)

        assert result.sentiment == TicketSentiment.ANGRY
        assert result.sentiment_confidence > 0.75

    def test_negative_sentiment_detection(self, analyzer: TicketAnalyzer) -> None:
        """Test that negative sentiment is correctly detected."""
        content = "I'm very disappointed and frustrated with this poor experience."
        result = analyzer.analyze("TKT-010", content)

        assert result.sentiment == TicketSentiment.NEGATIVE
        assert result.sentiment_confidence > 0.7

    def test_positive_sentiment_detection(self, analyzer: TicketAnalyzer) -> None:
        """Test that positive sentiment is correctly detected."""
        content = "Thank you for the excellent service! This is great and I'm very happy."
        result = analyzer.analyze("TKT-011", content)

        assert result.sentiment == TicketSentiment.POSITIVE
        assert result.sentiment_confidence > 0.65

    def test_neutral_sentiment_default(self, analyzer: TicketAnalyzer) -> None:
        """Test that tickets with no sentiment keywords default to NEUTRAL."""
        content = "I would like to inquire about the status of my request."
        result = analyzer.analyze("TKT-012", content)

        assert result.sentiment == TicketSentiment.NEUTRAL
        assert result.sentiment_confidence == 0.7

    def test_priority_review_for_negative_sentiment(self, analyzer: TicketAnalyzer) -> None:
        """
        Test that negative sentiment triggers priority review flag.
        This is a MANDATORY requirement per CLAUDE.md constitution.
        """
        content = "I'm unhappy with the bad service."
        result = analyzer.analyze("TKT-013", content)

        assert result.sentiment == TicketSentiment.NEGATIVE
        assert result.requires_priority_review is True

    def test_priority_review_for_angry_sentiment(self, analyzer: TicketAnalyzer) -> None:
        """
        Test that angry sentiment triggers priority review flag.
        This is a MANDATORY requirement per CLAUDE.md constitution.
        """
        content = "This is outrageous and unacceptable!"
        result = analyzer.analyze("TKT-014", content)

        assert result.sentiment == TicketSentiment.ANGRY
        assert result.requires_priority_review is True

    def test_no_priority_review_for_positive_sentiment(
        self, analyzer: TicketAnalyzer
    ) -> None:
        """Test that positive sentiment does not trigger priority review."""
        content = "Thank you for the great help!"
        result = analyzer.analyze("TKT-015", content)

        assert result.sentiment == TicketSentiment.POSITIVE
        assert result.requires_priority_review is False

    def test_account_id_extraction(self, analyzer: TicketAnalyzer) -> None:
        """Test that account IDs are correctly extracted."""
        content = "My account ACC-123456 has an issue."
        result = analyzer.analyze("TKT-016", content)

        assert len(result.extracted_entities) == 1
        entity = result.extracted_entities[0]
        assert entity.entity_type == EntityType.ACCOUNT_ID
        assert entity.value == "ACC-123456"
        assert entity.confidence >= 0.75

    def test_order_number_extraction(self, analyzer: TicketAnalyzer) -> None:
        """Test that order numbers are correctly extracted."""
        content = "I need help with order ORD-2024-5678."
        result = analyzer.analyze("TKT-017", content)

        assert len(result.extracted_entities) == 1
        entity = result.extracted_entities[0]
        assert entity.entity_type == EntityType.ORDER_NUMBER
        assert entity.value == "ORD-2024-5678"
        assert entity.confidence >= 0.75

    def test_product_name_extraction(self, analyzer: TicketAnalyzer) -> None:
        """Test that product names are correctly extracted."""
        content = "The product PRD-ABC123 is not working."
        result = analyzer.analyze("TKT-018", content)

        assert len(result.extracted_entities) == 1
        entity = result.extracted_entities[0]
        assert entity.entity_type == EntityType.PRODUCT_NAME
        assert entity.value == "PRD-ABC123"
        assert entity.confidence >= 0.75

    def test_multiple_entity_extraction(self, analyzer: TicketAnalyzer) -> None:
        """Test that multiple entities are extracted and sorted by position."""
        content = "Account ACC-789 has issue with order ORDER-5555 for product PRD-XYZ999."
        result = analyzer.analyze("TKT-019", content)

        assert len(result.extracted_entities) == 3

        # Verify entities are sorted by position
        assert result.extracted_entities[0].entity_type == EntityType.ACCOUNT_ID
        assert result.extracted_entities[1].entity_type == EntityType.ORDER_NUMBER
        assert result.extracted_entities[2].entity_type == EntityType.PRODUCT_NAME

    def test_no_entities_extracted(self, analyzer: TicketAnalyzer) -> None:
        """Test that tickets without entities return empty list."""
        content = "I have a general question about your service."
        result = analyzer.analyze("TKT-020", content)

        assert len(result.extracted_entities) == 0

    def test_ticket_id_preserved(self, analyzer: TicketAnalyzer) -> None:
        """Test that the ticket ID is correctly preserved in the result."""
        ticket_id = "TKT-CUSTOM-ID-001"
        content = "Test content"
        result = analyzer.analyze(ticket_id, content)

        assert result.ticket_id == ticket_id

    def test_analyzed_at_timestamp_set(self, analyzer: TicketAnalyzer) -> None:
        """Test that analysis timestamp is automatically set."""
        content = "Test content"
        result = analyzer.analyze("TKT-021", content)

        assert result.analyzed_at is not None

    def test_complex_real_world_ticket(self, analyzer: TicketAnalyzer) -> None:
        """Test analysis of a realistic complex ticket."""
        content = """
        I am extremely frustrated and disappointed with your service!

        My account ACC-456789 was charged twice for order ORD-2024-8888.
        This is completely unacceptable and I need an IMMEDIATE refund.

        The billing error has caused serious problems for my business.
        """
        result = analyzer.analyze("TKT-022", content)

        # Should be classified as billing
        assert result.category == TicketCategory.BILLING

        # Should have high/critical urgency due to "IMMEDIATE"
        assert result.urgency in (TicketUrgency.HIGH, TicketUrgency.CRITICAL)

        # Should detect negative/angry sentiment
        assert result.sentiment in (TicketSentiment.NEGATIVE, TicketSentiment.ANGRY)

        # MUST flag for priority review (constitution requirement)
        assert result.requires_priority_review is True

        # Should extract both account and order entities
        assert len(result.extracted_entities) == 2
        entity_types = {e.entity_type for e in result.extracted_entities}
        assert EntityType.ACCOUNT_ID in entity_types
        assert EntityType.ORDER_NUMBER in entity_types

    def test_case_insensitivity(self, analyzer: TicketAnalyzer) -> None:
        """Test that analysis is case-insensitive for keywords."""
        content_lower = "billing issue with refund"
        content_upper = "BILLING ISSUE WITH REFUND"
        content_mixed = "BiLLiNg IsSuE wItH ReFuNd"

        result_lower = analyzer.analyze("TKT-023", content_lower)
        result_upper = analyzer.analyze("TKT-024", content_upper)
        result_mixed = analyzer.analyze("TKT-025", content_mixed)

        # All should classify as billing
        assert result_lower.category == TicketCategory.BILLING
        assert result_upper.category == TicketCategory.BILLING
        assert result_mixed.category == TicketCategory.BILLING

    def test_entity_extraction_preserves_case(self, analyzer: TicketAnalyzer) -> None:
        """Test that extracted entities preserve original casing."""
        content = "Issue with account acc-12345 and ACCOUNT-67890"
        result = analyzer.analyze("TKT-026", content)

        # Should extract both with original casing
        assert len(result.extracted_entities) == 2
        values = {e.value for e in result.extracted_entities}
        assert "acc-12345" in values or "ACC-12345" in values
        assert "ACCOUNT-67890" in values
