# Chapter 10: Code Examples

Agent definitions, the security hook scripts, and a quality-gate settings file from Chapter 10.

The hands-on lab in Section 10.7 tells you to copy these files into your own
project. Nothing here runs on its own. Each file becomes part of a Claude Code
project's `.claude/` directory.

> **Claude Code behavior notes (as of November 7, 2026).** Two behaviors differ
> from what the printed listings suggest:
>
> - **Grep and Glob for subagents.** In a session started with plain `claude`
>   on macOS, Linux, or WSL, Claude Code gives a subagent the Grep and Glob
>   tools only when its `tools` line names them and leaves out Bash (or when
>   the main session already has them). `security-ash-agent.md` lists Bash. So
>   the agent searches with `grep` and `find` through Bash, and
>   `validate-security-commands.sh` blocks those commands. Expect a few
>   "Blocked" messages. The scanners still run, and the agent reads the flagged
>   files with Read.
> - **Task tools for the `TaskCompleted` gate.** The gate fires only in a
>   session that has Claude Code's task tools. They are on by default only on
>   Opus 4.7, Sonnet 4.6, Haiku 4.5, and earlier models. On newer models, start
>   Claude Code with `CLAUDE_CODE_ENABLE_TODO_TOOLS=1 claude` ("Task tool
>   availability" in the Claude Code tools reference). See
>   [Quality gate configuration](#quality-gate-configuration-section-106) below.
>
> For the latest behavior, see the Claude Code docs at code.claude.com/docs.

## Before you start: a project to run against

The lab needs a Python project for the agents to work in. Any FastAPI project
works. If you don't have one, this throwaway skeleton takes two minutes:

```bash
mkdir auth-lab && cd auth-lab && git init
python3 -m venv .venv && source .venv/bin/activate
pip install fastapi uvicorn pytest bandit black
mkdir -p src/auth tests
printf 'from fastapi import FastAPI\n\napp = FastAPI()\n' > src/main.py
touch src/__init__.py src/auth/__init__.py
```

This gives you:

- somewhere for the agents to write code
- `src/auth/` for the lab fixture you copy in during Phase 4
- pytest and bandit for the quality gates

Delete the directory when you finish the lab.

On Windows, run this lab under WSL. The hook scripts are bash. The formatting
hook also passes the edited file's path through `xargs`, which strips the
backslashes in native Windows paths. For a native setup, see the PowerShell
hooks in Claude Code's hooks documentation.

## Copying files into your project

Run every copy command below from your project's root (`auth-lab/` above). The
book prints these paths as `companion-repo/chapter-10/code-examples/...`.
`companion-repo` is wherever you cloned this repository. Set it once:

```bash
REPO=~/Practical-Agentic-Coding   # change if you cloned somewhere else
```

## Agent definitions (Section 10.5)

Copy these to `.claude/agents/` in your project:

```bash
mkdir -p .claude/agents
cp "$REPO"/chapter-10/code-examples/agents/security-ash-agent.md .claude/agents/
cp "$REPO"/chapter-10/code-examples/agents/documentation-agent.md .claude/agents/
cp "$REPO"/chapter-10/code-examples/agents/team-manager.md .claude/agents/
cp "$REPO"/chapter-10/code-examples/agents/python-impl.md .claude/agents/
```

| Agent | File | Model | Tools |
|-------|------|-------|-------|
| Security (ASH) | `agents/security-ash-agent.md` | Sonnet | Read, Grep, Glob, Bash (scoped) |
| Documentation | `agents/documentation-agent.md` | Haiku | Read, Glob, Grep, Write |
| Team Manager | `agents/team-manager.md` | Opus | Read, Glob, Grep, Agent, Write |
| Python Impl | `agents/python-impl.md` | Sonnet | Read, Write, Edit, Bash, Glob, Grep |

The design decisions behind the first three agents: Chapter 10, Section 10.5.

How these files compare to the printed listings:

- `documentation-agent.md` and `team-manager.md` match the printed listings
  exactly.
- `security-ash-agent.md` is the printed listing plus one instruction. It tells
  the agent to classify hardcoded credentials and signing secrets (Bandit
  B105/B106) as High. Bandit itself rates B105 Low. Without that line, the
  Phase 5 finding would not come back as the HIGH the book shows.
- `python-impl.md` is the tuned language specialist the lab uses in Phase 1.
  Use it if you would rather not install `python-pro` from the VoltAgent
  collection.

`security-ash-agent.md` and `documentation-agent.md` set `memory: project`, as
Section 10.5's design tables specify. `python-impl.md` does too.
`team-manager.md` has no memory, per its table.

Current Claude Code turns on Read, Write, and Edit for any subagent with a
`memory` field, so the agent can maintain its memory files. As a result, the
security and documentation agents get write tools that their `tools` lines do
not list. The "Never modify source code" instruction keeps the security agent
reporting instead of fixing. For a hard guarantee, remove the `memory` line
from that agent. It then loses its cross-session memory.

## Hook scripts (Sections 10.5 and 10.6)

```bash
mkdir -p .claude/hooks
cp "$REPO"/chapter-10/code-examples/hooks/validate-security-commands.sh .claude/hooks/
cp "$REPO"/chapter-10/code-examples/hooks/pre-commit-security-scan.sh .claude/hooks/
chmod +x .claude/hooks/*.sh
```

| Script | Purpose |
|--------|---------|
| `hooks/validate-security-commands.sh` | Restricts the security agent's Bash access to approved tools (ash, bandit, semgrep, checkov) |
| `hooks/pre-commit-security-scan.sh` | Runs Bandit before every `git commit` and blocks the commit on high-severity findings |

Requirements and behavior:

- Both scripts need `jq` on PATH.
- Both exit with status 2 to block.
- The pre-commit scan also needs `bandit` (`pip install bandit`). If either
  tool is missing, it prints a warning and skips the scan. It does not block
  every commit.

To see the block fire, try committing a file that contains
`subprocess.call(user_input, shell=True)` (Bandit B602, high severity). The
seeded lab fixture's hardcoded secret is a low-severity Bandit finding. It
goes through the security agent's review in Phase 5. This hook does not catch
it.

`validate-security-commands.sh` is the book's listing. Its allowlist checks
only the start of the command line. A chained command such as
`bandit -r . && <anything else>` still passes. Treat it as a guardrail for an
agent that follows its instructions. It is not a sandbox.

`pre-commit-security-scan.sh` reads the command from the hook input. It scans
only when the command contains `git commit`. Every other Bash command passes
straight through. This check backs up the `"if": "Bash(git commit*)"` filter in
the settings file. Claude Code documents that filter as best-effort: when it
cannot tell which commands a Bash call runs, it runs the hook anyway.

## Quality gate configuration (Section 10.6)

| File | Purpose |
|------|---------|
| `quality-gates-settings.json` | Example `.claude/settings.json` with PostToolUse formatting, a TaskCompleted test gate, and a PreToolUse pre-commit security scan |

This file is the Phase 3 listing from Section 10.7, unchanged.

1. Merge its `hooks` block into your project's `.claude/settings.json`. Do not
   overwrite the file, since you may already have settings there.
2. Copy `pre-commit-security-scan.sh` in from `hooks/`, as shown above. The
   `PreToolUse` entry references `.claude/hooks/pre-commit-security-scan.sh`.

The design of the security gate (run a scan, exit non-zero on critical
findings): Chapter 10, Section 10.6.

The `TaskCompleted` gate is an agent hook (`"type": "agent"`). Claude Code's
hooks documentation labels agent hooks experimental. If the gate does not fire,
or you want a gate that behaves the same on every run, swap that entry for a
command hook. Exit status 2 from a `TaskCompleted` hook keeps the task open and
feeds the message back to the agent. Either form fires only in a session that
has Claude Code's task tools (see the behavior notes at the top of this file).
The command form:

```json
{
  "hooks": {
    "TaskCompleted": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "pytest -q >/dev/null 2>&1; rc=$?; [ $rc -eq 0 ] || [ $rc -eq 5 ] || { echo 'Tests are failing: run pytest -q to see them' >&2; exit 2; }",
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

## Lab fixture (Section 10.7)

```bash
mkdir -p src/auth
cp "$REPO"/chapter-10/code-examples/fixtures/security_config.py src/auth/security_config.py
```

| File | Purpose |
|------|---------|
| `fixtures/security_config.py` | Auth configuration module with a hardcoded JWT signing secret (line 7), the seeded finding for the lab's feedback loop |

Copy this into your project before Phase 4 of the lab. The hardcoded secret
is the showcase finding for the Phase 5 feedback loop. What each scanner reports:

- Bandit 1.9 flags it as B105 (`Possible hardcoded password`, line 7) at Low
  severity.
- ASH 3.7 reports it twice. Its Bandit scanner repeats the Low B105. Its
  detect-secrets scanner raises a Critical `SECRET-SECRET-KEYWORD` on the same
  line, and that is what fails the ASH scan.
- The security agent classifies it as High, per the instruction its definition
  adds.

Leave the secret in place until the team manager routes the fix back to the
implementation agent. The exercise is built around that round trip.

## Verifying the setup

From a Claude Code session in your project:

1. Ask Claude to list the available agents. The four above should appear.
2. Address the security agent directly. Type `@`, pick `security-ash-agent`
   from the list, and add `review src/main.py`. Typing
   `@agent-security-ash-agent` by hand works too. A bare `@security-ash-agent`
   does not reach the agent.
3. Ask the security agent to run something outside the allowlist. The hook
   should block it. Claude Code runs hooks defined in a project agent file only
   after you trust the project folder, so accept the trust prompt when it
   appears.
4. Edit a Python file. Check that the PostToolUse hook reformats it.

## Bonus: SDK-based approach

The [`../hands-on-lab/`](../hands-on-lab/) directory holds a separate, optional
implementation. It uses the Anthropic Python SDK with Redis for inter-agent
messaging. You write the same coordination patterns (hierarchical,
peer-to-peer, blackboard) as Python code instead of Claude Code agent
definitions.

The native agent approach above is the chapter's primary lab and is faster to
set up. The SDK lab gives you more control over agent internals.
