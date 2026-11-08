# MCP integration: quick reference

Use this file to connect Claude Code to external systems with the Model Context Protocol (MCP). It covers configuration, common servers, security settings, a custom server, and troubleshooting.

What MCP adds to Claude Code, and when to use it: Chapter 8, Section 8.4.

For the latest, see the Claude Code docs at [code.claude.com/docs](https://code.claude.com/docs) and the [MCP specification](https://modelcontextprotocol.io/).

> **Updates to the book (as of November 7, 2026)**
>
> - **Node.js 24.** The filesystem and memory servers require a current Node.js 24 or later.
> - **Archived reference servers.** Anthropic's original Postgres and GitHub reference servers were archived in 2025. `@modelcontextprotocol/server-postgres` and `@modelcontextprotocol/server-github` are deprecated. Use MCP Toolbox for Databases and GitHub's official MCP server instead.
> - **Other deprecated packages.** The `@modelcontextprotocol/server-brave-search` and `server-puppeteer` reference packages are deprecated on npm as well. Do not wire them in.
> - **Package names drift.** The [Available MCP Servers](#available-mcp-servers) table lists the maintained entries. Treat exact package names as a snapshot. Check the MCP registry before you wire one in.

## Getting Started

### Prerequisites

- Node.js, for `npx`-launched servers. The filesystem and memory servers need Node.js 24 or later (see the note at the top). The custom-server example below was tested on Node.js 24.
- Claude Code installed
- Access to external systems you want to connect

### Basic Configuration

Register a server with `claude mcp add`. It writes the entry for you.

- For a stdio server: `claude mcp add --scope project <name> -- <command> [args...]`
- For a hosted server: `claude mcp add --transport http <name> --scope project <url>`

Scopes:

- `local`: just you, this repo. This is the default.
- `project`: checked into `.mcp.json`, so teammates get it too.
- `user`: all your repos.

Local and user entries live in `~/.claude.json`.

To keep a token out of a checked-in file, write `${VAR}` references into `.mcp.json` by hand, as the examples below do.

To configure a server by hand, create `.mcp.json` at the project root. Do not put MCP servers in `.claude/settings.json`. That file holds permissions and hooks.

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "package-name"],
      "env": {
        "API_KEY": "${API_KEY}"
      }
    }
  }
}
```

## Common Integrations

### PostgreSQL Database

Use MCP Toolbox for Databases, Google's open-source server, with the `--prebuilt=postgres` tool set.

**Installation:**

```bash
# Set environment variables
export POSTGRES_HOST="localhost"
export POSTGRES_DATABASE="mydb"
export POSTGRES_USER="claude_reader"
export POSTGRES_PASSWORD="your_password"
```

**Configuration:**

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
    }
  }
}
```

**Available Tools** (names vary by version; run `/mcp` to list them):
- `execute_sql` - Run SQL statements
- `list_tables` - List all tables

**Example Usage:**

```text
> List all tables in the database

> Describe the users table schema

> Query the tickets table for entries from the last 7 days
```

**Book example (Chapter 8, Section 8.4): database-informed debugging.** Claude pulls real rows through the database server, then compares the patterns with your code:

```text
> Query the users table to find patterns in accounts that got the
> "payment_failed" error in the last week. Then examine our PaymentService
> code and identify potential causes.
```

### GitHub

Use GitHub's official MCP server.

**Setup:**

1. Create a Personal Access Token in GitHub Settings.
2. Set the environment variable:
   ```bash
   export GITHUB_PAT="ghp_..."
   ```

**Configuration (hosted endpoint):**

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${GITHUB_PAT}"
      }
    }
  }
}
```

For local or GitHub Enterprise use, run the same server as a Docker image: `docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN ghcr.io/github/github-mcp-server`.

**Available Tools:**
- `search_repositories` - Search repos
- `get_file_contents` - Read files
- `list_issues` - List issues
- `issue_write` - Create or update issues
- `list_pull_requests` - List PRs

**Example Usage:**

```text
> Search for Python repositories about machine learning

> Get the README from owner/repo

> List open issues in my repository
```

### Filesystem

**Configuration:**

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/allowed/directory"
      ]
    }
  }
}
```

List only the directories Claude should access.

### Memory (Persistent)

**Configuration:**

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

This server keeps information across sessions.

## Multi-Server Configuration

