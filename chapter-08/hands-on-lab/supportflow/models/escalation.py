"""Pydantic models for escalation logic and rules."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class EscalationReason(str, Enum):
    """Reasons why a ticket was escalated for human review."""

    ANGRY_SENTIMENT = "angry_sentiment"
    MULTIPLE_NEGATIVE_INDICATORS = "multiple_negative_indicators"
    HIGH_VALUE_REFUND = "high_value_refund"
    LEGAL_THREAT = "legal_threat"
    SOCIAL_MEDIA_THREAT = "social_media_threat"
    COMPETITOR_MENTION = "competitor_mention"
    LOW_CONFIDENCE = "low_confidence"
    UNKNOWN_CATEGORY = "unknown_category"
    MANUAL_ESCALATION = "manual_escalation"


class EscalationPriority(str, Enum):
    """Priority level for escalated tickets."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EscalationRule(BaseModel):
    """Configuration for escalation detection rules."""

    # Financial thresholds
    refund_threshold_usd: float = Field(
        default=100.0,
        ge=0.0,
        description="Minimum refund amount in USD that triggers escalation",
    )

    # Confidence thresholds
    min_category_confidence: float = Field(
        default=0.80,
        ge=0.0,
        le=1.0,
        description="Minimum category confidence to avoid escalation",
    )
    min_urgency_confidence: float = Field(
        default=0.80,
        ge=0.0,
        le=1.0,
        description="Minimum urgency confidence to avoid escalation",
    )
    min_sentiment_confidence: float = Field(
        default=0.80,
        ge=0.0,
        le=1.0,
        description="Minimum sentiment confidence to avoid escalation",
    )

    # Risk keywords
    legal_keywords: List[str] = Field(
        default_factory=lambda: [
            "lawyer",
            "attorney",
            "legal action",
            "sue",
            "lawsuit",
            "court",
            "legal",
            "consumer protection",
            "better business bureau",
            "bbb",
            "regulatory",
            "compliance",
        ],
        description="Keywords indicating legal threats",
    )

    social_media_keywords: List[str] = Field(
        default_factory=lambda: [
            "twitter",
            "facebook",
            "instagram",
            "social media",
            "reddit",
            "review",
            "yelp",
            "trustpilot",
            "public",
            "post online",
            "tell everyone",
        ],
        description="Keywords indicating social media threats",
    )

    competitor_keywords: List[str] = Field(
        default_factory=lambda: [
            "competitor",
            "switch to",
            "moving to",
            "alternative",
            "better service",
            "switching providers",
            "cancel subscription",
            "canceling",
        ],
        description="Keywords indicating competitor mentions or churn risk",
    )

    # Multiple negative indicators threshold
    negative_indicator_threshold: int = Field(
        default=2,
        ge=1,
        description="Number of negative indicators before escalation",
    )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "refund_threshold_usd": 100.0,
                "min_category_confidence": 0.80,
                "min_urgency_confidence": 0.80,
                "min_sentiment_confidence": 0.80,
                "legal_keywords": ["lawyer", "sue", "legal action"],
                "social_media_keywords": ["twitter", "facebook", "review"],
                "competitor_keywords": ["competitor", "switch to"],
                "negative_indicator_threshold": 2,
            }
        }


class EscalationDetail(BaseModel):
    """Detailed information about a specific escalation reason."""

    reason: EscalationReason = Field(..., description="The escalation reason")
    description: str = Field(
        ..., min_length=1, description="Human-readable explanation"
    )
    matched_keywords: List[str] = Field(
        default_factory=list, description="Keywords that triggered this reason"
    )
    confidence_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence score if relevant to this reason",
    )
    threshold_value: Optional[float] = Field(
        default=None, description="Threshold value if relevant to this reason"
    )
    actual_value: Optional[float] = Field(
        default=None, description="Actual value compared to threshold"
    )

    @field_validator("description")
    @classmethod
    def description_must_not_be_whitespace(cls, v: str) -> str:
        """Ensure description is not just whitespace."""
        if not v.strip():
            raise ValueError("Description cannot be empty or whitespace")
        return v.strip()

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "reason": "angry_sentiment",
                "description": "Customer sentiment detected as ANGRY with high confidence",
                "matched_keywords": [],
                "confidence_score": 0.95,
                "threshold_value": None,
                "actual_value": None,
            }
        }


class EscalationResult(BaseModel):
    """Result of escalation evaluation for a ticket."""

    ticket_id: str = Field(..., min_length=1, description="Ticket identifier")
    requires_escalation: bool = Field(
        ..., description="Whether ticket requires human escalation"
    )
    escalation_priority: EscalationPriority = Field(
        ..., description="Priority level for escalated tickets"
    )
    escalation_reasons: List[EscalationDetail] = Field(
        default_factory=list,
        description="List of reasons why escalation is required",
    )
    negative_indicator_count: int = Field(
        default=0, ge=0, description="Number of negative indicators detected"
    )
    evaluated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When escalation evaluation was performed",
    )
    requires_immediate_attention: bool = Field(
        default=False,
        description="Whether ticket requires immediate (critical) attention",
    )

    @field_validator("ticket_id")
    @classmethod
    def ticket_id_must_not_be_whitespace(cls, v: str) -> str:
        """Ensure ticket ID is not just whitespace."""
        if not v.strip():
            raise ValueError("Ticket ID cannot be empty or whitespace")
        return v.strip()

    def model_post_init(self, __context: object) -> None:
        """
        Post-initialization validation for business rules.
        Ensures escalation flags are consistent.
        """
        # If there are escalation reasons, requires_escalation must be True
        if len(self.escalation_reasons) > 0 and not self.requires_escalation:
            object.__setattr__(self, "requires_escalation", True)

        # Critical priority requires immediate attention
        if (
            self.escalation_priority == EscalationPriority.CRITICAL
            and not self.requires_immediate_attention
        ):
            object.__setattr__(self, "requires_immediate_attention", True)

        # If escalation is required but priority is not set properly
        if self.requires_escalation and self.escalation_priority is None:
            # Default to HIGH priority if not specified
            object.__setattr__(self, "escalation_priority", EscalationPriority.HIGH)

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "ticket_id": "TKT-2024-001",
                "requires_escalation": True,
                "escalation_priority": "high",
                "escalation_reasons": [
                    {
                        "reason": "angry_sentiment",
                        "description": "Customer sentiment is ANGRY",
                        "matched_keywords": [],
                        "confidence_score": 0.95,
                    },
                    {
                        "reason": "legal_threat",
                        "description": "Customer mentioned potential legal action",
                        "matched_keywords": ["lawyer", "sue"],
                    },
                ],
                "negative_indicator_count": 2,
                "evaluated_at": "2024-01-15T10:30:00Z",
                "requires_immediate_attention": True,
            }
        }
