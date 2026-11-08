# Hands-on Lab: AI-DLC Setup for a REST API Feature (Section 14.9)

In this lab you use AI-DLC and Claude Code to build a notification-preferences
API for users. You will:

1. Install the workflow.
2. Run an Inception bolt. Its directed questions find the requirements you missed.
3. Approve the artifacts.
4. Run a Construction bolt, test-first.

> **Tested versions.** The prompts and setup steps here are the tested
> versions. Where they differ from the book text, follow this directory.
> AI-DLC changes faster than a printed page. The install steps are tested
> against the pinned v1.0.1 download. Its archive layout and the copy
> commands (bash and Windows PowerShell) work as written.

**Stack**: Claude Code + AI-DLC 1.x rules + Python/FastAPI + pytest.
**Time**: plan on 60-90 minutes.
**Prerequisites**: Claude Code CLI and Python 3.11+. Docker is optional, for a
real test database. Without Docker, point Construction at SQLite. The lab works
the same way.

## Which AI-DLC version?

AWS Labs maintains two implementations of the AI-DLC methodology. **They
install and run differently. Do not mix them.**

| | Workflows 1.x (this lab) | Workflows 2.x |
|---|---|---|
| What it is | Markdown rules the agent reads | Executable workflow engine (deterministic engine + verification stages) |
| Install | Copy the rules zip into your tool's rules or steering location | Native installer (`install.sh` or `install.ps1`), then `aidlc config --harness <name>` in the project |
| Tools | Kiro, Amazon Q Developer, Cursor, Cline, Claude Code, GitHub Copilot, OpenAI Codex | Claude Code, Kiro IDE and Kiro CLI, Codex CLI, Cursor, opencode, GitHub Copilot (check the README for the current matrix) |
| Where it lives | `v1` branch (kept for existing installations and maintenance) + the `v1.x` release assets | `main` branch (the default) + the Releases page |

The AI-DLC repository makes 2.x its default branch. It keeps 1.x on the `v1`
branch. The pinned v1.0.1 download below still works.

