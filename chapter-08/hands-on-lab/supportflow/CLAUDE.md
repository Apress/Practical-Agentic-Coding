# CLAUDE.md

This file is SupportFlow's constitution. Claude Code loads it automatically at the start of every session in this repository and follows the rules below without being reminded. Reference: [code.claude.com/docs](https://code.claude.com/docs).

## Project Overview

SupportFlow is a customer support ticket management system with AI-powered ticket analysis. The system enforces mandatory human review for customer-facing content and maintains complete audit trails for compliance.

## Development Commands

### Running the Application

```bash
# Using Docker Compose (Recommended)
docker-compose up

# The API will be available at:
# - http://localhost:8000 (API endpoints)
# - http://localhost:8000/docs (Interactive Swagger UI)
# - http://localhost:8000/redoc (ReDoc documentation)

# Stop the application
docker-compose down

# Rebuild after code changes
docker-compose up --build
```

```bash
# Running Locally (without Docker)
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# 3. Access the API at http://localhost:8000
```

### Testing

```bash
# Run all tests (unit + integration) with coverage
pytest tests/ --cov=models --cov=services --cov=api --cov=database --cov-report=html

# Run only unit tests
pytest tests/ --ignore=tests/integration -v

# Run only integration tests
pytest tests/integration/ -v

# Run specific test file
pytest tests/test_ticket_analyzer.py

# Run single test method
pytest tests/test_ticket_analyzer.py::TestTicketAnalyzer::test_angry_sentiment_detection

# Run with verbose output
pytest tests/ -v
```

### Type Checking

```bash
# Type check all code (strict mode enforced)
mypy models/ services/ api/ database/

# Type check specific module
mypy api/main.py
```

### Running Examples

```bash
# Demonstrate ticket analysis
python3 example.py

# Demonstrate response generation with human review workflow
python3 example_response_generation.py

# Demonstrate escalation engine with various scenarios
python3 example_escalation.py
```

### API Usage Examples

```bash
# Submit a ticket (using curl)
curl -X POST http://localhost:8000/tickets \
  -H "X-API-Key: demo-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"content": "I need help with my billing issue"}'

# Get ticket details
curl -X GET http://localhost:8000/tickets/TKT-20240115-ABC123 \
  -H "X-API-Key: demo-key-12345"

# List pending responses
curl -X GET http://localhost:8000/responses/pending \
  -H "X-API-Key: demo-key-12345"

# Approve a response
curl -X POST http://localhost:8000/responses/RESP-20240115-XYZ789/approve \
  -H "X-API-Key: demo-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"reviewed_by": "reviewer@example.com"}'

# Reject a response
curl -X POST http://localhost:8000/responses/RESP-20240115-XYZ789/reject \
  -H "X-API-Key: demo-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"reviewed_by": "reviewer@example.com", "reason": "Response needs improvement"}'

# Health check
curl http://localhost:8000/health
```

## Architecture

### Core Design Pattern: Service Layer Architecture

The codebase follows a four-layer architecture:

1. **API Layer** (`api/`): FastAPI REST endpoints and request/response handling
   - `main.py`: FastAPI application with all endpoints
   - `schemas.py`: Pydantic request/response models for API
   - `dependencies.py`: Database session and authentication dependencies
2. **Database Layer** (`database/`): Data persistence with SQLAlchemy ORM
   - `models.py`: SQLAlchemy models (Ticket, TicketAnalysis, Response, AuditLog)
   - `repositories.py`: Repository pattern for data access
   - `connection.py`: Database connection and session management
3. **Services Layer** (`services/`): Business logic and analysis algorithms
   - `ticket_analyzer.py`: Analyzes tickets for category, urgency, sentiment, and entities
   - `response_generator.py`: Generates customer responses requiring human approval
   - `escalation_engine.py`: Evaluates tickets for human escalation based on multiple criteria
4. **Models Layer** (`models/`): Pydantic models for business logic validation
   - `ticket_analysis.py`: Ticket classification and analysis models
   - `response.py`: Response generation and approval workflow models
   - `escalation.py`: Escalation rules and evaluation results
5. **Tests Layer** (`tests/`): Thorough test coverage
   - `tests/*.py`: Unit tests for services and models
   - `tests/integration/`: Integration tests for API workflows

### Key Architectural Decisions

