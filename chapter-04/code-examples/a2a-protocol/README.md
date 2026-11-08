# A2A Protocol Examples

This directory holds the Agent-to-Agent (A2A) protocol configuration examples from Chapter 4.

> **Note (as of November 7, 2026).** A2A was contributed by Google. The Linux Foundation stewards it as a hosted project of the Agentic AI Foundation (AAIF), alongside MCP and AGENTS.md. Its technical steering committee has nine seats, held by AWS, Bloomberg, Cisco, Google, IBM, Microsoft, Salesforce, SAP, and ServiceNow. The project's [GOVERNANCE.md](https://github.com/a2aproject/A2A/blob/main/GOVERNANCE.md) has the current list. The specification lives at [a2a-protocol.org](https://a2a-protocol.org/).

When to use A2A and why: Chapter 4, Section 4.2.

> **Two files, two purposes.**
>
> - `agent-card.json` is Listing 4-2 from the book. It is a spec-conformant A2A Agent Card that follows the specification's AgentCard schema.
> - `agent_manifest_governance.json` is an extended teaching manifest written for this repo. It adds input and output schemas per capability, pricing, SLAs, `trust_score`, and an interaction endpoint. The spec does *not* mandate those fields.
>
> Before you publish a real Agent Card, take the structure from the spec. Every hostname and registry URL below is a placeholder.

## Files in This Directory

| File | Description | Source |
|------|-------------|--------|
| `agent-card.json` | Spec-conformant A2A Agent Card for a security review agent | Listing 4-2 |
| `agent_manifest_governance.json` | Extended manifest: capability schemas, pricing, governance metadata beyond the spec | Extended example |
| `discovery.json` | Registry and direct discovery configuration | Extended example |

## Agent Card Structure (the spec shape, Listing 4-2)

Serve the Agent Card (agent-card.json) from the well-known discovery path: `https://{domain}/.well-known/agent-card.json`. Its fields:

| Fields | What they hold |
|--------|----------------|
| `name`, `description`, `version` | Who the agent is |
| `supportedInterfaces` | How to reach it: endpoint URL, protocol binding, protocol version |
| `capabilities`, `defaultInputModes`, `defaultOutputModes` | What modes it speaks |
| `skills` | The work the agent accepts |

```json
{
  "name": "Security Review Agent",
  "description": "...",
  "version": "1.0.0",
  "supportedInterfaces": [ ... ],
  "capabilities": { "streaming": true },
  "defaultInputModes": ["text/plain", "application/json"],
  "defaultOutputModes": ["text/plain", "application/json"],
  "skills": [ ... ]
}
```

See `agent-card.json` for the complete card. See the [A2A specification](https://a2a-protocol.org/) for the authoritative field list.

## The Extended Governance Manifest

The next sections describe `agent_manifest_governance.json`, the repo's extended teaching manifest. The spec does not mandate this shape. Its top-level sections:

```jsonc
{
  "manifest_version": "1.0.0",
  "protocol": { ... },      // A2A protocol details
  "identity": { ... },      // Agent identification
  "capabilities": [ ... ],  // What the agent can do
  "governance": { ... },    // Compliance and SLAs
  "interaction": { ... }    // How to call the agent
}
```

## Capability Definition

Each capability in the extended manifest defines one task the agent can perform:

```json
{
  "id": "task_scan_security",
  "name": "Security Vulnerability Scan",
  "description": "Performs deep static analysis of code artifacts.",
  "input_schema": {
    "type": "object",
    "properties": {
      "repository_url": { "type": "string", "format": "uri" },
      "branch": { "type": "string", "default": "main" },
      "severity_threshold": {
        "type": "string",
        "enum": ["Low", "Medium", "High", "Critical"]
      }
    },
    "required": ["repository_url"]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "vulnerabilities_found": { "type": "integer" },
      "report_url": { "type": "string", "format": "uri" },
      "risk_score": { "type": "number", "minimum": 0, "maximum": 10 }
    }
  },
  "pricing": {
    "unit": "per_scan",
    "amount": 0.05,
    "currency": "USD"
  }
}
```

## Governance Section

The governance section of the extended manifest:

```json
{
  "governance": {
    "compliance": ["SOC2", "GDPR", "EU-AI-Act-Minimal-Risk"],
    "sla": {
      "max_latency_ms": 5000,
      "uptime_guarantee": 0.999
    },
    "data_retention_policy": "ephemeral",
    "trust_score": 0.98
  }
}
```

### Compliance Standards

| Standard | Description |
|----------|-------------|
| SOC2 | SOC 2 (System and Organization Controls 2), the AICPA audit report on security controls |
| GDPR | General Data Protection Regulation |
| EU-AI-Act-Minimal-Risk | The system falls in the EU AI Act's minimal-risk category (the Act names risk categories: unacceptable, high, limited, minimal; it has no numbered tiers) |
| HIPAA | Health Insurance Portability and Accountability Act |
| PCI-DSS | Payment Card Industry Data Security Standard |

### Data Retention Policies

| Policy | Meaning |
|--------|---------|
| `ephemeral` | Data deleted immediately after processing |
| `session` | Data retained for session duration only |
| `30-days` | Data retained for 30 days |
| `compliance` | Data retained per regulatory requirements |

## Authentication Configuration

The interaction section defines how to authenticate:

```json
{
  "interaction": {
    "endpoint": "https://api.securityops.example.com/v1/a2a",
    "auth": {
      "type": "OAuth2",
      "grant_type": "client_credentials",
      "scopes": ["agent_invoke", "report_read"]
    }
  }
}
```

### Supported Auth Types

| Type | What it is |
|------|------------|
| `OAuth2` | OAuth 2.0 with token refresh |
| `API_Key` | A static key |
| `mTLS` | Mutual certificate auth |
| `JWT` | Stateless token-based authentication |

## Agent Discovery

Agents find each other through a registry or a direct query.

### Registry-Based Discovery

```json
{
  "discovery": {
    "method": "registry",
    "registry_url": "https://registry.example.com/v1/agents",
    "search_criteria": {
      "capabilities": ["security_scan", "code_review"],
      "compliance": ["SOC2"],
      "min_trust_score": 0.95
    }
  }
}
```

### Direct Discovery

```json
{
  "discovery": {
    "method": "direct",
    "known_agents": [
      {
        "agent_id": "urn:agent:security-bot-v1",
        "endpoint": "https://api.securityops.example.com/.well-known/agent-card.json"
      }
    ]
  }
}
```

## Versioning

The spec card carries a `version` field. The extended manifest adds a `manifest_version`, so consumers can tell schema changes from agent changes:

```json
{
  "version": "1.0.0",
  "manifest_version": "1.0.0"
}
```

## Related Resources

- [A2A Protocol Specification](https://a2a-protocol.org/) ([repository](https://github.com/a2aproject/A2A)): the authority on Agent Card fields and discovery
- [Agentic AI Foundation](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation): the Linux Foundation formation announcement (Dec 2025), which names MCP and AGENTS.md among the anchor projects
- [A2A Integration Tutorial](../../tutorials/a2a-integration.md) in this chapter
- Chapter 10: Orchestrating Multiple AI Agents, which builds a running agent team
