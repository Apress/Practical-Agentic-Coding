# Exercise 3: Artifacts and Knowledge Items

Maps to Chapter 6, Section 6.3.

## Objective

Use Antigravity's **Artifacts** and **Knowledge Items**. Artifacts let you review the agent's work. Knowledge Items carry context between sessions.

## Duration

30-40 minutes

## Prerequisites

- Exercises 1 and 2 complete
- Google Antigravity IDE with an active workspace
- Familiarity with the Intent Loop

---

## Part 1: Understanding Artifacts (10 minutes)

### What Are Artifacts?

An artifact is the agent's reasoning and proof of work, written down. You read it and comment on it before the agent acts. What artifacts are for: Chapter 6, Section 6.3.

### Artifact Types

| Type | Purpose | When created |
|------|---------|--------------|
| **Implementation Plan** | Technical roadmap, written before any code | Plan mode, on anything non-trivial |
| **Walkthrough** | Summary of what changed and why | After a multi-file change |
| **Screenshot** | Visual capture of UI state | Browser subagent verification |
| **Recording** | Looping video of the agent's browser actions | End-to-end flows |
| **Test Report** | Verification results | After running tests |

Examples of the first two are markdown files in `../../code-examples/artifacts/`. The others exist only inside a session.

### Exercise 3.1: Generate an Implementation Plan

Switch to **Plan Mode** in Antigravity. Request a feature with several parts:

**Prompt:**
```text
Design a notifications system for MoneyMind that:
1. Alerts users when spending exceeds budget in a category
2. Notifies about detected waste (unused subscriptions)
3. Sends weekly spending summaries
4. Supports both in-app and optional email notifications

Generate a detailed Implementation Plan Artifact before any coding.
```

**Review the Artifact:**
- Does it split the task into logical phases?
- Are file changes clearly listed?
- Are dependencies identified?
- Does it follow governance rules?

### Exercise 3.2: Provide Feedback on Artifacts

Give feedback on the plan:

1. Click on any section of the Implementation Plan
2. Add a comment like:
   ```text
   Consider using a notification queue pattern instead of synchronous
   delivery to improve performance and reliability.
   ```
3. Observe how the agent uses your feedback

### Exercise 3.3: Request a Walkthrough

After the agent implements a feature, request documentation:

**Prompt:**
```text
Generate a Walkthrough Artifact summarizing all changes made for the
notification system. Include:
- Files created or modified
- Key design decisions
- How to test each component
- Any known limitations
```

---

## Part 2: Knowledge Items (15 minutes)

### What Are Knowledge Items?

Knowledge Items (KIs) are **persistent memory** that carries across sessions. Antigravity extracts and stores them from your conversations. How KIs work: Chapter 6, Section 6.3.

### Exercise 3.4: View Existing Knowledge Items

Check what Antigravity has learned about your project:

**Prompt:**
```text
Show me all Knowledge Items that have been extracted from our
conversations about MoneyMind.
```

Or navigate to the Knowledge Items panel in the Agent Manager.

### Exercise 3.5: Create Explicit Knowledge Items

Create a KI by hand:

**Prompt:**
```text
Create a Knowledge Item with the following information:

Title: MoneyMind Code Review Standards
Content:
- All PRs must have 80%+ test coverage
- Security-sensitive code requires two reviewers
- API changes must update the OpenAPI spec
- Performance-critical code needs benchmarks
- No TODO comments in production code

This should be referenced in all future code review tasks.
```

### Exercise 3.6: Test Knowledge Persistence

Close your current chat session. Start a new one:

**New Session Prompt:**
```text
Review this code for MoneyMind: [paste some code]
Apply all relevant coding standards from our knowledge base.
```

**Verify**: Does the agent reference your Code Review Standards KI?

### Exercise 3.7: Knowledge Item Categories

Create Knowledge Items for different areas:

**Architecture KI:**
```text
Create a Knowledge Item about MoneyMind's architecture:

Title: MoneyMind Architecture Decisions
Content:
- We use Next.js App Router (NOT pages directory)
- State is managed with React hooks, not Redux
- API routes use Zod for validation
- Genkit flows handle all AI logic
- Mock data can be toggled via USE_MOCK_DATA env var
```

**Testing KI:**
```text
Create a Knowledge Item about testing preferences:

Title: MoneyMind Testing Conventions
Content:
- Use Jest with ts-jest for TypeScript
- Mock external APIs in unit tests
- Use React Testing Library for components
- Name test files as [component].test.tsx
- Group tests by feature in describe blocks
```

