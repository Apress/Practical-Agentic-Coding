"""
LinkForge - Pydantic v2 Schemas
Request/Response validation models.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(..., description="Service health status")
    version: str = Field(..., description="API version")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "version": "1.0.0"
            }
        }
    )


class LinkCreate(BaseModel):
    """Request schema for creating a shortened URL."""
    original_url: str = Field(
        ...,
        description="The URL to shorten",
        min_length=10,
        max_length=2048,
    )
    custom_code: Optional[str] = Field(
        None,
        description="Optional custom short code",
        min_length=4,
        max_length=10,
        pattern=r"^[a-zA-Z0-9_-]+$",
    )
    expires_in_days: Optional[int] = Field(
        None,
        description="Optional expiration in days",
        ge=1,
        le=365,
    )

    @field_validator("original_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate that the URL is well-formed."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "original_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "custom_code": None,
                "expires_in_days": 30
            }
        }
    )


class LinkResponse(BaseModel):
    """Response schema for link operations."""
    short_code: str = Field(..., description="The generated short code")
    original_url: str = Field(..., description="The original URL")
    created_at: datetime = Field(..., description="Creation timestamp")
    short_url: Optional[str] = Field(None, description="Full short URL")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "short_code": "abc123",
                "original_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "created_at": "2024-01-15T10:30:00Z",
                "short_url": "https://lnk.fg/abc123"
            }
        }
    )


class AnalyticsResponse(BaseModel):
    """Response schema for link analytics."""
    total_clicks: int = Field(..., description="Total number of clicks")
    unique_visitors: int = Field(..., description="Unique visitor count")
    clicks_today: int = Field(0, description="Clicks in the last 24 hours")
    clicks_this_week: int = Field(0, description="Clicks in the last 7 days")
    top_referrers: list[dict] = Field(
        default_factory=list,
        description="Top referrer sources"
    )
    top_countries: list[dict] = Field(
        default_factory=list,
        description="Top countries by clicks"
    )
    device_breakdown: dict = Field(
        default_factory=dict,
        description="Clicks by device type"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_clicks": 1523,
                "unique_visitors": 892,
                "clicks_today": 45,
                "clicks_this_week": 234,
                "top_referrers": [
                    {"source": "twitter.com", "clicks": 234},
                    {"source": "facebook.com", "clicks": 156}
                ],
                "top_countries": [
                    {"country": "US", "clicks": 567},
                    {"country": "GB", "clicks": 234}
                ],
                "device_breakdown": {
                    "mobile": 723,
                    "desktop": 645,
                    "tablet": 155
                }
            }
        }
    )


class ClickEvent(BaseModel):
    """Schema for analytics click events (internal use)."""
    link_id: int = Field(..., description="ID of the clicked link")
    short_code: str = Field(..., description="Short code that was clicked")
    clicked_at: datetime = Field(..., description="Click timestamp")
    referrer: Optional[str] = Field(None, description="HTTP referrer")
    user_agent: Optional[str] = Field(None, description="Browser user agent")
    ip_address: Optional[str] = Field(None, description="Client IP (hashed)")

    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    """Standard error response schema."""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code for debugging")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "Link not found",
                "error_code": "LINK_NOT_FOUND"
            }
        }
    )
