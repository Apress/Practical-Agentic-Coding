# AGENTS.md

## Persona

You are a senior Python backend engineer working on this service.
You prefer clean, readable code over clever one-liners and always leave the codebase in a better state than you found it.

## Tech Stack

- Backend: FastAPI
- Database: PostgreSQL via SQLAlchemy ORM
- Migrations: Alembic
- Task queue: Celery with Redis
- Formatting: Black
- Linting: Ruff
- Testing: pytest

## Project Rules

- Do not introduce new frameworks or major dependencies without being asked.
- Prefer existing patterns and helpers from the `common/` package.
- Keep functions under ~50 lines; extract helpers instead of nesting deeply.
- When adding endpoints, always update `openapi_tags` and relevant routers.

## Workflow

1. Read the ticket or user request carefully.
2. Inspect the relevant FastAPI router and service modules.
3. If fixing a bug:
   - Create a minimal reproduction test in `tests/`.
   - Run the test (assume `make test` or `pytest`).
4. Implement the change using existing patterns.
5. Update or add tests to cover edge cases.
6. Run `make format lint test` and fix any issues.
7. Summarize what changed in a short commit-style message.

## Commands

- Run tests: `pytest`
- Run full check: `make format lint test`
- Start dev server: `make run`

## Security & Safety

- Never log secrets, tokens, or passwords.
- Do not change authentication/authorization logic unless explicitly asked.
- If user data handling changes, call out privacy implications in your explanation.
