"""API request and response schemas for SupportFlow."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ===== Request Schemas =====


class TicketSubmitRequest(BaseModel):
    """Request schema for submitting a new ticket."""

    content: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Ticket content from customer",
        examples=["I need help with my billing. I was charged twice for the same order!"],
    )


class ResponseApproveRequest(BaseModel):
    """Request schema for approving a response."""

    reviewed_by: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Identifier of the human reviewer",
        examples=["reviewer@example.com", "john.doe"],
    )


class ResponseRejectRequest(BaseModel):
    """Request schema for rejecting a response."""

    reviewed_by: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Identifier of the human reviewer",
        examples=["reviewer@example.com", "john.doe"],
    )
    reason: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Reason for rejection",
        examples=["Response tone is too casual for this angry customer"],
    )


# ===== Response Schemas =====


class EntityResponse(BaseModel):
    """Response schema for an extracted entity."""

    entity_type: str = Field(..., description="Type of entity", examples=["order_id", "account_id"])
    value: str = Field(..., description="Entity value", examples=["ORDER-2024-5678"])
    confidence: float = Field(..., description="Confidence score", examples=[0.95])


class AnalysisResponse(BaseModel):
    """Response schema for ticket analysis."""

    category: str = Field(..., description="Ticket category", examples=["billing"])
    category_confidence: float = Field(..., description="Category confidence", examples=[0.92])
    urgency: str = Field(..., description="Urgency level", examples=["high"])
    urgency_confidence: float = Field(..., description="Urgency confidence", examples=[0.88])
    sentiment: str = Field(..., description="Customer sentiment", examples=["angry"])
    sentiment_confidence: float = Field(..., description="Sentiment confidence", examples=[0.95])
    requires_priority_review: bool = Field(
        ..., description="Whether ticket requires priority review", examples=[True]
    )
    extracted_entities: List[EntityResponse] = Field(
        default_factory=list, description="Entities extracted from ticket"
    )


class EscalationResponse(BaseModel):
    """Response schema for escalation evaluation."""

    should_escalate: bool = Field(..., description="Whether ticket should be escalated")
    priority: str = Field(..., description="Escalation priority", examples=["HIGH", "CRITICAL"])
    reasons: List[str] = Field(..., description="Reasons for escalation")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional escalation details")


class ResponseItemResponse(BaseModel):
    """Response schema for a generated response."""

    response_id: str = Field(..., description="Unique response identifier")
    ticket_id: str = Field(..., description="Associated ticket ID")
    body: str = Field(..., description="Response body text")
    status: str = Field(..., description="Response status", examples=["DRAFT", "APPROVED", "REJECTED"])
    requires_human_review: bool = Field(..., description="Whether response needs review")
    template_id: str = Field(..., description="Template used for generation")
    reviewed_by: Optional[str] = Field(None, description="Reviewer identifier")
    reviewed_at: Optional[datetime] = Field(None, description="Review timestamp")
    rejection_reason: Optional[str] = Field(None, description="Reason for rejection if rejected")
    created_at: datetime = Field(..., description="Creation timestamp")


class TicketResponse(BaseModel):
    """Response schema for ticket details."""

    ticket_id: str = Field(..., description="Unique ticket identifier")
    content: str = Field(..., description="Ticket content")
    created_at: datetime = Field(..., description="Creation timestamp")
    analysis: Optional[AnalysisResponse] = Field(None, description="Ticket analysis if available")
    escalation: Optional[EscalationResponse] = Field(None, description="Escalation info if available")
    responses: List[ResponseItemResponse] = Field(
        default_factory=list, description="Generated responses for this ticket"
    )


class TicketSubmitResponse(BaseModel):
    """Response schema for ticket submission."""

    ticket: TicketResponse = Field(..., description="Created ticket with analysis")
    draft_response: ResponseItemResponse = Field(..., description="Generated draft response")


class PendingResponsesResponse(BaseModel):
    """Response schema for pending responses list."""

    responses: List[ResponseItemResponse] = Field(..., description="List of pending responses")
    total: int = Field(..., description="Total number of pending responses")


class HealthResponse(BaseModel):
    """Response schema for health check."""

    status: str = Field(..., description="Service status", examples=["healthy"])
    timestamp: datetime = Field(..., description="Check timestamp")
    database: str = Field(..., description="Database status", examples=["connected"])


class ErrorResponse(BaseModel):
    """Response schema for errors."""

    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
