# Hands-On Lab: Building MoneyMind

Maps to Chapter 6, Section 6.6.

## Lab Overview

You will build **MoneyMind**, a financial dashboard. It classifies bank transactions and flags wasted subscription spend. In this lab the agents write most of the code. You prompt, review plans, and approve. You use three tools:

- **Antigravity IDE** for agent management and development
- **Genkit** for the intelligence layer and its traces
- **Antigravity CLI (`agy`)** for terminal work

The four phases take about 2.5 hours. When every item in the completion checklist near the end of this file is done, you are done.

> **As of November 7, 2026.** The prompts below match the book's Section 6.6 word for word (without the `>` prompt marker the book prints for `agy`). Where current tools differ from the book, follow this file:
>
> - Genkit's `init:ai-tools` (Step 2.1) configures your AI coding tool. It does not install the Gemini plugin.
> - The project needs Node.js 20.6 or newer (22 or 24 LTS recommended).
> - The reference app uses Next.js 15.5 (see the note under Step 1.4).
> - Antigravity loads a file in `.agents/rules/` only if it has a valid `trigger` in its frontmatter (see Step 1.2).
> - The Genkit MCP server needs a separate `agy mcp add` step (see Step 2.1).
> - On the Free and Google AI Plus plans, use the Flash-class model with the High thinking level (see Step 4.1).

## Learning Outcomes

By completing this lab, you will:

1. Configure Antigravity workspace governance and context injection
2. Build observable AI flows with Genkit and Dotprompt
3. Create an Agent Skill for the Antigravity CLI, invoked as a plain slash command
4. Integrate frontend, backend, and observability layers
5. Use the browser subagent for autonomous verification

## Prerequisites

### Software

