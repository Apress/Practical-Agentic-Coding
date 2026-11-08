# GitHub Copilot Instructions for LinkForge

## Project Overview

LinkForge is a URL shortening microservice built with FastAPI, PostgreSQL, and Redis. This file provides context and guidelines for GitHub Copilot to generate consistent, high-quality code.

## Technology Stack

- **Framework**: FastAPI with async/await patterns
- **Database**: PostgreSQL with SQLAlchemy 2.0 async
- **Caching**: Redis with async client
- **Validation**: Pydantic v2
- **Testing**: pytest with pytest-asyncio
- **Deployment**: Docker + GitHub Actions + Azure

## Code Standards

### Python Style
- Follow PEP 8 and PEP 484 (type hints)
- Use async/await for all I/O operations
- Prefer functional programming where appropriate
- Maximum line length: 88 characters (Black formatter)

### Naming Conventions
```python
# Classes: PascalCase
class LinkService:
    pass

# Functions/Methods: snake_case
async def create_short_url(url: str) -> str:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_TTL = 3600

# Private members: leading underscore
def _validate_internal(self) -> bool:
    pass
```

### API Design
- RESTful endpoints under `/api/v1/`
- Use HTTP status codes correctly (201 for create, 404 for not found)
- Return JSON responses with consistent schema
- Include pagination for list endpoints

### Error Handling
```python
# Use FastAPI HTTPException
from fastapi import HTTPException

async def get_link(short_code: str) -> Link:
    link = await repository.get_by_code(short_code)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return link
```

### Database Patterns
```python
# Use dependency injection for database sessions
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def get_links(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user)
) -> list[Link]:
    ...
```

### Testing Requirements
- Mock external dependencies (Redis, PostgreSQL)
- Use pytest fixtures for common setup
- Test both success and error paths
- Aim for 85%+ code coverage

## Architecture Guidelines

### Service Layer
Business logic should be in service classes, not route handlers:

```python
# Good
@router.post("/links")
async def create_link(
    request: LinkCreate,
    service: ShorteningService = Depends()
) -> LinkResponse:
    return await service.create(request)

# Avoid
@router.post("/links")
async def create_link(request: LinkCreate, db: AsyncSession = Depends()):
    # Don't put business logic here
```

### Dependency Injection
Use FastAPI's dependency injection for all services:

```python
class ShorteningService:
    def __init__(
        self,
        db: AsyncSession = Depends(get_db),
        cache: RedisCache = Depends(get_cache),
        analytics: AnalyticsService = Depends()
    ):
        self.db = db
        self.cache = cache
        self.analytics = analytics
```

## Deployment Considerations

### Docker
- Use multi-stage builds for smaller images
- Run as non-root user
- Include health check endpoints

### CI/CD
- Run tests before deployment
- Use GitHub Secrets for credentials
- Include rollback mechanisms

### Environment Variables
```text
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
REDIS_URL=redis://host:6379
SECRET_KEY=your-secret-key
DEBUG=false
```

## Common Prompts for Copilot

When working with Copilot, these prompts work well:

1. **For new endpoints**: "Create a FastAPI endpoint for [action] following the service layer pattern"
2. **For tests**: "Generate pytest tests for [function] with async support and mocked dependencies"
3. **For models**: "Create a SQLAlchemy async model for [entity] with Pydantic schema"
4. **For caching**: "Add Redis caching to [function] with configurable TTL"

## Files to Reference

When generating code, consider these key files:
- `src/models.py` - Database models
- `src/schemas.py` - Pydantic schemas
- `src/database.py` - Database configuration
- `tests/conftest.py` - Test fixtures
