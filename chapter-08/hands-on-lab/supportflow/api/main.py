"""FastAPI application for SupportFlow."""

import uuid
from datetime import datetime
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from api.dependencies import get_api_key, get_database
from api.schemas import (
    AnalysisResponse,
    EntityResponse,
    EscalationResponse,
    ErrorResponse,
    HealthResponse,
    PendingResponsesResponse,
    ResponseItemResponse,
    ResponseApproveRequest,
    ResponseRejectRequest,
    TicketResponse,
    TicketSubmitRequest,
    TicketSubmitResponse,
)
from database import init_db
from database.repositories import (
    AuditLogRepository,
    ResponseRepository,
    TicketAnalysisRepository,
    TicketRepository,
)
from services import EscalationEngine, ResponseGenerator, TicketAnalyzer

# Initialize FastAPI app
app = FastAPI(
    title="SupportFlow API",
    description="AI-powered customer support ticket management system with mandatory human review",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Initialize services
ticket_analyzer = TicketAnalyzer()
response_generator = ResponseGenerator()
escalation_engine = EscalationEngine()


@app.on_event("startup")
def startup_event() -> None:
    """Initialize database on startup."""
    init_db()


# ===== Helper Functions =====


def log_audit(
    db: Session,
    action: str,
    user_id: str,
    resource_type: str,
    resource_id: str,
    details: Optional[dict] = None,
) -> None:
    """Create an audit log entry."""
    audit_repo = AuditLogRepository(db)
    audit_repo.create(
        action=action,
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
    )


# ===== API Endpoints =====


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check endpoint",
)
def health_check(db: Session = Depends(get_database)) -> HealthResponse:
    """
    Check service health and database connectivity.

    Returns service status and database connection status.
    """
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return HealthResponse(
        status="healthy" if db_status == "connected" else "unhealthy",
        timestamp=datetime.utcnow(),
        database=db_status,
    )


