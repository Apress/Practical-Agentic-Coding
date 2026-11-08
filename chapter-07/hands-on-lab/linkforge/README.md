# LinkForge - URL Shortener Microservice

This is the reference implementation of the Chapter 7 lab. It is a URL shortening service with real-time analytics. It was built with the **Hybrid Workflow**, using Cursor and GitHub Copilot.

## Features

- **URL Shortening**: Generate short codes using Base62 encoding
- **Real-time Analytics**: Track clicks, referrers, and user agents. Aggregates are computed from the database.
- **Redis Caching**: Short-code lookups are served from Redis (the lab's target is sub-millisecond). Exponential backoff applies when Redis is unreachable.
- **Rate Limiting**: Redis-backed daily quota on `POST /api/v1/links` (`RATE_LIMIT_PER_DAY`, default 100 per caller per UTC day). Returns 429 once spent.
- **Async Architecture**: FastAPI with async/await throughout

One item is deliberately unfinished. The authentication dependency in `src/main.py` is a `TODO`. You resolve it with Cursor in the Chapter 7 lab (Phase 2, Step 2). Until then, rate limiting identifies callers by the `X-API-Key` header when present. Otherwise it uses the client IP.

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Redis (via Docker or local)
- PostgreSQL (via Docker or local)

### Installation

The one-command path is `./run.sh`. It starts Postgres and Redis, waits for both to be healthy, and runs the API on port 8000. Step by step:

```bash
# Clone and enter directory
cd linkforge

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env      # Windows: copy .env.example .env

# Start Postgres + Redis with Docker
docker-compose up -d db redis

# Run the application (--env-file loads your .env)
uvicorn src.main:app --reload --env-file .env
```

`./run.sh` runs the same sequence after the install step. It needs a POSIX shell (macOS, Linux, WSL, or Git Bash on Windows).

> Note: plain `docker-compose up -d` also builds and starts the containerized API on port 8000. Start only `db` and `redis` when you run the API locally with uvicorn.

When you are done, `docker-compose down` stops the containers. `docker-compose down -v` also deletes the data volumes.

### API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/links` | Create short URL |
| GET | `/api/v1/links/{code}` | Get link details |
| GET | `/{code}` | Redirect to original URL |
| GET | `/api/v1/links/{code}/analytics` | Get click analytics |

## Project Structure

```text
linkforge/
├── src/
│   ├── main.py           # FastAPI application
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic schemas
│   ├── database.py       # Database configuration
│   ├── shortener.py      # URL shortening logic
│   ├── cache.py          # Redis caching
│   ├── analytics.py      # Analytics service
│   └── ratelimit.py      # Redis-backed daily quota
├── tests/
│   ├── conftest.py       # Pytest fixtures
│   ├── test_shortening.py
│   ├── test_analytics.py
│   ├── test_cache.py
│   ├── test_security.py
│   └── test_ratelimit.py
├── .cursor/
│   └── rules/
│       └── linkforge.mdc # Cursor project rule
├── .github/
│   ├── copilot-instructions.md
│   └── workflows/
│       └── deploy-azure.yml
├── AGENTS.md             # AI agent instructions
├── requirements.txt      # Dependencies, all upper-bounded
├── run.sh                # One-command local launcher
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Configuration

### Environment Variables

These are the variables the code reads (see `src/database.py`, `src/cache.py`, `src/ratelimit.py`, `src/main.py`). `.env.example` lists all of them. uvicorn loads the file when you pass `--env-file .env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Async PostgreSQL connection string | `postgresql+asyncpg://postgres:postgres@localhost:5432/linkforge` |
| `REDIS_URL` | Redis connection string (cache + rate limiter) | `redis://localhost:6379` |
| `RATE_LIMIT_PER_DAY` | Shortening requests allowed per caller per UTC day | `100` |
| `DEBUG` | `true` enables SQLAlchemy SQL echo | `false` |
| `LOG_LEVEL` | Python logging level | `INFO` |

`SECRET_KEY` appears in `.env.example`, and the deploy workflow passes it through. No current code reads it. It is reserved for the authentication exercise (the `TODO` in `src/main.py`).

## Development

### Running Tests

The suite needs no running services. It uses SQLite plus in-memory Redis stand-ins. On the reference build, all 111 tests pass with total coverage of about 87%.

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_shortening.py -v
```

### Code Quality

```bash
# Format code
black src tests

# Check types
mypy src

# Lint
flake8 src tests
```

## Deployment

### Docker Build

```bash
docker build -t linkforge:latest .
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@your-db-host:5432/linkforge \
  -e REDIS_URL=redis://your-redis-host:6379 \
  linkforge:latest
```

The app fails fast if the database is unreachable at startup. The container needs `DATABASE_URL` and `REDIS_URL` pointing at running services. For a fully containerized local stack on one network, use `docker-compose up -d` (API + Postgres + Redis).

### CI/CD Pipeline

The project includes a GitHub Actions workflow (`.github/workflows/deploy-azure.yml`) that:
1. Runs tests and linting
2. Builds the Docker image
3. Pushes to Azure Container Registry
4. Deploys to Azure Container Instances and health-checks `/health`
5. On success, promotes the deployed image to the `:stable` tag. On failure, rolls back by redeploying `:stable` (the last image that passed its health check).

The test job gates on flake8 and an 80% coverage floor. mypy is an advisory step. The same gates are the bar for the code you build in the Chapter 7 lab. The reference implementation as shipped passes them. flake8 is clean and coverage is about 87%.

The build and deploy jobs read these repository secrets (Settings > Secrets and variables > Actions):

- `AZURE_CREDENTIALS`
- `AZURE_CONTAINER_REGISTRY_URL`
- `AZURE_REGISTRY_USERNAME`
- `AZURE_REGISTRY_PASSWORD`
- `AZURE_RESOURCE_GROUP`
- `AZURE_CONTAINER_INSTANCE_NAME`
- `DATABASE_URL`
- `REDIS_URL`
- `SECRET_KEY`

Without them, the test job still runs. The build job fails at its Azure login step, and the deploy job never starts.

> **Action versions (as of November 7, 2026).** The workflow pins `azure/login@v1`, `azure/docker-login@v1`, `azure/aci-deploy@v1`, and `codecov/codecov-action@v3`.
>
> - Those versions declare Node 12 or Node 16 runtimes. GitHub has retired both.
> - Newer majors exist for all but `azure/aci-deploy`. It has had no release since 2021.
> - The newest `azure/docker-login` major (v2) still targets Node 20, which GitHub has also retired. Its README says the action is not maintained.
>
> Treat the deploy jobs as a reference. Check them against current action versions before you rely on them. The test job depends on none of these actions except Codecov's upload, which is set not to fail the build.

The Azure resources bill while they exist. When you are done, delete the resource group (`az group delete --name <your-resource-group> --yes`). The lab README's Teardown section has details.

## AI Development Workflow

This project was built using the **Hybrid Workflow**:

1. **Phase 1 (Cursor agent chat)**: Scaffold the project structure (Composer model)
2. **Phase 2 (Cursor Tab)**: Add Redis caching and analytics
3. **Phase 3 (Cursor agent chat)**: Generate thorough tests
4. **Phase 4 (Copilot cloud agent)**: Automate deployment via issue assignment

The governance files for AI configuration are:
- `AGENTS.md` - General agent instructions (auto-detected by Cursor and Copilot)
- `.cursor/rules/linkforge.mdc` - Cursor project rule (`alwaysApply: true`, so it governs every prompt)
- `.github/copilot-instructions.md` - GitHub Copilot context (generate with `/init` in VS Code chat)

## License

See `LICENSE.txt` at the repository root.
