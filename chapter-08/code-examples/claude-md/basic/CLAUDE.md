# CLAUDE.md - Basic Project Template

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

[Brief description of the project, its purpose, and key stakeholders]

Example:
> TaskManager is a web application for personal task management. Built with
> React and Node.js, it helps individuals organize their daily tasks with
> categories, priorities, and due dates.

## Development Commands

### Running the Application

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### Testing

```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- path/to/test.ts
```

## Architecture

### Project Structure

```text
src/
├── components/     # React components
├── services/       # Business logic
├── utils/          # Utility functions
├── types/          # TypeScript definitions
└── tests/          # Test files
```

### Key Patterns

- Components follow the [pattern name] pattern
- State management using [library/approach]
- API calls handled through [service layer approach]

## Code Standards

### Language and Framework

- TypeScript with strict mode enabled
- React 18+ with functional components
- Node.js 20+ for backend

### Style Guidelines

- Use ESLint and Prettier for formatting
- Follow [style guide name] conventions
- Maximum line length: 100 characters

### Naming Conventions

- Components: PascalCase (e.g., `TaskList.tsx`)
- Functions: camelCase (e.g., `getUserTasks`)
- Constants: UPPER_SNAKE_CASE (e.g., `MAX_TASKS`)
- Files: kebab-case for non-components (e.g., `api-client.ts`)

## Testing Standards

- All new features must include tests
- Aim for 80% code coverage
- Use descriptive test names
- Mock external dependencies

## Dependencies

### Adding Dependencies

Before adding a new dependency:
1. Check if existing dependencies can solve the problem
2. Verify the package is actively maintained
3. Review security advisories
4. Consider bundle size impact

## Common Tasks

### Creating a New Component

1. Create component file in `src/components/`
2. Add corresponding test file
3. Export from index file if needed

### Adding an API Endpoint

1. Define types in `src/types/`
2. Implement in `src/services/`
3. Add error handling
4. Write integration tests

## Prohibited Actions

- Do not commit secrets or API keys
- Do not modify production configuration without review
- Do not skip tests for new features
- Do not use `any` type without justification
