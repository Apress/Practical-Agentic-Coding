# Chapter 7: Cursor and GitHub Copilot (Agent Mode): Mainstream AI Integration

Reference material, tutorials, and the LinkForge hands-on lab for Chapter 7.

## What's here

| Directory | What it is | Book section |
|-----------|-----------|--------------|
| `tutorials/` | Quick-reference guides for both tools. They cover installation, rules, instructions files, the six Cursor cookbook recipes, a dated note on GitHub Spark, and migrating between the tools. | 7.2, 7.3, 7.4 |
| `code-examples/` | Governance files, prompt libraries, and MCP configs to copy and adapt. Also the same tasks done in both tools. | 7.2, 7.3, 7.4 |
| `hands-on-lab/` | LinkForge, the app you build with the four-phase hybrid workflow. It is a FastAPI URL shortener with Redis caching, a test suite, and Copilot-driven deployment. | 7.6, 7.7 |
| `hands-on-lab/exercises/` | Three graded practice exercises to work before or alongside the lab. | 7.2, 7.3 |

Start with [`hands-on-lab/README.md`](./hands-on-lab/). The `linkforge/` directory next to it is the finished reference implementation. Read it to compare with your build. Run it directly if a lab step goes wrong.

> **Rule format note.** Cursor's governance convention is Project Rules. These are `.mdc` files with YAML frontmatter in `.cursor/rules/`, plus an `AGENTS.md` in the project root. Copilot in VS Code also auto-detects `AGENTS.md`. The lab and the templates in [`code-examples/cursor/project-rules/`](./code-examples/cursor/project-rules/) use that format. It matches Section 7.2 and the Section 7.6 lab steps. Cursor's documentation calls the older single-file `.cursorrules` legacy and slated for deprecation. If you have one from another project, split it into `.cursor/rules/*.mdc` or move it to `AGENTS.md`.

## Section map

| Section | Topic | Where it is in this directory |
|---------|-------|-------------------------------|
| 7.2 | Cursor: Tab, Inline Edit, Agents Window, indexing, rules, MCP | `tutorials/cursor-setup.md`, `tutorials/cursorrules-guide.md`, `code-examples/cursor/` |
| 7.2 | Rule templates to copy: basic, Python, TypeScript, enterprise | [`code-examples/cursor/project-rules/`](./code-examples/cursor/project-rules/) |
| 7.2 | Agent Skills: one skill, three load paths (`.cursor/skills/`, `.github/skills/`, shared `.agents/skills/`) | [`code-examples/skills/`](./code-examples/skills/) |
| 7.2 | The six cookbook recipes (data science, full-stack, MCP servers, Mermaid, large codebases, Bugbot) | `tutorials/cursor-cookbook-recipes.md` |
| 7.3 | GitHub Copilot: chat modes, ubiquity layer, Mission Control, Spaces, GitHub Spark | `tutorials/copilot-setup.md`, `tutorials/github-spark.md`, `code-examples/copilot/` |
| 7.4 | The environment vs the platform | `code-examples/comparison/side-by-side.md`, `tutorials/choosing-tool.md` |
| 7.5 | The hybrid "Architect-Auditor" workflow | `code-examples/comparison/side-by-side.md` |
| 7.6 | Hands-on lab: LinkForge | `hands-on-lab/` |
| 7.7 | Challenge lab: the multi-tenant transformation | "Challenge" section at the end of `hands-on-lab/README.md` |

## Current tool behavior (as of November 7, 2026)

The files in this directory match both tools as they work as of November 7, 2026. Where they differ from the book text, follow the files here.

- **Cursor context mentions.** Cursor's @-mention list does not include `@Codebase`, `@Docs`, `@Web`, or `@Git`. The agent searches the codebase and the web with its own tools. You @-mention files and folders. Git diffs come in through `@Commit` and `@Branch`. Cursor's documentation does not describe Merkle-tree indexing, Memories, or Notepads.
- **Inline Edit.** Cursor has no separate Inline Edit prompt. Cmd+K (Ctrl+K) does what Cmd+L does. It opens the agent with the selected lines referenced in the prompt. Where a step uses Inline Edit, do this:
  1. Select the code.
  2. Press Cmd+K.
  3. Type the instruction.
  4. Review the agent's diff before you keep it.
