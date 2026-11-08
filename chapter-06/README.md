# Chapter 6: Intent-First Development: Mastering Google Antigravity and the Antigravity CLI

## What's Here

This folder holds the material for Chapter 6:

- The MoneyMind lab project (an agentic financial dashboard)
- The workspace governance and context files you give Antigravity
- Antigravity CLI prompt patterns you can reuse
- Genkit flow and evaluation examples
- Four setup tutorials
- Three practice exercises

MoneyMind is the only thing here that runs. The other files are inputs you give the agent, or references to compare its output with. In this chapter you direct Antigravity, and Antigravity writes most of the code.

> **Naming note:** The terminal agent used here is the Antigravity CLI (command: `agy`). It is Google's successor to the consumer Gemini CLI. To convert legacy Gemini CLI extensions, run `agy plugin import gemini`.

## What You Do

1. Install Antigravity and the `agy` CLI (`tutorials/antigravity-setup.md`, `tutorials/antigravity-cli-guide.md`).
2. Read `tutorials/intent-first-workflow.md` before you start prompting. It covers the Intent Loop and the Constraint Sandwich prompt format.
3. Work through the four phases of the MoneyMind lab in `hands-on-lab/README.md`:
   1. Governance and context
   2. The Genkit intelligence layer
   3. A terminal skill
   4. Full integration with traces
4. Practice with the three exercises in `hands-on-lab/exercises/`.
5. Take on the chapter challenge at the end of the lab README (GCP deployment, real Plaid credentials, voice interaction).

## Map to the Book

| Repo path | Book section |
|-----------|--------------|
| `tutorials/intent-first-workflow.md` | Section 6.1 (the Intent-First philosophy and the Perceive-Plan-Act-Verify loop) |
| `code-examples/antigravity-config/` | Section 6.2 (native context and MCP), Section 6.3 (Secure Mode) |
| `code-examples/artifacts/` | Section 6.3 (Artifacts: implementation plans and walkthroughs) |
| `tutorials/antigravity-setup.md` | Section 6.3 (IDE surfaces: Agent Manager, conversation modes, Secure Mode) |
| `tutorials/antigravity-cli-guide.md` | Section 6.4 (the Antigravity CLI), Tables 6.2 to 6.4 |
| `code-examples/antigravity-cli/` | Section 6.4 (prompt-driven diagnosis, review, scaffolding, CI/CD), Listings 6-1 and 6-2 |
| `tutorials/genkit-setup.md` | Section 6.5 (Genkit as the observability layer) |
| `code-examples/genkit/` | Section 6.5 (flows, traces, evaluation-driven development), Listing 6-3 |
| `hands-on-lab/` | Section 6.6 (Hands-on Lab: Building "MoneyMind") |
| `hands-on-lab/README.md` (Chapter Challenge) | Section 6.7 (Chapter Challenge) |

## Go further with Antigravity and Genkit

These capabilities build on what Chapter 6 teaches. Plans, pricing, and availability change. Each item links to the vendor page with current details.

