# Exercise 1: Create MCP Configuration

**Time Required**: 30-45 minutes
**Difficulty**: Beginner-Intermediate
**Prerequisites**: Completed MCP Setup tutorial

## Learning Objectives

By completing this exercise, you will:
- Configure MCP servers for a real-world scenario
- Apply security best practices
- Understand server-specific configurations
- Validate your configuration file

## Scenario

You are setting up an MCP configuration for a development team that needs:
1. **GitHub Enterprise** - For PR reviews and code discovery
2. **PostgreSQL** - Read-only access to the analytics database
3. **Slack** - Team notifications and context retrieval
4. **Filesystem** - Sandboxed access to the project directory

The team has the following requirements:
- All credentials must use environment variables
- Database access must be read-only
- Filesystem access should be restricted to `/app/src`, `/app/tests`, and `/app/docs`
- Slack should only post to `#dev-notifications` and `#code-reviews`

## Step 1: Create the Basic Structure

Create a file named `mcp_config.json` with the basic structure:

```jsonc
{
  "mcpServers": {
    // Your servers go here
  }
}
```

## Step 2: Add GitHub Enterprise Server

Add GitHub's official MCP server. (The archived `@modelcontextprotocol/server-github` package is deprecated.) Requirements:
- Run the official Docker image `ghcr.io/github/github-mcp-server`
- Use environment variable `GITHUB_ENTERPRISE_PAT` for the token
- Use environment variable `GITHUB_ENTERPRISE_URL` for the GitHub Enterprise host. The server's `GITHUB_HOST` expects the full URL with the `https://` scheme, for example `https://github.example.com`.

For github.com (not GitHub Enterprise), you can also use the hosted remote form. It takes `"type": "http"`, `"url": "https://api.githubcopilot.com/mcp/"`, and an `Authorization: Bearer` header.

<details>
<summary>Hint (Click to expand)</summary>

```json
"github-enterprise": {
  "command": "docker",
  "args": [
    "run", "-i", "--rm",
    "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
    "-e", "GITHUB_HOST",
    "ghcr.io/github/github-mcp-server"
  ],
  "env": {
    "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_ENTERPRISE_PAT}",
    "GITHUB_HOST": "${GITHUB_ENTERPRISE_URL}"
  }
}
```
</details>

## Step 3: Add PostgreSQL Database Server

Add a PostgreSQL server through MCP Toolbox for Databases. (The archived `mcp/postgres` Docker image is deprecated.) Requirements:
- Run `@toolbox-sdk/server` with its prebuilt Postgres tools over stdio
- Connection details come from `POSTGRES_*` environment variables:
  - `${DB_USER}` for username (a read-only role)
  - `${DB_PASS}` for password
  - `${DB_HOST}` for host
  - Database name: `analytics`

<details>
<summary>Hint (Click to expand)</summary>

```json
"analytics-db": {
  "command": "npx",
  "args": ["-y", "@toolbox-sdk/server", "--prebuilt=postgres", "--stdio"],
  "env": {
    "POSTGRES_HOST": "${DB_HOST}",
    "POSTGRES_PORT": "5432",
    "POSTGRES_DATABASE": "analytics",
    "POSTGRES_USER": "${DB_USER}",
    "POSTGRES_PASSWORD": "${DB_PASS}"
  }
}
```
</details>

## Step 4: Add Slack Integration

Configure Slack. Requirements:
- Use the `@zencoderai/slack-mcp-server` package (the archived `@modelcontextprotocol/server-slack` is deprecated)
- Use the `SLACK_BOT_TOKEN` and `SLACK_TEAM_ID` environment variables. The server will not start without both.

Set the channel restriction from the scenario in Slack. This file cannot enforce it. Scope the bot token, and invite the bot only to `#dev-notifications` and `#code-reviews`. The solution records the intent with an `allowedChannels` annotation key. MCP clients do not enforce that key.

<details>
<summary>Hint (Click to expand)</summary>

```json
"slack": {
  "command": "npx",
  "args": ["-y", "@zencoderai/slack-mcp-server"],
  "env": {
    "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}",
    "SLACK_TEAM_ID": "${SLACK_TEAM_ID}"
  }
}
```
</details>

## Step 5: Add Filesystem Access

Configure filesystem access:
- Access to `/app/src`, `/app/tests`, and `/app/docs` only
- Use a single filesystem server that allows multiple paths

<details>
<summary>Hint (Click to expand)</summary>

```json
"project-files": {
  "command": "npx",
  "args": [
    "-y",
    "@modelcontextprotocol/server-filesystem",
    "/app/src",
    "/app/tests",
    "/app/docs"
  ]
}
```
</details>

## Step 6: Add Enterprise Metadata

Add a metadata section. Like the annotation keys below, `metadata` is not part of the MCP configuration format. Clients ignore it. It documents the file:

```jsonc
{
  "metadata": {
    "name": "DevTeam MCP Configuration",
    "version": "1.0",
    "owner": "your-email@example.com",
    "lastUpdated": "2026-08-24"
  },
  "mcpServers": {
    // Your servers
  }
}
```

## Expected Output

Your completed configuration should look similar to this structure:

```json
{
  "metadata": {
    "name": "DevTeam MCP Configuration",
    "version": "1.0",
    "owner": "your-email@example.com",
    "lastUpdated": "2026-08-24"
  },
  "mcpServers": {
    "github-enterprise": {
      "command": "docker",
      "args": [...],
      "env": {...}
    },
    "analytics-db": {
      "command": "npx",
      "args": [...],
      "env": {...}
    },
    "slack": {
      "command": "npx",
      "args": [...],
      "env": {...}
    },
    "project-files": {
      "command": "npx",
      "args": [...]
    }
  }
}
```

