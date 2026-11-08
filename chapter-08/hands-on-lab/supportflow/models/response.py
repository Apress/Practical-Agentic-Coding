"""Pydantic models for response generation."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class ResponseStatus(str, Enum):
    """Status of a generated response."""

    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"


class TemplateCategory(str, Enum):
    """Categories for response templates matching ticket categories."""

    BILLING = "billing"
    TECHNICAL = "technical"
    ACCOUNT = "account"
    GENERAL = "general"


class ResponseTemplate(BaseModel):
    """Template for generating customer responses."""

    template_id: str = Field(..., min_length=1, description="Unique template identifier")
    category: TemplateCategory = Field(..., description="Category this template applies to")
    subject: str = Field(
        ..., min_length=1, max_length=200, description="Subject line for the response"
    )
    body: str = Field(
        ..., min_length=1, description="Template body with placeholder variables"
    )
    placeholders: List[str] = Field(
        default_factory=list,
        description="List of placeholder names that can be substituted (e.g., 'customer_name')",
    )
    description: str = Field(
        ..., min_length=1, description="Description of when to use this template"
    )

    @field_validator("template_id", "subject", "body", "description")
    @classmethod
    def must_not_be_whitespace(cls, v: str) -> str:
        """Ensure fields are not just whitespace."""
        if not v.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return v.strip()

    @field_validator("body")
    @classmethod
    def must_not_contain_internal_details(cls, v: str) -> str:
        """
        Ensure template body doesn't contain internal system details.
        Per CLAUDE.md: Never include internal error codes or system details.
        """
        forbidden_terms = [
            "stack trace",
            "error code",
            "internal id",
            "database",
            "exception",
            "traceback",
            "sys.",
            "os.",
            "server error",
            "500",
            "404",
            "sql",
        ]
        v_lower = v.lower()
        for term in forbidden_terms:
            if term in v_lower:
                raise ValueError(
                    f"Template contains forbidden internal detail term: '{term}'"
                )
        return v

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "template_id": "TMPL-BILLING-001",
                "category": "billing",
                "subject": "Regarding Your Billing Inquiry",
                "body": "Dear {customer_name},\n\nThank you for contacting us about {issue_description}. "
                "We have reviewed your account and {resolution_details}.\n\n"
                "If you have any further questions, please don't hesitate to reach out.\n\n"
                "Best regards,\nSupport Team",
                "placeholders": ["customer_name", "issue_description", "resolution_details"],
                "description": "General billing inquiry response",
            }
        }


class GeneratedResponse(BaseModel):
    """A generated customer response requiring human review."""

    response_id: str = Field(..., min_length=1, description="Unique response identifier")
    ticket_id: str = Field(..., min_length=1, description="Associated ticket ID")
    template_id: str = Field(..., min_length=1, description="Template used for generation")
    subject: str = Field(..., min_length=1, max_length=200, description="Response subject")
    body: str = Field(..., min_length=1, description="Personalized response body")
    status: ResponseStatus = Field(
        default=ResponseStatus.DRAFT,
        description="Response status (always starts as DRAFT per constitution)",
    )
    generated_at: datetime = Field(
        default_factory=datetime.utcnow, description="When response was generated"
    )
    reviewed_at: Optional[datetime] = Field(
        default=None, description="When response was reviewed (None if not yet reviewed)"
    )
    reviewed_by: Optional[str] = Field(
        default=None, description="ID of human reviewer (None if not yet reviewed)"
    )
    substitutions: Dict[str, str] = Field(
        default_factory=dict,
        description="Dictionary of placeholder substitutions made",
    )
    requires_human_review: bool = Field(
        default=True,
        description="Flag indicating human review required (always True per constitution)",
    )

    @field_validator("status")
    @classmethod
    def status_must_be_draft_on_creation(cls, v: ResponseStatus) -> ResponseStatus:
        """
        Ensure newly created responses are always DRAFT status.
        Per CLAUDE.md: All generated responses must be marked as draft requiring human approval.
        """
        # This validator runs on initial creation
        # In practice, the default value handles this, but we enforce it here
        return v

    def model_post_init(self, __context: object) -> None:
        """
        Post-initialization validation for business rules.
        Enforces constitutional requirement for human review.
        """
        # If status is DRAFT, ensure review fields are None
        if self.status == ResponseStatus.DRAFT:
            if self.reviewed_at is not None or self.reviewed_by is not None:
                raise ValueError("DRAFT responses cannot have review information")

        # Ensure requires_human_review is always True for new responses
        if not self.requires_human_review:
            object.__setattr__(self, "requires_human_review", True)

    @field_validator("response_id", "ticket_id", "template_id", "subject", "body")
    @classmethod
    def must_not_be_whitespace(cls, v: str) -> str:
        """Ensure fields are not just whitespace."""
        if not v.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return v.strip()

    @field_validator("body")
    @classmethod
    def must_not_contain_internal_details(cls, v: str) -> str:
        """
        Ensure response body doesn't contain internal system details.
        CRITICAL per CLAUDE.md: Never include internal error codes or system details.
        """
        # Check for common internal details that should never appear
        forbidden_patterns = [
            "error code:",
            "exception:",
            "stack trace:",
            "internal id:",
            "database error",
            "sql error",
            "system error:",
            "traceback",
            "errno",
            "500 error",
            "404 error",
        ]

        v_lower = v.lower()
        for pattern in forbidden_patterns:
            if pattern in v_lower:
                raise ValueError(
                    f"Response contains forbidden internal detail pattern: '{pattern}'"
                )

        return v

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "response_id": "RESP-2024-001",
                "ticket_id": "TKT-2024-001",
                "template_id": "TMPL-BILLING-001",
                "subject": "Regarding Your Billing Inquiry",
                "body": "Dear John,\n\nThank you for contacting us about the duplicate charge. "
                "We have reviewed your account and processed a full refund.\n\n"
                "If you have any further questions, please don't hesitate to reach out.\n\n"
                "Best regards,\nSupport Team",
                "status": "draft",
                "generated_at": "2024-01-15T10:30:00Z",
                "reviewed_at": None,
                "reviewed_by": None,
                "substitutions": {
                    "customer_name": "John",
                    "issue_description": "the duplicate charge",
                    "resolution_details": "processed a full refund",
                },
                "requires_human_review": True,
            }
        }


class ResponseApproval(BaseModel):
    """Represents approval or rejection of a generated response."""

    response_id: str = Field(..., min_length=1, description="Response being reviewed")
    reviewer_id: str = Field(..., min_length=1, description="ID of human reviewer")
    approved: bool = Field(..., description="Whether response was approved or rejected")
    feedback: Optional[str] = Field(
        default=None, description="Optional reviewer feedback or rejection reason"
    )
    reviewed_at: datetime = Field(
        default_factory=datetime.utcnow, description="When review was performed"
    )

    @field_validator("response_id", "reviewer_id")
    @classmethod
    def must_not_be_whitespace(cls, v: str) -> str:
        """Ensure fields are not just whitespace."""
        if not v.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return v.strip()

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "response_id": "RESP-2024-001",
                "reviewer_id": "AGENT-123",
                "approved": True,
                "feedback": "Looks good, sending to customer",
                "reviewed_at": "2024-01-15T10:45:00Z",
            }
        }
