# Antigravity CLI (agy) Quick Reference

This page lists the commands and config files for the `agy` terminal agent. It covers install, auth, session control, permissions, skills, and CI.

How the CLI works and when to use each mechanism: Chapter 6, Section 6.4.

For the latest flags and steps, see Google's own reference at [antigravity.google/docs/cli/reference](https://antigravity.google/docs/cli/reference) and run `agy changelog`.

`agy` has no task subcommands. There is no `agy fix`, `agy review`, or `agy scaffold`. You type prompts. Launch flags only set up the session. `agy` is Google's successor to the consumer Gemini CLI. See [Migrating from Gemini CLI](#migrating-from-gemini-cli).

> **Where agy differs from the printed book**
>
> - **`--mode` values.** Use `accept-edits`, `auto`, or `plan`. Leave the flag off for the default mode. agy 1.4.2 warns on `--mode default`.
> - **Starting with a prompt.** Use `agy -i "prompt"`. agy 1.4.2 rejects a bare `agy "prompt"` with "unexpected argument".
> - **Shift+Tab** also cycles through `auto`. See [Slash Commands](#slash-commands) for where `auto` appears.
> - **Sandbox (agy 1.4.4 and later).** `--sandbox` and `enableTerminalSandbox` do nothing where the sandbox is unavailable: Windows 10, Windows 11 before 24H2, or Linux hosts that block unprivileged user namespaces. `proceed-in-sandbox` then behaves like `request-review`.
> - **Print mode approvals.** In `-p` runs, shell commands that need approval are soft-denied. The run still exits 0, with a notice on stderr.
> - **As of November 7, 2026, `--dangerously-skip-permissions`** blocks commands on agy's system command denylist (agy 1.5.2 and later). In `-p` runs on a Gemini Enterprise account, it also denies terminal commands or file access outside the workspace that your administrator requires to be reviewed.
> - **As of November 7, 2026 (agy 1.5.0 and later), `-p` without `--print-timeout`** waits for background tasks with no time limit. See [CI/CD Integration](#cicd-integration).

## Installation

On macOS and Linux, run the one-line script:

```bash
curl -fsSL https://antigravity.google/cli/install.sh | bash
agy install       # configures PATH and shell aliases
agy --version     # verify the install
agy update        # check for and install a newer version
```

On Windows, use the PowerShell installer:

```powershell
irm https://antigravity.google/cli/install.ps1 | iex
```

Or use the CMD installer:

```bat
curl -fsSL https://antigravity.google/cli/install.cmd -o install.cmd
install.cmd
del install.cmd
```

Both Windows installers put `agy.exe` in `%LOCALAPPDATA%\agy\bin` and run `agy install` for you. Open a new terminal before you run `agy --version`.

## Authentication

- **Local**: Credentials come from the system keyring. Google Sign-In in your browser is the fallback.
- **SSH**: The CLI prints an authorization URL. Open it in a browser on your local machine.
- **CI**: Set `GEMINI_API_KEY`. Write `{"modelProvider": "gemini"}` to `~/.gemini/antigravity-cli/settings.json`. You need both. The key alone does nothing. Runs without auth fail fast with an error. See [CI/CD Integration](#cicd-integration).

## First Run

- **Trust prompt**: On first launch in a new folder, `agy` asks whether you trust it. Accepting grants read, edit, and execute access to that directory. Accept only for folders you control.
- `!command` runs a shell command inside the session (`!npm test`). `/tasks` shows the execution logs.
- `agy -c` resumes your last conversation. The exit message prints the exact resume command.

## Driving the Terminal Agent

| Invocation | Notes |
|------------|-------|
| `agy` | Interactive session in the current directory |
| `agy -i "prompt"` | Interactive, with the prompt pre-submitted (`--prompt-interactive`; agy 1.4.2 rejects a bare `agy "prompt"` with "unexpected argument") |
| `agy -p "prompt"` | One-shot: print the answer and exit (scripts, CI) |
| `agy -c` / `agy --conversation <id>` | Resume the last conversation, or one by ID |
| `agy --model <name>` | Session model; `agy models` lists options, `/model` switches live |
| `agy --mode <accept-edits\|auto\|plan>` | Startup execution mode; leave the flag off for the default mode (agy 1.4.2 warns on `--mode default`) |
| `agy --add-dir <path>` | Add a directory to the workspace (repeatable) |
| `agy plugin import gemini` | Import legacy Gemini CLI extensions as skills/plugins |

Type everyday tasks as prompts:

```bash
# Codebase question (was `gemini ask`)
agy -p "What testing framework does this project use?"

# Diagnose and fix (was `gemini fix`)
agy -p "Diagnose why npm run build fails and propose a fix"

# Code review (was `gemini review`)
agy -p "Review the diff of my most recent commit. Be strict: flag style violations, missing error handling, and anything that breaks our project rules."

# Scaffolding (was `gemini scaffold`)
agy -i "Scaffold a Next.js dashboard with a Prisma backend. Follow 'clean architecture': separate the domain, data, and presentation layers."
```

You do not need to pipe input. The agent reads files itself. It runs the build or `git` itself when it needs their output.

In print mode, nobody is there to approve those shell commands. They are soft-denied. The run still exits 0, with a notice on stderr. To let a one-liner run commands, do one of these:

- Add `permissions.allow` rules in `~/.gemini/antigravity-cli/settings.json`, such as `"command(git)"` or `"command(regex:npm run (build|lint|test))"`.
- Run it in an interactive session.

To send one-shot output to a file, redirect it. This example reads `git log`, so allow `"command(git)"` first:

```bash
agy -p "Generate a changelog entry from the commits since the last tag" >> CHANGELOG.md
```

## Slash Commands

Type `?` on an empty prompt for the current list. The list grows between releases.

| Area | Commands |
|------|----------|
| Working state | `/plan` (plan mode), `/diff` (unified diffs), `/tasks` (shell logs), `/rewind` (roll back) |
| Agents and extensions | `/agents` (subagent activity), `/skills` (loaded skills), `/hooks` (active hooks), `/mcp` (MCP servers) |
| Session flow | `/resume` (previous thread), `/fork` (parallel session), `/btw` (side question), `/compact` (summarize the conversation to free context) |
| Housekeeping | `/settings` alias `/config` (settings editor), `/permissions` (preset), `/model` (switch model), `/credits` (remaining credits) |

Keyboard shortcuts:

- **Shift+Tab** cycles the execution mode in place. The modes are the default mode, accept-edits, auto, and plan.
- `auto` appears only where the terminal sandbox runs. In agy 1.4.4 and later, that includes Windows 11 24H2 or later. It does not appear for business or enterprise accounts.
- **Ctrl+R** opens the Artifact Review panel.

## Permissions and Sandboxing

There are four presets. Switch them in-session with `/permissions`.

| Preset | Behavior |
|--------|----------|
| `request-review` (default) | Line-level diff before each file write; `f` accepts or rejects hunks |
| `proceed-in-sandbox` | No prompts, sandboxed execution only |
| `always-proceed` | No prompts anywhere; controlled workspaces only |
| `strict` | Confirms every non-read-only tool |

- **Sandbox**: Use `--sandbox` at launch, or `enableTerminalSandbox` in settings. It limits what terminal commands can reach. For platforms where it does nothing, see the note at the top of this page.
- `allowNonWorkspaceAccess` is off by default. Leave it off unless a task needs files outside the workspace root.
- Keep `request-review` for any repository that matters. Use `always-proceed` and `--dangerously-skip-permissions` only in sandboxed or throwaway workspaces.
- `agy` has no offline mode. It authenticates to Google's cloud and has no local-model endpoint.

Why these settings matter (the prompt-injection risk): Chapter 6, Section 6.4.

## Configuration and Context Files

| File | What it holds |
|------|---------------|
| `~/.gemini/antigravity-cli/settings.json` | Theme, permission preset, verbosity |
| `~/.gemini/antigravity-cli/keybindings.json` | Your key-binding overrides; remove the file to restore defaults |
| `~/.gemini/config/mcp_config.json` | MCP servers, global scope |
| `.agents/mcp_config.json` | MCP servers, per workspace |
| `.agents/rules/` | Workspace governance rules |
| `.agents/skills/<name>/SKILL.md` | A skill, invoked as `/<name>` |
| `GEMINI.md` | Workspace context (Gemini CLI heritage) |
| `AGENTS.md` | Cross-tool context file, shareable across agents |

The config tree still lives under `.gemini`, carried over from Gemini CLI. The `settings.json` keys you will edit are:

- `toolPermission` (the preset above)
- `enableTerminalSandbox`
- `editor`

## Extending agy with Skills

- Put one skill per folder under `.agents/skills/`.
- The folder name becomes the slash command. There are no namespaces and no colon syntax.
- A skill is a single `SKILL.md` file: YAML frontmatter plus markdown instructions.

```markdown
<!-- .agents/skills/money-audit/SKILL.md -->
---
description: Audits MoneyMind for security compliance.
---

Scan the files or directory the user names for hardcoded Plaid secrets,
missing environment variables, and improper error handling. Report findings
with severity levels and suggested fixes.
```

1. Ask the agent to write the file. This keeps the frontmatter valid. The lab README, Phase 3, has the authoring prompt.
2. Run `/skills reload`, or start a new conversation.
3. Run the skill as `/money-audit ./`.

## CI/CD Integration

```bash
agy -p "..." --dangerously-skip-permissions --sandbox
```

- `-p` runs headless and prints one answer.
- `--dangerously-skip-permissions` auto-approves tool requests (no human present). For its denylist and Enterprise behavior, see the note at the top of this page. If the job needs only a few tools, use scoped `permissions.allow` rules in settings instead.
- `--sandbox` limits what those auto-approved tools can reach where the terminal sandbox is available. In agy 1.4.4 and later it does nothing elsewhere (see the note in ci-cd-integration.yml).
- `--print-timeout 10m` caps the run. As of November 7, 2026 (agy 1.5.0 and later), `-p` without it waits for background tasks with no time limit. A run the timeout cuts short prints an `AGY_ERROR` line and exits with code 3, so the CI step fails.
- **Gotcha**: Headless tool calls that fail approval are soft-denied. The run still exits 0 with only a stderr notice. Check stderr. Otherwise a partially skipped review can look like a pass.
- **Auth**: Set the `GEMINI_API_KEY` env var and `{"modelProvider": "gemini"}` in settings. See [Authentication](#authentication).

A GitHub Actions workflow you can adapt (install, headless auth, review step) is at [ci-cd-integration.yml](../code-examples/antigravity-cli/ci-cd-integration.yml). Flags shift between releases. Before you wire up CI, check antigravity.google/docs/cli/headless and run `agy changelog`.

## Migrating from Gemini CLI

- Config under `~/.gemini` imports automatically on the first `agy` launch.
- `agy plugin import gemini` converts extensions and TOML custom commands (`.gemini/commands/*.toml`, `/namespace:command` syntax) into skills or plugins. They do not run natively.
- `GEMINI.md` files keep working as workspace context.
- Steps change between releases. Check antigravity.google/docs and `agy changelog`.

## Troubleshooting

- **Misbehaves in a script or CI job**: Bare `agy` expects a TTY. Use `agy -p "..."`. Add `--dangerously-skip-permissions --sandbox` when the job needs tool access. Watch stderr for soft-denied tool calls. The run still exits 0.
- **"Not authenticated" in CI**: Set the `GEMINI_API_KEY` secret. Write `{"modelProvider": "gemini"}` to `~/.gemini/antigravity-cli/settings.json`. You need both.
- **Trust prompt on every new folder**: This is expected. It gates read, edit, and execute access per folder.
- **Model not available**: Run `agy models` to list what your account has. Switch with `/model` in-session or `--model` at launch.

## Next Steps

- Complete [Exercise 2: Antigravity CLI](../hands-on-lab/exercises/exercise-2-antigravity-cli.md)
- Set up [Firebase Genkit](./genkit-setup.md) for observability
- Learn the [Intent-First Workflow](./intent-first-workflow.md)
