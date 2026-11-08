# Firebase Genkit Examples

This is reference material for Chapter 6, Section 6.5 (Genkit as the observability layer). Read these files and adapt them. They are not a runnable project. The MoneyMind lab in `../../hands-on-lab/moneymind/` is the part that runs.

> **Book listing vs repo:** Listing 6-3 in the book sketches a file `src/agents/WasteWatcher.ts` with an `analyzeWaste` flow importing `../schemas/TransactionSchema`. That layout is illustrative. It is not a repo file. The working version is `detectWasteFlow` in the lab's [`src/lib/genkit.ts`](../../hands-on-lab/moneymind/src/lib/genkit.ts), where the schemas live in the same module.

## Files

| File | What it is |
|------|-----------|
| `flow-patterns.ts` | Eight flow patterns: typed flows, error handling, batching, named spans, streaming, branching, retries, composition |
| `evaluation-dataset.json` | A golden dataset of 13 labeled transactions covering all six MoneyMind categories |

## The one rule that breaks projects

Call `genkit({...})` **once** and share the result.

- `@genkit-ai/core` does not export a ready-made `ai` object. `import { ai } from '@genkit-ai/core'` will not compile.
- If two modules each call `genkit()`, each gets its own registry. Flows defined on one are invisible to the other. The Developer UI then shows an empty flow list, even though your code looks fine.

MoneyMind keeps its instance in `src/lib/ai.ts` and imports it everywhere else.

## Using flow-patterns.ts

Read it, then copy the pattern you need. The prompts it references (`simple-qa`, `process-data`, and the rest) are not included, so the file will not run as-is. Point each pattern at your own `.prompt` files.

Note these two API details:

- `ai.run(name, fn)` takes the span name as a plain string. That name labels the span in the trace waterfall.
- Streaming flows declare a `streamSchema` and receive `sendChunk` as the second argument to the flow function. Call `sendChunk` per chunk. Still return the complete output.

## Using evaluation-dataset.json

The Genkit CLI reads a golden dataset as a flat JSON array of `{ testCaseId, input, reference }` entries.

- Each `input` here uses the classify prompt's shape (`description`, `amount`, `currency`, optional `merchant_hint`).
- So evaluate `classifyTransactionFlow`. It is MoneyMind's thin flow over `classify.prompt` and takes exactly that shape.
- Do not point this dataset at `enrichTransactionFlow`. That flow requires a full Plaid transaction (`transaction_id`, `iso_currency_code`, and so on). Every case would fail Zod validation before the model is called.

`genkit eval:flow` scores the flow's answers with the evaluators your app registers. MoneyMind as shipped registers none. Until you add one, the command below stops with `No evaluators found in your app`.

1. Install the evaluator plugin: `npm install @genkit-ai/evaluator`.
2. Add `genkitEval({ metrics: [...] })` to the plugins list in `src/lib/ai.ts`.
3. Note the metric needs. The LLM-judged metrics (`FAITHFULNESS`, `ANSWER_RELEVANCY`, `ANSWER_ACCURACY`) need a `judge` model. `DEEP_EQUAL` needs no model, but it requires an exact match with `reference`. The optional `confidence` field the classify prompt returns would fail every case unless you drop it.

Then run it with the Developer UI already running:

```bash
cd ../../hands-on-lab/moneymind
npm run genkit                 # in one terminal
npx genkit eval:flow classifyTransactionFlow \
  --input ../../code-examples/genkit/evaluation-dataset.json
```

- `--evaluators` selects a subset of the registered evaluators.
- Each run calls the model once per case. LLM-judged metrics call the judge model too. Both use your Gemini quota.
- Keep this file in version control. When you change a prompt, re-run it and see which cases changed.

## Related

- [Genkit setup tutorial](../../tutorials/genkit-setup.md) for installation, the Developer UI, and reading traces
- [MoneyMind lab](../../hands-on-lab/moneymind/) for these patterns in a working project
