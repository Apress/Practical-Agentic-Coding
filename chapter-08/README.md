# Chapter 8: Constitutional Coding: Mastering Claude Code

Governance templates, tutorials, and the SupportFlow hands-on lab for Chapter 8.

## What's here

| Directory | What it is | Book section |
|-----------|-----------|--------------|
| `hands-on-lab/tutorials/` | Quick references: installing Claude Code, writing CLAUDE.md, hooks, MCP. | 8.2, 8.3, 8.4 |
| `code-examples/` | Copy-and-adapt artifacts: three CLAUDE.md templates, three working hook scripts, two MCP server configs, two sub-agent definitions. | 8.3, 8.4 |
| `hands-on-lab/supportflow/` | The finished SupportFlow application: FastAPI API, SQLAlchemy database, three services, tests, Docker, and its own `.claude/` governance directory. | 8.6 |
| `hands-on-lab/exercises/` | Three skill-building exercises (CLAUDE.md, hooks, MCP) plus the three Section 8.7 challenge labs. | 8.3, 8.4, 8.7 |
| `listings.md` | The chapter's configuration and script listings in copy-paste form, with notes on current Claude Code behavior. | All |

**Start here**: [`hands-on-lab/README.md`](./hands-on-lab/). It shows how to run SupportFlow and how to build your own from the chapter prompts.

## Section map

| Section | Topic | Where it is in this directory |
|---------|-------|------------------------------|
| 8.2 | Terminal-first architecture, the agentic loop, @-mentions, slash commands | `hands-on-lab/tutorials/claude-code-setup.md` |
| 8.3 | Governance: memory hierarchy, hooks, permissions, plan mode, checkpoints, skills | `hands-on-lab/tutorials/claude-md-guide.md`, `hands-on-lab/tutorials/hooks-reference.md`, `code-examples/claude-md/`, `code-examples/hooks/` |
| 8.4 | MCP, sub-agents, multi-platform deployment | `hands-on-lab/tutorials/mcp-integration.md`, `code-examples/mcp-configs/`, `code-examples/subagents/` |
| 8.5 | Extended thinking, collaboration patterns, headless mode | `listings.md` (headless CI/CD invocation) |
| 8.6 | Hands-on lab: SupportFlow | `hands-on-lab/supportflow/` |
| 8.7 | Challenge labs: debug and fix, security hardening, observability | `hands-on-lab/exercises/challenge-*.md` |

## Go further with Claude Code

These Claude Code features build on what Chapter 8 teaches. Plans, pricing, and availability change. Each item links to the vendor page with current details.

