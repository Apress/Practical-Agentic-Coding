# MCP Configuration Examples

This directory holds the Model Context Protocol (MCP) configuration examples from Chapter 4.

> **Note (as of November 7, 2026).** In 2025 Anthropic archived its first-party GitHub, Slack, and PostgreSQL reference servers. npm marks those packages deprecated. The server entries in this README point at the successors the book uses. None of them is deprecated as of November 7, 2026. Package names here are a snapshot. Confirm each one against the MCP registry and the server's own docs before you wire it in.

When to use MCP and why: Chapter 4, Section 4.2.

## Files in This Directory

| File | Description | Source |
|------|-------------|--------|
| `basic_config.json` | Standard MCP configuration with common integrations | Listing 4-1 |
| `enterprise_config.json` | Same servers with per-server permissions, rate limits, and monitoring | Extended example |

## Configuration Structure

Every MCP configuration uses this structure:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "executable",
      "args": ["arg1", "arg2"],
      "env": {
        "ENV_VAR": "value"
      }
    }
  }
}
```

Remote servers use `"type": "http"` with a `url` instead of `command`/`args`. They usually add a `headers` block for authentication. This is the Claude Code form. In Claude Code, a `url` entry without `type` is a configuration error. Kiro and Cursor document `url` and `headers` without a `type` key.

### Field Descriptions

| Field | Required | Description |
|-------|----------|-------------|
| `command` | Yes (stdio) | The executable to run (e.g., `npx`, `docker`, `python`) |
| `args` | Yes (stdio) | Command-line arguments passed to the executable |
| `env` | No | Environment variables for the server process |
| `type` / `url` / `headers` | Yes (remote) | Transport type, endpoint, and auth headers for hosted servers |

The configuration format has no per-server `description` key. Keep notes on what each server does in your team docs.

The extended `enterprise_config.json` keeps annotation keys for illustration only. No client enforces them. Strip them before you hand the file to a real client. The annotation keys are everything except `command`, `args`, `env`, `type`, `url`, and `headers`:

- `description`, `permissions`, `rateLimit`, `constraints`, `exclude`, `readOnly`
- `allowedChannels`, `allowedProjects`, `allowedPaths`, `deniedPaths`, `_comment`
- the top-level `version`, `metadata`, and `globalSettings` blocks

Two entries need your attention:

- `monitoring-prometheus` still uses a `REPLACE_WITH_...` placeholder image. The [MCP Registry](https://registry.modelcontextprotocol.io/) lists several community Prometheus servers. Pick one you trust and follow its own run instructions.
- `secrets-vault` runs HashiCorp's `hashicorp/vault-mcp-server` image. HashiCorp describes it as intended for local use.

## Common MCP Servers

### GitHub Server (official, hosted)

GitHub's official MCP server gives access to repositories, PRs, and issues. This entry points at GitHub's hosted endpoint. For local use, run the Docker image `ghcr.io/github/github-mcp-server`.

**Claude Code caveat for remote entries.** In a remote server's `url` and `headers`, Claude Code reads some well-known credential variables as empty. It does not expand them. Its MCP docs name `ANTHROPIC_API_KEY`, `NPM_TOKEN`, and `HTTPS_PROXY` as examples and do not publish the full list. If GitHub answers 401 and your token is valid, export the token under a project-specific name, such as `GITHUB_MCP_PAT`. Then reference that name.

```json
"github-manager": {
  "type": "http",
  "url": "https://api.githubcopilot.com/mcp/",
  "headers": {
    "Authorization": "Bearer ${GITHUB_TOKEN}"
  }
}
```

### PostgreSQL Server (MCP Toolbox for Databases)

Google's MCP Toolbox for Databases gives database access with its prebuilt Postgres tools. Connection details come from the `POSTGRES_*` environment variables. Use a read-only role.

```json
"database": {
  "command": "npx",
  "args": ["-y", "@toolbox-sdk/server", "--prebuilt=postgres", "--stdio"],
  "env": {
    "POSTGRES_HOST": "host",
    "POSTGRES_PORT": "5432",
    "POSTGRES_DATABASE": "dbname",
    "POSTGRES_USER": "read_only_user",
    "POSTGRES_PASSWORD": "${DB_PASSWORD}"
  }
}
```

### Filesystem Server

Sandboxed access to specific directories.

```json
"filesystem": {
  "command": "npx",
  "args": [
    "-y",
    "@modelcontextprotocol/server-filesystem",
    "/path/to/allowed/directory"
  ]
}
```

### Slack Server

Sends notifications and queries Slack channels. The server exits at startup unless both `SLACK_BOT_TOKEN` and `SLACK_TEAM_ID` (your workspace ID) are set. The optional `SLACK_CHANNEL_IDS` narrows the channels it lists. It does not limit where the bot can post. The bot's scopes and channel membership in Slack control that.

```json
"slack": {
  "command": "npx",
  "args": ["-y", "@zencoderai/slack-mcp-server"],
  "env": {
    "SLACK_BOT_TOKEN": "${SLACK_TOKEN}",
    "SLACK_TEAM_ID": "${SLACK_TEAM_ID}"
  }
}
```

## Credentials

Use environment variables for credentials. The syntax depends on the client:

- Claude Code and Kiro expand `${VAR}`. Kiro expands only the variables you approve in its settings.
- Cursor's syntax is `${env:VAR}`.

## Using MCP Configurations

The `mcpServers` block above works in every tool. The file location differs per tool and changes between releases. So does whether you edit the file by hand. Check the tool's current documentation. Use the tool's own command instead of hand-editing a path you guessed.

| Tool | How to register a server | Covered in |
|------|--------------------------|------------|
| Claude Code | Run `claude mcp add`. It writes the configuration at local, project, or user scope. Project scope is a `.mcp.json` at the project root, which you can also write by hand. Run `/mcp` in a session to see connection status and sign in with OAuth. | Chapter 8 |
| Amazon Kiro | Configure through the Kiro menu. The workspace file is `.kiro/settings/mcp.json`. | Chapter 5 |
| Cursor | Add the server block to `.cursor/mcp.json` in the project, or `~/.cursor/mcp.json` for every project. | Chapter 7 |

Commit project-scope configuration to version control. Do not commit user-scope configuration. It usually contains paths and tokens specific to you.

## Troubleshooting

### Server Won't Start
- Check that the command exists (`npx`, `docker`, etc.).
- Verify network connectivity for remote servers.
- Check that the environment variables are set.

### Permission Denied
- Verify the credentials are correct.
- Check that the filesystem paths are accessible.
- Check that the Docker daemon is running (for Docker-based servers).

### Connection Timeout
- Check network and firewall settings.
- Verify the database or service is running.
- Test connectivity with `curl` or `ping`.

## Related Resources

- [MCP Specification](https://modelcontextprotocol.io/)
- [MCP Registry](https://registry.modelcontextprotocol.io/)
- [Official MCP Servers](https://github.com/modelcontextprotocol/servers)
- [GitHub's official MCP server](https://github.com/github/github-mcp-server)
- [MCP Toolbox for Databases](https://github.com/googleapis/mcp-toolbox)
- [MCP Setup Tutorial](../../tutorials/mcp-setup.md) in this chapter
- Chapter 8: Claude Code and MCP
