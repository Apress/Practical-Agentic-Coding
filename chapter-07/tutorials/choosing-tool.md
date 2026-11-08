# Choosing Between Cursor and GitHub Copilot: Quick Reference

This file covers the practical steps for moving between the two tools or running both.

When to use each tool and why: Chapter 7, Section 7.4 (with Table 7.1). The hybrid "Architect-Auditor" workflow: Chapter 7, Section 7.5. The Section 7.6 lab runs that workflow end to end.

> **Current tool behavior (as of November 7, 2026).** These differ from the printed book:
>
> - Current VS Code has no Copilot Edit Mode. Use Agent Mode with a small set of attached files, and review each edit before you keep it.
> - Current Cursor has no `@Codebase` symbol. The agent searches the codebase with its own tools. Per Cursor's documentation, the search index is built and queried on your machine.
> - In Cursor, @-mention files and folders for precise context. Use `@Commit` and `@Branch` for git diffs.
> - The book's "Copilot Async Agent" is the Copilot cloud agent. Dispatch it by picking Copilot from an issue's assignees list.

## Pricing

Both vendors change pricing often. Check the current pages:

- **Cursor**: per-seat subscription with usage-based model allowances. See [cursor.com/pricing](https://cursor.com/pricing).
- **Copilot**: per-seat or per-user plans with an allowance of usage-based GitHub AI Credits. Heavier models consume credits faster. Some features require Business or Enterprise plans. See [docs.github.com/copilot](https://docs.github.com/copilot).

Time saved varies widely by team and task mix. Measure your own baseline before and after adoption.

## Migration paths

### From Copilot to Cursor

1. Export VS Code settings.
2. Install Cursor.
3. Import settings.
4. Create `.cursor/rules` (or reuse `AGENTS.md`) from `copilot-instructions.md`.
5. Keep Copilot for PR work.

### From Cursor to Copilot

1. Export Cursor settings.
2. Create `copilot-instructions.md` from your `.cursor/rules`. You can also run `/init` in VS Code chat to generate it.
3. Install Copilot in your preferred IDE.
4. Set up team governance.

Tip: both tools read `AGENTS.md` in the project root. Keep shared standards there.

### Running both

1. Use Cursor for development.
2. Push to GitHub.
3. Let Copilot handle PR review and CI/CD.
4. Keep both instruction files in sync.

## Related files

- [`cursor-setup.md`](cursor-setup.md) and [`copilot-setup.md`](copilot-setup.md): install and configure each tool.
- [`../code-examples/comparison/side-by-side.md`](../code-examples/comparison/side-by-side.md): the same tasks done in both tools.
