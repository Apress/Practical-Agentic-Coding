# Exercise 2: Antigravity CLI Mastery

Maps to Chapter 6, Section 6.4.

## Objective

Use the **Antigravity CLI (`agy`)** in the terminal for these tasks:

- Scaffolding from a prompt
- Error diagnosis
- Skills
- CI integration

## Duration

35-45 minutes

## Prerequisites

- Antigravity CLI installed (`curl -fsSL https://antigravity.google/cli/install.sh | bash`, then `agy install`. On Windows, see the [CLI guide](../../tutorials/antigravity-cli-guide.md#installation).)
- Authenticated (`agy` triggers keyring or Google Sign-In on first launch)
- Terminal/shell access
- Basic familiarity with the command line

agy has no subcommands. There is no `agy fix`, `agy review`, or `agy scaffold`.

1. Launch the terminal agent with `agy`.
2. Ask for what you want.
3. Control the session with slash commands.

For scripts, `agy -p "..."` runs a single prompt non-interactively.

---

## Part 1: Driving the Terminal Agent (10 minutes)

### Exercise 2.1: First Session and Trust Prompt

```bash
# Navigate to your MoneyMind project
cd chapter-06/hands-on-lab/moneymind

# Launch the interactive terminal agent
agy
```

On first launch in a new folder, agy shows a trust prompt for the directory. Accepting grants it read, edit, and execute access. Accept it for this lab folder.

Then ask a codebase question:

```text
> Where is the API key configuration stored in this project?
```

**Expected Output**: The agent identifies `.env.example` and describes how the project uses environment variables.

### Exercise 2.2: Slash Commands and Shell Mode

Inside the session, try the session-control commands:

```text
/plan          # enable plan mode
/diff          # unified diffs of modified files
/skills        # browse loaded Agent Skills
/mcp           # manage MCP servers
/permissions   # switch the permission preset
/settings      # interactive settings editor
```

Then try shell mode. A leading `!` runs the rest of the line as a shell command. You stay in the session.

```text
> !npm test
> !git status
```

Write down what each command shows about your session. Then try these keys:

- **Shift+Tab** cycles the execution mode: the default mode, accept-edits, auto, and plan. `auto` appears only where the terminal sandbox runs. In agy 1.4.4 and later, that includes Windows 11 24H2 or later. It does not appear for business or enterprise accounts.
- **Ctrl+R** opens the Artifact Review panel.

### Exercise 2.3: Model Selection and One-Shot Mode

```bash
# List available models
agy models

# Quick question, one-shot print mode (great for scripts)
agy -p "What testing framework does this project use?"

# Deep analysis with a specific model
agy --model <pro-class-model> -p "Analyze the security posture of this codebase and identify potential vulnerabilities"
```

**Compare**: Note the difference in response time and depth. Mid-session, `/model` switches models without a restart.

---

## Part 2: Diagnosis and Review Prompts (15 minutes)

### Exercise 2.4: The Smart Fix Loop

Add a deliberate error. Put this line near the top of `src/lib/genkit.ts`, below the imports:

```typescript
// Temporary: a type error the build will reject.
const broken: number = 'not a number';
```

Confirm the build fails before you ask the agent about it:

```bash
npm run build
```

Then launch agy and ask it to diagnose:

```text
> The npm build is failing. Read the error output, find the root cause,
> and propose a fix.
```

The agent runs the build itself and reads the output. You do not need to pipe anything. The default `request-review` preset shows you a line-level diff before each write. Press `f` to keep or drop each change.

For the non-interactive equivalent:

```bash
agy -p "Diagnose why npm run build fails and propose a fix"
```

In print mode, nobody is there to approve the build command. agy soft-denies it, and the agent works from the source alone. To let it run the build, first add a rule to `~/.gemini/antigravity-cli/settings.json`:

```json
{
  "permissions": {
    "allow": ["command(regex:npm run (build|lint|test))"]
  }
}
```

**Observe**: How does the agent find the error? Note that it runs the build itself and does not ask you for the log.

Before you continue, remove the broken line (or let the agent do it). Then re-run `npm run build`.

### Exercise 2.5: The Auto-Review Loop

Review your recent changes before committing:

```text
> Review the diff of my most recent commit. Be strict: flag style
> violations, missing error handling, and anything that breaks our
> project rules.
```

Try a focused variant:

```text
> Review my staged changes for security only: hardcoded secrets, missing
> input validation, and error handling that leaks internals.
```

### Exercise 2.6: Documentation Prompts

The agent reads your workspace. Name the files in the prompt. Do not pipe them.

```bash
agy -p "Read src/components/WasteCard.tsx and generate JSDoc documentation for it, including the props interface and usage examples"

agy -p "Read src/app/api/transactions/route.ts and generate OpenAPI-style documentation for this endpoint"
```

### Exercise 2.7: Analysis Prompts

```bash
agy -p "Scan the src directory and identify any exported functions or components that appear unused"

agy -p "Read package.json and identify dependencies that may be outdated or have security concerns"
```

---

## Part 3: Scaffolding and Skills (10 minutes)

### Exercise 2.8: Intent-Based Scaffolding

To scaffold, write a prompt. The agent generates the structure. It does not copy a template.

```text
> Scaffold a budget management module under src/features/budget with:
> a budget schema with category limits, a Genkit flow for budget
> analysis, and a React hook for budget state management.
```

For larger scaffolds, plan first. `agy --mode plan -i "..."` shows the file list before anything is written.

### Exercise 2.9: Create a Skill

A skill is a markdown file at `.agents/skills/<name>/SKILL.md`. You run it as a plain slash command named after its folder. Create a performance-analysis skill:

```bash
mkdir -p .agents/skills/perf-check
```

Then, inside agy:

```text
> Create a skill file at '.agents/skills/perf-check/SKILL.md'. Use YAML
> frontmatter with the description: 'Analyzes MoneyMind for performance
> issues.' In the markdown body, instruct the agent to check the files
> the user names for unnecessary re-renders, missing memoization, N+1
> query patterns, large bundle contributors, and unoptimized loops, and
> to provide specific recommendations with code examples.
> Output ONLY the SKILL.md content.
```

**Usage**:

```text
/perf-check src/components/TransactionList.tsx
```

The command is `/perf-check`, a plain slash command. There is no namespace or colon syntax.

1. Run `/skills reload`. A skill added while agy is running is not a slash command until you reload or start a new conversation.
2. Run `/skills` to confirm the skill loaded.

---

## Part 4: CI/CD Integration (10 minutes)

### Exercise 2.10: GitHub Actions Workflow

CI has no human at the keyboard. Use print mode plus explicit flags: `agy -p "..." --dangerously-skip-permissions --sandbox`.

- `-p` makes the run headless.
- The skip flag auto-approves tool requests.
- The sandbox limits where those auto-approved actions can reach.

> **As of November 7, 2026**
>
> - (agy 1.5.2 and later) The skip flag blocks commands on agy's system command denylist instead of approving them. In `-p` runs on a Gemini Enterprise account, it also denies terminal commands or file access outside the workspace that your administrator requires to be reviewed.
> - (agy 1.5.0 and later) `-p` waits for background tasks with no time limit. So the workflow below adds `--print-timeout 10m`. A run the timeout cuts short prints an `AGY_ERROR` line and exits with code 3, which fails the step.
> - (agy 1.4.4 and later) `--sandbox` does nothing where the terminal sandbox is unavailable, such as Linux hosts that block unprivileged user namespaces. Ubuntu 24.04, which `ubuntu-latest` runs, restricts them by default. On that runner, use `"permissions": {"allow": ["command(git)"]}` in the settings file in place of `--dangerously-skip-permissions`.

Watch for one headless quirk. When a tool call needs an approval it cannot get, agy soft-denies it, prints a notice to stderr, and returns exit code 0 anyway. A review that skipped its own checks still looks green.

For auth, pair a `GEMINI_API_KEY` secret with `"modelProvider": "gemini"` in `~/.gemini/antigravity-cli/settings.json`. Setting only the key does nothing. With neither piece in place, the run errors out.

Create `.github/workflows/ai-review.yml`:

```yaml
# .github/workflows/ai-review.yml
name: AI Code Review

on:
  pull_request:
    branches: [main]

jobs:
  ai-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
        with:
          fetch-depth: 0

      - name: Install Antigravity CLI
        run: |
          curl -fsSL https://antigravity.google/cli/install.sh | bash
          # The installer prints where it put the binary. Add that directory to
          # PATH for later steps; confirm the location against the installer
          # output for your version rather than assuming this one.
          echo "$HOME/.local/bin" >> $GITHUB_PATH
          # Headless auth: GEMINI_API_KEY only takes effect with this setting.
          mkdir -p ~/.gemini/antigravity-cli
          echo '{"modelProvider": "gemini"}' > ~/.gemini/antigravity-cli/settings.json

      - name: AI Code Review
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          agy -p "Review the diff between this branch and main. Flag \
          security issues, missing error handling, and style violations. \
          Output the findings as markdown." \
          --dangerously-skip-permissions --sandbox --print-timeout 10m > review.md

      - name: Post Review Summary
        run: |
          echo "## AI Review Summary" >> $GITHUB_STEP_SUMMARY
          cat review.md >> $GITHUB_STEP_SUMMARY
```

See the full workflow with critical-issue gating in [ci-cd-integration.yml](../../code-examples/antigravity-cli/ci-cd-integration.yml).

### Exercise 2.11: Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# AI-powered pre-commit hook

echo "Running AI code review..."

if [ -z "$(git diff --cached)" ]; then
    exit 0
fi

REVIEW=$(agy -p "Review my staged changes. If you find critical or
security issues, start your reply with the word CRITICAL. Otherwise give
a brief summary.")

if echo "$REVIEW" | grep -qi "^CRITICAL"; then
    echo "AI Review found critical issues:"
    echo "$REVIEW"
    echo ""
    echo "Commit blocked. Fix issues or use --no-verify to bypass."
    exit 1
fi

echo "AI Review passed!"
exit 0
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

The review runs `git diff --cached`, a shell command. Allow git in print mode before you rely on the hook. Add `"command(git)"` to `permissions.allow` in `~/.gemini/antigravity-cli/settings.json`. Without that rule, the command is soft-denied. The agent sees no diff, and every commit passes.

---

## Part 5: Challenge Tasks

### Challenge 2.1: Create a Test Generator Skill

Create `.agents/skills/test-gen/SKILL.md` that:
- Takes a TypeScript file as input
- Generates Jest tests with good coverage
- Includes edge cases and error scenarios

Invoke it as `/test-gen src/lib/genkit.ts`.

### Challenge 2.2: Build a Migration Assistant

Ask the agent to combine shell output with analysis in one prompt:

```bash
agy -p "Run 'npm outdated --json', analyze the outdated packages, and create a migration plan noting any breaking changes"
```

This prompt also needs a `permissions.allow` rule for the `npm outdated` command (for example `"command(regex:npm outdated.*)"`). Or run it in an interactive session where you approve it.

---

## Key Takeaways

- The Antigravity CLI takes prompts. It has no subcommands.
- `agy -p "..."` is the scriptable one-shot form.
- For CI, add `--dangerously-skip-permissions --sandbox`. Headless runs soft-deny unapproved tool calls and still exit zero.
- Skills (`.agents/skills/<name>/SKILL.md`) add plain slash commands to the agent.
- The permission presets and the trust prompt control what the agent may do. Keep them on.

## Quick Reference

| Invocation | Purpose |
|------------|---------|
| `agy` | Interactive terminal agent |
| `agy -i "prompt"` | Interactive with an initial prompt |
| `agy -p "prompt"` | One-shot print mode |
| `agy -c` | Resume the last conversation |
| `agy --mode plan` | Plan without editing |
| `/skills` | Browse loaded Agent Skills |
| `/diff` | Show unified diffs of modified files |
| `/permissions` | Switch the permission preset |
| `/rewind` | Roll the conversation back |
| `!<command>` | Run a shell command in-session |

---

## Next Exercise

Continue to [Exercise 3: Artifacts and Knowledge Items](./exercise-3-artifacts.md).