- [Google Antigravity IDE](https://antigravity.google/download)
- Node.js 22 or newer (24 LTS recommended), and npm. Node 18 cannot run `npm run genkit`, which uses Node's `--env-file` flag.
- The Antigravity CLI. On macOS and Linux, run `curl -fsSL https://antigravity.google/cli/install.sh | bash`, then `agy install`. On Windows, run `irm https://antigravity.google/cli/install.ps1 | iex` in PowerShell.
- Git

### API key

You need one key, for Genkit only (Phase 2 onward):

```bash
GEMINI_API_KEY=your_gemini_api_key
```

Get it at [aistudio.google.com/apikey](https://aistudio.google.com/apikey). The Antigravity IDE and CLI authenticate through your system keyring or Google Sign-In. They need no key locally.

### Two ways to work this lab

**Build it yourself with the agent (recommended).** Start from an empty folder. Work from Phase 1 forward. Let Antigravity generate each file from the prompts below. The finished project in `moneymind/` is your answer key.

**Or start from the finished project.** Use this if you want to read working code first, or if a phase stalls:

```bash
cd chapter-06/hands-on-lab/moneymind
npm ci                    # installs the exact versions in package-lock.json
cp .env.example .env      # then add your GEMINI_API_KEY (Windows: copy .env.example .env)
npm test                  # mock-data tests, no API key needed: expect "Tests: 7 passed, 7 total"
npm run dev               # http://localhost:3000
```

Either way, do not skip the artifact reviews. Read each plan before the agent writes code.

## Lab Phases

| Phase | Focus | Time |
|-------|-------|------|
| 1 | Mission control and governance: rules, context files, scaffolding | 30 min |
| 2 | The intelligence layer: Genkit flows with Dotprompt | 45 min |
| 3 | Terminal intelligence: an Agent Skill and generated docs | 30 min |
| 4 | Full system integration and trace verification | 45 min |

---

## Phase 1: Mission Control & Governance

### Step 1.1: Environment Initialization

Install any extensions you need from the Extensions view. Antigravity's default extension source is the **Open VSX Registry**. You can change the source in IDE settings. If the registry lacks an extension, download its `.vsix` and install it through the "..." menu of the Extensions view.

### Step 1.2: Establishing Governance

Add a rules file under `.agents/rules/` that sets the project's global constraints.

**Open Antigravity Chat and enter:**

```text
Create (an) antigravity rules file that mandates TypeScript for all code,
Tailwind for all styling, and Jest for all testing.
```

The agent creates a rules file (for example `.agents/rules/project-rules.md`) with the three workspace constraints.

As of November 7, 2026, Antigravity loads a file in `.agents/rules/` only if it starts with YAML frontmatter that sets a valid `trigger` (for example `trigger: always_on`). Check that the file the agent wrote has it.

### Step 1.3: Context Injection

Add domain-specific knowledge for the agent to use.

**Prompt:**

```text
Create a technical reference file at .context/plaid_reference.md. In this
file, document the structure of a standard Plaid Transaction object.
Explicitly state that the agent should ignore the legacy merchant_name field
and instead use the counterparties array and merchant_entity_id for
identifying merchants. Include a JSON example of a transaction showing these
fields so you have a grounded reference for future coding tasks.
```

### Step 1.4: Project Scaffolding

Open the **Agent Manager** view (standalone Antigravity app). Give an agent the prompt below. It uses the Constraint Sandwich shape (persona, requirements, negative constraints). To edit by hand, open the IDE from the manager.

**Prompt:**

```text
Initialize a Next.js project named 'MoneyMind' with App Router and
Tailwind. Use the Constraint Sandwich: Include a components and lib folder. Do
NOT include a pages directory.
```

> **Why no version in the prompt.** Next.js 14 has critical advisories with no 14.x fix, among them [GHSA-p293-qw3h-jr36](https://github.com/advisories/GHSA-p293-qw3h-jr36), [GHSA-2xp9-vwfh-vxw4](https://github.com/advisories/GHSA-2xp9-vwfh-vxw4), and [GHSA-2464-fhr4-w9xw](https://github.com/advisories/GHSA-2464-fhr4-w9xw). So the prompt lets the agent scaffold a current release. The reference app uses Next.js 15.5.

---

## Phase 2: The Intelligence Layer (Genkit & Dotprompt)

### Step 2.1: Genkit Initialization

In your terminal:

```bash
npx genkit init:ai-tools
```

1. Pick the **Gemini CLI** option. The book recommends this entry for the Antigravity CLI workflow (Section 6.4).
2. Register the Genkit MCP server with agy: `agy mcp add genkit -- npx genkit mcp --no-update-notification`.
3. Check that `agy mcp list` shows `genkit`.

In Genkit CLI 1.44, `init:ai-tools` configures the AI coding assistants you select. It registers the Genkit MCP server and installs context files that describe Genkit's structure and features to the assistant. It writes the MCP server entry to the project's `.gemini/settings.json`. agy does not read that file. As of agy 1.4.2, its `/mcp` panel lists servers from `~/.gemini/config/mcp_config.json` and `.agents/mcp_config.json` only. That is why step 2 is needed.

> **Note:** As of November 7, 2026 (Genkit CLI 1.44.1), the picker says "Gemini CLI", the name of agy's predecessor. If a later Genkit release renames the entry (say, to "Antigravity"), pick the renamed one.
>
> This step does not install the Google Generative AI plugin. The Gemini models come from the `@genkit-ai/google-genai` package. MoneyMind's `package.json` already lists it. In a fresh project, add it with `npm install genkit @genkit-ai/google-genai`.
>
> The first time you run a Genkit command, it prints a cookie and analytics notice and waits for Enter.

### Step 2.2: Defining Schema with Picoschema

Create the transaction classification prompt.

**Prompt:**

```text
Act as a Fintech Architect. Create a new file at prompts/classify.prompt using
the Dotprompt format. Use Picoschema for the schema definitions to ensure
better token efficiency.

Define an input schema for description, amount, and currency. Define an output
schema with:

* category: An enum of [Groceries, Dining, Transport, Housing, Income,
  Subscription].
* clean_merchant: A normalized brand name string.
* is_recurring: A boolean.

In the prompt body, use Handlebars conditional logic to check for an optional
merchant_hint field. Output ONLY the code for the .prompt file.
```

> **Check the schema syntax the agent produces.** Picoschema is not JSON Schema, and models often write JSON Schema by mistake. Enums and arrays take a parenthetical type on the *key*:
>
> ```yaml
> category(enum, the spending category): [Groceries, Dining, Transport]
> transactions(array):
>   merchant: string
> ```
>
> - A nested `enum:` key or a `type: array` / `items:` block throws "Picoschema: unsupported scalar type" when the prompt loads.
> - A `?` suffix (`merchant_hint?: string`) marks a field optional.
> - Check the model it pins. Pick a Flash-class model for this high-volume classification step. Confirm the name exists in your account. Do not trust the name the agent guessed.
>
> **Difference from the book:** The reference project's `classify.prompt` adds a fourth output field, `confidence` (a 0-to-1 score). The prompt above asks for three. The flow's Zod schema keeps `confidence` optional, so a prompt written exactly per the book still parses. Add it once the basics work.

### Step 2.3: Implementing the Flow

Create the enrichment flow that maps Plaid data to your schema.

**Prompt:**

```text
Create src/lib/genkit.ts and define a Genkit Flow named enrichTransactionFlow.
This flow must map raw data from the Plaid API to our classify.prompt schema.
Specifically, extract the merchant name from Plaid's counterparties array (use
it as merchant_hint) and map iso_currency_code to our currency field. Ensure
the function is strongly typed and observable.
```

> **Check the agent's output.** Call `genkit({...})` **once** and share the result. Check for these two common mistakes:
>
> - `import { ai } from '@genkit-ai/core'` will not compile. That package exports no such object.
> - A second `genkit()` call in a second file creates a second registry. Flows defined on one are invisible to the other. The Developer UI then shows an empty flow list, even though the code looks fine.
>
> The reference project keeps the instance in its own module, `src/lib/ai.ts`. Every other file imports it. If the agent puts a `genkit()` call into `src/lib/genkit.ts`, ask it to move the instance out.

### Step 2.4: Developer UI Verification

Launch the Genkit Developer UI. It needs an entry point that imports your flows. Pass it after `--`:

```bash
npm run genkit
```

That runs `genkit start -- npx tsx --env-file=.env genkit-server.ts`. A bare `npx genkit start` cannot find your flow definitions, so its flow list is empty.

The first run downloads the Developer UI itself from Google (storage.googleapis.com), so it needs network access. Offline, or behind a proxy that blocks that host, it fails with `EAI_AGAIN`.

1. Open `http://localhost:4000`.
2. Select `enrichTransactionFlow`.
3. Paste a sample Plaid transaction. `src/lib/mock-data.ts` has ready-made ones. Try the Starbucks entry first.
4. Confirm the category is right.
5. Open the **Trace View** to see the model's intermediate steps.

### Step 2.5: Developing Application UI

Switch to **Plan Mode** for complex UI development.

**Sandwich Prompt:**

```text
Act as a senior fintech UI/UX architect for Top Bun (Persona & Standards).
Reference the @.context/design_tokens.md to create a WasteCard.tsx component
that adheres to our established Glassmorphism theme.

The meat (functional requirements): The card must display a normalized
merchant logo, a monthly cost badge in high-contrast red, and a 'Usage: 0
days' warning. It must include a 'Cancel Subscription' action button.

Bottom bun (negative constraints): DO NOT use raw CSS; use ONLY Tailwind
utility classes. DO NOT use external icon libraries. Output an Implementation
Plan Artifact for my review before writing any TSX code.
```

---

## Phase 3: Terminal Intelligence (Antigravity CLI)

In this phase you add a **skill** to the `agy` terminal agent. A skill is a `SKILL.md` file under `.agents/skills/`. agy exposes it as a slash command named after its folder. (To convert legacy Gemini CLI custom commands into skills, run `agy plugin import gemini`.)

### Step 3.1: Bootstrapping the Skill Structure

Create the skill folder. Each skill has its own folder. The `SKILL.md` inside holds YAML frontmatter plus markdown instructions.

```bash
mkdir -p .agents/skills/money-audit
```

### Step 3.2: Creating the Security Auditor

Launch `agy`. Use the prompt below so the agent writes the `SKILL.md` itself. This keeps the frontmatter valid.

**Prompt (inside agy):**

```text
Act as a senior security engineer. Create a skill file at
'.agents/skills/money-audit/SKILL.md'. Use YAML frontmatter with the
description: 'Audits MoneyMind for security compliance.'
In the markdown body, instruct the agent to scan the files or directory
the user names for hardcoded Plaid secrets, missing environment
variables, and improper error handling.
Output ONLY the SKILL.md content.
```

**Usage:**

1. Run `/skills reload` (or start a new conversation) so agy registers the new skill.
2. Type `/money-audit ./` in your agy session.
3. Review the findings and the fixes the agent proposes.

A complete example skill is provided at [moneymind/.agents/skills/money-audit/SKILL.md](./moneymind/.agents/skills/money-audit/SKILL.md).

### Step 3.3: Generating the Developer Guide

Generate the project docs from inside `agy`. The agent reads `package.json` and the file tree directly.

```text
As a technical writer, read package.json and write a professional
DEVELOPER_GUIDE.md for the MoneyMind application. Include installation
steps for the local environment for Windows OS and MacOS, environment
setup for GEMINI_API_KEY, and a summary of the /money-audit skill.
Write ONLY the markdown to the file without any additional details.
```

---

## Phase 4: Full System Integration & Verification

### Step 4.1: Bootstrapping the Mock Backend

Use the **Agent Manager** view in **Plan Mode**. Select a Pro-class (thinking-tier) model. This task is architectural.

> **On the Free and Google AI Plus plans.** As of November 7, 2026, the only Gemini model Antigravity offers on these plans is a Flash-class one. Select it with the High thinking level for this step and Step 4.2. [antigravity.google/docs/models](https://antigravity.google/docs/models) lists the models each plan includes.

**Prompt:**

```text
Act as a senior backend architect. Study the .context/plaid_reference.md and
create a Next.js API route at app/api/transactions/route.ts. Use the existing
UI sample data to populate the mock responses so our testing remains
consistent with the current dashboard experience. Ensure the JSON strictly
follows the Plaid schema.

Also, the mock and the real API integration should be configurable with an
easy toggle through configuration. Write API testing scripts using Jest.
```

> **On the path.** Step 1.4 scaffolded the project with a `src/` directory. So the route belongs at `src/app/api/transactions/route.ts`. The reference project puts it there. The agent should work this out from the existing tree. If the plan proposes a top-level `app/`, say so before you approve. The URL is `/api/transactions` either way.
>
> The toggle is `USE_MOCK_DATA` in `.env`. In the reference project:
>
> - `USE_MOCK_DATA=false` without Plaid credentials returns a clear error. It does not fail silently.
> - The real Plaid call is left unimplemented on purpose (it returns 501). Wiring it up is the second chapter challenge.

### Step 4.2: Transaction Component Integration

Use the same setup as Step 4.1 (Agent Manager, Pro-class model). This step builds the frontend logic.

**Prompt:**

```text
Act as a senior frontend engineer. Create TransactionList.tsx to fetch data
from our mocked /api/transactions endpoint. Map the Plaid fields (description,
amount) and display the enrichment results from our enrichTransactionFlow.
Generate an Implementation Plan Artifact first.
```

Component files go in `src/components/`, per the rules from Phase 1.

### Step 4.3: Starting the Observability Server

A bare `npx genkit start` cannot find your flow definitions. Tell the CLI how to run your code. The entry point after `--` imports the flows and so registers them:

```bash
npx genkit start -- npx tsx --env-file=.env genkit-server.ts
```

The project ships this as `npm run genkit`. Either way, open `http://localhost:4000` for the **Genkit Developer UI**.

If the flow list is empty, the cause is almost always a second Genkit instance. Something called `genkit({...})` a second time, and the flows registered on a registry the UI is not reading. Keep one instance and import it everywhere.

### Step 4.4: Viewing Traces

1. **Trigger a Flow**: Select `enrichTransactionFlow` and click **Run**
2. **Navigate to Traces**: Click the clock icon in the left sidebar
3. **Inspect the Waterfall**: Click a Trace ID to see:
   - Input/Output: Raw JSON sent and received
   - Latency: Time for each reasoning step
   - Tool Calls: External API interactions

### Step 4.5: Autonomous Browser Verification (Optional)

Run the browser subagent against the live app to verify it end to end:

**Prompt:**

```text
As a quality engineer, navigate to http://localhost:3000. Verify that the
transaction list correctly renders mock data. Categorize the first five
transactions. Confirm that the Genkit enrichment (category and recurring
status) appears for each. Finally, generate a Screenshot Artifact and a Test
Report Artifact.
```

---

## Lab Completion Checklist

- [ ] Workspace rules in `.agents/rules/` and context files in `.context/`
- [ ] `prompts/classify.prompt` loads without a Picoschema error and returns a sensible category
- [ ] Exactly one Genkit instance, and `enrichTransactionFlow` appears in the Developer UI
- [ ] `/money-audit` defined at `.agents/skills/money-audit/SKILL.md` and run once in an `agy` session
- [ ] Mock backend answering at `/api/transactions`
- [ ] `TransactionList` rendering transactions with their enrichment
- [ ] A trace waterfall inspected in the Developer UI, latency read off it
- [ ] `npm test` passing

## Chapter Challenge

Add these features to MoneyMind:

### 1. Google Cloud Deployment

**Hint:** ask Antigravity:

```text
Create a deployment stack for MoneyMind to deploy to GCP.
```

> **Cost and teardown.** This challenge creates real, billable GCP resources (typically Cloud Run, Artifact Registry, and Cloud Build).
>
> 1. Use a dedicated GCP project, so cleanup stays simple.
> 2. Set a budget alert before you start.
> 3. Review the agent's plan artifact before you approve anything that provisions infrastructure.
> 4. When you are done, tear down. Delete the project (`gcloud projects delete <project-id>`), or remove the individual services and container images.
>
> An idle Cloud Run service costs little. Forgotten images and load balancers still cost money.

### 2. Real Plaid Integration

**Hint:** Create a free Plaid Dev account. Then use this prompt:

```text
Update the PlaidProvider to accept a real PLAID_CLIENT_ID and SECRET
from the secrets manager, moving away from sandbox credentials.
```

> In the reference project, the real-API path is the stub in `src/app/api/transactions/route.ts` that returns 501. There is no Plaid client module yet, so expect the agent to create one. Before you approve, check where its plan gets the credentials from.

### 3. Voice Interaction (bonus)

**Hint:** Use the Antigravity CLI:
```bash
agy -i "Scaffold a web-speech API wrapper that lets me say,
'Hey MoneyMind, how much did I spend on Uber?'"
```

---

## Troubleshooting

### The Developer UI shows no flows

There are two causes. Check them in this order.

1. You ran a bare `npx genkit start`, which has no entry point to import your flows. Use `npm run genkit`, or pass one explicitly:

```bash
npx genkit start -- npx tsx --env-file=.env genkit-server.ts
```

2. Something called `genkit({...})` twice. Each call gets its own registry, so flows defined on one are invisible to the other. Keep the instance in `src/lib/ai.ts` and import it everywhere.

### "Cannot find module '@genkit-ai/core'" or `ai` is undefined

`@genkit-ai/core` does not export a configured `ai` object. Import your own instance instead:

```typescript
import { ai } from './ai';   // or '@/lib/ai' from elsewhere in src/
```

### "Picoschema: unsupported scalar type"

A `.prompt` file uses JSON Schema syntax where Picoschema expects a parenthetical type on the key. Use `category(enum, description): [A, B]` and `items(array): {...}`. Do not use nested `enum:` or `type: array` blocks.

### API key errors

Confirm `GEMINI_API_KEY` is set in `.env`. Confirm you started the server through `npm run genkit` (which passes `--env-file=.env`). Start from the template to avoid typos:

```bash
cp .env.example .env
```

On Windows, use `copy .env.example .env` (CMD) or `Copy-Item .env.example .env` (PowerShell).

- `node: .env: not found` means there is no `.env` file yet. Create it from the template as above.
- `ERROR: GEMINI_API_KEY is not set` from `genkit-server.ts` means the file exists but still holds the template's placeholder.

### "Model not available"

The pinned model name does not exist for your account.

- For prompts, edit the `model:` line in the `.prompt` file.
- For the IDE, pick from its model selector.
- For the CLI, run `agy models`.

### Extension not found in Antigravity

Antigravity's extension source is the Open VSX Registry. If what you need is not published there, download the `.vsix` and use the Extensions view "..." menu > **Install from VSIX**.

### agy misbehaves in a script

A bare `agy` expects an interactive TTY. A script does not have one.

- In scripts and CI, use print mode: `agy -p "..."`. Add `--dangerously-skip-permissions --sandbox` when the job needs tool access. Exercise 2, Part 4 shows the full pattern.
- Headless tool calls that fail approval are soft-denied. The run still exits 0. Check stderr for skipped work.
- For CI auth, set `GEMINI_API_KEY`. Write `"modelProvider": "gemini"` into `~/.gemini/antigravity-cli/settings.json`. The key does nothing without the setting.

---

## Next Steps

1. Work the three exercises in `exercises/`
2. Read the patterns in `../code-examples/`
3. Continue to Chapter 7, which covers Cursor and GitHub Copilot
