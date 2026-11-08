# Antigravity setup: quick reference

This guide installs and configures the Antigravity IDE for the MoneyMind lab. It matches Phase 1 of the lab.

What the Antigravity features are and when to use them: Chapter 6, Section 6.3.

For the latest install steps, see Google's own guide at [antigravity.google/docs](https://antigravity.google/docs).

> **Updates to the book (as of November 7, 2026)**
>
> - The IDE calls the book's Secure Mode **Strict mode**.
> - On 2.0 builds, the Agent Manager is a standalone app and is the primary entry point. Your build may still show an in-IDE Agent Manager view. Every manager step in the lab works the same in the standalone app.
> - The only Gemini model on Antigravity's Free and Google AI Plus plans is a Flash-class one. On those plans, use it with the High thinking level where the model table below says Pro-class. [antigravity.google/docs/models](https://antigravity.google/docs/models) lists the models each plan includes.

## Before You Start

- A supported desktop OS (Windows, macOS, or Linux)
- Node.js 22 or newer (24 LTS recommended), and Git, for the MoneyMind project
- A Google account for sign-in
- A stable internet connection. Reasoning happens in Google's cloud, not locally.

An SSD makes the first indexing of a large repository faster, because indexing is disk-bound.

---

## Installation

### Step 1: Download and install

