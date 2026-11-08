# Intent-first workflow: quick reference

This page is a keyboard reference for working intent-first in Antigravity. It covers the steps, the files, and the prompt format.

Why intent-first works, and how the Perceive, Plan, Act, Verify loop runs: Chapter 6, Section 6.1.

---

## The Intent Loop

The agent works in four stages. This table shows what you do at each one.

| Stage | What you see | What you do |
|-------|--------------|-------------|
| Perceive | The agent reading files, the AST, and Git history | Make sure the context it needs exists (`.context/` files, rules) |
| Plan | An Implementation Plan artifact (in Plan mode) | Review it and comment before approving |
| Act | File edits, terminal commands, browser actions | Approve the actions it asks permission for |
| Verify | Test results and a Walkthrough artifact | Check the results against what you asked for |

---

## Practical Workflow

1. **State your intent.** Say what you want, for example "Add user authentication with Google OAuth".
2. **Pick a mode.** Use Fast mode for small, local tasks such as renaming a variable or running a command. Use Plan mode for new features, refactors, and multi-file changes.
3. **Review the Implementation Plan.** Check the files it changes, the dependencies it adds, and the rules it must follow.
4. **Comment on the plan.** Leave Google Docs-style comments on the artifact. For example:

   ```text
   Comment: "Consider using the existing UserRepository instead
   of creating a new data access layer"
   ```

5. **Approve, then verify.** Run the tests. Check the Genkit traces for AI flows. Use the browser subagent to check the UI. Read the Walkthrough.

When to use each mode and why: Chapter 6, Section 6.3.

---

## The Constraint Sandwich Technique

A Constraint Sandwich prompt has three parts, in this order:

1. Top bun: the persona and standards.
2. Meat: the functional requirements.
3. Bottom bun: the negative constraints ("DO NOT ...").

Example:

```text
Act as a senior fintech UI/UX architect.

Create a SpendingChart component that:
- Displays spending by category as a bar chart
- Shows percentage of total for each category
- Supports dark and light themes
- Is responsive for mobile and desktop
- Includes loading and error states

DO NOT use external charting libraries.
DO NOT use raw CSS; use ONLY Tailwind utilities.
DO NOT include any hardcoded data.
Output an Implementation Plan Artifact before coding.
```

How the sandwich prompt is used in the MoneyMind build: Chapter 6, Section 6.6.

---

## Context Management

The agent already reads your workspace. Add the domain knowledge it cannot infer as files in `.context/`:

```text
.context/
├── api_reference.md    # External API documentation
├── design_tokens.md    # UI/UX guidelines
├── architecture.md     # System design decisions
└── business_rules.md   # Domain-specific logic
```

Reference a file in a prompt with `@`:

```text
Reference the @.context/plaid_reference.md when implementing
the transaction processing logic.
```

How native context differs from MCP context: Chapter 6, Section 6.2.

---

## Governance and Rules

### Workspace Rules

Put a rules file inside `.agents/rules/`. The `trigger: always_on` frontmatter applies it to every task.

```markdown
---
trigger: always_on
---
# Project Rules

## Always
- Use TypeScript with strict mode
- Write tests for new functionality
- Document public APIs

## Never
- Commit secrets to the repository
- Use deprecated fields (see .context/deprecated.md)
- Bypass the review process

## Preferences
- Prefer composition over inheritance
- Use functional components in React
- Keep functions under 50 lines
```

### Knowledge Items

To record a rule as a Knowledge Item, ask the agent in this form:

```text
Create a Knowledge Item:

Title: Error Handling Standards
Content:
- All errors must be logged with context
- User-facing errors should be sanitized
- Network errors should include retry guidance
- Validation errors should list all issues
```

What Knowledge Items are and how the agent uses them: Chapter 6, Section 6.3.

---

## Troubleshooting

| Problem | What to try |
|---------|-------------|
| The output is not what you asked for | Refine the intent statement. Add more context. Use the Constraint Sandwich. |
| A multi-file change goes wrong | Run it again in Plan mode and review the plan before you approve |

---

## Next Steps

- Complete [Exercise 1: Intent-First](../hands-on-lab/exercises/exercise-1-intent-first.md)
- Learn the [Antigravity CLI](./antigravity-cli-guide.md)
- Set up [Firebase Genkit](./genkit-setup.md) for observability
- Start the [MoneyMind lab](../hands-on-lab/README.md)
