# Agent Directives

This file provides global directives for AI agents working on the Tech News Aggregator project. It is automatically included in all Kiro interactions regardless of inclusion mode.

## Project Context

You are working on a **Tech News Aggregator** application with a distinctive "Witty Tech Journalist" persona. The application curates technology stories from various sources and presents them with sharp, concise, and slightly cynical summaries that prioritize substance over hype.

## Core Principles

### 1. Spec-Driven Development

- Always reference the specs in `.kiro/specs/tech-news-aggregator/` before making changes
- Ensure code changes align with documented requirements
- Update specs when requirements evolve
- Maintain traceability between code and requirements

### 2. Code Quality Standards

- Maintain 70% minimum test coverage
- Use type hints for all function parameters and return types
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Document complex business logic with comments

### 3. Security First

- Never commit credentials or secrets to version control
- Use AWS Secrets Manager for all sensitive configuration
- Implement least privilege IAM policies
- Validate all user inputs
- Use parameterized queries for database operations

### 4. Persona Consistency

When generating summaries or content, maintain the "Witty Tech Journalist" persona:
- Sharp and concise tone
- Slightly cynical perspective
- Substance over hype
- Skeptical of marketing language
- Accessible explanations of technical concepts

## Technical Constraints

### Language & Framework

- Python 3.11+
- Flask for web application
- SQLAlchemy for database ORM
- Pydantic for data validation
- pytest for testing

### AWS Services

- Amazon Bedrock with a Claude Haiku-tier model for AI summaries and a Sonnet-tier fallback (model IDs from `BEDROCK_MODEL_ID` and `BEDROCK_FALLBACK_MODEL_ID`)
- Aurora PostgreSQL for data persistence
- AWS App Runner for container deployment
- S3 for file storage
- Secrets Manager for credentials

### Testing

- Use moto for AWS service mocking in unit tests
- Use LocalStack for integration testing
- Use Hypothesis for property-based testing
- Use Playwright for browser-based UI testing

## File Organization

Follow the structure defined in `.kiro/steering/structure.md`:

```text
src/
├── models/          # Pydantic data models
├── services/        # Business logic
├── repositories/    # Data access layer
├── scrapers/        # Web scraping modules
├── web/             # Flask application
└── config.py        # Centralized configuration
```

## Workflow Guidelines

### When Adding Features

1. Check if feature is covered in requirements spec
2. Update design spec if needed
3. Create or update task in tasks.md
4. Implement with tests
5. Update documentation

### When Fixing Bugs

1. Reproduce the issue
2. Write a failing test
3. Fix the bug
4. Verify test passes
5. Update relevant documentation

### When Refactoring

1. Ensure thorough test coverage exists
2. Make incremental changes
3. Run tests after each change
4. Update documentation if interfaces change

## Communication Style

When explaining code or decisions:
- Be concise and direct
- Provide rationale for technical choices
- Reference relevant documentation
- Suggest alternatives when appropriate
- Highlight potential risks or trade-offs

## Prohibited Actions

- Do not hardcode credentials or API keys
- Do not commit temporary or generated files
- Do not bypass security controls
- Do not skip test coverage requirements
- Do not modify production data directly
