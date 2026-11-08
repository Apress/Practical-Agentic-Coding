# Exercise 3: MCP Integration

## Objective

Configure Model Context Protocol (MCP) servers that connect Claude Code to databases, APIs, and services.

## Duration

45-60 minutes

## Background

MCP connects Claude Code to systems outside the filesystem, such as databases, monitoring, CI/CD, and issue trackers. Why that matters: Chapter 8, Section 8.4. This exercise gets the connections working.

### What You Connect

After you configure the servers below, Claude can pull:
- live error rates out of monitoring
- query patterns straight from the database
- deploy history out of CI/CD
- open issues and project state

The cross-system exercises in Part 3 use these.

### MCP Architecture

```text
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Claude Code   │────▶│   MCP Server    │────▶│ External System │
│  (MCP Client)   │◀────│  (Tool Provider)│◀────│ (DB, API, etc.) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Part 1: Understanding MCP Configuration

The quickest route is `claude mcp add`. It writes the entry for you. Pass `--scope project` for a team-shared server. The other scopes are local and user.

This exercise edits the project-scope file directly. That file is `.mcp.json` at the repo root. It is checked in, so every teammate gets the same servers.

Do not put MCP servers in `.claude/settings.json`. That file holds permissions and hooks.

```json
{
  "mcpServers": {
    "server-name": {
      "command": "executable",
      "args": ["arg1", "arg2"],
      "env": {
        "ENV_VAR": "${ENV_VAR}"
      }
    }
  }
}
```

### Configuration Fields

| Field | Description |
|-------|-------------|
| `command` | Executable to run the MCP server (stdio servers) |
| `args` | Command-line arguments |
| `env` | Environment variables. `${VAR}` reads one from your shell. `${VAR:-default}` adds a fallback |
| `type` / `url` / `headers` | Transport type, endpoint, and auth headers (hosted servers) |

## Part 2: Common MCP Servers

> **Update (as of November 7, 2026).** Anthropic's original Postgres and GitHub reference servers were archived in 2025. The entries below use the maintained successors. Package names drift. Check the MCP registry and each server's documentation for the current entry.

### PostgreSQL Server

Connect to PostgreSQL through MCP Toolbox for Databases, with the `--prebuilt=postgres` tool set:

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
- `execute_sql` - Execute SQL statements
- `list_tables` - List all tables

### GitHub Server

Connect to GitHub's official hosted MCP server:

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

For offline or GitHub Enterprise use, there is also a local Docker image (`ghcr.io/github/github-mcp-server`).

**Available Tools:**
- `search_repositories` - Search for repos
- `get_file_contents` - Read files
- `issue_write` - Create or update issues
- `list_pull_requests` - List PRs

### Filesystem Server

File operations:

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

### Memory Server

Memory that persists across sessions:

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

## Part 3: Hands-On Exercises

### Exercise 3A: Configure PostgreSQL MCP

Set up Claude Code to query a database.

**Step 1**: Set up environment

```bash
# Set your database connection details
export POSTGRES_HOST="localhost"
export POSTGRES_DATABASE="supportflow"
export POSTGRES_USER="claude_readonly"
export POSTGRES_PASSWORD="your_password"
```

MCP Toolbox also ships prebuilt tool sets for other databases, such as SQLite and MySQL. For those, change the `--prebuilt` value and the environment variables.

**If you do not have Postgres:** SupportFlow runs on SQLite until Challenge Lab 3 migrates it. You can point Toolbox at its database file instead.

1. Start the API once so `supportflow.db` exists. Under Docker the file is `data/supportflow.db`.
2. From the `supportflow/` directory, run:

```bash
export SQLITE_DATABASE="$PWD/supportflow.db"
```

```json
{
  "mcpServers": {
    "sqlite": {
      "command": "npx",
      "args": ["-y", "@toolbox-sdk/server", "--prebuilt=sqlite", "--stdio"],
      "env": {
        "SQLITE_DATABASE": "${SQLITE_DATABASE}"
      }
    }
  }
}
```

The `sqlite` tool set exposes `execute_sql` and `list_tables`, the same names as the Postgres one. The prompts in Step 3 work unchanged. Tool rules become `mcp__sqlite__execute_sql`.

**Step 2**: Create MCP configuration

Create or update `.mcp.json` at the project root. Or let `claude mcp add --scope project` write the entry for you.

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

**Step 3**: Test the connection

Start Claude Code and try:

```text
> List all tables in the database

