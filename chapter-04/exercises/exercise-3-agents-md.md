# Exercise 3: Write an AGENTS.md File

**Time Required**: 30-40 minutes
**Difficulty**: Beginner-Intermediate
**Prerequisites**: Completed AGENTS.md Creation Guide tutorial

## Learning Objectives

By completing this exercise, you will:
- Write a complete AGENTS.md from scratch
- Define appropriate agent personas and workflows
- Establish security boundaries and restrictions
- Create actionable project rules

## Scenario

You are the lead developer for an **E-commerce Order Management System**. The system uses:

**Tech Stack:**
- Python 3.11 with FastAPI
- PostgreSQL database with SQLAlchemy ORM
- Redis for caching and Celery task queue
- Stripe for payment processing
- SendGrid for email notifications

**Project Structure:**
```text
order-management/
├── app/
│   ├── api/                 # FastAPI routers
│   ├── services/            # Business logic
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   └── core/                # Configuration, security
├── tests/
├── migrations/              # Alembic migrations
├── infrastructure/          # Docker, K8s configs
└── docs/
```

**Critical Constraints:**
- Payment processing code (`app/services/payment.py`) requires human review
- Authentication code (`app/core/security.py`) is frozen
- Never expose customer PII in logs
- All database changes require migrations
- Tests must cover happy path, edge cases, and error handling

## Step 1: Create the Basic Structure

Create an `AGENTS.md` file with all required sections:

```markdown
# AGENTS.md

## Persona
[Define the agent's role and approach]

## Tech Stack
[List all technologies]

## Project Rules
[Define non-negotiable constraints]

## Workflow
[Step-by-step task approach]

## Commands
[Available development commands]

## Restricted Areas
[Files/directories to avoid]

## Security & Safety
[Security guidelines]
```

## Step 2: Write the Persona

Create a persona for a senior backend engineer. The engineer:
- Specializes in e-commerce systems
- Prioritizes reliability and data integrity
- Is cautious with payment and customer data
- Values clear documentation

Write 3-5 sentences describing this persona.

<details>
<summary>Hint (Click to expand)</summary>

```markdown
## Persona

You are a senior Python backend engineer specializing in e-commerce systems.
You prioritize reliability, data integrity, and customer trust above all else.
You are especially cautious when handling payment processing and customer PII.
You believe in defensive programming - always validate inputs, handle errors
gracefully, and never assume external services will behave correctly.
```
</details>

## Step 3: Document the Tech Stack

List all technologies from the scenario. Include versions and configurations where they matter.

<details>
<summary>Hint (Click to expand)</summary>

```markdown
## Tech Stack

- **Language**: Python 3.11
- **Framework**: FastAPI
- **Database**: PostgreSQL via SQLAlchemy ORM (async)
- **Migrations**: Alembic
- **Cache/Queue**: Redis + Celery
- **Payments**: Stripe Python SDK
- **Email**: SendGrid
- **Testing**: pytest with pytest-asyncio
- **Formatting**: Black (line length: 88)
- **Linting**: Ruff
- **Type Checking**: mypy (strict mode)
```
</details>

## Step 4: Establish Project Rules

Write rules covering:

1. **Code Organization**
   - Where business logic belongs
   - How to handle external services
   - Function length limits

2. **Testing Requirements**
   - Minimum test coverage
   - Required test cases
   - Mocking requirements

3. **Documentation Standards**
   - Type hints requirements
   - Docstring format
   - When to update CHANGELOG

4. **Database Rules**
   - Migration requirements
   - Query patterns

Write at least 10 specific rules (the validation checklist below checks for 10).

<details>
<summary>Hint: Sample Rules (Click to expand)</summary>

```markdown
## Project Rules

### Code Organization
- Business logic belongs in `app/services/`, not in routers
- External API calls must use the wrapper classes in `app/integrations/`
- Keep functions under 50 lines; extract helpers for complex logic
- All API endpoints must have corresponding Pydantic schemas

### Testing
- Every new feature requires tests covering:
  - Happy path (expected behavior)
  - Edge cases (empty input, boundary values)
  - Error cases (invalid input, service failures)
- Mock all external services (Stripe, SendGrid, Redis)
- Aim for >85% branch coverage on service layer

### Documentation
- All public functions must have type hints
- Use Google-style docstrings for service methods
- Update CHANGELOG.md for any user-facing changes
- Add inline comments explaining *why*, not *what*
```
</details>

