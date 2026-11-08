# Antigravity CLI (agy) Code Examples

## Overview

These are prompt patterns for the `agy` terminal agent (the Antigravity CLI, successor to the consumer Gemini CLI). There are no task subcommands. Everything is a prompt. Use `agy -p "..."` for the scriptable one-shot form in CI. Chapter 6, Section 6.4 explains the design.

## Files

| File | Purpose |
|------|---------|
| `scaffolding.sh` | Prompt-driven project and module generation |
| `error-resolution.sh` | Diagnosis and fix patterns (the "Smart Fix" loop) |
| `code-review.sh` | Review workflows (the "Auto-Review" loop) |
| `ci-cd-integration.yml` | GitHub Actions workflow with headless agy |

> **Differences from the book's Listing 6-2 (as of November 7, 2026)**
>
> `ci-cd-integration.yml` is a fuller version of Listing 6-2, which the chapter labels a conceptual shape.
>
> - The listing writes `--output-format json` to `review.json`. It posts it with a `scripts/post-review-comments.js` you would write yourself. This workflow asks for markdown instead and posts it with `actions/github-script`, so it runs without an extra script.
> - It adds a security-audit job and a changelog job.
> - It uses the Node 24 major of each action (`actions/checkout@v7`, `actions/github-script@v9`, `actions/upload-artifact@v7`). As of November 7, 2026, GitHub's runners do not ship Node 20, which the `@v4` in Listing 6-2 targets.

## Quick Reference

### One-Liners

```bash
# Quick codebase question
agy -p "What dependencies does this project use?"

# Diagnose a failing build
agy -p "Diagnose why npm run build fails and propose a fix"

# Review before you push
agy -p "Review the diff of my most recent commit. Be strict."

# Generate docs
agy -p "Read src/lib/*.ts and generate API documentation as markdown" > api-docs.md
```

Print mode reads and writes workspace files without asking. Shell commands need approval. When nobody is there to approve them, they are soft-denied. So a one-liner such as the build diagnosis sees the code but not the build output. Grant what a prompt needs with `permissions.allow` rules in `~/.gemini/antigravity-cli/settings.json`. For example:

```json
{
  "permissions": {
    "allow": ["command(git)", "command(regex:npm run (build|lint|test))"]
  }
}
```

Or run the prompt in an interactive `agy` session. There you approve each command as it comes up.

### Launchers

| Invocation | Notes |
|------------|-------|
| `agy` | Interactive session in the current directory |
| `agy -i "prompt"` | Interactive, with the prompt pre-submitted (`--prompt-interactive`; agy 1.4.2 rejects a bare `agy "prompt"` with "unexpected argument") |
| `agy -p "prompt"` | One-shot: print the answer and exit |
| `agy -c` / `agy --conversation <id>` | Resume the last conversation, or one by ID |
| `agy --model <name>` | Session model (`agy models` lists options) |
| `agy --mode <accept-edits\|auto\|plan>` | Startup execution mode; leave the flag off for the default mode (agy 1.4.2 warns on `--mode default`) |
| `agy --add-dir <path>` | Add a directory to the workspace (repeatable) |

### CI Pattern

```bash
agy -p "..." --dangerously-skip-permissions --sandbox
```

- `-p` runs headless and prints one answer.
- `--dangerously-skip-permissions` auto-approves tool requests. As of November 7, 2026, it blocks commands on agy's system command denylist instead (agy 1.5.2 and later). In `-p` runs on a Gemini Enterprise account, it also denies terminal commands or file access outside the workspace that your administrator requires to be reviewed. If only a few tools are needed, use scoped `permissions.allow` rules in settings instead.
- `--sandbox` limits what auto-approved tools can reach where the terminal sandbox is available. In agy 1.4.4 and later it does nothing elsewhere (see the note in ci-cd-integration.yml).
- `--print-timeout 10m` caps the run. As of November 7, 2026 (agy 1.5.0 and later), `-p` without it waits for background tasks with no time limit. A run the timeout cuts short prints an `AGY_ERROR` line and exits with code 3, so the CI step fails.
- Gotcha: Tool calls that fail approval in headless mode are soft-denied. The run still exits 0. Check stderr for skipped work.
- CI auth: Set `GEMINI_API_KEY`. Write `"modelProvider": "gemini"` into `~/.gemini/antigravity-cli/settings.json`. The key does nothing without the setting. [ci-cd-integration.yml](./ci-cd-integration.yml) shows the full setup.

### Common Patterns

See the individual files for examples and usage notes. For install, auth, slash commands, and permission presets, see the [Antigravity CLI guide](../../tutorials/antigravity-cli-guide.md).
