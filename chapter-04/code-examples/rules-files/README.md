# Rules Files Examples

This directory holds the Kiro steering file from Chapter 4, Listing 4-4 (`steering-code-quality.md`). It is the full version, including the review checklist the book trims for space.

When to use rules files and why: Chapter 4, Section 4.2.

## Where rules files live

Each platform in Part II has its own mechanism. The names and paths differ:

| Platform | Mechanism | Location | Covered in |
|----------|-----------|----------|------------|
| Amazon Kiro | Steering files (Markdown) and agent hooks | `.kiro/steering/`, `~/.kiro/steering/`, `.kiro/hooks/` | Chapter 5 |
| Cursor | Project rules (`.mdc` files with YAML frontmatter) plus AGENTS.md | `.cursor/rules/`, `AGENTS.md` | Chapter 7 |
| GitHub Copilot | Custom instructions | `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `AGENTS.md` | Chapter 7 |
| Claude Code | CLAUDE.md, modular rule files, and lifecycle hooks | `CLAUDE.md`, `.claude/rules/*.md`; hooks are declared in `.claude/settings.json` (their scripts conventionally live in `.claude/hooks/`) | Chapter 8 |

Notes on the table:

- Only hooks and equivalent lifecycle handlers can block an action. The model can still ignore a Markdown rule.
- The steering file in this directory is a real Kiro artifact (Markdown under `.kiro/steering/`).
- Formats change between releases. Check the current documentation for the tool you use.

## Files in This Directory

| File | Description | Source |
|------|-------------|--------|
| `steering-code-quality.md` | Kiro steering file with scope, implementation, validation, and review-checklist standards | Listing 4-4, full version including the review checklist |

## Integration with CI/CD

Put the same constraint in CI. Use the linters and scanners you already trust. Do not write your own rule runner. Example:

```yaml
# GitHub Actions
- name: Lint and type-check
  run: |
    ruff check .
    ruff format --check .

- name: Scan for hardcoded secrets
  run: gitleaks git --no-banner --redact

- name: Security scan
  run: bandit -r src/ -ll
```

Some architectural rules have no off-the-shelf linter. An example is the "no business logic in views.py" rule in the AGENTS.md example. For those, write a short script that greps the disallowed imports and exits non-zero.

## Troubleshooting

### Rules Not Triggering

1. Check that the file path patterns match your files.
2. Confirm the tool is reading the file. Ask the agent to restate one of your rules. If it cannot, the file is not being loaded. The path or format is wrong for that tool's current version.

## Related Resources

- [Kiro steering documentation](https://kiro.dev/docs/steering/): the mechanism Chapter 5 uses
- [Cursor documentation](https://cursor.com/docs): project rules and AGENTS.md, covered in Chapter 7
- [Claude Code documentation](https://code.claude.com/docs): CLAUDE.md and hooks, covered in Chapter 8
- [AGENTS.md templates](../agents-md/): AGENTS.md templates for this chapter
- Chapter 5: Amazon Kiro
- Chapter 7: Cursor and GitHub Copilot
- Chapter 8: Claude Code