## Step 5: Define the Workflow

Write a step-by-step workflow for an agent. Cover these cases:
- Receiving a bug fix request
- Implementing a new feature
- Refactoring existing code

Include at least 7 steps. Cover investigation, implementation, testing, and documentation.

<details>
<summary>Hint (Click to expand)</summary>

```markdown
## Workflow

1. **Understand the Request**
   - Read the ticket or user request carefully
   - Identify affected components (router, service, model)
   - Check for related issues or existing implementations

2. **Investigate**
   - Examine relevant router in `app/api/`
   - Review service methods in `app/services/`
   - Check existing test patterns in `tests/`

3. **For Bug Fixes**
   - Write a failing test that reproduces the bug
   - Run the test to confirm it fails
   - Implement the fix
   - Verify all related tests pass

4. **For New Features**
   - Create Pydantic schemas first (input/output contracts)
   - Implement service method with business logic
   - Add router endpoint calling the service
   - Write thorough tests

5. **Verify**
   - Run `make check` (format, lint, typecheck, test)
   - Ensure test coverage hasn't decreased
   - Check for any security implications

6. **Document**
   - Update docstrings for new/modified functions
   - Update CHANGELOG.md if user-facing
   - Add comments for non-obvious logic

7. **Summarize**
   - Provide a commit-style summary of changes
   - Note any risks or items needing human review
```
</details>

## Step 6: List Available Commands

Document all the commands an agent might need:

<details>
<summary>Hint (Click to expand)</summary>

```markdown
## Commands

### Development
- Start dev server: `make run` or `uvicorn app.main:app --reload`
- Database shell: `make db-shell`

### Testing
- Run all tests: `pytest`
- Run with coverage: `pytest --cov=app --cov-report=term-missing`
- Run specific tests: `pytest tests/test_orders.py -k "test_create"`
- Run fast (skip slow): `pytest -m "not slow"`

### Code Quality
- Format code: `make format` or `black . && isort .`
- Lint: `make lint` or `ruff check .`
- Type check: `make typecheck` or `mypy app/`
- All checks: `make check`

### Database
- Apply migrations: `alembic upgrade head`
- Create migration: `alembic revision --autogenerate -m "description"`
- Rollback one: `alembic downgrade -1`
```
</details>

## Step 7: Define Restricted Areas

List all files and directories the agent should NOT modify. Group them by reason:

<details>
<summary>Hint (Click to expand)</summary>

```markdown
## Restricted Areas

These areas require human review or are frozen:

### Security Critical (Frozen)
- `app/core/security.py` - Authentication logic (compliance frozen)
- `app/core/permissions.py` - Authorization rules
- `infrastructure/secrets/` - Secret configurations

### Requires Human Review
- `app/services/payment.py` - Payment processing (PCI compliance)
- `app/services/refund.py` - Refund logic (financial impact)
- `migrations/` - Database schema changes

### Infrastructure
- `Dockerfile*` - Container configurations
- `docker-compose*.yml` - Orchestration
- `.github/workflows/` - CI/CD pipelines
- `infrastructure/k8s/` - Kubernetes manifests

### Configuration
- `*.env*` - Environment files (never read)
- `alembic.ini` - Migration configuration
- `pyproject.toml` - Project configuration
```
</details>

## Step 8: Add Security Guidelines

Write security rules for:
- Handling secrets
- Logging practices
- Customer data (PII)
- External service calls

<details>
<summary>Hint (Click to expand)</summary>

```markdown
## Security & Safety

### Secrets
- Never hardcode API keys, tokens, or passwords
- Use `os.getenv()` or the config module for secrets
- Reference `.env.example` for required variables

### Logging
- NEVER log customer PII (email, address, payment info)
- Use structured logging with appropriate levels
- Mask sensitive data: `card_number=****1234`

### Customer Data
- Always validate and sanitize user input
- Use Pydantic schemas for request validation
- Apply rate limiting on sensitive endpoints

### External Services
- Always handle API failures gracefully
- Implement timeouts for all external calls
- Use circuit breakers for Stripe and SendGrid
- Never retry payment operations automatically

### Code Safety
- No `eval()` or `exec()` in application code
- Use parameterized queries (ORM handles this)
- Validate all webhook signatures
```
</details>

