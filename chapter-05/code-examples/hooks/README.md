# Kiro Hook Examples

This directory holds example hook configurations for common development tasks.

When to use hooks and why: Chapter 5, Section 5.5.

> **Hook format differs from the book.** These files use the `.kiro.hook` layout from Kiro IDE 0.x. Kiro IDE 1.0 and later use a different format. Kiro 1.0 and later list `.kiro.hook` files as legacy hooks, with an upgrade badge that converts them. Kiro 1.0 cannot create new manual hooks. See [Hook File Format](#hook-file-format) and Kiro's [hooks documentation](https://kiro.dev/docs/hooks/) for the current schema.

## Hook File Format

The `.kiro.hook` layout:

- One hook per file in `.kiro/hooks/`
- A `when` block for the trigger
- A `then` block for the action

```json
{
  "enabled": true,
  "name": "Hook Name",
  "description": "What this hook does",
  "version": "1",
  "when": {
    "type": "fileEdited",
    "patterns": ["*.py"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "Instructions for the agent"
  }
}
```

The Kiro IDE 1.0 and later format:

- Hooks you create are saved as `.kiro/hooks/<name>.json`.
- The `version` is `"v1"`.
- A `hooks` array holds the entries.
- Each entry uses `trigger`, `matcher` (a regular expression), and `action` in place of `when` and `then`.

Kiro 1.0 and later list `.kiro.hook` files as legacy hooks, with an upgrade badge that converts them. See Kiro's [hooks documentation](https://kiro.dev/docs/hooks/) for the current schema.

## Trigger Types

The book and Kiro 1.0 use the names in the first column. A `.kiro.hook` file needs the value in the second.

| Book and Kiro 1.0 name | `when.type` in a `.kiro.hook` file | Use case |
|------------------------|-------------------------------------|----------|
| `UserPromptSubmit` | `promptSubmit` | Context gathering |
| `Stop` | `agentStop` | Follow-up actions after the agent responds |
| `PreToolUse` / `PostToolUse` | `preToolUse` / `postToolUse` | Inspect or react to tool calls |
| `PostFileCreate` | `fileCreated` | Scaffolding |
| `PostFileSave` | `fileEdited` | Validation, test sync |
| `PostFileDelete` | `fileDeleted` | Cleanup |
| Manual Trigger | `userTriggered` | Heavy, on-demand operations |

File-based triggers take a `patterns` list. The list keeps a hook from firing on every file in the tree. The other triggers take no `patterns` key. Kiro's [What's new in IDE 1.0: Hooks](https://kiro.dev/docs/ide/whats-new-v1/hooks/) page has the full mapping, including the session-start trigger.

Kiro 1.0 cannot create new manual hooks. An existing `userTriggered` hook such as `docs-sync.kiro.hook` still runs from the play button in the AGENT HOOKS panel. For a new on-demand workflow, Kiro's documentation recommends a steering file with `inclusion: manual`. Run it as a `/<filename>` slash command. Phase 4 of the hands-on lab shows one.

## Available Examples

| File | Trigger | Description |
|------|---------|-------------|
| `test-coverage.kiro.hook` | `PostFileSave` (`fileEdited`) | Auto-generate tests for changed code |
| `docs-sync.kiro.hook` | Manual Trigger (`userTriggered`) | Update documentation |
| `security-audit.kiro.hook` | `PostFileSave` (`fileEdited`) | Check for security issues |
| `api-docs.kiro.hook` | `PostFileSave` (`fileEdited`) | Generate OpenAPI specs |
| `commit-helper.kiro.hook` | `Stop` (`agentStop`) | Generate commit messages |
| `document-generator.kiro.hook` | `PostFileSave` (`fileEdited`) | Generate documentation for changed files (Exercise 5.1) |

## Limiting Trigger Scope

Use specific patterns. This hook fires only for source files:

```json
{
  "when": {
    "type": "fileEdited",
    "patterns": ["src/**/*.py"]
  }
}
```

Hook best practices: Chapter 5, Section 5.5.

## Installing These Examples

Copy a hook file into your project's `.kiro/hooks/` directory. Run the command from `chapter-05/code-examples/hooks/`. The example assumes your project is at `~/daily-briefing-agent`.

The lab project already ships its own `docs-sync` and `test-coverage` hooks, tuned to its Python tests. Do not copy those two names from here, or you replace them. This example adds a hook the lab does not have:

```bash
cp api-docs.kiro.hook ~/daily-briefing-agent/.kiro/hooks/
```

On Windows (PowerShell):

```powershell
Copy-Item api-docs.kiro.hook $HOME\daily-briefing-agent\.kiro\hooks\
```

Kiro lists hooks from that directory in the AGENT HOOKS panel. Kiro 1.0 and later marks a copied `.kiro.hook` file as legacy and offers the upgrade badge.

If a copied hook does not appear, check that:

- The filename ends in `.kiro.hook`.
- The JSON parses.
- `"enabled"` is `true`.

Build at least one hook through the panel before you copy files. Phase 4 of the hands-on lab walks through it. The panel shows the trigger types your Kiro version offers. Trust the panel over any list in this repository.

Hooks live in `.kiro/hooks/`, so they travel with the repository. Teammates get every hook you commit. Narrow the trigger scope before you commit a hook.
