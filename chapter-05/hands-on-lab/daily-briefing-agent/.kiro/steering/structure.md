# Project Structure & Organization

## Directory Layout

```text
daily-briefing-agent/
├── src/                          # Source code (main application)
│   ├── models/                   # Pydantic data models
│   │   ├── __init__.py
│   │   ├── story.py              # Story, Category models
│   │   ├── source.py             # Source configuration model
│   │   └── summary.py            # SummaryMetadata model
│   ├── services/                 # Business logic services
│   │   ├── __init__.py
│   │   ├── story_collector.py    # Story collection from sources
│   │   ├── summary_generator.py  # AI summary generation
│   │   ├── ranking_engine.py     # Story ranking and scoring
│   │   └── briefing_generator.py # Daily briefing creation
│   ├── repositories/             # Data access layer
│   │   ├── __init__.py
│   │   ├── base.py               # Base repository class
│   │   ├── story_repository.py   # Story CRUD operations
│   │   └── source_repository.py  # Source management
│   ├── scrapers/                 # Web scraping modules
│   │   ├── __init__.py
│   │   ├── base_scraper.py       # Abstract scraper interface
│   │   └── hackernews_scraper.py # Hacker News implementation
│   ├── web/                      # Flask web application
│   │   ├── __init__.py
│   │   ├── app.py                # Flask app factory
│   │   ├── routes.py             # HTTP route handlers
│   │   ├── templates/            # Jinja2 templates
│   │   │   ├── base.html
│   │   │   ├── feed.html
│   │   │   └── story_card.html
│   │   └── static/               # CSS, JavaScript
│   │       ├── css/
│   │       └── js/
│   ├── config.py                 # Centralized configuration
│   └── __init__.py
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py               # Shared test fixtures
│   ├── test_models.py            # Model tests
│   ├── test_services.py          # Service tests
│   ├── test_repositories.py      # Repository tests
│   ├── test_scrapers.py          # Scraper tests
│   ├── test_api.py               # API endpoint tests
│   ├── test_integration.py       # Integration tests
│   └── test_property.py          # Property-based tests
├── infrastructure/               # Infrastructure as Code
│   ├── cloudformation/           # CloudFormation templates
│   │   ├── vpc.yaml              # VPC and networking
│   │   ├── database.yaml         # Aurora PostgreSQL
│   │   ├── apprunner.yaml        # App Runner service
│   │   └── monitoring.yaml       # CloudWatch resources
│   ├── parameters/               # Environment parameters
│   │   ├── dev.json
│   │   └── prod.json
│   └── deploy.py                 # Deployment automation
├── scripts/                      # Utility scripts
│   ├── setup_localstack.py       # LocalStack resource setup
│   ├── test_runner.py            # Test execution helper
│   └── seed_data.py              # Development data seeding
├── docs/                         # Documentation
│   └── api.md                    # API documentation
├── .kiro/                        # Kiro IDE configuration
│   ├── steering/                 # Steering files
│   │   ├── product.md
│   │   ├── tech.md
│   │   └── structure.md
│   ├── specs/                    # Specifications
│   │   └── tech-news-aggregator/
│   │       ├── requirements.md
│   │       ├── design.md
│   │       └── tasks.md
│   ├── hooks/                    # Hook configurations
│   │   ├── test-coverage.kiro.hook
│   │   └── docs-sync.kiro.hook
│   └── settings/
│       └── mcp.json              # MCP server config
├── AGENTS.md                     # Agent directives
├── requirements.txt              # Python dependencies
├── requirements-dev.txt          # Development dependencies
├── pytest.ini                    # Pytest configuration
├── Makefile                      # Build automation
├── docker-compose.yml            # Container orchestration
├── docker-compose.localstack.yml # LocalStack setup
├── Dockerfile                    # Container build
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore patterns
└── README.md                     # Project documentation
```

## Source Code Organization

### Models (`src/models/`)

Data models using Pydantic for validation:

- Define all data structures as Pydantic models
- Include validation logic in model definitions
- Use type hints for all fields
- Document with docstrings

**Example**:
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class Story(BaseModel):
    """A technology news story with metadata."""
    id: str = Field(..., description="Unique identifier")
    title: str = Field(..., max_length=500)
    url: str = Field(..., description="Original article URL")
    summary: Optional[str] = None
    score: float = Field(default=0.0, ge=0)
    published_at: datetime