Put several servers in one `.mcp.json`:

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
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "./data"]
    }
  }
}
```

## Security Settings

Which systems to connect and how much access to give: Chapter 8, Section 8.4.

### 1. Use Environment Variables

```bash
# Set secrets in shell, not in config
export POSTGRES_PASSWORD="your_db_password"
export GITHUB_PAT="ghp_..."
```

Do not hardcode credentials in `.mcp.json`. The file is checked in. A pasted password ships to everyone who clones the repository. Use `${VAR}` references instead.

### 2. Use Read-Only Database Users

```sql
-- Create read-only user
CREATE USER claude_reader WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE mydb TO claude_reader;
GRANT USAGE ON SCHEMA public TO claude_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO claude_reader;

-- Block dangerous operations
REVOKE INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public FROM claude_reader;
```

### 3. Combine with Permissions

Permission rules live in `.claude/settings.json`. The server definitions stay in `.mcp.json`. Rules use the form `mcp__<server>__<tool>`. A rule matches a whole tool. It does not match SQL verbs inside an argument.

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

A rule cannot allow `SELECT` and deny `DELETE` inside the same `execute_sql` tool. To enforce read-only access, use one of these:

- The database grant in step 2 above
- A PreToolUse hook that inspects the query text

### 4. Limit File System Access

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/specific/project/data"
      ]
    }
  }
}
```

Grant access only to the directories Claude needs.

### 5. Use Minimal Token Scopes

For GitHub:

- Use a fine-grained token. Limit it to the repositories Claude needs. Give it read-only permissions unless it must write.
- With a classic token, `repo` grants full access to private repositories. `public_repo` can write to public ones. No classic scope gives read-only access to private repositories.
- Do not grant `admin:repo_hook` or `delete_repo`.

## Creating Custom MCP Servers

### Basic Structure

The TypeScript SDK's `McpServer` registers each tool with a zod input schema.

1. Set up the package:
   - `npm init -y`
   - `npm pkg set type=module`
   - `npm install @modelcontextprotocol/sdk zod`
   - `npm install -D typescript @types/node`
2. Write the server:

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({ name: "my-custom-server", version: "1.0.0" });

server.registerTool(
  "my_tool",
  {
    description: "What this tool does",
    inputSchema: { param1: z.string() },
  },
  async ({ param1 }) => ({
    content: [{ type: "text", text: `Received ${param1}` }],
  }),
);

// Start server; a stdio server must not write anything else to stdout
const transport = new StdioServerTransport();
await server.connect(transport);
```

[Exercise 3, Part 4](../exercises/exercise-3-mcp.md) builds a complete server this way against the SupportFlow API. It includes the `tsconfig.json`, the build command, and an end-to-end check.

### Configure Custom Server

```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["./path/to/server.js"],
      "env": {
        "MY_API_KEY": "${MY_API_KEY}"
      }
    }
  }
}
```

## Troubleshooting

### Server Not Starting

```bash
# Test server manually
npx -y @toolbox-sdk/server --help

# Check environment variables
echo $POSTGRES_HOST $POSTGRES_DATABASE $POSTGRES_USER
```

### Connection Refused

```bash
# Check database is running
pg_isready -h localhost -p 5432

# Test connection
psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DATABASE" -c "SELECT 1"
```

### Permission Denied

1. Check that API tokens have the correct scopes.
2. Check the database user permissions.
3. Check the file system permissions.

### Timeout Errors

1. Increase the operation timeout.
2. Check network connectivity.
3. Check that the server responds.

## Available MCP Servers

This table lists the maintained entries as of November 7, 2026. Package names drift (see the note at the top).

| Server | Package | Purpose |
|--------|---------|---------|
| PostgreSQL | `@toolbox-sdk/server` (MCP Toolbox for Databases, `--prebuilt=postgres`) | Database queries |
| GitHub | Official GitHub MCP server (hosted `https://api.githubcopilot.com/mcp/` or Docker `ghcr.io/github/github-mcp-server`) | Repository operations |
| Filesystem | `@modelcontextprotocol/server-filesystem` | File access |
| Memory | `@modelcontextprotocol/server-memory` | Persistent memory |
| Brave Search | `@brave/brave-search-mcp-server` (Brave's own server) | Web search |
| Playwright | `@playwright/mcp` (Microsoft's Playwright server) | Browser automation |

### Community Servers

For community servers, check the [MCP Registry](https://registry.modelcontextprotocol.io/) and the [reference server repository](https://github.com/modelcontextprotocol/servers).

## See Also

- [MCP Configuration Examples](../../code-examples/mcp-configs/)
- [Exercise 3: MCP Integration](../exercises/exercise-3-mcp.md)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [MCP Server Repository](https://github.com/modelcontextprotocol/servers)