**Pydantic-First Validation**: All data structures use Pydantic models with Field validators. The `TicketAnalysisResult` model enforces business rules at the model level (e.g., `model_post_init` ensures negative sentiment is always flagged).

**Immutable Entities**: `ExtractedEntity` uses `frozen=True` to prevent modification after creation, ensuring data integrity in concurrent processing scenarios.

**Keyword-Based Analysis**: The `TicketAnalyzer` uses keyword matching dictionaries (`_CATEGORY_KEYWORDS`, `_URGENCY_KEYWORDS`, `_SENTIMENT_KEYWORDS`) rather than ML models. This design choice prioritizes explainability, determinism, and zero external dependencies. To modify classification behavior, update these dictionaries in `services/ticket_analyzer.py`.

**Confidence Scoring**: All analysis methods return tuple pairs of `(classification, confidence_score)`. Confidence scores use consistent ranges (0.0-1.0) and are calculated based on keyword match counts relative to total matches.

### Critical Business Rules: Dual Enforcement Pattern

**1. Sentiment-Based Priority Flagging**

The `requires_priority_review` flag is automatically set to `True` when sentiment is `NEGATIVE` or `ANGRY`. This enforcement happens in two places:

- **Service layer**: `TicketAnalyzer.analyze()` sets the flag based on sentiment
- **Model layer**: `TicketAnalysisResult.model_post_init()` enforces the rule even if service layer fails

**2. Human Review Requirement for Responses**

All generated responses MUST be reviewed by humans before sending. This enforcement also uses dual patterns:

- **Service layer**: `ResponseGenerator.generate_response()` always creates responses with `status=DRAFT` and `requires_human_review=True`
- **Model layer**: `GeneratedResponse.model_post_init()` enforces that `requires_human_review=True` even if service layer is bypassed

**3. Internal Detail Prevention**

Multiple validation layers prevent internal system details from reaching customers:

- **Template validation**: `ResponseTemplate.body` field validator rejects forbidden terms
- **Response validation**: `GeneratedResponse.body` field validator rejects forbidden patterns
- **Substitution sanitization**: `ResponseGenerator._sanitize_substitutions()` uses regex to catch internal details in dynamic content

This defense-in-depth approach ensures constitutional compliance cannot be accidentally bypassed.

## API Endpoints

### Authentication

All endpoints (except `/health`) require API key authentication via the `X-API-Key` header.

**Default API Key**: `demo-key-12345`

### Available Endpoints

**Health Check**
- `GET /health` - Check service health and database connectivity
- No authentication required
- Returns: `{status, timestamp, database}`

**Ticket Management**
- `POST /tickets` - Submit a new support ticket
  - Request: `{content: string}`
  - Returns: Ticket with analysis, escalation info, and draft response
  - Creates audit log entries for ticket creation and analysis
- `GET /tickets/{ticket_id}` - Get ticket details with analysis and responses
  - Returns: Complete ticket information including all responses

**Response Review**
- `GET /responses/pending` - List all draft responses awaiting human review
  - Returns: List of responses with status=DRAFT
- `POST /responses/{response_id}/approve` - Approve a draft response
  - Request: `{reviewed_by: string}`
  - Returns: Approved response with review metadata
  - Creates audit log entry for approval
- `POST /responses/{response_id}/reject` - Reject a draft response
  - Request: `{reviewed_by: string, reason: string}`
  - Returns: Rejected response with rejection reason
  - Creates audit log entry for rejection

**Interactive Documentation**
- `GET /docs` - Swagger UI (interactive API testing interface)
- `GET /redoc` - ReDoc documentation

### Response Status Codes

- `200 OK` - Successful request
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data or operation
- `401 Unauthorized` - Missing or invalid API key (older FastAPI versions answered a missing key with `403 Forbidden`; the tests accept either)
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error

## Deployment

### Docker Deployment

**Prerequisites**: Docker and Docker Compose installed

**Quick Start**:
```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

**Configuration**:
- SQLite database stored in `./data` volume
- Default API key: `demo-key-12345`
- Environment variables can be set in `docker-compose.yml`

### Local Development

**Prerequisites**: Python 3.11+

**Setup**:
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn api.main:app --reload
```

**Environment Variables**:
- `DATABASE_URL` - Database connection string (default: `sqlite:///./supportflow.db`)
- `API_KEY` - Valid API key for authentication (default: `demo-key-12345`)
- `SQL_ECHO` - Enable SQL query logging (default: `false`)

