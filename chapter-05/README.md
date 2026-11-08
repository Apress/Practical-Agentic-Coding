# Chapter 5: The Architecture of Intent: Mastering Kiro

## What's Here

This folder holds the materials for Chapter 5. The chapter uses Kiro, from AWS. You get:

- The starter project for the "Daily Briefing" hands-on lab
- Reference copies of the specs and steering files the author's Kiro session produced
- Reusable hook and MCP configuration examples
- Three practice exercises with answer keys
- A challenge lab with the four exercises printed at the end of the chapter

Nothing here runs on its own. In this tool chapter, you drive Kiro and Kiro writes the code. Use these files as inputs to Kiro, and compare Kiro's output against them.

> **Current tool behavior (as of November 7, 2026).** These work differently today than the book describes:
>
> - Kiro's hook format
> - Three of the AWS MCP servers the chapter lists
> - Bedrock's model access
> - App Runner's availability for new accounts
>
> The lab README opens with the list of differences. Where it disagrees with the book, follow the lab README.

## Go further with Kiro

These capabilities build on the spec-driven workflow from Chapter 5. Plans, pricing, and availability change. Each item links to the vendor page with current details.

- **Credit sharing for Kiro Enterprise.** Enterprise admins pool the monthly credits of every seated user into one shared pool. Credits a light user leaves unused cover a heavy user. Admins set limits per user, per group, and per profile in the Kiro console under Access management > Credit sharing. Switching existing individual subscriptions to credit sharing cannot be undone. Credits stay the unit of cost. Introduced in November 2026. [Kiro docs: credit pooling](https://kiro.dev/docs/enterprise/credit-pooling/)
- **Usage metrics over OpenTelemetry.** Kiro Enterprise account admins can send per-user adoption, engagement, and credit use by model to any OTLP-compatible platform, such as Amazon CloudWatch, Datadog, Elastic, Honeycomb, OpenSearch, or your own collector. You set up one account-level export in the Kiro console. Kiro delivers the metrics daily, alongside the per-user CSV activity report. Introduced in September 2026. [Kiro docs: OpenTelemetry export](https://kiro.dev/docs/enterprise/monitor-and-track/user-activity/opentelemetry/)
- **Workflows.** A workflow is a reusable multi-step plan stored in `.kiro/workflows/`. Kiro shows you the plan before anything runs. It then runs each step in its own background agent session. You can pause, resume, stop, or steer each session while you keep working in the parent chat. Workflows are off by default. They use more tokens, and so more credits, than a single session. Turn them on with the `kiroAgent.workflows.enabled` setting in the IDE, `/settings` > Features in the CLI, or the Kiro Web settings. Introduced in Kiro IDE 1.2, Kiro CLI 2.26, and Kiro Web (September 2026). [Kiro docs: Workflows](https://kiro.dev/docs/workflows/)
- **Kiro CLI 3.0.** `kiro-cli` ships as one standalone binary. It starts interactive sessions on the V3 agent harness by default. Existing V2 users are asked first, and `kiro-cli --v2` keeps the V2 harness. It upgrades V2 custom agents automatically and keeps a `.json.bak` copy of each. Release 3.0 retired the Classic interface, the macOS desktop app, and inline shell autocomplete. It also removed the `autocomplete`, `inline`, `translate`, `theme`, and `dashboard` commands. Introduced in Kiro CLI 3.0 (November 2026). [Kiro CLI 3.0 changelog](https://kiro.dev/changelog/cli/3-0/)
- **Memory.** Kiro can carry what it learns about a repository into later chat sessions. This covers commands, conventions, corrections, debugging insights, and approaches already ruled out. Memories are stored locally for your user account. The Kiro IDE and local V3 sessions of the Kiro CLI on the same machine share them. In the IDE, review them in the Memories view. Pick Use and learn, Use but don't learn, Use only, or Off (the default) in the Kiro Agent: Memory setting. In the CLI, use `/memories` with read and write, read only, or off. Steering files stay the place for rules you want under version control. Introduced in Kiro CLI 2.29 and Kiro IDE 1.4 (October 2026). [Kiro docs: Memory](https://kiro.dev/docs/memory/)
- **Enterprise sign-in controls and governance.** On managed devices, admins can limit sign-in to IAM Identity Center, prefill the start URL and Region, and add an IT help link through the admin-protected `managed-settings.json`. In the Kiro console, admins keep an approved model list with a default model. They can allow MCP servers only from a registry, or turn MCP off. They can turn off web search and web fetch. They decide whether users can start cloud sessions or generate API keys. Introduced in Kiro IDE 1.2 (September 2026). [Kiro docs: governance](https://kiro.dev/docs/enterprise/governance/)
- **Local command sandbox and autonomous mode.** Kiro can run the agent's shell commands and their child processes inside an operating-system sandbox on your machine. Outbound network can be blocked, limited to common development hosts, or open. The sandbox is off by default. Turn it on from **Sandbox** in the IDE status bar or with `/sandbox` in the CLI (Linux needs `bwrap`). In the CLI, `/autonomous on` runs a local task without per-command approval and turns the sandbox on first. This brings Kiro Web's autonomous execution to local sessions. The sandbox lowers risk but does not fully isolate. Keep reviewing what the agent proposes. Introduced in Kiro IDE 1.3 and Kiro CLI 2.31 (October 2026). [Kiro docs: sandbox](https://kiro.dev/docs/sandbox/)
- **Approve for me.** This works in interactive local V3 sessions of the Kiro CLI. Your deny, ask, and allow rules apply first. Then Approve for me approves routine actions, blocks risky ones, and asks you about the rest. Turn it on per workspace under `/permissions` > Policies. Introduced in Kiro CLI 2.36 (October 2026). [Kiro docs: Approve for me](https://kiro.dev/docs/permissions/#approve-for-me)

## What You Do

1. Install and authenticate Kiro (`tutorials/kiro-setup.md`).
2. Work the three practice exercises in `hands-on-lab/exercises/`. Do them before the lab.
3. Run the eight-phase lab in `hands-on-lab/README.md`. It builds the Daily Briefing agent from vibe prompt to deployed app.
4. Try the open-ended extensions in `challenge-lab/README.md`.

## Map to the Book

| Repo path | Book section |
|-----------|--------------|
| `tutorials/kiro-setup.md` | Section 5.5, Exercise 5.1 (installation and configuration) |
| `tutorials/sdd-methodology.md` | Section 5.2 (Spec-Driven Development) |
| `tutorials/steering-files-guide.md` | Section 5.4 (Agent Steering) |
| `code-examples/steering-files/` | Section 5.4 (foundational steering files) |
| `code-examples/specs/` | Section 5.2 (spec artifacts) |
| `code-examples/hooks/` | Section 5.5 (Kiro Hooks) and Exercise 5.1 |
| `code-examples/mcp-configs/` | Section 5.6 (MCP server configuration), Listing 5-1 |
| `hands-on-lab/` | Section 5.7 (Hands-on Lab: Build "Daily Briefing" Agent) |
| `hands-on-lab/prompts/` | Section 5.7, Listings 5-2 to 5-4 |
| `daily-briefing-agent/` | Section 5.7 (the author's reference specs) and Section 5.8 (the `.kiro/` directory you commit) |
| `daily-briefing-agent-notes/` | Section 5.7, Phase 1 (what vibe mode produced) |
| `challenge-lab/` | Chapter exercises (end of chapter) |

## Learning Objectives

After you work through this chapter's materials, you can:

- Build with Kiro hands-on
- Run the Spec-Driven Development (SDD) loop
- Write EARS acceptance criteria
- Keep "Vibe" (outcome-led intent) separate from "Spec" (technical constraints)
- Set up Kiro Powers, Hooks, and lifecycle events
- Wire Kiro to local databases and external APIs over MCP
- Build a working "Daily Briefing" agent through an iterative lab
- Commit the generated `.kiro/` artifacts
- Review agent output like a teammate's PR

## Terms Used in the Lab

One line each, with the book section that explains the term.

- **Spec-Driven Development (SDD)**: the spec files (`requirements.md`, `design.md`, `tasks.md` under `.kiro/specs/`). Section 5.2.
- **Vibe and Spec**: outcome-led intent, and explicit, measurable constraints. Section 5.2. Exercise 1 drills it.
- **EARS**: the "WHEN [condition] THE SYSTEM SHALL [behavior]" shape Kiro uses for acceptance criteria. Section 5.7, Phase 2.
- **Steering files**: `product.md`, `tech.md`, `structure.md`, and `AGENTS.md`, read on every interaction. Section 5.4.
- **Context tiers**: global, local, and file context. Section 5.3.
- **Powers**: installable capability bundles. Section 5.5.
- **Hooks**: event-driven automations. Section 5.5.
- **MCP servers**: how Kiro reaches databases and AWS services. Section 5.6.

## Directory Structure

```text
chapter-05/
├── README.md                              # This file
├── challenge-lab/
│   └── README.md                          # The four end-of-chapter exercises
├── hands-on-lab/
│   ├── README.md                          # Eight-phase lab walkthrough
│   ├── daily-briefing-agent/              # Lab starter project (you build here)
│   │   ├── .kiro/
│   │   │   ├── steering/                  # product.md, tech.md, structure.md
│   │   │   ├── specs/tech-news-aggregator/  # requirements.md, design.md, tasks.md
│   │   │   ├── hooks/                     # test-coverage, docs-sync (pre-1.0 hook format)
│   │   │   └── settings/mcp.json          # MCP server config
│   │   ├── src/config.py                  # Configuration module (given), plus src/__init__.py
│   │   ├── tests/conftest.py              # Shared pytest fixtures (given)
│   │   ├── AGENTS.md                      # Agent directives
│   │   ├── Makefile                       # Development shortcuts
│   │   ├── pytest.ini                     # Test markers and options
│   │   ├── requirements.txt               # Python dependencies
│   │   ├── .env.example                   # Environment template
│   │   ├── .gitignore
│   │   └── README.md                      # Project README
│   ├── prompts/                           # The book's lab prompts (Listings 5-2 to 5-4) as paste-ready files
│   └── exercises/                         # Practice exercises with answer keys
│       ├── exercise-1-sdd-basics.md
│       ├── exercise-2-steering-files.md
│       └── exercise-3-hooks-powers.md
├── daily-briefing-agent/                  # REFERENCE artifacts from the author's run
│   ├── .kiro/                             # Full generated specs, steering, hooks
│   ├── .gitignore                         # From the Phase 8 cleanup prompt
│   └── README.md                          # How to use these as a comparison
├── daily-briefing-agent-notes/            # Phase 1 "vibe" output from the author's run
│   ├── README.md
│   ├── concept-exploration.md
│   ├── mvp-features.md
│   ├── persona-voice-examples.md
│   └── tech-stack-considerations.md
├── code-examples/
│   ├── steering-files/                    # Steering file templates
│   ├── mcp-configs/                       # MCP configuration examples
│   ├── hooks/                             # Hook configuration examples
│   └── specs/                             # Spec document templates
└── tutorials/
    ├── kiro-setup.md                      # Installation and setup
    ├── sdd-methodology.md                 # The SDD workflow
    └── steering-files-guide.md            # Steering file quick reference
```

### Two Daily Briefing directories, on purpose

`hands-on-lab/daily-briefing-agent/` is the **starter**. Its specs are short. Its `src/` holds only `config.py` (and `__init__.py`). You and Kiro write everything else during the lab.

`daily-briefing-agent/` at the chapter root is the **reference**. It holds the full `requirements.md`, `design.md`, and `tasks.md` that the author's Kiro session produced. Compare your specs against it after each phase. Read `daily-briefing-agent/README.md` before you open it.

`daily-briefing-agent-notes/` holds the markdown files Kiro generated on its own during the Phase 1 vibe prompt.

## Hands-On Lab: Daily Briefing Agent

The lab builds a tech news aggregator that:

- **Aggregates tech news** from Hacker News
- **Generates witty summaries** using Amazon Bedrock (Claude models)
- **Writes daily briefings** to markdown files named `briefing_YYYY-MM-DD.md`
- **Deploys to AWS** using App Runner, Aurora PostgreSQL, and S3

### Lab Phases

1. **Vibe prompt**: Set the creative persona and intent.
2. **Spec definition**: Add the technical constraints.
3. **Iterative refinement**: Shape the implementation plan through conversation.
4. **Hook configuration**: Automate test coverage and documentation.
5. **Powers installation**: Add AWS infrastructure capability.
6. **MCP configuration**: Connect the AWS MCP servers.
7. **Task execution**: Build and test the application locally.
8. **Iterative improvements**: Change a deployment decision, then update the specs to match.

## Prerequisites

- Kiro installed ([installation guide](https://kiro.dev/docs/getting-started/installation/))
- An AWS account that can use Amazon Bedrock (Claude models need a one-time use-case form per account), Aurora PostgreSQL, App Runner (or Amazon ECS Express Mode if your account is new to App Runner), S3, and Secrets Manager
- AWS CLI configured with a profile Kiro can use
- Node.js and npm (the `npx`-launched MCP servers, including the local PostgreSQL Toolbox server, need them)
- [uv](https://docs.astral.sh/uv/) (the AWS MCP servers launch through `uvx`)
- Docker Desktop running. LocalStack needs it. So do an optional local Postgres container and the GitHub MCP server, if you use them.
- A LocalStack auth token. As of November 7, 2026, LocalStack needs one (see the lab README).
- Python 3.11 or newer. The book's spec constraint pins Python 3.13. Any version from 3.11 up runs the starter scaffold.

## Quick Start

1. **Install Kiro**: Follow the [installation guide](https://kiro.dev/docs/getting-started/installation/).
2. **Authenticate**: Follow the [authentication guide](https://kiro.dev/docs/getting-started/authentication/).
3. **Copy the starter**: Copy `hands-on-lab/daily-briefing-agent/` to a working directory of your own. This keeps your changes separate from the repo.
4. **Open the folder in Kiro**: Select File > Open Folder, then select the copy.
5. **Trust the folder**: Run **Workspaces: Manage Workspace Trust**, choose **Trust Folder**, then run **Developer: Reload Window**. Kiro opens a folder you have not trusted in Restricted Mode. In Restricted Mode it skips the folder's steering, MCP configuration, and hooks.
6. **Check the panels**: The Kiro (ghost) icon in the left rail should show SPECS and AGENT HOOKS. Powers have their own panel, the ghost icon with a lightning bolt.
7. **Follow the lab**: `hands-on-lab/README.md`.

## Practice Exercises

Work these before the lab. Each one ends with an answer key or sample solutions.

1. **[SDD basics](hands-on-lab/exercises/exercise-1-sdd-basics.md)**: Sort requirements into Vibe and Spec. Then rewrite the vague ones as EARS-notation acceptance criteria.
2. **[Steering files](hands-on-lab/exercises/exercise-2-steering-files.md)**: Read the lab starter's steering files. Then write your own `product.md`, `tech.md`, and `structure.md` for a different project.
3. **[Hooks and Powers](hands-on-lab/exercises/exercise-3-hooks-powers.md)**: Analyze two hook configurations. Design four of your own. Pick the Powers a project would need.

## Chapter Exercises

These are the four exercises printed at the end of Chapter 5. They are open-ended. They build on the finished lab. They have no answer keys. Instructions and success criteria are in [`challenge-lab/README.md`](challenge-lab/).

1. **Modify the briefing agent**: Change the deployment model from App Runner to ECS, ALB, and CloudFront. Edit the requirements, not the templates.
2. **Vibe check**: Swap the "witty journalist" persona for an "academic researcher". Note what changes in the code structure and the output.
3. **Security hook**: Build a hook that scans staged changes for security issues before each commit.
4. **Agent steering**: Have Kiro generate a steering document for the project. Then add rules and watch how its output changes.

## Related Resources

- [Kiro documentation](https://kiro.dev/docs/)
- [Kiro Powers](https://kiro.dev/powers/)
- [AWS MCP servers](https://awslabs.github.io/mcp)
- [Amazon Bedrock documentation](https://docs.aws.amazon.com/bedrock/)

## Navigation

- **Previous**: [Chapter 4 - Recent Advances in AI and Autonomous Agents](../chapter-04/)
- **Next**: [Chapter 6 - Intent-First Development: Mastering Google Antigravity and the Antigravity CLI](../chapter-06/)
