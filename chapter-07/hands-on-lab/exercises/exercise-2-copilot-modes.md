# Exercise 2: GitHub Copilot Modes

## Objective

Practice GitHub Copilot's chat modes and the cloud agent:

- Ask Mode (exploratory)
- Edit Mode (collaborative)
- Agent Mode (autonomous)
- Plan Mode
- the Copilot cloud agent

> **Tool note.** The book describes three Copilot Chat modes in VS Code: Ask, Edit, and Agent. VS Code deprecated Edit mode in version 1.110. VS Code 1.126 and later offer it only when an administrator has disabled Agent mode by policy. Part 2 below practices Edit mode's discipline in Agent mode. You use a fixed working set and approve every change.

## Prerequisites

- VS Code with GitHub Copilot extension
- GitHub account with Copilot enabled
- LinkForge project (or any Python project)

## Part 1: Ask Mode - Exploratory (15 minutes)

Ask Mode is read-only. It explains code without making changes.

### Task 1.1: Code Explanation

1. Open LinkForge in VS Code
2. Open the Chat view (Ctrl+Alt+I on Windows and Linux, Ctrl+Cmd+I on Mac) and pick **Ask** in the mode picker
3. Select the `ShorteningService` class in `src/shortener.py`
4. Ask Copilot:

```text
Explain this class architecture. What design patterns does it use?
```

5. **Observe**: Copilot analyzes without modifying files

### Task 1.2: API Exploration

1. With no code selected, ask:

```text
How does FastAPI dependency injection work in this project?
```

2. Then ask follow-up questions:

```text
Show me all the dependencies that get injected
```

### Task 1.3: Learn from Context

1. Ask:

```text
What testing patterns are used in this project?
```

2. Then:

```text
How would I add a new test for the rate limiting feature?
```

**Key Insight**: Ask Mode retrieves context from open files and workspace but performs no file system operations.

## Part 2: The Edit Mode Discipline, in Agent Mode (20 minutes)

Edit Mode had write access only to a "working set" you chose. Current VS Code has no Edit mode. Follow these steps instead:

1. Switch to Agent mode.
2. Attach exactly the files you want changed. Drag them from the Explorer into the chat input.
3. Tell the agent to change nothing else.
4. Review each proposed edit before you keep it.

### Task 2.1: Guided Refactoring

1. Open `src/shortener.py`
2. Switch to **Agent** in the mode picker
3. **Fix the working set**: attach `src/shortener.py` to the chat
4. Enter:

```text
Refactor the validate_url method to use a URLValidator class instead of inline validation. Change only the attached file.
```

5. **Review the diff**: Copilot shows the proposed changes
6. Keep or undo each change

### Task 2.2: Multi-File Edit

1. Attach three files:
   - `src/models.py`
   - `src/schemas.py`
   - `src/shortener.py`

2. Request:

```text
Add a "description" field to links. Change only the attached files. It should:
- Be optional in the Link model
- Appear in LinkCreate and LinkResponse schemas
- Be stored in the database
```

3. Review each file's changes in the diff view
4. Keep or undo file by file, and check that nothing outside the three files changed

### Task 2.3: Iterative Refinement

1. After keeping the changes, ask:

```text
Now add validation to ensure description is max 500 characters
```

2. Copilot keeps the context of the previous edits

**Key Insight**: you approve every change before it stays. The review step keeps you in the loop.

## Part 3: Agent Mode - Autonomous (25 minutes)

Agent Mode can run terminal commands, crawl files, and self-correct.

### Task 3.1: Self-Healing Bug Fix

1. Switch to Agent Mode in Copilot Chat
2. Introduce a deliberate bug in `src/shortener.py`:

```python
# Change this:
return ''.join(secrets.choice(BASE62_ALPHABET) for _ in range(length))

# To this (bug):
return ''.join(secrets.choice(BASE62_ALPHABET) for _ in range(lenght))  # typo!
```

3. Ask Copilot Agent:

```text
Run the tests and fix any errors you find
```

4. **Observe** the agent:
   - Runs `pytest` in terminal
   - Reads the error output
   - Identifies the typo
   - Fixes it
   - Re-runs tests to verify

### Task 3.2: Feature Implementation with Discovery

1. Ask the Agent:

```text
Add a feature to track link click sources (direct, social, email, other).
Figure out where changes need to be made by exploring the codebase.
```

2. **Observe** the agent:
   - Crawls the file system
   - Identifies relevant files
   - Proposes a plan
   - Implements changes
   - Optionally runs tests

