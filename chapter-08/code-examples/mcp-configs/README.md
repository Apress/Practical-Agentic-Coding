# MCP Server Configurations

This directory holds example configurations that connect Claude Code to external systems with the Model Context Protocol (MCP).

What MCP adds and when to use it: Chapter 8, Section 8.4.

> **Update (as of November 7, 2026).** Anthropic archived its original reference servers for GitHub and PostgreSQL in 2025. Do not use configs that still name `@modelcontextprotocol/server-postgres` or `server-github`. The `@modelcontextprotocol/server-brave-search` reference package is deprecated too. Package names drift. Check the MCP registry before you wire one in.

## Overview

MCP servers give Claude Code tools for databases, APIs, and services. Each configuration file sets up one integration.

## Available Configurations

The two `.json` files are annotated references. Besides the `mcpServers` block, they carry documentation keys such as `description`, `available_tools`, and `security_recommendations`.

To use one, do either of these:

- Copy only the `mcpServers` block into your project's `.mcp.json`.
- Register the server with `claude mcp add --scope project`. It writes `.mcp.json` for you.

Claude Code asks for approval before it uses a project-scoped server from `.mcp.json` for the first time.

### postgres-config.json

Connects to PostgreSQL databases for:
- Running SQL queries
- Describing table schemas
- Listing database tables

### github-config.json

Connects to GitHub for:
- Searching repositories
- Reading file contents
- Creating and managing issues
- Working with pull requests

### Complete Example

A full configuration combining multiple servers:

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@toolbox-sdk/server", "--prebuilt=postgres", "--stdio"],
      "env": {
        "POSTGRES_HOST": "${POSTGRES_HOST}",
        "POSTGRES_DATABASE": "${POSTGRES_DATABASE}",
        "POSTGRES_USER": "${POSTGRES_USER}",
        "POSTGRES_PASSWORD": "${POSTGRES_PASSWORD}"
      }
    },
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${GITHUB_PAT}"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/allowed/path"
      ]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

- `postgres` uses MCP Toolbox for Databases with its prebuilt Postgres tools. It reads connection details from the `POSTGRES_*` variables.
- `github` uses GitHub's hosted server over HTTP.

## Configuration Structure

### Basic Format

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

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `command` | Yes (stdio) | Executable to run the server |
| `args` | No | Command-line arguments |
| `env` | No | Environment variables |
| `type` / `url` / `headers` | Yes (remote) | Transport type, endpoint, and auth headers for hosted servers |

### Environment Variable References

Use `${VAR_NAME}` to reference an environment variable. Use `${VAR_NAME:-default}` to fall back to a default. Claude Code expands both in `command`, `args`, `env`, `url`, and `headers`:

```json
{
  "env": {
    "POSTGRES_PASSWORD": "${POSTGRES_PASSWORD}",
    "API_KEY": "${MY_API_KEY}"
  }
}
```

## Security Settings

### 1. Use Environment Variables for Secrets

```bash
# Set secrets in your shell
export POSTGRES_PASSWORD="your_db_password"
export GITHUB_PAT="ghp_your_token"

# Never hardcode secrets in configuration files
```

### 2. Use Read-Only Database Users

```sql
-- Create a read-only user for MCP
CREATE USER claude_reader WITH PASSWORD 'secure_password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO claude_reader;

-- Revoke dangerous permissions
REVOKE INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public FROM claude_reader;
```

### 3. Limit File System Access

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/specific/allowed/directory"
      ]
    }
  }
}
```

### 4. Combine with Permissions

MCP tools are named `mcp__<server>__<tool>`. Permission rules match the whole tool. Put the rules in `.claude/settings.json`. `.mcp.json` holds only the server definitions.

```json
{
  "permissions": {
    "allow": [
      "mcp__postgres__execute_sql",
      "mcp__postgres__list_tables"
    ]
  }
}
```

Run `/mcp` in a session to see the tools a connected server exposes. Names vary by server version. A rule that names a tool that does not exist matches nothing, with no warning.

A permission rule cannot inspect what is *inside* an argument. So you cannot allow `SELECT` and deny `DELETE` on the same `execute_sql` tool this way. To enforce read-only access, use one of these:

- The database grant: a `claude_reader` role with `SELECT` only. This holds even if a hook is misconfigured.
- A PreToolUse hook that reads the query text and exits 2 on a write verb.

## Common MCP Servers

The table lists the maintained entries as of November 7, 2026 (see the update note at the top). Treat exact package names as a snapshot.

| Server | Package | Purpose |
|--------|---------|---------|
| PostgreSQL | `@toolbox-sdk/server` (MCP Toolbox for Databases, `--prebuilt=postgres`) | Database queries |
| GitHub | Official GitHub MCP server (hosted `https://api.githubcopilot.com/mcp/` or Docker `ghcr.io/github/github-mcp-server`) | Repository operations |
| Filesystem | `@modelcontextprotocol/server-filesystem` | File operations |
| Memory | `@modelcontextprotocol/server-memory` | Persistent memory |
| Brave Search | `@brave/brave-search-mcp-server` (Brave's own server; the `@modelcontextprotocol/server-brave-search` reference package is deprecated) | Web search |

### Installation

Run stdio servers with npx. No installation is required:

```bash
npx -y @toolbox-sdk/server --prebuilt=postgres --stdio
```

Or install globally:

```bash
npm install -g @toolbox-sdk/server
```

Hosted servers such as GitHub's need no installation. The client connects to the URL directly.

## Troubleshooting

### Server Not Found

```bash
# Verify the package exists
npx -y @toolbox-sdk/server --help
```

### Connection Refused

```bash
# Check database is running
pg_isready -h localhost -p 5432

# Check environment variables
echo $POSTGRES_HOST $POSTGRES_DATABASE $POSTGRES_USER
```

### Permission Denied

- Check that API tokens have the required scopes
- Check the database user permissions
- Check the file system path permissions

## See Also

- [Exercise 3: MCP Integration](../../hands-on-lab/exercises/exercise-3-mcp.md)
- [MCP Integration Tutorial](../../hands-on-lab/tutorials/mcp-integration.md)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
