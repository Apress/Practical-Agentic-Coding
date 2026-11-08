# Firebase Genkit setup: quick reference

This guide installs and configures Genkit for the MoneyMind project. It matches Phase 2 of the lab.

- Every flow run produces a trace. You read it in the local **Genkit Developer UI**.
- After deployment, the same telemetry can feed the **Firebase Genkit Monitoring** console.

What Genkit flows, traces, and evaluation are for, and why they matter: Chapter 6, Section 6.5.

For the latest install steps and APIs, see Genkit's own guide at [genkit.dev/docs/get-started](https://genkit.dev/docs/get-started/).

> **Update to the book (as of November 7, 2026, Genkit CLI 1.44.1): the "Gemini CLI" option in `init:ai-tools`**
>
> - The `npx genkit init:ai-tools` picker says "Gemini CLI", the name of agy's predecessor. Pick it.
> - That option writes the Genkit MCP server to `.gemini/settings.json`. agy does not read that file. agy loads MCP servers only from `~/.gemini/config/mcp_config.json` and `.agents/mcp_config.json`.
> - So also run `agy mcp add genkit -- npx genkit mcp --no-update-notification`. Check that `agy mcp list` shows `genkit`.
> - If a later Genkit release renames the option (say, to "Antigravity"), pick the renamed entry.
> - The first time you run a Genkit command, it shows a cookie and analytics notice and waits for Enter.

---

## Installation

### Prerequisites

