# Hands-On Lab: Building LinkForge

**Reference**: Chapter 7, Section 7.6 (the lab) and Section 7.7 (the challenge at the end of this file)

**Time**: plan 2 to 4 hours for the four phases. The challenge adds another 1 to 2.

**Done when**:

- Your build serves the Swagger UI at `/docs`.
- `pytest --cov=src` passes at the 85% coverage the Phase 3 prompt asks for. (The CI workflow enforces an 80% floor.)
- The Copilot cloud agent's deployment PR from Phase 4 is reviewed and merged.

The challenge has its own success criteria at the end of this file.

## Overview

This lab builds **LinkForge**, a URL shortener with real-time click analytics. It uses the four-phase Hybrid Workflow. Cursor handles development and GitHub Copilot handles deployment. Chapter 7, Sections 7.5 through 7.7 teach the workflow. This file is the runnable version.

You write the prompts and the agents write the code. Your output will not match this repository line for line. That is expected. The `linkforge/` directory next to this file is the finished reference implementation. Use it to:

- compare your build
- see what "done" looks like
- recover if a phase goes wrong

To see the target, you can run the reference implementation before you start. The one-command path is `cd linkforge && ./run.sh`. Run it inside an activated virtual environment with the requirements installed. It starts Postgres and Redis, waits for both, and runs the API. `run.sh` needs a POSIX shell (macOS, Linux, WSL, or Git Bash on Windows). The same steps one at a time:

```bash
cd linkforge
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # Windows: copy .env.example .env
docker-compose up -d db redis  # just the databases
uvicorn src.main:app --reload --env-file .env  # then open http://localhost:8000/docs
pytest --cov=src               # the test suite the lab has you generate
```

`--env-file .env` makes the app read your `.env`. Without it, the code falls back to the same defaults that `.env.example` holds.

> Note: plain `docker-compose up -d` also builds and starts the containerized API on port 8000. That collides with the `uvicorn --reload` instance. Start only `db` and `redis` when you want to run the API locally.

## User Story

> As a content creator, I need short links for long video URLs, live click counts, and a geographic breakdown of my audience. I will pay $9/month for 10,000 links plus advanced analytics.

## Technical Requirements

| Requirement | Implementation |
|-------------|----------------|
| **Latency** | FastAPI async endpoints for sub-100ms response |
| **Caching** | Redis for <1ms URL lookups |
| **Analytics** | Each click pushes an event onto a Redis list (`analytics:events`) and stores a row that the analytics endpoint aggregates |
| **Rate Limiting** | Free tier capped at 100 new links per user per day |
| **Storage** | PostgreSQL for durable link storage |
| **Scalability** | Horizontal scaling via Docker workers |

## The Four-Phase Hybrid Workflow

| Phase | Tool | Objective |
|-------|------|-----------|
| **1. Drafting** | Cursor agent chat (Composer model) | Scaffold the FastAPI service |
| **2. Refactoring** | Cursor Tab & background validation | Add Redis caching and analytics |
| **3. Testing** | Cursor agent chat | Generate and run the test suite |
| **4. Deployment** | Copilot cloud agent | CI/CD and Azure deployment |

