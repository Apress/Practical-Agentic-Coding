# CLAUDE.md - Team Project Template

This file establishes shared conventions for Claude Code across a development team, balancing governance with flexibility.

## Project Overview

**Project**: CollaborativeEditor
**Team**: Platform Engineering (8 developers)
**Stack**: TypeScript, Next.js, PostgreSQL, Redis
**Repository**: monorepo with multiple packages

Real-time collaborative document editor supporting multiple users editing simultaneously with conflict resolution and version history.

## Development Commands

### Setup

```bash
# Clone and install
git clone <repo>
pnpm install

# Set up local environment
cp .env.example .env.local
pnpm db:setup
```

### Development

```bash
# Start all services
pnpm dev

# Start specific package
pnpm --filter @editor/api dev
pnpm --filter @editor/web dev

# Run database migrations
pnpm db:migrate
```

### Testing

```bash
# Run all tests
pnpm test

# Run tests for specific package
pnpm --filter @editor/api test

# Run e2e tests
pnpm test:e2e

# Type check
pnpm typecheck
```

### Building

```bash
# Build all packages
pnpm build

# Build specific package
pnpm --filter @editor/web build
```

## Architecture

### Monorepo Structure

```text
packages/
├── api/              # Backend API (Next.js API routes)
├── web/              # Frontend application
├── shared/           # Shared types and utilities
├── editor-core/      # CRDT-based editor engine
├── realtime/         # WebSocket server
└── database/         # Database schemas and migrations
```

### Key Design Decisions

1. **CRDT for conflict resolution** - All collaborative state uses CRDTs
2. **Event sourcing** - Document changes stored as events
3. **Optimistic updates** - UI updates immediately, syncs in background
4. **Feature flags** - New features behind flags for gradual rollout

## Code Standards

### TypeScript Configuration

- Strict mode enabled across all packages
- No implicit any
- Strict null checks
- ES2022 target

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Components | PascalCase | `DocumentHeader.tsx` |
| Hooks | camelCase with use prefix | `useDocument.ts` |
| Utils | camelCase | `formatDate.ts` |
| Types | PascalCase | `DocumentState.ts` |
| Constants | UPPER_SNAKE | `MAX_DOCUMENT_SIZE` |

### File Organization

```typescript
// Component file structure
// 1. Imports (external, then internal)
// 2. Types
// 3. Constants
// 4. Component
// 5. Helpers (if any)
// 6. Export

import { useState } from 'react';
import { DocumentState } from '@editor/shared';

interface Props {
  documentId: string;
}

const MAX_TITLE_LENGTH = 100;

export function DocumentHeader({ documentId }: Props) {
  // ...
}
```

### Error Handling

```typescript
// Use Result type for operations that can fail
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E };

// Domain-specific errors
class DocumentNotFoundError extends Error {
  constructor(documentId: string) {
    super(`Document not found: ${documentId}`);
    this.name = 'DocumentNotFoundError';
  }
}
```

## Team Conventions

### Git Workflow

1. Create feature branch from `main`
2. Branch naming: `feature/ABC-123-description` or `fix/ABC-123-description`
3. Commits follow conventional commits
4. PR requires 1 approval minimum
5. Squash merge to main

### Commit Messages

```text
feat(editor): add real-time cursor tracking
fix(api): handle race condition in document save
docs(readme): update setup instructions
test(editor-core): add CRDT merge tests
chore(deps): update dependencies
```

### Code Review Guidelines

**Authors should:**
- Keep PRs under 400 lines when possible
- Write clear PR descriptions
- Add screenshots for UI changes
- Respond to feedback within 24 hours

**Reviewers should:**
- Review within 24 hours
- Be constructive and specific
- Approve or request changes (no "comment only")
- Test locally for significant changes

## Testing Standards

### Unit Tests

- All utility functions must have tests
- Components should have snapshot tests
- Aim for 80% coverage on new code

### Integration Tests

- API endpoints must have integration tests
- Database operations must be tested against real database
- Use test containers for isolation

### E2E Tests

- Critical user flows must have e2e tests
- Run in CI before merge to main
- Use Playwright for browser testing

## Security Guidelines

### Authentication

- Use NextAuth.js for authentication
- Session tokens stored in httpOnly cookies
- Implement CSRF protection

### Data Access

- Always check document ownership before operations
- Use Prisma for type-safe database queries
- Never expose internal IDs to clients (use UUIDs)

### Secrets Management

- Use environment variables for all secrets
- Different values for dev/staging/prod
- Rotate API keys quarterly

## Performance Guidelines

### Frontend

- Use React.memo for expensive components
- Lazy load routes and heavy components
- Images should use next/image
- Monitor Core Web Vitals

### Backend

- Cache frequently accessed data in Redis
- Use database indexes for common queries
- Implement pagination for list endpoints
- Set appropriate timeouts

### Real-time

- Batch WebSocket messages (50ms window)
- Implement exponential backoff for reconnection
- Monitor connection count and latency

## Common Tasks

### Adding a New Feature

1. Create feature flag in `packages/shared/flags.ts`
2. Implement behind flag
3. Write tests
4. Update documentation
5. Enable flag gradually (10% -> 50% -> 100%)

### Adding a New API Endpoint

1. Define types in `packages/shared/types/`
2. Add route in `packages/api/routes/`
3. Add validation with Zod
4. Write integration tests
5. Update OpenAPI spec

### Database Changes

1. Create migration in `packages/database/migrations/`
2. Test migration up and down
3. Update Prisma schema
4. Generate types: `pnpm db:generate`
5. PR requires DBA review for production tables

## Prohibited Actions

### Code Quality

- No `any` types without explicit comment justifying
- No console.log in production code
- No disabled eslint rules without justification
- No skipped tests without issue link

### Security

- No hardcoded credentials
- No logging of sensitive data
- No disabled security headers
- No direct database access from frontend

### Operations

- No force pushes to main
- No merging without CI passing
- No deploying on Fridays (except hotfixes)
- No changes to shared packages without team discussion

## Team Contacts

| Role | Person | Slack |
|------|--------|-------|
| Tech Lead | Alice | @alice |
| Backend Lead | Bob | @bob |
| Frontend Lead | Carol | @carol |
| DevOps | Dave | @dave |

## Resources

- [Team Wiki](https://wiki.company.com/platform-engineering)
- [API Documentation](https://api-docs.company.com)
- [Design System](https://design.company.com)
- [Runbooks](https://runbooks.company.com)