- Node.js 22 or newer (20.6 or newer works; `npm run genkit` uses Node's `--env-file` flag, which Node 18 lacks)
- npm or pnpm
- A Gemini API key

### Initialize in Your Project

Go to your MoneyMind project and run the AI-tools initializer:

```bash
cd chapter-06/hands-on-lab/moneymind
npx genkit init:ai-tools
```

When prompted, pick the **Gemini CLI** option. Then follow the update note at the top of this page.

The command configures the AI coding assistants you select:

- It registers the Genkit MCP server.
- It installs context files that describe Genkit's structure and features to the assistant.

It does not install a model plugin. The `npm install` step below does that.

### Install Dependencies

```bash
npm install genkit @genkit-ai/google-genai zod@3
```

Genkit 1.x uses Zod 3. A bare `zod` installs Zod 4, which Genkit does not accept.

---

## Project Configuration

### Environment Variables

Genkit's Google Generative AI plugin reads `GEMINI_API_KEY`. Set it in `.env`:

```bash
# Gemini API key (required)
GEMINI_API_KEY=your_api_key_here
```

Get your key at https://aistudio.google.com/apikey.

### Initialization Code

Call `genkit({...})` **once** and share the result. Breaking this rule is the most common way to break a Genkit project.

- `@genkit-ai/core` does not export a ready-made `ai` object. `import { ai } from '@genkit-ai/core'` does not compile.
- If two modules each call `genkit()`, each gets its own registry. Flows defined on one are invisible to the other. The Developer UI then shows an empty flow list, even though your code looks fine.

MoneyMind keeps the instance in its own module, so there is exactly one:

```typescript
// src/lib/ai.ts
import { genkit } from 'genkit';
import { googleAI } from '@genkit-ai/google-genai';

export const ai = genkit({
  plugins: [googleAI()],
  // Where the .prompt files live. './prompts' is the default, stated here
  // so the connection between ai.prompt('classify') and
  // prompts/classify.prompt is visible.
  promptDir: './prompts',
});
```

---

## Defining Flows

### Basic Flow Structure

Every other module imports that instance:

```typescript
// src/lib/genkit.ts
import { z } from 'zod';
import { ai } from './ai';

// Define input and output schemas
const InputSchema = z.object({
  query: z.string(),
});

const OutputSchema = z.object({
  answer: z.string(),
  confidence: z.number(),
});

// Define the flow
export const myFlow = ai.defineFlow(
  {
    name: 'myFlow',
    inputSchema: InputSchema,
    outputSchema: OutputSchema,
  },
  async (input) => {
    const prompt = ai.prompt('answer-question');
    const response = await prompt({ query: input.query });

    // Parse before returning: the model's reply is untrusted input.
    return OutputSchema.parse(response.output);
  }
);
```

### Using Dotprompt

Create prompt files in `prompts/`:

```yaml
# prompts/classify.prompt
---
model: googleai/gemini-flash-latest
config:
  temperature: 0.1
  maxOutputTokens: 1024
  thinkingConfig:
    thinkingLevel: LOW

input:
  schema:
    description: string, the raw transaction description
    amount: number
    currency: string, ISO 4217 code
    merchant_hint?: string, optional normalized merchant name

output:
  schema:
    category(enum, the spending category): [Groceries, Dining, Transport, Housing, Income, Subscription]
    clean_merchant: string, normalized merchant brand name
    is_recurring: boolean
---

Classify this financial transaction:
- Description: {{description}}
- Amount: {{amount}} {{currency}}
{{#if merchant_hint}}
- Merchant hint: {{merchant_hint}}
{{/if}}

Return the category, the normalized merchant name, and whether it recurs.
```

**Picoschema syntax** (it is not JSON Schema):

- Declare an enum with a parenthetical type on the *key*: `category(enum, description): [A, B]`. A nested `enum:` key throws "unsupported scalar type" when the prompt loads.
- Declare an array the same way: `items(array): {...}` works. `type: array / items:` does not.
- The text after the comma inside the parentheses becomes the field description.
- A `?` suffix on a key makes it optional.

**Model names age out.** `-latest` aliases track the current model in a tier. Before you pin a specific version, check the model list your account shows.

### Calling Prompts in Flows

`ai.prompt('classify')` looks up `prompts/classify.prompt` by filename. Calling it renders the template and calls the model:

```typescript
export const enrichFlow = ai.defineFlow(
  {
    name: 'enrichTransactionFlow',
    inputSchema: PlaidTransactionSchema,
    outputSchema: EnrichedTransactionSchema,
  },
  async (transaction) => {
    const classifyPrompt = ai.prompt('classify');
    const response = await classifyPrompt({
      description: transaction.name,
      amount: transaction.amount,
      currency: transaction.iso_currency_code,
      // Per .context/plaid_reference.md: counterparties, not merchant_name.
      merchant_hint: transaction.counterparties?.[0]?.name,
    });

    return {
      ...transaction,
      enrichment: EnrichmentOutputSchema.parse(response.output),
    };
  }
);
```

To give a step its own trace span, wrap it in `ai.run(name, fn)`. The name is a plain string. It becomes the span label in the waterfall.

```typescript
const document = await ai.run('fetchDocument', async () => {
  return await loadDocument(input.documentId);
});
```

---

## Starting the Genkit Developer UI

The Developer UI serves at `http://localhost:4000`. It lists only the flows that a running process has registered. A bare `npx genkit start` has no entry point to import your flow definitions, so its flow list is empty.

MoneyMind registers its flows in `genkit-server.ts`. Pass that entry point after `--`:

```bash
npx genkit start -- npx tsx --env-file=.env genkit-server.ts
```

### Using npm Scripts

MoneyMind ships this command as a script in `package.json`:

```json
{
  "scripts": {
    "genkit": "genkit start -- npx tsx --env-file=.env genkit-server.ts"
  }
}
```

Then run:

```bash
npm run genkit
```

---

## Using the Genkit Developer UI

### Dashboard Overview

The UI has these panels:
- **Flows Panel**: List of defined flows
- **Run Panel**: Execute flows with test input
- **Traces Panel**: View execution history
- **Evaluations Panel**: Run eval datasets

### Running a Flow

1. Select a flow from the left sidebar
2. Enter JSON input in the input panel
3. Click **Run**
4. View output in the result panel

### Example Input for enrichTransactionFlow

```json
{
  "transaction_id": "txn_test_001",
  "account_id": "acc_001",
  "amount": 15.99,
  "iso_currency_code": "USD",
  "date": "2024-01-15",
  "name": "NETFLIX.COM",
  "counterparties": [
    {
      "name": "Netflix",
      "type": "merchant",
      "confidence_level": "VERY_HIGH"
    }
  ],
  "payment_channel": "online",
  "pending": false
}
```

---

## Understanding Traces

### The Trace Waterfall

Each trace shows these parts:
- **Spans**: Individual steps in the flow
- **Timing**: Duration of each span
- **Input/Output**: Data at each step
- **Errors**: Any exceptions thrown

### Trace Components

```text
enrichTransactionFlow                 flow: input is the Plaid transaction, output the enriched one
└── classify                          the prompt from prompts/classify.prompt
    └── googleai/gemini-flash-latest  the model call
```

- Nearly all of the flow's time is the single model call.
- The Plaid mapping and the Zod parse run inline in the flow. They get no spans of their own. To time a step separately, wrap it in `ai.run(name, fn)`.
- Exact labels and timings vary with your Genkit version and model.

### Viewing Trace Details

1. Click **Traces** (clock icon) in the left sidebar
2. Select a trace by ID
3. Expand spans to see details
4. Check input/output for each span

### Debugging with Traces

| What the trace shows | What to check |
|----------------------|---------------|
| Long model latency | Your model selection |
| Parsing errors | Your schema definitions |
| Missing output | Your prompt template |
| Repeated calls | Your flow logic |

---

## Evaluation-Driven Development

### Creating Golden Datasets

A golden dataset is a set of inputs with known answers. The Genkit CLI reads it as a **flat JSON array**. Each entry has these fields:

- `input`: what the flow receives.
- `reference` (optional): the known-good answer.
- `testCaseId` (optional).

```json
[
  {
    "testCaseId": "dining-001",
    "input": {
      "description": "STARBUCKS #12345",
      "amount": 5.5,
      "currency": "USD"
    },
    "reference": {
      "category": "Dining",
      "clean_merchant": "Starbucks",
      "is_recurring": false
    }
  },
  {
    "testCaseId": "subscription-001",
    "input": {
      "description": "NETFLIX.COM",
      "amount": 15.99,
      "currency": "USD"
    },
    "reference": {
      "category": "Subscription",
      "clean_merchant": "Netflix",
      "is_recurring": true
    }
  }
]
```

`code-examples/genkit/evaluation-dataset.json` in this chapter is a fuller version. It covers all six categories.

Run it against the flow whose input schema matches the dataset. These entries use the classify prompt's shape. In MoneyMind, that is `classifyTransactionFlow`. Do not use `enrichTransactionFlow`: it requires a full Plaid transaction, so it would reject every case at the Zod boundary.

```bash
npx genkit eval:flow classifyTransactionFlow --input ../../code-examples/genkit/evaluation-dataset.json
```

Before you run it:

1. Work from the `moneymind/` directory.
2. Start the Developer UI (`npm run genkit`), so the CLI can reach your flows.
3. Register at least one evaluator. MoneyMind ships without one. Run `npm install @genkit-ai/evaluator`, then add `genkitEval({ metrics: [...] })` to the plugins list in `src/lib/ai.ts`. Without an evaluator, the CLI stops with `No evaluators found in your app`.

### Evaluation Metrics

| Metric | Needs a judge model? |
|--------|----------------------|
| **Faithfulness** (`FAITHFULNESS`) | Yes |
| **Relevance** (`ANSWER_RELEVANCY`) | Yes, plus an embedder |
| **Accuracy** (`ANSWER_ACCURACY`) | Yes |
| **Exact match** (`DEEP_EQUAL`) | No |

- `--evaluators` selects a subset of what you registered.
- Latency is not an evaluator. Read it off the trace.

What each metric measures and when to run evaluations: Chapter 6, Section 6.5.

---

## Production Observability

After deployment, the same flows can send their telemetry to the **Firebase Genkit Monitoring** console. MoneyMind does not turn this on. To turn it on, follow the [Genkit monitoring guide](https://genkit.dev/docs/observability/getting-started/):

1. Install the Firebase plugin: `npm install @genkit-ai/firebase`.
2. Enable telemetry. Either set `ENABLE_FIREBASE_MONITORING=true` in the deployment environment, or call `enableFirebaseTelemetry()` from `@genkit-ai/firebase` in `src/lib/ai.ts`.
3. Enable the Cloud Logging, Cloud Trace, and Cloud Monitoring APIs in the Google Cloud project. The project must be on the Firebase Blaze plan.
4. Grant the service account that runs the app the Monitoring Metric Writer, Cloud Trace Agent, and Logs Writer roles.

5. Deploy.
6. Run a flow.
7. Open Genkit Monitoring in the Firebase console. The first metrics can take a few minutes to appear.

---

## Troubleshooting

### "Cannot find flow definitions"

Check that your flows are exported. Check that you pass the right entry file:

```bash
npx genkit start -- npx tsx --env-file=.env genkit-server.ts
```

### "API key not found"

Set the environment variable:

```bash
export GEMINI_API_KEY=your_key
```

Or use `--env-file`:

```bash
npx tsx --env-file=.env genkit-server.ts
```

### "Port 4000 already in use"

```bash
npx genkit start --port 4001 -- npx tsx --env-file=.env genkit-server.ts
```

### Traces not appearing

1. Verify tracing is enabled in your Genkit initialization
2. Check trace store configuration
3. Ensure the flow completed (check for errors)

---

## Quick Reference

### CLI Commands

| Command | Purpose |
|---------|---------|
| `npx genkit init:ai-tools` | Wire your AI coding assistant up with Genkit context files |
| `npx genkit start -- <run command>` | Start the Developer UI with your app as the entry point |
| `npx genkit flow:run <flow> '<json>'` | Run one flow from the terminal |
| `npx genkit flow:batchRun <flow> <file>` | Run a flow over a JSON batch of inputs |
| `npx genkit eval:flow <flow> --input <file>` | Evaluate a flow against a golden dataset |
| `npx genkit trace:list` | List recent traces |

Command names and flags change between releases. Run `npx genkit --help` for the list that matches your installed version.

---

## Next Steps

- Complete the [MoneyMind lab](../hands-on-lab/README.md)
- Learn the [Intent-First workflow](./intent-first-workflow.md)
- Master the [Antigravity CLI](./antigravity-cli-guide.md)
- Review [code examples](../code-examples/)