> Describe the schema of the tickets table

> Query the last 10 tickets ordered by created_at
```

### Exercise 3B: Configure GitHub MCP

Connect Claude Code to your GitHub repositories.

**Step 1**: Create a GitHub token

1. Go to GitHub Settings > Developer settings > Personal access tokens.
2. Create a token with `repo` scope.
3. Set the environment variable:

```bash
export GITHUB_PAT="ghp_your_token_here"
```

**Step 2**: Add the GitHub server to `.mcp.json`

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

**Step 3**: Test GitHub integration

```text
> Search for repositories related to "supportflow"

> List open issues in my repository

> Get the contents of README.md from the main branch
```

### Exercise 3C: Multi-Server Configuration

Configure multiple MCP servers together.

**Step 1**: Create a complete configuration in `.mcp.json`

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
        "./data"
      ]
    }
  }
}
```

**Step 2**: Test cross-system queries

```text
> Check the database for tickets with errors, then create a GitHub issue
> summarizing the top 5 issues.

> Compare the ticket count in the database with the number of
> closed issues in GitHub.
```

### Exercise 3D: Database-Informed Debugging

Use MCP to analyze real data alongside code.

**Scenario**: Users report payment failures.

```text
> Query the database to find patterns in accounts that got the
> "payment_failed" error in the last week. What do they have in common?

> Based on the database patterns, examine the PaymentService code
> and identify potential causes for the failures.
```

Claude compares the production data with the code and reports what it finds.

## Part 4: Creating a Custom MCP Server

Create a custom MCP server for SupportFlow. It exposes ticket operations by calling the running SupportFlow API.

**Step 1**: Create the server project (from your project root)

```bash
mkdir -p mcp-supportflow/src
cd mcp-supportflow
npm init -y
npm pkg set type=module
npm install @modelcontextprotocol/sdk zod
npm install -D typescript @types/node
```

`type=module` lets the server use ES module imports and top-level `await`.

**Step 2**: Create `tsconfig.json` in `mcp-supportflow/`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "rootDir": "src",
    "outDir": "dist",
    "strict": true,
    "skipLibCheck": true,
    "types": ["node"]
  },
  "include": ["src"]
}
```

Recent TypeScript releases require `rootDir` and `types`. The same file works with TypeScript 5.

**Step 3**: Create `src/index.ts`:

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const API_URL = process.env.SUPPORTFLOW_API_URL ?? "http://localhost:8000";
const API_KEY = process.env.SUPPORTFLOW_API_KEY ?? "demo-key-12345";

// Call the running SupportFlow API and return the body as MCP text content.
async function callApi(path: string, init: RequestInit = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
      ...init.headers,
    },
  });
  const text = await response.text();
  return {
    content: [{ type: "text" as const, text }],
    isError: !response.ok,
  };
}

const server = new McpServer({ name: "supportflow-mcp", version: "1.0.0" });

server.registerTool(
  "analyze_ticket",
  {
    description:
      "Submit a support ticket to SupportFlow and return its analysis " +
      "(category, urgency, sentiment), escalation result, and draft response",
    inputSchema: { content: z.string().min(10).max(5000) },
  },
  async ({ content }) =>
    callApi("/tickets", { method: "POST", body: JSON.stringify({ content }) }),
);

server.registerTool(
  "get_escalation_status",
  {
    description: "Fetch a stored ticket, including whether it should be escalated",
    inputSchema: { ticket_id: z.string() },
  },
  async ({ ticket_id }) => callApi(`/tickets/${encodeURIComponent(ticket_id)}`),
);

// Stdio servers must never write to stdout except protocol messages.
const transport = new StdioServerTransport();
await server.connect(transport);
```

The server has two tools:

- `analyze_ticket` submits a ticket through `POST /tickets`. The API also stores the ticket and its draft response.
- `get_escalation_status` reads a ticket back through `GET /tickets/{ticket_id}`.

