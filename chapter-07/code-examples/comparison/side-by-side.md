# Cursor and GitHub Copilot: Same Tasks, Both Tools

This file shows the same tasks done in each tool, at the keyboard. It matches both tools' documentation as of November 7, 2026.

Why the two tools differ and when to pick each: Chapter 7, Section 7.4. The hybrid "Architect-Auditor" workflow: Chapter 7, Section 7.5.

> **Current tool behavior (as of November 7, 2026).** These differ from the printed book:
>
> - Current VS Code has no Copilot Edit Mode. For multi-file edits, use Agent Mode with attached files.
> - Cursor's agent searches the codebase on its own. There is no `@Codebase` symbol.
> - The book's "Copilot Async Agent" is the Copilot cloud agent. Dispatch it by assigning an issue.

## Where each feature lives

| Feature | Cursor | GitHub Copilot |
|---------|--------|----------------|
| **Multi-file Edits** | Agents Window (Composer model) | Agent Mode with attached files |
| **Background Execution** | Cloud agents from the Agents Window | Copilot cloud agent (issue assignment) |
| **Governance** | .cursor/rules + AGENTS.md | copilot-instructions.md + .github/agents/*.agent.md |
| **PR Review** | Bugbot (rules in `.cursor/BUGBOT.md`, also runnable on demand before pushing) | Native Copilot code review |
| **Issue Integration** | Via MCP | Native |

## Same Task, Different Approaches

### Task: Add a New API Endpoint

#### Using Cursor

1. Open the agent chat with Cmd+I. Shortcuts change between releases. See cursor.com/docs.
2. Enter this prompt:
```text
Create a new GET /api/v1/users/:id/orders endpoint that:
- Returns paginated orders for a user
- Includes order items
- Requires authentication
- Add tests
```
3. Review the file list and the diff preview.
4. Accept the changes.

#### Using Copilot

1. Open Copilot Chat and switch to Agent mode.
2. Attach the relevant files (routes.ts, orderService.ts).
3. Enter this prompt:
```text
Create a new GET /api/v1/users/:id/orders endpoint with
pagination, eager loading for items, and authentication.
Change only the attached files.
```
4. Review each file change.
5. Keep or undo the changes file by file.

### Task: Debug a Failing Test

#### Using Cursor

1. Open Chat.
2. Enter this prompt:
```text
The test in test_orders.py is failing.
Run the tests, analyze the error, and fix it.
```
3. Cursor runs the tests in the terminal.
4. It fixes the code and re-runs the tests.

#### Using Copilot

1. Switch to Agent Mode.
2. Enter this prompt:
```text
Run pytest test_orders.py, analyze failures, fix them,
and verify by re-running.
```
3. The agent runs the commands.
4. It creates the fix and verifies it.

### Task: Understand Legacy Code

#### Using Cursor

```text
Explain the data flow from the /checkout endpoint
through to the payment processor. Include a diagram.
```

The agent searches the codebase with its own tools before answering.

#### Using Copilot

```text
Explain how the checkout process works. Start from the
/checkout endpoint and trace through to payment processing.
```

Copilot uses workspace context and open files.

## Governance Files

### Cursor Project Rules

Project Rules live in `.cursor/rules/` as `.mdc` files with frontmatter. Cursor auto-detects `AGENTS.md` in the project root for high-level guidance. Cursor's documentation calls the old single-file `.cursorrules` legacy and slated for deprecation.

```markdown
# AGENTS.md (project root)

You are a senior engineer working on an e-commerce platform.

## Standards
- Use TypeScript strict mode
- Async/await for all I/O
- Service layer pattern

## Architecture
- Routes -> Services -> Repositories
- No business logic in controllers
```

**Scoped rule with frontmatter** (`.cursor/rules/api-routes.mdc`). The frontmatter must be the first thing in the file:
```markdown
---
description: "API route conventions"
globs: "src/routes/*.ts"
alwaysApply: false
---

# API Routes
- RESTful naming
- Proper status codes
- Schema validation (zod)
```

### Copilot copilot-instructions.md

````markdown
# .github/copilot-instructions.md

## Project: E-Commerce Platform

### Tech Stack
- TypeScript 5.0
- Express.js
- PostgreSQL + Prisma

### Patterns
Service layer pattern. Example:
```typescript
class OrderService {
  async createOrder(data: CreateOrderInput): Promise<Order> {
    // Business logic here
  }
}
```
````

## Pricing

Both vendors change pricing often. Check the current pages:

- **Cursor**: per-seat tiers with usage-based model allowances. See [cursor.com/pricing](https://cursor.com/pricing).
- **Copilot**: plans with an allowance of usage-based GitHub AI Credits. Heavier models consume credits faster. See [docs.github.com/copilot](https://docs.github.com/copilot).

## Migration Tips

### From Copilot to Cursor
1. Export VS Code settings.
2. Install Cursor.
3. Import settings.
4. Install extensions.
5. Create .cursor/rules (or reuse AGENTS.md) from copilot-instructions.

### Using Both
1. Keep both installed.
2. Use Cursor for development.
3. Use VS Code + Copilot for PR work.
4. Keep the governance files in sync.
