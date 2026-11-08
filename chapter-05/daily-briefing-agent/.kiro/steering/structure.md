# Project Structure & Organization

## Directory Layout

```text
tech-news-aggregator/
├── src/                          # Source code (main application)
│   ├── models/                   # Data models and schemas
│   ├── services/                 # Business logic services
│   ├── repositories/             # Data access layer
│   ├── scrapers/                 # Web scraping modules
│   ├── lambda_handlers/          # AWS Lambda function handlers
│   ├── web/                      # Flask web application
│   ├── config.py                 # Centralized configuration management
│   └── __init__.py
├── tests/                        # Test suite
│   ├── test_*.py                 # Test files following pytest conventions
│   ├── conftest.py               # Shared test fixtures
│   ├── browser_fixtures.py       # Browser testing fixtures
│   └── __init__.py
├── infrastructure/               # Infrastructure as Code
│   ├── cloudformation/           # CloudFormation templates
│   ├── parameters/               # Environment-specific parameters
│   ├── deploy.py                 # Deployment automation
│   └── README.md                 # Infrastructure documentation
├── scripts/                      # Utility and automation scripts
│   ├── test_runner.py            # Custom test execution
│   ├── setup_localstack.py       # LocalStack resource setup
│   └── check_config.py           # Configuration validation
├── docs/                         # Project documentation
├── .kiro/                        # Kiro IDE configuration
│   ├── specs/                    # Project specifications
│   └── steering/                 # AI assistant guidance
├── requirements.txt              # Python dependencies
├── setup.py                      # Package configuration
├── pytest.ini                   # Test configuration
├── Makefile                      # Build automation
├── docker-compose.yml            # Container orchestration
└── README.md                     # Project overview
```

## Source Code Organization

### Core Application (`src/`)

#### Models (`src/models/`)
- Data models using Pydantic for validation
- Database schema definitions
- API request/response models
- Domain entities (Story, Source, Summary, etc.)

#### Services (`src/services/`)
- Business logic implementation
- Story collection and processing
- Summary generation using Bedrock
- Daily briefing creation
- Quality scoring and ranking

#### Repositories (`src/repositories/`)
- Data access layer abstraction
- DynamoDB operations
- S3 file operations
- Database connection management
- Query optimization

#### Scrapers (`src/scrapers/`)
- Web scraping implementations
- Source-specific parsers (Hacker News, etc.)
- Content extraction and normalization
- Rate limiting and error handling

#### Lambda Handlers (`src/lambda_handlers/`)
- AWS Lambda function entry points
- Event processing logic
- API Gateway integration
- Scheduled task handlers

#### Web Application (`src/web/`)
- Flask application setup
- HTTP route definitions
- Template rendering
- Static asset management
- API endpoints

### Configuration Management

#### Central Configuration (`src/config.py`)
- Environment-specific settings
- AWS service configuration
- LocalStack integration
- Validation and error handling
- Precedence: system env > .env files > defaults

## Testing Organization

### Test Structure (`tests/`)
- **Naming Convention**: `test_*.py` files
- **Test Classes**: `Test*` classes for grouping related tests
- **Test Functions**: `test_*` functions for individual test cases

### Test Categories
- **Unit Tests**: Fast, isolated tests with mocked dependencies
- **Integration Tests**: LocalStack-based AWS service testing
- **Property Tests**: Hypothesis-based property testing
- **Browser Tests**: Playwright-based UI testing
- **Hybrid Tests**: Mixed LocalStack + moto mocking

### Fixtures (`conftest.py`, `browser_fixtures.py`)
- Shared test setup and teardown
- Database and service mocking
- Browser automation setup
- Environment configuration

## Infrastructure Organization

### CloudFormation Templates (`infrastructure/cloudformation/`)
- **main-infrastructure.yaml**: Core AWS resources
- **lambda-deployment.yaml**: Lambda packaging and layers
- **briefing-schedule.yaml**: EventBridge scheduling

### Deployment Automation (`infrastructure/deploy.py`)
- Stack deployment orchestration
- Parameter management
- Template validation
- Rollback capabilities

### Environment Parameters (`infrastructure/parameters/`)
- **dev.json**: Development environment settings
- **prod.json**: Production environment settings
- Environment-specific resource configurations

## File Naming Conventions

### Python Files
- **Snake case**: `story_collector.py`, `summary_generator.py`
- **Test files**: `test_story_collector.py`, `test_summary_generator.py`
- **Class names**: PascalCase (`StoryCollector`, `SummaryGenerator`)
- **Function names**: Snake case (`collect_stories`, `generate_summary`)

### Configuration Files
- **Environment files**: `.env.local`, `.env.dev`, `.env.prod`
- **Docker files**: `docker-compose.yml`, `docker-compose.localstack.yml`
- **AWS files**: CloudFormation templates use kebab-case

### Documentation
- **Markdown files**: ALL_CAPS for summaries, PascalCase for guides
- **README files**: Always `README.md` in relevant directories

## Import Conventions

### Absolute Imports
```python
from src.models.story import Story
from src.services.story_collector import StoryCollector
from src.repositories.dynamodb_repository import DynamoDBRepository
```

### Relative Imports (within modules)
```python
from .models import Story
from ..repositories import DynamoDBRepository
```

### Third-party vs Local
```python
# Third-party imports first
import boto3
from flask import Flask
from pydantic import BaseModel

# Local imports after blank line
from src.config import get_config
from src.models.story import Story
```

## Environment Separation

### Development Environments
- **local**: LocalStack with mocked AWS services
- **dev**: AWS development environment
- **prod**: AWS production environment

### Configuration Precedence
1. System environment variables (highest priority)
2. Environment-specific .env files
3. Default values in Config class (lowest priority)

### Resource Naming
- **Format**: `{environment}-{project}-{resource}`
- **Example**: `dev-tech-news-aggregator-stories-table`

## Documentation Standards

### Code Documentation
- **Docstrings**: Google-style docstrings for all public functions
- **Type hints**: Required for all function parameters and returns
- **Comments**: Explain complex business logic, not obvious code

### Project Documentation
- **README.md**: Project overview and quick start
- **docs/**: Detailed guides and specifications
- **Infrastructure README**: Deployment and architecture details

## Anti-Patterns to Avoid

### Code Organization
- **No duplicate files**: Maintain single source of truth
- **No circular imports**: Use dependency injection patterns
- **No deep nesting**: Keep directory structure flat where possible

### Configuration
- **No hardcoded values**: Use configuration management
- **No duplicate configs**: Centralize in `src/config.py`
- **No secrets in code**: Use AWS Secrets Manager

### Testing
- **No test duplication**: Use fixtures and parameterization
- **No environment leakage**: Isolate test environments
- **No flaky tests**: Ensure deterministic test behavior