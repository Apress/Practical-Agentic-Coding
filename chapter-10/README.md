# Chapter 10: Orchestrating Multiple AI Agents: Team Coordination

Agent definitions, hooks, and labs for Chapter 10.

> **ASH install (as of October 31, 2026).** Install ASH with an interpreter
> pin, as ASH's install guide shows:
> `pipx install --python python3.12 'automated-security-helper[cdk] @ git+https://github.com/awslabs/automated-security-helper.git@v3'`
> Any Python from 3.10 to 3.14 works. Without the pin, pipx or uv can pick
> Python 3.15, and the install fails there. Install from GitHub only. The PyPI
> package named `automated-security-helper` is not ASH.

## What's here

```text
chapter-10/
├── README.md            # This file
├── code-examples/       # Agent definitions and hooks used by the main lab (Sections 10.5, 10.6)
│   ├── agents/          # security-ash-agent, documentation-agent, team-manager, python-impl
│   ├── fixtures/        # security_config.py, the seeded finding for the Phase 5 feedback loop
│   ├── hooks/           # validate-security-commands.sh, pre-commit-security-scan.sh
│   └── quality-gates-settings.json
├── challenge-lab/       # Debugging with competing hypotheses (Section 10.8)
│   ├── starter/         # Three services with a seeded race condition, logs, findings board
│   └── solution/        # Answer key and grading rubric (read after, not before)
└── hands-on-lab/        # BONUS: manager, peer, and blackboard coordination with the Anthropic Python SDK + Redis
```

## What you do

The main lab (Section 10.7) runs in Claude Code. It does not run in this repo.
You install agents into your own project's `.claude/` directory. Then you
orchestrate them from a Claude Code session. This repo supplies the files you
copy in.

1. Read Chapter 10, Sections 10.1 through 10.6.
2. Follow the lab in Section 10.7. Copy the agent definitions, the hook script,
   and the lab fixture from [code-examples/](./code-examples/) into your project.
   [code-examples/README.md](./code-examples/README.md) describes each file.
3. Try the challenge lab: [challenge-lab/README.md](./challenge-lab/README.md) (Section 10.8).
4. Optional: work through the bonus SDK lab in
   [hands-on-lab/README.md](./hands-on-lab/README.md). You write three of the
   chapter's coordination patterns as Python code:
   - a manager agent (hierarchical, Section 10.2)
   - direct peer messaging (Section 10.3)
   - the blackboard (Section 10.6)

When to use each orchestration pattern and why: Chapter 10, Section 10.2.

## The agent team you assemble (Section 10.7)

| Agent | Role | Model | Where it comes from |
|-------|------|-------|---------------------|
| code-architect | Designs implementation blueprints | Sonnet | `feature-dev` plugin (Section 10.4) |
| code-reviewer | Reviews with confidence scoring | Sonnet | `feature-dev` plugin (Section 10.4) |
| python-impl | Implements FastAPI code | Sonnet | `code-examples/agents/python-impl.md` |
| qa-expert | Writes the tests | Sonnet | VoltAgent collection, `categories/04-quality-security/qa-expert.md` (Section 10.4) |
| security-ash-agent | Runs ASH and Bandit scans | Sonnet | `code-examples/agents/security-ash-agent.md` |
| documentation-agent | Generates API docs from code | Haiku | `code-examples/agents/documentation-agent.md` |
| team-manager | Discovers agents, decomposes tasks, coordinates | Opus | `code-examples/agents/team-manager.md` |

[code-examples/README.md](./code-examples/README.md) lists where the repo's
agent and hook files differ from the printed listings.

## Prerequisites

For the main lab (Sections 10.7 and 10.8):

- Claude Code CLI, signed in.
- A Python project to run the auth-feature scenario against. Any FastAPI
  project works. If you don't have one,
  [code-examples/README.md](./code-examples/README.md) shows a two-minute
  throwaway skeleton.
- `jq` on PATH. The security validation hook uses it.
- `black` for the format-on-edit hook (`pip install black`). Without it, the
  hook does nothing.
- Bandit or AWS Automated Security Helper (ASH), so the security agent has a
  real scanner to call. `pip install bandit` is enough. The Phase 5 feedback
  loop needs the scan to flag the hardcoded secret seeded by
  `code-examples/fixtures/security_config.py`. To install ASH, see the ASH
  install note at the top of this file.
- On Windows, WSL. The hook scripts are bash (see
  [code-examples/README.md](./code-examples/README.md)).
- For the Section 10.8 challenge, turn on Claude Code's experimental agent
  teams feature (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`; see
  [challenge-lab/README.md](./challenge-lab/README.md)).

**Time required**: 90-120 minutes, covering Sections 10.7 and 10.8 together.

The bonus SDK lab takes a separate 3-4 hours. It has its own prerequisites:
Docker for Redis and an Anthropic API key. See
[hands-on-lab/README.md](./hands-on-lab/README.md).

## Next steps

- **Chapter 11**: Extend these coordination patterns into DevOps and infrastructure
- **Chapter 12**: Security and governance for multi-agent systems