- **The Antigravity CLI as an ACP agent.** `agy acp` runs the Antigravity CLI as an Agent Client Protocol server. ACP editors such as Zed, JetBrains IDEs, Android Studio, and Xcode can then use agy as their in-editor agent. They use your agy sign-in and settings and the default, accept-edits, and plan modes. In the editor, register `agy` with the argument `acp` as a custom agent. On SSH or browserless setups, use `agy acp --login`. Introduced in agy 1.5.0 (November 2026). [Antigravity CLI: ACP](https://antigravity.google/docs/cli/acp/)
- **Remote agents.** A remote agent runs a conversation and its tools in a Google-managed environment. It works from attached GitHub repositories, Drive files, or uploads. Long tasks keep running while your laptop is closed. Start one from the App (New Remote Project), with `agy --remote-agent` (add `--project <name>` to pick a remote project), or on the web at antigravity.google.com. If the task needs your local checkout or dev server, use Remote Control instead. Introduced in Antigravity App 2.29.0 (November 2026). [Remote agents](https://antigravity.google/docs/remote-agents/)
- **Remote Control.** Follow and steer a running local session from another device. Start it with `/remote-control`, `agy --remote-control`, or the `agy remote-control start` background service. It does not work with ADC sign-in. Introduced in agy 1.2.0 (September 2026). [Remote Control](https://antigravity.google/docs/remote-control/)
- **Plugin marketplace.** A plugin bundles skills, MCP servers, subagents, rules, and hooks. Install one from the official marketplace with `/plugin` or `agy plugin install <name>@antigravity-plugins-official` in agy, or from the Customizations tab in the App. Check one in CI with `agy plugin validate --strict --json`. Partner plugins such as Figma, Linear, and Stripe sign in to your account after install. A plugin can add MCP servers and hooks to your agent. Check its permissions and what it adds before you enable it. Introduced in Antigravity App 2.18.1 (September 2026). [Plugin marketplace](https://antigravity.google/docs/marketplace/)
- **Voice mode.** Talk a task through with the agent and hear it answer. You can steer it mid-task and answer most permission prompts by voice. Destructive actions such as file deletion or a force-push still need a click on Allow. Start it from the message box in the App (local conversations only) or with `/voice live` (F6) in agy. `/voice dictate` (F5) only types your words into the prompt. Introduced in Antigravity App 2.29.0 (November 2026). [Voice mode](https://antigravity.google/docs/voice-mode/)
- **Prompt-screening hooks.** A PreInvocation hook receives the message you just sent as `lastUserInput`. It can return `terminationBehavior: "terminate"` to stop the turn before the model sees it, for example when a prompt contains a Plaid secret or an account number. Return an `errorMessage` with it to tell the user why. In `agy -p` runs, that error message makes the run exit non-zero, so CI notices. Introduced in agy 1.4.11 (October 2026). [Hooks](https://antigravity.google/docs/hooks/)
- **Finish reason in JSON output.** With `--output-format json` or `stream-json`, the result carries a `finished_reason` (`print_timeout`, `interrupted`, or `error`) when a turn ends early. A CI script can use it to tell a cut-off answer from a complete one. Introduced in agy 1.4.11 (October 2026). [agy changelog](https://github.com/google-antigravity/antigravity-cli/blob/main/CHANGELOG.md)
- **Billing choices and AI credits.** After a Google Cloud sign-in, agy asks you to choose a Gemini subscription or Pay As You Go. On Google AI Pro and Ultra, the AI Credit Overages setting (`useG1Credits` in agy settings) decides whether credits are spent once your baseline quota runs out. The standalone Antigravity IDE is not supported for enterprise deployments. Enterprise readers run the lab in the App, agy, or an IDE extension. Introduced in agy 1.4.11 (October 2026). [Pricing](https://antigravity.google/pricing), [Enterprise](https://antigravity.google/docs/enterprise/)
- **Interactions API routing in Genkit.** The googleAI plugin sends `-latest` aliases, such as MoneyMind's `gemini-flash-latest`, and several other models to the Gemini Interactions API. That API does not store requests unless you set `store: true`. The lab's lockfile keeps Genkit 1.42. If you upgrade, rerun the classify and waste-detect flows in the Developer UI. Compare their traces before you trust the results. Introduced in Genkit JS 1.43.0 (October 2026). [Genkit JS 1.43.0](https://github.com/genkit-ai/genkit/releases/tag/genkit%401.43.0)
- **Request-logging opt-out in Genkit.** Paid Gemini API projects created on or after October 26, 2026 log generateContent requests by default. For models that stay on generateContent, Genkit's googleAI plugin sends `store` on those requests. Set it in a request's `config` or with `googleAI({ store: false })`. MoneyMind's locked Genkit 1.42 cannot opt out per request. Turn off logging in your project's logs settings in AI Studio instead. Introduced in Genkit JS 1.44.0 (November 2026). [Genkit JS 1.44.0](https://github.com/genkit-ai/genkit/releases/tag/genkit%401.44.0)
- **Recoverable Genkit agents.** With `throwOnError: false`, a failed or aborted agent turn returns its conversation up to the last completed tool round. You can then resume instead of starting over. Sub-agents can run in the background. The `contextCompression` middleware keeps long runs inside a token budget. When a multi-step call fails, the Developer UI's Retry and Continue buttons do the same by hand. Introduced in Genkit JS 1.43.0 (October 2026). [Genkit JS 1.43.0](https://github.com/genkit-ai/genkit/releases/tag/genkit%401.43.0)

## Terms Used in the Lab

One line each. Chapter 6 explains the concepts.

- **Intent Loop**: The agent cycles Perceive > Plan > Act > Verify. You review the plan artifact between Plan and Act.
- **Plan Mode / Fast Mode**: Use Plan for multi-file and architectural tasks (it produces reviewable artifacts). Use Fast for small local edits.
- **Native context / MCP**: The agent reads your workspace directly. External systems (databases, ticket trackers, APIs) come in through MCP servers.
- **Artifacts**: The plans, walkthroughs, and screenshots agents produce for review. Examples are in `code-examples/artifacts/`.
- **Constraint Sandwich**: The prompt shape used throughout the lab:

```text
Act as a senior fintech architect.        <- persona and standards
Create a WasteCard.tsx component that...  <- functional requirements
DO NOT use raw CSS; ONLY Tailwind...      <- negative constraints
```

## Directory Structure

```text
chapter-06/
├── README.md                            # This file
├── tutorials/
│   ├── README.md                        # Tutorial index and reading order
│   ├── antigravity-setup.md             # IDE install, models, Secure Mode, workspace setup
│   ├── antigravity-cli-guide.md         # agy: install, auth, slash commands, permissions, skills
│   ├── intent-first-workflow.md         # Quick reference: Intent Loop, sandwich, context
│   └── genkit-setup.md                  # Genkit flows, Developer UI, traces, evaluation
├── code-examples/
│   ├── README.md
│   ├── antigravity-cli/                 # agy prompt patterns (reference, not scripts to run)
│   │   ├── README.md
│   │   ├── scaffolding.sh               # Prompt-driven project generation
│   │   ├── error-resolution.sh          # The "Smart Fix" loop
│   │   ├── code-review.sh               # The "Auto-Review" loop
│   │   └── ci-cd-integration.yml        # GitHub Actions with headless agy
│   ├── antigravity-config/              # Workspace configuration templates
│   │   ├── README.md
│   │   ├── settings.json                # Everyday workspace settings
│   │   ├── secure-mode.json             # Strict variant for sensitive work
│   │   └── rules-template.md            # Starting point for .agents/rules/
│   ├── genkit/                          # Observability examples
│   │   ├── README.md
│   │   ├── flow-patterns.ts             # Eight flow patterns
│   │   └── evaluation-dataset.json      # Golden dataset for genkit eval:flow
│   └── artifacts/                       # What agent artifacts look like
│       ├── README.md
│       ├── implementation-plan-example.md
│       └── walkthrough-example.md
└── hands-on-lab/
    ├── README.md                        # The four-phase lab and the chapter challenge
    ├── exercises/
    │   ├── README.md
    │   ├── exercise-1-intent-first.md   # The Intent Loop in practice
    │   ├── exercise-2-antigravity-cli.md # agy, skills, CI integration
    │   └── exercise-3-artifacts.md      # Artifacts and Knowledge Items
    └── moneymind/                       # The lab project (this is what runs)
        ├── README.md
        ├── AGENTS.md                    # Cross-tool project context
        ├── .agents/
        │   ├── rules/project-rules.md   # Workspace governance (Phase 1)
        │   └── skills/money-audit/SKILL.md  # The /money-audit skill (Phase 3)
        ├── .antigravity/
        │   ├── settings.json            # Workspace settings record
        │   └── knowledge/project-patterns.md  # Knowledge Item example
        ├── .context/
        │   ├── plaid_reference.md       # Grounding facts for the Plaid schema
        │   └── design_tokens.md         # Glassmorphism design system
        ├── prompts/
        │   ├── classify.prompt          # Transaction classification (Dotprompt)
        │   └── waste-detect.prompt      # Subscription waste detection
        ├── src/
        │   ├── app/                     # Next.js App Router pages and API routes
        │   ├── components/              # TransactionList, WasteCard
        │   └── lib/                     # ai.ts (Genkit instance), genkit.ts (flows), mock-data.ts
        ├── genkit-server.ts             # Entry point for the Genkit Developer UI
        ├── .env.example                 # Environment template (GEMINI_API_KEY, Plaid, USE_MOCK_DATA)
        ├── .eslintrc.json               # ESLint config for npm run lint
        ├── jest.config.js
        ├── package.json
        ├── package-lock.json            # Exact dependency versions, for npm ci
        ├── tsconfig.json
        ├── tailwind.config.ts
        └── postcss.config.js
```

## Prerequisites

- Node.js 22 or newer (24 LTS recommended), and npm. MoneyMind was tested on Node 20.20, 22.23, and 24.13. Node 18 cannot run `npm run genkit`, which needs Node's `--env-file` flag.
- Google Antigravity IDE ([antigravity.google/download](https://antigravity.google/download))
- The Antigravity CLI: `curl -fsSL https://antigravity.google/cli/install.sh | bash`, then `agy install`, on macOS and Linux. On Windows, run `irm https://antigravity.google/cli/install.ps1 | iex` in PowerShell (the [CLI guide](./tutorials/antigravity-cli-guide.md#installation) has the CMD variant)
- A Gemini API key for Genkit ([aistudio.google.com/apikey](https://aistudio.google.com/apikey)). The IDE and CLI sign in with your Google account. This key is only for the Genkit layer.
- Working familiarity with TypeScript and React

## Quick Start

```bash
cd chapter-06/hands-on-lab/moneymind
npm ci                    # installs the exact versions in package-lock.json
cp .env.example .env      # then add your GEMINI_API_KEY (Windows: copy .env.example .env)
npm test                  # mock-data and Plaid-mapping tests, no API key needed
npm run dev               # dashboard at http://localhost:3000
npm run genkit            # Genkit Developer UI at http://localhost:4000
```

Run `npm test` first to check that your clone is intact. It needs no API key and calls no model. It should report `Tests: 7 passed, 7 total`. `npm run build` and `npm run lint` also run without a key. Then follow `hands-on-lab/README.md` from Phase 1.

## Learning Path

| Step | Resource | Time |
|------|----------|------|
| 1 | [Antigravity setup](./tutorials/antigravity-setup.md) | 20-30 min |
| 2 | [Intent-first workflow](./tutorials/intent-first-workflow.md) | 25-35 min |
| 3 | [Antigravity CLI guide](./tutorials/antigravity-cli-guide.md) | 30-40 min |
| 4 | [Genkit setup](./tutorials/genkit-setup.md) | 25-35 min |
| 5 | [Hands-on lab: MoneyMind](./hands-on-lab/README.md) | 2.5 hours |
| 6 | [Exercise 1: Intent-first](./hands-on-lab/exercises/exercise-1-intent-first.md) | 30-45 min |
| 7 | [Exercise 2: Antigravity CLI](./hands-on-lab/exercises/exercise-2-antigravity-cli.md) | 35-45 min |
| 8 | [Exercise 3: Artifacts](./hands-on-lab/exercises/exercise-3-artifacts.md) | 30-40 min |

## Additional Resources

- [Antigravity documentation](https://antigravity.google/docs)
- [Antigravity CLI reference](https://antigravity.google/docs/cli/reference)
- [Genkit getting started](https://genkit.dev/docs/get-started/)

## Navigation

- **Previous**: [Chapter 5 - The Architecture of Intent: Mastering Kiro](../chapter-05/README.md)
- **Next**: [Chapter 7 - Cursor and GitHub Copilot (Agent Mode): Mainstream AI Integration](../chapter-07/README.md)
