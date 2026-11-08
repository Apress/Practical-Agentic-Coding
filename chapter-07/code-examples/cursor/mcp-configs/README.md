# MCP Configuration for Cursor

Model Context Protocol (MCP) lets Cursor connect to external systems as if they were local tools.

## Setup

1. Copy `mcp.json` to `~/.cursor/mcp.json` for every project. On Windows, `~` is your user profile folder. Or copy it to `.cursor/mcp.json` inside one project. Cursor merges the two files. A project entry wins over a global one with the same name.
2. Delete the entries you do not need. Each one starts a server.
3. Set the environment variables the entries read. `${env:NAME}` is Cursor's syntax for an environment variable. `${userHome}` is your home directory. For stdio servers, you can instead point an `envFile` field at a `.env` file.
4. Restart Cursor.
5. Check each server's toggle under **Customize > MCPs**. Connection errors appear in the Output panel (Cmd+Shift+U / Ctrl+Shift+U) under **MCP Logs**.

## Available Servers

### Linear (Project Management)
```json
{
  "linear": {
    "command": "npx",
    "args": ["-y", "mcp-remote", "https://mcp.linear.app/mcp"]
  }
}
```

**Use Cases:**
- Read and create issues
- Update issue status
- View project boards
- Sync development with tasks

### PostgreSQL (Database)

Runs through MCP Toolbox for Databases. The archived `@modelcontextprotocol/server-postgres` is deprecated.

```json
{
  "postgres": {
    "command": "npx",
    "args": ["-y", "@toolbox-sdk/server", "--prebuilt=postgres", "--stdio"],
    "env": {
      "POSTGRES_HOST": "${env:POSTGRES_HOST}",
      "POSTGRES_PORT": "5432",
      "POSTGRES_DATABASE": "${env:POSTGRES_DATABASE}",
      "POSTGRES_USER": "${env:POSTGRES_USER}",
      "POSTGRES_PASSWORD": "${env:POSTGRES_PASSWORD}"
    }
  }
}
```

**Use Cases:**
- Run SQL queries from chat
- Analyze query performance
- Generate migration scripts
- Debug data issues

**Example Prompts:**
- "Find the slowest queries hitting the orders table"
- "Show me the schema for the users table"
- "Suggest an index for this query pattern"

### GitHub (Repository)

Connects to GitHub's official hosted MCP server. The archived `@modelcontextprotocol/server-github` is deprecated. A Docker image (`ghcr.io/github/github-mcp-server`) is also available for local or GitHub Enterprise use.

```json
{
  "github": {
    "url": "https://api.githubcopilot.com/mcp/",
    "headers": {
      "Authorization": "Bearer ${env:GITHUB_PAT}"
    }
  }
}
```

Cursor identifies a remote server by its `url`. There is no `type` field to set.

**Use Cases:**
- Read repository files
- Create and manage issues
- View PR history
- Search code across repos

### Figma (Design)

This entry runs the community Framelink server (`figma-developer-mcp`). It reads a Figma personal access token from `FIGMA_API_KEY`. Figma also publishes its own MCP server. See Figma's documentation if you prefer that.

```json
{
  "figma": {
    "command": "npx",
    "args": ["-y", "figma-developer-mcp", "--stdio"],
    "env": {
      "FIGMA_API_KEY": "${env:FIGMA_API_KEY}"
    }
  }
}
```

**Use Cases:**
- Fetch design specifications
- Generate UI components from designs
- Extract colors and typography
- Sync design tokens

### Memory Bank (Persistence)
This entry supports the Memory Bank pattern from Section 7.2. The server keeps a knowledge graph in a `.jsonl` file named by `MEMORY_FILE_PATH`.

```json
{
  "memory": {
    "command": "npx",
    "args": ["-y", "@itseasy21/mcp-knowledge-graph"],
    "env": {
      "MEMORY_FILE_PATH": "${userHome}/.cursor/memory.jsonl"
    }
  }
}
```

**Use Cases:**
- Remember decisions across sessions
- Store architectural context
- Track project preferences
- Build knowledge graph

## Creating Custom MCP Servers

### Basic Structure

The TypeScript SDK's `McpServer` registers each tool with a zod input schema.

1. Run `npm install @modelcontextprotocol/sdk zod`.
2. Set `"type": "module"` in `package.json` so top-level `await` works.
3. Start from this structure:

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({ name: "my-server", version: "1.0.0" });

server.registerTool(
  "my_tool",
  {
    description: "Description of what this tool does",
    inputSchema: { param: z.string().describe("Parameter description") },
  },
  async ({ param }) => ({
    content: [{ type: "text", text: `You sent: ${param}` }],
  }),
);

const transport = new StdioServerTransport();
await server.connect(transport);
```

For a complete, tested project, see Part 4 of [`chapter-08/hands-on-lab/exercises/exercise-3-mcp.md`](../../../../chapter-08/hands-on-lab/exercises/exercise-3-mcp.md). It covers package setup, `tsconfig.json`, the build, and an end-to-end check against a running API.

### Testing with Inspector
```bash
npx @modelcontextprotocol/inspector node dist/index.js
```

## Security Considerations

1. **Least Privilege**: Only enable servers you need
2. **Read-Only by Default**: Start with read-only access
3. **Token Scoping**: Use minimal token permissions
4. **Environment Variables**: Never hardcode credentials
5. **Network Isolation**: Use VPN for sensitive databases

## Troubleshooting

### Server Not Connecting
1. Check environment variables are set
2. Verify npx can access the package
3. Check the Output panel's **MCP Logs** for errors
4. Test server independently first

### Permission Errors
1. Verify token has required scopes
2. Check network/firewall rules
3. Ensure server binary is executable

### Performance Issues
1. Increase server timeout
2. Check database connection pooling
3. Monitor memory usage
