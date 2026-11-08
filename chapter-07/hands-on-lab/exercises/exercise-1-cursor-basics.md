# Exercise 1: Cursor Basics

## Objective

Practice Cursor's core features:

- Tab
- Inline Edit
- the Agents Window
- background validation

> Naming note: "Composer" is the name of Cursor's in-house model that powers agent runs. The multi-agent surface is the Agents Window. Shortcuts and panel layouts change between releases. See [cursor.com/docs](https://cursor.com/docs).

## Prerequisites

- Cursor IDE installed
- A sample project (or use LinkForge from the hands-on lab)

## Part 1: Tab - Predictive Coding (15 minutes)

### Task 1.1: Experience Next-Action Prediction

1. Open the LinkForge project in Cursor
2. Navigate to `src/models.py`
3. Add a new field to the `Link` model:

```python
title: Optional[str] = Column(String(200), nullable=True)
```

4. **Observe**: After typing the field, press Tab and watch Cursor predict:
   - Updates to the `__repr__` method
   - Updates to the Pydantic schema in `schemas.py`
   - Suggestions for migration files

### Task 1.2: Multi-line Tab Completion

1. Open `src/shortener.py`
2. Start typing a new method:

```python
async def update_link(
    self,
    short_code: str,
```

3. Press Tab repeatedly to see Cursor complete:
   - Method parameters
   - Type hints
   - Implementation body
   - Error handling

**Question**: How does Tab differ from traditional autocomplete?

## Part 2: Inline Edit (Cmd+K) (15 minutes)

> As of November 7, 2026, Cursor has no separate Inline Edit prompt. Cmd+K (Ctrl+K) opens the agent with the selected lines referenced. The tasks below work the same way. Review the agent's diff before you keep it.

### Task 2.1: Refactor with Natural Language

1. Open `src/analytics.py`
2. Select the `_detect_device` method
3. Press `Cmd+K` (or `Ctrl+K` on Windows)
4. Type: "Add detection for smart TVs and gaming consoles"
5. Review the diff and accept

### Task 2.2: Extract a Function

1. Open `src/shortener.py`
2. Select the URL validation code inside `validate_url`
3. Press `Cmd+K`
4. Type: "Extract the domain validation logic into a separate `_validate_domain` helper method"
5. Review and refine if needed

### Task 2.3: Add Documentation

1. Select any undocumented function
2. Press `Cmd+K`
3. Type: "Add a complete Google-style docstring with Args, Returns, and Raises"

**Question**: When would you use Inline Edit vs Tab?

## Part 3: The Agents Window - Multi-File Operations (20 minutes)

### Task 3.1: Quick Inline Agent (Micro-Agent)

1. Press `Cmd+I` (or `Ctrl+I`) to open the agent chat
2. Enter this prompt:

```text
LinkForge already enforces a daily quota in src/ratelimit.py.
Add a second, hourly rate limit that:
- Limits requests per user per hour
- Uses Redis for tracking
- Returns 429 Too Many Requests when exceeded
- Is configurable via environment variable
```

3. Observe how Cursor:
   - Reads the existing `src/ratelimit.py` before writing anything
   - Extends that module (or adds a sibling file) with the hourly limit
   - Updates imports and wires the new limit into `main.py`

### Task 3.2: The Agents Window

1. Open the Agents Window. Open the Command Palette (Cmd+Shift+P / Ctrl+Shift+P), then choose **Open Agents Window**.
2. Find these three functions. They are present in every panel layout:
   - **Scope**: which files the agent intends to modify (its blast radius)
   - **Review**: a diff preview you inspect before anything lands
   - **Steering**: the conversation thread where you adjust course mid-run

3. Enter this prompt:

```text
Add a link expiration cleanup job:
1. Create a background task that runs every hour
2. Find all expired links in the database
3. Log the cleanup action
4. Emit a metric for monitoring
5. Add configuration for cleanup batch size
```

4. Review the plan before execution
5. Interrupt mid-run to add: "Also send email notifications to users whose links are expiring within 24 hours"

