# CLAUDE.md - Enterprise Project Template

This file establishes constitutional governance for Claude Code in enterprise environments with strict compliance, security, and audit requirements.

## Project Overview

**Project**: PaymentGateway
**Classification**: Confidential
**Compliance**: PCI DSS Level 1, SOC 2 Type II
**SLA**: 99.99% uptime

Payment processing service handling $2M+ daily transactions across multiple payment methods and currencies. Integrated with major payment processors and banking systems.

## Development Commands

### Running the Application

```bash
# Development (uses test keys)
docker-compose -f docker-compose.dev.yml up

# Local testing
npm run dev:local

# Never run production locally
```

### Testing

```bash
# Unit tests (required before every commit)
npm test

# Integration tests (required before PR)
npm run test:integration

# Security scan (required weekly)
npm run security:scan

# Full compliance check
npm run compliance:check
```

### Deployment

```bash
# Deployments are automated through CI/CD
# Manual deployment is PROHIBITED
# Emergency procedures documented in runbooks/
```

## Architecture

### System Design

```text
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway (Kong)                      │
│              Rate Limiting, Authentication, WAF             │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
├──────────────────┬──────────────────┬──────────────────────┤
│  Payment Service │ Reconciliation   │ Reporting Service    │
│  (Core Business) │ Service          │ (Read-only)          │
└──────────────────┴──────────────────┴──────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                               │
│       Primary DB (PostgreSQL) │ Audit DB (Immutable)       │
└─────────────────────────────────────────────────────────────┘
```

### Critical Design Decisions

- **All database operations MUST be async** (asyncpg)
- **Financial calculations use Decimal, NEVER float**
- **Every state change requires an audit log entry**
- **All PII must be encrypted at rest and in transit**

## Code Standards

### Language Requirements

- Python 3.11+ with strict type hints
- No `Any` types except for third-party library interfaces
- All public functions require docstrings (Google style)
- Maximum cyclomatic complexity: 10

### Data Handling

- **No raw SQL** - use SQLAlchemy ORM exclusively
- All user input MUST be validated with Pydantic
- Sensitive data MUST use `SecretStr` type
- JSON serialization MUST exclude sensitive fields

### Error Handling

```python
# REQUIRED: Use domain-specific exceptions
class PaymentError(Exception):
    """Base exception for payment operations."""
    def __init__(self, message: str, error_code: str, correlation_id: str):
        self.message = message
        self.error_code = error_code
        self.correlation_id = correlation_id
        super().__init__(message)

# PROHIBITED: Generic exceptions without context
raise Exception("Payment failed")  # NEVER DO THIS
```

## Security Requirements

### Non-Negotiable Rules

1. **No secrets in code** - use environment variables or secrets manager
2. **All user input validated and sanitized** before processing
3. **Rate limiting on all public endpoints** (100 req/min default)
4. **TLS 1.3 required** for all external communications
5. **PII must be masked in logs** (show only last 4 digits)

### Authentication

- All endpoints require authentication (except health check)
- Use OAuth 2.0 with PKCE for user flows
- Service-to-service uses mTLS
- Session timeout: 15 minutes

### Audit Logging

```python
# REQUIRED for all state-changing operations
audit_log.record(
    action="payment.process",
    actor_id=request.user_id,
    resource_type="payment",
    resource_id=payment.id,
    details={
        "amount": str(payment.amount),  # Decimal as string
        "currency": payment.currency,
        "status_before": previous_status,
        "status_after": new_status,
    },
    timestamp=datetime.utcnow(),
    correlation_id=request.correlation_id,
)
```

## Testing Standards

### Coverage Requirements

| Component | Minimum Coverage |
|-----------|-----------------|
| Financial logic | 95% |
| API endpoints | 90% |
| Utility functions | 80% |
| Overall | 90% |

### Required Test Types

- Unit tests for all business logic
- Integration tests for API flows
- Contract tests for external services
- Security tests (OWASP ZAP scan)
- Performance tests (load testing)
- Chaos tests (failure injection)

### Test Database

- Integration tests use **isolated test database**
- Mock external payment processors in unit tests
- Never use production data in tests (use synthetic data)

## Compliance

### PCI DSS Requirements

- No storage of full card numbers (tokenization only)
- Cardholder data encrypted with AES-256
- Access logging for all cardholder data access
- Annual penetration testing required

### Data Retention

- Transaction records: 7 years
- Audit logs: 7 years (immutable)
- Debug logs: 90 days
- PII: Delete upon account closure (GDPR)

## Incident Response

### Severity Levels

| Severity | Description | Response Time |
|----------|-------------|---------------|
| SEV1 | Payment processing down | 15 minutes |
| SEV2 | Partial degradation | 1 hour |
| SEV3 | Non-critical issue | 4 hours |
| SEV4 | Minor bug | Next sprint |

### On-Call Escalation

1. Primary on-call engineer
2. Team lead (after 15 min SEV1)
3. Engineering manager (after 30 min SEV1)
4. VP Engineering (after 1 hour SEV1)

## Prohibited Actions

### Code

- **NEVER** store credit card numbers (use tokens)
- **NEVER** use float for money calculations
- **NEVER** log full card numbers or CVV
- **NEVER** commit secrets to version control
- **NEVER** disable security middleware
- **NEVER** bypass rate limiting

### Operations

- **NEVER** deploy without CI/CD pipeline
- **NEVER** access production database directly
- **NEVER** share credentials
- **NEVER** disable audit logging
- **NEVER** modify production without change ticket

### Third-Party Dependencies

- **NEVER** add dependencies without security review
- **NEVER** use packages with known vulnerabilities
- **NEVER** use unmaintained packages (no updates in 12 months)

## Change Management

All changes must follow the change management process:

1. Create change ticket
2. Security review (if applicable)
3. Code review (2 approvers required)
4. QA sign-off
5. Deploy to staging
6. Automated testing
7. Deploy to production (during maintenance window)
8. Post-deployment verification

## Contact

- **Team Lead**: [email]
- **Security Team**: security@company.com
- **Compliance**: compliance@company.com
- **On-Call**: pagerduty.com/company-payments
