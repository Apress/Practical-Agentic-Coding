# SupportFlow - AI-Assisted Customer Support

A customer support ticket management system with AI analysis and mandatory human review. This is the reference implementation for the Chapter 8 hands-on lab (Section 8.6). It becomes production ready when you complete Challenge Lab 1.

> **This build has deliberate defects.** About 20 of its 105 tests fail on purpose. The implementation falls short of the test suite in a few places. Finding and fixing them is [Challenge Lab 1](../exercises/challenge-1-debug-and-fix.md). Expect a red `pytest` run on a fresh clone. Your checkout is not broken. See [`../README.md`](../README.md) for the lab flow.

To rebuild this system yourself with Claude Code, use the full Phase 4 build prompt in [`BUILD_PROMPT.md`](BUILD_PROMPT.md). It includes request/response examples and endpoint documentation requirements.

## Features

### Core Capabilities
- **REST API**: FastAPI-based REST API with interactive Swagger UI
- **Ticket Analysis**: Automated classification, urgency assessment, and sentiment detection
- **Entity Extraction**: Automatic extraction of account IDs, order numbers, and product names
- **Priority Flagging**: Negative/angry sentiment automatically flagged for priority review
- **Escalation Engine**: Multi-criteria evaluation for human review routing with configurable rules
- **Response Generation**: Template-based response generation with mandatory human review
- **Human Review Workflow**: All AI-generated responses require approval before sending

### Technical Features
- **Database Persistence**: SQLite (dev) / PostgreSQL (prod) with SQLAlchemy ORM
- **Audit Logging**: Complete audit trail for all operations with timestamps
- **API Authentication**: API key-based authentication for all endpoints
- **Security**: Multiple validation layers prevent internal system details from reaching customers
- **Docker Deployment**: Multi-stage Docker container with docker-compose
- **Interactive Testing**: Swagger UI for API testing and exploration
- **Typing**: Python 3.11+ type hints throughout, with `mypy.ini` set to strict mode. As shipped, strict mypy reports 2 errors in `models/` and `services/` and about 90 in `api/` and `database/`. Most are SQLAlchemy `Column` attribute types. Treat `mypy` as a target, not a passing gate
- **Thorough Tests**: 105 unit and integration tests. The suite is the specification. Roughly 20 fail until you complete Challenge Lab 1

## Project Structure

```text
supportflow/
├── api/                         # FastAPI REST API
│   ├── __init__.py
│   ├── main.py                  # FastAPI application
│   ├── schemas.py               # Request/response models
│   └── dependencies.py          # Database & auth dependencies
├── database/                    # Database layer
│   ├── __init__.py
│   ├── models.py                # SQLAlchemy ORM models
│   ├── repositories.py          # Data access layer
│   └── connection.py            # Database connection manager
├── models/                      # Pydantic business models
│   ├── __init__.py
│   ├── ticket_analysis.py      # Ticket classification models
│   ├── response.py              # Response generation models
│   └── escalation.py            # Escalation rules and results
├── services/                    # Business logic
│   ├── __init__.py
│   ├── ticket_analyzer.py      # Ticket analysis service
│   ├── response_generator.py   # Response generation service
│   └── escalation_engine.py    # Escalation evaluation service
├── tests/                       # Test suite
│   ├── test_ticket_analyzer.py      # Unit tests
│   ├── test_response_generator.py
│   ├── test_escalation_engine.py
│   ├── test_bash_hook.sh            # Tests the PreToolUse hook itself
│   └── integration/             # Integration tests
│       ├── test_api_workflow.py
│       ├── test_authentication.py
│       └── test_audit_logging.py
├── .claude/                     # Claude Code configuration
│   ├── settings.json            # Permissions + PreToolUse hook
│   ├── hooks/                   # Safety hooks
│   │   ├── validate-bash-command.sh
│   │   └── README.md            # Every pattern it blocks, and why
│   └── skills/
│       └── review-drafts/SKILL.md   # The human-review workflow
├── CLAUDE.md                    # Project constitution
├── API_GUIDE.md                 # Endpoint reference
├── BUILD_PROMPT.md              # Full Phase 4 build prompt (Section 8.6)
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker container definition
├── docker-compose.yml           # Docker deployment config
├── .env.example                 # Environment variables template
├── example.py                   # Ticket analysis demo
├── example_response_generation.py  # Response generation demo
└── example_escalation.py        # Escalation engine demo
```

## Quick Start

### Using Docker (Recommended)

```bash
# Start the application
docker-compose up

# Access the API
# - API: http://localhost:8000
# - Interactive UI: http://localhost:8000/docs
# - API Documentation: http://localhost:8000/redoc

# Stop the application
docker-compose down
```

If `docker-compose` prints `command not found`, your Docker install ships Compose as a plugin. Run `docker compose` (with a space) wherever this README says `docker-compose`.

### Local Installation

```bash
# Requires Python 3.11+
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # Windows: copy .env.example .env

# Start the API server (--env-file loads your .env)
uvicorn api.main:app --reload --env-file .env

# Access at http://localhost:8000
```

Without `--env-file`, the server uses the same defaults as `.env.example`: SQLite file `supportflow.db` and API key `demo-key-12345`.

## API Usage

### Quick Example

```bash
# Submit a ticket
curl -X POST http://localhost:8000/tickets \
  -H "X-API-Key: demo-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"content": "I need help with my billing issue"}'

# List pending responses
curl -X GET http://localhost:8000/responses/pending \
  -H "X-API-Key: demo-key-12345"

# Approve a response
curl -X POST http://localhost:8000/responses/RESP-20240115-XYZ/approve \
  -H "X-API-Key: demo-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"reviewed_by": "reviewer@example.com"}'
```

