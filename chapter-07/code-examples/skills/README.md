# Agent Skills for Cursor and Copilot

This folder holds one small skill, `add-endpoint/SKILL.md`. It shows the Agent Skills format that both tools in this chapter load. Chapter 4, Section 4.2 introduces the format. Chapter 7, Section 7.2 explains how skills relate to rules.

A skill is a folder that holds a `SKILL.md` file. The file has YAML frontmatter (`name`, `description`) and markdown instructions. The agent reads the `description` to decide when to load the skill. Write it as a trigger condition.

## Where to place it

The same folder works in both tools. Only the path differs:

```text
# Cursor
.cursor/skills/add-endpoint/SKILL.md

# GitHub Copilot
.github/skills/add-endpoint/SKILL.md

# Either tool (shared, cross-tool path)
.agents/skills/add-endpoint/SKILL.md
```

- **Cursor** reads `.cursor/skills/` and `.agents/skills/`. It also reads Claude and Codex skill folders for cross-tool compatibility.
- **Copilot** reads `.github/skills/`, `.claude/skills/`, and `.agents/skills/`. This holds in VS Code, in its CLI, and as the cloud agent.

These paths change between releases. Confirm them against each tool's docs.

To try it:

```bash
mkdir -p /path/to/your-project/.agents/skills
cp -r add-endpoint /path/to/your-project/.agents/skills/
```

Then ask the agent to "add an endpoint to list a user's links". Check that it follows the procedure in the skill.

## Related

- [`../cursor/project-rules/README.md`](../cursor/project-rules/README.md): the standing standards that this skill's procedure assumes
- Chapter 6 and Chapter 8 labs carry fuller skills (`.agents/skills/money-audit/`, `.claude/skills/review-drafts/`) if you want larger examples