@app.post(
    "/tickets",
    response_model=TicketSubmitResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Tickets"],
    summary="Submit a new support ticket",
    responses={
        201: {"description": "Ticket created with analysis and draft response"},
        401: {"model": ErrorResponse, "description": "Invalid API key"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
)
def submit_ticket(
    request: TicketSubmitRequest,
    db: Session = Depends(get_database),
    api_key: str = Depends(get_api_key),
) -> TicketSubmitResponse:
    """
    Submit a new customer support ticket.

    This endpoint:
    1. Creates a new ticket
    2. Analyzes ticket content (category, sentiment, urgency, entities)
    3. Evaluates for escalation
    4. Generates a draft response requiring human review
    5. Logs all operations to audit trail

    All responses are created as DRAFT and require human approval before sending.
    """
    # Generate unique ticket ID
    ticket_id = f"TKT-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

    # Create ticket
    ticket_repo = TicketRepository(db)
    ticket = ticket_repo.create(ticket_id=ticket_id, content=request.content)

    # Log ticket creation
    log_audit(
        db=db,
        action="ticket.created",
        user_id=api_key,
        resource_type="ticket",
        resource_id=ticket_id,
        details={"content_length": len(request.content)},
    )

    # Analyze ticket
    analysis_result = ticket_analyzer.analyze(ticket_id=ticket_id, content=request.content)

    # Store analysis
    analysis_repo = TicketAnalysisRepository(db)
    entities_json = [
        {
            "entity_type": entity.entity_type.value,
            "value": entity.value,
            "confidence": entity.confidence,
        }
        for entity in analysis_result.extracted_entities
    ]

    # Evaluate escalation
    escalation_result = escalation_engine.evaluate(
        ticket_id=ticket_id,
        ticket_content=request.content,
        analysis=analysis_result,
        refund_amount_usd=None,  # Would be extracted from content in real system
    )

    escalation_json = {
        "should_escalate": escalation_result.requires_escalation,
        "priority": escalation_result.escalation_priority.value,
        "reasons": [detail.reason.value for detail in escalation_result.escalation_reasons],
    }

    ticket_analysis = analysis_repo.create(
        ticket_id=ticket.id,
        category=analysis_result.category.value,
        category_confidence=analysis_result.category_confidence,
        urgency=analysis_result.urgency.value,
        urgency_confidence=analysis_result.urgency_confidence,
        sentiment=analysis_result.sentiment.value,
        sentiment_confidence=analysis_result.sentiment_confidence,
        requires_priority_review=analysis_result.requires_priority_review,
        extracted_entities=entities_json,
        escalation_data=escalation_json,
    )

    # Log analysis
    log_audit(
        db=db,
        action="ticket.analyzed",
        user_id="system",
        resource_type="ticket",
        resource_id=ticket_id,
        details={
            "category": analysis_result.category.value,
            "sentiment": analysis_result.sentiment.value,
            "urgency": analysis_result.urgency.value,
        },
    )

    # Generate draft response
    response_id = f"RESP-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

    # Provide default substitutions (in production, these would be extracted from ticket/customer data)
    default_substitutions = {
        "customer_name": "Valued Customer",
        "issue_description": "your inquiry",
        "resolution_details": "our team will investigate",
        "balance_info": "current",
    }

    generated_response = response_generator.generate_from_analysis(
        response_id=response_id,
        ticket_analysis=analysis_result,
        custom_substitutions=default_substitutions,
    )

    # Store response
    response_repo = ResponseRepository(db)
    response = response_repo.create(
        response_id=response_id,
        ticket_id=ticket.id,
        template_id=generated_response.template_id,
        body=generated_response.body,
        status=generated_response.status.value,
        requires_human_review=generated_response.requires_human_review,
    )

    # Log response generation
    log_audit(
        db=db,
        action="response.generated",
        user_id="system",
        resource_type="response",
        resource_id=response_id,
        details={
            "ticket_id": ticket_id,
            "template_id": generated_response.template_id,
            "status": "DRAFT",
        },
    )

    # Build response
    return TicketSubmitResponse(
        ticket=TicketResponse(
            ticket_id=ticket.ticket_id,
            content=ticket.content,
            created_at=ticket.created_at,
            analysis=AnalysisResponse(
                category=analysis_result.category.value,
                category_confidence=analysis_result.category_confidence,
                urgency=analysis_result.urgency.value,
                urgency_confidence=analysis_result.urgency_confidence,
                sentiment=analysis_result.sentiment.value,
                sentiment_confidence=analysis_result.sentiment_confidence,
                requires_priority_review=analysis_result.requires_priority_review,
                extracted_entities=[
                    EntityResponse(
                        entity_type=entity.entity_type.value,
                        value=entity.value,
                        confidence=entity.confidence,
                    )
                    for entity in analysis_result.extracted_entities
                ],
            ),
            escalation=EscalationResponse(
                should_escalate=escalation_result.requires_escalation,
                priority=escalation_result.escalation_priority.value,
                reasons=[detail.reason.value for detail in escalation_result.escalation_reasons],
                details={},
            ),
        ),
        draft_response=ResponseItemResponse(
            response_id=response.response_id,
            ticket_id=ticket.ticket_id,
            body=response.body,
            status=response.status,
            requires_human_review=bool(response.requires_human_review),
            template_id=response.template_id,
            reviewed_by=response.reviewed_by,
            reviewed_at=response.reviewed_at,
            rejection_reason=response.rejection_reason,
            created_at=response.created_at,
        ),
    )


@app.get(
    "/tickets/{ticket_id}",
    response_model=TicketResponse,
    tags=["Tickets"],
    summary="Get ticket details",
    responses={
        200: {"description": "Ticket details with analysis and responses"},
        401: {"model": ErrorResponse, "description": "Invalid API key"},
        404: {"model": ErrorResponse, "description": "Ticket not found"},
    },
)
def get_ticket(
    ticket_id: str,
    db: Session = Depends(get_database),
    api_key: str = Depends(get_api_key),
) -> TicketResponse:
    """
    Get ticket details including analysis and all responses.

    Returns complete ticket information with analysis results and any generated responses.
    """
    ticket_repo = TicketRepository(db)
    ticket = ticket_repo.get_by_ticket_id(ticket_id)

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {ticket_id} not found",
        )

    # Get analysis
    analysis_repo = TicketAnalysisRepository(db)
    analysis = analysis_repo.get_by_ticket_id(ticket.id)

    analysis_response = None
    escalation_response = None
    if analysis:
        analysis_response = AnalysisResponse(
            category=analysis.category,
            category_confidence=analysis.category_confidence,
            urgency=analysis.urgency,
            urgency_confidence=analysis.urgency_confidence,
            sentiment=analysis.sentiment,
            sentiment_confidence=analysis.sentiment_confidence,
            requires_priority_review=bool(analysis.requires_priority_review),
            extracted_entities=[
                EntityResponse(**entity) for entity in analysis.extracted_entities
            ],
        )

        if analysis.escalation_data:
            escalation_response = EscalationResponse(**analysis.escalation_data)

    # Get responses
    responses = [
        ResponseItemResponse(
            response_id=resp.response_id,
            ticket_id=ticket.ticket_id,
            body=resp.body,
            status=resp.status,
            requires_human_review=bool(resp.requires_human_review),
            template_id=resp.template_id,
            reviewed_by=resp.reviewed_by,
            reviewed_at=resp.reviewed_at,
            rejection_reason=resp.rejection_reason,
            created_at=resp.created_at,
        )
        for resp in ticket.responses
    ]

    return TicketResponse(
        ticket_id=ticket.ticket_id,
        content=ticket.content,
        created_at=ticket.created_at,
        analysis=analysis_response,
        escalation=escalation_response,
        responses=responses,
    )


@app.get(
    "/responses/pending",
    response_model=PendingResponsesResponse,
    tags=["Responses"],
    summary="List pending responses for review",
    responses={
        200: {"description": "List of responses awaiting human review"},
        401: {"model": ErrorResponse, "description": "Invalid API key"},
    },
)
def list_pending_responses(
    db: Session = Depends(get_database),
    api_key: str = Depends(get_api_key),
) -> PendingResponsesResponse:
    """
    List all responses with DRAFT status awaiting human review.

    Returns responses that need human approval before sending to customers.
    """
    response_repo = ResponseRepository(db)
    pending = response_repo.list_pending(limit=100)

    # Get ticket IDs for each response
    ticket_repo = TicketRepository(db)
    responses = []
    for resp in pending:
        ticket = ticket_repo.get_by_id(resp.ticket_id)
        if ticket:
            responses.append(
                ResponseItemResponse(
                    response_id=resp.response_id,
                    ticket_id=ticket.ticket_id,
                    body=resp.body,
                    status=resp.status,
                    requires_human_review=bool(resp.requires_human_review),
                    template_id=resp.template_id,
                    reviewed_by=resp.reviewed_by,
                    reviewed_at=resp.reviewed_at,
                    rejection_reason=resp.rejection_reason,
                    created_at=resp.created_at,
                )
            )

    return PendingResponsesResponse(responses=responses, total=len(responses))


@app.post(
    "/responses/{response_id}/approve",
    response_model=ResponseItemResponse,
    tags=["Responses"],
    summary="Approve a draft response",
    responses={
        200: {"description": "Response approved successfully"},
        401: {"model": ErrorResponse, "description": "Invalid API key"},
        404: {"model": ErrorResponse, "description": "Response not found"},
        400: {"model": ErrorResponse, "description": "Response already reviewed"},
    },
)
def approve_response(
    response_id: str,
    request: ResponseApproveRequest,
    db: Session = Depends(get_database),
    api_key: str = Depends(get_api_key),
) -> ResponseItemResponse:
    """
    Approve a draft response for sending to customer.

    Human reviewers use this endpoint to approve AI-generated responses.
    Only DRAFT responses can be approved.
    """
    response_repo = ResponseRepository(db)
    response = response_repo.get_by_response_id(response_id)

    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Response {response_id} not found",
        )

    if response.status != "DRAFT":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Response already reviewed with status: {response.status}",
        )

    # Approve response
    approved = response_repo.approve(response_id=response_id, reviewed_by=request.reviewed_by)

    # Get ticket for audit log
    ticket_repo = TicketRepository(db)
    ticket = ticket_repo.get_by_id(response.ticket_id)

    # Log approval
    log_audit(
        db=db,
        action="response.approved",
        user_id=request.reviewed_by,
        resource_type="response",
        resource_id=response_id,
        details={"ticket_id": ticket.ticket_id if ticket else None},
    )

    return ResponseItemResponse(
        response_id=approved.response_id,
        ticket_id=ticket.ticket_id if ticket else "",
        body=approved.body,
        status=approved.status,
        requires_human_review=bool(approved.requires_human_review),
        template_id=approved.template_id,
        reviewed_by=approved.reviewed_by,
        reviewed_at=approved.reviewed_at,
        rejection_reason=approved.rejection_reason,
        created_at=approved.created_at,
    )


