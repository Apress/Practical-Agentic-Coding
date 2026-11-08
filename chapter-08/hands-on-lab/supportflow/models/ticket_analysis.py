"""Pydantic models for ticket analysis results."""

from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field, field_validator


class TicketCategory(str, Enum):
    """Ticket category classification."""

    BILLING = "billing"
    TECHNICAL = "technical"
    ACCOUNT = "account"
    GENERAL = "general"


class TicketUrgency(str, Enum):
    """Ticket urgency level."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketSentiment(str, Enum):
    """Customer sentiment classification."""

    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    ANGRY = "angry"


class EntityType(str, Enum):
    """Types of entities that can be extracted from tickets."""

    ACCOUNT_ID = "account_id"
    ORDER_NUMBER = "order_number"
    PRODUCT_NAME = "product_name"


class ExtractedEntity(BaseModel):
    """Represents an extracted entity from a ticket."""

    entity_type: EntityType = Field(
        ..., description="The type of entity extracted"
    )
    value: str = Field(
        ..., min_length=1, description="The extracted entity value"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score for the extraction (0.0 to 1.0)",
    )
    position: int = Field(
        ..., ge=0, description="Character position in the original text"
    )

    @field_validator("value")
    @classmethod
    def value_must_not_be_whitespace(cls, v: str) -> str:
        """Ensure entity value is not just whitespace."""
        if not v.strip():
            raise ValueError("Entity value cannot be empty or whitespace")
        return v.strip()

    class Config:
        """Pydantic model configuration."""

        frozen = True  # Make immutable for safety


class TicketAnalysisResult(BaseModel):
    """Complete analysis result for a support ticket."""

    ticket_id: str = Field(..., min_length=1, description="Unique ticket identifier")
    category: TicketCategory = Field(..., description="Classified ticket category")
    category_confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score for category classification",
    )
    urgency: TicketUrgency = Field(..., description="Assessed urgency level")
    urgency_confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score for urgency assessment",
    )
    sentiment: TicketSentiment = Field(..., description="Detected customer sentiment")
    sentiment_confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score for sentiment detection",
    )
    extracted_entities: List[ExtractedEntity] = Field(
        default_factory=list, description="Entities extracted from ticket content"
    )
    analyzed_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when analysis was performed",
    )
    requires_priority_review: bool = Field(
        ...,
        description="Flag indicating if ticket requires priority review (negative/angry sentiment)",
    )

    @field_validator("ticket_id")
    @classmethod
    def ticket_id_must_not_be_whitespace(cls, v: str) -> str:
        """Ensure ticket ID is not just whitespace."""
        if not v.strip():
            raise ValueError("Ticket ID cannot be empty or whitespace")
        return v.strip()

    def model_post_init(self, __context: object) -> None:
        """Post-initialization validation for business rules."""
        # Ensure negative/angry sentiment is flagged for priority review
        if self.sentiment in (TicketSentiment.NEGATIVE, TicketSentiment.ANGRY):
            if not self.requires_priority_review:
                # This should never happen, but enforce the business rule
                object.__setattr__(self, "requires_priority_review", True)

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "ticket_id": "TKT-2024-001234",
                "category": "billing",
                "category_confidence": 0.92,
                "urgency": "high",
                "urgency_confidence": 0.87,
                "sentiment": "negative",
                "sentiment_confidence": 0.95,
                "extracted_entities": [
                    {
                        "entity_type": "account_id",
                        "value": "ACC-789456",
                        "confidence": 0.98,
                        "position": 45,
                    },
                    {
                        "entity_type": "order_number",
                        "value": "ORD-2024-5678",
                        "confidence": 0.94,
                        "position": 120,
                    },
                ],
                "analyzed_at": "2024-01-15T10:30:00Z",
                "requires_priority_review": True,
            }
        }
