# Spec-Driven Development (SDD) in Kiro: quick reference

This page lists what you click, type, and check in each phase of a Kiro spec. It does not teach the method.

What SDD is, and when and why to use it: Chapter 5, Section 5.2.

## Where spec files live

Each spec is a folder under `.kiro/specs/` with `requirements.md`, `design.md`, and `tasks.md`. The [SDD phases table](#sdd-phases) lists what each file holds. Templates for all three: [`../code-examples/specs/`](../code-examples/specs/).

## Phase 1: Requirements

1. Create a spec: click the (+) in the SPECS section of the Kiro (ghost) panel.
2. Write each user story in this format: "As a [user], I want [goal], so that [benefit]".
3. Write acceptance criteria in EARS syntax (see [EARS syntax patterns](#ears-syntax-patterns)).
4. Review the requirements with Kiro and approve them.

Minimal example:

```markdown
### Requirement 1

**User Story:** As a tech-savvy reader, I want to access curated technology
news with witty commentary, so that I can stay informed while being
entertained by sharp insights.

#### Acceptance Criteria

1. WHEN a user visits the application THEN the system SHALL display
   a feed of curated technology stories
2. WHEN stories are displayed THEN each story SHALL include a witty
   summary maintaining a sharp, cynical tone
```

## Phase 2: Design

1. After you approve the requirements, select "Move to Design Phase".
2. Give Kiro your technical constraints, one per line:

```text
Constraint: The application must be written in Python 3.13 with Flask
Constraint: Use Amazon Bedrock APIs with Claude models for summarization
Constraint: Deploy on AWS App Runner with VPC connectivity
Design: Use repository pattern for data access separation
```

3. Review the generated `design.md`.
4. Ask questions and iterate until the design is right.

Architecture diagrams come from Mermaid in `design.md`.

## Phase 3: Tasks

1. After you approve the design, select "Move to Implementation Plan".
2. Review the generated tasks.
3. Add groupings and priorities:

```text
Instruction: Group tasks into MVPs - start with local development and
testing, then AWS infrastructure deployment
Instruction: Include property-based tests for all core business logic
```

## Phase 4: Implementation

1. Open `tasks.md`.
2. Click "Start Task" on the first task.
3. Review the code changes before you accept them.
4. Check that the tests pass.
5. Commit the working increment.
6. Repeat for the remaining tasks.

## Related Kiro features

- **Steering files** (`product.md`, `tech.md`, `structure.md`) feed every phase. See the [steering files guide](./steering-files-guide.md).
- **Hooks** run routine checks during implementation, such as keeping tests in step with source. See [`../code-examples/hooks/`](../code-examples/hooks/).
- **Powers** add capability during design and implementation. Lab Phase 5 uses the AWS infrastructure Power to validate CloudFormation.

## Next Steps

1. Practice with [Exercise 1: SDD Basics](../hands-on-lab/exercises/exercise-1-sdd-basics.md).
2. Read the [Steering Files](./steering-files-guide.md) guide.
3. Start the [Daily Briefing Lab](../hands-on-lab/README.md).

## Quick Reference

### EARS Syntax Patterns

| Pattern | Format |
|---------|--------|
| When/Then | WHEN [trigger] THEN system SHALL [action] |
| Where | WHERE [condition] THEN system SHALL [action] |
| If/Then | IF [condition] THEN system SHALL [action] |

### SDD Phases

| Phase | Primary Output | Key Activities |
|-------|---------------|----------------|
| Requirements | requirements.md | User stories, acceptance criteria |
| Design | design.md | Architecture, data models, interfaces |
| Tasks | tasks.md | Implementation breakdown, prioritization |
| Implementation | Code | Task execution, testing, review |
