# Chapter 8 Code Listings: Constitutional Coding

The configuration and script listings from Chapter 8, in copy-paste form, under the section each one is printed in. Listings marked **Repo addition** are not printed in the book; they come from the SupportFlow reference implementation. Where current Claude Code behaves differently from the printed listing, a note follows it.

---

## 8.3 - Sample CLAUDE.md (Project Constitution)

```markdown
# Project: PaymentGateway

## Overview
Payment processing service handling $2M+ daily transactions.
PCI DSS compliance required. Uptime SLA: 99.99%.

## Architecture Principles
- All database operations must be async (asyncpg)
- Financial calculations use Decimal, never float
- Every state change requires an audit log entry

## Code Standards
- Python 3.11+ with strict type hints
- No raw SQL, use SQLAlchemy ORM exclusively
- All public functions require docstrings

## Security Requirements
- No secrets in code, use environment variables
- All user input validated and sanitized
- Rate limiting on all public endpoints

## Testing
- Minimum 90% code coverage for financial logic
- Integration tests use isolated test database
- Mock external payment processors in unit tests
```

---

## 8.3 - Modular Rules Structure

Create this folder structure for large projects:

```text
your-project/
├── CLAUDE.md              # Main project instructions
└── .claude/
    └── rules/
        ├── security.md    # Security requirements
        ├── api-design.md  # API conventions
        └── testing.md     # Testing standards
```

### Example: api-design.md with Path Scoping

```markdown
---
paths:
  - "src/api/**/*.ts"
  - "src/controllers/**/*.ts"
---

# API Development Rules
- All endpoints must include input validation
- Use standard error response format
- Include OpenAPI documentation comments
```

---

## 8.3 - PreToolUse Hook: Block Dangerous Commands

Save as `.claude/hooks/validate-bash.sh`:

```bash
#!/bin/bash
# .claude/hooks/validate-bash.sh
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Block destructive operations
BLOCKED="git push --force|git reset --hard|rm -rf /"
if echo "$COMMAND" | grep -qE "$BLOCKED"; then
    echo "BLOCKED: This command matches a dangerous pattern" >&2
    exit 2  # Exit code 2 blocks the operation
fi
exit 0
```

Make executable: `chmod +x .claude/hooks/validate-bash.sh`

---

## 8.3 - PostToolUse Hook: Auto-Run Tests

Save as `.claude/hooks/post-edit.sh`:

```bash
#!/bin/bash
# .claude/hooks/post-edit.sh
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [[ "$FILE_PATH" == *.py ]]; then
    echo "Running tests for modified file..."
    pytest tests/ -x -q --tb=short >&2 || exit 2
fi
```

Make executable: `chmod +x .claude/hooks/post-edit.sh`

Exit code 2 with the failures on stderr is what lets Claude see them after the edit. [`code-examples/hooks/post-edit-tests.sh`](code-examples/hooks/post-edit-tests.sh) is a fuller version that also covers JavaScript and Rust projects.

---

## 8.3 - Permission Configuration

Save in `.claude/settings.json` or project settings:

```json
{
  "permissions": {
    "allow": [
      "Bash(npm test)",
      "Bash(npm run build)",
      "Bash(git status)",
      "Bash(git diff*)",
      "Edit(src/**)",
      "Edit(tests/**)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(git push --force*)",
      "Edit(.env*)",
      "Edit(**/secrets/**)"
    ],
    "defaultMode": "acceptEdits"
  }
}
```

