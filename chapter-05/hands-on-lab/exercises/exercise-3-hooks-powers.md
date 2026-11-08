# Exercise 3: Configuring Hooks and Powers

> This practice exercise has model answers. See the [Sample Solutions](#sample-solutions) at the end of this file. The four open-ended chapter exercises are in [`../../challenge-lab/`](../../challenge-lab/README.md). They give success criteria instead of answer keys.

> **Hook format differs from the book.** The JSON in this exercise uses the `.kiro.hook` layout from Kiro IDE 0.x. Kiro IDE 1.0 and later save new hooks in a different format and cannot create new manual hooks. See [Hook Configuration Format](#hook-configuration-format).

## Overview

In this exercise, you configure Kiro Hooks to automate development tasks. You also install Kiro Powers to add agent capabilities.

## Learning Objectives

- Name the Kiro Hook trigger types and their use cases
- Create custom hooks for common development tasks
- Install and configure Kiro Powers
- Combine hooks and powers in one workflow

## Background: Kiro Hooks

### Hook Architecture

Each hook has two parts:
- **Trigger (When)**: The event that activates the hook
- **Action (Then)**: The AI-powered response that executes

### Trigger Types

| Trigger | Description | Use Case |
|---------|-------------|----------|
| `UserPromptSubmit` | User submits a prompt | Context gathering |
| `SessionStart` | Agent session begins | Load project context |
| `Stop` | Agent finishes responding | Follow-up actions |
| `PreToolUse` / `PostToolUse` | Before/after a tool invocation | Inspect or react to tool calls |
| `PostFileCreate` | New file created | Initial setup/scaffolding |
| `PostFileSave` | File is saved | Validation, test synchronization |
| `PostFileDelete` | File is removed | Cleanup tasks |
| Manual Trigger | Manual execution | On-demand operations |

### Hook Configuration Format

The JSON in this exercise uses the `.kiro.hook` layout from Kiro IDE 0.x. The hooks this chapter ships use the same layout. That layout names the triggers differently from the book and from Kiro 1.0:

| Book and Kiro 1.0 name | `when.type` in a `.kiro.hook` file |
|------------------------|-------------------------------------|
| `PostFileSave` | `fileEdited` |
| `PostFileCreate` | `fileCreated` |
| `PostFileDelete` | `fileDeleted` |
| `UserPromptSubmit` | `promptSubmit` |
| `Stop` | `agentStop` |
| `PreToolUse` / `PostToolUse` | `preToolUse` / `postToolUse` |
| Manual Trigger | `userTriggered` |

```json
{
  "enabled": true,
  "name": "Hook Name",
  "description": "What the hook does",
  "version": "1",
  "when": {
    "type": "fileEdited",
    "patterns": ["*.py", "*.js"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "Instructions for the agent when triggered"
  }
}
```

In Kiro IDE 1.0 and later:

- Kiro lists `.kiro.hook` files as legacy hooks, with an upgrade badge.
- Hooks you create are saved as `.kiro/hooks/<name>.json`.
- Those files use `trigger`, `matcher` (a regular expression), and `action` fields in place of `when` and `then`.
- You can no longer create new manual hooks.

Kiro's [hooks documentation](https://kiro.dev/docs/hooks/) has the current schema. Its [What's new in IDE 1.0: Hooks](https://kiro.dev/docs/ide/whats-new-v1/hooks/) page has the full trigger mapping.

## Exercise Tasks

### Task 1: Analyze Hook Configurations (15 minutes)

Read each hook configuration below. Explain what it does:

#### Hook A: Test Coverage

```json
{
  "enabled": true,
  "name": "Auto Test Coverage",
  "version": "1",
  "when": {
    "type": "fileEdited",
    "patterns": ["*.py"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "Analyze modified file, identify changed functions, check test coverage, generate tests for gaps"
  }
}
```

**Questions:**

1. When does this hook trigger?

   _____________________________________________

2. What files does it monitor?

   _____________________________________________

3. What does the agent do when triggered?

   _____________________________________________

4. What potential issues might this hook cause?

   _____________________________________________

---

#### Hook B: Documentation Sync

```json
{
  "enabled": true,
  "name": "Documentation Sync",
  "version": "1",
  "when": {
    "type": "userTriggered"
  },
  "then": {
    "type": "askAgent",
    "prompt": "Review source changes and update README.md and docs folder"
  }
}
```

**Questions:**

1. Why is this hook set to Manual Trigger instead of automatic?

   _____________________________________________

2. What benefit does manual triggering provide?

   _____________________________________________

---

### Task 2: Design Custom Hooks (30 minutes)

Design a hook for each scenario below. Write the complete JSON configuration for each one.

#### Scenario A: Security Audit Hook

Create a hook that performs security checks when any Python file is saved.

**Requirements:**
- Check for hardcoded credentials
- Identify SQL injection vulnerabilities
- Flag insecure imports
- Log findings to a security report

**Your Hook Configuration:**

```json
{
  "enabled": true,
  "name": "[YOUR NAME]",
  "description": "[YOUR DESCRIPTION]",
  "version": "1",
  "when": {
    "type": "[YOUR TRIGGER]",
    "patterns": ["[YOUR PATTERNS]"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "[YOUR PROMPT]"
  }
}
```

---

#### Scenario B: API Documentation Generator

Create a hook that generates OpenAPI documentation when API route files change.

**Requirements:**
- Monitor changes to `**/routes/*.py` files
- Extract endpoint definitions
- Generate/update OpenAPI schema
- Validate schema after generation

**Your Hook Configuration:**

```json
{

}
```

---

#### Scenario C: Commit Message Helper

Create a hook that generates semantic commit messages when the agent completes a task.

**Requirements:**
- Trigger after agent finishes
- Analyze changes made
- Generate conventional commit message
- Include ticket reference if available

**Your Hook Configuration:**

```json
{

}
```

---

#### Scenario D: New Component Scaffolding

Create a hook that scaffolds boilerplate when a new React component file is created.

**Requirements:**
- Trigger on `.tsx` file creation in `components/` directory
- Generate component skeleton
- Create corresponding test file
- Add to component index

**Your Hook Configuration:**

```json
{

}
```

---

### Task 3: Kiro Powers Installation (20 minutes)

#### Part A: Identify Required Powers

For a project that needs to:
- Deploy AWS infrastructure
- Generate architecture diagrams
- Test APIs with Postman
- Monitor application performance

List which Kiro Powers you would install:

| Requirement | Power Name | Purpose |
|-------------|------------|---------|
| AWS Infrastructure | | |
| Architecture Diagrams | | |
| API Testing | | |
| Monitoring | | |

#### Part B: Powers Configuration Walkthrough

Answer these questions about configuring the AWS Infrastructure Power:

1. Where do you find the Powers marketplace in Kiro?

   _____________________________________________

2. What credentials might be required for AWS powers?

   _____________________________________________

3. How do you verify a Power is working correctly?

   _____________________________________________

4. What should you do if a Power fails to install?

   _____________________________________________

---

### Task 4: Combined Workflow Design (25 minutes)

Design an automated workflow with hooks and powers for a continuous deployment scenario.

#### Scenario: Feature Branch Workflow

When a developer completes work on a feature:
1. Tests should run automatically
2. Documentation should update
3. Infrastructure should validate
4. Code should be ready for PR

**Design the workflow:**

| Step | Hook/Power | Trigger | Action |
|------|-----------|---------|--------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |

**Write configuration for the most complex hook in your workflow:**

```json
{

}
```

---

### Task 5: Best Practices Quiz (10 minutes)

1. **Why should you "start simple" with hooks?**

   _____________________________________________

2. **How can you prevent hooks from slowing down development?**

   _____________________________________________

3. **Where are hook configuration files stored?**

   _____________________________________________

4. **How do you temporarily disable a hook without deleting it?**

   _____________________________________________

5. **What's the benefit of using GLOB patterns in hook triggers?**

   _____________________________________________

---

## Sample Solutions

### Task 2: Sample Hook Configurations

#### Scenario A: Security Audit Hook

```json
{
  "enabled": true,
  "name": "Security Audit",
  "description": "Performs security checks on Python files when saved, looking for vulnerabilities and insecure patterns",
  "version": "1",
  "when": {
    "type": "fileEdited",
    "patterns": ["**/*.py"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "Perform a security audit on this file:\n1. Check for hardcoded credentials (API keys, passwords, tokens)\n2. Identify potential SQL injection vulnerabilities\n3. Flag insecure imports (pickle, eval, exec usage)\n4. Check for improper input validation\n5. Report findings with severity levels (HIGH, MEDIUM, LOW)\n6. Suggest remediation for each issue found"
  }
}
```

#### Scenario B: API Documentation Generator

```json
{
  "enabled": true,
  "name": "API Doc Generator",
  "description": "Generates OpenAPI documentation when API routes change",
  "version": "1",
  "when": {
    "type": "fileEdited",
    "patterns": ["**/routes/*.py", "**/api/*.py"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "A route file has been modified. Please:\n1. Extract all endpoint definitions (path, method, parameters)\n2. Parse docstrings for endpoint descriptions\n3. Identify request/response models\n4. Update the OpenAPI specification in docs/openapi.yaml\n5. Validate the generated schema\n6. List any endpoints missing documentation"
  }
}
```

#### Scenario C: Commit Message Helper

The `Stop` trigger (`agentStop` in this layout) fires when the agent finishes responding. It takes no `patterns` key. A fuller version of this hook ships as [`../../code-examples/hooks/commit-helper.kiro.hook`](../../code-examples/hooks/commit-helper.kiro.hook).

```json
{
  "enabled": true,
  "name": "Commit Message Helper",
  "description": "Generates a Conventional Commits message after the agent completes a task",
  "version": "1",
  "when": {
    "type": "agentStop"
  },
  "then": {
    "type": "askAgent",
    "prompt": "The task is complete. Review the files added, modified, or deleted, classify the change (feat, fix, docs, refactor, test, chore), and generate a Conventional Commits message: type(scope): description, with a short body listing the changes. Reference a ticket number if one was mentioned. Output the message in a code block."
  }
}
```

#### Scenario D: New Component Scaffolding

```json
{
  "enabled": true,
  "name": "Component Scaffolder",
  "description": "Scaffolds boilerplate when a new React component file is created",
  "version": "1",
  "when": {
    "type": "fileCreated",
    "patterns": ["components/**/*.tsx"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "A new component file was created. Please:\n1. Generate the component skeleton (typed props interface, function component, default export)\n2. Create a matching test file next to it following the project's test conventions\n3. Add the component to the nearest index.ts barrel export\n4. Follow the naming and structure rules in the steering files"
  }
}
```

### Task 3: Required Powers

| Requirement | Where it comes from | Purpose |
|-------------|---------------------|---------|
| AWS Infrastructure | AWS infrastructure Power | CloudFormation and CDK generation and validation |
| Architecture Diagrams | Mermaid diagrams in `design.md` (the AWS Diagram MCP server the book names has been retired) | Architecture visuals in the spec |
| API Testing | Postman integration in the Powers catalog | Automated API testing |
| Monitoring | An observability partner in the Powers catalog (Datadog and Dynatrace both appear there) | Application observability |

Not every capability comes as a Power. Some come from MCP servers you configure directly. This is why the lab has Phase 6 as well as Phase 5. The catalog changes. Before you pick a name, browse the catalog in the POWERS panel or on the Kiro site to see what is available to you.

If you build your own Power, use the Agent Plugins format:

- A `plugin.json` manifest (name, version, description, activation keywords)
- Optional `skills/`
- Optional `mcp.json`

The Power Builder scaffolds this layout. As of November 7, 2026, it puts steering guidance in skills, not a `dev.kiro/` directory. Section 5.5 of the chapter walks through it.

### Task 5: Quiz Answers

1. **Why should you "start simple" with hooks?**
   - Complex hooks can slow down development
   - Simple hooks are easier to debug
   - Start with file-to-file relationships before complex workflows
   - Allows you to understand hook behavior before scaling

2. **How can you prevent hooks from slowing down development?**
   - Limit trigger scope to specific patterns
   - Use manual triggers for heavy operations (in Kiro 1.0, a manual steering file you run as a slash command)
   - Keep prompts focused and concise
   - Monitor hook execution times

3. **Where are hook configuration files stored?**
   - In the `.kiro/hooks/` directory
   - Kiro IDE 0.x used `.kiro.hook` files; Kiro 1.0 and later saves `<name>.json` files there

4. **How do you temporarily disable a hook without deleting it?**
   - Set `"enabled": false` in the hook configuration

5. **What's the benefit of using GLOB patterns in hook triggers?**
   - Target specific file types or directories
   - Reduce unnecessary hook executions
   - Create focused, efficient automation
   - Support complex matching like `**/tests/**/*.py`

## Summary

Check that your hooks and powers:

- Start with simple, focused automations
- Use the right trigger type for each scenario
- Use powers for complex integrations
- Get monitored and adjusted over time
- Work together in one workflow