## Expected Output

Your completed AGENTS.md should:
- Be roughly 100-180 lines (the solution below runs about 170)
- Cover all 7 sections
- Include specific, actionable rules
- Reflect the e-commerce domain

## Validation Checklist

Before submitting, verify your AGENTS.md:

- [ ] Has a clear, domain-specific Persona
- [ ] Lists complete Tech Stack with versions
- [ ] Includes at least 10 specific Project Rules
- [ ] Has a 7+ step Workflow
- [ ] Documents all relevant Commands
- [ ] Lists Restricted Areas with explanations
- [ ] Includes Security guidelines for:
  - [ ] Secrets handling
  - [ ] Logging practices
  - [ ] Customer data protection
  - [ ] External service safety

## Bonus Challenges

### Challenge 1: Add Domain-Specific Rules

Add rules specific to e-commerce:
- Order state machine transitions
- Inventory management
- Price calculation precision
- Tax handling

### Challenge 2: Create Specialized Agent Files

Create additional agent files for specific roles:
- `security-agent.md` - For security review agent
- `docs-agent.md` - For documentation generation
- `refactor-agent.md` - For code refactoring tasks

### Challenge 3: Add Escalation Protocol

Define when and how the agent escalates to humans:

```markdown
## Escalation Protocol

Escalate immediately for:
- Any changes to payment processing logic
- Database migrations affecting orders or payments
- Changes that might affect regulatory compliance

Escalate after 3 failed attempts for:
- Complex refactoring spanning multiple services
- Performance optimization decisions
- Architectural changes
```

## Solution

<details>
<summary>Complete Solution (Click to expand)</summary>