As of November 7, 2026, the VS Code extension's chat panel does not read `defaultMode` from a project's `.claude/settings.json` or `.claude/settings.local.json`, so its conversations do not start in `acceptEdits` from this file; the allow and deny rules still apply there. To start them in `acceptEdits`, set `claudeCode.initialPermissionMode` to `acceptEdits` in your VS Code user settings (see the [setup tutorial](hands-on-lab/tutorials/claude-code-setup.md#vs-code-extension)).

---

## 8.3 - Sandbox Configuration

```json
{
  "sandbox": {
    "enabled": true
  }
}
```

Or run `/sandbox` in a session. Enables OS-level confinement of Bash commands; used in Challenge Lab 2. How the sandbox layer differs from permission rules is explained in Chapter 8.

---

## 8.4 - MCP Server Configuration

Add to `.mcp.json` at the project root (the project-scope MCP config file; `claude mcp add --scope project` writes here):

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@toolbox-sdk/server", "--prebuilt=postgres", "--stdio"],
      "env": {
        "POSTGRES_HOST": "${POSTGRES_HOST}",
        "POSTGRES_DATABASE": "${POSTGRES_DATABASE}",
        "POSTGRES_USER": "${POSTGRES_USER}",
        "POSTGRES_PASSWORD": "${POSTGRES_PASSWORD}"
      }
    },
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${GITHUB_PAT}"
      }
    }
  }
}
```

Postgres via MCP Toolbox for Databases; GitHub via its hosted server. Do not substitute the archived `@modelcontextprotocol/server-postgres` or `server-github` packages (deprecated 2025). Used in Exercise 3.

---

## 8.4 - Custom Sub-Agent Definition

Save as `.claude/agents/security-reviewer.md`:

```markdown
---
name: security-reviewer
description: Security expert. Use after any auth-related changes.
tools: Read, Grep, Glob
model: sonnet
---

You are a senior security engineer specializing in OWASP Top 10.

When invoked:
1. Identify authentication and authorization code
2. Check for common vulnerabilities
3. Provide prioritized findings

Focus on: injection, broken auth, sensitive data exposure.
```

---

## 8.4 - GitHub Actions Integration

Save as `.github/workflows/claude-review.yml`:

```yaml
name: Claude Code Review
on:
  pull_request:
    types: [opened, synchronize]
jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
      id-token: write
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 1
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: |
            REPO: ${{ github.repository }}
            PR NUMBER: ${{ github.event.pull_request.number }}
            Review this pull request for code quality, security,
            and test coverage. Post inline comments on specific
            issues and a summary comment.
          claude_args: |
            --allowedTools "mcp__github_inline_comment__create_inline_comment,Bash(gh pr comment:*),Bash(gh pr diff:*),Bash(gh pr view:*)"
```

Reviews every PR automatically. For @claude-mention conversational review instead, run `/install-github-app` and use the simpler workflow it writes.

---

## 8.5 - Headless Mode for CI/CD

```bash
claude -p "Review the changes in this PR. Check for security issues." \
       --allowedTools "Read,Glob,Grep" \
       --output-format json
```

`-p` runs one prompt and exits; `--output-format json` gives parseable output; add `--permission-mode plan` to keep the run read-only. Used in Challenge Lab 3's CI pipeline.

---

## 8.6 - SupportFlow Hands-on Lab

### Project Setup

```bash
mkdir supportflow && cd supportflow
claude
```

Then run:
```text
> /init
```

### SupportFlow CLAUDE.md (Repo addition)

A minimal constitution of the kind the Phase 1 prompt produces. The full one the reference implementation uses is [`hands-on-lab/supportflow/CLAUDE.md`](hands-on-lab/supportflow/CLAUDE.md).

```markdown
# Project: SupportFlow

## Overview
Customer support automation system for ticket triage and response generation.

## Architecture
- Python 3.11+ with strict typing
- FastAPI for the API layer
- Pydantic for request/response validation

## Business Rules
- Customer-facing text must be reviewed by humans before sending
- All ticket data must be logged for audit purposes
- Never include internal system details in customer responses
- Sentiment analysis must flag tickets with negative sentiment for priority review