### Production Deployment

**Database**: For production, use PostgreSQL instead of SQLite:
```bash
DATABASE_URL=postgresql://user:password@host:5432/supportflow
```

**Security**:
- Change default API key to a secure random value
- Use environment variables for sensitive configuration
- Enable HTTPS/TLS in production
- Set up proper firewall rules

**Monitoring**:
- Health check endpoint: `GET /health`
- Audit logs stored in `audit_logs` table
- Monitor database connections and response times

## Technical Requirements

### Python Environment
- **Version**: Python 3.11+ required
- **Type Hints**: All functions must have complete type annotations
- **Mypy**: Strict mode enforced (see `mypy.ini`)
- **No `Any` types**: Except when interfacing with untyped third-party libraries

### Data Validation
- **Pydantic**: All data structures must use Pydantic `BaseModel`
- **Field Constraints**: Use `Field()` with validation constraints (min_length, ge, le, etc.)
- **Custom Validators**: Use `@field_validator` for complex validation logic

### Testing Standards
- **Coverage**: Minimum 80% coverage enforced via pytest.ini
- **Test Structure**: Use pytest class-based structure (`TestClassName`)
- **Constitution Tests**: Include specific tests verifying business rule compliance

## Business Rules (Non-Negotiable)

### 1. Human Review Requirement
**CRITICAL**: AI-generated customer responses MUST be reviewed by humans before sending.
- Implement review queues for all generated content
- Track reviewer identity and timestamp

### 2. Audit Logging
**MANDATORY**: Log all ticket operations with:
- ISO 8601 timestamps with timezone
- User/agent who made changes
- Previous and new values
- 7-year retention period

### 3. Security & Privacy
**NON-NEGOTIABLE**: Never expose internal system details in customer-facing responses.
- No stack traces, internal IDs, database queries, or service names
- Only include: public ticket IDs, customer data, resolution info

