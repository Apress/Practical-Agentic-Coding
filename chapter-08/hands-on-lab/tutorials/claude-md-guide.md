# CLAUDE.md: quick reference

Use this file while you write a CLAUDE.md. It covers where the files go, the file layout, rule-file syntax, and how to check that Claude follows your rules.

What a CLAUDE.md is for, how the memory levels combine, and what makes a good one: Chapter 8, Section 8.3.

## Where the Files Go

Claude Code reads these files automatically at session start. Table 8.3 in the book lists the levels. The locations are:

- **Project memory**: `./CLAUDE.md` (or `./.claude/CLAUDE.md`), checked into git
- **Project rules**: `./.claude/rules/*.md`, optionally scoped with `paths:` frontmatter (see Modular Rules below)
- **User memory**: `~/.claude/CLAUDE.md`
- **Local memory**: `./CLAUDE.local.md` at the project root, kept out of version control
- **Managed policy**: `/Library/Application Support/ClaudeCode/CLAUDE.md` (macOS), `/etc/claude-code/CLAUDE.md` (Linux and WSL), `C:\Program Files\ClaudeCode\CLAUDE.md` (Windows)

A CLAUDE.md can pull in other files with `@path/to/file` imports. Imports can nest up to four hops deep.

In a session, run `/memory` to:

- Open the loaded CLAUDE.md files for editing
- List, edit, or switch off auto memory

Review the auto memory notes like any other input. Claude follows a note it wrote itself as a rule.

## CLAUDE.md Structure

### Recommended Sections

```markdown
# Project: [Name]

## Overview
[Project description, purpose, key metrics]

## Development Commands
[How to build, test, run]

## Architecture
[System design, patterns, key decisions]

## Code Standards
[Language, style, conventions]

## Security Requirements
[Non-negotiable security rules]

## Testing Standards
[Coverage, patterns, requirements]

## Prohibited Actions
[What NOT to do]
```

### Example section

Each section holds short, specific rules. A minimal example:

```markdown
## Prohibited Actions

### Never:
1. Store credit card numbers (use tokens)
2. Use float for money (use Decimal)
3. Log sensitive data (mask PII)
4. Commit secrets to git
5. Deploy without CI/CD pipeline
6. Bypass rate limiting
7. Disable audit logging
```

## Modular Rules

To split rules into separate files, put them in `.claude/rules/`:

### Structure

```text
.claude/
├── rules/
│   ├── security.md
│   ├── api-design.md
│   ├── database.md
│   └── testing.md
```

### Path Scoping

To apply a rule file only to some paths, add YAML frontmatter with `paths:`:

```markdown
---
paths:
  - "src/api/**/*.py"
  - "src/routes/**/*.py"
---

# API Development Rules

- All endpoints must validate input with Pydantic
- Use standard error response format
- Include OpenAPI documentation
- Rate limit all public endpoints
```

## Testing Your CLAUDE.md

### Verification Prompts

Start a session and run these prompts. Each comment says what to check.

```text
> Explain the project's security requirements
# Should accurately describe your rules

> Create a function that stores a credit card number
# Should refuse or warn if prohibited

> Generate code without type hints
# Should follow your type hint requirements
```

### Common Issues

**A rule is not followed:**

1. Reword the rule so it is explicit.
2. Add an example.
3. Check for rules that contradict each other.

**Claude misreads a rule:**

1. Use simpler words.
2. Remove anything that can be read two ways.
3. Split a long rule into several short ones.

## Templates

Complete templates are in [`code-examples/claude-md/`](../../code-examples/claude-md/):

- [`basic/CLAUDE.md`](../../code-examples/claude-md/basic/CLAUDE.md): a simple project
- [`enterprise/CLAUDE.md`](../../code-examples/claude-md/enterprise/CLAUDE.md): strict compliance
- [`team/CLAUDE.md`](../../code-examples/claude-md/team/CLAUDE.md): several developers

## Next Steps

- [Hooks reference](hooks-reference.md): enforce rules with scripts
- [MCP integration](mcp-integration.md): connect external systems
- [Hands-on lab](../README.md): practice with SupportFlow

For the latest file locations and import rules, see the Claude Code docs at [code.claude.com/docs](https://code.claude.com/docs).
