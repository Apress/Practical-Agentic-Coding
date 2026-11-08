# Exercise 1: Intent-First Development

Maps to Chapter 6, Section 6.1.

## Objective

Add a new MoneyMind feature by driving the Perceive-Plan-Act-Verify loop.

## Duration

30-45 minutes

## Prerequisites

- Phase 1 of the MoneyMind lab complete, or the finished `moneymind/` project installed (`npm install`, `.env` with your `GEMINI_API_KEY`)
- Google Antigravity IDE installed and signed in
- Working knowledge of TypeScript and React

---

## Part 1: Understanding the Intent Loop (10 minutes)

### The Four Stages

Read Chapter 6, Section 6.1 for how the four stages work. In this exercise, you see each one:

1. **Perceive**: The agent scans your codebase.
2. **Plan**: The agent produces a plan, usually as a reviewable artifact.
3. **Act**: The agent edits files, runs terminal commands, or drives the browser.
4. **Verify**: Tests and previews check the result. The Agent Inbox collects it for your approval.

### Exercise 1.1: Analyze Your Codebase

Open Antigravity. Enter this prompt in the chat:

```text
Analyze the MoneyMind codebase and provide a summary of:
1. The main components and their responsibilities
2. How data flows from the API to the UI
3. Which Genkit flows are defined and what they do
```

**Expected Output**: The agent describes the TransactionList and WasteCard components, the API routes, and the Genkit flows (enrichTransactionFlow, batchEnrichFlow, detectWasteFlow).

---

## Part 2: Adding a New Feature with Intent (20 minutes)

### The Feature: Spending Summary Card

You will add a "Spending Summary" card that shows total spending by category.

### Exercise 1.2: Write the Intent Prompt

State your **intent**. Leave out implementation details.

**Prompt (Fast Mode):**
```text
I want to add a spending summary feature to MoneyMind that shows users
how much they've spent in each category this month. Display it as a
card with a bar chart or visual representation.
```

The prompt does not specify:
- File names
- Component structure
- Styling details
- Data fetching approach

**Observe**: Watch how Antigravity reads your intent and generates a plan.

### Exercise 1.3: Switch to Plan Mode

Now try the same feature in **Plan Mode**:

**Prompt (Plan Mode):**
```text
As a senior fintech UI/UX architect, design and implement a Spending Summary
feature for MoneyMind.

The feature should:
- Aggregate transaction amounts by category
- Display a visual summary (chart or progress bars)
- Show percentage of total spending per category
- Follow the Glassmorphism design from .context/design_tokens.md

Generate an Implementation Plan Artifact for review before coding.
```

### Exercise 1.4: Review the Artifact

When the agent produces an Implementation Plan:

1. **Check the files it plans to create/modify**
2. **Review the component structure**
3. **Verify it follows your governance rules** (.agents/rules/)
4. **Provide feedback** using Google Docs-style comments

**Feedback Example:**
```text
Add feedback: "Use Tailwind's w-full and bg-gradient-to-r for the progress bars
instead of custom SVG charts for simplicity."
```

---

## Part 3: The Verify Stage (10 minutes)

### Exercise 1.5: Verify the Implementation

After the agent implements the feature:

1. **Run the application**:
   ```bash
   npm run dev
   ```

2. **Check the Genkit traces** (if the feature uses AI):
   ```bash
   npm run genkit
   ```
   Open http://localhost:4000 and confirm any new flows appear. An empty flow list means there is a second `genkit()` call. There should be exactly one instance, in `src/lib/ai.ts`.

3. **Run tests**:
   ```bash
   npm test
   ```

4. **Use the browser subagent** for visual verification:
   ```text
   Navigate to localhost:3000 and verify that the Spending Summary card
   renders correctly. Check that:
   - Categories are displayed with correct colors
   - Amounts are formatted as currency
   - The design matches our Glassmorphism theme
   Generate a Screenshot Artifact for documentation.
   ```

---

## Part 4: Reflection Questions

Answer these questions in a markdown file or your notes:

1. **How did the agent's interpretation differ between Fast Mode and Plan Mode?**

2. **What information did you have to provide versus what the agent inferred?**

3. **What did the artifact let you check before the code was written?**

4. **What would you do differently next time to get better results?**

---

## Bonus Challenge

Use the Intent-First approach to add a **Monthly Budget** feature:

**Intent Prompt:**
```text
Add a budget tracking feature that lets users set monthly spending limits
per category and shows progress toward those limits with visual alerts
when approaching the limit.
```

Document:
- The artifacts generated
- Feedback you provided
- Final implementation quality

---

## Key Takeaways

- State **what** you want. Let the agent decide **how** to code it.
- The agent uses context (rules, reference files) to make its decisions.
- Artifacts show you the plan, so you can review it.
- In the Verify stage, check that the implementation matches your intent.

---

## Next Exercise

Continue to [Exercise 2: Antigravity CLI](./exercise-2-antigravity-cli.md).
