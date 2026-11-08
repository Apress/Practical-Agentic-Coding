# Code Quality and Validation Standards

## Scope

Apply these standards when creating or modifying application code,
tests, configuration, and documentation in this repository.

## Implementation Rules

- Prefer small, cohesive changes that preserve existing public behavior
  unless the task explicitly requires a breaking change.
- Follow the repository's established language, framework, formatting,
  naming, and directory conventions.
- Do not introduce a new dependency when an existing project dependency
  or standard-library capability satisfies the requirement.
- Keep secrets, credentials, private keys, and production data out of
  source code, tests, logs, examples, and documentation.

## Validation Rules

- Run the relevant formatter, linter, type checker, and test suite after
  code changes whenever the repository provides them.
- Add or update tests for changed behavior, including error paths and
  boundary conditions where appropriate.
- Do not claim that a check passed unless it was actually executed.
- If validation cannot run, state the command, the reason it could not
  run, and the expected verification procedure.

## Review Checklist

Before completing a task, verify that:

1. The change satisfies the stated acceptance criteria.
2. Tests cover the modified behavior.
3. Documentation and examples match the implemented behavior.
4. Error messages are actionable and do not expose sensitive data.
5. The diff contains no unrelated refactoring or generated-file noise.
