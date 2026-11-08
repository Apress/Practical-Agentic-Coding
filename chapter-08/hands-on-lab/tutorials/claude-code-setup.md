# Claude Code setup: quick reference

Use this file to install Claude Code, sign in, and set up a project for the Chapter 8 lab. For the latest install options, see the vendor's guide at [code.claude.com/docs](https://code.claude.com/docs).

What the setup choices mean, and when to use each permission mode: Chapter 8, Section 8.3.

> **Updates to the book (as of November 7, 2026)**
>
> - **Default permission mode.** With no `defaultMode` set, an interactive session starts in `auto` (Claude Code 2.1.283 and later). To be asked before each edit and command, use the [user configuration](#user-configuration) below. The CLI shows `default` as Manual.
> - **npm 12.** npm 12 skips the install step that puts the `claude` binary in place. `claude` then prints `Error: claude native binary not installed.` If `npm --version` starts with 12, use the native installer. Or follow "Fix an npm 12 install" in the Claude Code installation troubleshooting docs.
> - **VS Code chat panel.** The chat panel does not read a project's `.claude/settings.json` or `.claude/settings.local.json` for its starting permission mode. So SupportFlow's `"defaultMode": "default"` does not apply there. The project's permission rules and hooks still load. A `claude` session in the integrated terminal reads the mode as usual. See [VS Code extension](#vs-code-extension) for the fix.

## Prerequisites

You need:

- **Operating System**: macOS, Linux, WSL, or Windows
- **Node.js**: only for the npm install option, version 22 or later
- **Terminal**: bash, zsh, PowerShell, or a compatible shell
- **Account**: Claude.ai Pro/Max/Teams/Enterprise OR Anthropic API key

## Installation

### Option 1: Native installer (recommended)

```bash
# macOS / Linux / WSL
curl -fsSL https://claude.ai/install.sh | bash

# Verify installation
claude --version
```

On Windows, in PowerShell:

```powershell
irm https://claude.ai/install.ps1 | iex
```

Native installations update themselves in the background. You can also install with Homebrew (`brew install --cask claude-code`) or winget (`winget install Anthropic.ClaudeCode`).

### Option 2: npm

```bash
# Requires Node.js 22 or later; do not use sudo
npm install -g @anthropic-ai/claude-code

# Verify installation
claude --version
```

If `npm --version` starts with 12, read the npm 12 note at the top of this file.

The install methods change between releases. Check code.claude.com/docs for the current options for your platform.

## Authentication

### Using Claude.ai Account

1. Run Claude Code:
   ```bash
   claude
   ```

2. Follow the sign-in prompt in your browser.

3. Allow Claude Code to access your account.

### Using API Key

1. Get an API key from [console.anthropic.com](https://console.anthropic.com/).

2. Set the environment variable:
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   ```

3. Add it to your shell profile so it persists:
   ```bash
   # For bash
   echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.bashrc

   # For zsh
   echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.zshrc
   ```

## First Run

### Start Claude Code

```bash
# Navigate to your project
cd my-project

# Start Claude Code
claude
```

### Initialize Your Project

```text
> /init
```

Claude reads your project and creates a starter CLAUDE.md. It contains:

- The detected language and framework
- The project structure
- Suggested conventions

### Basic Commands

| Command | Description |
|---------|-------------|
| `/init` | Initialize CLAUDE.md for project |
| `/help` | Show available commands |
| `/usage` | Show token usage and limits (`/cost` also works) |
| `/compact` | Compress conversation |
| `/resume` | Continue previous session |
| `/rewind` | Roll back to a checkpoint |
| `/effort` | Set reasoning depth |
| `/model` | Switch models |

## Configuration

### Project Configuration

Create `.claude/settings.json` in your project:

```json
{
  "permissions": {
    "allow": [
      "Bash(npm test)",
      "Bash(npm run build)",
      "Edit(src/**)",
      "Edit(tests/**)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Edit(.env*)"
    ]
  }
}
```

Write file rules as `Edit(...)`, as above. Claude Code checks file paths against `Edit(...)` and `Read(...)` rules only. It accepts a `Write(path)` rule but never checks it.

### User Configuration

Create `~/.claude/settings.json` for global preferences:

```json
{
  "model": "sonnet",
  "theme": "dark",
  "permissions": {
    "defaultMode": "default"
  }
}
```

Put `defaultMode` inside `permissions`. This configuration starts each session in `default`. The CLI shows this mode as Manual. The value `manual` also works. Without it, sessions start in `auto` (see the note at the top).

### Permission Modes

What each mode does and when to use it: Chapter 8, Section 8.3 (Table 8.6).

The values are:

- `default`
- `acceptEdits`
- `plan`
- `auto`
- `dontAsk`
- `bypassPermissions`

Deny rules apply in every mode. A project's `.claude/settings.json` or `.claude/settings.local.json` cannot set `auto` or `bypassPermissions` as `defaultMode`. It has no effect there. Start those modes with the command-line flag instead.

Set the permission mode:

```bash
# Start with a specific mode
claude --permission-mode acceptEdits

# Or set "defaultMode" in settings.json, or press Shift+Tab in a session
```

## IDE Integration

### VS Code Extension

1. Install the "Claude Code" extension from the marketplace.
2. The extension bundles its own copy of the CLI for its chat panel. To run `claude` in VS Code's integrated terminal, install the standalone CLI as well.
3. The extension gives you inline diffs, @-mentions, and a chat panel.

To start chat-panel conversations in Manual mode, set `claudeCode.initialPermissionMode` to `default` in your VS Code user settings (see the VS Code note at the top of this file). Without this setting, the panel picks its starting mode in this order:

1. The mode you last picked from the mode indicator at the bottom of the prompt box
2. `defaultMode` from `~/.claude/settings.json` or managed settings
3. The built-in default, auto mode

### JetBrains Plugin

1. Install the plugin from JetBrains Marketplace. The plugin does not bundle the CLI, so install Claude Code itself too.
2. Configure it in **Settings > Tools > Claude Code [Beta]**.
3. Open it from the tool window or with the keyboard shortcut.

## Troubleshooting

### Common Issues

**"Command not found"**
```bash
# Check npm global path
npm config get prefix

# Add to PATH if needed
export PATH="$PATH:$(npm config get prefix)/bin"
```

**"Authentication failed"**
```bash
# Check what account you are signed in as
claude auth status

# Sign out, then sign back in
claude auth logout
claude auth login
```

**"Permission denied"**
```bash
# Check API key is set
echo $ANTHROPIC_API_KEY

# Verify account status
claude auth status
```

### Diagnostic Command

Run diagnostics:

```bash
claude doctor
```

`claude doctor` prints read-only installation and settings diagnostics. It does not start a session.

Inside a session, `/doctor` runs a fuller checkup. It checks installation, settings, extensions, and CLAUDE.md problems. It proposes fixes and applies them once you confirm.

## Next Steps

1. **Create CLAUDE.md**: See [CLAUDE.md Guide](claude-md-guide.md)
2. **Add Hooks**: See [Hooks Reference](hooks-reference.md)
3. **Configure MCP**: See [MCP Integration](mcp-integration.md)
4. **Start the Lab**: See [Hands-On Lab](../README.md)

## Additional Resources

- [Claude Code Documentation](https://code.claude.com/docs)
- [API Reference](https://platform.claude.com/docs/en/api/overview)
- [Claude Support](https://support.claude.com/)
- [GitHub Issues](https://github.com/anthropics/claude-code/issues)
