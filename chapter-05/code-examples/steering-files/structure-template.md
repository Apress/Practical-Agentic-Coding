# Project Structure Template

Use this template to create your own `structure.md` steering file. Place the completed file in `.kiro/steering/structure.md`.

---

~~~markdown
# Project Structure & Organization

## Directory Layout

```text
[project-name]/
├── src/                          # Source code (main application)
│   ├── [module]/                 # [Description]
│   ├── [module]/                 # [Description]
│   ├── [module]/                 # [Description]
│   ├── config.py                 # Centralized configuration
│   └── __init__.py
├── tests/                        # Test suite
│   ├── test_*.py                 # Test files
│   ├── conftest.py               # Shared fixtures
│   └── __init__.py
├── infrastructure/               # Infrastructure as Code
│   ├── [iac-tool]/               # IaC templates
│   └── README.md                 # Infrastructure docs
├── scripts/                      # Utility scripts
├── docs/                         # Documentation
├── .[tool]/                      # Tool configuration
├── requirements.txt              # Dependencies
├── setup.py                      # Package configuration
├── [config-file]                 # Tool configurations
└── README.md                     # Project overview
```

## Source Code Organization

### [Module Name] (`src/[module]/`)
- [Description of contents]
- [Types of files found here]
- [Responsibilities of this module]

### [Module Name] (`src/[module]/`)
- [Description of contents]
- [Types of files found here]
- [Responsibilities of this module]

## Testing Organization

### Test Structure (`tests/`)
- **Naming Convention**: `test_*.py` files
- **Test Classes**: `Test*` classes for grouping
- **Test Functions**: `test_*` functions for individual tests

### Test Categories
- **[Category]**: [Description and purpose]
- **[Category]**: [Description and purpose]

## File Naming Conventions

### [Language] Files
- **[Type]**: [Convention with example]
- **[Type]**: [Convention with example]

### Configuration Files
- **[Type]**: [Convention with example]

## Import Conventions

### Absolute Imports
```[language]
[example imports]
```

### Relative Imports (within modules)
```[language]
[example imports]
```

## Environment Separation

### Environments
- **[env]**: [Purpose]
- **[env]**: [Purpose]

### Resource Naming
- **Format**: `{environment}-{project}-{resource}`
- **Example**: `[example resource name]`

## Documentation Standards

### Code Documentation
- [Standard 1]
- [Standard 2]

### Project Documentation
- [Where docs live]
- [What goes in each location]

## Anti-Patterns to Avoid

### Code Organization
- **[Anti-pattern]**: [Why it's bad]
- **[Anti-pattern]**: [Why it's bad]

### Configuration
- **[Anti-pattern]**: [Why it's bad]
- **[Anti-pattern]**: [Why it's bad]

### Testing
- **[Anti-pattern]**: [Why it's bad]
- **[Anti-pattern]**: [Why it's bad]
~~~

---

## Example: Python Web Application Structure

~~~markdown
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
├── pytest.ini                    # Test configuration
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

## File Naming Conventions

### Python Files
- **Snake case**: `story_collector.py`, `summary_generator.py`
- **Test files**: `test_story_collector.py`
- **Class names**: PascalCase (`StoryCollector`)
- **Function names**: Snake case (`collect_stories`)

### Configuration Files
- **Environment files**: `.env.local`, `.env.dev`, `.env.prod`
- **Docker files**: `docker-compose.yml`
- **AWS files**: CloudFormation templates use kebab-case

## Import Conventions

### Absolute Imports
```python
from src.models.story import Story
from src.services.story_collector import StoryCollector
from src.repositories.dynamodb_repository import DynamoDBRepository
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

### Environments
- **local**: LocalStack with mocked AWS services
- **dev**: AWS development environment
- **prod**: AWS production environment

### Resource Naming
- **Format**: `{environment}-{project}-{resource}`
- **Example**: `dev-tech-news-aggregator-stories-table`

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
~~~

---

## Tips for Writing structure.md

1. **Be Visual**: ASCII directory trees help comprehension
2. **Explain Purposes**: Don't just list - explain why things go where
3. **Include Examples**: Show real file names and paths
4. **Document Patterns**: Make conventions explicit
5. **List Anti-Patterns**: Help prevent common mistakes
