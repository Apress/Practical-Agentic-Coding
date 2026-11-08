# Key Advancements in Agentic Coding

Chapter 16, Section 16.7 of *Practical Agentic Coding* says that the companion repository tracks significant enhancements in the agentic AI coding industry. This file is that log. It lists key advancements in the tools and practices the book covers, current as of November 7, 2026.

**What belongs here:** advancements large enough to affect how you apply the book. Examples:

- tool renames and successions
- framework releases that change a workflow taught in a chapter
- protocol shifts
- billing model changes
- deprecations

Routine version bumps and feature-level details do not belong here. Vendor documentation remains the authoritative source for those.

**How to read an entry:** each entry says what changed, why it matters, and which chapters it affects. Use it to find the chapter text to re-read.

- Entries are in date order, oldest first. The newest entry is at the bottom.
- Before you adopt anything you find here, run the seven checks in Chapter 16, Section 16.6.

**To report a missing advancement:** open an issue or a pull request on this repository (see [Contributing.md](../Contributing.md)). Use the template below.

This file covers changes in the industry. Corrections to book content go in [errata.md](../errata.md) instead.

## Entry template

```markdown
### YYYY-MM: Short title

- **Area:** (tools / models / frameworks / protocols / billing / other)
- **What changed:** one or two sentences on the shift.
- **Chapters affected:** which chapters' content or labs this touches, and whether the book's guidance still holds as written.
```

---

## Entries

### 2026-07: MCP specification 2026-07-28 makes the protocol stateless