> **Naming note (as of November 7, 2026).**
>
> - Prompts labeled "Prompt to Composer" go into Cursor's agent chat. It runs them on the Composer model. "Composer" is the model's name. The surface is the Agents Window.
> - The book calls Phase 4's agent the "Copilot Async Agent". GitHub calls it the Copilot cloud agent.
> - Shortcuts and panel layouts change between releases. See [cursor.com/docs](https://cursor.com/docs).

The prompts below are the ones printed in Section 7.6. Where this file adds a step or a note that the book does not have, it says so.

## Project Structure

```text
linkforge/
├── .cursor/
│   └── rules/
│       └── linkforge.mdc         # Cursor project rule (created in Phase 1, Step 2)
├── .github/
│   ├── copilot-instructions.md   # Copilot governance
│   └── workflows/
│       └── deploy-azure.yml      # CI/CD pipeline
├── AGENTS.md                     # Agent instructions
├── README.md                     # Project documentation
├── src/
│   ├── main.py                   # FastAPI entry point
│   ├── models.py                 # SQLAlchemy ORM models
│   ├── schemas.py                # Pydantic v2 schemas
│   ├── database.py               # Async database setup
│   ├── shortener.py              # Core shortening logic
│   ├── cache.py                  # Redis caching layer
│   ├── analytics.py              # Analytics service
│   └── ratelimit.py              # Redis-backed daily quota
├── tests/
│   ├── conftest.py               # Pytest fixtures
│   ├── test_shortening.py        # URL creation tests
│   ├── test_analytics.py         # Click tracking tests
│   ├── test_cache.py             # Redis cache layer tests
│   ├── test_security.py          # Input validation and endpoint security tests
│   └── test_ratelimit.py         # Daily quota tests
├── requirements.txt              # Python dependencies (upper-bounded)
├── run.sh                        # One-command local launcher
├── Dockerfile                    # Multi-stage build
├── docker-compose.yml            # Local development
└── .env.example                  # Environment template
```

## Prerequisites

Before you start, check that you have:

- [ ] Cursor IDE installed ([download](https://cursor.com))
- [ ] GitHub Copilot enabled in VS Code
- [ ] Python 3.11+ installed
- [ ] Docker and Docker Compose installed
- [ ] PostgreSQL and Redis (or use Docker)
- [ ] GitHub account with repository access
- [ ] An Azure subscription for Phase 4. The deployment creates Azure Container Registry and Azure Container Instances resources. They bill until you remove them. See Teardown.

## Phase 1: Architect (Cursor Agent Chat)

**Goal**: Stand up the core FastAPI microservice from nothing.

### Step 1: Create Project Structure

```bash
mkdir LinkForge
cursor LinkForge
```

If the `cursor` command is not on your PATH, start Cursor and open the folder with **File > Open Folder**.

### Step 2: Add a Project Rule

1. Open the agent chat (Cmd+I / Ctrl+I) in Agent mode. Shift+Tab switches modes. As of November 7, 2026, Ask mode is read-only and cannot create the file.
2. Prompt Cursor to create the `.cursor/rules/linkforge.mdc` project rule below.
3. Review and accept the file Cursor proposes.

With `alwaysApply: true`, every later generation in this lab follows these standards without a reminder.

Create `.cursor/rules/linkforge.mdc`:

```markdown
---
description: "LinkForge engineering standards"
alwaysApply: true
---
You are an expert Python backend engineer building production-grade microservices.
**Coding Standards:**
- Use async/await everywhere for I/O operations
- Pydantic v2 for strict schema validation
- Type hints on all functions
- SQLAlchemy ORM for database abstraction
- Dependency injection for all services
**Architecture Patterns:**
- Service layer for business logic (not in routes)
- Repository pattern for data access
- Factory pattern for connection pooling
**Testing:**
- Unit tests must mock external dependencies (Redis, PostgreSQL)
- Integration tests use Docker containers
- 80%+ code coverage minimum
**Performance:**
- Async-first: No blocking calls in request handlers
- Cache frequently accessed data in Redis
- Use connection pooling for databases
**Naming Conventions:**
- Routes: `/api/v1/{resource}`
- Services: `*Service` (e.g., ShorteningService)
- Models: `*Schema` (Pydantic), `*Model` (SQLAlchemy)
```

### Step 3: Scaffold the Project

**Prompt to Composer:**

```text
Create a FastAPI project structure for LinkForge, a URL shortener microservice.

Implement:
1. main.py - Entry point with FastAPI app, root health check endpoint
2. models.py - SQLAlchemy ORM models:
   - User (id, username, email, api_key, created_at)
   - Link (id, user_id, original_url, short_code, created_at, expires_at)
   - AnalyticsEvent (id, link_id, clicked_at, referrer, ip_address)
3. schemas.py - Pydantic v2 models:
   - LinkCreate (original_url: str)
   - LinkResponse (short_code: str, original_url: str, created_at: datetime)
   - AnalyticsResponse (total_clicks: int, unique_users: int)
4. database.py - SQLAlchemy async session setup, get_db dependency
5. shortener.py - Core logic:
   - generate_short_code(url: str) -> str (use base62 encoding, handle collisions)
   - validate_url(url: str) -> bool
6. requirements.txt with: fastapi, uvicorn, sqlalchemy, asyncpg, redis, pydantic

Use async patterns everywhere. Include proper error handling.
```

### Step 4: Verify Output

Cursor generates several files at once in the Agents Window. Before you move on, check:
- [ ] Imports resolve across all generated files
- [ ] async/await used consistently in I/O paths
- [ ] Models use Pydantic v2 `ConfigDict`, not the v1 `class Config`
- [ ] Database sessions are `AsyncSession` via the async sessionmaker
- [ ] Short codes come from base62 encoding, with collision handling

### Step 5: Install and Run

**Prompt to Composer:**
```text
Build the project using pip and a project requirement file in the latest Python environment. Start the server and then open the documentation URL in a web browser to review the API specifications.
```

As of November 7, 2026, Cursor's default run mode is Auto-review, under Settings > Agents > Approvals & Execution. It runs allowlisted and sandboxed commands without asking. It sends the rest to a safety classifier. Expect approval requests for some commands only. Review each one as it comes up.

Along the way, the agent may adjust code and configuration (dependency versions, environment settings) until the objective is met. When the server is up, open `http://localhost:8000/docs` for the Swagger UI.

## Phase 2: Iterate over the Build (Cursor Agent Chat)

**Goal**: Layer in Redis caching and asynchronous click-event analytics.

### Step 1: Refactor with Cursor

**Prompt to Composer:**

```text
Refactor LinkForge to add:

1. Redis Integration:
   - Add redis dependency to requirements.txt
   - Create cache.py with RedisCache class (singleton pattern)
   - Cache short_code lookups (1-hour TTL)
   - Invalidate cache when link is updated

2. Analytics Service:
   - Create analytics.py with AnalyticsService
   - On link redirect, emit async event to Redis stream
   - Track: clicked_at, referrer header, user_agent (for device detection)
   - Use Pydantic for event schema validation

3. Update database.py:
   - Add async Redis client initialization
   - Implement connection pooling with pool_size=20

4. Update shortener.py:
   - Inject RedisCache and AnalyticsService
   - Log click event when short_code is redirected

Maintain all existing tests. Use dependency injection for services.
```

### Step 2: Iterate to Stabilize the Application

When you see the refactored code, prompt again where needed. Section 7.6 uses these two follow-ups. Send them one at a time:

```text
The main file looks good, but it still has a pending TODO for the authentication dependency.
```

```text
Analytics service is good, but implement exponential backoff for Redis pushes in case of temporary connection loss.
```

Repo addition: the reference implementation also enforces the free-tier quota from the technical requirements (`src/ratelimit.py`). If your build has no rate limit yet, ask for one:

```text
Add rate limiting for the shortening endpoint: 100 requests per user per day on the free tier, counted in Redis.
```

Between prompts, use Tab for small changes. Or select the code and press Cmd+K / Ctrl+K to send only that selection to the agent. As of November 7, 2026, this takes the place of Inline Edit.

## Phase 3: Auditor (Testing with Cursor Chat)

**Goal**: Generate a thorough test suite with edge case coverage.

### Step 1: Generate Test Structure

**Prompt to Composer:**

```text
Generate a thorough pytest test suite for LinkForge with at least 85% coverage.

Requirements:
- Test all async endpoints (create_short_url, redirect, get_analytics)
- Test edge cases: duplicate URLs, expired links, invalid formats, malformed URLs
- Test Redis cache hit/miss scenarios
- Test concurrent requests (simulate 100 simultaneous shortens)
- Test analytics data accuracy under load
- Test rate limiting enforcement (100 shortening requests/user/day on the free tier)
- Mock PostgreSQL and Redis (no actual database connections in tests)
- Aim for 85%+ code coverage

Organize tests into:
  tests/test_shortening.py - URL creation and validation
  tests/test_analytics.py - Click tracking and event streaming
  tests/test_security.py - Rate limiting and authorization
  tests/conftest.py - Pytest fixtures and mock setup

Test async routes with pytest and AsyncClient. Mock Redis and database using unittest.mock. Include parameterized tests for edge cases. Organize all test scripts in a dedicated folder. Run the dependency servers and verify that the test coverage meets the specified criteria. Create a single script to run servers and API tests, and a user guide for running tests. Please run the suite and ensure that all tests are passing and the coverage target is met.
```

### Step 2: Review and Improve Test Coverage

The agent will not always hit the target on the first pass. Check it yourself. Run the suite in the integrated terminal:

```bash
pytest --cov=src --cov-report=html
```

If tests fail or coverage falls short, give the terminal output back to the agent:

1. Select the output.
2. Press Cmd+L / Ctrl+L to add it to the current chat. Or press Cmd+Shift+L / Ctrl+Shift+L to start a new agent with it.
3. Ask the agent to fix the failing cases.

Cursor's keyboard-shortcuts reference page lists this pair the other way around. The bindings here are the ones Cursor 3.25 ships.

### Step 3: Test the Service

**Prompt to Composer:**

```text
The microservice is built and unit tested. It depends on the database and Redis cache servers. Create the complete application starter script that runs all required services and then the functional test of all APIs on the operational server (e.g., port 8000). Ensure all functional use cases are tested. Resolve any testing issues by checking the requirements and fixing the code to ensure full functionality. Ask for help if needed. Create a User Guide Read me for the application with steps to set up the environment and run the server and test. Run the server per the guide.
```

Approve the permission requests as they come up. The reference implementation's starter script is `linkforge/run.sh`. Its guide is `linkforge/README.md`.

## Phase 4: Delegator (Copilot Cloud Agent)

**Goal**: Automate deployment with GitHub Copilot.

### Step 1: Open in VS Code and Generate Repository Instructions

1. Open the LinkForge folder in VS Code.
2. Sign in with a Copilot-enabled GitHub account. Hover over the Copilot icon in the Status Bar and select **Use AI Features**.
3. In the Copilot chat, run `/init`. Copilot analyzes the project and writes its instructions file.
4. Read the generated file. Correct anything it got wrong about the project before you continue.

Current VS Code documents `/init` as "generate or update workspace instructions" and does not name the file. The book expects `.github/copilot-instructions.md`. That is also the file the Copilot CLI's `/init` writes.

### Step 2: Push to GitHub

Create an empty repository on GitHub, for example `linkforge`. Then push from the LinkForge folder. Use Cursor's built-in Git support or a terminal:

```bash
git init
git add .
git commit -m "Initial LinkForge implementation"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/linkforge.git
git push -u origin main
```

If you are new to this, ask Copilot in chat. The book's version of the prompt is `@github Help me with instructions to push this GitHub project to the agenticcoders account.` As of November 7, 2026, the default Copilot harness in VS Code does not support chat participants such as `@github`. Leave the prefix off and use your own account name.

### Step 3: Create Deployment Issue

On GitHub, open a new issue. Add Copilot as the assignee (**Assignees**, then **Copilot**), as you would a human teammate.

This needs a Copilot plan that includes the cloud agent. It is not part of Copilot Free. On Business and Enterprise plans it follows the organization's Copilot in the cloud policy. As of November 7, 2026, that policy is on by default. An administrator can turn it off.

```text
Title: Deploy LinkForge to Azure Container Instances with CI/CD

Please generate:

1. **Dockerfile**
   - Multi-stage build (builder stage for dependencies)
   - Python 3.11 slim image
   - Health check for Kubernetes readiness probe
   - Non-root user (security best practice)

2. **.github/workflows/deploy-azure.yml**
   - Trigger on push to main
   - Run: pytest, flake8, mypy checks
   - Build Docker image
   - Push to Azure Container Registry (ACR)
   - Deploy to Azure Container Instances (ACI)
   - Update DNS record to point to new container
   - Include rollback if health check fails

3. **.env.example**
   - DATABASE_URL=postgresql+asyncpg://user:pass@localhost/linkforge
   - REDIS_URL=redis://localhost:6379
   - AZURE_CONTAINER_REGISTRY_URL=
   - AZURE_CONTAINER_INSTANCE_NAME=

4. **docker-compose.yml** (for local development)
   - FastAPI service
   - PostgreSQL service
   - Redis service
   - Network configuration

Include comments explaining each step.
```

### Step 4: Wait for Agent Completion

The cloud agent works through these steps:

1. It acknowledges the issue.
2. It analyzes the codebase.
3. It generates the Dockerfile and workflow.
4. It opens a pull request with a summary of the changes.

You get a notification when the pull request is ready for review. GitHub Actions workflows do not run automatically on the agent's pushes. Approve them on the pull request with **Approve and run workflows**.

### Step 5: Review and Merge

Review the Dockerfile and workflow, then merge.

Before the deploy job can succeed, add the secrets the workflow reads to the repository. The reference workflow (`linkforge/.github/workflows/deploy-azure.yml`) reads these:

- `AZURE_CREDENTIALS`
- `AZURE_CONTAINER_REGISTRY_URL`
- `AZURE_REGISTRY_USERNAME`
- `AZURE_REGISTRY_PASSWORD`
- `AZURE_RESOURCE_GROUP`
- `AZURE_CONTAINER_INSTANCE_NAME`
- `DATABASE_URL`
- `REDIS_URL`
- `SECRET_KEY`

The agent's workflow may name them differently. Check its file. After the merge, a push to `main` tests, builds, and deploys the application.

### Step 6: Iterate and Improve

Keep assigning follow-up issues to Copilot. You can also open a pull request yourself and request a review from Copilot under **Reviewers**.

## Challenge: Multi-Tenant Transformation

**Reference**: Chapter 7, Section 7.7

LinkForge works. Now the product needs Teams, so several people can manage links for one organization. This is the open-ended extension. There is no answer key, because agentic output is not reproducible line for line. This section gives:

- the requirements
- the starting prompts
- success criteria you can check yourself

Branch before you start. You can then diff what the agent changed:

```bash
git checkout -b challenge-multi-tenant
```

### Requirements

1. **Database refactoring:**
   - New `Team` model: id, name, owner_id, created_at
   - New `TeamMember` model: team_id, user_id, role (admin | editor | viewer)
   - `Link` gains a `team_id` foreign key

2. **Authorization:**
   - Only team admins can invite or remove members
   - Only admins and editors can create or delete links
   - Any member of a team can view its analytics
   - RBAC checks present in every endpoint

3. **Analytics by team:**
   - `GET /api/v1/teams/{team_id}/analytics/summary` aggregates click counts over every link the team owns

4. **Testing:**
   - An admin of Team 1 (User A) has no access to Team 2's links
   - Promotion and demotion of team members works
   - Analytics stay isolated per team (User C never sees another team's data)

### Refactoring Path (Cursor Agents Window)

**Prompt to Composer:**

```text
Refactor LinkForge to support multi-tenant teams:

1. Add models (models.py):
   - Team model with owner_id, created_at
   - TeamMember model with role enum (admin, editor, viewer)
   - Add team_id FK to Link model

2. Update schemas (schemas.py):
   - LinkCreate now requires team_id
   - New schemas: TeamCreate, TeamMemberAdd, TeamResponse

3. Add authorization (auth.py):
   - get_current_user dependency
   - check_team_membership dependency (verifies user is member of team)
   - check_team_admin dependency (verifies user is admin)

4. Update routes (routes/links.py):
   - POST /api/v1/teams/{team_id}/links - Create link (require team membership)
   - GET /api/v1/teams/{team_id}/links - List team links
   - GET /api/v1/teams/{team_id}/analytics/summary - Aggregate analytics

Maintain backward compatibility for single-user links.
```

### Testing Path (Cursor Chat)

**Prompt:**

```text
Generate pytest tests for multi-tenant security:
- User A (admin of Team 1) cannot view Team 2's links
- User B (viewer of Team 1) cannot delete links
- User C (non-member) receives 403 Forbidden
- Analytics are correctly isolated per team
- Concurrent requests from different users don't leak data
```

### Success Criteria

- [ ] Three new model classes
- [ ] Two new API routes
- [ ] At least five integration tests passing
- [ ] Zero cross-tenant data leakage
- [ ] Coverage of 85% or better (`pytest --cov=src --cov-report=term-missing`)

## Troubleshooting

**Port 8000 already in use.** `uvicorn` exits with "address already in use". Usually a plain `docker-compose up -d` also started the containerized API, and it holds port 8000. Free it with `docker-compose stop app`. Or run the local server on another port (`uvicorn src.main:app --reload --port 8001`). To find any other process on the port, run `lsof -i :8000` (macOS/Linux) or `netstat -ano | findstr :8000` (Windows).

**Port 5432 or 6379 already in use.** `docker-compose up -d db redis` fails with "port is already allocated". A local PostgreSQL or Redis (or another project's container) already holds the port. Stop that service. Or change the host side of the mapping in `docker-compose.yml` (for example `"5433:5432"`), and point `DATABASE_URL` or `REDIS_URL` in `.env` at the new port.

**`docker-compose: command not found`.** Newer Docker installs ship Compose as a plugin. Run `docker compose` (with a space) wherever this lab says `docker-compose`. The two are interchangeable here. `run.sh` detects whichever you have.

**Docker is not running.** `docker-compose up` fails with "Cannot connect to the Docker daemon" (or "error during connect" on Windows). Start Docker Desktop, or on Linux run `sudo systemctl start docker`. Confirm with `docker info` and retry.

**Dependency-version drift.** Every entry in `linkforge/requirements.txt` carries a compatible upper bound. A fresh install resolves to the versions the code and tests were written against. If imports or tests fail inside an older virtual environment:

1. Recreate it with `python3 -m venv venv`.
2. Activate it with `source venv/bin/activate` (or `venv\Scripts\activate` on Windows).
3. Reinstall with `pip install -r requirements.txt`. Do not upgrade packages one by one.

**Verifying the test suite.** From `linkforge/`, run:

```bash
pytest --cov=src
```

Expected outcome:

- All 111 tests pass across the five test files (shortening, analytics, cache, security, rate limiting).
- The per-module coverage table ends with a total of about 87%.

The suite needs no running services. It uses a temporary SQLite database and in-memory Redis stand-ins. It works before you start Docker. A failure here points at your environment (see the drift entry above). It does not point at Postgres or Redis.

The CI workflow runs the same command with these gates:

- an 80% coverage floor (`--cov-fail-under=80`)
- flake8 as a hard gate
- mypy as an advisory step. The reference still reports type errors, so that step is marked `continue-on-error`.

The reference implementation clears the hard gates. flake8 is clean and coverage is about 87%. Use the same gates as the bar for the suite you generate in Phase 3.

## Teardown

**Local.** `docker-compose down` stops the Postgres and Redis containers. It keeps their data. To also remove the named volumes (`postgres_data`, `redis_data`) and every stored link, run:

```bash
docker-compose down -v
```

**Azure (Phase 4).** The Container Registry and Container Instance created in Phase 4 bill for as long as they exist, even when idle. When you finish the lab, delete the whole resource group. This removes the container instance, the registry, and every image pushed to it:

```bash
az group delete --name <your-resource-group> --yes --no-wait
```

Verify with `az group exists --name <your-resource-group>`. It prints `false` once deletion completes. If you created the repository only for this lab, also remove the `AZURE_*`, `DATABASE_URL`, `REDIS_URL`, and `SECRET_KEY` secrets from its GitHub settings.

## Why each tool owns its phase

Why Cursor owns Phases 1 to 3 and Copilot's cloud agent owns Phase 4: Chapter 7, Sections 7.4 and 7.5.

## Resources

- [Cursor Documentation](https://cursor.com/docs)
- [GitHub Copilot Documentation](https://docs.github.com/copilot)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLAlchemy Async Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