**See [API_GUIDE.md](API_GUIDE.md) for complete API documentation.**

## Programmatic Usage

### Ticket Analysis

```python
from services.ticket_analyzer import TicketAnalyzer

analyzer = TicketAnalyzer()
result = analyzer.analyze(
    ticket_id="TKT-2024-001",
    content="I'm very frustrated! My account ACC-123456 was overcharged."
)

print(f"Category: {result.category}")
print(f"Urgency: {result.urgency}")
print(f"Sentiment: {result.sentiment}")
print(f"Priority Review Required: {result.requires_priority_review}")
print(f"Extracted Entities: {result.extracted_entities}")
```

### Escalation Evaluation

```python
from services.escalation_engine import EscalationEngine

engine = EscalationEngine()

# Evaluate ticket for escalation
escalation = engine.evaluate(
    ticket_id=result.ticket_id,
    ticket_content="I'm furious and calling my lawyer!",
    analysis=result,
    refund_amount_usd=150.0
)

print(f"Requires Escalation: {escalation.requires_escalation}")  # True
print(f"Priority: {escalation.escalation_priority}")  # EscalationPriority.HIGH
print(f"Reasons: {len(escalation.escalation_reasons)}")  # Multiple reasons

# Check specific escalation reasons
for reason in escalation.escalation_reasons:
    print(f"  - {reason.reason}: {reason.description}")
```

### Response Generation with Human Review

```python
from services.response_generator import ResponseGenerator
from models.response import ResponseApproval

generator = ResponseGenerator()

# Generate draft response (always requires human review)
response = generator.generate_from_analysis(
    response_id="RESP-001",
    ticket_analysis=result,
    custom_substitutions={
        "customer_name": "John Smith",
        "issue_description": "the duplicate charge",
        "resolution_details": "processed a full refund",
        "balance_info": "corrected"
    }
)

print(f"Status: {response.status}")  # ResponseStatus.DRAFT, always
print(f"Requires Review: {response.requires_human_review}")  # Always True

# Human approval required before sending
approval = ResponseApproval(
    response_id=response.response_id,
    reviewer_id="AGENT-001",
    approved=True,
    feedback="Looks good"
)

approved = generator.approve_response(response, approval)
print(f"Status: {approved.status}")  # ResponseStatus.APPROVED
# Only approved responses can be sent to customers
```

### Analysis Results

The analyzer returns a `TicketAnalysisResult` with:

**Ticket Analysis Results:**
- **Category**: billing, technical, account, or general
- **Urgency**: low, medium, high, or critical
- **Sentiment**: positive, neutral, negative, or angry
- **Extracted Entities**: Account IDs, order numbers, product names
- **Priority Flag**: Automatically set for negative/angry sentiment

**Response Generation Results:**
- **Generated Response**: Draft requiring human review
- **Template-Based**: Uses category-appropriate templates
- **Personalization**: Substitutes placeholders with ticket details
- **Status Tracking**: DRAFT → APPROVED/REJECTED workflow
- **Audit Trail**: Timestamps and reviewer IDs recorded

**Escalation Evaluation Results:**
- **Escalation Decision**: Boolean flag for human review requirement
- **Priority Level**: CRITICAL/HIGH/MEDIUM/LOW based on severity
- **Detailed Reasons**: List of specific escalation triggers
- **Negative Indicators**: Count of concerning factors
- **Immediate Attention**: Flag for critical cases requiring instant routing

## Running Tests

```bash
# Run all tests (unit + integration)
pytest tests/

# Run only unit tests
pytest tests/ --ignore=tests/integration -v

# Run only integration tests
pytest tests/integration/ -v

# Run with coverage
pytest tests/ --cov=models --cov=services --cov=api --cov=database --cov-report=html

# Run type checking (strict; reports existing errors, see Features above)
mypy models/ services/ api/ database/
```

**Test Coverage**: 105 tests cover all components and workflows. On this reference build, expect roughly 20 failures. They are the deliberate defects behind [Challenge Lab 1](../exercises/challenge-1-debug-and-fix.md). The suite passes when that challenge is complete.

## Interactive Testing with Swagger UI

Access the interactive API documentation at **http://localhost:8000/docs**

Features:
- Try all API endpoints directly in your browser
- View request/response schemas
- See example requests and responses
- No need for curl or Postman

## Configuration

### Environment Variables

Create a `.env` file (see `.env.example`). Start the server with `--env-file .env` so it is read. The code reads exactly these three variables:

```bash
# Database
DATABASE_URL=sqlite:///./supportflow.db
# For PostgreSQL: postgresql://user:password@host:5432/supportflow

# Authentication
API_KEY=demo-key-12345

# Debug
SQL_ECHO=false
```

The project's `.claude/settings.json` denies Claude edits to `.env` and `.env.*`. That includes `.env.example`. Change that template by hand.

### Production Deployment

For production:
1. **Change API Key**: Use a secure random key
2. **Use PostgreSQL**: Replace SQLite with PostgreSQL
3. **Enable HTTPS**: Configure TLS/SSL
4. **Set up Monitoring**: Use health endpoint and audit logs
5. **Configure Backups**: Regular database backups

## Constitution

This project follows strict requirements defined in `CLAUDE.md`:

- **Human Review**: All customer-facing responses require human approval
- **Audit Logging**: All ticket operations must be logged
- **Security**: No internal system details in customer responses
- **Priority Review**: Negative/angry sentiment requires priority escalation

## Development

- Python 3.11+ required
- Strict type checking enforced
- Pydantic for all data validation
- 80% minimum test coverage

## License

See `LICENSE.txt` at the repository root.
