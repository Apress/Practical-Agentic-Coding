# Custom Sub-Agents

This directory holds example sub-agent definitions for Claude Code.

## Overview

A sub-agent is a helper agent with its own context window, instructions, and tool list. This file covers definitions and invocation only.

Why and when to use sub-agents, how they run, how deep they nest, and what a spawn costs: Chapter 8, Section 8.4.

## How Sub-Agents Work

```text
┌─────────────────────────────────────────────────────────────────┐
│                     Main Claude Code Session                     │
│                                                                 │
│  > Review the security of my auth changes                       │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Security        │  │ Test Writer     │  │ Documentation   │ │
│  │ Reviewer        │  │ Agent           │  │ Agent           │ │
│  │                 │  │                 │  │                 │ │
│  │ [Isolated       │  │ [Isolated       │  │ [Isolated       │ │
│  │  Context]       │  │  Context]       │  │  Context]       │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Built-in Sub-Agents

Table 8.7 lists the three built-in agents: Explore, Plan, and General-purpose. Explore runs on the main conversation's model. Explore and Plan stay read-only.

## Creating Custom Sub-Agents

Place markdown files in `.claude/agents/`:

```text
.claude/
└── agents/
    ├── security-reviewer.md
    └── test-writer.md
```

Both files in this directory are complete definitions. Copy them into a project's `.claude/agents/` unchanged. Add your own next to them, in the format below.

### Agent Definition Format

```markdown
---
name: agent-name
description: Brief description for when to use this agent
tools: Read, Grep, Glob, Write
model: sonnet
---

System prompt and instructions for the agent.
```

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier for the agent |
| `description` | Yes | When/why to use this agent |
| `tools` | No | Comma-separated list (or YAML list) of allowed tools. Omit it to inherit every tool |
| `model` | No | `sonnet`, `opus`, `haiku`, a full model ID, or `inherit` |

The documentation lists more optional fields, such as `permissionMode`, `skills`, `mcpServers`, and `hooks`. See the sub-agents page at [code.claude.com/docs](https://code.claude.com/docs).

## Files in This Directory

### security-reviewer.md

A security-focused agent that:
- Reviews code for OWASP Top 10 vulnerabilities
- Checks authentication and authorization
- Identifies sensitive data exposure
- Provides prioritized findings

### test-writer.md

A testing-focused agent that:
- Generates unit tests for new code
- Creates integration test scenarios
- Writes edge case tests
- Follows project testing conventions

## Using Sub-Agents

### Automatic Delegation

Claude Code delegates to a matching sub-agent automatically:

```text
> Review the security of my recent auth changes
```

If you have a security-reviewer agent defined, Claude may use it automatically.

### Explicit Invocation

Name the agent in the prompt. Claude delegates to it:

```text
> Use the security-reviewer subagent to analyze src/auth/
```

Or @-mention it. Type `@` and pick the agent from the typeahead, or write `@agent-security-reviewer`.

To run a whole session as one agent, with its tool restrictions and model, start Claude Code with `claude --agent security-reviewer`.

### Managing Agents

Edit the files in `.claude/agents/` (project) or `~/.claude/agents/` (personal) directly. Or ask Claude to create or change one. `/agents` prints a reminder of these options. It takes no subcommands.

## Example Workflow

### Step 1: Define the Agent

Create `.claude/agents/api-reviewer.md`:

```markdown
---
name: api-reviewer
description: API design expert. Use for REST API review.
tools: Read, Grep, Glob
model: sonnet
---

You are a senior API architect specializing in REST API design.

When invoked:
1. Review endpoint structure and naming
2. Check for consistent error handling
3. Validate request/response schemas
4. Verify authentication requirements
5. Check rate limiting implementation

Output format:
- Summary of API structure
- Issues found (prioritized)
- Recommendations
```

### Step 2: Use the Agent

```text
> Review the API endpoints in src/api/ for design consistency
```

### Step 3: Review Results

The agent works in a separate context. It runs in the background unless you wait on it. When it finishes, it reports back a short summary.

## Troubleshooting

### Agent Not Found

- Check file is in `.claude/agents/`
- Verify YAML frontmatter is valid
- Check `name` field matches
- Check the frontmatter has both `name` and `description`, the only required fields

### Agent Not Being Used

- Make the description clear and specific
- Check that the agent matches the task type
- Try explicit invocation

### Limited Output

- The agent has its own context window
- Complex tasks may need multiple passes
- Break the task into smaller tasks

## See Also

- [Claude Code Documentation](https://code.claude.com/docs)
- [Sub-Agent Reference](https://code.claude.com/docs/en/sub-agents)