@app.post(
    "/responses/{response_id}/reject",
    response_model=ResponseItemResponse,
    tags=["Responses"],
    summary="Reject a draft response",
    responses={
        200: {"description": "Response rejected successfully"},
        401: {"model": ErrorResponse, "description": "Invalid API key"},
        404: {"model": ErrorResponse, "description": "Response not found"},
        400: {"model": ErrorResponse, "description": "Response already reviewed"},
    },
)
def reject_response(
    response_id: str,
    request: ResponseRejectRequest,
    db: Session = Depends(get_database),
    api_key: str = Depends(get_api_key),
) -> ResponseItemResponse:
    """
    Reject a draft response with feedback.

    Human reviewers use this endpoint to reject AI-generated responses
    that don't meet quality standards. Rejection reason is required for feedback.
    """
    response_repo = ResponseRepository(db)
    response = response_repo.get_by_response_id(response_id)

    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Response {response_id} not found",
        )

    if response.status != "DRAFT":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Response already reviewed with status: {response.status}",
        )

    # Reject response
    rejected = response_repo.reject(
        response_id=response_id, reviewed_by=request.reviewed_by, reason=request.reason
    )

    # Get ticket for audit log
    ticket_repo = TicketRepository(db)
    ticket = ticket_repo.get_by_id(response.ticket_id)

    # Log rejection
    log_audit(
        db=db,
        action="response.rejected",
        user_id=request.reviewed_by,
        resource_type="response",
        resource_id=response_id,
        details={
            "ticket_id": ticket.ticket_id if ticket else None,
            "reason": request.reason,
        },
    )

    return ResponseItemResponse(
        response_id=rejected.response_id,
        ticket_id=ticket.ticket_id if ticket else "",
        body=rejected.body,
        status=rejected.status,
        requires_human_review=bool(rejected.requires_human_review),
        template_id=rejected.template_id,
        reviewed_by=rejected.reviewed_by,
        reviewed_at=rejected.reviewed_at,
        rejection_reason=rejected.rejection_reason,
        created_at=rejected.created_at,
    )
