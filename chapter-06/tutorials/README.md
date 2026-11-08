# Chapter 6 Tutorials

These are quick references for the three tools Chapter 6 covers, plus the intent-first workflow. Work through them before the MoneyMind lab. The lab assumes the tools are installed and that you know the Intent Loop terms from Chapter 6, Section 6.1.

## Tutorial Index

| Tutorial | What it covers | Book section | Time |
|----------|----------------|--------------|------|
| [Antigravity setup](./antigravity-setup.md) | IDE install, model tiers, Secure Mode, workspace rules and context | Section 6.3 | 20-30 min |
| [Intent-first workflow](./intent-first-workflow.md) | The Intent Loop, the Constraint Sandwich, context management | Section 6.1 | 25-35 min |
| [Antigravity CLI guide](./antigravity-cli-guide.md) | `agy`: install, auth, slash commands, permission presets, skills, CI | Section 6.4 | 30-40 min |
| [Genkit setup](./genkit-setup.md) | Flows, Dotprompt, the Developer UI, traces, evaluation | Section 6.5 | 25-35 min |

## Recommended Order

1. **Antigravity setup**. Install the IDE first.
2. **Intent-first workflow**. Learn the Plan mode and artifact review steps.
3. **Antigravity CLI guide**. Note that `agy` has no subcommands.
4. **Genkit setup**. Set up traces for your flows.

Then start the [MoneyMind lab](../hands-on-lab/README.md).

## Quick Links

**Setup**
- [Model selection](./antigravity-setup.md#configure-model-selection)
- [Workspace rules](./antigravity-setup.md#configure-workspace-rules)

**Methodology**
- [The Intent Loop](./intent-first-workflow.md#the-intent-loop)
- [The Constraint Sandwich](./intent-first-workflow.md#the-constraint-sandwich-technique)
- [Context management](./intent-first-workflow.md#context-management)

**CLI**
- [Driving the terminal agent](./antigravity-cli-guide.md#driving-the-terminal-agent)
- [Slash commands](./antigravity-cli-guide.md#slash-commands)
- [Permissions and sandboxing](./antigravity-cli-guide.md#permissions-and-sandboxing)
- [Skills](./antigravity-cli-guide.md#extending-agy-with-skills)
- [Migrating from Gemini CLI](./antigravity-cli-guide.md#migrating-from-gemini-cli)

**Observability**
- [Defining flows](./genkit-setup.md#defining-flows)
- [Understanding traces](./genkit-setup.md#understanding-traces)
- [Evaluation-driven development](./genkit-setup.md#evaluation-driven-development)

## Prerequisites

- Node.js 22 or newer (24 LTS recommended), and Git
- A Google account for Antigravity sign-in
- A Gemini API key for the Genkit tutorial ([aistudio.google.com/apikey](https://aistudio.google.com/apikey))
- Working knowledge of TypeScript

## Getting Help

- [Antigravity documentation](https://antigravity.google/docs)
- [Antigravity CLI reference](https://antigravity.google/docs/cli/reference)
- [Genkit documentation](https://genkit.dev/docs/get-started/)

These tools change quickly. Where this chapter and the official docs disagree, follow the docs.

---

## Navigation

- [Back to Chapter 6](../README.md)
- [Hands-on lab](../hands-on-lab/README.md)
- [Code examples](../code-examples/README.md)
- [Exercises](../hands-on-lab/exercises/README.md)