- **Mods.** A mod is a plugin written as JavaScript or TypeScript handlers that run inside Claude Code. A mod can hold or answer a tool call, draw a pane, or add a command that runs without a Claude turn. The shell-script hooks in this chapter keep working. The docs call them settings hooks to tell the two apart. Use a mod only when a settings hook cannot do the job. A mod runs with your permissions, so install mods only from sources you trust. Administrators can allow only their own mods with the `allowManagedModsOnly` managed setting. Introduced in Claude Code 2.1.287 (October 2026). [Claude Code mods overview](https://code.claude.com/docs/en/plugins/mods/overview)
- **Fail-closed hooks.** Add `"onFailure": "block"` to a command or HTTP hook. The action is then refused when the hook cannot start, times out, or exits with an unexpected code. Without it, a security hook with a mistyped path or a script that crashes lets the action through. The hooks in this chapter already exit 2 when `jq` is missing. `onFailure` covers the failures a script cannot catch for itself. Introduced in Claude Code 2.1.295 (October 2026). [Hooks reference](https://code.claude.com/docs/en/hooks)
- **Block writes outside the project.** Set `"permissions": {"blockWritesOutsideWorkingDirectories": true}`. The Write, Edit, and NotebookEdit tools then refuse paths outside your working directories. This applies in every permission mode, `bypassPermissions` included. It does not limit shell commands, MCP tools, or the programs hooks run. Turn on `/sandbox` as well. Introduced in Claude Code 2.1.314 (October 2026). [Settings reference](https://code.claude.com/docs/en/settings-reference#permissions-blockwritesoutsideworkingdirectories)
- **Deny instead of prompting.** Set `"permissions": {"denyInsteadOfPrompting": true}`. A pending permission prompt then becomes a denial. An unattended session, subagent, or teammate keeps working instead of waiting on you. The setting is documented in the release notes. Introduced in Claude Code 2.1.319 (November 2026). [Claude Code CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)
- **AGENTS.md as project instructions.** In a project with no CLAUDE.md, Claude Code loads AGENTS.md as the project instructions. One file can then serve Claude Code and the other agents in Part II. When both files exist, CLAUDE.md loads by default. To choose which loads, use Project instructions in `/config`. Introduced in Claude Code 2.1.277 (September 2026). [Memory: AGENTS.md](https://code.claude.com/docs/en/memory#agents-md)
- **Model and provider policy for organizations.** Managed settings can limit which API providers a machine may use (`allowedProviders`), block named models (`deniedModels`), keep each model version out until you list it (`"availableModelsMatch": "exact"`), and cap effort (`maxEffortLevel`, which also works outside managed settings). Use them with the enterprise template in `code-examples/claude-md/enterprise/`. Introduced in Claude Code 2.1.267 to 2.1.285 (September 2026). [Model configuration](https://code.claude.com/docs/en/model-config)
- **Spend controls on the Claude apps gateway.** For organizations that route Claude Code through a self-hosted Claude apps gateway:
  - Cap each developer's spend by day, week, or month.
  - Give a group one shared monthly pool on top of each member's own cap.
  - Pull past spend per developer, per day, or per IdP group from `GET /v1/organizations/analytics/cost`.

  Developers see their own spend in `/usage`. Per-developer caps are on the spend limits page. Pooled budgets and the cost report are described in the release notes. Introduced in Claude Code 2.1.316 to 2.1.319 (October and November 2026). [Gateway spend limits](https://code.claude.com/docs/en/claude-apps-gateway-spend-limits) and the [Claude Code CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)
- **Subagent effort and follow-ups.** `CLAUDE_CODE_SUBAGENT_EFFORT` gives every subagent that names no effort level its own default instead of the session's. Some subagents or teammates run on a different model from the session, such as the sub-agents in `code-examples/subagents/` that pin `sonnet`. They use that model's saved or default effort, not the session's. Finished subagents stay listed under Earlier in this session in `/tasks`. You can reopen one and send it a follow-up. Introduced in Claude Code 2.1.316 to 2.1.319 (October and November 2026). [Subagents](https://code.claude.com/docs/en/sub-agents)
- **Audit commands for your constitution and skills.** `/doctor prompt-audit` checks CLAUDE.md, AGENTS.md, skills, agents, and commands for prompting patterns written for older models, and `/skill-doctor` shows which skills go unused and what each costs in context. Plugin authors can run `claude plugin eval` for scored, repeatable test runs. Introduced in Claude Code 2.1.263 to 2.1.283 (September 2026). [Commands reference](https://code.claude.com/docs/en/commands)

## What you practice here

Chapter 8 covers Claude Code's governance model. This directory is where you practice it. You will:

- Write a CLAUDE.md constitution and modular rule files
- Configure lifecycle hooks, permission rules, plan mode, checkpoints, and a project skill
- Wire up MCP servers and define custom sub-agents
- Build, deploy, and verify the SupportFlow application end to end
- Harden and operate it in the three challenge labs

The concepts behind these features, and how Claude Code compares with other tools, are in Chapter 8.

## Directory Structure

```text
chapter-08/
├── README.md                            # This file
├── listings.md                          # The chapter's config and script listings
├── hands-on-lab/
│   ├── README.md                        # Lab instructions, start here
│   ├── supportflow/                     # The finished SupportFlow application
│   │   ├── .claude/                     # Its own constitution in action
│   │   │   ├── settings.json            # Permissions + PreToolUse hook
│   │   │   ├── hooks/
│   │   │   │   ├── validate-bash-command.sh
│   │   │   │   └── README.md            # Every pattern it blocks, and why
│   │   │   └── skills/
│   │   │       └── review-drafts/SKILL.md   # The human-review workflow (Phase 3)
│   │   ├── CLAUDE.md                    # Project constitution
│   │   ├── README.md                    # How to run, test, and use it
│   │   ├── API_GUIDE.md                 # Endpoint reference
│   │   ├── BUILD_PROMPT.md              # Full Phase 4 build prompt
│   │   ├── api/                         # FastAPI: main, schemas, dependencies
│   │   ├── database/                    # SQLAlchemy: models, repositories, connection
│   │   ├── models/                      # Pydantic: ticket_analysis, response, escalation
│   │   ├── services/                    # ticket_analyzer, response_generator,
│   │   │                                #   escalation_engine
│   │   ├── tests/                       # Unit tests + integration/ + test_bash_hook.sh
│   │   ├── example*.py                  # Three runnable demos, no server needed
│   │   ├── Dockerfile, docker-compose.yml
│   │   ├── requirements.txt, mypy.ini, pytest.ini
│   │   └── .env.example
│   ├── exercises/
│   │   ├── exercise-1-claude-md.md      # Skill builder: writing a constitution
│   │   ├── exercise-2-hooks.md          # Skill builder: lifecycle hooks
│   │   ├── exercise-3-mcp.md            # Skill builder: MCP servers
│   │   ├── challenge-1-debug-and-fix.md         # Section 8.7, challenge 1
│   │   ├── challenge-2-security-hardening.md    # Section 8.7, challenge 2
│   │   ├── challenge-3-observability.md         # Section 8.7, challenge 3
│   │   ├── challenge-labs-reference.md          # Patterns shared by all three
│   │   └── claude-code-features-for-challenges.md  # Which feature for which task
│   └── tutorials/
│       ├── claude-code-setup.md         # Installation and configuration
│       ├── claude-md-guide.md           # CLAUDE.md quick reference
│       ├── hooks-reference.md           # Hook events and config
│       └── mcp-integration.md           # MCP quick reference
└── code-examples/
    ├── claude-md/                       # CLAUDE.md templates
    │   ├── basic/CLAUDE.md
    │   ├── enterprise/CLAUDE.md
    │   └── team/CLAUDE.md
    ├── hooks/                           # Hook scripts you can run today
    │   ├── validate-bash.sh             # PreToolUse: block dangerous commands
    │   ├── post-edit-tests.sh           # PostToolUse: auto-run tests
    │   ├── validate-customer-response.sh
    │   └── README.md
    ├── mcp-configs/                     # MCP configurations
    │   ├── postgres-config.json
    │   ├── github-config.json
    │   └── README.md
    └── subagents/                       # Sub-agent definitions
        ├── security-reviewer.md
        ├── test-writer.md
        └── README.md
```

The defects Challenge Lab 1 has you fix are **deliberate**. They are in `hands-on-lab/supportflow/`. Do not treat them as repository bugs. See [`hands-on-lab/exercises/challenge-1-debug-and-fix.md`](./hands-on-lab/exercises/challenge-1-debug-and-fix.md) for the list.

## Quick reference

Keep Tables 8.1 to 8.6 from the chapter open during the lab. They cover the memory hierarchy, tools and default permissions, permission modes, slash commands, hook events, and exit codes. The Claude Code documentation at [code.claude.com/docs](https://code.claude.com/docs) has the current versions.

[`listings.md`](./listings.md) collects the chapter's configs and scripts in copy-paste form. It adds notes where current Claude Code behavior matters.

## Quick Start

### 1. Run the reference implementation

Run SupportFlow first. It takes a few minutes and shows you the target.

```bash
cd hands-on-lab/supportflow
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt   # the tests and demos run on your machine
cp .env.example .env              # Windows: copy .env.example .env
docker-compose up -d              # API on http://localhost:8000/docs
pytest tests/ -q                  # the suite the lab has you generate
```

If `docker-compose` prints `command not found`, your Docker install ships Compose as a plugin. Run `docker compose` (with a space) wherever this lab says `docker-compose`.

About 20 of the 105 tests fail on purpose (20 failed, 85 passed on the reference build). They are Challenge Lab 1's assignment. Your checkout is not broken (see below). The suite needs no running server. `pytest.ini` adds coverage flags automatically, so the run prints a coverage report even with `-q`.

Or without Docker, in the same activated virtual environment:

```bash
uvicorn api.main:app --reload --env-file .env
python example.py                 # ticket analysis demo, no server needed
```

### 2. Build it yourself

[`hands-on-lab/README.md`](./hands-on-lab/) walks you through the five phases from Section 8.6. This is the main path through the chapter.

1. Write the constitution.
2. Build the three services.
3. Add governance hooks and the review skill.
4. Build the API.
5. Verify it end to end.

### 3. Practice the individual skills

[`hands-on-lab/exercises/`](./hands-on-lab/exercises/) has three self-contained exercises:

1. [Exercise 1](./hands-on-lab/exercises/exercise-1-claude-md.md): writing an effective CLAUDE.md
2. [Exercise 2](./hands-on-lab/exercises/exercise-2-hooks.md): implementing lifecycle hooks
3. [Exercise 3](./hands-on-lab/exercises/exercise-3-mcp.md): configuring MCP servers

### 4. Take on the challenge labs

Section 8.7 has three challenges, in increasing difficulty. Start with challenge 1. The other two assume its fixes are in place.

1. [Debug and fix](./hands-on-lab/exercises/challenge-1-debug-and-fix.md): the deliberate defects behind the failing tests, to find and fix
2. [Security hardening](./hands-on-lab/exercises/challenge-2-security-hardening.md): key management, RBAC, rate limiting, TLS
3. [Observability and operations](./hands-on-lab/exercises/challenge-3-observability.md): structured logging, metrics, PostgreSQL, CI/CD

### 5. Borrow from the templates

[`code-examples/`](./code-examples/) holds files you can copy into your own project:

- Three CLAUDE.md templates at different scales
- Three hook scripts
- Two MCP server configs
- Two sub-agent definitions

## Prerequisites

- Terminal and command-line familiarity
- Basic shell scripting (bash), plus `jq` installed (every hook example parses JSON with it)
- Node.js and npm, for the MCP servers in Section 8.4 (as of November 7, 2026, the filesystem and memory servers require a current Node.js 24 or later)
- Python 3.11+ for the hands-on lab
- Docker and Docker Compose, for the lab's deployment and verification phases
- Claude Code installed and authenticated (see [`hands-on-lab/tutorials/claude-code-setup.md`](./hands-on-lab/tutorials/claude-code-setup.md))

## Additional Resources

- [Claude Code Documentation](https://code.claude.com/docs)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Anthropic Developer Portal](https://console.anthropic.com/)

## Navigation

- **Previous**: [Chapter 7 - Cursor and GitHub Copilot (Agent Mode): Mainstream AI Integration](../chapter-07/README.md)
- **Next**: [Chapter 9 - Agent Memory and Context Models: Building Cognitive Architectures for Agentic Systems](../chapter-09/README.md) (Part III)

Also relevant:

- [Chapter 6 - Intent-First Development: Mastering Google Antigravity and the Antigravity CLI](../chapter-06/README.md)
- [Chapter 11](../chapter-11/README.md), which builds the headless-mode CI/CD pipelines this chapter introduces