### Task 3.3: Plan Mode Before Agent Mode

Plan Mode drafts an implementation plan up front. It asks clarifying questions as it goes. No code changes happen until you approve. Check the plan, then hand it to Agent Mode.

1. Switch to Plan Mode in the chat mode picker
2. Ask: "Plan how to add link click-source tracking (direct, social, email, other) to this project"
3. Review and adjust the plan, then hand it to Agent Mode to execute

### Task 3.4: Complex Multi-Step Task

1. Create a GitHub issue (or simulate locally):

```markdown
## Feature: Link QR Code Generation

Add ability to generate QR codes for shortened links.

Requirements:
- New endpoint: GET /api/v1/links/{code}/qr
- Return PNG image
- Support size parameter (default 200x200)
- Cache generated QR codes in Redis
```

2. Assign the issue to Copilot from the assignees list (this dispatches the Copilot cloud agent)
3. Watch it:
   - Install `qrcode` package
   - Create the endpoint
   - Add caching
   - Write tests

## Part 4: Mode Comparison (10 minutes)

### Task 4.1: Same Task, Three Modes

Try the same task in each mode:

**Task**: "Add a last_accessed_at field to the Link model"

1. **Ask Mode**: Get explanation of what needs to change
2. **Plan Mode**: Get a step-by-step plan, without code changes
3. **Agent Mode**: Let it implement end-to-end, reviewing each edit before you keep it

### Task 4.2: Document Your Findings

| Aspect | Ask Mode | Plan Mode | Agent Mode |
|--------|----------|-----------|------------|
| Autonomy Level | | | |
| File System Access | | | |
| Terminal Access | | | |
| Best Use Case | | | |
| Human Oversight | | | |

## Part 5: Copilot Beyond the IDE (15 minutes)

### Task 5.1: Copilot in GitHub.com

1. Push your LinkForge changes to GitHub
2. Create a Pull Request
3. **Observe**: Copilot can generate PR summaries
4. Request a code review from Copilot

### Task 5.2: Copilot CLI

Copilot CLI is an agent that runs in your terminal. It can plan a task, edit files, and run commands without leaving the shell.

1. Install it with `npm install -g @github/copilot` (Node.js 22 or later). For the winget, Homebrew, and install-script options, see [docs.github.com/copilot](https://docs.github.com/copilot). Then start a session with `copilot`.
2. From the LinkForge directory, try:

```text
Find all Python files modified in the last week and summarize what changed
```

3. Then try a small edit task:

```text
Add a --version flag to the __main__ entry point in src/main.py and document it in the README
```

### Task 5.3: The Cloud Agent via Issues

1. Create a GitHub Issue:

```markdown
Title: Add Prometheus metrics endpoint

Description:
- Create /metrics endpoint
- Track: requests_total, request_duration, active_connections
- Use prometheus-fastapi-instrumentator
```

2. Assign the issue to Copilot from the assignees list
3. **Observe**: The cloud agent works in the background and opens a draft PR

## Deliverables

Create a comparison document:

1. **Mode Selection Guide**: When to use each mode
2. **Autonomy Ladder**: Diagram showing control vs automation
3. **Best Practices**: 3 tips for each mode
4. **Integration Points**: How Copilot works across GitHub ecosystem

## Bonus Challenge

Set up a complete CI/CD pipeline using only Copilot:

1. Create issues for:
   - Dockerfile optimization
   - GitHub Actions workflow
   - Staging deployment
   - Production deployment

2. Assign all to Copilot
3. Review and merge the resulting PRs
4. Document the experience

## Summary

| Mode | Trigger | Capability | Use Case |
|------|---------|------------|----------|
| Ask | Mode picker in the Chat view | Read-only exploration | Learning, planning |
| Agent | Mode picker, or Ctrl+Shift+I / Shift+Cmd+I | Full autonomy + tools | Complex features; attach files and review each edit for Edit-mode precision |
| Plan | Mode picker in chat | Plan before code is touched | Verify-then-execute |
| Cloud agent | Assign a GitHub Issue to Copilot | Background execution | CI/CD, automation |

## Key Takeaways

1. **Ask Mode**: low risk. Start here for unfamiliar code.
2. **Agent Mode with a fixed working set**: medium risk, high control. This is the old Edit Mode discipline. Use it for important changes.
3. **Agent Mode**: higher risk. Use it for well-defined tasks. Run Plan Mode first for complex ones.
4. **Cloud agent**: runs in the background. Use it for routine automation. GitHub records every action in the execution history.
