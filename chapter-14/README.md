# Chapter 14: Migration Strategies: From Traditional to Agentic Development

This directory holds the Chapter 14 worksheets and labs.

- The assessment worksheets support Sections 14.3 and 14.8.
- The hands-on lab installs AI-DLC into a Claude Code project. You then run a full Inception-Construction cycle for a REST API feature.

The migration phases, the assessment model, and the framework comparison are in the book. For when to migrate and why: Chapter 14, Sections 14.2 to 14.7.

> **Updates to the book (as of November 7, 2026).** The AI-DLC repository makes Workflows 2.x its default `main` branch. The Section 14.9 lab still uses the pinned 1.x rules (v1.0.1). GitHub Spec-Kit adds a `converge` step and runs its commands as `/speckit-*` skills. See "External frameworks" below for details.

## What this chapter ships

The lab uses the AI-DLC rules that AWS Labs publishes (see External frameworks below). This repository does not copy that framework code. This directory holds the assessment documents and the current, tested lab instructions:

```text
chapter-14/
├── README.md                          # This file
├── migration-readiness-checklist.md   # Which Part III patterns you already have (Section 14.3)
├── skills-matrix.md                   # Skills gap analysis by migration phase (Section 14.8)
├── hands-on-lab/                      # Section 14.9: AI-DLC setup + lab prompts
│   ├── README.md                      #   pinned 1.x install steps, tested prompts
│   ├── UPDATES-AIDLC-2.0.md           #   what Workflows 2.0 changed + how to run the lab on it
│   └── prompts/                       #   Inception and Construction bolt prompts
│       ├── 01-inception-bolt.md
│       └── 02-construction-bolt.md
└── challenge-lab/                     # Section 14.10: CI/CD wiring
    ├── README.md                      #   challenge, success criteria, hints
    └── starter/
        └── .github/workflows/
            └── aidlc-operations.yml   #   pipeline scaffold with numbered TODOs
```

## Assets

- **[migration-readiness-checklist.md](./migration-readiness-checklist.md)**: the fill-in pattern inventory from Section 14.3. Fill it in before you plan. It shows which Part III patterns you already partly have.
- **[skills-matrix.md](./skills-matrix.md)**: the skills gap worksheet from Section 14.8. Each skill maps to the migration phase that needs it and the chapter that teaches it. It also lists what developers do NOT need to learn.
- **[hands-on-lab/](./hands-on-lab/)**: the Section 14.9 lab. Install AI-DLC 1.x into a Claude Code project. Then run a full Inception-Construction cycle for a notification-preferences API.
  - Time: 60-90 minutes.
  - Needs: Claude Code CLI and Python 3.11+. Docker is optional.
- **[challenge-lab/](./challenge-lab/)**: the Section 14.10 extension. It is a GitHub Actions scaffold with numbered TODOs. You wire the security gate, cost gate, and canary deploy into an Operations pipeline.

## External frameworks

Section 14.4 compares three methodologies. Two of them live in their own public repositories.

### AWS AI-DLC

Repository: [github.com/awslabs/aidlc-workflows](https://github.com/awslabs/aidlc-workflows) (MIT-0). It has three phases (Inception, Construction, Operations) and two implementations.

As of November 7, 2026:

- **Workflows 2.x** is the executable workflow engine. It is the default `main` branch and installs with a native installer.
- **Workflows 1.x** is the rules files, with broad tool support. It lives on the `v1` branch. The repository keeps that branch for existing installations and maintenance. Its rules zips stay on the Releases page as `v1.x` assets.
- **The Section 14.9 lab uses the pinned v1.0.1 rules release.** That release stays downloadable.

For the tested install steps, see [hands-on-lab/README.md](./hands-on-lab/README.md). For the 2.x path, see [hands-on-lab/UPDATES-AIDLC-2.0.md](./hands-on-lab/UPDATES-AIDLC-2.0.md).

### GitHub Spec-Kit

Repository: [github.com/github/spec-kit](https://github.com/github/spec-kit) (MIT).

As of November 7, 2026:

- Its core Spec-Driven Development flow runs a `converge` step after `implement`. Section 14.4 does not cover this step.
- It runs its commands as `/speckit-*` skills in your agent's chat. Take the current workflow from its [README](https://github.com/github/spec-kit/blob/main/README.md).
- It bundles two optional processes as extensions:
  - bug fixing: `specify extension add bug`
  - idea assessment: `specify extension add assess`
- Idea assessment ends in a go, clarify, or stop decision before you write a spec. This is close to the front-end work of AI-DLC Inception.
- Spec-Kit has no Operations phase, so Table 14.3 holds.
- Version 1.3.0 removed the core `taskstoissues` command. To turn tasks into GitHub issues, install the bundled `github` extension (`specify extension add github`). See the [CHANGELOG](https://github.com/github/spec-kit/blob/main/CHANGELOG.md).

### Kiro

Kiro Spec-Driven Development is the third option. It is built into the Kiro IDE. Chapter 5, "The Architecture of Intent: Mastering Kiro," covers it (kiro.dev/docs/specs).

### Cost and usage features

The Part II tools have enterprise cost and usage features:

- Kiro credit pooling and usage export
- Copilot usage metrics
- Claude Code spend controls

See the "Go further" lists for [Kiro](../chapter-05/README.md#go-further-with-kiro), [Cursor and GitHub Copilot](../chapter-07/README.md#go-further-with-cursor-and-github-copilot), and [Claude Code](../chapter-08/README.md#go-further-with-claude-code).

## How to use this chapter's assets

1. Bring your five readiness scores forward from [chapter-13/readiness-rubric.md](../chapter-13/readiness-rubric.md).
2. Run [migration-readiness-checklist.md](./migration-readiness-checklist.md) to inventory which patterns you already have.
3. Use [skills-matrix.md](./skills-matrix.md) to plan training per phase.
4. Do the Section 14.9 lab in [hands-on-lab/README.md](./hands-on-lab/README.md). It uses the pinned AI-DLC 1.x rules and tested prompts.
5. Extend it into CI/CD with [challenge-lab/README.md](./challenge-lab/README.md) and its starter workflow.

## Prerequisites

- **Assessment documents**: a text editor.
- **Section 14.9 lab**: the Claude Code CLI and Python 3.11+. Docker is optional, for a real test database. SQLite works too (see the lab README).
- **Section 14.10 challenge lab**: everything the lab needs, plus:
  - a GitHub repository where you can run Actions
  - a repository secret that holds an API key or workload-identity credential for the headless agent
