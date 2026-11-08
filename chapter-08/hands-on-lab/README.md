# Hands-On Lab: Building SupportFlow

**Reference**: Chapter 8, Section 8.6 (this lab) and Section 8.7 (the challenge labs in [`exercises/`](exercises/))
**Time**: A few minutes to run the reference implementation. Plan a 2-4 hour session to build SupportFlow yourself through the five phases.
**Done when**: Every box in [Success Criteria](#success-criteria) is checked. The last one is a working `/review-drafts` loop.

> **Update to the book (as of November 7, 2026): default permission mode.** A session with no permission mode configured starts in auto mode (Claude Code 2.1.283 and later). File edits in the project run without asking. A safety classifier decides on most commands instead of you. So you will see few of the approval prompts that Sections 8.2 and 8.6 describe.
>
> To approve each edit and command yourself, do one of these:
>
> - Start with `claude --permission-mode default`. The CLI shows this mode as Manual.
> - Set `"defaultMode": "default"` under `permissions` in `~/.claude/settings.json`, as the [setup tutorial's](tutorials/claude-code-setup.md#user-configuration) user configuration does.
>
> From auto mode, the first Shift+Tab switches to Manual. The third reaches plan mode. A `/plan` prefix works in any mode.

In this lab you build **SupportFlow**, a customer support automation system. You write the prompts and Claude writes the code. Your build will not match this repository line for line. That is expected.

[`supportflow/`](supportflow/) is the finished reference implementation. Use it to:

- See the target
- Compare it against your own build
- Fall back to it if a phase goes wrong

[`tutorials/`](tutorials/) holds quick references for installing Claude Code, CLAUDE.md, hooks, and MCP (Sections 8.2 to 8.4).

## Lab Overview

### The Business Problem

A support team handles 500+ tickets a day. Each takes roughly 15 minutes:

- Reading (2-3 min)
- Categorizing and prioritizing (1-2 min)
- Drafting replies to routine issues (5-10 min)
- Escalating anything unusual (varies)

### The Solution

SupportFlow takes over the routine steps. The system triages tickets and drafts replies. A person approves or rejects each draft and handles the escalations.

### What You Will Build

1. **Ticket Analyzer**: assigns a category, urgency level, and sentiment to each incoming ticket
2. **Response Generator**: produces template-based draft replies
3. **Escalation Engine**: routes tickets that need a human
4. **Quality Hooks**: blocks any generated response from going out unreviewed

## Learning Objectives

By completing this lab, you will:

- Implement constitutional governance with CLAUDE.md
- Create lifecycle hooks for automated quality control
- Configure permission systems for bounded autonomy
- Build defense-in-depth validation layers
- Test systems against adversarial inputs

## Prerequisites

- Claude Code installed and authenticated (see [`tutorials/claude-code-setup.md`](tutorials/claude-code-setup.md))
- Python 3.11+ with pip
- Docker and Docker Compose (Phase 5 deploys and verifies the running container)
- `jq` installed (the governance hooks in Phase 3 parse JSON with it)
- Basic familiarity with FastAPI and Pydantic
- Terminal and command-line experience

## Lab Structure

```text
hands-on-lab/
├── README.md                 # This file
├── supportflow/              # Finished reference implementation
│   ├── .claude/              # The constitution, in force
│   │   ├── settings.json     # Permissions + PreToolUse hook
│   │   ├── hooks/            # validate-bash-command.sh + README
│   │   └── skills/
│   │       └── review-drafts/SKILL.md  # The Phase 3 review workflow
│   ├── CLAUDE.md             # Project constitution
│   ├── README.md             # How to run, test, and use it
│   ├── API_GUIDE.md          # Endpoint reference
│   ├── BUILD_PROMPT.md       # Full Phase 4 build prompt
│   ├── api/                  # FastAPI REST API
│   ├── database/             # SQLAlchemy models, repositories, connection
│   ├── models/               # Pydantic business models
│   ├── services/             # TicketAnalyzer, ResponseGenerator, EscalationEngine
│   ├── tests/                # Unit tests + integration/ + test_bash_hook.sh
│   ├── example*.py           # Three runnable demos, no server needed
│   └── Dockerfile, docker-compose.yml, requirements.txt
├── exercises/
│   ├── exercise-1-claude-md.md              # Skill builder
│   ├── exercise-2-hooks.md                  # Skill builder
│   ├── exercise-3-mcp.md                    # Skill builder
│   ├── challenge-1-debug-and-fix.md         # Section 8.7
│   ├── challenge-2-security-hardening.md    # Section 8.7
│   ├── challenge-3-observability.md         # Section 8.7
│   ├── challenge-labs-reference.md          # Patterns shared by all three
│   └── claude-code-features-for-challenges.md
└── tutorials/
    ├── claude-code-setup.md                 # Installation and configuration
    ├── claude-md-guide.md                   # CLAUDE.md deep dive
    ├── hooks-reference.md                   # Hook events, config, and patterns
    └── mcp-integration.md                   # MCP tutorial
```

## Getting Started

### Option 1: Run the reference implementation first

Run the finished system first. It takes a minute and shows you the target.

```bash
cd supportflow
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # Windows: copy .env.example .env

# With Docker
docker-compose up -d          # then open http://localhost:8000/docs
docker-compose logs -f

# Or locally
uvicorn api.main:app --reload --env-file .env

# Either way (no server needed for these)
pytest tests/ -v
python example.py             # ticket analysis demo
```

Submit a ticket to confirm the whole path works:

```bash
curl -X POST http://localhost:8000/tickets \
  -H "X-API-Key: demo-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"content": "I was charged twice for order ORD-2024-5678 and I need a refund."}'
```

**Expect about 20 of the 105 tests to fail (20 failed, 85 passed on the reference build). Do not fix them yet.** Those failures are the Challenge Lab 1 assignment. The test suite is the specification, and the implementation falls short of it on purpose in a few places. [`exercises/challenge-1-debug-and-fix.md`](exercises/challenge-1-debug-and-fix.md) maps each failure to the defect behind it. The suite passes only after you finish that challenge.

### Option 2: Build from scratch (recommended)

Follow Section 8.6 to build SupportFlow yourself:

```bash
mkdir my-supportflow && cd my-supportflow
claude
```

Read the permission-mode note at the top of this file before you start.

Then in the session:

```text
> /init
```

Work the five phases in order. In each phase:

1. Enter **plan mode** (Shift+Tab, or prefix with `/plan`) first. Review the approach before Claude writes code.
2. If a step produces something you do not want, run **`/rewind`**. Do not stack fixes on fixes.

For Phase 4, the chapter prints a condensed build prompt. The complete version is in [`supportflow/BUILD_PROMPT.md`](supportflow/BUILD_PROMPT.md). It adds request/response examples and endpoint documentation requirements. Use it when you want your build to track the reference solution closely.

### Option 3: Practice the individual skills

Do these three self-contained exercises in order:

1. **[Exercise 1: CLAUDE.md](exercises/exercise-1-claude-md.md)**: create constitutional governance
2. **[Exercise 2: Hooks](exercises/exercise-2-hooks.md)**: implement lifecycle hooks
3. **[Exercise 3: MCP](exercises/exercise-3-mcp.md)**: configure external integrations

## Key Constitutional Principles

### 1. Human Review Requirement

All AI-generated customer responses MUST be reviewed by humans before sending.

```python
# Enforcement in code
class GeneratedResponse(BaseModel):
    requires_human_review: bool = Field(default=True)
    status: ResponseStatus = Field(default=ResponseStatus.DRAFT)
```

### 2. Audit Logging

All ticket operations must be logged with timestamps and user identity.

### 3. Internal Detail Prevention

Never expose internal system details (stack traces, internal IDs, etc.) in customer-facing responses.

### 4. Priority Escalation

Negative/angry sentiment MUST trigger priority escalation for human review.

## Lab Phases

The prompts below are the ones printed in Section 8.6, in order. Notes that the book does not have are marked "Repo note".

### Phase 1: Project Setup with Constitutional Governance

- Create a CLAUDE.md with business rules and technical standards
- Use **plan mode** so Claude proposes the module layout and data flow before it writes a file
- Configure permissions

After `/init` (Option 2 above), customize the generated CLAUDE.md:

```text
Create a CLAUDE.md for SupportFlow with these requirements:
- Python 3.11+ with strict typing and in virtual environment
- FastAPI for the API layer
- Pydantic for request/response validation
- Customer-facing text must be reviewed by humans before sending
- All ticket data must be logged for audit purposes
- Never include internal system details in customer responses
- Sentiment analysis must flag tickets with negative sentiment for priority review
```

Then enter plan mode (Shift+Tab, or prefix the prompt with `/plan`) and ask for the approach before any file is written:

```text
> /plan How would you structure the SupportFlow project to satisfy
> every rule in CLAUDE.md? Propose the module layout and data flow.
```

### Phase 2: Building Core Components

- Implement TicketAnalyzer with keyword-based classification
- Build ResponseGenerator with template management
- Create EscalationEngine with configurable rules

```text
> Create a TicketAnalyzer class that:
> - Classifies tickets into categories: billing, technical, account, general
> - Assesses urgency: low, medium, high, critical
> - Detects sentiment: positive, neutral, negative, angry
> - Extracts key entities: account IDs, order numbers, product names
> Use Pydantic models for all data structures.
```

```text
> Create a ResponseGenerator that:
> - Maintains a library of template responses for common issues
> - Personalizes templates with ticket-specific details
> - Marks all generated responses as "draft" requiring human approval
> - Never includes internal error codes or system details in responses
```

```text
> Create an EscalationEngine that flags tickets for human review when:
> - Sentiment is "angry" or multiple negative indicators
> - Issue involves refunds over $100
> - Customer mentions legal action, social media, or competitors
> - Analyzer confidence is below 80%
> - Issue doesn't match any known category
```

### Phase 3: Governance Through Hooks and Skills

- Add a PreToolUse hook that blocks dangerous Bash commands
- Save the human-review workflow as a **skill** at `.claude/skills/review-drafts/SKILL.md`. Anyone who clones the repo can then run the same checklist with `/review-drafts`

The hook, short form (Option 1 in the book):

```text
> Create a PreToolUse hook that blocks dangerous Bash commands like rm -rf,
> sudo, chmod 777, and curl piped to sh. Save the hook configuration to
> .claude/settings.json
```

Or the detailed form (Option 2):

```text
> Create a security validation hook for Claude Code with the following:
> 1. Create a shell script at .claude/hooks/security-check.sh that:
>    - Reads JSON input from stdin
>    - Extracts the command from tool_input.command using jq
>    - Blocks commands containing: rm -rf, sudo, chmod 777, curl|sh, wget|sh
>    - Returns exit code 2 with an error message when blocked
>    - Returns exit code 0 when allowed
> 2. Add the hook configuration to .claude/settings.json that:
>    - Triggers on PreToolUse event
>    - Matches only Bash tool
>    - Runs the security-check.sh script
```

Repo note: Check the `command` Claude writes into `.claude/settings.json`. It should start with `"$CLAUDE_PROJECT_DIR"/.claude/hooks/`. A relative path stops resolving once Claude changes directory, and the hook then fails open. The reference implementation names the script `validate-bash-command.sh`, not `security-check.sh` ([`supportflow/.claude/hooks/README.md`](supportflow/.claude/hooks/README.md)).

The review workflow as a skill:

```text
> Create a project skill at .claude/skills/review-drafts/SKILL.md that
> walks through reviewing pending draft responses: list drafts, check each
> against our customer-response rules in CLAUDE.md, and summarize which
> to approve, which to reject, and why.
```

### Phase 4: Building and Unit Testing the API

- FastAPI REST endpoints over the three services
- SQLite plus SQLAlchemy behind a repository pattern
- API key authentication and audit logging
- Docker deployment and integration tests

The condensed build prompt from the chapter (the complete version is [`supportflow/BUILD_PROMPT.md`](supportflow/BUILD_PROMPT.md)):

```text
> Create a deployable FastAPI application for SupportFlow with Swagger UI:
> 1. REST API (api/main.py): POST /tickets, GET /tickets/{id},
>    GET /responses/pending, POST /responses/{id}/approve,
>    POST /responses/{id}/reject, GET /health. Use the existing
>    TicketAnalyzer, ResponseGenerator, and EscalationEngine services.
> 2. SQLite database with SQLAlchemy models (Ticket, TicketAnalysis,
>    Response, AuditLog) behind a repository pattern.
> 3. API key authentication via X-API-Key header.
> 4. Audit logging of every operation to the audit_logs table.
> 5. Docker deployment: Dockerfile + docker-compose.yml.
> 6. Integration tests covering submit -> analyze -> generate -> approve.
> 7. Update README.md with deployment and testing instructions.
> Constitutional requirements: all responses created as DRAFT requiring
> human approval, audit everything, no internal details in responses.
```

### Phase 5: Deployment and Functional Testing

- Verify the container is running and every endpoint responds
- Confirm sentiment detection, escalation, audit logging, and authentication behave as the constitution requires
- Run `/review-drafts` on the tickets you submitted during testing. The lab is done when this human-review loop works end to end

On the reference implementation in `supportflow/`, that loop does not work yet. The pending queue comes back empty and approvals are refused. Fix the Challenge Lab 1 defects (Tasks 2 and 3) to make it work. The verification run is meant to show these failures.

Make sure Docker is running, then:

```text
> Verify that the SupportFlow FastAPI application is deployed and fully
> functional. Fix any functional issues:
> 1. Check application status: confirm the Docker container is running and
>    review recent logs for errors.
> 2. Test every API endpoint: health check, ticket submission (use an angry
>    customer ticket), ticket retrieval, pending responses, approve one
>    response, reject another.
> 3. Verify core features: sentiment detection flags the angry ticket,
>    escalation fires on high priority, audit logging records operations,
>    authentication rejects requests without the API key.
> 4. Output: a clear summary showing all endpoints working, with example
>    responses, the Swagger UI URL, and sample curl commands I can run.
```

## Architecture Overview

```text
┌──────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                     │
├──────────────────────────────────────────────────────────────┤
│ POST /tickets  GET /tickets/:id  POST /responses/:id/approve │
└──────────────────────────────────────────────────────────────┘
                              │
┌──────────────────────────────────────────────────────────────┐
│                    Service Layer                             │
├────────────────┬──────────────────┬─────────────────────────┤
│ TicketAnalyzer │ ResponseGenerator │ EscalationEngine        │
│ - Categorize   │ - Draft responses │ - Priority routing      │
│ - Sentiment    │ - Template mgmt   │ - Rule evaluation       │
│ - Entities     │ - Human review    │ - Audit trails          │
└────────────────┴──────────────────┴─────────────────────────┘
                              │
┌──────────────────────────────────────────────────────────────┐
│                    Database Layer                            │
│  SQLAlchemy ORM with audit logging                          │
└──────────────────────────────────────────────────────────────┘
```

## Success Criteria

After completing the lab, your implementation should:

- [ ] Classify tickets into billing, technical, account, or general categories
- [ ] Detect sentiment (positive, neutral, negative, angry)
- [ ] Extract entities (account IDs, order numbers, product names)
- [ ] Generate draft responses with mandatory human review
- [ ] Escalate tickets based on configurable rules
- [ ] Log all operations for audit purposes
- [ ] Block dangerous operations via hooks
- [ ] Run the review workflow as a `/review-drafts` skill
- [ ] Pass all unit and integration tests

## Challenge Labs

Section 8.7 has three open-ended challenges, in increasing difficulty. Do them in order. Challenges 2 and 3 assume the fixes from challenge 1 are in place.

| Challenge | Focus | What you practice |
|-----------|-------|-------------------|
| [1. Debug and fix](exercises/challenge-1-debug-and-fix.md) | The deliberate defects in the reference implementation | Bug investigation, log analysis, systematic debugging |
| [2. Security hardening](exercises/challenge-2-security-hardening.md) | Key management, RBAC, rate limiting, input validation, TLS | Security review, architecture improvement, config management |
| [3. Observability and operations](exercises/challenge-3-observability.md) | Structured logging, Prometheus metrics, PostgreSQL, alerting, CI/CD | Infrastructure automation, performance analysis, DevOps |

Two supporting files:

- [`challenge-labs-reference.md`](exercises/challenge-labs-reference.md) collects the patterns and completion criteria common to all three.
- [`claude-code-features-for-challenges.md`](exercises/claude-code-features-for-challenges.md) maps each Claude Code feature to the task it helps with.

The defects in challenge 1 are intentional. The Phase 5 verification run finds them. Fixing them is the exercise.

## Troubleshooting

### Common Issues

1. **Import errors**: Run from `supportflow/`, the project root. Do not run from a subdirectory.
2. **Database errors**: Delete the SQLite file (`supportflow.db`, or the `data/` volume under Docker). Restart to recreate the schema.
3. **Hook not executing**: Check each of these:
   - The script is executable (`chmod +x .claude/hooks/*.sh`).
   - `jq` is installed.
   - `matcher` is a string such as `"Bash"`, not an object.
   - The hook `command` starts with `"$CLAUDE_PROJECT_DIR"`, not a relative path. Hooks run in the session's current directory, and that directory moves when Claude runs `cd`.

   Run `/hooks` in a session to list what Claude Code loaded.
4. **Hook times out**: `timeout` is in **seconds**. `10` means ten seconds.
5. **API key errors**: Set `API_KEY` in `.env`, or use the default `demo-key-12345`.
6. **Port 8000 already in use**: Stop the other process, or change the published port in `docker-compose.yml`.
7. **`docker-compose`: command not found**: Docker Engine installs on Linux ship Compose as a plugin. Run `docker compose` (with a space) wherever this lab says `docker-compose`.

### Getting Help

- Read `supportflow/CLAUDE.md` for the project's conventions and business rules
- Read `supportflow/API_GUIDE.md` for endpoint request and response shapes
- Check [`tutorials/`](tutorials/) for the quick references
- Run `/doctor` in Claude Code to diagnose installation and configuration problems

## Next Steps

After completing this lab:

1. Take on the [challenge labs](#challenge-labs) above
2. Borrow from the templates in [`../code-examples/`](../code-examples/) for your own projects
3. Read the tutorials in [`tutorials/`](tutorials/)
4. Move on to [Chapter 9: Agent Memory and Context Models: Building Cognitive Architectures for Agentic Systems](../../chapter-09/README.md)
