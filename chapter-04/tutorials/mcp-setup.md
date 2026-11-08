# MCP setup: quick reference

**Time Required**: 20-30 minutes
**Difficulty**: Beginner
**Prerequisites**: Basic familiarity with JSON, terminal/command line

> **Note (as of November 7, 2026).** The filesystem server requires a current Node.js 24 or later. On older Node, npm first prints an `npm warn EBADENGINE` Unsupported engine block. If you see it, upgrade Node.

> **Server packages change.** The package names below are a point-in-time snapshot. Anthropic's original `@modelcontextprotocol/server-github` reference server was archived in 2025. The archived `@modelcontextprotocol/server-slack` and the `mcp/postgres` reference image are deprecated. Confirm the current entry in the [MCP Registry](https://registry.modelcontextprotocol.io/) and the server's own docs before you wire it in.

When to use MCP and why: Chapter 4, Section 4.2.

For the latest setup details, see the [MCP documentation](https://modelcontextprotocol.io/) and your tool's own MCP guide.

## What you build

An MCP configuration with four servers: filesystem, GitHub, database, and Slack.

## Step 1: Learn the file format

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

Hosted (remote) servers use a different form. Give them `"type": "http"`, a `url`, and a `headers` block for authentication. Leave out `command` and `args`. This tutorial uses both forms.

### Field reference

| Field | Required | Description |
|-------|----------|-------------|
| `command` | Yes (stdio) | The executable to run (e.g., `npx`, `docker`, `python`) |
| `args` | Yes (stdio) | Command-line arguments passed to the executable |
| `env` | No | Environment variables for the server process |
| `type` / `url` / `headers` | Yes (remote) | Transport type, endpoint, and auth headers for hosted servers |

The format has no per-server `description` key. Write down each server's purpose in your team docs, not in the file.

## Step 2: Create your first MCP configuration

Create a file called `mcp_config.json`:

```json
{
  "mcpServers": {
    "project-files": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/your/project"
      ]
    }
  }
}
```

What each part does:

- `command: "npx"` runs the Node.js package executor.
- The `-y` flag confirms the package installation automatically.
- `@modelcontextprotocol/server-filesystem` is the official filesystem MCP server.
- `/path/to/your/project` is the directory the agent can access.

### Try it

1. Replace `/path/to/your/project` with a real project path.
2. Save the file.

## Step 3: Add a GitHub server

Use GitHub's official MCP server. The hosted endpoint is the simplest form:

```json
{
  "mcpServers": {
    "project-files": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/your/project"
      ]
    },
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${GITHUB_TOKEN}"
      }
    }
  }
}
```

To run the server locally (for example, against GitHub Enterprise), use GitHub's Docker image: `docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN ghcr.io/github/github-mcp-server`.

`${GITHUB_TOKEN}` references an environment variable. Do not paste the token into the file. The syntax depends on the client:

- Claude Code and Kiro expand `${VAR}`. Kiro expands only the variables you approve in its settings.
- Cursor writes it as `${env:GITHUB_TOKEN}`.
- Claude Code expects the `"type": "http"` key on a remote entry. Kiro and Cursor take `url` and `headers` without it.

**Claude Code caveat for remote entries.** In a remote server's `url` and `headers`, Claude Code reads some well-known credential variables as empty. It does not expand them. Its MCP docs name `ANTHROPIC_API_KEY`, `NPM_TOKEN`, and `HTTPS_PROXY` as examples and do not publish the full list. If GitHub answers 401 and your token is valid, export the token under a project-specific name, such as `GITHUB_MCP_PAT`. Then reference that name.

### Set the environment variable

**Linux/Mac:**
```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

**Windows (PowerShell):**
```powershell
$env:GITHUB_TOKEN="ghp_your_token_here"
```

**Or add it to your shell profile** (~/.bashrc, ~/.zshrc):
```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

## Step 4: Add a database server

Use MCP Toolbox for Databases (Google's open-source server, actively maintained) with the prebuilt Postgres tool set:

```json
{
  "mcpServers": {
    "project-files": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/your/project"
      ]
    },
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${GITHUB_TOKEN}"
      }
    },
    "database": {
      "command": "npx",
      "args": ["-y", "@toolbox-sdk/server", "--prebuilt=postgres", "--stdio"],
      "env": {
        "POSTGRES_HOST": "${DB_HOST}",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DATABASE": "${DB_NAME}",
        "POSTGRES_USER": "${DB_USER}",
        "POSTGRES_PASSWORD": "${DB_PASS}"
      }
    }
  }
}
```

Toolbox arguments:

- `@toolbox-sdk/server` is MCP Toolbox for Databases.
- `--prebuilt=postgres` loads the prebuilt Postgres tool set.
- `--stdio` runs over stdio, the transport local MCP clients expect.
- The `POSTGRES_*` environment variables supply the connection details.

To connect with a read-only database user, create one first:

```sql
CREATE USER mcp_readonly WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE mydb TO mcp_readonly;
GRANT USAGE ON SCHEMA public TO mcp_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO mcp_readonly;
```

## Step 5: Add Slack

Use the `@zencoderai/slack-mcp-server` package. The server refuses to start unless both `SLACK_BOT_TOKEN` and `SLACK_TEAM_ID` (your Slack workspace ID) are set.

```json
{
  "mcpServers": {
    "project-files": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/your/project"
      ]
    },
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${GITHUB_TOKEN}"
      }
    },
    "database": {
      "command": "npx",
      "args": ["-y", "@toolbox-sdk/server", "--prebuilt=postgres", "--stdio"],
      "env": {
        "POSTGRES_HOST": "${DB_HOST}",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DATABASE": "${DB_NAME}",
        "POSTGRES_USER": "${DB_USER}",
        "POSTGRES_PASSWORD": "${DB_PASS}"
      }
    },
    "slack": {
      "command": "npx",
      "args": ["-y", "@zencoderai/slack-mcp-server"],
      "env": {
        "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}",
        "SLACK_TEAM_ID": "${SLACK_TEAM_ID}"
      }
    }
  }
}
```

## Step 6: Register the configuration with your tool

The `mcpServers` block works in every tool. The file location does not. Each tool has its own path and its own registration command, and both change between releases. Use the tool's own command where one exists. Do not hand-edit a path you guessed.

| Tool | How to register | Covered in |
|------|-----------------|------------|
| Claude Code | `claude mcp add` writes the configuration for you at local, project, or user scope. To use your file as-is, save it as `.mcp.json` in the project root (the project-scope file). Then run `claude mcp list` to check it. Run `/mcp` in a session to check connection status and sign in to servers that need OAuth. | Chapter 8 |
| Amazon Kiro | Configure through the Kiro menu. The workspace file is `.kiro/settings/mcp.json`. Commit it with the rest of `.kiro/`. | Chapter 5 |
| Cursor | Copy the `mcpServers` block into `.cursor/mcp.json` in the project (or `~/.cursor/mcp.json` for every project). Rewrite each `${VAR}` as `${env:VAR}`. | Chapter 7 |

Check your tool's current documentation for the path before you file a bug about a server that will not connect. A configuration in the wrong location fails silently. The tool sees no servers.

## Troubleshooting

### Server won't start

```bash
# Check if npx is available
npx --version

# Check if Docker is running (only needed for Docker-based servers)
docker info

# Test a stdio server manually (Ctrl+C to stop)
npx -y @modelcontextprotocol/server-filesystem /tmp
```

On Windows, point the test at a folder that exists. For example: `npx -y @modelcontextprotocol/server-filesystem C:\Users\you\Desktop`.

A working server prints `Secure MCP Filesystem Server running on stdio`. Then it waits for a client. An error here is the same error your agent tool would hit. If npm prints `npm warn EBADENGINE`, see the Node.js note at the top of this file.

### Permission denied

- Verify the credentials are correct.
- Check that the environment variables are set.
- For Docker, check that the daemon is running.

### Connection timeout

- Check network connectivity.
- Verify the database or service is running.
- Test with `curl` or `psql` directly.

## Verification checklist

- [ ] Created `mcp_config.json` with at least one server
- [ ] Set up required environment variables
- [ ] Tested that Docker is running (if using a Docker-based server such as `ghcr.io/github/github-mcp-server`)
- [ ] Placed configuration in the correct location for your IDE/tool
- [ ] No hardcoded credentials in the configuration
- [ ] No archived server packages (`@modelcontextprotocol/server-github`, `server-slack`, `server-postgres`, or the `mcp/postgres` image)

## Next steps

1. **Exercise 1**: [Create a complete MCP configuration](../exercises/exercise-1-mcp-config.md)
2. **Tutorial**: [A2A Protocol Integration](./a2a-integration.md)
3. **Tool chapters**: Chapter 5 configures MCP servers in Amazon Kiro. Chapter 8 covers Claude Code and MCP.

## Reference

- [MCP Specification](https://modelcontextprotocol.io/)
- [MCP Registry](https://registry.modelcontextprotocol.io/)
- [Official MCP Servers](https://github.com/modelcontextprotocol/servers)
- [GitHub's official MCP server](https://github.com/github/github-mcp-server)
- [MCP Toolbox for Databases](https://github.com/googleapis/mcp-toolbox)
- [Code Example: basic_config.json](../code-examples/mcp-config/basic_config.json)
- [Code Example: enterprise_config.json](../code-examples/mcp-config/enterprise_config.json)