```markdown
# AGENTS.md

## Persona

You are a senior Python backend engineer specializing in e-commerce systems.
You prioritize reliability, data integrity, and customer trust above all else.
You are especially cautious when handling payment processing and customer PII.
You believe in defensive programming - always validate inputs, handle errors
gracefully, and never assume external services will behave correctly.
When in doubt, err on the side of caution and flag for human review.

## Tech Stack

- **Language**: Python 3.11
- **Framework**: FastAPI
- **Database**: PostgreSQL via SQLAlchemy ORM (async)
- **Migrations**: Alembic
- **Cache/Queue**: Redis + Celery
- **Payments**: Stripe Python SDK
- **Email**: SendGrid
- **Testing**: pytest with pytest-asyncio
- **Formatting**: Black (line length: 88)
- **Linting**: Ruff
- **Type Checking**: mypy (strict mode)

## Project Rules

### Code Organization
- Business logic belongs in `app/services/`, not in routers
- Routers (`app/api/`) handle request/response only
- External API calls must use wrapper classes in `app/integrations/`
- Keep functions under 50 lines; extract helpers for complex logic
- All API endpoints must have corresponding Pydantic schemas

### Testing
- Every new feature requires tests covering:
  - Happy path (expected behavior)
  - Edge cases (empty input, boundary values, null cases)
  - Error cases (invalid input, service failures)
- Mock all external services (Stripe, SendGrid, Redis)
- Never make real API calls in tests
- Aim for >85% branch coverage on service layer

### Documentation
- All public functions must have type hints
- Use Google-style docstrings for service methods
- Update CHANGELOG.md for any user-facing changes
- Add inline comments explaining *why*, not *what*

### Database
- All schema changes require Alembic migrations
- No raw SQL - use SQLAlchemy ORM
- Add indexes for frequently queried fields
- Use transactions for multi-step operations

### Money Handling
- Use Decimal for all price calculations
- Store amounts in cents (integers) in database
- Always specify currency explicitly
- Round at the final step only

## Workflow

1. **Understand the Request**
   - Read the ticket or user request carefully
   - Identify affected components (router, service, model)
   - Check for related issues or existing implementations

2. **Investigate**
   - Examine relevant router in `app/api/`
   - Review service methods in `app/services/`
   - Check existing test patterns in `tests/`
   - Look for similar implementations to follow

3. **For Bug Fixes**
   - Write a failing test that reproduces the bug
   - Run the test to confirm it fails
   - Implement the fix
   - Verify all related tests pass

4. **For New Features**
   - Create Pydantic schemas first (input/output contracts)
   - Implement service method with business logic
   - Add router endpoint calling the service
   - Write thorough tests

5. **Verify**
   - Run `make check` (format, lint, typecheck, test)
   - Ensure test coverage hasn't decreased
   - Check for any security implications

6. **Document**
   - Update docstrings for new/modified functions
   - Update CHANGELOG.md if user-facing
   - Add comments for non-obvious logic

7. **Summarize**
   - Provide a commit-style summary of changes
   - Note any risks or items needing human review

## Commands

### Development
- Start dev server: `make run` or `uvicorn app.main:app --reload`
- Database shell: `make db-shell`

### Testing
- Run all tests: `pytest`
- Run with coverage: `pytest --cov=app --cov-report=term-missing`
- Run specific tests: `pytest tests/test_orders.py -k "test_create"`
- Run fast (skip slow): `pytest -m "not slow"`

### Code Quality
- Format code: `make format` or `black . && isort .`
- Lint: `make lint` or `ruff check .`
- Type check: `make typecheck` or `mypy app/`
- All checks: `make check`

### Database
- Apply migrations: `alembic upgrade head`
- Create migration: `alembic revision --autogenerate -m "description"`
- Rollback one: `alembic downgrade -1`

## Restricted Areas

### Security Critical (Frozen)
- `app/core/security.py` - Authentication logic
- `app/core/permissions.py` - Authorization rules
- `infrastructure/secrets/` - Secret configurations

### Requires Human Review
- `app/services/payment.py` - Payment processing
- `app/services/refund.py` - Refund logic
- `migrations/` - Database schema changes

### Infrastructure
- `Dockerfile*` - Container configurations
- `docker-compose*.yml` - Orchestration
- `.github/workflows/` - CI/CD pipelines
- `infrastructure/k8s/` - Kubernetes manifests

### Configuration
- `*.env*` - Environment files (never read)
- `alembic.ini` - Migration configuration
- `pyproject.toml` - Project configuration

## Security & Safety

### Secrets
- Never hardcode API keys, tokens, or passwords
- Use `os.getenv()` or the config module for secrets
- Reference `.env.example` for required variables

### Logging
- NEVER log customer PII (email, address, payment info)
- Use structured logging with appropriate levels
- Mask sensitive data: `card_number=****1234`

### Customer Data
- Always validate and sanitize user input
- Use Pydantic schemas for request validation
- Apply rate limiting on sensitive endpoints

### External Services
- Always handle API failures gracefully
- Implement timeouts for all external calls (30s max)
- Use circuit breakers for Stripe and SendGrid
- Never retry payment operations automatically

### Code Safety
- No `eval()` or `exec()` in application code
- Use parameterized queries (ORM handles this)
- Validate all webhook signatures
```
</details>

## Common Mistakes to Avoid

1. **Too Generic**
   ```markdown
   ## Wrong - Generic
   You are a software developer. Write good code.

   ## Correct - Specific
   You are a senior Python backend engineer specializing in e-commerce.
   You prioritize data integrity for financial transactions.
   ```

2. **Missing Context**
   ```markdown
   ## Wrong - No context
   - Don't modify payment code

   ## Correct - With context
   - `app/services/payment.py` - Payment processing requires human review
     due to PCI compliance requirements
   ```

3. **Vague Rules**
   ```markdown
   ## Wrong
   - Write tests

   ## Correct
   - Every new feature requires tests covering:
     - Happy path
     - Edge cases (empty input, boundary values)
     - Error cases (service failures)
   ```

## Next Steps

After completing this exercise:

1. **Apply it to a real project.** This is Exercise 4.1 from Section 4.5 of the book. Use a codebase you work in.
2. **Test that the agent reads it.** Start a session. Ask the agent to restate one of your rules. If it cannot, the file is not being loaded.
3. **Read the [Governance Guide](../tutorials/governance-guide.md)** and add the AGILITY controls.
4. **Chapter 5**: Amazon Kiro steering files, which also pick up AGENTS.md.

## Reference

- [AGENTS.md Creation Guide](../tutorials/agents-md-guide.md)
- [Code Example: AGENTS.md](../code-examples/agents-md/AGENTS.md)
- [Code Example: AGENTS_enterprise.md](../code-examples/agents-md/AGENTS_enterprise.md)