Both send the `X-API-Key` header. A non-2xx answer comes back flagged as an error.

**Step 4**: Build it

```bash
npx tsc
```

This writes `dist/index.js`.

**Step 5**: Configure in Claude Code

Add this to `.mcp.json` at the project root, next to the `mcp-supportflow/` folder. `${API_KEY:-demo-key-12345}` reads your `API_KEY` environment variable. If it is not set, it uses the demo key.

```json
{
  "mcpServers": {
    "supportflow": {
      "command": "node",
      "args": ["./mcp-supportflow/dist/index.js"],
      "env": {
        "SUPPORTFLOW_API_URL": "http://localhost:8000",
        "SUPPORTFLOW_API_KEY": "${API_KEY:-demo-key-12345}"
      }
    }
  }
}
```

**Step 6**: Try it

1. Start the SupportFlow API (`docker-compose up -d`, or `uvicorn api.main:app --env-file .env`).
2. Start `claude` in the project root.
3. Approve the project MCP server when asked.
4. Run `/mcp` and check that `supportflow` is connected.
5. Run:

```text
> Use the supportflow analyze_ticket tool on this ticket: "I was charged
> twice for order ORD-2024-5678 and I need a refund."

> Now check the escalation status of that ticket.
```

This server was built with Node.js 24, TypeScript 5.9 and 7.0, and `@modelcontextprotocol/sdk` 1.32. It was checked end to end against the reference API:

- The tool list shows both tools.
- `analyze_ticket` creates a ticket.
- `get_escalation_status` reads it back.
- An unknown ticket ID comes back as an error.

## Part 5: Security Considerations

### Environment Variables

Do this: keep secrets in your shell environment and reference them as `${VAR}`.

```bash
export POSTGRES_PASSWORD="your_db_password"
export GITHUB_PAT="ghp_..."
```

Do not do this: a literal secret in `.mcp.json`. The file is checked in and ships to everyone who clones the repository.

```jsonc
{
  "env": {
    "POSTGRES_PASSWORD": "hunter2"  // Don't do this!
  }
}
```

### Limiting MCP Server Access

Use the `permissions` field in `.claude/settings.json` to restrict which MCP tools Claude may call. The server definition stays in `.mcp.json`. The permission rules live in settings. Rules use the form `mcp__<server>__<tool>`. A rule matches a whole tool. It does not match SQL verbs inside an argument.

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

A rule cannot allow `SELECT` and deny `DELETE` inside the same `execute_sql` tool. To enforce read-only access, use the database grant (next section) or a PreToolUse hook that inspects the query text.

### Read-Only Database Connections

Use read-only database users:

```sql
-- Create read-only user for MCP
CREATE USER claude_readonly WITH PASSWORD 'secure_password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO claude_readonly;
```

## Deliverables

1. A project-root `.mcp.json` with at least two MCP servers configured
2. Documentation of what each server provides
3. Example prompts demonstrating cross-system analysis
4. A security configuration limiting dangerous operations

## Self-Assessment

- [ ] PostgreSQL MCP server configured and working
- [ ] GitHub MCP server configured (or alternative)
- [ ] Environment variables properly externalized
- [ ] Permissions restrict dangerous operations
- [ ] Successfully ran cross-system queries

## Troubleshooting

### "Server not found" error
```bash
# Ensure npx can find the package
npx -y @toolbox-sdk/server --help
```

### "Connection refused" error
```bash
# Check database is running
pg_isready -h localhost -p 5432
```

### "Permission denied" error
```bash
# Check environment variables are set
echo $POSTGRES_HOST $POSTGRES_DATABASE $POSTGRES_USER
```

## Solution Reference

Compare your solution with the examples in [`../../code-examples/mcp-configs/`](../../code-examples/mcp-configs/).

## Next Steps

You have completed all three exercises. Return to the [main lab](../README.md) and build the complete SupportFlow system.

Then take on the Section 8.7 challenges, in order:

1. [Debug and fix](challenge-1-debug-and-fix.md)
2. [Security hardening](challenge-2-security-hardening.md)
3. [Observability and operations](challenge-3-observability.md)