---

## Part 3: Practical Applications (10 minutes)

### Exercise 3.8: Onboarding a New Team Member

Use artifacts to create onboarding documentation:

**Prompt (Plan Mode):**
```text
Act as a technical writer. Create a complete onboarding guide for
a new developer joining the MoneyMind project.

Include:
1. Project overview and architecture
2. Development environment setup
3. Key files and their purposes
4. Common development tasks
5. Testing and deployment workflows
6. Who to ask for help (roles, not names)

Reference all relevant Knowledge Items.
Generate as a Walkthrough Artifact in Markdown format.
```

### Exercise 3.9: Architecture Decision Record

Create an ADR using artifacts:

**Prompt:**
```text
Generate an Architecture Decision Record (ADR) for our choice to use
Firebase Genkit for AI orchestration in MoneyMind.

Follow this template:
- Title
- Status (proposed/accepted/deprecated)
- Context
- Decision
- Consequences (positive and negative)
- Alternatives Considered

Create as a documentation artifact.
```

### Exercise 3.10: Debugging with Artifacts

Use artifacts to document debugging sessions:

**Prompt:**
```text
I'm seeing an issue where transactions are not being enriched properly.
The enrichTransactionFlow is returning undefined for some transactions.

Create a Debug Investigation Artifact that:
1. Lists possible causes
2. Provides diagnostic steps
3. Suggests fixes for each cause
4. Includes code snippets for testing
```

---

## Part 4: Advanced Patterns

### Pattern 1: Artifact Chains

Create a series of related artifacts, in this order:

1. **Requirements Artifact**: What we're building
2. **Design Artifact**: How we'll build it
3. **Implementation Artifact**: The actual code
4. **Test Artifact**: Verification evidence
5. **Documentation Artifact**: User-facing docs

### Pattern 2: Knowledge Item Layering

Group KIs by scope:

```text
Global KIs (all projects):
  - Code style preferences
  - Security requirements
  - Documentation standards

Project KIs (MoneyMind):
  - Architecture decisions
  - API contracts
  - Test conventions

Feature KIs (Notifications):
  - Notification types
  - Delivery channels
  - Rate limits
```

### Pattern 3: Artifact Reviews

Use artifacts for team reviews:

**Prompt:**
```text
Generate a Review Request Artifact for the notification system implementation.
Include:
- Summary of changes
- Areas needing special attention
- Questions for reviewers
- Testing instructions
- Screenshots of UI changes
```

---

## Part 5: Challenge Tasks

### Challenge 3.1: Create a Project Knowledge Base

Build a knowledge base for MoneyMind:

1. Create 5 Knowledge Items covering different aspects
2. Make them reference each other where it fits
3. Test that new sessions use this knowledge

### Challenge 3.2: Artifact-Driven Feature Development

Develop a new feature using only artifacts:

1. Create a Requirements Artifact
2. Generate an Implementation Plan Artifact
3. Have the agent implement based on the plan
4. Generate a Walkthrough Artifact
5. Create a Test Report Artifact

Document the entire flow.

### Challenge 3.3: Knowledge Item Maintenance

Create a workflow that keeps KIs current:

```text
Create a Knowledge Item maintenance prompt that:
1. Reviews all existing KIs
2. Identifies outdated information
3. Suggests updates based on recent code changes
4. Archives deprecated knowledge
```

---

## Key Takeaways

- **Artifacts** let you review the agent's output.
- **Knowledge Items** keep memory across sessions.
- Comment on artifacts to steer the agent.
- Keep your KIs organized and current.
- Use artifact chains for multi-phase work.

## Artifact Quick Reference

| Action | Command/Prompt |
|--------|----------------|
| Request plan | "Generate an Implementation Plan Artifact" |
| Get summary | "Create a Walkthrough Artifact" |
| Visual proof | "Generate a Screenshot Artifact" |
| Test evidence | "Create a Test Report Artifact" |
| View KIs | Check Knowledge Items panel |
| Create KI | "Create a Knowledge Item about..." |

---

## Summary

You have completed the three exercises:

1. **Exercise 1**: Intent-First Development with the Perceive-Plan-Act-Verify loop
2. **Exercise 2**: The Antigravity CLI in the terminal
3. **Exercise 3**: Artifacts and Knowledge Items

---

## Next Steps

- Return to the [Hands-On Lab](../README.md) to continue building MoneyMind
- Explore the [Code Examples](../../code-examples/) for more patterns
- Use the [Tutorials](../../tutorials/) as a quick reference
