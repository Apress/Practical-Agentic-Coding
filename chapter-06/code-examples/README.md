# Chapter 6 Code Examples

This folder holds reference material from Chapter 6. Nothing here is a program to run. It holds these kinds of files:

- Configuration files you copy into a project
- Prompt patterns you adapt
- Artifact examples you read

The only thing that runs is the MoneyMind lab in `../hands-on-lab/moneymind/`.

## What's in Each Directory

| Directory | What it holds | Book section |
|-----------|---------------|--------------|
| `antigravity-cli/` | `agy` prompt patterns for diagnosis, review, scaffolding, and CI | Section 6.4, Listings 6-1 and 6-2 |
| `antigravity-config/` | Workspace settings, the Secure Mode variant, and a rules template | Sections 6.2 and 6.3 |
| `genkit/` | Eight flow patterns and a golden evaluation dataset | Section 6.5, Listing 6-3 |
| `artifacts/` | A real Implementation Plan and the Walkthrough that followed it | Section 6.3 |

```text
code-examples/
├── README.md                     # This file
├── antigravity-cli/
│   ├── README.md
│   ├── scaffolding.sh            # Prompt-driven project generation
│   ├── error-resolution.sh       # The "Smart Fix" loop
│   ├── code-review.sh            # The "Auto-Review" loop
│   └── ci-cd-integration.yml     # GitHub Actions with headless agy
├── antigravity-config/
│   ├── README.md
│   ├── settings.json             # Everyday workspace settings
│   ├── secure-mode.json          # Strict variant for sensitive work
│   └── rules-template.md         # Starting point for .agents/rules/
├── genkit/
│   ├── README.md
│   ├── flow-patterns.ts          # Eight flow patterns
│   └── evaluation-dataset.json   # Golden dataset, 13 labeled transactions
└── artifacts/
    ├── README.md
    ├── implementation-plan-example.md
    └── walkthrough-example.md
```

## Antigravity CLI in One Screen

`agy` is an interactive terminal agent. It has no task subcommands. There is no `agy fix`, `agy review`, or `agy scaffold`. You ask for what you want. The launch flags only control how the session starts.

```bash
# One-shot print mode: the workhorse for scripts and CI
agy -p "What testing framework does this project use?"
agy -p "Diagnose why npm run build fails and propose a fix"
agy -p "Review the diff of my most recent commit. Be strict."

# Interactive session, opening with a prompt already submitted
agy -i "Scaffold an Express API with TypeScript"
```

The `.sh` files in `antigravity-cli/` collect these prompts, with notes on when each one helps. Read them and adapt them. They are not scripts to run unchanged against your own repo.

In print mode, the agent reads and writes files in the workspace without asking. Shell commands (running the build, the tests, or `git`) need approval. With no one to approve them, they are soft-denied. The run still exits 0, with a notice on stderr. To let a prompt run the commands it needs, do one of these:

- Add `permissions.allow` rules in `~/.gemini/antigravity-cli/settings.json`, such as `"command(git)"` or `"command(regex:npm run (build|lint|test))"`.
- Run the prompt in an interactive session, where you approve each command.

## Applying the Configuration

```bash
# From your project root; REPO is where you cloned this repository
REPO=~/Practical-Agentic-Coding
mkdir -p .antigravity .agents/rules
cp "$REPO/chapter-06/code-examples/antigravity-config/settings.json" .antigravity/settings.json
cp "$REPO/chapter-06/code-examples/antigravity-config/rules-template.md" .agents/rules/project-rules.md
```

On Windows (PowerShell):

```powershell
$REPO = "$HOME\Practical-Agentic-Coding"
New-Item -ItemType Directory -Force .antigravity, .agents\rules
Copy-Item "$REPO\chapter-06\code-examples\antigravity-config\settings.json" .antigravity\settings.json
Copy-Item "$REPO\chapter-06\code-examples\antigravity-config\rules-template.md" .agents\rules\project-rules.md
```

Then edit both. The settings file is a readable record of decisions. To change behavior, use Antigravity's own settings UI. Key names change between releases.

## Related

- [Tutorials](../tutorials/) for step-by-step setup
- [Exercises](../hands-on-lab/exercises/) for practice
- [MoneyMind](../hands-on-lab/moneymind/) for all of this in a working project

## Navigation

- [Back to Chapter 6](../README.md)
- [Hands-on lab](../hands-on-lab/README.md)