## Code Standards
- All functions must have type hints
- Use Pydantic models for all data structures
- Complete docstrings for public APIs
```

### Hooks Configuration (Repo addition)

Add to `.claude/settings.json`. `$CLAUDE_PROJECT_DIR` is the project root. The path still resolves after Claude changes directory.

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{
        "type": "command",
        "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/validate-customer-response.sh"
      }]
    }]
  }
}
```

### Response Validation Hook (Repo addition)

Save as `.claude/hooks/validate-customer-response.sh`. As a PostToolUse hook it cannot undo the write. Exit 2 sends the error back to Claude, and Claude fixes the file. The fuller version is [`code-examples/hooks/validate-customer-response.sh`](code-examples/hooks/validate-customer-response.sh):

```bash
#!/bin/bash
# .claude/hooks/validate-customer-response.sh
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Check if this is a customer-facing response
if [[ "$FILE_PATH" == *"responses"* ]]; then
    # Ensure it's marked as draft
    if ! grep -q "STATUS: DRAFT" "$FILE_PATH"; then
        echo "ERROR: Customer responses must be marked as DRAFT" >&2
        exit 2
    fi
fi
exit 0
```

Make executable: `chmod +x .claude/hooks/validate-customer-response.sh`

### SupportFlow Project Structure (Repo addition)

The layout the lab converges on, matching `companion-repo/chapter-08/hands-on-lab/supportflow/`:

```text
supportflow/
├── CLAUDE.md                     # Project constitution
├── .claude/
│   ├── settings.json             # Permissions + hooks configuration
│   ├── hooks/
│   │   └── validate-bash-command.sh
│   └── skills/
│       └── review-drafts/SKILL.md    # The human-review workflow
├── api/                          # FastAPI REST layer
│   ├── main.py                   # Endpoints
│   ├── schemas.py                # Request/response models
│   └── dependencies.py           # DB session + API key auth
├── database/                     # Persistence
│   ├── models.py                 # SQLAlchemy: Ticket, TicketAnalysis,
│   │                             #   Response, AuditLog
│   ├── repositories.py           # Repository pattern
│   └── connection.py
├── models/                       # Pydantic business models
│   ├── ticket_analysis.py
│   ├── response.py
│   └── escalation.py
├── services/                     # Business logic
│   ├── ticket_analyzer.py        # Classification, sentiment, entities
│   ├── response_generator.py     # Template drafting, always DRAFT
│   └── escalation_engine.py      # Human escalation rules
├── tests/                        # Unit tests + integration/
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Reference Tables

The chapter's lookup tables are in the book: available tools and their default permissions (Table 8.1), everyday slash commands (Table 8.2), the memory hierarchy (Table 8.3), hook events (Table 8.4), hook exit codes (Table 8.5), and permission modes (Table 8.6). The current versions live in the Claude Code documentation at [code.claude.com/docs](https://code.claude.com/docs). Claude Code behavior that affects these listings, as of November 7, 2026:

- The tool that launches sub-agents is named `Agent` (releases before Claude Code 2.1.63 call it `Task`, and `Task(...)` works as an alias); use `Agent` in permission rules and hook matchers.
- On macOS, Linux, and WSL, Claude Code leaves `Glob` and `Grep` out of the default tool set and searches with `find` and `grep` through Bash, whose built-in read-only commands run without prompting. Naming either tool in `--allowedTools`, as the Section 8.5 headless listing does, restores both.
- Claude Code checks file paths only against `Edit(...)` and `Read(...)` rules. A `Write(path)` rule is accepted but never consulted, which is why the permission listing above uses `Edit(...)`.
- A hook exit code other than 0 or 2 is a non-blocking error: the operation continues, and the transcript shows a hook error notice.
- PostToolUse hooks cannot block, because the tool already ran; exit 2 there shows stderr to Claude.
- The default timeout for a command hook is 600 seconds.
- The built-in Explore sub-agent runs on the main conversation's model.
- The sandbox is off until you enable it, and it covers Bash commands on macOS, Linux, and WSL2; native Windows runs commands unsandboxed.
- An interactive session with no permission mode configured starts in `auto` (Claude Code 2.1.283 and later), and the CLI shows `default` as Manual. Start with `claude --permission-mode default`, or set `permissions.defaultMode`, to be asked before each edit and command.

---

## Quick Reference: MCP Server Packages (Repo addition)

| Server | Package | Purpose |
|--------|---------|---------|
| PostgreSQL | `@toolbox-sdk/server` (MCP Toolbox for Databases, `--prebuilt=postgres`) | Database queries |
| GitHub | Official GitHub MCP server (hosted `https://api.githubcopilot.com/mcp/` or Docker `ghcr.io/github/github-mcp-server`) | Repository operations |
| Filesystem | `@modelcontextprotocol/server-filesystem` | File access |
| Memory | `@modelcontextprotocol/server-memory` | Persistent memory |

