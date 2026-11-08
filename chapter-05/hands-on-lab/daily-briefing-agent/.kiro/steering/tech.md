---
inclusion: always
---

# Tech News Aggregator Development Guidelines

## Architecture Patterns (MANDATORY)

### Code Organization

- **Repository Pattern**: ALWAYS separate data access (`src/repositories/`) from business logic (`src/services/`)
- **Pydantic Models**: Use for ALL data structures in `src/models/` - no exceptions
- **Type Hints**: Required for all function parameters and return types
- **Central Config**: Use `src/config.py` Config class for ALL settings - never hardcode values

### Error Handling Standards

- Use specific exception types, not bare `except:`
- Implement retry logic with exponential backoff for AWS service calls
- Return proper HTTP status codes (200, 400, 404, 500)
- Log errors with structured logging (include context, not just message)

### Dependency Injection

- Services receive dependencies through constructor injection
- Supports testing with mocks
- Configuration loaded once at startup, passed to components

## Technology Stack Rules

### Python (3.11+) Requirements

| Library | Purpose | Version |
|---------|---------|---------|
| Flask | Web framework for HTTP endpoints | 3.0+ |
| Pydantic | Data validation and serialization | 2.0+ |
| boto3 | AWS SDK interactions | Latest |
| SQLAlchemy | ORM for Aurora PostgreSQL | 2.0+ |
| requests | HTTP client for web scraping | Latest |
| beautifulsoup4 | HTML parsing for scraping | Latest |
| pytest | Testing framework | Latest |
| hypothesis | Property-based testing | Latest |

### AWS Services Usage

| Service | Purpose | Notes |
|---------|---------|-------|
| Amazon Bedrock | AI summaries with Claude | Haiku-tier primary, Sonnet-tier fallback |
| Aurora PostgreSQL | Primary database | Private subnet, VPC endpoint |
| AWS App Runner | Container deployment | VPC Connector required |
| Amazon S3 | Briefing file storage | VPC endpoint access |
| Secrets Manager | Credential storage | Auto-rotation enabled |
| CloudWatch | Monitoring and metrics | Custom namespace |

**Note**: The App Runner rows reflect where the lab ends up after Phase 8. The book's Phase 2 constraint deliberately pins Amazon Lightsail + CloudFront first; the temporary disagreement between your spec and this table is intended, and Phase 8 resolves it. When the spec in `.kiro/specs/` and this table conflict, follow the spec.

### Amazon Bedrock Configuration

Model IDs come from the environment, never from a literal in application code.
Bedrock's Claude lineup changes and availability varies by region, so the current
ID belongs in configuration where it can be updated without a code change.

Current Claude models on Bedrock accept only the default sampling settings, so requests leave out temperature, top_p, and top_k. They also think by default: a response can start with a thinking block, so read the summary from the content block whose type is text rather than content[0], and leave max_tokens room for the thinking.

```python
BEDROCK_CONFIG = {
    'primary_model': os.environ['BEDROCK_MODEL_ID'],
    'fallback_model': os.environ['BEDROCK_FALLBACK_MODEL_ID'],
    'max_tokens': 4096,
    'region': os.getenv('AWS_REGION', 'us-east-1')
}
```

See `.env.example` for the defaults and for how to confirm the right ID for your
region.

## Code Style (NON-NEGOTIABLE)

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Files | `snake_case.py` | `story_collector.py` |
| Classes | `PascalCase` | `StoryCollector` |
| Functions/Variables | `snake_case` | `collect_stories` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_RETRY_COUNT` |
| Test files | `test_` prefix | `test_story_collector.py` |

### Import Order

```python
# 1. Standard library
import os
from typing import List, Optional
from datetime import datetime

# 2. Third-party (blank line before)
import boto3
from flask import Flask, jsonify
from pydantic import BaseModel