**Question**: When would you reach for the quick inline agent versus the full Agents Window?

### Task 3.3: Parallel Agents in Worktrees

The Agents Window can run several agents at once. Give each agent its own git worktree (an isolated checkout). Then simultaneous tasks cannot overwrite one another's files.

1. Start one agent on a small bug fix
2. Start a second agent on an unrelated test refactor
3. Review each diff independently before accepting

**Question**: Why does worktree isolation matter when two agents touch the same repository?

## Part 4: Background Validation (10 minutes)

Before an edit reaches you, Cursor can test it in an off-screen editor. It reads what the language servers report and corrects problems first.

> The book calls this the "shadow workspace," a name from Cursor's 2024 documentation. Cursor's documentation does not use the name today. Treat this part as observation. It is not a guaranteed behavior.

### Task 4.1: Observe Self-Correction

1. Open the agent chat and enter a prompt that might produce errors:

```text
Create a new SQLAlchemy model that references a non-existent table called "categories"
```

2. **Observe**:
   - The proposed change goes into an off-screen editor first
   - It collects diagnostics from your installed language servers and linters
   - If there are errors, it self-corrects before showing you

3. Watch the suggestion process - you should see:
   - Initial generation
   - Background validation
   - Corrected output (if needed)

### Task 4.2: Verify Background Validation Benefits

1. Try this intentionally broken prompt:

```text
Add a method to ShorteningService that calls self.nonexistent_method() and returns the result
```

2. Notice how Cursor either:
   - Refuses to generate obviously broken code
   - Warns you about the issue
   - Suggests alternatives

## Part 5: Directing Context (10 minutes)

> Current Cursor has no `@Codebase`, `@Docs`, `@Web`, or `@Git` symbols (the book's context symbols). The agent searches your codebase and the web with its own tools.

The @-mentions available are:

- files and folders
- `@Commit` and `@Branch` for git diffs
- `@Chats` for an earlier conversation
- `@Terminals`
- `@Browser`

These tasks practice those equivalents.

### Task 5.1: Let the Agent Search the Codebase

1. Open the agent chat
2. Enter: `Explain how the Redis caching layer integrates with the shortening service`
3. Observe which files the agent searches and reads before it answers (this is the search the book's `@Codebase` describes)

### Task 5.2: Point at Exact Files

1. Enter: `@src/cache.py @src/shortener.py Where does a cache miss fall back to the database?`
2. Compare the answer's focus with Task 5.1

### Task 5.3: Ask for Current Documentation

1. Enter: `Search the web for the current FastAPI documentation on OAuth2 password flow, then explain how to add it to this project`
2. Notice that the agent runs a web search on its own (this takes the place of the book's `@Docs` and `@Web`)

### Task 5.4: Bring In Git Context

1. Commit your work from the earlier parts on a branch
2. Enter: `@Branch Summarize what changed on this branch`

**Question**: When would you @-mention a file yourself rather than let the agent search?

## Deliverables

Create a document answering:

1. **Tab vs Inline Edit**: When do you use each?
2. **Quick inline agent vs the Agents Window**: What are the trade-offs?
3. **Background validation**: How does it reduce "broken code" fatigue?
4. **Directing context**: Give an example use case for each (agent codebase search, a file @-mention, a web search, `@Branch`)

## Bonus Challenge

Use Cursor to add a complete "Link Analytics Dashboard" feature:

1. New endpoint: `GET /api/v1/dashboard`
2. Returns aggregated stats for all user's links
3. Includes charts data (clicks over time)
4. Add caching for performance

Track how many iterations it takes to get working code.

## Summary

| Feature | Best For | How to Open |
|---------|----------|-------------|
| Tab | Flow state, completions | Tab |
| Selection to the agent (replaces Inline Edit) | Scoped transformations | Cmd+K |
| Quick inline agent | Rapid single-file changes | Cmd+I |
| Agents Window | Multi-file features, parallel agents | Command Palette, then Open Agents Window |
| Background validation | Error-free suggestions | (Automatic) |
