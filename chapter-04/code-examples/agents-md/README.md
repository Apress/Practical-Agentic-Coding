# AGENTS.md Templates

This directory holds the AGENTS.md templates from Chapter 4.

AGENTS.md is a single file at the repo root. It gives coding agents their operating instructions for the project.

When to use AGENTS.md and why: Chapter 4, Section 4.2 and Section 4.5.

## Files in This Directory

| File | Description | Source |
|------|-------------|--------|
| `AGENTS.md` | Backend service template: persona, stack, rules, workflow, commands, safety | Listing 4-6 |
| `AGENTS_enterprise.md` | Numbered enterprise template with governance and restricted areas | Listing 4-3, extended with an architecture diagram and more detail |

## AGENTS.md Structure

The templates use these sections:

```markdown
# AGENTS.md

## Persona
Who the agent should pretend to be

## Tech Stack
Technologies used in the project

## Project Rules
Non-negotiable constraints

## Workflow
Step-by-step process for tasks

## Commands
Specific commands the agent should run

## Restricted Areas
Files and directories to avoid
```

## Using a template

1. Copy `AGENTS.md` (or `AGENTS_enterprise.md`, renamed to `AGENTS.md`) to your project root.
2. Replace each section with your project's own content.
3. Commit the file to Git.

## How Agents Use AGENTS.md

| Tool | How it reads AGENTS.md | Covered in |
|------|------------------------|------------|
| Amazon Kiro | Treats it as a steering file (workspace root or `~/.kiro/steering/`). | Chapter 5 |
| Cursor | Reads it from the project root. | Chapter 7 |
| GitHub Copilot in VS Code | Auto-detects it alongside `copilot-instructions.md`. | Chapter 7 |
| Claude Code | See the note below. | Chapter 8 |
| CI/CD | A headless agent invocation can pass the file as context, the same way an interactive session loads it. | |

**Claude Code.** Its own file is CLAUDE.md. Claude Code 2.1.277 and later also read AGENTS.md, but only in a project with no CLAUDE.md. When both exist, it reads CLAUDE.md alone. Two exceptions:

- CLAUDE.md imports AGENTS.md with an `@AGENTS.md` line.
- You change **Project instructions** in `/config`.

If your team keeps both files, put `@AGENTS.md` at the top of CLAUDE.md. Then there is one source of truth.

Support and file-detection rules change between releases. Check the tool's current documentation before you assume a file is being read. To confirm, ask the agent to restate a rule from the file.

## Rules files

AGENTS.md is guidance for the model. Hard blocking needs a hook, linter, or CI check. See [../rules-files/](../rules-files/) for the rules half.

## Related Resources

- [agents.md](https://agents.md/): the AGENTS.md convention
- [How to write a great AGENTS.md](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/): GitHub's analysis of 2,500+ repositories, cited in Exercise 4.1
- Chapter 5: Amazon Kiro, which reads AGENTS.md as a steering file
- Chapter 7: Cursor and GitHub Copilot, which both pick up AGENTS.md automatically
- Chapter 8: Claude Code, whose own file for the same role is CLAUDE.md
