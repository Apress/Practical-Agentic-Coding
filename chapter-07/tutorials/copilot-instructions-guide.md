# copilot-instructions.md: Quick Reference

Where Copilot's instruction files live, their format, and how to check they work. For the latest details, see GitHub's own guide at [docs.github.com/copilot](https://docs.github.com/copilot).

Why governance files matter and how they fit the platform: Chapter 7, Section 7.3. The Section 7.6 lab uses them on LinkForge.

## Generate the file

In VS Code, run the `/init` chat command. It analyzes the project and generates or updates the workspace instructions. Check which file it wrote, then review and refine it.

The Copilot CLI's `/init` always writes `.github/copilot-instructions.md`.

## File Location

```text
your-repo/
├── .github/
│   └── copilot-instructions.md    # Repository instructions
├── src/
└── ...
```

**Important**: The file must be in the `.github/` directory to be recognized.

Copilot adds the file's contents to its context for every interaction in the repository.

## Path-Specific Instructions

For guidance that applies only to some files, add one or more `NAME.instructions.md` files under `.github/instructions/`. This is the Copilot counterpart of a glob-scoped Cursor rule. The `applyTo` frontmatter field names the files they cover:

```markdown
---
applyTo: "src/api/**/*.py,tests/api/**/*.py"
---

- Every endpoint validates input with a Pydantic schema
- Return 404 with {"detail": "..."} for missing resources
```

- Separate several patterns with commas.
- GitHub documents these files for Copilot Chat in VS Code, the Copilot cloud agent, and Copilot code review.
- To keep a file away from one agent, add `excludeAgent: "code-review"` (or `"cloud-agent"`) to the frontmatter.

## Basic Structure

```markdown
# GitHub Copilot Instructions for [Project Name]

## Project Overview
[Brief description of the project]

## Technology Stack
- [List of technologies and versions]

## Code Conventions
[Style guide and patterns]

## Architecture
[System design and patterns]

## Common Patterns
[Code examples showing expected patterns]

## Files to Reference
[Key files Copilot should consider]
```

## Minimal Example

```markdown
## Technology Stack

### Backend
- **Language**: Python 3.11
- **Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0 (async)
- **Database**: PostgreSQL 15
- **Cache**: Redis 7

## Key Files Reference

| File | Purpose |
|------|---------|
| `src/models/` | SQLAlchemy models - follow existing patterns |
| `src/schemas/` | Pydantic schemas - match model fields |
| `tests/conftest.py` | Test fixtures - reuse existing mocks |
```

For a full template, see [`../code-examples/copilot/copilot-instructions/`](../code-examples/copilot/copilot-instructions/).

## Organization-Level Instructions

For organization owners:

1. Go to Organization settings.
2. Open Copilot > Custom instructions.
3. Add organization-wide instructions.

GitHub documents organization instructions for Copilot Chat on GitHub.com, Copilot code review, and the Copilot cloud agent.

```markdown
# Organization Standards

All repositories must follow:
- Security: No secrets in code
- Compliance: GDPR data handling
- Style: Organization style guide
```

## Combining with Cursor Rules

If you use both Cursor and Copilot, put each kind of rule here:

| Rules | File |
|-------|------|
| Common rules | `AGENTS.md` (auto-detected by both tools) |
| Cursor-specific rules | `.cursor/rules/` |
| Copilot-specific rules | `copilot-instructions.md` |
| Reusable Copilot agent roles | `<name>.agent.md` profiles in `.github/agents/` |

```markdown
# AGENTS.md - Universal

## Project: MyApp
- Python 3.11, FastAPI
- Service layer pattern
- 80% test coverage

For detailed rules, see:
- Cursor: .cursor/rules/
- Copilot: .github/copilot-instructions.md
```

## Troubleshooting

### Instructions Not Applied

1. Check that the file is in the `.github/` directory.
2. Check the file name: `copilot-instructions.md`.
3. Update VS Code (Copilot ships with it). Check that the Copilot icon in the Status Bar shows you signed in.
4. Restart the IDE.

### Conflicting Suggestions

1. Make the instructions more specific.
2. Add explicit "do not" statements.
3. Give concrete examples.

### Too Much Context

1. Keep only the essential patterns.
2. Link to other docs instead of copying them.
3. Use a "Key Files" section for context.
