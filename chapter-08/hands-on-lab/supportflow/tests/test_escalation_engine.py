"""Tests for the EscalationEngine service."""

import pytest

from models.escalation import (
    EscalationPriority,
    EscalationReason,
    EscalationRule,
)
from models.ticket_analysis import (
    TicketAnalysisResult,
    TicketCategory,
    TicketSentiment,
    TicketUrgency,
)
from services.escalation_engine import EscalationEngine


class TestEscalationEngine:
    """Test suite for EscalationEngine class."""

    @pytest.fixture
    def engine(self) -> EscalationEngine:
        """Create an EscalationEngine instance with default rules."""
        return EscalationEngine()

    @pytest.fixture
    def custom_engine(self) -> EscalationEngine:
        """Create an EscalationEngine with custom rules."""
        rules = EscalationRule(
            refund_threshold_usd=50.0,
            min_category_confidence=0.70,
            negative_indicator_threshold=3,
        )
        return EscalationEngine(rules)

    @pytest.fixture
    def normal_analysis(self) -> TicketAnalysisResult:
        """Create a normal analysis result (no escalation triggers)."""
        return TicketAnalysisResult(
            ticket_id="TKT-001",
            category=TicketCategory.BILLING,
            category_confidence=0.90,
            urgency=TicketUrgency.MEDIUM,
            urgency_confidence=0.85,
            sentiment=TicketSentiment.NEUTRAL,
            sentiment_confidence=0.80,
            extracted_entities=[],
            requires_priority_review=False,
        )

    def test_initialization_with_default_rules(self, engine: EscalationEngine) -> None:
        """Test that engine initializes with default rules."""
        assert engine.rules.refund_threshold_usd == 100.0
        assert engine.rules.min_category_confidence == 0.80
        assert engine.rules.negative_indicator_threshold == 2

    def test_initialization_with_custom_rules(self, custom_engine: EscalationEngine) -> None:
        """Test that engine can be initialized with custom rules."""
        assert custom_engine.rules.refund_threshold_usd == 50.0
        assert custom_engine.rules.min_category_confidence == 0.70
        assert custom_engine.rules.negative_indicator_threshold == 3

    def test_no_escalation_for_normal_ticket(
        self, engine: EscalationEngine, normal_analysis: TicketAnalysisResult
    ) -> None:
        """Test that normal tickets don't trigger escalation."""
        result = engine.evaluate(
            ticket_id="TKT-001",
            ticket_content="I have a question about my bill.",
            analysis=normal_analysis,
            refund_amount_usd=None,
        )

        assert result.requires_escalation is False
        assert len(result.escalation_reasons) == 0
        assert result.negative_indicator_count == 0

    def test_escalation_for_angry_sentiment(
        self, engine: EscalationEngine, normal_analysis: TicketAnalysisResult
    ) -> None:
        """Test that angry sentiment triggers escalation."""
        # Create analysis with angry sentiment
        angry_analysis = TicketAnalysisResult(
            ticket_id="TKT-002",
            category=TicketCategory.BILLING,
            category_confidence=0.90,
            urgency=TicketUrgency.HIGH,
            urgency_confidence=0.85,
            sentiment=TicketSentiment.ANGRY,
            sentiment_confidence=0.95,
            extracted_entities=[],
            requires_priority_review=True,
        )

        result = engine.evaluate(
            ticket_id="TKT-002",
            ticket_content="This is absolutely unacceptable!",
            analysis=angry_analysis,
        )

        assert result.requires_escalation is True
        assert result.escalation_priority == EscalationPriority.HIGH
        assert EscalationReason.ANGRY_SENTIMENT in [
            r.reason for r in result.escalation_reasons
        ]
        assert result.negative_indicator_count >= 1

    def test_escalation_for_high_refund(
        self, engine: EscalationEngine, normal_analysis: TicketAnalysisResult
    ) -> None:
        """Test that high refund amount triggers escalation."""
        result = engine.evaluate(
            ticket_id="TKT-003",
            ticket_content="I need a refund",
            analysis=normal_analysis,
            refund_amount_usd=150.0,
        )

        assert result.requires_escalation is True
        assert EscalationReason.HIGH_VALUE_REFUND in [
            r.reason for r in result.escalation_reasons
        ]

        # Find the refund detail
        refund_detail = next(
            r
            for r in result.escalation_reasons
            if r.reason == EscalationReason.HIGH_VALUE_REFUND
        )
        assert refund_detail.actual_value == 150.0
        assert refund_detail.threshold_value == 100.0

    def test_no_escalation_for_low_refund(
        self, engine: EscalationEngine, normal_analysis: TicketAnalysisResult
    ) -> None:
        """Test that refunds below threshold don't trigger escalation."""
        result = engine.evaluate(
            ticket_id="TKT-004",
            ticket_content="I need a small refund",
            analysis=normal_analysis,
            refund_amount_usd=50.0,
        )

        assert result.requires_escalation is False
        assert EscalationReason.HIGH_VALUE_REFUND not in [
            r.reason for r in result.escalation_reasons
        ]

    def test_escalation_for_legal_threat(
        self, engine: EscalationEngine, normal_analysis: TicketAnalysisResult
    ) -> None:
        """Test that legal threats trigger escalation."""
        result = engine.evaluate(
            ticket_id="TKT-005",
            ticket_content="I'm going to sue you and contact my lawyer!",
            analysis=normal_analysis,
        )

        assert result.requires_escalation is True
        assert result.escalation_priority == EscalationPriority.HIGH
        assert EscalationReason.LEGAL_THREAT in [
            r.reason for r in result.escalation_reasons
        ]

        # Check matched keywords
        legal_detail = next(
            r
            for r in result.escalation_reasons
            if r.reason == EscalationReason.LEGAL_THREAT
        )
        assert "sue" in legal_detail.matched_keywords
        assert "lawyer" in legal_detail.matched_keywords

    def test_escalation_for_social_media_threat(
        self, engine: EscalationEngine, normal_analysis: TicketAnalysisResult
    ) -> None:
        """Test that social media threats trigger escalation."""
        result = engine.evaluate(
            ticket_id="TKT-006",
            ticket_content="I'm posting this on Twitter and leaving a review!",
            analysis=normal_analysis,
        )

        assert result.requires_escalation is True
        assert EscalationReason.SOCIAL_MEDIA_THREAT in [
            r.reason for r in result.escalation_reasons
        ]

        # Check matched keywords
        social_detail = next(
            r
            for r in result.escalation_reasons
            if r.reason == EscalationReason.SOCIAL_MEDIA_THREAT
        )
        assert "twitter" in social_detail.matched_keywords
        assert "review" in social_detail.matched_keywords

    def test_escalation_for_competitor_mention(
        self, engine: EscalationEngine, normal_analysis: TicketAnalysisResult
    ) -> None:
        """Test that competitor mentions trigger escalation."""
        result = engine.evaluate(
            ticket_id="TKT-007",
            ticket_content="I'm switching to a competitor with better service!",
            analysis=normal_analysis,
        )

        assert result.requires_escalation is True
        assert EscalationReason.COMPETITOR_MENTION in [
            r.reason for r in result.escalation_reasons
        ]

    def test_escalation_for_low_confidence_category(
        self, engine: EscalationEngine
    ) -> None:
        """Test that low category confidence triggers escalation."""
        low_confidence_analysis = TicketAnalysisResult(
            ticket_id="TKT-008",
            category=TicketCategory.GENERAL,
            category_confidence=0.50,  # Below 0.80 threshold
            urgency=TicketUrgency.MEDIUM,
            urgency_confidence=0.85,
            sentiment=TicketSentiment.NEUTRAL,
            sentiment_confidence=0.80,
            extracted_entities=[],
            requires_priority_review=False,
        )

        result = engine.evaluate(
            ticket_id="TKT-008",
            ticket_content="Something unclear",
            analysis=low_confidence_analysis,
        )

        assert result.requires_escalation is True
        assert EscalationReason.LOW_CONFIDENCE in [
            r.reason for r in result.escalation_reasons
        ]
        assert EscalationReason.UNKNOWN_CATEGORY in [
            r.reason for r in result.escalation_reasons
        ]

    def test_escalation_for_low_confidence_sentiment(
        self, engine: EscalationEngine
    ) -> None:
        """Test that low sentiment confidence triggers escalation."""
        low_sentiment_analysis = TicketAnalysisResult(
            ticket_id="TKT-009",
            category=TicketCategory.BILLING,
            category_confidence=0.90,
            urgency=TicketUrgency.MEDIUM,
            urgency_confidence=0.85,
            sentiment=TicketSentiment.NEUTRAL,
            sentiment_confidence=0.60,  # Below 0.80 threshold
            extracted_entities=[],
            requires_priority_review=False,
        )

        result = engine.evaluate(
            ticket_id="TKT-009",
            ticket_content="I'm not sure how I feel",
            analysis=low_sentiment_analysis,
        )

        assert result.requires_escalation is True
        low_conf_reasons = [
            r for r in result.escalation_reasons if r.reason == EscalationReason.LOW_CONFIDENCE
        ]
        assert len(low_conf_reasons) >= 1

    def test_escalation_for_multiple_negative_indicators(
        self, engine: EscalationEngine
    ) -> None:
        """Test that multiple negative indicators trigger escalation."""
        negative_analysis = TicketAnalysisResult(
            ticket_id="TKT-010",
            category=TicketCategory.GENERAL,
            category_confidence=0.55,  # Low confidence
            urgency=TicketUrgency.MEDIUM,
            urgency_confidence=0.70,  # Low confidence
            sentiment=TicketSentiment.NEGATIVE,
            sentiment_confidence=0.85,
            extracted_entities=[],
            requires_priority_review=True,
        )

        result = engine.evaluate(
            ticket_id="TKT-010",
            ticket_content="I'm switching to a competitor!",
            analysis=negative_analysis,
        )

        assert result.requires_escalation is True
        # Should have: low category conf, low urgency conf, unknown category, competitor mention
        assert result.negative_indicator_count >= 2

    def test_critical_priority_for_angry_plus_legal(
        self, engine: EscalationEngine
    ) -> None:
        """Test that angry sentiment + legal threat = CRITICAL priority."""
        angry_analysis = TicketAnalysisResult(
            ticket_id="TKT-011",
            category=TicketCategory.BILLING,
            category_confidence=0.90,
            urgency=TicketUrgency.CRITICAL,
            urgency_confidence=0.85,
            sentiment=TicketSentiment.ANGRY,
            sentiment_confidence=0.95,
            extracted_entities=[],
            requires_priority_review=True,
        )

        result = engine.evaluate(
            ticket_id="TKT-011",
            ticket_content="This is unacceptable! I'm calling my lawyer!",
            analysis=angry_analysis,
        )

        assert result.requires_escalation is True
        assert result.escalation_priority == EscalationPriority.CRITICAL
        assert result.requires_immediate_attention is True
        assert EscalationReason.ANGRY_SENTIMENT in [
            r.reason for r in result.escalation_reasons
        ]
        assert EscalationReason.LEGAL_THREAT in [
            r.reason for r in result.escalation_reasons
        ]

    def test_high_priority_for_angry_sentiment_alone(
        self, engine: EscalationEngine
    ) -> None:
        """Test that angry sentiment alone = HIGH priority."""
        angry_analysis = TicketAnalysisResult(
            ticket_id="TKT-012",
            category=TicketCategory.BILLING,
            category_confidence=0.90,
            urgency=TicketUrgency.HIGH,
            urgency_confidence=0.85,
            sentiment=TicketSentiment.ANGRY,
            sentiment_confidence=0.95,
            extracted_entities=[],
            requires_priority_review=True,
        )

        result = engine.evaluate(
            ticket_id="TKT-012",
            ticket_content="I'm furious about this!",
            analysis=angry_analysis,
        )

        assert result.escalation_priority == EscalationPriority.HIGH

    def test_medium_priority_for_social_media(
        self, engine: EscalationEngine, normal_analysis: TicketAnalysisResult
    ) -> None:
        """Test that social media threat = MEDIUM priority."""
        result = engine.evaluate(
            ticket_id="TKT-013",
            ticket_content="I'm posting about this on Facebook",
            analysis=normal_analysis,
        )

        assert result.escalation_priority == EscalationPriority.MEDIUM

    def test_low_priority_for_single_low_confidence(
        self, engine: EscalationEngine
    ) -> None:
        """Test that single low confidence = LOW priority."""
        low_urgency_analysis = TicketAnalysisResult(
            ticket_id="TKT-014",
            category=TicketCategory.BILLING,
            category_confidence=0.90,
            urgency=TicketUrgency.MEDIUM,
            urgency_confidence=0.70,  # Only this is low
            sentiment=TicketSentiment.NEUTRAL,
            sentiment_confidence=0.85,
            extracted_entities=[],
            requires_priority_review=False,
        )

        result = engine.evaluate(
            ticket_id="TKT-014",
            ticket_content="Normal inquiry",
            analysis=low_urgency_analysis,
        )

        assert result.escalation_priority == EscalationPriority.LOW

    def test_update_rules(self, engine: EscalationEngine) -> None:
        """Test that rules can be updated."""
        new_rules = EscalationRule(
            refund_threshold_usd=200.0,
            min_category_confidence=0.90,
        )

        engine.update_rules(new_rules)

        assert engine.rules.refund_threshold_usd == 200.0
        assert engine.rules.min_category_confidence == 0.90

    def test_case_insensitive_keyword_detection(
        self, engine: EscalationEngine, normal_analysis: TicketAnalysisResult
    ) -> None:
        """Test that keyword detection is case-insensitive."""
        result = engine.evaluate(
            ticket_id="TKT-015",
            ticket_content="I'm calling my LAWYER and will SUE!",
            analysis=normal_analysis,
        )

        assert EscalationReason.LEGAL_THREAT in [
            r.reason for r in result.escalation_reasons
        ]

    def test_word_boundary_keyword_matching(
        self, engine: EscalationEngine, normal_analysis: TicketAnalysisResult
    ) -> None:
        """Test that keywords match on word boundaries."""
        # "sue" should match but not in "issue"
        result = engine.evaluate(
            ticket_id="TKT-016",
            ticket_content="I have an issue with my account",
            analysis=normal_analysis,
        )

        assert EscalationReason.LEGAL_THREAT not in [
            r.reason for r in result.escalation_reasons
        ]

        # But explicit "sue" should match
        result2 = engine.evaluate(
            ticket_id="TKT-017",
            ticket_content="I will sue",
            analysis=normal_analysis,
        )

        assert EscalationReason.LEGAL_THREAT in [
            r.reason for r in result2.escalation_reasons
        ]

    def test_escalation_reasons_stored_in_result(
        self, engine: EscalationEngine, normal_analysis: TicketAnalysisResult
    ) -> None:
        """Test that all escalation reasons are captured in result."""
        result = engine.evaluate(
            ticket_id="TKT-018",
            ticket_content="I'm angry, will sue, and posting on Twitter!",
            analysis=normal_analysis,
        )

        reason_types = {r.reason for r in result.escalation_reasons}
        assert EscalationReason.LEGAL_THREAT in reason_types
        assert EscalationReason.SOCIAL_MEDIA_THREAT in reason_types

    def test_negative_indicator_count_accurate(
        self, engine: EscalationEngine
    ) -> None:
        """Test that negative indicator count is accurate."""
        low_conf_analysis = TicketAnalysisResult(
            ticket_id="TKT-019",
            category=TicketCategory.GENERAL,
            category_confidence=0.50,
            urgency=TicketUrgency.MEDIUM,
            urgency_confidence=0.70,
            sentiment=TicketSentiment.NEGATIVE,
            sentiment_confidence=0.85,
            extracted_entities=[],
            requires_priority_review=True,
        )

        result = engine.evaluate(
            ticket_id="TKT-019",
            ticket_content="Switching to competitor",
            analysis=low_conf_analysis,
        )

        # Should count: low category conf, low urgency conf, unknown category, competitor
        assert result.negative_indicator_count >= 3

    def test_custom_threshold_honored(self, custom_engine: EscalationEngine) -> None:
        """Test that custom thresholds are honored."""
        analysis = TicketAnalysisResult(
            ticket_id="TKT-020",
            category=TicketCategory.BILLING,
            category_confidence=0.90,
            urgency=TicketUrgency.MEDIUM,
            urgency_confidence=0.85,
            sentiment=TicketSentiment.NEUTRAL,
            sentiment_confidence=0.80,
            extracted_entities=[],
            requires_priority_review=False,
        )

        # $75 refund should trigger with custom threshold of $50
        result = custom_engine.evaluate(
            ticket_id="TKT-020",
            ticket_content="Need refund",
            analysis=analysis,
            refund_amount_usd=75.0,
        )

        assert result.requires_escalation is True
        assert EscalationReason.HIGH_VALUE_REFUND in [
            r.reason for r in result.escalation_reasons
        ]

    def test_evaluation_timestamp_captured(
        self, engine: EscalationEngine, normal_analysis: TicketAnalysisResult
    ) -> None:
        """Test that evaluation timestamp is captured."""
        result = engine.evaluate(
            ticket_id="TKT-021",
            ticket_content="Test",
            analysis=normal_analysis,
        )

        assert result.evaluated_at is not None

    def test_complex_real_world_scenario(self, engine: EscalationEngine) -> None:
        """Test a complex real-world escalation scenario."""
        complex_analysis = TicketAnalysisResult(
            ticket_id="TKT-022",
            category=TicketCategory.BILLING,
            category_confidence=0.92,
            urgency=TicketUrgency.CRITICAL,
            urgency_confidence=0.88,
            sentiment=TicketSentiment.ANGRY,
            sentiment_confidence=0.96,
            extracted_entities=[],
            requires_priority_review=True,
        )

        result = engine.evaluate(
            ticket_id="TKT-022",
            ticket_content=(
                "I am absolutely furious! You charged me $250 incorrectly and "
                "I've had enough. I'm contacting my lawyer, the Better Business Bureau, "
                "and posting about this terrible experience on social media. "
                "I'm also switching to your competitor who has better service!"
            ),
            analysis=complex_analysis,
            refund_amount_usd=250.0,
        )

        # Should have multiple escalation reasons
        assert result.requires_escalation is True
        assert result.escalation_priority == EscalationPriority.CRITICAL
        assert result.requires_immediate_attention is True

        reason_types = {r.reason for r in result.escalation_reasons}
        assert EscalationReason.ANGRY_SENTIMENT in reason_types
        assert EscalationReason.HIGH_VALUE_REFUND in reason_types
        assert EscalationReason.LEGAL_THREAT in reason_types
        assert EscalationReason.SOCIAL_MEDIA_THREAT in reason_types
        assert EscalationReason.COMPETITOR_MENTION in reason_types

        # Multiple negative indicators
        assert result.negative_indicator_count >= 4