1. Download the installer for your platform from [antigravity.google/download](https://antigravity.google/download).
2. Run it.
3. Follow any platform-specific steps on the download page. Do not use a package-manager recipe copied from elsewhere. The distribution channels have changed more than once.

### Step 2: Launch and authenticate

1. Launch Antigravity.
2. Sign in with your Google account. You do not paste an API key here. You need a Gemini API key later, for the Genkit layer only.
3. Approve the model-access permissions it asks for.
4. Open any folder and ask the chat panel "Summarize this project." A useful answer means indexing and model access both work.

---

## Initial Configuration

### Extension Source: Open VSX Registry

Antigravity is a VS Code fork. Its default extension source is the **Open VSX Registry**, not Microsoft's marketplace.

- Install extensions from the Extensions view as usual. Most common ones are available.
- Change the source in Antigravity IDE settings if you need to.
- If the registry lacks an extension, download the `.vsix`. Then use the Extensions view "..." menu > **Install from VSIX**.

### Configure Model Selection

Open the model selector in the chat panel (or Antigravity Settings, depending on your build). Pick a tier per task:

| Task | Tier to pick |
|------|--------------|
| Renaming, small edits, running commands | A Flash-class model |
| Planning, multi-file refactors, architecture | A Pro-class model |
| Code generation inside an approved plan | A Pro-class model |

- Pick the exact model names from the list your account shows. Do not copy them from a doc. They change between releases, and a stale pin either fails or silently downgrades you.
- Genkit prompt files pin their own models separately, in `prompts/*.prompt`.
- On the Free and Google AI Plus plans, see the update note at the top of this page.

### Enable Secure Mode (Optional)

1. Open Antigravity Settings and find the security section.
2. Enable **Strict mode** (the IDE's name for the book's Secure Mode).
3. Set the URL allowlist and denylist for the browser subagent.
4. Set the forced-review policies for terminal commands and browser JavaScript.
5. Set workspace isolation.

`code-examples/antigravity-config/secure-mode.json` in this chapter records those choices. Read it alongside the UI.

---

## Workspace Setup

### Create Your First Workspace

1. **File** > **Open Folder** > Select your project
2. Wait for Antigravity to index your codebase
3. Check the status bar for indexing progress

### Configure Workspace Rules

Add a rules file under `.agents/rules/` in your project root (for example `.agents/rules/project-rules.md`):

```markdown
---
trigger: always_on
---
# Project Rules

## Language Requirements
- ALL code MUST be written in TypeScript
- Use strict mode enabled

## Styling
- Use Tailwind CSS for all styling
- Follow design tokens in .context/

## Testing
- Jest for all tests
- Minimum 80% coverage

## Security
- NEVER hardcode secrets
- Use environment variables
```

### Set Up Context Files

Create a `.context/` directory for domain-specific knowledge:

```text
.context/
├── api_reference.md    # External API documentation
├── design_tokens.md    # UI and UX guidelines
├── architecture.md     # System design decisions
└── glossary.md         # Domain terminology
```

The MoneyMind lab uses two of these files:

- `.context/plaid_reference.md` tells the agent which Plaid fields to trust.
- `.context/design_tokens.md` defines the Glassmorphism theme.

---

## The Surfaces: Agent Manager, Editor, and Extensions

The lab uses two of these surfaces:

1. **Agent Manager (standalone app)**: Dispatch and monitor multiple agents here. Jump to the Editor when a result needs hand-editing. It also hosts task queues, scheduled background jobs, and subagents that parallelize a single task.
2. **Editor**: The VS Code-style IDE for hands-on work.
3. **Editor extensions**: The same agents inside VS Code or JetBrains, if you keep your current editor.

Pending approvals and finished results collect in the **Agent Inbox** inside the Agent Manager. Set your approval behavior there. A background agent needs you only when it asks for permission or finishes.

For the current list of surfaces, see [antigravity.google/docs](https://antigravity.google/docs).

---

## Environment Variables

The Antigravity IDE and CLI authenticate through Google Sign-In. They need no API key. You need a Gemini API key only for the Genkit intelligence layer (Phase 2 of the lab):

```bash
# Gemini API key (required for Genkit)
GEMINI_API_KEY=your_api_key_here
```

### Getting Your API Key

1. Visit [aistudio.google.com/apikey](https://aistudio.google.com/apikey).
2. Create a new API key.
3. Put it in your environment.

For the MoneyMind lab, the `.env` file is enough. `npm run genkit` passes `--env-file=.env`.

```bash
cp .env.example .env
# then edit .env and set GEMINI_API_KEY
```

On Windows, use `copy .env.example .env` (CMD) or `Copy-Item .env.example .env` (PowerShell).

To set the key for a whole shell session instead:

**macOS and Linux:**
```bash
export GEMINI_API_KEY="your_key"
# add the same line to ~/.bashrc or ~/.zshrc to make it persist
```

**Windows (PowerShell):**
```powershell
Set-Item -Path Env:GEMINI_API_KEY -Value "your_key"
# or set it permanently through System environment variables
```

Never commit the key. `.env` is already in this project's `.gitignore`. That also keeps it out of the agent's context.

---

## Verifying Installation

### Test Basic Functionality

1. Open a project in Antigravity
2. Open the chat panel (the chat icon in the activity bar, or the command palette)
3. Type: "Summarize this project"
4. Verify the agent responds with project analysis

### Test Agent Manager

1. Open the Agent Manager (the standalone Antigravity app on 2.0 builds; older builds also have an in-IDE view)
2. Create a new task: "Create a simple TypeScript utility function"
3. Verify the agent creates a plan artifact
4. Approve and watch execution

### Test CLI Integration

1. Open the integrated terminal in Antigravity.
2. Launch `agy` once, interactively. Sign in and accept the trust prompt for the folder. Print mode reuses those cached credentials.
3. Run:

```bash
agy -p "What files are in this project?"
```

---

## Troubleshooting

**"Model not available"**
The model name you pinned no longer exists, or your account does not have it. Reopen the model selector and pick from the list it shows. For the CLI, run `agy models` to list what your account can use.

**Slow first open on a large repo**
Indexing is disk-bound. Exclude the heavy directories (`node_modules`, build output) from indexing in settings. Let it finish one pass. Later opens reuse the index.

**Extensions not loading**
Antigravity's default extension source is the Open VSX Registry. If the extension is not published there, download the `.vsix` and use the Extensions view "..." menu > **Install from VSIX**. A reload also helps: Ctrl/Cmd + Shift + P, then "Developer: Reload Window".

**Agent not responding**
Check these in order:

1. Your internet connection (reasoning runs in Google's cloud).
2. Whether your sign-in is still valid.
3. A different model.

**Genkit errors mentioning the API key**
This error comes from the Genkit layer, not the IDE. Confirm `GEMINI_API_KEY` is set in `.env`. Confirm you started the server with `npm run genkit` (which passes `--env-file=.env`).

### Getting Help

Start at [antigravity.google/docs](https://antigravity.google/docs). It stays current with the release you are running. The surfaces and setting names in this chapter have already changed once.

---

## Next Steps

1. Read the [intent-first workflow guide](./intent-first-workflow.md)
2. Learn the [Antigravity CLI](./antigravity-cli-guide.md)
3. Set up [Firebase Genkit](./genkit-setup.md) for observability
4. Start the [MoneyMind hands-on lab](../hands-on-lab/README.md)

---

## Quick Reference

Antigravity uses VS Code's keybinding system. Use the command palette (Ctrl/Cmd + Shift + P) to find an action. The Keyboard Shortcuts editor shows the binding for each action in your build.

| Action | How to get there |
|--------|------------------|
| Open the chat panel | Command palette, or the chat icon in the activity bar |
| Open the Agent Manager | The standalone Antigravity app; on older builds, also via the command palette or its icon in the IDE activity bar |
| Switch between Fast and Plan mode | Mode selector in the chat panel |
| Review artifacts | Artifact panel in the Agent Manager, or Ctrl+R in an `agy` session |
