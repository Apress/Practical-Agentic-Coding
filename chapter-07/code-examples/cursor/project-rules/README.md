# Cursor project rule templates (`.cursor/rules/*.mdc`)

Four starting-point rule sets you can copy into a project:

- one generic template
- two language-specific templates
- one template for regulated or large-scale work

## The format

These files use Cursor's **Project Rules** format. They are `.mdc` files that live in `.cursor/rules/` inside your repository. Each rule is markdown with a YAML frontmatter header. The header controls when Cursor injects the rule. The rules system skips plain `.md` files placed there.

The rule hierarchy (project, team, and user rules, and `AGENTS.md`): Chapter 7, Section 7.2.

The frontmatter fields:

- **`description`**: the agent reads this to decide whether to pull the rule into context.
- **`globs`**: the rule activates only for files matching the pattern (e.g., `**/*.py`).
- **`alwaysApply`**: when `true`, Cursor loads the rule into every prompt and ignores `globs` and `description`. That spends context tokens on every request. Keep it rare.

Cursor's current documentation calls the older single-file `.cursorrules` format legacy and slated for deprecation. If you have one, move its content into `.cursor/rules/*.mdc` files or `AGENTS.md`. Use the four migration steps in [`cursorrules-guide.md`](../../../tutorials/cursorrules-guide.md#migrating-from-cursorrules).

## The four templates

| File | Frontmatter | Use it for |
|------|-------------|------------|
| `basic.mdc` | `alwaysApply: true` | Any project, any language. Code standards, communication style, and a short best-practices list. The one to start from if you have not written rules before. |
| `python.mdc` | `globs: "**/*.py"` | Python work. Type hints, naming, async patterns, error handling, pytest conventions, plus framework sections for FastAPI, Django, and data science. |
| `typescript.mdc` | `globs: "**/*.ts,**/*.tsx"` | TypeScript work. Strict mode, explicit return types, naming, error handling, testing, plus React and Node sections. |
| `enterprise.mdc` | `alwaysApply: true` | Regulated or large-scale projects. Complexity and length limits, a never-do/always-do security list, GDPR, SOC 2, and HIPAA patterns, microservice and database architecture, testing and documentation requirements, change management, and observability. |

Pick one language template. Add `enterprise.mdc` on top if you need the compliance content. The two are written to combine. The language file covers how code should look. The enterprise file covers what the organization requires.

The language templates use `globs`, so they load only when a matching file is in play. The other two use `alwaysApply`.

## Using a template as-is

```bash
mkdir -p /path/to/your-project/.cursor/rules
cp python.mdc /path/to/your-project/.cursor/rules/
```

Then edit it. The agent follows whatever the rule file says, even if it describes someone else's project. Also edit the frontmatter:

1. Tighten the `globs` to your source layout.
2. Rewrite the `description` so the agent can tell when the rule applies.

## Splitting a template

For anything longer than the basic template, split it into several files. Cursor loads a rule only when its `globs` match or its `description` fits the task. Smaller files keep the prompt smaller:

```text
.cursor/rules/
├── python-style.mdc      # from python.mdc: standards, naming, patterns
├── testing.mdc           # from python.mdc: pytest conventions
└── security.mdc          # from enterprise.mdc: never-do/always-do lists
```

For the `.mdc` format, glob targeting, and `alwaysApply`, see `tutorials/cursorrules-guide.md` in this chapter.

## Related

- [`../composer-prompts/README.md`](../composer-prompts/README.md): prompt examples for agent runs
- [`../mcp-configs/README.md`](../mcp-configs/README.md): MCP server configurations for Cursor
- [`../../../tutorials/cursorrules-guide.md`](../../../tutorials/cursorrules-guide.md): the project-rules quick reference
- [`../../../hands-on-lab/linkforge/.cursor/rules/linkforge.mdc`](../../../hands-on-lab/linkforge/.cursor/rules/linkforge.mdc): the lab's own rule file, for comparison
- [`../../skills/README.md`](../../skills/README.md): Agent Skills, the on-demand complement to standing rules