```

### Services (`src/services/`)

Business logic implementation:

- Each service handles a single domain concern
- Services receive dependencies through constructor
- Return Pydantic models, not dictionaries
- Include complete error handling

**Example**:
```python
class StoryCollector:
    """Collects and processes tech news stories."""

    def __init__(self, scrapers: List[BaseScraper], repository: StoryRepository):
        self.scrapers = scrapers
        self.repository = repository

    def collect_stories(self) -> List[Story]:
        """Collect stories from all configured sources."""
        # Implementation
```

### Repositories (`src/repositories/`)

Data access layer abstraction:

- Abstract database operations from business logic
- Implement retry logic for transient failures
- Use connection pooling
- Return domain models, not raw database results

### Scrapers (`src/scrapers/`)

Web scraping implementations:

- Inherit from `BaseScraper` abstract class
- Implement rate limiting
- Handle errors gracefully
- Normalize data to Story model format

### Web Application (`src/web/`)

Flask application setup:

- Use application factory pattern
- Organize routes by feature/domain
- Templates use Jinja2 inheritance
- Static assets in dedicated directory

## File Naming Conventions

### Python Files

| Type | Convention | Example |
|------|------------|---------|
| Modules | `snake_case.py` | `story_collector.py` |
| Test files | `test_*.py` | `test_story_collector.py` |
| Config | `config.py` | `config.py` |
| Init | `__init__.py` | `__init__.py` |

### Other Files

| Type | Convention | Example |
|------|------------|---------|
| CloudFormation | `kebab-case.yaml` | `vpc-infrastructure.yaml` |
| Documentation | `UPPERCASE.md` or `PascalCase.md` | `README.md`, `SetupGuide.md` |
| Environment | `.env.{environment}` | `.env.local`, `.env.prod` |
| Docker | Standard names | `Dockerfile`, `docker-compose.yml` |

## Import Conventions

### Standard Pattern

```python
# 1. Standard library imports
import os
import json
from typing import List, Optional, Dict
from datetime import datetime, timedelta

# 2. Third-party imports (blank line before)
import boto3
from flask import Flask, jsonify, request
from pydantic import BaseModel, Field
from sqlalchemy import create_engine

# 3. Local imports (blank line before)
from src.config import get_config, Config
from src.models.story import Story
from src.services.collector import StoryCollector
from src.repositories.story_repository import StoryRepository
```

### Absolute vs Relative Imports

**Prefer absolute imports** in most cases:
```python
# Good
from src.models.story import Story
from src.services.collector import StoryCollector

# Acceptable within package
from .models import Story
from ..repositories import StoryRepository
```

## Environment Separation

### Configuration Files

| Environment | Files | Purpose |
|-------------|-------|---------|
| Local | `.env.local` | Local development |
| Development | `.env.dev` | AWS dev environment |
| Production | `.env.prod` | AWS production |

### Resource Naming

Format: `{environment}-daily-briefing-{resource}`

Examples:
- `dev-daily-briefing-stories-table`
- `prod-daily-briefing-briefings-bucket`
- `dev-daily-briefing-apprunner-service`

## Anti-Patterns to Avoid

### Code Organization

- **No duplicate files**: Maintain single source of truth
- **No circular imports**: Use dependency injection
- **No deep nesting**: Maximum 3 levels in directory structure
- **No god classes**: Split large classes into focused components

### Configuration

- **No hardcoded values**: Use `src/config.py`
- **No secrets in code**: Use Secrets Manager or environment variables
- **No duplicate configs**: Single configuration source

### Data Access

- **No direct database access in services**: Use repository pattern
- **No raw SQL in business logic**: Abstract in repository
- **No ORM models in API responses**: Convert to Pydantic

### Testing

- **No test duplication**: Use fixtures and parameterization
- **No flaky tests**: Ensure deterministic behavior
- **No environment leakage**: Isolate test environments

## Documentation Standards

### Code Documentation

- **Docstrings**: Google-style for all public functions/classes
- **Type hints**: Required for all parameters and returns
- **Comments**: Explain *why*, not *what*

### Project Documentation

- **README.md**: Quick start, overview, setup
- **docs/**: Detailed guides and API documentation
- **AGENTS.md**: Agent-specific directives
- **Code comments**: Complex business logic only
