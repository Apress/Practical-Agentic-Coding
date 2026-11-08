# Cursor Setup: Quick Reference

Install and configure Cursor. For the latest steps, see Cursor's own guide at [cursor.com/docs](https://cursor.com/docs).

What Tab, the Agents Window, indexing, rules, and MCP are for, and when to use each: Chapter 7, Section 7.2.

> **Current tool behavior (as of November 7, 2026).** These differ from the printed book:
>
> - **No `@Codebase`, `@Docs`, or `@Web` symbols.** For codebase-wide or web questions, just ask. The agent searches the codebase and the web with its own tools.
> - **Context mentions that exist.** @-mention the files and folders that matter (`@src/auth.ts`, `@src/routes/`). Use `@Commit` or `@Branch` to bring in git diffs, and `@Chats` for an earlier conversation.
> - **No separate Inline Edit.** Cmd+K (Ctrl+K) sends the selection to the agent. See the shortcuts table below.

## Installation

### Download Cursor

1. Visit [cursor.com](https://cursor.com).
2. Download the installer for your platform:
   - **macOS**: `.dmg` file
   - **Windows**: `.exe` installer
   - **Linux**: `.deb` (apt), `.rpm` (dnf), or AppImage. Cursor recommends the apt or dnf package over AppImage.

### System Requirements

- **macOS**: 12 (Monterey) or later, Apple Silicon or Intel
- **Windows**: Windows 10 or later
- **Linux**: Debian/Ubuntu or RHEL/Fedora packages, or the portable AppImage

These come from Cursor's quickstart page. It does not document hardware minimums.

## Initial Setup

### First Launch

1. Open Cursor.
2. Sign in with one of these:
   - GitHub account (recommended)
   - Google account
   - Email

### Import VS Code Settings

If migrating from VS Code:

1. Open Cursor Settings (Cmd+Shift+J / Ctrl+Shift+J).
2. Go to **General > Account**.
3. Under **VS Code Import**, click **Import**. This brings over extensions, themes, settings, and keybindings.

Cursor installs extensions from the Open VSX registry. It does not use the VS Code Marketplace, so a few Marketplace-only extensions may be missing.

### Choose AI Model

1. Open the model picker at the top of the chat or agent panel. You can also press Cmd+/ (Ctrl+/ on Windows/Linux) to cycle through models.
2. Pick a model. Your choice carries over to new chats until you change it.
3. If you are unsure, pick **Auto** if your plan offers it. As of November 7, 2026, Plus does not. Otherwise pick Composer, one of Cursor's own models.

The model list depends on your plan and changes often. To add your own API keys, go to **Cursor Settings > Models**.

### Find the main features

- **Tab**: turn it on or off from the **Tab** indicator in the status bar, or under **Cursor Settings > Tab**.
- **Agents Window**: open it from the Command Palette with **Open Agents Window**.
- **Background validation** of AI edits is automatic. You do not need to set it up.

## Configure Rules

### Create Project Rules

1. Create `AGENTS.md` in your project root. Cursor detects it automatically. It needs no metadata.

```markdown
You are an expert [language] developer.

## Code Standards
- [Your coding standards]

## Architecture
- [Your patterns]

## Naming
- [Your conventions]
```

2. Create folder-specific rules in `.cursor/rules/`, for example `api.mdc`. The frontmatter must be the first thing in the file.

```markdown
---
description: "API route conventions"
globs: "src/routes/**/*.ts"
---

# API Standards
- RESTful naming
- Proper error handling
```

## Configure MCP (Model Context Protocol)

### Enable MCP Servers

1. Create the config file. Use `~/.cursor/mcp.json` for all projects, or `.cursor/mcp.json` in a project for that project only.

```json
{
  "mcpServers": {
    "github": {
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${env:GITHUB_PAT}"
      }
    }
  }
}
```

Notes on this file:

- This is GitHub's official hosted MCP server. The archived `@modelcontextprotocol/server-github` package is deprecated.
- `${env:GITHUB_PAT}` is Cursor's syntax for reading an environment variable. The token stays out of the file.
- Remote servers use `url`. Stdio servers use `command`, `args`, and `env`.

2. Restart Cursor.
3. Check that the server's toggle is on under **Customize > MCPs**.
4. If it fails to connect, open the Output panel (Cmd+Shift+U / Ctrl+Shift+U) and select **MCP Logs**.

## Keyboard Shortcuts

> Cursor's shortcuts and panel layouts change between releases. Check [cursor.com/docs](https://cursor.com/docs) for the current bindings.

### Essential Shortcuts

| Action | macOS | Windows/Linux |
|--------|-------|---------------|
| Tab Completion | Tab | Tab |
| Send the selection to the agent (replaces Inline Edit) | Cmd+K | Ctrl+K |
| Agent chat | Cmd+I | Ctrl+I |
| Add selection to the current chat | Cmd+L | Ctrl+L |
| Start a new agent with the selection | Cmd+Shift+L | Ctrl+Shift+L |
| Command Palette | Cmd+Shift+P | Ctrl+Shift+P |

Cursor's keyboard-shortcuts reference page lists the Cmd+I and Cmd+L pair the other way around. The bindings here are the ones Cursor 3.25 ships.

### Customize Shortcuts

1. Open Keyboard Shortcuts. Press Cmd+R then Cmd+S (Ctrl+R then Ctrl+S on Windows/Linux).
2. Search for "cursor".
3. Change the bindings you need.

## Team Setup (Teams and Enterprise)

### Admin Configuration

1. Go to [cursor.com/dashboard](https://cursor.com/dashboard).
2. Click **Create Team**. From an existing account, click **Upgrade to Teams**.
3. Invite team members.
4. Configure team rules in the dashboard. A team rule is free-form text with no frontmatter. For example:

```text
Security requirements:
- No API keys in code
- Use parameterized queries
```

Tick **Enforce this rule** to stop team members from switching it off.

### Sync Rules Across Team

1. Check project rules (`.cursor/rules/`, `AGENTS.md`) into version control. Every clone then gets them.
2. Keep organization-wide standards in team rules. Team rules apply to every member's projects.
3. Individual developers cannot disable team rules marked **Enforce this rule**.

## Privacy Settings

### Configure Data Privacy

1. Open Cursor Settings (Cmd+Shift+J / Ctrl+Shift+J).
2. Go to **General**.
3. Turn on **Privacy Mode** if your policy requires it.

Cursor's security page ([cursor.com/security](https://cursor.com/security)) describes how code and requests are handled under each setting. Some models carry their own data policies.

### Exclude Files

Create `.cursorignore`. Cursor blocks the listed files from the agent, Tab, and @-mentions. This is on top of what `.gitignore` already excludes.

Terminal commands and MCP tools run outside those controls. They can still read ignored files. Keep real secrets out of the workspace as well.

```text
# Ignore sensitive files
.env
secrets/
*.pem
*.key

# Ignore generated files
node_modules/
dist/
build/
```

## Troubleshooting

### Common Issues

**Slow Indexing**
- Add large folders to `.cursorignore`.
- Reduce the project size if you can.
- Wait for the initial index to complete.

**Tab Not Working**
- Check that Tab is enabled in settings.
- Check that the model is responding.
- Check your subscription status.

**Agent Errors**
- Check that your API key is valid.
- Check network connectivity.
- Read the error messages in the output.

### Reset Cursor

If nothing else works:

1. Close Cursor.
2. Back up `~/.cursor/mcp.json` and anything else you added under `~/.cursor` (user rules, skills, hooks).
3. Delete the `~/.cursor` folder.
4. Reinstall from a fresh download.

## Resources

- [Official Documentation](https://cursor.com/docs)
- [Cursor Forum](https://forum.cursor.com) (the community channel Cursor's docs point to)
- [Changelog](https://cursor.com/changelog)
