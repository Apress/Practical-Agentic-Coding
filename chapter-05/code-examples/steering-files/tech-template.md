# Technology Stack Template

Use this template to create your own `tech.md` steering file. Place the completed file in `.kiro/steering/tech.md`.

---

~~~markdown
---
inclusion: always
---

# [Project Name] Development Guidelines

## Architecture Patterns (MANDATORY)

### Code Organization
- **[Pattern Name]**: [Description of the pattern and why it's used]
- **[Pattern Name]**: [Description of the pattern and why it's used]
- **[Pattern Name]**: [Description of the pattern and why it's used]

### Error Handling Standards
- [Standard 1]: [Description]
- [Standard 2]: [Description]
- [Standard 3]: [Description]

## Technology Stack Rules

### [Primary Language] ([Version]+) Requirements
- **[Framework]**: [Purpose and usage context]
- **[Library]**: [Purpose and usage context]
- **[Tool]**: [Purpose and usage context]

### [Cloud Provider] Services Usage
- **[Service 1]**: [Purpose and configuration notes]
- **[Service 2]**: [Purpose and configuration notes]
- **[Service 3]**: [Purpose and configuration notes]

## Code Style (NON-NEGOTIABLE)

### Naming Conventions
- **Files**: [Convention with example]
- **Classes**: [Convention with example]
- **Functions/Variables**: [Convention with example]
- **Constants**: [Convention with example]

### Import Order
```[language]
# 1. Standard library
[example imports]

# 2. Third-party (blank line before)
[example imports]

# 3. Local imports (blank line before)
[example imports]
```

## Testing Strategy (REQUIRED)

### Test Categories & Markers
- `[marker]`: [Description of test type and when to use]
- `[marker]`: [Description of test type and when to use]
- `[marker]`: [Description of test type and when to use]

### Coverage Requirements
- [Requirement 1]
- [Requirement 2]

## Environment Configuration

### Environment Precedence (STRICT ORDER)
1. [Highest priority source]
2. [Medium priority source]
3. [Lowest priority source]

### Local Development Setup
- [Setup instruction 1]
- [Setup instruction 2]

## Development Commands

### Essential Workflows
```bash
# [Category 1]
[command]  # Description

# [Category 2]
[command]  # Description
```

## [Technology]-Specific Patterns

### [Component/Service] Best Practices
- [Best practice 1]
- [Best practice 2]
- [Best practice 3]

## Performance & Cost Optimization

### [Area 1]
- [Guideline]
- [Guideline]

### [Area 2]
- [Guideline]
- [Guideline]
~~~

---

## Example: Python/AWS Tech Stack

~~~markdown
---
inclusion: always
---

# Tech News Aggregator Development Guidelines

## Architecture Patterns (MANDATORY)

### Code Organization
- **Repository Pattern**: ALWAYS separate data access (`src/repositories/`)
  from business logic (`src/services/`)
- **Pydantic Models**: Use for ALL data structures in `src/models/` - no
  exceptions
- **Type Hints**: Required for all function parameters and return types
- **Central Config**: Use `src/config.py` Config class for ALL settings -
  never hardcode values

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
- **pytest**: Testing with markers (`@pytest.mark.unit`,
  `@pytest.mark.integration`)

### AWS Services Usage
- **Bedrock**: a higher-reasoning Claude model for complex summaries, a fast
  Claude model for simple tasks. Model IDs live in configuration, not in code
- **Aurora PostgreSQL**: Primary database with proper indexing and
  foreign keys
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
- Use a higher-reasoning model for complex summaries (higher cost, better quality)
  and a fast model for simple tasks (lower cost, faster)
- Read model IDs from configuration, never from a literal in application code:
  the Bedrock model catalog changes and availability varies by region
- Always implement retry logic and fallback strategies
- Handle rate limiting gracefully

### Database Patterns
- Use normalized relational design with proper foreign keys
- Use SQL joins for complex queries
- Use bulk operations for performance
- Index frequently queried columns

## Infrastructure as Code

### CloudFormation Rules
- Templates in `infrastructure/cloudformation/`
- Environment parameters in `infrastructure/parameters/`
- Always validate before deployment
- Use consistent resource naming: `{env}-{project}-{resource}`
~~~

---

## Tips for Writing tech.md

1. **Be Prescriptive**: Use words like "ALWAYS", "NEVER", "REQUIRED"
2. **Provide Examples**: Code snippets make guidelines concrete
3. **Explain Why**: Help developers understand the rationale
4. **Stay Current**: Update when stack or patterns change
5. **Be Consistent**: Align with actual project practices