Anthropic archived its reference Postgres and GitHub servers in 2025. Package names go stale. Check the MCP registry before you wire one in.

---

## Quick Reference: Sub-Agent Frontmatter (Repo addition)

Only `name` and `description` are required.

- `tools` takes a comma-separated list. Omit it to inherit every tool.
- `model` takes `sonnet`, `opus`, `haiku`, a full model ID, or `inherit`.

```markdown
---
name: agent-name
description: When to use this agent
tools: Read, Grep, Glob, Write
model: sonnet
---

Agent instructions and system prompt here.
```

---

## Quick Reference: Hook Input JSON Structure (Repo addition)

This is what a PreToolUse hook receives on stdin for a Bash call. The field names come from the Claude Code hooks reference. Edit and Write calls carry `tool_input.file_path`, always an absolute path.

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/session-transcript.jsonl",
  "cwd": "/home/you/my-project",
  "permission_mode": "default",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {
    "command": "npm test"
  },
  "tool_use_id": "toolu_01ABC"
}
```

---

## Quick Reference: Escalation Priority Levels (Repo addition)

| Priority | Triggers |
|----------|----------|
| CRITICAL | Angry + legal threat, or 4+ negative indicators |
| HIGH | Angry sentiment, legal threat, or 3+ negative indicators |
| MEDIUM | Social media threat, competitor mention, or 2 indicators |
| LOW | Single indicator (high refund, low confidence) |

---

## Complete SupportFlow CLAUDE.md Example (Repo addition)

````markdown
# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

SupportFlow is a customer support ticket management system with AI-powered
ticket analysis. The system enforces mandatory human review for customer-facing
content and maintains complete audit trails for compliance.

## Development Commands

### Running the Application

```bash
# Using Docker Compose (Recommended)
docker-compose up

# The API will be available at:
# - http://localhost:8000 (API endpoints)
# - http://localhost:8000/docs (Interactive Swagger UI)
```

### Testing

```bash
# Run all tests with coverage
pytest tests/ --cov=models --cov=services --cov=api --cov-report=html

# Run only unit tests
pytest tests/ --ignore=tests/integration -v

# Type check all code
mypy models/ services/ api/ database/
```

## Architecture

### Core Design Pattern: Service Layer Architecture

1. **API Layer** (`api/`): FastAPI REST endpoints
2. **Database Layer** (`database/`): SQLAlchemy ORM
3. **Services Layer** (`services/`): Business logic
4. **Models Layer** (`models/`): Pydantic validation

### Critical Business Rules

1. **Human Review Requirement**: All AI-generated responses MUST be reviewed
2. **Audit Logging**: All ticket operations logged with timestamps
3. **Internal Detail Prevention**: Never expose system details to customers

## Technical Requirements

- Python 3.11+ with strict type hints
- Pydantic for all data structures
- Minimum 80% test coverage

## Prohibited Actions

Never:
1. Send AI-generated content without human review
2. Expose internal system information in responses
3. Skip audit logging for ticket operations
4. Use weak or dynamic typing
````
