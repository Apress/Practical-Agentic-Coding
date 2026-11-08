# Exercise 3: AI Governance - Cursor Rules vs copilot-instructions.md

## Objective

Write governance files that enforce architectural standards in AI coding assistants. Write rules for both Cursor and GitHub Copilot.

## Prerequisites

- Cursor IDE installed
- VS Code with GitHub Copilot
- LinkForge project (or any project)

## Part 1: Understanding Governance (10 minutes)

### The Problem: Catastrophic Amnesia

AI assistants forget context between sessions. Without governance:
- Each interaction starts fresh
- Team standards are inconsistent
- Architectural decisions must be re-explained

### The Solution: Governance as Code

| File | Tool | Location | Scope |
|------|------|----------|-------|
| `.cursor/rules/*.mdc` | Cursor (Project Rules) | `.cursor/rules/` | File-specific via globs |
| `AGENTS.md` | Both (auto-detected) | Project root | General agent guidance |
| `copilot-instructions.md` | Copilot | `.github/` | Repository-wide |
| `<name>.instructions.md` | Copilot (path-specific instructions) | `.github/instructions/` | Files matching its `applyTo` globs |
| `<name>.agent.md` | Copilot (custom agent profiles) | `.github/agents/` | Reusable agent roles |

## Part 2: Creating Cursor Rules (20 minutes)

### Task 2.1: Basic Rules File

Start with the simplest option, an `AGENTS.md` file in your project root. Cursor and Copilot both auto-detect it. It needs no frontmatter. Write plain markdown:

```markdown
You are an expert Python backend engineer.

## Code Standards
- Use async/await for all I/O operations
- Type hints on all public functions
- Pydantic v2 for validation

## Architecture
- Service layer pattern (business logic not in routes)
- Dependency injection via FastAPI Depends()

## Naming
- Routes: `/api/v1/{resource}`
- Services: `*Service` (e.g., LinkService)
- Models: `*Model` (SQLAlchemy), `*Schema` (Pydantic)
```

### Task 2.2: Test Your Rules

1. Open Cursor's agent chat
2. Prompt: "Create a new endpoint to list all users"
3. **Verify** the generated code follows:
   - Async patterns
   - Type hints
   - Service layer pattern
   - Correct naming conventions

### Task 2.3: Scoped Project Rules with Frontmatter

Create `.cursor/rules/api-routes.mdc`:

````markdown
---
description: "Applies when creating new API routes"
globs: "src/main.py,src/routes/*.py"
alwaysApply: false
---

# API Route Standards

## Response Format
All endpoints must return:
- 200/201 for success
- Pydantic model responses
- Include `X-Request-ID` header

## Error Handling
```python
from fastapi import HTTPException

# Always use HTTPException with specific status codes
raise HTTPException(
    status_code=404,
    detail="Resource not found",
    headers={"X-Error-Code": "RESOURCE_NOT_FOUND"}
)
```

## Pagination
List endpoints must support:
- `limit` (default: 20, max: 100)
- `offset` (default: 0)
- Return total count in headers
````

### Task 2.4: Glob Pattern Rules

Create `.cursor/rules/testing.mdc`. Keep `alwaysApply: false`. With `alwaysApply: true`, Cursor ignores the globs and loads the rule into every request.

```markdown
---
description: "Test file conventions"
globs: "tests/**/*.py"
alwaysApply: false
---

# Testing Standards

- Use pytest and pytest-asyncio
- Mock external dependencies (DB, Redis)
- Test both success and error paths
- Use descriptive test names: `test_{what}_{scenario}_{expected}`
- Fixtures in conftest.py
- Minimum 80% coverage
```

## Part 3: Creating copilot-instructions.md (20 minutes)

### Task 3.1: Generate Instructions with /init

