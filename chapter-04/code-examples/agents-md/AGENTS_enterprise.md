# AGENTS.md: Autonomous Developer Instructions

## 1. Project Mission & Identity

This repository houses the **Nexus Inventory System**, a high-performance Python/Django backend. Your goal is to maintain a 99.9% system uptime through clean, service-oriented code.

## 2. Technical Ethos & Architecture

We follow the **Service Layer Pattern**. Logic must be decoupled from the transport layer.

- **Views (views.py):** Strictly for request parsing and response formatting. No business logic.
- **Services (services.py):** All business logic, third-party integrations, and complex calculations.
- **Models (models.py):** Pure schema definitions and simple property methods.

### Architecture Diagram

```text
┌─────────────────┐
│   API Layer     │  ◄── views.py (request/response only)
├─────────────────┤
│  Service Layer  │  ◄── services.py (business logic)
├─────────────────┤
│   Data Layer    │  ◄── models.py (schema definitions)
├─────────────────┤
│    Database     │
└─────────────────┘
```

## 3. Operational Rules (Logos)

These rules are non-negotiable. Violations will result in rejected pull requests.

### Style
- Use `black` for formatting (line length: 88)
- Adhere to PEP 8
- Import ordering: stdlib, third-party, local (use `isort`)

### Testing
- Use `pytest`
- No new feature is complete without a corresponding test in `/tests`
- Aim for >90% branch coverage on service-layer logic
- Mock external dependencies; never hit real APIs in tests

### Documentation
- Every new function must include a type hint and a Google-style docstring
- Update `CHANGELOG.md` for user-facing changes
- Add inline comments for non-obvious logic (explain *why*, not *what*)

### Type Safety
```python
# Required pattern for all functions
def process_order(
    order_id: str,
    quantity: int,
    options: dict[str, Any] | None = None
) -> OrderResult:
    """
    Process an order and return the result.

    Args:
        order_id: Unique identifier for the order
        quantity: Number of items to process
        options: Optional processing options

    Returns:
        OrderResult containing status and details

    Raises:
        OrderNotFoundError: If order_id doesn't exist
        ValidationError: If quantity is invalid
    """
    ...
```

## 4. Governance & Restricted Areas

To comply with our **NIST-based Risk Management** protocols:

### No-Go Zones
- Do not modify any files in `/infrastructure/security` or `/legacy/auth`
- Do not touch `/migrations/` without explicit human approval
- Never modify `conftest.py` global fixtures

### Secrets
- Never write hardcoded keys
- Use `os.getenv()` and reference `.env.example`
- All secrets must go through the vault client: `from common.vault import get_secret`

### Dependencies
- Do not add new libraries to `requirements.txt` without checking for high-severity CVEs
- Run `pip-audit` before proposing new dependencies
- Prefer standard library solutions over third-party when feasible

### Database Operations
- No raw SQL in application code (use ORM)
- All schema changes require a migration file
- No `DROP` statements in migrations without backup verification

## 5. Handover & Memory Protocol

When your task is complete or you hit a blocker:

### Status Update
- Summarize changes in a `summary.md` in the task branch
- Include: what changed, why, testing done, risks

### Memory Injection
- If you discover a project-specific quirk (e.g., a bug in a specific library version), suggest an update to this `AGENTS.md` file
- Document workarounds in `/docs/known-issues.md`

### Escalation Protocol
1. Try three different approaches before escalating
2. Document what was tried and why it failed
3. Tag `@human-review` in comments for complex architectural decisions

## 6. Communication Style

- Be concise
- Use technical, precise language
- When proposing a major refactor, provide a three-sentence rationale focusing on **Performance** and **Maintainability**

### Commit Message Format
```text
type(scope): brief description

- Detail 1
- Detail 2

Refs: TICKET-123
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`

## 7. Common Commands

```bash
# Development
make dev                    # Start development server
make shell                  # Django shell with IPython

# Testing
pytest                      # Run all tests
pytest -x                   # Stop on first failure
pytest --cov=app           # With coverage report
pytest -k "test_order"     # Run specific tests

# Code Quality
make format                 # Run black + isort
make lint                   # Run ruff
make typecheck             # Run mypy
make check                 # All quality checks

# Database
make migrate               # Apply migrations
make makemigrations        # Create new migration
```

## 8. Environment Setup

Required environment variables (see `.env.example`):
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection for Celery
- `SECRET_KEY` - Django secret key
- `SENTRY_DSN` - Error tracking (optional in dev)

## 9. Review Checklist

Before marking work as complete:
- [ ] All tests pass (`make test`)
- [ ] Code is formatted (`make format`)
- [ ] No linting errors (`make lint`)
- [ ] Type hints added for new code
- [ ] Docstrings added for public functions
- [ ] CHANGELOG.md updated (if user-facing)
- [ ] No hardcoded secrets
- [ ] Branch coverage maintained or improved
