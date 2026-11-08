# A2A Agent Cards: quick reference

**Time Required**: 25-35 minutes
**Difficulty**: Intermediate
**Prerequisites**: Completed MCP Setup tutorial, familiarity with JSON Schema

> **Two file shapes. Know which one you are editing.**
>
> - **The spec Agent Card** (Listing 4-2 in the book, shipped as [`agent-card.json`](../code-examples/a2a-protocol/agent-card.json)) follows the A2A specification's AgentCard schema. It is the wire format. Publish this one.
> - **The extended manifest** (shipped as [`agent_manifest_governance.json`](../code-examples/a2a-protocol/agent_manifest_governance.json)) is a teaching model. It is not the wire format. Some of its fields (`trust_score`, `pricing`) are not in the specification.
>
> A2A is stewarded by the Linux Foundation. [a2a-protocol.org](https://a2a-protocol.org/) is the authority on the actual field names, the well-known discovery path, and the transport. Take your schema from the spec. Every hostname and registry URL below is a placeholder.

When to use A2A and why: Chapter 4, Section 4.2.

For the latest field list, see the [A2A specification](https://a2a-protocol.org/).

## What you build

1. A spec Agent Card.
2. An extended manifest with capability schemas, governance metadata, and authentication.

## Step 1: Start with the spec Agent Card (Listing 4-2)

The spec Agent Card, in the shape of the book's Listing 4-2:

```json
{
  "name": "Security Review Agent",
  "description": "Reviews code changes for defects and security vulnerabilities.",
  "version": "1.0.0",
  "supportedInterfaces": [
    { "url": "https://security-review-agent.example.com/a2a/v1", "protocolBinding": "JSONRPC", "protocolVersion": "1.0" }
  ],
  "capabilities": { "streaming": true },
  "defaultInputModes": ["text/plain", "application/json"],
  "defaultOutputModes": ["text/plain", "application/json"],
  "skills": [
    { "id": "security-review", "name": "Security Review", "description": "Analyzes a code change and returns prioritized security findings.", "tags": ["code-review", "security"] }
  ]
}
```

Publish it at the spec's discovery path: `https://{domain}/.well-known/agent-card.json`. Peer agents look for it there. The `skills` array lists the work the agent offers.

The remaining steps build the extended manifest. Its top-level sections:

```jsonc
{
  "manifest_version": "1.0.0",
  "protocol": { ... },      // A2A protocol details
  "identity": { ... },      // Who the agent is
  "capabilities": [ ... ],  // What it can do
  "governance": { ... },    // Compliance and SLAs
  "interaction": { ... }    // How to call it
}
```

## Step 2: Define agent identity

Create `agent_manifest.json` with identity information:

```json
{
  "manifest_version": "1.0.0",
  "protocol": {
    "name": "A2A",
    "version": "1.0",
    "handshake_type": "standard_discovery"
  },
  "identity": {
    "agent_id": "urn:agent:my-code-reviewer-v1",
    "name": "CodeReviewer",
    "description": "Automated code review agent focusing on Python best practices and common bugs.",
    "owner": "Your Team Name",
    "contact": "team-email@example.com"
  }
}
```

### Identity field reference

| Field | Required | Description |
|-------|----------|-------------|
| `agent_id` | Yes | Unique URN identifier (format: `urn:agent:name-version`) |
| `name` | Yes | Human-readable agent name |
| `description` | Yes | What the agent does |
| `owner` | Yes | Team or organization responsible |
| `contact` | Yes | Email or contact method |

## Step 3: Define capabilities

Each capability has:

- An input schema (what it accepts).
- An output schema (what it returns).
- Optional pricing information.

```json
{
  "manifest_version": "1.0.0",
  "protocol": {
    "name": "A2A",
    "version": "1.0",
    "handshake_type": "standard_discovery"
  },
  "identity": {
    "agent_id": "urn:agent:code-reviewer-v1",
    "name": "CodeReviewer",
    "description": "Automated code review agent.",
    "owner": "Your Team",
    "contact": "team@example.com"
  },
  "capabilities": [
    {
      "id": "task_review_code",
      "name": "Code Review",
      "description": "Reviews Python code for best practices, bugs, and security issues.",
      "input_schema": {
        "type": "object",
        "properties": {
          "code": {
            "type": "string",
            "description": "The source code to review"
          },
          "language": {
            "type": "string",
            "enum": ["python", "javascript", "typescript"],
            "default": "python"
          },
          "review_type": {
            "type": "string",
            "enum": ["quick", "thorough", "security-focused"],
            "default": "thorough"
          }
        },
        "required": ["code"]
      },
      "output_schema": {
        "type": "object",
        "properties": {
          "issues": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "severity": { "type": "string" },
                "line": { "type": "integer" },
                "message": { "type": "string" },
                "suggestion": { "type": "string" }
              }
            }
          },
          "overall_score": {
            "type": "number",
            "minimum": 0,
            "maximum": 10
          },
          "summary": { "type": "string" }
        }
      }
    }
  ]
}
```

## Step 4: Add governance information

```json
{
  "manifest_version": "1.0.0",
  "protocol": { ... },
  "identity": { ... },
  "capabilities": [ ... ],
  "governance": {
    "compliance": ["SOC2", "GDPR"],
    "sla": {
      "max_latency_ms": 10000,
      "uptime_guarantee": 0.99
    },
    "data_retention_policy": "ephemeral",
    "trust_score": 0.95
  }
}
```

### Governance fields

| Field | Description |
|-------|-------------|
| `compliance` | Array of compliance standards (SOC2, GDPR, HIPAA, etc.) |
| `sla.max_latency_ms` | Maximum response time in milliseconds |
| `sla.uptime_guarantee` | Uptime percentage (0.99 = 99%) |
| `data_retention_policy` | How long data is kept (ephemeral, session, 30-days) |
| `trust_score` | Computed trust score from 0 to 1 |

### `data_retention_policy` values

| Policy | Meaning |
|--------|---------|
| `ephemeral` | Deleted immediately |
| `session` | Retained for session only |
| `30-days` | Retained for 30 days |
| `compliance` | Per regulatory requirements |

## Step 5: Configure authentication

```json
{
  "manifest_version": "1.0.0",
  "protocol": { ... },
  "identity": { ... },
  "capabilities": [ ... ],
  "governance": { ... },
  "interaction": {
    "endpoint": "https://api.example.com/v1/a2a",
    "auth": {
      "type": "OAuth2",
      "grant_type": "client_credentials",
      "scopes": ["agent_invoke", "report_read"]
    }
  }
}
```

### Authentication types

| Type | Configuration |
|------|---------------|
| `OAuth2` | `grant_type`, `scopes` |
| `API_Key` | `header_name` (default: X-API-Key) |
| `mTLS` | Certificate configuration |
| `JWT` | `issuer`, `audience` |

**API Key example:**
```json
"auth": {
  "type": "API_Key",
  "header_name": "X-Agent-API-Key"
}
```

**JWT example:**
```json
"auth": {
  "type": "JWT",
  "issuer": "https://auth.example.com",
  "audience": "agent-api"
}
```

## Step 6: Add discovery

### Registry-based discovery

```json
{
  "discovery": {
    "method": "registry",
    "registry_url": "https://registry.example.com/v1/agents",
    "search_criteria": {
      "capabilities": ["code_review", "security_scan"],
      "compliance": ["SOC2"],
      "min_trust_score": 0.9
    }
  }
}
```

### Direct discovery

```json
{
  "discovery": {
    "method": "direct",
    "known_agents": [
      {
        "agent_id": "urn:agent:security-bot-v1",
        "endpoint": "https://api.securityops.example.com/.well-known/agent-card.json"
      },
      {
        "agent_id": "urn:agent:docs-generator-v2",
        "endpoint": "https://docs-generator.example.com/.well-known/agent-card.json"
      }
    ]
  }
}
```

## Step 7: Compare with the complete files

1. Open [`agent_manifest_governance.json`](../code-examples/a2a-protocol/agent_manifest_governance.json). It is a complete extended manifest for a security review agent.
2. Open [`agent-card.json`](../code-examples/a2a-protocol/agent-card.json). It describes the same agent in the wire format.
3. Open [`discovery.json`](../code-examples/a2a-protocol/discovery.json) for the discovery configuration.

## Verification checklist

- [ ] Read the spec Agent Card in `agent-card.json` and can name its required fields
- [ ] Created a complete extended manifest file
- [ ] Defined at least one capability with input/output schemas
- [ ] Added governance information (compliance, SLAs)
- [ ] Configured authentication method
- [ ] Validated JSON syntax: `python -m json.tool agent_manifest.json` prints the file back, reformatted, when it parses

## Common mistake

An input schema with no `"required"` array. Add one next to `"properties"`, for example `"required": ["code"]`.

## Next steps

1. **Exercise 2**: [Create an A2A Agent Card](../exercises/exercise-2-agent-card.md)
2. **Tutorial**: [AGENTS.md Creation Guide](./agents-md-guide.md)
3. **Multi-agent work**: Chapter 10 builds a running agent team.

## Reference

- [A2A Protocol Specification](https://a2a-protocol.org/) ([repository](https://github.com/a2aproject/A2A))
- [Agentic AI Foundation](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation): the Linux Foundation formation announcement (Dec 2025), which names MCP and AGENTS.md among the anchor projects
- [Code Example: agent-card.json](../code-examples/a2a-protocol/agent-card.json) (Listing 4-2, spec-conformant)
- [Code Example: agent_manifest_governance.json](../code-examples/a2a-protocol/agent_manifest_governance.json) (extended teaching manifest)
- [Code Example: discovery.json](../code-examples/a2a-protocol/discovery.json)
