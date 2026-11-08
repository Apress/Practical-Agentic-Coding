# AGENTS.md - MoneyMind Project Context

This file provides essential context for AI agents working on the MoneyMind project.

## Project Overview

MoneyMind is an agentic financial dashboard that transforms bank transaction data into actionable insights. It demonstrates Intent-First Development using Google's Antigravity IDE, the Antigravity CLI (agy), and Firebase Genkit.

## Architecture

Three layers, top to bottom.

```text
UI            src/app/page.tsx
              src/components/TransactionList.tsx, WasteCard.tsx
                  |
                  v
API           GET  /api/transactions   -> mock data, or Plaid when USE_MOCK_DATA=false
              POST /api/enrich         -> runs the Genkit flows
                  |
                  v
Intelligence  src/lib/ai.ts       the single configured Genkit instance
              src/lib/genkit.ts   classifyTransactionFlow, enrichTransactionFlow,
                                  batchEnrichFlow, detectWasteFlow
                  |
                  v
Prompts       prompts/classify.prompt      (Flash-class model)
              prompts/waste-detect.prompt  (Pro-class model)
```

Everything in the intelligence layer shares the one `ai` instance from `src/lib/ai.ts`, and `genkit-server.ts` imports the flows so the Genkit Developer UI can see them.

## Key Files

| File | Purpose |
|------|---------|
| `src/lib/ai.ts` | The single configured Genkit instance. Import `ai` from here; never call `genkit()` again |
| `src/lib/genkit.ts` | Genkit flow definitions and schemas |
| `src/lib/mock-data.ts` | Mock Plaid transactions |
| `src/lib/mock-data.test.ts` | Tests for the mock data and Plaid field mapping |
| `genkit-server.ts` | Entry point that imports the flows for the Developer UI |
| `prompts/classify.prompt` | Transaction classification (Flash-class model) |
| `prompts/waste-detect.prompt` | Waste detection (Pro-class model) |
| `jest.config.js` | Jest with ts-jest, `@/` alias mapped to `src/` |
| `.agents/rules/project-rules.md` | Workspace governance |
| `.agents/skills/money-audit/SKILL.md` | Security audit skill (`/money-audit`) |
| `.context/plaid_reference.md` | Plaid schema, and which fields to trust |
| `.context/design_tokens.md` | Glassmorphism design system |

## Development Rules

1. **TypeScript only**: all code is TypeScript with strict mode
2. **Tailwind only**: no raw CSS, no CSS modules, no styled-components
3. **Jest testing**: Jest with ts-jest is the test runner
4. **Plaid schema**: read the `counterparties` array, never the legacy `merchant_name`
5. **Environment variables**: never hardcode secrets
6. **One Genkit instance**: import `ai` from `src/lib/ai.ts`; a second `genkit()` call creates a second registry and the Developer UI stops seeing your flows

## Common Tasks

### Add a New Component
1. Create it in `src/components/`
2. Use the Glassmorphism tokens from `.context/design_tokens.md`
3. Add TypeScript interfaces for the props
4. Write Jest tests (component tests need the jsdom environment; see the project README)

### Add a New Genkit Flow
1. Define it in `src/lib/genkit.ts`, importing `ai` from `./ai`
2. Add a `.prompt` file in `prompts/`, with Picoschema schemas
3. Parse the model output against a Zod schema before returning it
4. Add it to the `flows` export so `genkit-server.ts` reports it

### Add a New API Route
1. Create `src/app/api/[route]/route.ts`
2. Validate input with Zod
3. Handle errors without exposing internals
4. Respect the `USE_MOCK_DATA` toggle

## Testing

```bash
npm test              # run all tests
npm run test:watch    # watch mode
npm run test:coverage # coverage report
npm run typecheck     # tsc --noEmit
npm run lint          # next lint
```

The shipped tests need no API key and call no model, so they are the fast check that a change did not break the deterministic logic.

## Observability

```bash
npm run genkit
```

Then open http://localhost:4000. This expands to `genkit start -- npx tsx --env-file=.env genkit-server.ts`; the entry point after `--` is what lets the CLI find the flow definitions.

## Environment Setup

Required variables in `.env` (start from `.env.example`):

- `GEMINI_API_KEY`: required for Genkit
- `USE_MOCK_DATA`: `true` by default; set `false` only once real Plaid credentials exist

---

*This file gives AI agents the project context and constraints. It is the cross-tool standard context file, so any agent that reads AGENTS.md picks it up.*
