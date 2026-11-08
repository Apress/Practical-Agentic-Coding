# MoneyMind - Agentic Financial Dashboard

This is the lab project for Chapter 6, Section 6.6. MoneyMind reads raw bank transaction data and does three jobs:

- It categorizes transactions with an AI flow.
- It normalizes messy merchant strings.
- It flags subscriptions you pay for but do not use.

The project shows these techniques:

- **Intent-first development**: You direct the agent. The agent writes the code.
- **Observable AI flows**: Every model call and tool call shows up as a Genkit trace.
- **Hybrid context**: Native context for the code, `.context/` files for domain facts, MCP for outside systems.
- **Agent Skills**: `/money-audit` is a terminal command defined in one markdown file.

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | Next.js 15 (App Router) |
| Styling | Tailwind CSS |
| AI flows | Firebase Genkit |
| Prompts | Dotprompt with Picoschema |
| Terminal agent | Antigravity CLI (`agy`) |
| Testing | Jest with ts-jest |

## Getting Started

### Prerequisites

- Node.js 22 or newer (24 LTS recommended). Tested on Node 20.20, 22.23, and 24.13. Node 18 cannot run `npm run genkit`, which uses Node's `--env-file` flag.
- A Gemini API key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
- Google Antigravity IDE, for the agent-driven parts of the lab
- The Antigravity CLI, for Phase 3: `curl -fsSL https://antigravity.google/cli/install.sh | bash`, then `agy install`

The IDE and CLI sign in with your Google account. The API key is only for the Genkit layer.

### Install

```bash
cd chapter-06/hands-on-lab/moneymind
npm ci
cp .env.example .env
# edit .env and set GEMINI_API_KEY
```

`npm ci` installs the exact dependency versions recorded in `package-lock.json`. This project was tested with those versions. On Windows, copy the template with `copy .env.example .env` (CMD) or `Copy-Item .env.example .env` (PowerShell).

### Verify your clone

```bash
npm test
```

The tests cover the mock data and Plaid field mapping. They need no API key and call no model. A pass (`Tests: 7 passed, 7 total`) means your clone and toolchain work. `npm run build` and `npm run lint` need no key either.

### Run

```bash
npm run dev      # dashboard at http://localhost:3000
npm run genkit   # Genkit Developer UI at http://localhost:4000
```

Run them in two terminals. The lab uses both at once.

`npm run genkit` runs `genkit start -- npx tsx --env-file=.env genkit-server.ts`. Keep the `--` part. A bare `npx genkit start` cannot find your flow definitions, so the Developer UI shows an empty flow list.

## Project Layout

```text
moneymind/
├── .agents/                  # Cross-tool agent configuration
│   ├── rules/project-rules.md          # Workspace governance (lab Phase 1)
│   └── skills/money-audit/SKILL.md     # The /money-audit skill (lab Phase 3)
├── .antigravity/
│   ├── settings.json                   # Record of the workspace decisions
│   └── knowledge/project-patterns.md   # Knowledge Item example
├── .context/                 # Facts that ground the agent's reasoning
│   ├── plaid_reference.md              # Which Plaid fields to trust
│   └── design_tokens.md                # Glassmorphism design system
├── prompts/                  # Dotprompt files
│   ├── classify.prompt                 # Transaction classification
│   └── waste-detect.prompt             # Subscription waste detection
├── src/
│   ├── app/
│   │   ├── api/transactions/route.ts   # GET, mock or Plaid via USE_MOCK_DATA
│   │   ├── api/enrich/route.ts         # POST, runs the Genkit flows
│   │   ├── layout.tsx
│   │   ├── page.tsx                    # Dashboard
│   │   └── globals.css
│   ├── components/
│   │   ├── TransactionList.tsx
│   │   └── WasteCard.tsx
│   └── lib/
│       ├── ai.ts                       # The one configured Genkit instance
│       ├── genkit.ts                   # Flows and schemas
│       ├── mock-data.ts                # Plaid-shaped sample transactions
│       └── mock-data.test.ts
├── genkit-server.ts          # Entry point for the Developer UI
├── .env.example              # Environment template
├── .eslintrc.json            # ESLint config for npm run lint
├── jest.config.js
├── package.json
├── package-lock.json         # Exact dependency versions, for npm ci
├── tsconfig.json
├── tailwind.config.ts
└── postcss.config.js
```

## How the Genkit Wiring Works

**Call `genkit({...})` once and share the result.**

- `src/lib/ai.ts` creates that single instance.
- `src/lib/genkit.ts` imports it to define flows.
- `genkit-server.ts` imports both, so the Developer UI has flows to show.
- The API routes import the flows.

A second `genkit()` call gets its own registry. Flows defined on it are invisible to the first one. The Developer UI then shows an empty list, even though the code looks fine. `import { ai } from '@genkit-ai/core'` does not work either. That package exports no such object.

### Flows