- **Area:** protocols
- **What changed:** The Model Context Protocol's current revision, 2026-07-28, drops the `initialize` handshake and protocol-level sessions. Every request carries its protocol version and client capabilities. Servers describe themselves through a new `server/discover` call. The revision deprecates Roots, Sampling, and Logging. It formally deprecates the older HTTP+SSE transport in favor of Streamable HTTP. It also defines how to interoperate with clients and servers on 2025-11-25 and earlier. Version 2 of the official TypeScript SDK (`@modelcontextprotocol/server` and `@modelcontextprotocol/client`, July 2026) and Python SDK (`mcp` 2.0, July 2026) implement it. The TypeScript v1 line (`@modelcontextprotocol/sdk`) stays on 2025-11-25 and receives fixes for at least six months after v2's release. Sources: [modelcontextprotocol.io/specification/2026-07-28/changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog), [github.com/modelcontextprotocol/typescript-sdk](https://github.com/modelcontextprotocol/typescript-sdk).
- **Chapters affected:** Chapter 4, Section 4.2; Chapter 8, Section 8.4; Chapter 11, Sections 11.2 and 11.4; Chapter 16, Section 16.2. The book's guidance holds as written. The `mcpServers` entries it shows (stdio commands and `"type": "http"` endpoints) are unchanged. The Chapter 8 lab's custom server is built on the v1 SDK.

### 2026-09: TypeSafe introduces System One models and Jev

- **Area:** models
- **What changed:** TypeSafe introduced System One models, "a new class of frontier models built to make fast, structured decisions that software can use directly," trained with a method it calls Reinforcement Learning for Calibrated Decisions (RLCD). Its first public model, Jev, returns typed decisions with calibrated probabilities instead of text. Jev is in early access. Jev 1.14.0 followed in October 2026. Sources: [typesafe.ai/blog/introducing-system-one-models-and-jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev), [docs.typesafe.ai](https://docs.typesafe.ai).
- **Chapters affected:** Chapter 4, Section 4.3 (foundation models) and Chapter 16, Sections 16.2 and 16.7. The book's guidance holds as written. Run the Section 16.6 checks before you adopt it.

### 2026-10: Claude Code adds mods

- **Area:** tools
- **What changed:** On October 1, 2026, Claude Code 2.1.287 introduced Claude Mods. Mods are plugins written as JavaScript or TypeScript event handlers that run inside Claude Code. A mod can hold or answer tool calls, draw panes, and add commands that run without a Claude turn. The documentation calls the settings-file hooks that Chapter 8 teaches "settings hooks" to tell the two apart. Administrators can limit mods to their own through managed settings. Sources: [github.com/anthropics/claude-code/blob/main/CHANGELOG.md](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md), [code.claude.com/docs/en/plugins/mods/overview](https://code.claude.com/docs/en/plugins/mods/overview), [code.claude.com/docs/en/plugins/mods/admin](https://code.claude.com/docs/en/plugins/mods/admin).
- **Chapters affected:** Chapter 8, Sections 8.3 and 8.4, and Chapter 10, Section 10.6. See the ["Go further with Claude Code" list](../chapter-08/README.md#go-further-with-claude-code) for details. The book's guidance holds as written. The Chapter 8 hooks still work. A mod runs with your permissions, so install mods only from sources you trust.

### 2026-10: Gemini 4 Argon becomes Google's flagship reasoning model

- **Area:** models
- **What changed:** Google released Gemini 4 Argon (`gemini-4-argon`) to general availability on October 13, 2026. The Gemini API documentation calls it Google's flagship reasoning model. Antigravity offers it on Google AI Pro (paid, or a trial on eligible premium devices), Ultra, and Enterprise plans. Genkit's `googleAI` plugin lists it from Genkit 1.43.0. Sources: [ai.google.dev/gemini-api/docs/changelog](https://ai.google.dev/gemini-api/docs/changelog), [antigravity.google/docs/models](https://antigravity.google/docs/models), [Genkit JS 1.43.0](https://github.com/genkit-ai/genkit/releases/tag/genkit%401.43.0).
- **Chapters affected:** Chapter 6, Sections 6.1, 6.3, 6.5, and 6.6 (model tiers). The book describes tiers rather than model names, so its guidance holds. Where it asks for a Pro-class or thinking-tier model, pick the deepest reasoning model your plan lists. The Genkit plugin lists the `gemini-flash-latest` and `gemini-pro-latest` aliases that the MoneyMind prompts use. Run the Section 16.6 checks before you adopt it.

### 2026-10: Cursor releases its Agent SDK

- **Area:** tools
- **What changed:** On October 20, 2026, Cursor made its Agent SDK generally available. An agent is a versioned project. It holds instructions, typed tools, skills, MCP connections, and channels such as pull request events, Slack, webhooks, and schedules. You test it with evals and deploy it to Cursor's hosting or your own infrastructure. Sources: [cursor.com/changelog/agent-sdk](https://cursor.com/changelog/agent-sdk), [cursor.com/docs/agent-sdk](https://cursor.com/docs/agent-sdk).
- **Chapters affected:** Chapter 10, Section 10.5 (building custom agents) and Chapter 11, Section 11.2 (the AI DevOps ecosystem). The book's guidance holds as written. Run the Section 16.6 checks before you adopt it.

### 2026-10: MCP servers can serve Agent Skills

- **Area:** protocols
- **What changed:** On October 23, 2026, version 2.4.0 of the official MCP TypeScript SDK implemented the Skills over MCP extension (SEP-2640), With it, an MCP server can publish folders of Agent Skills (a SKILL.md file plus supporting files). Clients list and read them through MCP resources. Like every MCP extension, it stays off until both client and server opt in. Client support varies. Sources: [modelcontextprotocol.io/extensions/overview](https://modelcontextprotocol.io/extensions/overview), [modelcontextprotocol.io/extensions/skills/overview](https://modelcontextprotocol.io/extensions/skills/overview), [TypeScript SDK v2.4.0](https://github.com/modelcontextprotocol/typescript-sdk/releases/tag/v2.4.0).
- **Chapters affected:** Chapter 4, Section 4.2; Chapter 7, Section 7.2; Chapter 8, Section 8.4. See the ["Go further with MCP and A2A" list](../chapter-04/README.md#go-further-with-mcp-and-a2a) for details. The book's guidance holds as written. Skills checked into the repository still load the way the chapters show. This extension adds a way to share one set across many repositories.

### 2026-10: GitHub Copilot becomes one connected cloud session

- **Area:** tools
- **What changed:** On October 28, 2026, GitHub began rolling out Copilot in the cloud on every Copilot plan except Free. It is one session that you can start on github.com, GitHub Mobile, VS Code, the Copilot CLI, or the GitHub Copilot app, and continue on any of them. Sessions run in a GitHub-hosted cloud sandbox by default. GitHub Actions and your own registered machines are the other environments. A single Copilot in the cloud policy covers the cloud agent, Copilot Chat on github.com, and Copilot Mobile. Each of these had a separate policy before. In VS Code, the Copilot harness is the default for new chats from version 1.143. Sources: [github.blog/changelog/2026-10-28-work-from-anywhere-with-a-new-connected-copilot-cloud-experience](https://github.blog/changelog/2026-10-28-work-from-anywhere-with-a-new-connected-copilot-cloud-experience), [github.blog/changelog/2026-10-28-github-copilot-in-vs-code-universe-releases](https://github.blog/changelog/2026-10-28-github-copilot-in-vs-code-universe-releases), [docs.github.com/copilot](https://docs.github.com/copilot).
- **Chapters affected:** Chapter 7, Sections 7.3, 7.5, and 7.6 (Phase 4); Chapter 10, Sections 10.1 and 10.3; Chapter 11, Sections 11.2 and 11.5, which describe the cloud agent running in GitHub Actions sandboxes. The book's guidance holds. Assigning an issue to Copilot opens a pull request for you to review. You approve its workflow runs.

### 2026-10: GitHub Agentic Workflows generally available

- **Area:** tools
- **What changed:** GitHub made GitHub Agentic Workflows, an open-source GitHub Next project, generally available on October 28, 2026 for GitHub Free, Team, and Enterprise. You write the automation as natural-language Markdown files. They compile into standard GitHub Actions YAML and run a coding agent inside Actions. The default agent is GitHub Copilot CLI, which needs a Copilot license. You can choose another engine. The agent is read-only by default and sandboxed. Its outputs are validated before they are applied. Sources: [github.blog/changelog/2026-10-28-github-agentic-workflows-generally-available](https://github.blog/changelog/2026-10-28-github-agentic-workflows-generally-available/), [github.github.com/gh-aw](https://github.github.com/gh-aw/).
- **Chapters affected:** Chapter 11, Sections 11.2 and 11.5 (agents inside CI/CD), and Chapter 13, Section 13.5 (the GitHub case study runs on this system). The book's guidance holds as written. Run the Section 16.6 checks before you adopt it.

### 2026-10: Copilot Automations become shared, event-driven team workflows

- **Area:** tools
- **What changed:** On October 28, 2026, GitHub extended Copilot Automations. An automation pairs a prompt, triggers, and allowed tools, and runs Copilot in the cloud. Shared automations belong to a repository and bill AI Credits to the repository owner. The update added:
  - GitHub event triggers (issues, pull requests, discussions, and security alerts)
  - an API trigger for external systems
  - chaining on another automation's success or failure
  - custom MCP tools
  - credit limits per run, day, week, or month
  - proposed prompt changes that you review before they apply

  VS Code 1.144 added cloud automations to its Agents window. Sources: [github.blog/changelog/2026-10-28-build-shared-workflows-for-your-team-with-copilot-automations](https://github.blog/changelog/2026-10-28-build-shared-workflows-for-your-team-with-copilot-automations), [github.blog/changelog/2026-10-28-new-tools-triggers-and-cost-controls-for-copilot-automations](https://github.blog/changelog/2026-10-28-new-tools-triggers-and-cost-controls-for-copilot-automations), [github.blog/changelog/2026-10-28-create-and-manage-copilot-automations-in-visual-studio-code](https://github.blog/changelog/2026-10-28-create-and-manage-copilot-automations-in-visual-studio-code).
- **Chapters affected:** Chapter 7, Section 7.3; Chapter 10, Section 10.3 (handoffs between agents); Chapter 11, Sections 11.2 and 11.5 (event-triggered agents in delivery pipelines). See the "Go further" lists in [Chapter 7](../chapter-07/README.md#go-further-with-cursor-and-github-copilot) and [Chapter 11](../chapter-11/README.md#go-further-with-ai-devops-tools) for details. The book's guidance holds as written. Scope each automation's tools tightly. Set a credit limit before you let it run on events.

### 2026-11: Kiro CLI 3.0 makes the V3 agent harness the default

- **Area:** tools
- **What changed:** On November 3, 2026, Kiro CLI 3.0.0 shipped as one standalone `kiro-cli` binary. It starts interactive sessions on the V3 agent harness by default. Existing V2 users are asked before the V3 default applies. `kiro-cli --v2` keeps V2. V2 custom agents are upgraded automatically, with a `.json.bak` copy of each. The release retired the Classic interface, the macOS desktop app, and inline shell autocomplete. It also retired the `autocomplete`, `inline`, `translate`, `theme`, and `dashboard` commands. Sources: [kiro.dev/changelog/cli/3-0](https://kiro.dev/changelog/cli/3-0/), [kiro.dev/blog/cli-3](https://kiro.dev/blog/cli-3/), [kiro.dev/docs/cli/agent-harness](https://kiro.dev/docs/cli/agent-harness/).
- **Chapters affected:** Chapter 5, Section 5.1, which names the Kiro CLI. See the ["Go further with Kiro" list](../chapter-05/README.md#go-further-with-kiro) for details. The book's guidance holds as written. The book mentions the Kiro CLI by name and teaches none of the retired commands.

### 2026-11: Kiro Enterprise moves to pooled credits

- **Area:** billing
- **What changed:** On November 4, 2026, Kiro introduced credit pooling, labeled Credit sharing in the Kiro console. Each Kiro Enterprise seat adds its monthly credits to one shared pool. Admins cap usage per user, per group, or per profile. At introduction it was the only option for Kiro profiles created from then on. Existing customers switch with a one-way wizard that cancels each user's individual subscription. Sources: [kiro.dev/changelog/general/credit-pooling](https://kiro.dev/changelog/general/credit-pooling/), [kiro.dev/docs/enterprise/credit-pooling](https://kiro.dev/docs/enterprise/credit-pooling/).
- **Chapters affected:** Chapter 15, Section 15.7 (price a Kiro rollout as seats plus pooled credits instead of per-user plans) and Chapter 14 (set group limits for each pilot team). See the ["Go further with Kiro" list](../chapter-05/README.md#go-further-with-kiro) for details. Chapter 5, Section 5.1 holds as written. Credits remain the unit, and each model has its own credit cost.
