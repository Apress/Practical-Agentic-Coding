# AGENTS.md: quick reference

**Time Required**: 20-30 minutes
**Difficulty**: Beginner
**Prerequisites**: Basic Markdown knowledge, familiarity with development workflows

When to use AGENTS.md and why: Chapter 4, Section 4.2 and Section 4.5.

For the latest format details, see [agents.md](https://agents.md/).

## What you build

An `AGENTS.md` file at your project root.

## Step 1: Create the file

1. Create `AGENTS.md` at your project root.
2. Paste this skeleton:

```markdown
# AGENTS.md

## Persona
[Who the agent should be]

## Tech Stack
[Technologies used in the project]

## Project Rules
[Non-negotiable constraints]

## Workflow
[Step-by-step process for tasks]

## Commands
[Specific commands to run]

## Restricted Areas
[Files and directories to avoid]
```

## Step 2: Fill in each section

| Section | What to write |
|---------|---------------|
| Persona | A specific role, for example "senior Python backend engineer" |
| Tech Stack | Every framework and tool the project uses, with settings such as line length |
| Project Rules | Constraints the agent must follow |
| Workflow | Numbered steps for a task, from reading the ticket to the commit message |
| Commands | The exact commands for dev server, tests, formatting, linting, type checks, and migrations |
| Restricted Areas | Paths the agent must not modify, with the reason for each |
| Security & Safety | Rules for secrets, unsafe code, access control, and dependencies |

### Example lines

```markdown
## Tech Stack

- **Backend**: FastAPI
- **Database**: PostgreSQL via SQLAlchemy ORM
- **Formatting**: Black (line length: 88)
- **Testing**: pytest with pytest-asyncio

## Commands

- Run all tests: `pytest`
- Run with coverage: `pytest --cov=app`
- Lint: `make lint` or `ruff check .`
- Type check: `make typecheck` or `mypy app/`

## Restricted Areas

- `/infrastructure/security/` - Security configurations
- `/legacy/auth/` - Legacy authentication code (frozen for compliance)
- `*.env*` - Environment files (never read or modify)
- `/migrations/` - Database migrations require human review
```

## Step 3: Compare with the complete examples

- [`AGENTS.md`](../code-examples/agents-md/AGENTS.md): a backend service (Listing 4-6).
- [`AGENTS_enterprise.md`](../code-examples/agents-md/AGENTS_enterprise.md): the Nexus Inventory System (Listing 4-3, extended).

## Step 4: Check that the agent reads it

1. Start a session in your tool.
2. Ask the agent to restate one of your rules.
3. If it cannot, the file is not being loaded. Check the file name, the location, and your tool's documentation.

Which tools read AGENTS.md, and how Claude Code treats it next to CLAUDE.md: see [How Agents Use AGENTS.md](../code-examples/agents-md/README.md#how-agents-use-agentsmd).

## Verification checklist

Before moving on, verify your AGENTS.md:

- [ ] Has a clear Persona section
- [ ] Lists the complete Tech Stack
- [ ] Defines specific Project Rules
- [ ] Includes a step-by-step Workflow
- [ ] Documents available Commands
- [ ] Specifies Restricted Areas
- [ ] Addresses Security considerations
- [ ] Is placed at the project root

## Next steps

1. **Exercise 3**: [Write a Complete AGENTS.md](../exercises/exercise-3-agents-md.md)
2. **Tutorial**: [Governance with AGILITY Framework](./governance-guide.md)
3. **Kiro**: Chapter 5 covers Amazon Kiro steering files, which read AGENTS.md too.

## Reference

- [The AGENTS.md convention](https://agents.md/)
- [Code Example: AGENTS.md](../code-examples/agents-md/AGENTS.md)
- [Code Example: AGENTS_enterprise.md](../code-examples/agents-md/AGENTS_enterprise.md)