| Flow | Input | Output |
|------|-------|--------|
| `classifyTransactionFlow` | The classify prompt's own shape: `description`, `amount`, `currency`, optional `merchant_hint` | The enrichment alone (category, clean merchant, recurring flag, optional confidence). The evaluation target for `npx genkit eval:flow classifyTransactionFlow --input ../../code-examples/genkit/evaluation-dataset.json`, once you add an evaluator plugin (see `../../code-examples/genkit/README.md`) |
| `enrichTransactionFlow` | One Plaid transaction | The same transaction plus `enrichment` (category, clean merchant, recurring flag, optional confidence) |
| `batchEnrichFlow` | An array of Plaid transactions | The array enriched, with per-item failures isolated so one bad transaction does not sink the batch |
| `detectWasteFlow` | Enriched transactions and a period in days | A waste report: flagged items, monthly cost, and a total |

The book's Listing 6-3 sketches this pattern as `src/agents/WasteWatcher.ts` with an `analyzeWaste` flow. That file is illustrative. The working version here is `detectWasteFlow` in `src/lib/genkit.ts`. Its schemas are defined in the same file, not in a separate `schemas/` directory.

The Plaid-facing and prompt-facing schemas use snake_case, because the API and the `.prompt` files use it. No translation layer is needed.

### Prompts

Both `.prompt` files declare their schemas in Picoschema. Follow these two syntax rules when you edit them:

- Enums and arrays use a parenthetical type on the key: `category(enum, description): [A, B]` and `items(array): {...}`. A nested `enum:` or `type: array` block is JSON Schema and throws "unsupported scalar type" at load time.
- A `?` suffix on a key makes the field optional: `merchant_hint?: string`.

Each file pins its own model:

- `classify.prompt` uses a Flash-class model. It runs on every transaction.
- `waste-detect.prompt` uses a Pro-class model. It reasons over a whole history.

Model names change between releases. Check what your account offers before you pin a specific version.

## API Reference

### GET /api/transactions

Returns transactions. It uses mock data unless `USE_MOCK_DATA=false`. With `USE_MOCK_DATA=false`, it needs `PLAID_CLIENT_ID` and `PLAID_SECRET`.

Query parameters: `limit`, `category` (Plaid primary category), `startDate`, `endDate` (both `YYYY-MM-DD`).

> The real Plaid path is left unimplemented on purpose and returns 501. Wiring it up is the second chapter challenge.

### POST /api/enrich

Runs the enrichment flows. Send `{ "transaction": {...} }` for one transaction, or `{ "transactions": [...] }` for a batch. Both return `{ success, data, meta }`.

## Working With the Agent

### Plan mode

For a change that touches several files:

1. Switch the Agent Manager to Plan mode with a Pro-class model.
2. Read the Implementation Plan artifact it produces.
3. Comment on it.
4. Approve it.

### The Constraint Sandwich

```text
Top bun:    "Act as a senior fintech architect..."
Meat:       "Create a WasteCard.tsx component that..."
Bottom bun: "DO NOT use raw CSS; use ONLY Tailwind..."
```

### The /money-audit skill

Launch `agy` in this directory. Run the skill as a plain slash command:

```text
/money-audit ./
```

The skill is defined in one file, `.agents/skills/money-audit/SKILL.md`. The folder name is the command name. There is no namespace or colon syntax.

### Generating documentation

```bash
agy -p "As a technical writer, read package.json and write a professional DEVELOPER_GUIDE.md for the MoneyMind application"
```

## Testing

```bash
npm test                # everything
npm run test:watch      # watch mode
npm run test:coverage   # with coverage
npm run typecheck       # tsc --noEmit
npm run lint            # next lint (one expected warning: WasteCard uses a plain <img>; Next.js 15 also notes that next lint is deprecated)
npm run build           # production build; needs network access for the Google Fonts download
```

`npm run build` also prints "Compiled with warnings" about an optional OpenTelemetry module (`@opentelemetry/exporter-jaeger` not found). The warning comes from Genkit's telemetry dependencies. It does not fail the build.

The shipped tests are node-environment tests over deterministic logic. Component tests need a DOM. To add them:

1. Install `jest-environment-jsdom` and `@testing-library/react`.
2. Switch `testEnvironment` to `'jsdom'` in `jest.config.js`.

## Security

- No hardcoded keys. Everything sensitive comes from the environment.
- `.env` is in `.gitignore`. That also keeps it out of the agent's perception engine.
- API routes validate input with Zod and return sanitized errors.
- `/money-audit` checks all of the above on demand.

### Why Next.js 15, not 14

Next.js 14 has critical advisories with no 14.x fix, among them [GHSA-p293-qw3h-jr36](https://github.com/advisories/GHSA-p293-qw3h-jr36) (remote code execution on servers hosted on Windows), [GHSA-2xp9-vwfh-vxw4](https://github.com/advisories/GHSA-2xp9-vwfh-vxw4) (remote code execution in the image optimizer with AVIF files), and [GHSA-2464-fhr4-w9xw](https://github.com/advisories/GHSA-2464-fhr4-w9xw) (remote code execution in the image optimizer with SVG files, fixed in 15.5.28). So the reference app uses Next.js 15.5. If the Step 1.4 prompt you follow asks for Next.js 14, ask for Next.js 15 instead.

MoneyMind is a learning project, not a production app. Its dependencies are locked to the versions this lab was tested with. New vulnerabilities (CVEs) are published against packages like these all the time, so `npm audit` will flag some. Before you build anything real on top of this project, check the advisories yourself and update the dependencies.

## License

Educational use with *Practical Agentic Coding* (Apress, 2026). See the LICENSE.txt at the repository root.
