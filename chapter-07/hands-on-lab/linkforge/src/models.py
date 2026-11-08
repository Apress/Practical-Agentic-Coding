"""
LinkForge - SQLAlchemy ORM Models
Database models for the URL shortener.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Index,
    Text,
)
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class User(Base):
    """
    User model for authentication and link ownership.

    Attributes:
        id: Primary key
        username: Unique username
        email: User email address
        api_key: API key for programmatic access
        created_at: Account creation timestamp
        links: Relationship to user's links
    """
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, index=True)
    username: str = Column(String(50), unique=True, nullable=False, index=True)
    email: str = Column(String(255), unique=True, nullable=False)
    api_key: Optional[str] = Column(String(64), unique=True, nullable=True)
    created_at: datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    links = relationship("Link", back_populates="user", lazy="selectin")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>"


class Link(Base):
    """
    Link model for storing shortened URLs.

    Attributes:
        id: Primary key
        user_id: Foreign key to owning user
        original_url: The full original URL
        short_code: The generated short code
        created_at: Link creation timestamp
        expires_at: Optional expiration timestamp
        click_count: Cached click counter
        user: Relationship to owning user
        analytics_events: Relationship to click events
    """
    __tablename__ = "links"
    __table_args__ = (
        Index("idx_links_short_code", "short_code"),
        Index("idx_links_user_id", "user_id"),
    )

    id: int = Column(Integer, primary_key=True, index=True)
    user_id: int = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    original_url: str = Column(Text, nullable=False)
    short_code: str = Column(String(10), unique=True, nullable=False, index=True)
    created_at: datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    expires_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)
    click_count: int = Column(Integer, default=0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="links")
    analytics_events = relationship(
        "AnalyticsEvent",
        back_populates="link",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Link(id={self.id}, short_code='{self.short_code}')>"

    @property
    def is_expired(self) -> bool:
        """Check if the link has expired."""
        if self.expires_at is None:
            return False
        expires_at = self.expires_at
        if expires_at.tzinfo is None:  # SQLite returns naive values; they are UTC
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) > expires_at


class AnalyticsEvent(Base):
    """
    Analytics event model for tracking clicks.

    Attributes:
        id: Primary key
        link_id: Foreign key to the clicked link
        clicked_at: Click timestamp
        referrer: HTTP referrer header
        user_agent: Browser user agent string
        ip_address: Client IP address (hashed for privacy)
        country_code: Geo-located country (optional)
        device_type: Detected device type
        link: Relationship to the clicked link
    """
    __tablename__ = "analytics_events"
    __table_args__ = (
        Index("idx_analytics_link_id", "link_id"),
        Index("idx_analytics_clicked_at", "clicked_at"),
    )

    id: int = Column(Integer, primary_key=True, index=True)
    link_id: int = Column(
        Integer,
        ForeignKey("links.id", ondelete="CASCADE"),
        nullable=False,
    )
    clicked_at: datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    referrer: Optional[str] = Column(String(2048), nullable=True)
    user_agent: Optional[str] = Column(String(512), nullable=True)
    ip_address: Optional[str] = Column(String(64), nullable=True)  # Hashed
    country_code: Optional[str] = Column(String(2), nullable=True)
    device_type: Optional[str] = Column(String(20), nullable=True)

    # Relationships
    link = relationship("Link", back_populates="analytics_events")

    def __repr__(self) -> str:
        return f"<AnalyticsEvent(id={self.id}, link_id={self.link_id})>"