A per-server `description` key is not part of the MCP configuration format. Document what each server is for in your team docs.

## Validation Checklist

Before submitting, verify:

- [ ] JSON is valid: `python -m json.tool mcp_config.json` prints the file back, reformatted (an error names the line and column instead)
- [ ] All credentials use environment variables (no hardcoded secrets)
- [ ] Database connection uses a read-only role
- [ ] Filesystem access is restricted to specified directories
- [ ] No archived server packages (`@modelcontextprotocol/server-github`, `server-slack`, `server-postgres`, or the `mcp/postgres` image)
- [ ] Metadata section is complete

## Bonus Challenges

The keys in these challenges (`rateLimit`, `constraints`) are governance annotations for illustration. They are not part of the configuration format. MCP clients do not enforce them. The same goes for `metadata`, `allowedChannels`, `exclude`, and `globalSettings` in the solution below. Strip all of them before you hand the file to a real client.

### Challenge 1: Add Rate Limiting

Add rate limiting configuration to the GitHub server:

```json
"rateLimit": {
  "requestsPerMinute": 30,
  "burstLimit": 50
}
```

### Challenge 2: Add Query Constraints

Add query constraints to the database server:

```json
"constraints": {
  "maxQueryTime": "30s",
  "maxRowsReturned": 10000,
  "allowedOperations": ["SELECT", "EXPLAIN"]
}
```

### Challenge 3: Add Monitoring

Add a Prometheus monitoring server for metrics collection.

## Solution

<details>
<summary>Complete Solution (Click to expand)</summary>

```json
{
  "metadata": {
    "name": "DevTeam MCP Configuration",
    "version": "1.0",
    "owner": "devteam@example.com",
    "lastUpdated": "2026-08-24"
  },
  "mcpServers": {
    "github-enterprise": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
        "-e", "GITHUB_HOST",
        "ghcr.io/github/github-mcp-server"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_ENTERPRISE_PAT}",
        "GITHUB_HOST": "${GITHUB_ENTERPRISE_URL}"
      },
      "rateLimit": {
        "requestsPerMinute": 30,
        "burstLimit": 50
      }
    },
    "analytics-db": {
      "command": "npx",
      "args": ["-y", "@toolbox-sdk/server", "--prebuilt=postgres", "--stdio"],
      "env": {
        "POSTGRES_HOST": "${DB_HOST}",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DATABASE": "analytics",
        "POSTGRES_USER": "${DB_USER}",
        "POSTGRES_PASSWORD": "${DB_PASS}"
      },
      "constraints": {
        "maxQueryTime": "30s",
        "maxRowsReturned": 10000,
        "allowedOperations": ["SELECT", "EXPLAIN"]
      }
    },
    "slack": {
      "command": "npx",
      "args": ["-y", "@zencoderai/slack-mcp-server"],
      "env": {
        "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}",
        "SLACK_TEAM_ID": "${SLACK_TEAM_ID}"
      },
      "allowedChannels": ["#dev-notifications", "#code-reviews"]
    },
    "project-files": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/app/src",
        "/app/tests",
        "/app/docs"
      ],
      "exclude": [
        "**/.env*",
        "**/secrets/**",
        "**/*.key",
        "**/*.pem"
      ]
    }
  },
  "globalSettings": {
    "logging": {
      "level": "info",
      "redactSecrets": true
    },
    "security": {
      "requireTLS": true,
      "auditAllRequests": true
    }
  }
}
```
</details>

## Common Mistakes to Avoid

1. **Hardcoding credentials**
   ```jsonc
   // WRONG
   "env": {
     "GITHUB_TOKEN": "ghp_abc123"  // Never do this!
   }

   // CORRECT
   "env": {
     "GITHUB_TOKEN": "${GITHUB_TOKEN}"
   }
   ```

2. **Not restricting filesystem access**
   ```jsonc
   // WRONG - Too broad
   "args": ["...", "/"]

   // CORRECT - Specific paths
   "args": ["...", "/app/src", "/app/tests"]
   ```

3. **Full-privilege database user**
   ```jsonc
   // WRONG - superuser account
   "POSTGRES_USER": "postgres"

   // CORRECT - read-only role
   "POSTGRES_USER": "read_only_user"
   ```

4. **Archived server packages**
   ```jsonc
   // WRONG - archived and deprecated on npm in 2025
   "args": ["-y", "@modelcontextprotocol/server-github"]

   // CORRECT - GitHub's official server (hosted endpoint or Docker image)
   "type": "http",
   "url": "https://api.githubcopilot.com/mcp/"
   ```

## Next Steps

After completing this exercise:

1. **Validate the JSON**: `python -m json.tool mcp_config.json`. If it parses, the file is printed back, reformatted. If not, you get the error and its position, for example `Expecting property name enclosed in double quotes: line 1 column 9 (char 8)`.
2. **Load it in a real tool**: register one server with your agentic tool. See [Using MCP Configurations](../code-examples/mcp-config/README.md#using-mcp-configurations) for the per-tool command. Confirm that the agent can reach the server. A configuration in the wrong location fails silently, even if it parses.
3. **Exercise 2**: [Create an A2A Agent Card](./exercise-2-agent-card.md)
4. **Tutorial**: [A2A Protocol Integration](../tutorials/a2a-integration.md)

## Reference

- [MCP Setup Tutorial](../tutorials/mcp-setup.md)
- [Code Example: basic_config.json](../code-examples/mcp-config/basic_config.json)
- [Code Example: enterprise_config.json](../code-examples/mcp-config/enterprise_config.json)
