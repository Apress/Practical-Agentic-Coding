"""Ticket analysis service for classification, urgency assessment, and sentiment detection."""

import re
from typing import List, Tuple

from models.ticket_analysis import (
    EntityType,
    ExtractedEntity,
    TicketAnalysisResult,
    TicketCategory,
    TicketSentiment,
    TicketUrgency,
)


class TicketAnalyzer:
    """
    Analyzes support tickets to classify category, assess urgency, detect sentiment,
    and extract key entities.

    This class implements the business logic for ticket analysis while adhering to
    SupportFlow's constitution requirements for sentiment flagging and audit logging.
    """

    # Keywords for category classification
    _CATEGORY_KEYWORDS = {
        TicketCategory.BILLING: {
            "invoice",
            "payment",
            "charge",
            "billing",
            "refund",
            "credit card",
            "subscription",
            "bill",
            "fee",
            "cost",
            "price",
            "overcharged",
        },
        TicketCategory.TECHNICAL: {
            "error",
            "bug",
            "broken",
            "not working",
            "crash",
            "slow",
            "performance",
            "login",
            "access",
            "technical",
            "issue",
            "problem",
            "feature",
        },
        TicketCategory.ACCOUNT: {
            "account",
            "password",
            "username",
            "profile",
            "settings",
            "email",
            "phone",
            "update",
            "change",
            "reset",
            "verify",
        },
    }

    # Keywords for urgency assessment
    _URGENCY_KEYWORDS = {
        TicketUrgency.CRITICAL: {
            "critical",
            "emergency",
            "urgent",
            "immediately",
            "asap",
            "down",
            "outage",
            "security breach",
            "data loss",
        },
        TicketUrgency.HIGH: {
            "important",
            "high priority",
            "soon",
            "blocking",
            "cannot work",
            "business impact",
        },
        TicketUrgency.MEDIUM: {"help", "issue", "problem", "need", "should"},
    }

    # Keywords for sentiment detection
    _SENTIMENT_KEYWORDS = {
        TicketSentiment.ANGRY: {
            "furious",
            "outraged",
            "unacceptable",
            "disgusted",
            "terrible",
            "worst",
            "horrible",
            "incompetent",
            "ridiculous",
            "pathetic",
        },
        TicketSentiment.NEGATIVE: {
            "disappointed",
            "frustrated",
            "unhappy",
            "dissatisfied",
            "upset",
            "annoyed",
            "bad",
            "poor",
            "not satisfied",
        },
        TicketSentiment.POSITIVE: {
            "thank",
            "thanks",
            "appreciate",
            "great",
            "excellent",
            "good",
            "happy",
            "satisfied",
            "helpful",
            "wonderful",
        },
    }

    # Regex patterns for entity extraction
    _ENTITY_PATTERNS = {
        EntityType.ACCOUNT_ID: re.compile(
            r"\b(?:ACC|ACCT|ACCOUNT)[-_]?\d{4,10}\b", re.IGNORECASE
        ),
        EntityType.ORDER_NUMBER: re.compile(
            r"\b(?:ORD|ORDER)[-_]?\d{4,10}\b", re.IGNORECASE
        ),
        EntityType.PRODUCT_NAME: re.compile(
            r"\b(?:PRD|PRODUCT)[-_]?[A-Z0-9]{4,15}\b", re.IGNORECASE
        ),
    }

    def analyze(self, ticket_id: str, content: str) -> TicketAnalysisResult:
        """
        Perform complete analysis of a support ticket.

        Args:
            ticket_id: Unique identifier for the ticket
            content: The ticket content/description to analyze

        Returns:
            TicketAnalysisResult containing all analysis results

        Example:
            >>> analyzer = TicketAnalyzer()
            >>> result = analyzer.analyze(
            ...     "TKT-001",
            ...     "I'm very upset! My account ACC-123456 was overcharged."
            ... )
            >>> result.sentiment
            <TicketSentiment.NEGATIVE: 'negative'>
            >>> result.requires_priority_review
            True
        """
        content_lower = content.lower()

        # Classify category
        category, category_confidence = self._classify_category(content_lower)

        # Assess urgency
        urgency, urgency_confidence = self._assess_urgency(content_lower)

        # Detect sentiment
        sentiment, sentiment_confidence = self._detect_sentiment(content_lower)

        # Extract entities
        entities = self._extract_entities(content)

        # Determine if priority review is required (negative/angry sentiment)
        requires_priority_review = sentiment in (
            TicketSentiment.NEGATIVE,
            TicketSentiment.ANGRY,
        )

        return TicketAnalysisResult(
            ticket_id=ticket_id,
            category=category,
            category_confidence=category_confidence,
            urgency=urgency,
            urgency_confidence=urgency_confidence,
            sentiment=sentiment,
            sentiment_confidence=sentiment_confidence,
            extracted_entities=entities,
            requires_priority_review=requires_priority_review,
        )

    def _classify_category(self, content: str) -> Tuple[TicketCategory, float]:
        """
        Classify ticket into a category based on keyword matching.

        Args:
            content: Lowercase ticket content

        Returns:
            Tuple of (category, confidence_score)
        """
        category_scores = {}

        for category, keywords in self._CATEGORY_KEYWORDS.items():
            matches = sum(1 for keyword in keywords if keyword in content)
            if matches > 0:
                category_scores[category] = matches

        if not category_scores:
            return TicketCategory.GENERAL, 0.5

        # Get category with highest score
        best_category = max(category_scores, key=category_scores.get)
        total_matches = sum(category_scores.values())
        confidence = min(0.95, 0.6 + (category_scores[best_category] / total_matches) * 0.35)

        return best_category, round(confidence, 2)

    def _assess_urgency(self, content: str) -> Tuple[TicketUrgency, float]:
        """
        Assess ticket urgency based on keyword matching.

        Args:
            content: Lowercase ticket content

        Returns:
            Tuple of (urgency_level, confidence_score)
        """
        urgency_scores = {}

        for urgency, keywords in self._URGENCY_KEYWORDS.items():
            matches = sum(1 for keyword in keywords if keyword in content)
            if matches > 0:
                urgency_scores[urgency] = matches

        if not urgency_scores:
            return TicketUrgency.LOW, 0.6

        # Get highest urgency level detected (critical > high > medium)
        if TicketUrgency.CRITICAL in urgency_scores:
            confidence = min(0.95, 0.75 + urgency_scores[TicketUrgency.CRITICAL] * 0.1)
            return TicketUrgency.CRITICAL, round(confidence, 2)
        elif TicketUrgency.HIGH in urgency_scores:
            confidence = min(0.90, 0.70 + urgency_scores[TicketUrgency.HIGH] * 0.1)
            return TicketUrgency.HIGH, round(confidence, 2)
        elif TicketUrgency.MEDIUM in urgency_scores:
            confidence = min(0.85, 0.65 + urgency_scores[TicketUrgency.MEDIUM] * 0.05)
            return TicketUrgency.MEDIUM, round(confidence, 2)

        return TicketUrgency.LOW, 0.6

    def _detect_sentiment(self, content: str) -> Tuple[TicketSentiment, float]:
        """
        Detect customer sentiment based on keyword matching.

        Per SupportFlow constitution: negative/angry sentiment MUST be flagged
        for priority review.

        Args:
            content: Lowercase ticket content

        Returns:
            Tuple of (sentiment, confidence_score)
        """
        sentiment_scores = {}

        for sentiment, keywords in self._SENTIMENT_KEYWORDS.items():
            matches = sum(1 for keyword in keywords if keyword in content)
            if matches > 0:
                sentiment_scores[sentiment] = matches

        if not sentiment_scores:
            return TicketSentiment.NEUTRAL, 0.7

        # Prioritize detection: angry > negative > positive
        if TicketSentiment.ANGRY in sentiment_scores:
            confidence = min(0.95, 0.80 + sentiment_scores[TicketSentiment.ANGRY] * 0.05)
            return TicketSentiment.ANGRY, round(confidence, 2)
        elif TicketSentiment.NEGATIVE in sentiment_scores:
            confidence = min(0.92, 0.75 + sentiment_scores[TicketSentiment.NEGATIVE] * 0.05)
            return TicketSentiment.NEGATIVE, round(confidence, 2)
        elif TicketSentiment.POSITIVE in sentiment_scores:
            confidence = min(0.90, 0.70 + sentiment_scores[TicketSentiment.POSITIVE] * 0.05)
            return TicketSentiment.POSITIVE, round(confidence, 2)

        return TicketSentiment.NEUTRAL, 0.7

    def _extract_entities(self, content: str) -> List[ExtractedEntity]:
        """
        Extract key entities from ticket content using regex patterns.

        Args:
            content: Original ticket content (with original casing)

        Returns:
            List of extracted entities with confidence scores
        """
        entities: List[ExtractedEntity] = []

        for entity_type, pattern in self._ENTITY_PATTERNS.items():
            for match in pattern.finditer(content):
                # Base confidence on pattern specificity
                confidence = 0.90 if "-" in match.group() or "_" in match.group() else 0.75

                entities.append(
                    ExtractedEntity(
                        entity_type=entity_type,
                        value=match.group(),
                        confidence=confidence,
                        position=match.start(),
                    )
                )

        # Sort by position for consistent ordering
        return sorted(entities, key=lambda e: e.position)
