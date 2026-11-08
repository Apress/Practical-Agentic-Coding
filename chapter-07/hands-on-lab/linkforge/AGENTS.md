# AGENTS.md - LinkForge Project

## Project Context

LinkForge is a URL shortening microservice with real-time analytics. This file provides high-level instructions for AI agents working on this codebase.

## Architecture Overview

```text
┌─────────────────────────────────────────────────────────┐
│                      FastAPI App                        │
├─────────────────────────────────────────────────────────┤
│  Routes (main.py)                                       │
│    └── Dependency Injection                             │
│          ├── ShorteningService                          │
│          ├── AnalyticsService                           │
│          └── DailyRateLimiter                           │
├─────────────────────────────────────────────────────────┤
│  Services Layer                                         │
│    ├── shortener.py (URL creation, validation)          │
│    ├── analytics.py (click tracking, events)            │
│    ├── cache.py (Redis caching layer)                   │
│    └── ratelimit.py (Redis-backed daily quota)          │
├─────────────────────────────────────────────────────────┤
│  Data Layer                                             │
│    ├── models.py (SQLAlchemy ORM)                       │
│    ├── schemas.py (Pydantic validation)                 │
│    └── database.py (async session management)           │
├─────────────────────────────────────────────────────────┤
│  External Services                                      │
│    ├── PostgreSQL (primary storage)                     │
│    └── Redis (caching + event streaming)                │
└─────────────────────────────────────────────────────────┘
```

There is no authentication service yet. The `user_id` parameter in `main.py` carries a `TODO`. Implementing the authentication dependency is a deliberate exercise in the Chapter 7 lab (Phase 2, Step 2). Do not invent an `AuthService`. If a task requires user identity, surface the TODO to the developer.

## Key Patterns

### 1. Async-First
All I/O operations use async/await. Never use blocking calls in request handlers.

```python
# Correct
async def get_link(code: str) -> Link | None:
    result = await db.execute(select(Link).where(Link.short_code == code))
    return result.scalar_one_or_none()

# Incorrect
def get_link(code: str) -> Link | None:
    result = db.execute(select(Link).where(Link.short_code == code))
    return result.scalar_one_or_none()
```

### 2. Service Layer
Business logic lives in service classes, not route handlers.

### 3. Dependency Injection
Use FastAPI's Depends() for all external dependencies.

### 4. Repository Pattern
Database access is abstracted through repository methods.

## Task Guidelines

### When Adding Features
1. Start with the Pydantic schema in `schemas.py`
2. Add database model in `models.py` if needed
3. Implement business logic in appropriate service
4. Add route in `main.py` with dependency injection
5. Write tests in `tests/` directory

### When Fixing Bugs
1. Write a failing test first
2. Fix the issue
3. Verify all existing tests pass

### When Refactoring
1. Ensure test coverage exists
2. Make incremental changes
3. Run tests after each change

## File Responsibilities

| File | Responsibility | Should Contain |
|------|---------------|----------------|
| `main.py` | HTTP routes | Route definitions, middleware |
| `models.py` | Database schema | SQLAlchemy models |
| `schemas.py` | Validation | Pydantic models |
| `shortener.py` | URL logic | Code generation, validation |
| `analytics.py` | Event tracking | Click logging, aggregation |
| `cache.py` | Caching layer | Redis operations |
| `ratelimit.py` | Daily quota | Per-caller counters, limiter dependency |
| `database.py` | DB config | Session factory, engine |

## Testing Strategy

- **Unit tests**: Test service methods in isolation
- **Integration tests**: Test API endpoints with mocked DB
- **End-to-end tests**: Test full flow with Docker services

## Performance Targets

- API response time: < 100ms
- Redis lookup: < 1ms
- Database query: < 50ms
- Test suite runtime: < 30s

## Security Checklist

Current state, to preserve when changing code:

- [x] All user input validated with Pydantic
- [x] Rate limiting on the shortening endpoint (`RATE_LIMIT_PER_DAY`, Redis-backed, per caller per UTC day)
- [x] No secrets in code or logs
- [x] SQL injection prevented (parameterized queries via SQLAlchemy)
- [ ] Authentication required for protected routes (the deliberate `TODO` in `main.py`; a lab exercise, see above)

## Common Tasks

### "Add a new API endpoint"
1. Define schema in `schemas.py`
2. Add route in `main.py`
3. Implement logic in appropriate service
4. Add tests in `tests/`

### "Add database field"
1. Update SQLAlchemy model in `models.py`
2. Update Pydantic schema in `schemas.py`
3. Create migration (if using Alembic)
4. Update affected services and tests

### "Improve performance"
1. Profile the slow operation
2. Consider Redis caching
3. Optimize database queries
4. Add appropriate indexes

## Environment Setup

```bash
# One-command path: starts Postgres + Redis, waits, runs the API
./run.sh

# Or step by step:
pip install -r requirements.txt

# Start Postgres + Redis only (plain 'up -d' would also start the
# containerized API on port 8000 and collide with the local server)
docker-compose up -d db redis

# Run tests (no services needed: SQLite + in-memory Redis stand-ins)
pytest --cov=src

# Start development server
uvicorn src.main:app --reload

# Teardown: docker-compose down (add -v to delete data volumes)
```
