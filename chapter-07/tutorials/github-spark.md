# GitHub Spark and Mission Control: Quick Reference

**Reference**: Chapter 7, Section 7.3 ("GitHub Copilot: The Ecosystem Paradigm")

This file gives the current status of two Copilot surfaces from Section 7.3, and the steps that still run. Neither one is configured from a file, so this repository has no code artifact for them.

What Spark and mission control are, and why they matter: Chapter 7, Section 7.3.

## Part 1: GitHub Spark (retired, as of November 7, 2026)

> **Status, as of November 7, 2026.** GitHub has retired Spark on github.com.
>
> - From August 4, 2026 it accepts no new users and no new apps.
> - Existing users had until August 31, 2026 to export their apps.
> - Apps already deployed keep running.
>
> Source: GitHub changelog, "Upcoming deprecation of GitHub Spark on github.com". GitHub Models, which Spark used for AI features, was retired on July 30, 2026. None of the Spark steps in Section 7.3 can be run today.

Read Section 7.3 as a record of Spark's design. This repository carries no walkthrough for a product you cannot use.

If you exported a Spark app before the cutoff, it is an ordinary GitHub repository. Work on it the way Section 7.6 works on LinkForge:

1. Clone it.
2. Open it in your editor with Copilot.
3. Send deployment changes through pull requests.

You can use the prompts from Section 7.3 as first prompts in another app-building tool. The runbook one, for example:

```text
Turn this runbook into an interactive checklist. When a user checks a box,
log the timestamp. Add an AI assistant that suggests the next command based
on the incident type.
```

## Part 2: Mission Control

> **Name change.** GitHub's documentation calls the book's mission control the agents page, at github.com/copilot/agents. You can also reach it from the agents panel on any page on GitHub, and from the **Agents** tab in each repository.

**How to try it**:

1. Dispatch two independent pieces of work as Copilot cloud agent tasks. Assign two GitHub Issues to Copilot, as in Section 7.6 Phase 4.
2. Follow both from the agents page, not from each pull request.
3. On each pull request, click **Approve and run workflows** so the checks run.

The cloud agent needs a Copilot plan that includes it. Copilot Free does not. On Business and Enterprise plans it follows the organization's Copilot in the cloud policy. As of November 7, 2026, that policy is on by default. An administrator can turn it off.

## See also

- [`copilot-setup.md`](copilot-setup.md): plans, IDE installation, chat modes, cloud agent dispatch
- [`copilot-instructions-guide.md`](copilot-instructions-guide.md): repository-level governance for Copilot
- [`../code-examples/copilot/workflow-examples/async-agent-workflow.md`](../code-examples/copilot/workflow-examples/async-agent-workflow.md): the cloud agent workflow end to end
- [`choosing-tool.md`](choosing-tool.md): moving between the two tools, or running both