# 3. Local imports (blank line before)
from src.config import get_config
from src.models.story import Story
from src.services.collector import StoryCollector
```

### Docstring Format (Google Style)

```python
def generate_summary(story: Story, config: Config) -> str:
    """Generate a witty summary for a tech story.

    Uses Amazon Bedrock with Claude to create summaries that maintain
    the Witty Tech Journalist persona.

    Args:
        story: The Story object to summarize.
        config: Application configuration with Bedrock settings.

    Returns:
        A witty, cynical summary of the story.

    Raises:
        BedrockError: If the AI service is unavailable.
        ValidationError: If the story content is insufficient.
    """
```

## Testing Strategy (REQUIRED)

### Test Categories & Markers

| Marker | Purpose | Dependencies |
|--------|---------|--------------|
| `@pytest.mark.unit` | Fast, isolated tests | Mocked everything |
| `@pytest.mark.integration` | LocalStack-based tests | LocalStack running |
| `@pytest.mark.property` | Hypothesis-based tests | hypothesis library |
| `@pytest.mark.browser` | Playwright UI tests | Browser available |

### Coverage Requirements

- **Minimum**: 70% overall code coverage
- **Critical paths**: 90% coverage for business logic
- **Use `conftest.py`** for shared fixtures
- **Use moto** for AWS service mocking in unit tests

### Test File Organization

```text
tests/
├── conftest.py              # Shared fixtures
├── test_models.py           # Data model tests
├── test_services.py         # Business logic tests
├── test_repositories.py     # Data access tests
├── test_api.py              # API endpoint tests
├── test_integration.py      # Integration tests (LocalStack)
└── test_property.py         # Property-based tests
```

## Environment Configuration

### Environment Precedence (STRICT ORDER)

1. System environment variables (highest priority)
2. `.env` files (`.env.local`, `.env.dev`, `.env.prod`)
3. Config class defaults (lowest priority)

### Required Environment Variables

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_PROFILE=your-profile  # or use IAM role

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname
# Or use Secrets Manager
DATABASE_SECRET_ARN=arn:aws:secretsmanager:...

# Application
FLASK_ENV=development
LOG_LEVEL=INFO

# Feature Flags
ENABLE_BEDROCK=true
ENABLE_CACHING=true
```

### LocalStack Configuration

For local development, detect LocalStack automatically:

```python
if os.getenv('LOCALSTACK_ENDPOINT'):
    # Use LocalStack endpoints
    s3_client = boto3.client('s3', endpoint_url=os.getenv('LOCALSTACK_ENDPOINT'))
else:
    # Use real AWS
    s3_client = boto3.client('s3')
```

## Development Commands

### Essential Workflows

```bash
# Development server
python run_dev_server.py

# Testing
pytest -m unit                    # Fast mocked tests
pytest -m integration             # LocalStack tests
pytest -m "not integration"       # All except integration
make test-coverage                # With coverage report

# Code quality
make format                       # black + isort
make lint                         # flake8 + mypy
make check                        # All quality checks

# LocalStack
docker compose -f docker-compose.localstack.yml up -d
python scripts/setup_localstack.py
```

## AWS Integration Patterns

### Bedrock Best Practices

- Use the Haiku tier for summaries (cost-effective, fast), with the Sonnet tier as the fallback
- Implement retry with exponential backoff
- Track token usage for cost monitoring
- Cache summaries for duplicate content
- Handle rate limiting gracefully (429 responses)

### Database Patterns

- Use SQLAlchemy ORM with proper relationship mapping
- Implement connection pooling for Aurora
- Use read replicas for query-heavy operations
- Index frequently queried columns
- Use bulk operations for batch inserts

### Error Handling for AWS Services

```python
import botocore.exceptions

try:
    response = bedrock_client.invoke_model(...)
except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] == 'ThrottlingException':
        # Implement backoff and retry
        pass
    elif e.response['Error']['Code'] == 'ValidationException':
        # Log and use fallback
        pass
    else:
        raise
```

## Security Requirements

### Never Do

- Hardcode credentials or API keys
- Log sensitive data
- Store secrets in code or config files
- Disable SSL verification
- Use pickle for untrusted data

### Always Do

- Use Secrets Manager for credentials
- Validate all user inputs
- Use parameterized queries
- Enable encryption at rest and in transit
- Follow least privilege for IAM roles