### 4. Sentiment Analysis & Priority
**REQUIRED**: Negative/angry sentiment MUST trigger priority escalation.
- Run sentiment analysis on ALL incoming tickets
- Flag negative/angry sentiment for priority review
- Assign higher priority scores
- Notify supervisors for severely negative sentiment
- Log sentiment scores (but don't expose to customers)

## Code Organization

### Module Responsibilities

**models/ticket_analysis.py**: Defines all enums and Pydantic models
- `TicketCategory`, `TicketUrgency`, `TicketSentiment`, `EntityType` enums
- `ExtractedEntity`: Immutable entity with type, value, confidence, position
- `TicketAnalysisResult`: Complete analysis result with automatic priority flagging

**services/ticket_analyzer.py**: Ticket analysis business logic
- `analyze()`: Main entry point returning `TicketAnalysisResult`
- `_classify_category()`: Keyword-based category classification
- `_assess_urgency()`: Urgency level determination
- `_detect_sentiment()`: Sentiment detection with priority flagging
- `_extract_entities()`: Regex-based entity extraction

**services/response_generator.py**: Response generation with mandatory human review
- `generate_response()`: Creates DRAFT response from template with substitutions
- `generate_from_analysis()`: Auto-selects template based on ticket category
- `approve_response()`: Marks response as approved by human reviewer
- `reject_response()`: Marks response as rejected with feedback
- `_sanitize_substitutions()`: Validates substitutions don't contain internal details
- Template library: Maintains default templates for all categories

**services/escalation_engine.py**: Multi-criteria escalation evaluation
- `evaluate()`: Evaluates ticket against all escalation rules
- `_check_angry_sentiment()`: Detects angry sentiment
- `_check_low_confidence()`: Checks all confidence scores
- `_check_unknown_category()`: Detects unclear categorization
- `_check_high_refund()`: Checks financial thresholds
- `_detect_keywords()`: Finds legal, social media, competitor keywords
- `_calculate_priority()`: Determines CRITICAL/HIGH/MEDIUM/LOW priority
- Configurable rules: Financial thresholds, confidence minimums, keyword lists

**models/response.py**: Response generation models
- `ResponseTemplate`: Template with placeholders and validation
- `GeneratedResponse`: Response with status tracking and review metadata
- `ResponseApproval`: Human review action with feedback
- `ResponseStatus`: Enum for DRAFT/APPROVED/REJECTED states
- `TemplateCategory`: Maps to ticket categories

**models/escalation.py**: Escalation evaluation models
- `EscalationRule`: Configurable thresholds and keyword lists
- `EscalationResult`: Evaluation result with priority and reasons
- `EscalationDetail`: Individual reason with audit trail
- `EscalationReason`: Enum for escalation triggers
- `EscalationPriority`: Enum for CRITICAL/HIGH/MEDIUM/LOW

### Adding New Classifications

To add a new category/urgency/sentiment level:
1. Add enum value to appropriate enum in `models/ticket_analysis.py`
2. Add keyword set to corresponding dictionary in `services/ticket_analyzer.py`
3. Update classification method logic if needed
4. Add test cases in `tests/test_ticket_analyzer.py`

To add a new entity type:
1. Add enum value to `EntityType` in `models/ticket_analysis.py`
2. Add regex pattern to `_ENTITY_PATTERNS` in `services/ticket_analyzer.py`
3. Add extraction test cases

To add a new response template:
1. Create `ResponseTemplate` instance with unique `template_id`
2. Add template using `ResponseGenerator.add_template()`
3. Set appropriate category and placeholders
4. Ensure template body doesn't contain forbidden terms (validated automatically)

### Response Generation Workflow

The typical workflow for generating and approving responses:

1. **Ticket Analysis**: Use `TicketAnalyzer.analyze()` to classify ticket
2. **Response Generation**: Use `ResponseGenerator.generate_from_analysis()` or `generate_response()`
   - Response is created with `status=DRAFT`
   - `requires_human_review=True` is automatically set
3. **Human Review**: Human agent reviews draft response
4. **Approval/Rejection**:
   - If approved: `ResponseGenerator.approve_response()` updates status to APPROVED
   - If rejected: `ResponseGenerator.reject_response()` updates status to REJECTED
5. **Sending**: Only APPROVED responses can be sent to customers

### Escalation Evaluation Workflow

The escalation workflow identifies tickets requiring human review:

1. **Ticket Analysis**: Analyze ticket content and metadata
2. **Escalation Evaluation**: `EscalationEngine.evaluate()` checks multiple criteria:
   - Sentiment (angry or multiple negative indicators)
   - Financial thresholds (refunds over $100 by default)
   - Risk keywords (legal, social media, competitor mentions)
   - Confidence scores (below 80% by default)
   - Category clarity (unknown/unclear categories)
3. **Priority Assignment**: Tickets assigned CRITICAL/HIGH/MEDIUM/LOW priority
4. **Routing**: Escalated tickets routed to appropriate human review queues
5. **Audit Trail**: All escalation reasons captured with detailed explanations

### Escalation Priority Levels

- **CRITICAL**: Angry + legal threat, or 4+ negative indicators (immediate attention)
- **HIGH**: Angry sentiment, legal threat, or 3+ negative indicators
- **MEDIUM**: Social media threat, competitor mention, or 2 negative indicators
- **LOW**: Single indicator (high refund, low confidence)

## Development Safety Hooks

### PreToolUse Hook: Bash Command Validation

SupportFlow uses a PreToolUse hook to protect against accidentally running dangerous Bash commands during development.

**Configuration**: `.claude/settings.json`

**Hook Script**: `.claude/hooks/validate-bash-command.sh`

**Blocked Commands**:
- `rm -rf /` - Root filesystem deletion
- `rm -rf ~` - Home directory deletion
- `rm -rf *` - Wildcard deletion
- `sudo rm` - Privileged deletion
- `chmod 777` - World-writable permissions
- `curl | sh` - Piped shell execution
- `dd to /dev/*` - Block device writing
- `mkfs` - Filesystem formatting
- Fork bombs and system control commands

**Testing the Hook**:
```bash
./tests/test_bash_hook.sh
# Expected: 46 tests, all passing
```

**Example**:
```bash
# This command would be BLOCKED:
rm -rf /

# This command would be ALLOWED:
rm -rf ./build
```

The hook provides immediate feedback before dangerous operations execute, protecting your development environment.

## Prohibited Actions

Never:
1. Send AI-generated content to customers without human review
2. Expose internal system information in customer-facing responses
3. Skip audit logging for ticket operations
4. Bypass sentiment analysis on incoming tickets
5. Use weak or dynamic typing
6. Commit code that fails type checking
7. Skip the priority review flag for negative/angry sentiment
8. Disable development safety hooks without understanding implications
