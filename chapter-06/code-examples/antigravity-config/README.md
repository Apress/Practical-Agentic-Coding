# Antigravity Configuration Examples

These are configuration templates for a Google Antigravity workspace. They match Chapter 6, Sections 6.2 and 6.3.

The files record the decisions Chapter 6 asks you to make:

- Which model tier to use per task
- What the agent may do without asking
- What the context engine indexes
- How Secure Mode is set

To change behavior, use Antigravity's own settings UI. Key names change between releases. Check [antigravity.google/docs](https://antigravity.google/docs) before you rely on a specific key.

## Files

| File | Purpose |
|------|---------|
| `settings.json` | Everyday workspace settings: models, auto-approval, indexing, artifacts, browser subagent |
| `secure-mode.json` | The strict variant for sensitive or client work: URL governance, forced review, audit logging |
| `rules-template.md` | Starting point for `.agents/rules/project-rules.md`, the governance constraints |

## Applying Them

```bash
# From your project root; REPO is where you cloned this repository
REPO=~/Practical-Agentic-Coding
mkdir -p .antigravity .agents/rules
cp "$REPO/chapter-06/code-examples/antigravity-config/settings.json" .antigravity/settings.json
cp "$REPO/chapter-06/code-examples/antigravity-config/rules-template.md" .agents/rules/project-rules.md
```

On Windows (PowerShell):

```powershell
$REPO = "$HOME\Practical-Agentic-Coding"
New-Item -ItemType Directory -Force .antigravity, .agents\rules
Copy-Item "$REPO\chapter-06\code-examples\antigravity-config\settings.json" .antigravity\settings.json
Copy-Item "$REPO\chapter-06\code-examples\antigravity-config\rules-template.md" .agents\rules\project-rules.md
```

For sensitive work, merge `secure-mode.json` into your settings, or set the equivalents in Antigravity Settings under Strict mode.

Both JSON files use `"//"`-prefixed keys as comments, because JSON has no comment syntax. Each key is unique, so the files stay valid JSON. If you add your own notes, keep the keys distinct too.

Replace every placeholder host and address (`*.internal.example.com`, `security@example.com`, `SLACK_SECURITY_WEBHOOK_URL`) with your own. Until you do, the Secure Mode config has no effect.

## Where Rules Live

- Workspace rules go in `.agents/rules/`. They travel with the repository, so your teammates and their agents get the same constraints.
- `AGENTS.md` at the project root is the cross-tool context file. Any agent that follows that convention can read it.
- The MoneyMind lab ships both. See `../../hands-on-lab/moneymind/` for a filled-in example of each.

## Related

- [Antigravity setup tutorial](../../tutorials/antigravity-setup.md)
- [MoneyMind lab](../../hands-on-lab/moneymind/) for these files in use
