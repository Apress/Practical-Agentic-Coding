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
- Implement retry logic for AWS service calls
- Return proper HTTP status codes (200, 400, 404, 500)
- Log errors with structured logging

## Technology Stack Rules

### Python (3.11+) Requirements
- **Flask**: Web framework for HTTP endpoints
- **Pydantic**: Data validation and serialization
- **boto3**: AWS SDK interactions
- **pytest**: Testing with markers (`@pytest.mark.unit`, `@pytest.mark.integration`)

### AWS Services Usage
- **Bedrock**: Claude Sonnet 4.5 for complex summaries, Claude Haiku 4.5 for simple tasks
- **Aurora PostgreSQL**: Primary database with proper indexing and foreign keys
- **S3**: File storage for briefings and static assets
- **Lambda**: Background processing with thin handlers

## Code Style (NON-NEGOTIABLE)

### Naming Conventions
- **Files**: `snake_case.py` (e.g., `story_collector.py`)
- **Classes**: `PascalCase` (e.g., `StoryCollector`)
- **Functions/Variables**: `snake_case` (e.g., `collect_stories`)
- **Tests**: `test_` prefix (e.g., `test_story_collector.py`)

### Import Order
```python
# 1. Standard library
import os
from typing import List, Optional

# 2. Third-party (blank line before)
import boto3
from pydantic import BaseModel

# 3. Local imports (blank line before)
from src.config import get_config
from src.models.story import Story
```

## Testing Strategy (REQUIRED)

### Test Categories & Markers
- `@pytest.mark.unit`: Fast, mocked dependencies (use `moto` for AWS)
- `@pytest.mark.integration`: LocalStack-based AWS testing
- `@pytest.mark.property`: Hypothesis-based property testing
- `@pytest.mark.browser`: Playwright UI testing

### Coverage Requirements
- Minimum 70% code coverage
- Use `conftest.py` for shared fixtures
- Use `browser_fixtures.py` for UI test setup

## Environment Configuration

### Environment Precedence (STRICT ORDER)
1. System environment variables (highest)
2. `.env` files (`.env.local`, `.env.dev`, `.env.prod`)
3. Config class defaults (lowest)

### LocalStack Integration
- Config automatically detects LocalStack endpoints
- Use for integration testing, not unit tests

## Development Commands

### Essential Workflows
```bash
# Development server
python run_dev_server.py

# Testing
python scripts/test_runner.py unit        # Fast mocked tests
python scripts/test_runner.py integration # LocalStack tests
make test-browser                         # UI tests

# Code quality (run before commits)
make format  # black (line length 88)
make lint    # flake8 + mypy
```

## AWS Integration Patterns

### Bedrock Best Practices
- Use Claude Sonnet 4.5 for complex summaries (higher cost, better quality)
- Use Claude Haiku 4.5 for simple tasks (lower cost, faster)
- Always implement retry logic and fallback strategies
- Handle rate limiting gracefully

### Database Patterns
- Use normalized relational design with proper foreign keys
- Use SQL joins for complex queries
- Use bulk operations for performance
- Index frequently queried columns

### Lambda Development
- Keep handlers thin - delegate to service layer
- Use Config class for environment variables
- Return structured error responses
- Optimize memory allocation based on usage patterns

## Infrastructure as Code

### CloudFormation Rules
- Templates in `infrastructure/cloudformation/`
- Environment parameters in `infrastructure/parameters/`
- Always validate before deployment: `python infrastructure/deploy.py validate`
- Use consistent resource naming: `{env}-tech-news-{resource}`

## Performance & Cost Optimization

### Monitoring Requirements
- Use structured logging with appropriate levels
- Monitor Lambda execution times and error rates
- Set up CloudWatch alarms for critical failures

### Cost Management
- Choose appropriate Bedrock model for task complexity
- Use Aurora Serverless v2 for variable workloads
- Optimize Lambda memory allocation

## Product Context

This is a tech news aggregator with a "Witty Tech Journalist" persona that:
- Cuts through tech industry hype with skeptical commentary
- Provides substance-focused, slightly cynical summaries
- Maintains sharp but informative tone
- Prioritizes quality over quantity in content curation