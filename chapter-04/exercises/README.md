# Chapter 4 Exercises

This directory holds the hands-on exercises for Chapter 4: "Recent Advances in AI and Autonomous Agents."

## Overview

| Exercise | Title | Time | Difficulty | Focus |
|----------|-------|------|------------|-------|
| 1 | [Create MCP Configuration](./exercise-1-mcp-config.md) | 30-45 min | Beginner-Intermediate | MCP servers, security |
| 2 | [Create A2A Agent Card](./exercise-2-agent-card.md) | 35-45 min | Intermediate | JSON Schema, capabilities |
| 3 | [Write AGENTS.md File](./exercise-3-agents-md.md) | 30-40 min | Beginner-Intermediate | Agent behavior, workflows |

The book's in-chapter Exercise 4.2 (extend the synchronous invocation with tool use) has a worked solution in [`../code-examples/invocation-patterns/tool_using_invocation.py`](../code-examples/invocation-patterns/tool_using_invocation.py).

## Prerequisites

1. **Read Chapter 4.** The exercises here are numbered on their own:
   - Exercise 3 is the book's Exercise 4.1 (Section 4.5).
   - Exercise 4.2 has its worked solution in `code-examples/` (see above).
   - The three end-of-chapter Chapter Exercises are open questions with no files here. For the AGENTS.md one, reuse Exercise 3's section structure. For the approval-workflow one, start from the Accountability and Intervention sections of the [Governance Guide](../tutorials/governance-guide.md).

2. **Do the matching tutorial first.**
   - Exercise 1 follows [MCP Setup](../tutorials/mcp-setup.md)
   - Exercise 2 follows [A2A Integration](../tutorials/a2a-integration.md)
   - Exercise 3 follows the [AGENTS.md Guide](../tutorials/agents-md-guide.md)

3. **Keep the code examples open** for comparison: [mcp-config](../code-examples/mcp-config/), [a2a-protocol](../code-examples/a2a-protocol/), [agents-md](../code-examples/agents-md/).

4. **Have a way to validate JSON.** Your editor's JSON support is enough. Or run `python -m json.tool yourfile.json`. If the file parses, it prints the file back, reformatted. If not, it names the line and column of the first syntax error.

## Learning Path

Do the exercises in order:

```text
Exercise 1: MCP Configuration
         │
         │  Learn how agents connect to tools
         ▼
Exercise 2: A2A Agent Card
         │
         │  Learn how agents discover each other
         ▼
Exercise 3: AGENTS.md File
         │
         │  Learn how to control agent behavior
         ▼
    Ready for Chapter 5 (Amazon Kiro)
```

## Exercise Summaries

### Exercise 1: Create MCP Configuration

**Scenario**: Configure MCP for a development team needing GitHub, PostgreSQL, Slack, and filesystem access.

**Key Skills**:
- Structuring MCP configuration files
- Using environment variables for credentials
- Applying security best practices
- Sandboxing filesystem access

**Output**: A complete `mcp_config.json` file

### Exercise 2: Create A2A Agent Card

**Scenario**: Create an agent card for a Security Review Agent that performs SAST analysis and OWASP assessments.

**Key Skills**:
- Defining agent identity and capabilities
- Writing JSON Schema for inputs/outputs
- Configuring governance and compliance
- Setting up authentication

**Output**: A complete `security_agent.json` file

### Exercise 3: Write AGENTS.md File

**Scenario**: Write agent instructions for an E-commerce Order Management System.

**Key Skills**:
- Creating effective agent personas
- Defining project rules and workflows
- Establishing security boundaries
- Writing actionable instructions

**Output**: A complete `AGENTS.md` file

## Assessment Criteria

Each exercise includes:
- Validation checklists to verify your work
- Common mistakes to avoid
- Bonus challenges for advanced learners
- Complete solutions (hidden by default)

## Tips for Success

1. Read the whole scenario before you write anything. Each one has constraints in the requirements list.
2. Write your own version before you open the solution.
3. Validate your JSON before you compare. A misplaced comma looks like a design difference.
4. Do at least one bonus challenge. In the bonus challenges, the constraints start to conflict.

## Time

| Exercise | Core | With bonus |
|----------|------|------------|
| 1 | 30 min | 45 min |
| 2 | 35 min | 45 min |
| 3 | 30 min | 40 min |

All three take about 1.5 to 2.25 hours, depending on how much bonus work you do.

## If you get stuck

1. Re-read the matching tutorial section.
2. Open the equivalent file in `../code-examples/` and compare it with yours.
3. Expand the exercise's hints one at a time.
4. Then look at the solution.

## Next Steps

After completing all exercises:

1. **Chapter 5**: Amazon Kiro and spec-driven development
2. **Chapter 6**: Google Antigravity and the Antigravity CLI
3. **Chapter 7**: Cursor and GitHub Copilot in agent mode
4. **Chapter 8**: Claude Code, CLAUDE.md, hooks, and MCP

## Related Resources

- [Chapter 4 README](../README.md)
- [Code Examples](../code-examples/)
- [Tutorials](../tutorials/)
