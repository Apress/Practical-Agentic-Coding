"""SQLAlchemy database models for SupportFlow."""

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Ticket(Base):
    """Ticket database model."""

    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(String(50), unique=True, nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    analysis = relationship("TicketAnalysis", back_populates="ticket", uselist=False)
    responses = relationship("Response", back_populates="ticket")


class TicketAnalysis(Base):
    """Ticket analysis results database model."""

    __tablename__ = "ticket_analyses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False, unique=True)

    # Analysis results
    category = Column(String(50), nullable=False)
    category_confidence = Column(Float, nullable=False)
    urgency = Column(String(50), nullable=False)
    urgency_confidence = Column(Float, nullable=False)
    sentiment = Column(String(50), nullable=False)
    sentiment_confidence = Column(Float, nullable=False)
    requires_priority_review = Column(Integer, nullable=False)  # 0 or 1 (SQLite boolean)

    # Extracted entities (stored as JSON)
    extracted_entities = Column(JSON, nullable=False)

    # Escalation info (stored as JSON)
    escalation_data = Column(JSON, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    ticket = relationship("Ticket", back_populates="analysis")


class Response(Base):
    """Generated response database model."""

    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    response_id = Column(String(50), unique=True, nullable=False, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)

    # Response content
    template_id = Column(String(50), nullable=False)
    body = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="DRAFT")  # DRAFT, APPROVED, REJECTED
    requires_human_review = Column(Integer, nullable=False, default=1)  # 0 or 1 (SQLite boolean)

    # Approval tracking
    reviewed_by = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    ticket = relationship("Ticket", back_populates="responses")


class AuditLog(Base):
    """Audit log database model."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    action = Column(String(100), nullable=False, index=True)
    user_id = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)  # ticket, response, etc.
    resource_id = Column(String(100), nullable=False)
    details = Column(JSON, nullable=True)  # Before/after data, additional context
    ip_address = Column(String(50), nullable=True)

    def __repr__(self) -> str:
        """String representation of audit log entry."""
        return f"<AuditLog(action={self.action}, user={self.user_id}, resource={self.resource_type}:{self.resource_id})>"
