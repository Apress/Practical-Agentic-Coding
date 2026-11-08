"""Data access repositories for SupportFlow."""

from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from database.models import AuditLog, Response, Ticket, TicketAnalysis


class TicketRepository:
    """Repository for ticket data access."""

    def __init__(self, db: Session) -> None:
        """Initialize repository with database session."""
        self.db = db

    def create(self, ticket_id: str, content: str) -> Ticket:
        """Create a new ticket."""
        ticket = Ticket(ticket_id=ticket_id, content=content)
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def get_by_ticket_id(self, ticket_id: str) -> Optional[Ticket]:
        """Get ticket by ticket_id."""
        return self.db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()

    def get_by_id(self, id: int) -> Optional[Ticket]:
        """Get ticket by database ID."""
        return self.db.query(Ticket).filter(Ticket.id == id).first()

    def list_all(self, limit: int = 100) -> List[Ticket]:
        """List all tickets with optional limit."""
        return self.db.query(Ticket).order_by(Ticket.created_at.desc()).limit(limit).all()


class TicketAnalysisRepository:
    """Repository for ticket analysis data access."""

    def __init__(self, db: Session) -> None:
        """Initialize repository with database session."""
        self.db = db

    def create(
        self,
        ticket_id: int,
        category: str,
        category_confidence: float,
        urgency: str,
        urgency_confidence: float,
        sentiment: str,
        sentiment_confidence: float,
        requires_priority_review: bool,
        extracted_entities: List[Dict[str, str]],
        escalation_data: Optional[Dict[str, str]] = None,
    ) -> TicketAnalysis:
        """Create ticket analysis record."""
        analysis = TicketAnalysis(
            ticket_id=ticket_id,
            category=category,
            category_confidence=category_confidence,
            urgency=urgency,
            urgency_confidence=urgency_confidence,
            sentiment=sentiment,
            sentiment_confidence=sentiment_confidence,
            requires_priority_review=1 if requires_priority_review else 0,
            extracted_entities=extracted_entities,
            escalation_data=escalation_data,
        )
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis

    def get_by_ticket_id(self, ticket_id: int) -> Optional[TicketAnalysis]:
        """Get analysis by ticket database ID."""
        return self.db.query(TicketAnalysis).filter(TicketAnalysis.ticket_id == ticket_id).first()


class ResponseRepository:
    """Repository for response data access."""

    def __init__(self, db: Session) -> None:
        """Initialize repository with database session."""
        self.db = db

    def create(
        self,
        response_id: str,
        ticket_id: int,
        template_id: str,
        body: str,
        status: str = "DRAFT",
        requires_human_review: bool = True,
    ) -> Response:
        """Create a new response."""
        response = Response(
            response_id=response_id,
            ticket_id=ticket_id,
            template_id=template_id,
            body=body,
            status=status,
            requires_human_review=1 if requires_human_review else 0,
        )
        self.db.add(response)
        self.db.commit()
        self.db.refresh(response)
        return response

    def get_by_response_id(self, response_id: str) -> Optional[Response]:
        """Get response by response_id."""
        return self.db.query(Response).filter(Response.response_id == response_id).first()

    def list_pending(self, limit: int = 100) -> List[Response]:
        """List all responses with DRAFT status."""
        return (
            self.db.query(Response)
            .filter(Response.status == "DRAFT")
            .order_by(Response.created_at.desc())
            .limit(limit)
            .all()
        )

    def approve(self, response_id: str, reviewed_by: str) -> Optional[Response]:
        """Approve a response."""
        response = self.get_by_response_id(response_id)
        if not response:
            return None

        response.status = "APPROVED"
        response.reviewed_by = reviewed_by
        response.reviewed_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(response)
        return response

    def reject(self, response_id: str, reviewed_by: str, reason: str) -> Optional[Response]:
        """Reject a response with feedback."""
        response = self.get_by_response_id(response_id)
        if not response:
            return None

        response.status = "REJECTED"
        response.reviewed_by = reviewed_by
        response.reviewed_at = datetime.utcnow()
        response.rejection_reason = reason
        self.db.commit()
        self.db.refresh(response)
        return response


class AuditLogRepository:
    """Repository for audit log data access."""

    def __init__(self, db: Session) -> None:
        """Initialize repository with database session."""
        self.db = db

    def create(
        self,
        action: str,
        user_id: str,
        resource_type: str,
        resource_id: str,
        details: Optional[Dict[str, str]] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        """Create an audit log entry."""
        audit_log = AuditLog(
            action=action,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
        )
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        return audit_log

    def list_by_resource(
        self, resource_type: str, resource_id: str, limit: int = 100
    ) -> List[AuditLog]:
        """List audit logs for a specific resource."""
        return (
            self.db.query(AuditLog)
            .filter(
                AuditLog.resource_type == resource_type,
                AuditLog.resource_id == resource_id,
            )
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
            .all()
        )

    def list_by_user(self, user_id: str, limit: int = 100) -> List[AuditLog]:
        """List audit logs for a specific user."""
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.user_id == user_id)
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
            .all()
        )

    def list_all(self, limit: int = 100) -> List[AuditLog]:
        """List all audit logs."""
        return self.db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