This lab uses **1.x**. It installs in minutes on every tool in Part II. Inception,
Construction, Bolts, and human approval gates work the same way in 2.0. To run
the lab on 2.0, see [UPDATES-AIDLC-2.0.md](./UPDATES-AIDLC-2.0.md). For the
latest install steps, see the vendor's own guide in the
[AI-DLC repository](https://github.com/awslabs/aidlc-workflows).

## Setup (Workflows 1.x, Claude Code)

Work in an empty scratch directory. The scenario mentions "an existing user
service." You do not need one. Inception uses the context you describe, and
Construction builds the endpoints from scratch. A scratch project also keeps
AI-DLC's `CLAUDE.md` away from a real one.

```bash
mkdir aidlc-lab && cd aidlc-lab
git init
```

Download a pinned 1.x rules release. Always pin the version. The
`releases/latest` link points at the 2.x installer. It does not point at a rules zip.

```bash
curl -L -o aidlc-rules.zip https://github.com/awslabs/aidlc-workflows/releases/download/v1.0.1/ai-dlc-rules-v1.0.1.zip
unzip aidlc-rules.zip -d ~
```

The archive has its own `aidlc-rules/` top-level folder. Unzipping to `~` gives
you `~/aidlc-rules/` with two rule sets inside. Install them into your project root:

```bash
cp ~/aidlc-rules/aws-aidlc-rules/core-workflow.md ./CLAUDE.md
mkdir -p .aidlc-rule-details
cp -R ~/aidlc-rules/aws-aidlc-rule-details/* .aidlc-rule-details/
```

Delete the zip (`rm aidlc-rules.zip`). You no longer need it, and it should not
end up in your commits.

On Windows, run the same setup in PowerShell (5.1 or 7):

```powershell
mkdir aidlc-lab
cd aidlc-lab
git init
Invoke-WebRequest -Uri https://github.com/awslabs/aidlc-workflows/releases/download/v1.0.1/ai-dlc-rules-v1.0.1.zip -OutFile aidlc-rules.zip -UseBasicParsing
Expand-Archive aidlc-rules.zip -DestinationPath $HOME
Copy-Item "$HOME\aidlc-rules\aws-aidlc-rules\core-workflow.md" ".\CLAUDE.md"
New-Item -ItemType Directory -Force -Path ".aidlc-rule-details"
Copy-Item "$HOME\aidlc-rules\aws-aidlc-rule-details\*" ".aidlc-rule-details\" -Recurse
Remove-Item aidlc-rules.zip
```

Expected project structure:

```text
aidlc-lab/                       # (the book calls this my-project/)
├── CLAUDE.md                    # AI-DLC core workflow rules
└── .aidlc-rule-details/         # Detailed phase rules
    ├── common/
    ├── inception/
    ├── construction/
    ├── extensions/
    └── operations/
```

Verify the install:

1. Start Claude Code.
2. Ask *"What instructions are currently active in this project?"*
3. Check that the answer describes AI-DLC's three phases.

> If you already have a `CLAUDE.md`, append `core-workflow.md` to it. Do not
> overwrite it. Or keep the lab in a fresh scratch project (recommended).

## Running the lab

**Scenario**: an existing user service needs notification preferences for
email, SMS, and push. The feature needs:

- three endpoints
- a schema change
- validation
- tests

1. Start the Inception bolt with [prompts/01-inception-bolt.md](./prompts/01-inception-bolt.md).
   AI-DLC asks you directed questions. Answer honestly. "I don't know" is a
   valid answer. It marks a requirements gap.
2. Review the Inception artifacts (requirements, design decisions). Read them
   before you approve them.
3. Run the Construction bolt test-first with [prompts/02-construction-bolt.md](./prompts/02-construction-bolt.md).
4. Verify with quality-gate hooks. One hook formats on every edit. Another runs
   the tests on task completion. These are the Chapter 10, Section 10.6
   patterns. The tested configs are in
   [../../chapter-10/code-examples/](../../chapter-10/code-examples/).
   1. Use `quality-gates-settings.json` as your `.claude/settings.json`.
   2. Copy `hooks/pre-commit-security-scan.sh` into `.claude/hooks/`. The
      `PreToolUse` entry in `quality-gates-settings.json` runs this script.
   3. Run `chmod +x` on the script.
   4. Install the tools: `pip install black bandit`, plus `jq` from your
      package manager.
      - The format-on-edit hook needs `jq` and `black` on PATH. Without them
        it does nothing.
      - The scan needs `jq` and `bandit`. If either is missing, it warns and
        skips. It does not block your commits.
   5. The test gate runs on task completion, so it needs Claude Code's task
      tools. On models newer than Opus 4.7, Sonnet 4.6, and Haiku 4.5, start
      Claude Code with `CLAUDE_CODE_ENABLE_TODO_TOOLS=1 claude`. See the
      Chapter 10 code-examples README.

When you finish, AI-DLC is installed and working, and you have a tested, shipped feature.

## Troubleshooting

- **Download 404s**: releases move. Open the [Releases page](https://github.com/awslabs/aidlc-workflows/releases).
  Find the current `v1.x` release and its `ai-dlc-rules-v1.x.zip` asset. Update the `curl` URL.
  The newest entries on that page are 2.x releases. They carry an installer instead of a rules zip.
  The 1.x entries are further down.
- **Claude doesn't mention AI-DLC when asked**: check that `CLAUDE.md` is at the
  project root you launched from. Check that `.aidlc-rule-details/` is next to it.
- **Kiro instead of Claude Code**: the same rules install as Kiro steering
  files. Run this from your project root, after the `unzip` step above:

  ```bash
  mkdir -p .kiro/steering
  cp -R ~/aidlc-rules/aws-aidlc-rules .kiro/steering/
  cp -R ~/aidlc-rules/aws-aidlc-rule-details .kiro/
  ```

  For other tools, see the README on the repository's [`v1` branch](https://github.com/awslabs/aidlc-workflows/tree/v1).
  It has the 1.x steps for Cursor, GitHub Copilot, Amazon Q, Cline, and Codex.
  It also has PowerShell and CMD variants. The `main` branch README covers 2.x only.
