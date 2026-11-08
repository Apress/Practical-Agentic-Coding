"""Escalation engine for identifying tickets requiring human review."""

import re
from typing import List, Optional, Tuple

from models.escalation import (
    EscalationDetail,
    EscalationPriority,
    EscalationReason,
    EscalationResult,
    EscalationRule,
)
from models.ticket_analysis import TicketAnalysisResult, TicketCategory, TicketSentiment


class EscalationEngine:
    """
    Evaluates tickets against escalation rules to determine if human review is required.

    The engine checks multiple criteria:
    - Sentiment-based (angry or multiple negative indicators)
    - Financial thresholds (refunds over threshold)
    - Risk keywords (legal action, social media, competitors)
    - Confidence thresholds (low analyzer confidence)
    - Category matching (unknown/low confidence categories)

    All escalations include detailed reasoning for audit purposes.
    """

    def __init__(self, rules: Optional[EscalationRule] = None) -> None:
        """
        Initialize EscalationEngine with optional custom rules.

        Args:
            rules: Custom escalation rules. If None, uses default rules.
        """
        self.rules = rules if rules is not None else EscalationRule()

    def evaluate(
        self,
        ticket_id: str,
        ticket_content: str,
        analysis: TicketAnalysisResult,
        refund_amount_usd: Optional[float] = None,
    ) -> EscalationResult:
        """
        Evaluate a ticket for escalation based on analysis and content.

        Args:
            ticket_id: Unique ticket identifier
            ticket_content: Original ticket content for keyword detection
            analysis: TicketAnalysisResult from TicketAnalyzer
            refund_amount_usd: Optional refund amount if mentioned in ticket

        Returns:
            EscalationResult with escalation decision and detailed reasons

        Example:
            >>> engine = EscalationEngine()
            >>> result = engine.evaluate(
            ...     "TKT-001",
            ...     "I'm furious! I want to sue you!",
            ...     analysis,
            ...     refund_amount_usd=150.0
            ... )
            >>> result.requires_escalation
            True
            >>> len(result.escalation_reasons)
            3  # angry sentiment, legal threat, high refund
        """
        escalation_reasons: List[EscalationDetail] = []
        negative_indicators = 0

        # Check 1: Angry sentiment
        if self._check_angry_sentiment(analysis):
            reason = self._create_sentiment_detail(analysis)
            escalation_reasons.append(reason)
            negative_indicators += 1

        # Check 2: Low confidence scores
        confidence_reasons = self._check_low_confidence(analysis)
        escalation_reasons.extend(confidence_reasons)
        negative_indicators += len(confidence_reasons)

        # Check 3: Unknown or low confidence category
        if self._check_unknown_category(analysis):
            reason = self._create_unknown_category_detail(analysis)
            escalation_reasons.append(reason)
            negative_indicators += 1

        # Check 4: High value refund
        if refund_amount_usd is not None and self._check_high_refund(refund_amount_usd):
            reason = self._create_refund_detail(refund_amount_usd)
            escalation_reasons.append(reason)
            # High refunds are serious but don't count as "negative indicators"

        # Check 5: Legal threats
        legal_keywords = self._detect_keywords(
            ticket_content, self.rules.legal_keywords
        )
        if legal_keywords:
            reason = self._create_legal_detail(legal_keywords)
            escalation_reasons.append(reason)
            negative_indicators += 1

        # Check 6: Social media threats
        social_keywords = self._detect_keywords(
            ticket_content, self.rules.social_media_keywords
        )
        if social_keywords:
            reason = self._create_social_media_detail(social_keywords)
            escalation_reasons.append(reason)
            negative_indicators += 1

        # Check 7: Competitor mentions
        competitor_keywords = self._detect_keywords(
            ticket_content, self.rules.competitor_keywords
        )
        if competitor_keywords:
            reason = self._create_competitor_detail(competitor_keywords)
            escalation_reasons.append(reason)
            negative_indicators += 1

        # Check 8: Multiple negative indicators
        if negative_indicators >= self.rules.negative_indicator_threshold:
            # Add a specific reason for multiple negative indicators if not already angry
            if not self._check_angry_sentiment(analysis):
                reason = self._create_multiple_negative_detail(negative_indicators)
                escalation_reasons.append(reason)

        # Determine if escalation is required
        requires_escalation = len(escalation_reasons) > 0

        # Calculate priority level
        priority = self._calculate_priority(escalation_reasons, negative_indicators)

        # Determine if immediate attention is needed
        immediate_attention = self._requires_immediate_attention(
            escalation_reasons, analysis
        )

        return EscalationResult(
            ticket_id=ticket_id,
            requires_escalation=requires_escalation,
            escalation_priority=priority,
            escalation_reasons=escalation_reasons,
            negative_indicator_count=negative_indicators,
            requires_immediate_attention=immediate_attention,
        )

    def _check_angry_sentiment(self, analysis: TicketAnalysisResult) -> bool:
        """Check if sentiment is angry."""
        return analysis.sentiment == TicketSentiment.ANGRY

    def _check_low_confidence(
        self, analysis: TicketAnalysisResult
    ) -> List[EscalationDetail]:
        """Check for low confidence scores and return details for each."""
        details: List[EscalationDetail] = []

        # Check category confidence
        if analysis.category_confidence < self.rules.min_category_confidence:
            details.append(
                EscalationDetail(
                    reason=EscalationReason.LOW_CONFIDENCE,
                    description=f"Category confidence ({analysis.category_confidence:.2f}) "
                    f"below threshold ({self.rules.min_category_confidence:.2f})",
                    confidence_score=analysis.category_confidence,
                    threshold_value=self.rules.min_category_confidence,
                    actual_value=analysis.category_confidence,
                )
            )

        # Check urgency confidence
        if analysis.urgency_confidence < self.rules.min_urgency_confidence:
            details.append(
                EscalationDetail(
                    reason=EscalationReason.LOW_CONFIDENCE,
                    description=f"Urgency confidence ({analysis.urgency_confidence:.2f}) "
                    f"below threshold ({self.rules.min_urgency_confidence:.2f})",
                    confidence_score=analysis.urgency_confidence,
                    threshold_value=self.rules.min_urgency_confidence,
                    actual_value=analysis.urgency_confidence,
                )
            )

        # Check sentiment confidence
        if analysis.sentiment_confidence < self.rules.min_sentiment_confidence:
            details.append(
                EscalationDetail(
                    reason=EscalationReason.LOW_CONFIDENCE,
                    description=f"Sentiment confidence ({analysis.sentiment_confidence:.2f}) "
                    f"below threshold ({self.rules.min_sentiment_confidence:.2f})",
                    confidence_score=analysis.sentiment_confidence,
                    threshold_value=self.rules.min_sentiment_confidence,
                    actual_value=analysis.sentiment_confidence,
                )
            )

        return details

    def _check_unknown_category(self, analysis: TicketAnalysisResult) -> bool:
        """Check if category is unknown (GENERAL with low confidence)."""
        return (
            analysis.category == TicketCategory.GENERAL
            and analysis.category_confidence < self.rules.min_category_confidence
        )

    def _check_high_refund(self, refund_amount: float) -> bool:
        """Check if refund amount exceeds threshold."""
        return refund_amount >= self.rules.refund_threshold_usd

    def _detect_keywords(self, content: str, keywords: List[str]) -> List[str]:
        """
        Detect keywords in ticket content (case-insensitive).

        Args:
            content: Ticket content to search
            keywords: List of keywords to find

        Returns:
            List of matched keywords
        """
        content_lower = content.lower()
        matched = []

        for keyword in keywords:
            # Use word boundary regex for better matching
            pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
            if re.search(pattern, content_lower):
                matched.append(keyword)

        return matched

    def _create_sentiment_detail(self, analysis: TicketAnalysisResult) -> EscalationDetail:
        """Create escalation detail for angry sentiment."""
        return EscalationDetail(
            reason=EscalationReason.ANGRY_SENTIMENT,
            description=f"Customer sentiment detected as {analysis.sentiment.value.upper()} "
            f"with {analysis.sentiment_confidence:.0%} confidence",
            confidence_score=analysis.sentiment_confidence,
        )

    def _create_unknown_category_detail(
        self, analysis: TicketAnalysisResult
    ) -> EscalationDetail:
        """Create escalation detail for unknown category."""
        return EscalationDetail(
            reason=EscalationReason.UNKNOWN_CATEGORY,
            description=f"Ticket category unclear (GENERAL with only "
            f"{analysis.category_confidence:.0%} confidence)",
            confidence_score=analysis.category_confidence,
            threshold_value=self.rules.min_category_confidence,
            actual_value=analysis.category_confidence,
        )

    def _create_refund_detail(self, amount: float) -> EscalationDetail:
        """Create escalation detail for high refund amount."""
        return EscalationDetail(
            reason=EscalationReason.HIGH_VALUE_REFUND,
            description=f"Refund amount (${amount:.2f}) exceeds threshold "
            f"(${self.rules.refund_threshold_usd:.2f})",
            threshold_value=self.rules.refund_threshold_usd,
            actual_value=amount,
        )

    def _create_legal_detail(self, keywords: List[str]) -> EscalationDetail:
        """Create escalation detail for legal threats."""
        return EscalationDetail(
            reason=EscalationReason.LEGAL_THREAT,
            description=f"Customer mentioned potential legal action: {', '.join(keywords)}",
            matched_keywords=keywords,
        )

    def _create_social_media_detail(self, keywords: List[str]) -> EscalationDetail:
        """Create escalation detail for social media threats."""
        return EscalationDetail(
            reason=EscalationReason.SOCIAL_MEDIA_THREAT,
            description=f"Customer mentioned social media or public posting: {', '.join(keywords)}",
            matched_keywords=keywords,
        )

    def _create_competitor_detail(self, keywords: List[str]) -> EscalationDetail:
        """Create escalation detail for competitor mentions."""
        return EscalationDetail(
            reason=EscalationReason.COMPETITOR_MENTION,
            description=f"Customer mentioned competitors or switching: {', '.join(keywords)}",
            matched_keywords=keywords,
        )

    def _create_multiple_negative_detail(self, count: int) -> EscalationDetail:
        """Create escalation detail for multiple negative indicators."""
        return EscalationDetail(
            reason=EscalationReason.MULTIPLE_NEGATIVE_INDICATORS,
            description=f"Multiple negative indicators detected ({count} indicators)",
            actual_value=float(count),
            threshold_value=float(self.rules.negative_indicator_threshold),
        )

    def _calculate_priority(
        self, reasons: List[EscalationDetail], negative_count: int
    ) -> EscalationPriority:
        """
        Calculate escalation priority based on reasons.

        Priority levels:
        - CRITICAL: Angry sentiment + legal threat, or 4+ negative indicators
        - HIGH: Angry sentiment, legal threat, or 3+ negative indicators
        - MEDIUM: Social media threat, competitor mention, or 2 negative indicators
        - LOW: Single low confidence or other single indicator
        """
        if not reasons:
            return EscalationPriority.LOW

        reason_types = {r.reason for r in reasons}

        # CRITICAL: Combination of angry + legal, or many negative indicators
        if (
            EscalationReason.ANGRY_SENTIMENT in reason_types
            and EscalationReason.LEGAL_THREAT in reason_types
        ):
            return EscalationPriority.CRITICAL

        if negative_count >= 4:
            return EscalationPriority.CRITICAL

        # HIGH: Angry sentiment, legal threat, or many indicators
        if EscalationReason.ANGRY_SENTIMENT in reason_types:
            return EscalationPriority.HIGH

        if EscalationReason.LEGAL_THREAT in reason_types:
            return EscalationPriority.HIGH

        if negative_count >= 3:
            return EscalationPriority.HIGH

        # MEDIUM: Social media, competitor, or multiple indicators
        if EscalationReason.SOCIAL_MEDIA_THREAT in reason_types:
            return EscalationPriority.MEDIUM

        if EscalationReason.COMPETITOR_MENTION in reason_types:
            return EscalationPriority.MEDIUM

        if negative_count >= 2:
            return EscalationPriority.MEDIUM

        # LOW: Single indicator (high refund, single low confidence, etc.)
        return EscalationPriority.LOW

    def _requires_immediate_attention(
        self, reasons: List[EscalationDetail], analysis: TicketAnalysisResult
    ) -> bool:
        """
        Determine if ticket requires immediate (critical) attention.

        Immediate attention needed for:
        - Legal threats combined with angry sentiment
        - Critical priority escalations
        """
        reason_types = {r.reason for r in reasons}

        # Legal threat + angry = immediate attention
        if (
            EscalationReason.LEGAL_THREAT in reason_types
            and analysis.sentiment == TicketSentiment.ANGRY
        ):
            return True

        # Will be set to True by model_post_init if priority is CRITICAL
        return False

    def update_rules(self, rules: EscalationRule) -> None:
        """
        Update escalation rules.

        Args:
            rules: New escalation rules to apply
        """
        self.rules = rules
