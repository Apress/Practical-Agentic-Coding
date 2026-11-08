# MCP Configuration Examples

This directory holds example MCP (Model Context Protocol) server configurations for Kiro.

When to use MCP servers and why: Chapter 5, Section 5.6.

> **Server changes since the book.**
>
> - The AWS Diagram MCP server is retired. See [AWS MCP Servers](#aws-mcp-servers).
> - The Model Context Protocol project has archived several reference servers. These files use the maintained successors. See [Available Examples](#available-examples).
> - As of November 7, 2026, the filesystem and memory servers need Node.js 24 or later.

## Overview

These configs register external tools and data sources with Kiro over MCP. Once a server is up, ask for what you need in chat. Do not paste schemas into the conversation.

**Example**: "Use local-db to describe the user table."

Kiro routes the request through the server on its own.

## Configuration Location

MCP servers are configured in `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "command-to-run",
      "args": ["arg1", "arg2"],
      "description": "What this server provides"
    }
  }
}
```

## Available Examples

| File | Description | Prerequisites |
|------|-------------|---------------|
| `local-database.json` | Local PostgreSQL via MCP Toolbox for Databases, plus a read-only variant | Node.js and npm; `POSTGRES_*` environment variables set |
| `aws-services.json` | The four AWS MCP servers from the lab's Phase 6 list that AWS offers | `uv` installed (`pip install uv`), AWS credentials configured |
| `development-tools.json` | Filesystem, GitHub, memory, search (Brave), and browser-automation (Playwright) servers | Node.js and npm (24 or later for the filesystem and memory servers, as of November 7, 2026); Docker for the GitHub server; some entries need API keys |

None of these files are drop-in. Each has placeholders you must replace, such as a project path, database connection details, a region, or an API key. Copy the entries you need into `.kiro/settings/mcp.json` and edit them. Do not replace that file wholesale.

The Model Context Protocol project has archived its reference servers for Postgres, GitHub, Slack, Brave Search, Puppeteer, and others. npm marks those packages deprecated. Listing 5-1 and these files use the maintained successors:

- MCP Toolbox for Databases, for Postgres
- GitHub's official server
- Brave's own search server
- Microsoft's Playwright server, for browser automation

Package names change. Check the MCP registry before you wire one in.

Kiro only expands environment variables you have approved. When a server's `env` block references one, such as `${POSTGRES_PASSWORD}`, Kiro shows a warning. Add the variable under **Mcp Approved Env Vars** in Kiro settings.

## AWS MCP Servers

AWS provides official MCP servers at [awslabs.github.io/mcp](https://awslabs.github.io/mcp).

### Recommended AWS MCP Servers

| Server | Purpose | Documentation |
|--------|---------|---------------|
| AWS API | Direct AWS API access (superseded by the AWS MCP Server) | [Link](https://awslabs.github.io/mcp/servers/aws-api-mcp-server) |
| AWS Knowledge | AWS best practices; a remote server at `https://knowledge-mcp.global.api.aws` | [Link](https://awslabs.github.io/mcp/servers/aws-knowledge-mcp-server) |
| AWS Documentation | AWS docs search | [Link](https://awslabs.github.io/mcp/servers/aws-documentation-mcp-server) |
| Aurora Postgres | Database operations; you name the cluster or endpoint in chat | [Link](https://awslabs.github.io/mcp/servers/postgres-mcp-server) |
| AWS Diagram | Retired: every PyPI release is yanked and its documentation page is gone | None |

In place of the retired diagram server, AWS offers a diagram skill in its [deploy-on-aws agent plugin](https://github.com/awslabs/agent-plugins/tree/main/plugins/deploy-on-aws). That plugin targets Claude Code, Codex, and Cursor. Its README describes Kiro support as experimental, through a third-party converter. For the lab, use Mermaid diagrams in `design.md`.

Do not install the PyPI package named `awslabs.aws-knowledge-mcp-server`. Its only release is yanked with the reason "Not ours". The AWS Knowledge server has no local package. Connect to its URL, as `aws-services.json` does.

## Prerequisites

### Node.js and npm

The local database server and most development-tool servers launch through `npx`:

```bash
node --version
npx --version
```

### Docker (for the GitHub server)

The GitHub server in `development-tools.json` runs GitHub's official image. Before Kiro starts the server, check that the daemon is up and pull the image:

```bash
docker ps
docker pull ghcr.io/github/github-mcp-server
```

### uv (for the AWS servers)

The AWS MCP servers in `aws-services.json` launch through `uvx`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # macOS and Linux
uvx --version
```

On Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`. Homebrew (`brew install uv`) and `pipx install uv` also work. See docs.astral.sh/uv for every option.

On Windows, AWS documents a different launch form for these servers: `"command": "uv"` with `"args": ["tool", "run", "--from", "<package>@latest", "<package>.exe"]`. Each server's page at awslabs.github.io/mcp shows its Windows block.

### AWS Credentials

Most AWS MCP servers need credentials. Configure a profile and check that it resolves:

```bash
aws configure
aws sts get-caller-identity
```

Use a named profile, not environment variables. Put the profile name in the server's `env` block:

- `AWS_API_MCP_PROFILE_NAME` for the AWS API server
- `AWS_PROFILE` for the others

Never put an access key in `mcp.json`. That file gets committed.

## Troubleshooting

### Common Issues

| Issue | What to check |
|-------|---------------|
| Docker daemon not running | Start Docker Desktop, then `docker ps` |
| Permission denied on the Docker socket | On Linux, add yourself to the `docker` group and re-login |
| Connection refused from the database server | The database is actually running, and the `POSTGRES_*` host, port, and database values are right |
| Invalid or missing AWS credentials | `aws sts get-caller-identity` succeeds, and the profile named in the server's `env` block exists |
| `uvx: command not found` | `pip install uv`, and `uvx` is on the PATH Kiro sees |
| Server shows red in the MCP panel | Read the server's own stderr in the panel, then paste it into Kiro Chat |

### Getting Help

Use Kiro Chat to troubleshoot MCP issues:

```text
Help me configure the AWS API MCP Server for us-east-1 region.
```

Kiro can find and fix configuration problems.