- **Copilot Edit mode.** VS Code deprecated Edit mode in version 1.110. VS Code 1.126 and later offer it only when an administrator has disabled Agent mode by policy. The exercises here use Agent mode instead. They review each proposed edit before keeping it.
- **GitHub Spark.** GitHub has retired Spark on github.com (August 2026) and GitHub Models (July 2026). See [`tutorials/github-spark.md`](./tutorials/github-spark.md) for the status and the Section 7.3 steps you can still run.
- **Names.** GitHub calls the book's "Copilot Async Agent" the **Copilot cloud agent**. The agent dashboard the book calls mission control is the agents page at github.com/copilot/agents.

## Go further with Cursor and GitHub Copilot

Chapter 7 teaches agentic development with Cursor and GitHub Copilot. The capabilities below build on it. Plans, pricing, and availability change. Each item links to the vendor page with current details.

### Cursor

- **Rollouts.** A Cursor bot writes a monitoring plan when a pull request opens. After the change deploys, it checks logs, metrics, and traces in each environment. It reports the change as healthy, regressed, or inconclusive. On a regression it names the suspect change. It can open a revert pull request or hand off to a cloud agent. It does not merge or roll back on its own. Introduced in September 2026. [Cursor Rollouts](https://cursor.com/docs/rollouts)
- **Security Review.** A review bot reads each non-draft pull request in the context of the codebase. It posts one comment that lists exploitable bugs. Each bug has a severity, an attack path, and a proposed fix. The bot also enforces security rules your team writes. Style and quality review stay with Bugbot (Recipe 6 in [`tutorials/cursor-cookbook-recipes.md`](./tutorials/cursor-cookbook-recipes.md)). Introduced in September 2026. [Rollouts and Security Review](https://cursor.com/changelog/rollouts-and-security-reviewer)
- **Projects.** A coordinator agent takes on a long-running feature, migration, or full app. It plans and delegates to cloud and local agents. It does not write code itself. It keeps a shared set of context files in sync across the machines its agents use. It can act on Slack channels, schedules, or your pull requests without a prompt. Introduced in September 2026. [Projects](https://cursor.com/docs/agent/projects)
- **Self-hosted workers for cloud agents.** Cloud agent tool execution can run inside your own network. It can run on a single machine (My Machines) or on named, autoscaling worker pools shared by a team (Team pools). Start them from the CLI with `agent worker start` or `agent worker controller`. Cloud agents can also run in third-party sandboxes such as AWS Lambda, Cloudflare, Modal, Vercel, and E2B. Introduced in September 2026. [Team pools](https://cursor.com/docs/cloud-agent/self-hosted/pool)
- **Live apps from cloud agents.** Ask a cloud agent to build an app. Cursor scaffolds it, adds Postgres if needed, and sets up sign-in through Cursor SSO. Once its security checks pass (for example, for secrets in app files), Cursor hosts it at a domain you pick. Team admins can see every app, add custom security review rules, approve blocked publishes, and unpublish any app. Introduced in November 2026. [Apps](https://cursor.com/docs/cloud-agent/apps)

### GitHub Copilot

- **Copilot Automations.** An automation combines a prompt, triggers, and allowed tools. It runs Copilot in the cloud on its own, with AI Credit limits per run or per period. Triggers include:
  - GitHub events (issues, pull requests, code scanning, Dependabot alerts)
  - a REST API for outside systems such as Jira or PagerDuty
  - the success or failure of another automation

  Shared automations belong to a repository. VS Code runs automations in the cloud from the Agents window (setting `chat.automations.cloud.enabled`), or locally on a cron schedule. Introduced in October 2026. [Shared workflows with Copilot Automations](https://github.blog/changelog/2026-10-28-build-shared-workflows-for-your-team-with-copilot-automations)
- **Code review effort, approvals, and API.** The Max review effort runs several independent review agents on models from different providers. It reconciles their findings. It costs more time and AI Credits. Copilot's approval can count toward required approvals. The approval is dismissed when more commits are pushed. You can request reviews and set the effort level through the REST and GraphQL APIs. You can also manage code review settings through the API. Introduced in October 2026. [Max and approvals](https://github.blog/changelog/2026-10-28-copilot-code-review-merge-with-confidence-with-max-and-approvals)
- **Agent Merge.** Select **Watch and fix** in a pull request's merge box. Copilot then fixes failing Actions workflows, merge conflicts, or both in a cloud development environment. It works with auto-merge. It can be on by default for all your pull requests. Introduced on github.com in October 2026. [Agent Merge](https://github.blog/changelog/2026-10-28-agent-merge-watches-and-fixes-pull-requests-in-the-cloud)
- **Copilot Fusion.** In the model picker, choose Copilot Fusion with an effort level (Standard, High, or Max) instead of a single model. Copilot picks the model for each prompt, or orchestrates several, for example in a cascade. Local models can be part of the mix. Introduced in October 2026. [Copilot Fusion](https://github.blog/changelog/2026-10-28-route-and-orchestrate-models-with-github-copilot-fusion)
- **Local sandboxing.** In Copilot CLI, the Copilot app, and VS Code, the commands Copilot runs have restricted access to:
  - the filesystem
  - the network
  - Git and `gh` credentials
  - local MCP servers

  This works on Windows, macOS, and Linux. Enterprises can require the sandbox through managed settings. Introduced in October 2026. [Local sandboxing](https://github.blog/changelog/2026-10-07-local-sandboxing-for-github-copilot-now-generally-available)
- **Assisted permissions.** A model classifies each command, path, or URL request. Clearly safe ones proceed. The rest ask you. Turn it on with `/permissions` in Copilot CLI, or from the permissions picker in VS Code. Admins can block Allow All while keeping Assisted, or set the default mode. Introduced in October 2026. [Assisted permissions](https://github.blog/changelog/2026-10-26-github-copilot-assisted-permissions-generally-available)
- **Enterprise controls.** Enterprise admins can:
  - set one default policy (Enabled, Disabled, or Let organizations decide) for Copilot features added later
  - require or block plugins, and limit plugin marketplaces
  - enforce the enterprise `allowedMcpServers` list, in VS Code 1.145 and later

  Members can ask for a larger AI Credit budget. Owners approve it under Requests from members. Introduced in September and October 2026. [Global default for Copilot features](https://github.blog/changelog/2026-10-22-global-default-for-copilot-features-generally-available)
- **Impact dashboard and usage metrics API.** The Copilot impact dashboard shows feature engagement, industry comparisons, and agent adoption. Agent adoption includes Copilot Chat and the VS Code Agents window. The usage metrics API reports:
  - VS Code Agents use
  - custom skills, agents, and MCP servers
  - bring-your-own-key and enterprise custom models
  - the per-repository rate at which Copilot code review comments get addressed

  Introduced in September through November 2026. [Impact dashboard updates](https://github.blog/changelog/2026-11-06-copilot-impact-dashboard-adds-chat-and-vs-code-agent-usage)

## Directory Structure

```text
chapter-07/
├── README.md                            # This file
├── hands-on-lab/
│   ├── README.md                        # Lab instructions, start here
│   ├── linkforge/                       # Finished reference implementation
│   │   ├── .cursor/rules/linkforge.mdc  # Cursor project rule (Section 7.6, Step 2)
│   │   ├── .env.example                 # Environment template
│   │   ├── .github/
│   │   │   ├── copilot-instructions.md
│   │   │   └── workflows/deploy-azure.yml
│   │   ├── AGENTS.md                    # Cross-tool agent instructions
│   │   ├── README.md                    # How to run and test LinkForge
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml           # Postgres + Redis + API
│   │   ├── requirements.txt             # All dependencies upper-bounded
│   │   ├── run.sh                       # One-command local launcher
│   │   ├── src/                         # main, models, schemas, database,
│   │   │                                #   shortener, cache, analytics,
│   │   │                                #   ratelimit
│   │   └── tests/                       # conftest + shortening, analytics,
│   │                                    #   cache, security, ratelimit suites
│   └── exercises/
│       ├── exercise-1-cursor-basics.md
│       ├── exercise-2-copilot-modes.md
│       └── exercise-3-governance.md
├── code-examples/
│   ├── cursor/
│   │   ├── project-rules/               # Rule templates, .cursor/rules/*.mdc format
│   │   │   ├── README.md                #   Which template to pick, how to adapt it
│   │   │   ├── basic.mdc                #   Any language, minimal starting point
│   │   │   ├── python.mdc               #   Python, FastAPI/Django/data science
│   │   │   ├── typescript.mdc           #   TypeScript, React/Node
│   │   │   └── enterprise.mdc           #   Compliance, security, observability
│   │   ├── composer-prompts/            # Agent chat prompt examples
│   │   └── mcp-configs/                 # MCP configurations
│   ├── copilot/
│   │   ├── copilot-instructions/        # Instruction templates
│   │   ├── workflow-examples/           # Cloud agent workflow examples
│   │   └── agent-mode/                  # Agent mode examples
│   ├── skills/                          # Agent Skills example (Cursor + Copilot)
│   │   ├── README.md                    #   The load paths explained
│   │   └── add-endpoint/SKILL.md        #   A tiny procedure skill
│   └── comparison/                      # Side-by-side examples
└── tutorials/
    ├── cursor-setup.md                  # Cursor installation guide
    ├── copilot-setup.md                 # Copilot installation guide
    ├── cursorrules-guide.md             # Cursor project rules reference
    ├── copilot-instructions-guide.md    # Instructions file reference
    ├── cursor-cookbook-recipes.md       # Section 7.2 recipes 1-6
    ├── github-spark.md                  # Section 7.3 Spark (retired) + mission control
    └── choosing-tool.md                 # Migrating between the tools
```

`linkforge/src/` is a complete implementation. It is not a scaffold with blanks. The one `TODO` in `src/main.py` (the authentication dependency) is deliberate. In Section 7.6, Phase 2 Step 2, you prompt Cursor to resolve that item.

## Hands-on lab at a glance

You build LinkForge in the four phases of Section 7.6:

1. Scaffold the FastAPI service in Cursor's agent chat.
2. Extend it with Redis caching and click analytics.
3. Generate and run the test suite.
4. Hand deployment to the Copilot cloud agent through a GitHub issue.

The stack is FastAPI, PostgreSQL, Redis, Docker, and GitHub Actions. The Section 7.7 challenge is at the end of the lab README.

## Quick Reference

### Cursor Shortcuts
| Action | Mac | Windows |
|--------|-----|---------|
| Agent chat | Cmd+I | Ctrl+I |
| Send the selection to the agent (replaces Inline Edit) | Cmd+K | Ctrl+K |
| Add selection to the current chat | Cmd+L | Ctrl+L |
| Start a new agent with the selection | Cmd+Shift+L | Ctrl+Shift+L |
| Open the Agents Window | Command Palette, "Open Agents Window" | Command Palette, "Open Agents Window" |
| Tab Autocomplete | Tab | Tab |

> Cursor's shortcuts and panel layout change between releases. Check [cursor.com/docs](https://cursor.com/docs) for the current layout.

### Copilot Modes (VS Code)
| Mode | Trigger | Autonomy Level |
|------|---------|----------------|
| Ask | Mode picker in the Chat view (Ctrl+Cmd+I on Mac, Ctrl+Alt+I on Windows) | Read-only |
| Agent | Mode picker, or Shift+Cmd+I / Ctrl+Shift+I to open chat in agent mode | Autonomous in-IDE |
| Plan | Mode picker, or start the prompt with `/plan` | Plans before code is touched |
| Cloud agent | Assign a GitHub Issue to Copilot | Autonomous, async on GitHub |

Edit mode, the book's middle step between Ask and Agent, is not available in current VS Code (see "Current tool behavior" above).

## Prerequisites

- Cursor IDE installed (a standalone editor built on VS Code)
- A GitHub Copilot plan that includes the cloud agent for Phase 4. Any plan except Copilot Free works. As of November 7, 2026, GitHub's Copilot in the cloud policy controls the cloud agent. It is on by default for Business and Enterprise seats. An administrator can turn it off. Usage is billed in GitHub AI Credits.
- Python 3.11+, and Node.js for the `npx`-launched MCP servers in `code-examples/`
- Docker and Docker Compose
- Git configured with GitHub authentication
- An Azure subscription for the Phase 4 deployment. Azure Container Registry and Azure Container Instances bill while they exist. The lab's Teardown step removes them.

## Navigation

- **Previous**: [Chapter 6 - Intent-First Development: Mastering Google Antigravity and the Antigravity CLI](../chapter-06/README.md)
- **Next**: [Chapter 8 - Constitutional Coding: Mastering Claude Code](../chapter-08/README.md)

Also relevant: [Chapter 5 - The Architecture of Intent: Mastering Kiro](../chapter-05/README.md), the third dedicated AI development environment compared in Section 7.4.