1. Open the project in VS Code.
2. Open Copilot chat and type `/init`. Copilot analyzes the codebase and generates or updates the workspace instructions.
3. Check which file it wrote. (The Copilot CLI's `/init` always writes `.github/copilot-instructions.md`.)
4. Review and refine the file.

To write it by hand instead, create `.github/copilot-instructions.md`:

````markdown
# GitHub Copilot Instructions

## Project Context
This is LinkForge, a URL shortener microservice built with FastAPI.

## Technology Stack
- Framework: FastAPI with async/await
- Database: PostgreSQL with SQLAlchemy 2.0 async
- Caching: Redis
- Validation: Pydantic v2

## Code Conventions

### Python Style
- Follow PEP 8 and PEP 484
- Use async/await for all I/O
- Maximum line length: 88 (Black formatter)

### API Design
- RESTful endpoints under `/api/v1/`
- Use proper HTTP status codes
- Return JSON with consistent schema

### Database
- Use SQLAlchemy ORM, not raw SQL
- Always use async sessions
- Include proper indexes

## Common Patterns

### Service Layer
```python
# Business logic in services, not routes
class LinkService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def create_link(self, url: str) -> Link:
        # Implementation
```

### Error Handling
```python
from fastapi import HTTPException

async def get_link(code: str) -> Link:
    link = await self.repo.get_by_code(code)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return link
```

## Files to Reference
When generating code, consider:
- `src/models.py` - Database models
- `src/schemas.py` - Pydantic schemas
- `tests/conftest.py` - Test fixtures
````

### Task 3.2: Test Your Instructions

1. Open VS Code with Copilot
2. Ask Copilot Chat: "Create a new endpoint to get link statistics"
3. **Verify** the generated code follows your instructions

### Task 3.3: Add Domain-Specific Knowledge

Extend `copilot-instructions.md`:

```markdown
## Domain Knowledge

### URL Shortening
- Short codes are Base62 encoded (a-z, A-Z, 0-9)
- Codes should be 6-8 characters
- Handle collision detection
- Support custom codes with validation

### Analytics
- Track clicks asynchronously
- Hash IP addresses for privacy
- Detect device type from User-Agent
- Store referrer source (domain only)

### Security
- Never expose internal IDs
- Rate limit public endpoints
- Validate all URLs (no javascript:, data:, file:)
- Use parameterized queries
```

### Task 3.4: Scope Instructions to a Path

In Copilot, a path-specific instructions file does the job of a glob-scoped Cursor rule. Create `.github/instructions/tests.instructions.md`:

```markdown
---
applyTo: "tests/**/*.py"
---

- Use pytest and pytest-asyncio
- Mock Redis and the database; no live connections
- Name tests test_{what}_{scenario}_{expected}
```

GitHub documents path-specific files for Copilot Chat in VS Code, the Copilot cloud agent, and Copilot code review. To list several patterns in `applyTo`, separate them with commas.

## Part 4: Comparing Governance Approaches (15 minutes)

### Task 4.1: Create Equivalent Rules

Write the same rule in both formats:

**Requirement**: "All database queries must use async patterns and include error handling"

**Cursor Rule** (`.cursor/rules/database.mdc`):
````markdown
---
description: "Database query patterns"
globs: "src/**/*.py"
---

# Database Standards

All queries must:
1. Use `async` session
2. Handle `NoResultFound` exceptions
3. Use `select()` syntax, not `query()`

Example:
```python
async def get_by_id(self, id: int) -> Optional[Model]:
    try:
        result = await self.db.execute(
            select(Model).where(Model.id == id)
        )
        return result.scalar_one_or_none()
    except NoResultFound:
        return None
```
````

**Copilot Instructions** (add to `.github/copilot-instructions.md`):
````markdown
## Database Patterns

Always use async database patterns:
```python
# Correct
async def get_by_id(self, id: int) -> Optional[Model]:
    result = await self.db.execute(
        select(Model).where(Model.id == id)
    )
    return result.scalar_one_or_none()

# Incorrect - blocking call
def get_by_id(self, id: int) -> Model:
    return self.db.query(Model).filter_by(id=id).first()
```
````

### Task 4.2: Compare Effectiveness

Test both rules:

1. **With Cursor**: Ask the agent chat to create a new database repository method
2. **With Copilot**: Ask Chat to create the same method
3. Compare adherence to your rules

## Part 5: Advanced Governance (15 minutes)

### Task 5.1: Enforced Team Rules (Cursor)

If you are on a Cursor Teams or Enterprise plan:

1. Go to the Cursor Dashboard
2. Create a Team Rule. Team rules are free-form text with no frontmatter. Enforcement is a checkbox in the dashboard. Tick **Enforce this rule** so team members cannot switch it off. Paste:

```markdown
# Security Requirements

NEVER:
- Commit API keys or secrets
- Use string concatenation in SQL
- Disable SSL verification
- Log sensitive user data

ALWAYS:
- Use environment variables for secrets
- Use parameterized queries
- Enable HTTPS
- Mask PII in logs
```

### Task 5.2: BUGBOT.md for PR Automation

Bugbot reviews pull requests against natural-language rules in `.cursor/BUGBOT.md`. A subproject can add its own, for example `backend/.cursor/BUGBOT.md`. To run Bugbot:

- Comment `bugbot run` on a pull request.
- Or run the `/review-bugbot` skill from the agent before you push.

Project rules in `.cursor/rules/` do not apply to Bugbot runs. Create `.cursor/BUGBOT.md`:

```markdown
# Bug Bot Rules

## Database Migrations
- New indices MUST use CONCURRENTLY
- Never DROP columns, rename to *_DEPRECATED
- Prefer TEXT over VARCHAR

## Performance
- No N+1 queries in loops
- Always use pagination
- Cache expensive computations

## Security
- No credentials in code
- No `eval()` or `exec()`
- Validate all user input
```

### Task 5.3: AGENTS.md for Universal Guidance

Create/update `AGENTS.md`:

````markdown
# AGENTS.md

## Project: LinkForge

### Quick Context
URL shortener with analytics. FastAPI + PostgreSQL + Redis.

### Architecture

```text
Routes (main.py) -> Services (shortener.py) -> Repository -> Database
                 -> Cache (cache.py) -> Redis
                 -> Analytics (analytics.py) -> Events
```

### Key Files
| File | Purpose |
|------|---------|
| src/main.py | API routes |
| src/models.py | Database models |
| src/shortener.py | Business logic |

### Common Tasks
- "Add endpoint" -> Update main.py, create schema, add tests
- "Add model field" -> Update models.py, schemas.py, migration

### Testing
Run: `pytest --cov=src`
Target: 80% coverage
````

## Deliverables

Create a governance package for your project:

1. **`AGENTS.md`**: Universal agent instructions (read by both tools)
2. **`.cursor/rules/`**: 3 file-specific Project Rules
3. **`.github/copilot-instructions.md`**: Complete Copilot context (try `/init`)
4. **`.cursor/BUGBOT.md`**: PR review rules
5. **Comparison doc**: Pros/cons of each approach

## Bonus Challenge

Create a "Governance Audit" workflow:

1. Write a script that checks if generated code follows your rules
2. Add it to CI/CD pipeline
3. Track compliance metrics over time

## Summary

| Aspect | Cursor rules | copilot-instructions.md |
|--------|--------------|------------------------|
| Location | `.cursor/rules/` + `AGENTS.md` | `.github/` (+ `.github/instructions/` for path-specific files) |
| Format | Markdown with YAML frontmatter | Plain Markdown; path-specific files add `applyTo` frontmatter |
| Targeting | Glob patterns | Repository-wide, or `applyTo` globs |
| Enforcement | Team rules (Teams and Enterprise) | Advisory |
| Best For | File-specific patterns | General context |

## Key Takeaways

1. **Use governance files.** Without them, AI outputs are inconsistent.
2. **Start simple.** Begin with basic rules. Add specifics as needed.
3. **Include examples.** AI follows code samples better than descriptions.
4. **Use version control.** Treat governance files like code.
5. **Review regularly.** Update rules as patterns change.
