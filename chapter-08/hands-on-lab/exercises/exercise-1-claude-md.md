# Exercise 1: Creating CLAUDE.md - Constitutional Governance

## Objective

Write a CLAUDE.md and modular rule files for a project, then check that Claude follows them.

## Duration

30-45 minutes

## Background

CLAUDE.md holds the rules, constraints, and conventions that Claude Code follows in your project. It usually covers:

- Project context and architecture
- Code standards and conventions
- Business rules and constraints
- Security requirements
- Testing standards

## Part 1: Understanding the Hierarchy

Section 8.3 (Table 8.3) covers the five-level memory hierarchy and auto memory. This exercise uses two of the levels:

- The project file `./CLAUDE.md`
- The modular rules in `./.claude/rules/`

While you work, run `/memory` in a session. It shows which CLAUDE.md files are loaded and what auto memory holds. Auto memory can include notes you did not write.

## Part 2: Anatomy of CLAUDE.md

A complete CLAUDE.md usually has these sections:

```markdown
# Project: [Name]

## Overview
[Project description, business context, key metrics]

## Architecture Principles
[Fundamental design decisions]

## Code Standards
[Language, frameworks, style requirements]

## Security Requirements
[Non-negotiable security rules]

## Testing Standards
[Coverage requirements, testing patterns]

## Prohibited Actions
[Explicit list of what NOT to do]
```

## Part 3: Hands-On Exercise

### Task 1: Analyze an Existing CLAUDE.md

Read the SupportFlow CLAUDE.md and identify:

1. What business rules are encoded?
2. What technical standards are required?
3. What actions are prohibited?

```bash
cat ../supportflow/CLAUDE.md
```

**Questions to answer:**
- How does the CLAUDE.md enforce human review of AI-generated content?
- What architecture pattern does the project use?
- How are security requirements specified?

### Task 2: Create a CLAUDE.md for a New Project

Create a CLAUDE.md for a sample project, **FinanceTracker**, a personal finance application.

Requirements:
- Node.js with TypeScript (strict mode)
- React frontend with Next.js
- PostgreSQL database
- Must comply with financial data regulations
- All transactions must be logged
- No storing of credit card numbers
- Minimum 85% test coverage

Create your CLAUDE.md:

```bash
mkdir finance-tracker && cd finance-tracker
```

Include these sections:

1. **Overview**: Project description and compliance requirements
2. **Architecture**: Frontend/backend separation, API design
3. **Code Standards**: TypeScript strict mode, React patterns
4. **Security**: PII handling, encryption requirements
5. **Testing**: Coverage targets, required test types
6. **Prohibited Actions**: What Claude should never do

### Task 3: Add Modular Rules

Create topic rules in the `.claude/rules/` directory:

```text
.claude/
└── rules/
    ├── security.md
    ├── api-design.md
    └── database.md
```

Example `security.md` with path scoping:

```markdown
---
paths:
  - "src/services/auth/**"
  - "src/api/auth/**"
---

# Authentication Security Rules

- All authentication endpoints must use HTTPS
- Passwords must be hashed with bcrypt (cost factor 12+)
- Session tokens must expire after 24 hours
- Failed login attempts must be rate-limited (5 per minute)
- MFA must be supported for sensitive operations
```

Create three rule files for your FinanceTracker project.

## Part 4: Testing Your CLAUDE.md

1. Start Claude Code in your project directory.
2. Ask Claude to explain the project rules.
3. Ask Claude to generate code that breaks a rule.
4. Check that Claude follows the constraints.

Example test prompts:

```text
> Explain the project's security requirements

> Create a function to store credit card numbers in the database
# Should refuse or warn about the rule violation

> Generate a React component without TypeScript
# Should follow the TypeScript strict mode requirement
```

## Part 5: Review Checklist

What makes a CLAUDE.md work, and why: Chapter 8, Section 8.3. Before you finish, check your file against this list.

### Do:
- Be specific and actionable
- Include examples where helpful
- Explain the "why" behind rules
- Keep it version-controlled
- Update when conventions change

### Don't:
- Write vague guidelines ("write good code")
- Include implementation details that change frequently
- Make it so long Claude can't process it effectively
- Forget to share with new team members

## Deliverables

1. A CLAUDE.md for FinanceTracker (20+ lines)
2. Three modular rule files in `.claude/rules/`
3. Answers to the analysis questions from Task 1
4. Screenshots or logs showing Claude following your rules

## Self-Assessment

- [ ] Does your CLAUDE.md cover all major sections?
- [ ] Are security requirements explicit and actionable?
- [ ] Did you include prohibited actions?
- [ ] Are your modular rules properly scoped?
- [ ] Does Claude follow the rules when you test it?

## Solution Reference

Compare your solution with the templates in [`../../code-examples/claude-md/`](../../code-examples/claude-md/).

## Next Steps

Continue to [Exercise 2: Implementing Hooks](exercise-2-hooks.md). It enforces your rules with scripts.
