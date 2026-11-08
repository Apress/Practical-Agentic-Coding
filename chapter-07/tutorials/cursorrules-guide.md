# Cursor Project Rules: Quick Reference

Where Cursor rules live, the `.mdc` file format, and how to check that a rule applies. For the latest details, see Cursor's own docs at [cursor.com/docs](https://cursor.com/docs).

How rules work as governance, when to use each rule type, and why: Chapter 7, Section 7.2.

**Project Rules** live in `.cursor/rules/` inside your repository. Each rule is a markdown file with the `.mdc` extension. It must open with YAML frontmatter. The rules system skips any plain `.md` file in that directory.

For high-level guidance only, use an **`AGENTS.md`** file in the project root. It needs no metadata. Copilot in VS Code auto-detects it too.

### Migrating from `.cursorrules`

> **Legacy format.** The single-file `.cursorrules` in the project root was the original convention. Cursor's help center says it "is legacy and will be deprecated." Move any project that still has one.

Follow Cursor's own steps:

1. Open the command palette (Cmd+Shift+P on Mac, Ctrl+Shift+P on Windows and Linux) and run **New Cursor Rule**.
2. Copy the content of `.cursorrules` into the new rule file.
3. Set the rule type to **Always Apply**. This matches how the old file behaved.
4. Delete `.cursorrules` from the project root. Otherwise the old and new copies both load.

If the content is high-level guidance with no file targeting, an `AGENTS.md` in the project root also works.

Rules apply to the agent (chat). They do not apply to Tab completions or to Bugbot pull request reviews. Bugbot reads `.cursor/BUGBOT.md` instead.

## Rule Hierarchy

```text
Team Rules (Dashboard)                 → Organization standards (Team and Enterprise plans)
    ↓
Project Rules (.cursor/rules/*.mdc)    → Repository-specific patterns
  + AGENTS.md (root or subdirectory)   → High-level project guidance
    ↓
User Rules (Customize → Rules)         → Personal preferences
```

Cursor merges every rule that applies. When two rules conflict, the earlier source in this order wins.

## File Locations

| Location | Scope | Holds |
|----------|-------|-------|
| Customize → Rules | Global (your account) | Personal preferences |
| Cursor Dashboard | Organization | Org-wide team rules; can be marked enforced |
| `.cursor/rules/*.mdc` | Project folder | Targeted, version-controlled rules |
| `AGENTS.md` | Project root | Simple project rules (also read by Copilot) |

A rule can ship supporting files next to it:

```text
.cursor/rules/
  service-pattern.mdc    # Frontmatter + instruction logic
  templates/
    template.ts          # A code template referenced by the rule
```

## Simple Text Format (AGENTS.md)

When you do not need targeting metadata, put plain markdown in `AGENTS.md`:

```markdown
You are an expert Python developer working on a FastAPI project.

## Code Standards
- Use async/await for all I/O operations
- Type hints on all functions
- Pydantic v2 for validation

## Architecture
- Service layer for business logic
- Repository pattern for data access
- Dependency injection via FastAPI

## Naming
- Routes: /api/v1/{resource}
- Services: *Service
- Models: *Model (SQLAlchemy), *Schema (Pydantic)
```

## The `.mdc` Format

A rule opens with a YAML frontmatter block. Its fields decide *when* the rule enters context:

```markdown
---
description: "When this rule applies (for AI to decide)"
globs: "src/**/*.py,tests/**/*.py"
alwaysApply: false
---

# Rule Title

Rule content goes here...
```

### Frontmatter Fields

| Field | Type | Description |
|-------|------|-------------|
| `description` | string | Helps AI decide when to use rule |
| `globs` | string | File patterns that trigger the rule; separate several with commas |
| `alwaysApply` | boolean | Include in every prompt; when `true`, Cursor ignores `globs` and `description` |

When no glob matches, the agent reads `description` to decide whether to pull the rule into context. Write it as a trigger condition.

### Book example (Chapter 7, Section 7.2)

`.cursor/rules/react-standards.mdc`. Chat and Agent follow it in every request without being told. The frontmatter must be the first thing in the file.

```markdown
---
description: "React component standards"
alwaysApply: true
---
All new React components must be functional components using hooks.
Data fetching must go through `useApiClient()`; do not use `fetch` directly.
```

### Minimal Example

`.cursor/rules/api-routes.mdc`. The frontmatter must be the first thing in the file.

```markdown
---
description: "Conventions for creating new API routes"
globs: "src/routes/*.py,src/main.py"
alwaysApply: false
---

# API Route Standards

## Error Handling
- Use HTTPException with specific status codes
- Include error_code for client handling
- Log errors with context

## Authentication
- Protected routes use `Depends(get_current_user)`
- Check permissions with `Depends(require_role("admin"))`
```

More templates to copy (basic, Python, TypeScript, enterprise) are in [`../code-examples/cursor/project-rules/`](../code-examples/cursor/project-rules/).

## Verify Rules Are Applied

1. Open Cursor's agent chat.
2. Ask: "Show me the rules you're following".
3. Request a code generation.
4. Check that the output follows your rules.

If the agent ignores a rule:

1. Make the rule more explicit.
2. Add examples that show the rule.
3. Use `alwaysApply: true` for critical rules.

## Version Control Rules

```bash
# Add to git
git add AGENTS.md
git add .cursor/rules/
git commit -m "Add Cursor rules for project standards"
```

## Enforced Team Rules

Team rules are available on Cursor's Team and Enterprise plans. Manage them in the Cursor Dashboard. They apply across the organization. When an admin marks a rule **"Enforce this rule"**, developers cannot switch it off.

## Troubleshooting

### Rule Not Applied

1. Check that the file has the `.mdc` extension. Cursor ignores plain `.md`.
2. Check that the file path matches the glob.
3. Check the frontmatter syntax.
4. Check the `alwaysApply` setting.
5. Restart Cursor.

### Conflicting Rules

1. Cursor applies team rules first, then project rules, then user rules. On a conflict the earlier source wins.
2. Within one level, rewrite overlapping rules so they no longer disagree.
3. State the precedence in the rule text itself.

### Performance Issues

1. Limit `alwaysApply` rules.
2. Use specific globs.
3. Keep rules concise.
