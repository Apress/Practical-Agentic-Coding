# Exercise 1: SDD Basics - Converting Vague Requirements to Specs

> This practice exercise has fixed answers. See the [Answer Key](#answer-key) at the end of this file. The four open-ended chapter exercises are in [`../../challenge-lab/`](../../challenge-lab/README.md). They give success criteria instead of answer keys.

## Overview

In this exercise, you turn vague, creative requirements into concrete, testable specifications.

## Learning Objectives

- Tell "Vibe" requirements from "Spec" requirements
- Convert abstract goals into measurable constraints
- Spot ambiguous requirements

## Background: Vibe vs. Spec

Chapter 5, Section 5.2 explains the difference. Use this table as a quick reference for the tasks below.

| Aspect | Vibe (Outcome-led) | Spec (Technical) |
|--------|--------------------|------------------|
| Nature | Subjective, qualitative | Objective, quantitative |
| Purpose | State the intended outcome | Define measurable behavior |
| Examples | "Make it snappy" | "Response time < 200ms" |
| LLM Interpretation | Wide latitude | Narrow constraints |
| Consistency | Often inconsistent | Consistently achievable |

## Exercise Tasks

### Task 1: Identify Vibe vs. Spec (10 minutes)

Categorize each requirement as "Vibe" or "Spec":

1. "The dashboard should feel modern and clean"
2. "User authentication must use OAuth 2.0"
3. "Error messages should be helpful and friendly"
4. "The API must return responses within 500ms"
5. "The app should work on mobile devices"
6. "Data must be encrypted at rest using AES-256"
7. "The UI should be intuitive"
8. "All endpoints must use HTTPS"

**Your Answers:**

| # | Requirement | Vibe or Spec? |
|---|-------------|---------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |
| 6 | | |
| 7 | | |
| 8 | | |

---

### Task 2: Convert Vibe to Spec (20 minutes)

Rewrite each vague "vibe" requirement as a concrete specification:

#### Example

**Vibe**: "The application must feel very fast"
**Spec**: "The system response time SHALL be under 200 milliseconds for 95% of requests"

#### Your Turn

1. **Vibe**: "The layout should be modern, clean, and spacious"

   **Your Spec**: _____________________________________________

2. **Vibe**: "Error messages should be presented in a useful and friendly manner"

   **Your Spec**: _____________________________________________

3. **Vibe**: "The app should handle lots of users"

   **Your Spec**: _____________________________________________

4. **Vibe**: "The code should be well-tested"

   **Your Spec**: _____________________________________________

5. **Vibe**: "The system should be secure"

   **Your Spec**: _____________________________________________

---

### Task 3: Write EARS-Style Requirements (15 minutes)

EARS (Easy Approach to Requirements Syntax) gives you patterns for clear requirements:

| Pattern | Format | Example |
|---------|--------|---------|
| When/Then | WHEN [trigger] THEN [system] SHALL [action] | WHEN user clicks submit THEN system SHALL validate input |
| Where | WHERE [condition] THEN [system] SHALL [action] | WHERE user is admin THEN system SHALL display admin panel |
| If/Then | IF [condition] THEN [system] SHALL [action] | IF connection fails THEN system SHALL retry 3 times |

Write EARS-style requirements for these scenarios:

1. **Scenario**: User searches for stories

   **Your Requirement**: _____________________________________________

2. **Scenario**: Story is older than 48 hours

   **Your Requirement**: _____________________________________________

3. **Scenario**: Summary generation fails

   **Your Requirement**: _____________________________________________

4. **Scenario**: Admin wants to force refresh

   **Your Requirement**: _____________________________________________

---

### Task 4: Practice with Kiro (30 minutes)

1. Open Kiro and create a new spec for a simple "Task Manager" application.
2. Start with the vibe prompt:

   ```text
   I want to build a task manager that helps developers track their work.
   It should be simple and not overwhelming. Focus on getting things done.
   ```

3. Then add concrete constraints:

   ```text
   Constraint: Use Python with FastAPI
   Constraint: Store tasks in SQLite for local development
   Constraint: Each task must have title, description, status, and due date
   Constraint: Tasks can have one of three statuses: TODO, IN_PROGRESS, DONE
   Requirement: Users can filter tasks by status
   Requirement: Users can sort tasks by due date
   ```

4. Review the generated requirements and design documents.
5. List any gaps or ambiguities in the generated specs.

**Reflection Questions:**

- What did Kiro interpret differently than you expected?
- Which constraints were most effective at guiding the output?
- What additional constraints would you add?

---

## Answer Key

### Task 1: Identify Vibe vs. Spec

| # | Requirement | Answer |
|---|-------------|--------|
| 1 | "The dashboard should feel modern and clean" | Vibe |
| 2 | "User authentication must use OAuth 2.0" | Spec |
| 3 | "Error messages should be helpful and friendly" | Vibe |
| 4 | "The API must return responses within 500ms" | Spec |
| 5 | "The app should work on mobile devices" | Vibe (could be Spec with specific breakpoints) |
| 6 | "Data must be encrypted at rest using AES-256" | Spec |
| 7 | "The UI should be intuitive" | Vibe |
| 8 | "All endpoints must use HTTPS" | Spec |

### Task 2: Sample Spec Conversions

1. "The layout should be modern, clean, and spacious"
   - **Spec**: "The UI SHALL implement a 12-column grid system with minimum 16px margins between elements and maximum 1200px content width"

2. "Error messages should be presented in a useful and friendly manner"
   - **Spec**: "Validation errors SHALL return HTTP 400 with JSON body containing 'error' field with user-facing message and 'code' field with machine-readable error code"

3. "The app should handle lots of users"
   - **Spec**: "The system SHALL support 1000 concurrent users with response times under 500ms at 95th percentile"

4. "The code should be well-tested"
   - **Spec**: "Unit test coverage SHALL be minimum 70% for all modules; critical paths SHALL have 90% coverage"

5. "The system should be secure"
   - **Spec**: "The system SHALL authenticate all API requests using JWT tokens; passwords SHALL be hashed using bcrypt with minimum 10 rounds; all sensitive data SHALL be encrypted at rest using AES-256"

### Task 3: Sample EARS Requirements

1. **User searches for stories**
   - WHEN a user submits a search query THEN the system SHALL return stories whose title or summary matches the query, ordered by relevance
2. **Story is older than 48 hours**
   - WHERE a story's publication time is more than 48 hours old THEN the system SHALL exclude it from the main feed
3. **Summary generation fails**
   - IF summary generation fails THEN the system SHALL retry up to 3 times and, on final failure, SHALL display the story headline without a summary and log the error
4. **Admin wants to force refresh**
   - WHEN an admin triggers a manual refresh THEN the system SHALL re-fetch stories from all sources and regenerate the current briefing

Your wording will differ. Check that each requirement names a concrete trigger and an observable behavior. Task 4 is open-ended practice in Kiro and has no fixed answer.

## Summary

Check your work against these rules:

- **Vibe** states the intended outcome. It leaves room for interpretation.
- **Spec** gives measurable criteria you can test.
- Write requirements with EARS patterns.
- Include acceptance criteria with every spec.
