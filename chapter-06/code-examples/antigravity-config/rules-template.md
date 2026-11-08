---
trigger: always_on
---
# Workspace Rules Template

1. Copy this file to `.agents/rules/project-rules.md`.
2. Replace every bracketed placeholder with your own choices.
3. Keep the frontmatter block at the top. Antigravity skips a rules file without a valid `trigger`.

Rules in `.agents/rules/` travel with the repository, so your teammates and their agents get the same constraints. Keep the rules short. State prohibitions explicitly, for example "DO NOT use raw CSS", not "prefer Tailwind." For a filled-in example, see `../../hands-on-lab/moneymind/.agents/rules/project-rules.md`.

---

# [PROJECT_NAME] Workspace Rules

These rules are automatically enforced for all agent-generated code.

## Language & Framework

### Required
- ALL code MUST be written in [LANGUAGE] with strict mode
- Use [FRAMEWORK] version [VERSION] or higher
- Prefer [PATTERN] for [USE_CASE]

### Forbidden
- DO NOT use [DEPRECATED_PATTERN]
- DO NOT import from [RESTRICTED_PACKAGE]

## Code Style

### Naming Conventions
- Use camelCase for functions and variables
- Use PascalCase for classes and components
- Use SCREAMING_SNAKE_CASE for constants
- Prefix interfaces with I (optional)

### File Organization
- Place components in src/components/
- Place utilities in src/lib/
- Place API routes in src/app/api/
- Place tests adjacent to source files

### Import Order
1. External dependencies
2. Internal modules (absolute paths)
3. Relative imports
4. Types/interfaces
5. Styles

## Testing

### Requirements
- ALL new code MUST include tests
- Minimum [PERCENTAGE]% code coverage
- Use [TEST_FRAMEWORK] for unit tests
- Use [E2E_FRAMEWORK] for integration tests

### Test Structure
- One test file per component/module
- Use descriptive test names
- Group tests with describe blocks
- Include edge cases and error scenarios

## Security

### CRITICAL - Never Do
- NEVER hardcode secrets, API keys, or passwords
- NEVER commit .env files
- NEVER expose internal errors to users
- NEVER trust user input without validation

### Required Practices
- All sensitive values from environment variables
- Input validation with [VALIDATION_LIBRARY]
- Proper error handling without leaking internals
- Use parameterized queries for database access

## Documentation

### Required Documentation
- JSDoc for all public functions
- README for new modules
- CHANGELOG entries for features
- Architecture decision records for significant changes

### Comment Guidelines
- Explain WHY, not WHAT
- Update comments when code changes
- Remove TODO comments before merging

## Performance

### Best Practices
- Lazy load components when appropriate
- Memoize expensive computations
- Avoid N+1 query patterns
- Profile before optimizing

### Forbidden Patterns
- Synchronous file operations in requests
- Blocking operations in render path
- Unbounded loops over user data

## Git & Version Control

### Commit Messages
- Use conventional commits format
- Reference issue numbers
- Keep subject under 50 characters

### Branch Naming
- feature/[issue-number]-description
- bugfix/[issue-number]-description
- hotfix/critical-issue-description

## Agent-Specific Rules

### Artifacts
- Generate Implementation Plan for complex tasks
- Create Walkthrough after multi-file changes
- Include screenshots for UI changes

### Review Requirements
- Complex logic requires human review
- Security changes require explicit approval
- Database changes require migration plan

---

## Project-Specific Rules

Add your project-specific rules here:

### [DOMAIN] Rules
- [SPECIFIC_RULE_1]
- [SPECIFIC_RULE_2]

### API Contract
- Follow schema in .context/api_reference.md
- Use [PREFERRED_FIELD] instead of [DEPRECATED_FIELD]

---

*Last updated: [DATE]*
*Version: 1.0*
