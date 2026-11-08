# Exercise 2: Create an A2A Agent Card

**Time Required**: 35-45 minutes
**Difficulty**: Intermediate
**Prerequisites**: Completed A2A Integration tutorial

## Learning Objectives

By completing this exercise, you will:
- Create a complete agent manifest (`security_agent.json`) from scratch
- Define capabilities with proper JSON Schema
- Configure governance and compliance settings
- Set up authentication for agent interactions

## Scenario

You are creating an Agent Card for a **Security Review Agent**. Other agents in your organization will use it. This agent specializes in:
- Static Application Security Testing (SAST)
- OWASP Top 10 vulnerability detection
- Dependency vulnerability scanning
- Security code review

The agent needs to:
- Accept repository URLs for scanning
- Return vulnerability reports with severity levels
- Comply with SOC2 and GDPR requirements
- Support OAuth2 authentication

> **A note on the schema.** This exercise builds the repo's *extended teaching manifest* (the shape in [`agent_manifest_governance.json`](../code-examples/a2a-protocol/agent_manifest_governance.json)). It is **not** the wire format.
>
> - Listing 4-2 in the book is a spec-conformant Agent Card, shipped as [`agent-card.json`](../code-examples/a2a-protocol/agent-card.json).
> - A2A is stewarded by the Linux Foundation. [a2a-protocol.org](https://a2a-protocol.org/) is the authority on real field names, the discovery path, and the transport.
> - When you publish, take the schema from the spec. Bonus Challenge 4 walks that translation.
>
> All hostnames here are placeholders.

## Step 1: Create the Basic Structure

Create a file named `security_agent.json`:

```jsonc
{
  "manifest_version": "1.0.0",
  "protocol": {
    // Protocol information
  },
  "identity": {
    // Agent identity
  },
  "capabilities": [
    // What the agent can do
  ],
  "governance": {
    // Compliance and SLAs
  },
  "interaction": {
    // How to call the agent
  }
}
```

## Step 2: Define Protocol and Identity

Fill in the protocol and identity sections:

**Requirements:**
- Protocol version: 1.0 (the A2A specification version that Listing 4-2's `protocolVersion` targets)
- Handshake type: standard_discovery
- Agent ID format: `urn:agent:security-reviewer-v1`
- Include owner and contact information

<details>
<summary>Hint (Click to expand)</summary>

```json
"protocol": {
  "name": "A2A",
  "version": "1.0",
  "handshake_type": "standard_discovery"
},
"identity": {
  "agent_id": "urn:agent:security-reviewer-v1",
  "name": "SecurityReviewer",
  "description": "...",
  "owner": "Security Team",
  "contact": "security@example.com"
}
```
</details>

## Step 3: Define the Security Scan Capability

Create a capability for security vulnerability scanning:

**Input Schema:**
- `repository_url` (required) - Git repository URL to scan
- `branch` (optional) - Branch to scan, default: "main"
- `severity_threshold` (optional) - Minimum severity to report: Low, Medium, High, Critical
- `scan_type` (optional) - Type of scan: sast, dependencies, full

**Output Schema:**
- `vulnerabilities_found` - Total count
- `critical_count` - Critical vulnerabilities
- `high_count` - High severity vulnerabilities
- `medium_count` - Medium severity vulnerabilities
- `low_count` - Low severity vulnerabilities
- `report_url` - URL to full report
- `risk_score` - 0-10 risk assessment
- `scan_duration_seconds` - How long the scan took

<details>
<summary>Hint: Input Schema (Click to expand)</summary>

```json
"input_schema": {
  "type": "object",
  "properties": {
    "repository_url": {
      "type": "string",
      "format": "uri",
      "description": "HTTPS URL of the Git repository to scan"
    },
    "branch": {
      "type": "string",
      "default": "main",
      "description": "Git branch to scan"
    },
    "severity_threshold": {
      "type": "string",
      "enum": ["Low", "Medium", "High", "Critical"],
      "default": "Medium",
      "description": "Minimum severity level to include in results"
    },
    "scan_type": {
      "type": "string",
      "enum": ["sast", "dependencies", "full"],
      "default": "full",
      "description": "Type of security scan to perform"
    }
  },
  "required": ["repository_url"]
}
```
</details>

<details>
<summary>Hint: Output Schema (Click to expand)</summary>

```json
"output_schema": {
  "type": "object",
  "properties": {
    "vulnerabilities_found": {
      "type": "integer",
      "description": "Total number of vulnerabilities found"
    },
    "critical_count": {
      "type": "integer"
    },
    "high_count": {
      "type": "integer"
    },
    "medium_count": {
      "type": "integer"
    },
    "low_count": {
      "type": "integer"
    },
    "report_url": {
      "type": "string",
      "format": "uri",
      "description": "URL to the full vulnerability report"
    },
    "risk_score": {
      "type": "number",
      "minimum": 0,
      "maximum": 10,
      "description": "Overall risk assessment score"
    },
    "scan_duration_seconds": {
      "type": "integer",
      "description": "Time taken to complete the scan"
    }
  }
}
```
</details>

## Step 4: Add a Second Capability

Add a capability for **OWASP Top 10 Assessment**:

**Capability Requirements:**
- ID: `task_owasp_assessment`
- Accepts: repository URL, compliance level (`basic`, `comprehensive`)
- Returns: compliance status, findings per OWASP category, recommendations

Design the input and output schemas yourself. Base them on what an OWASP assessment would need.

## Step 5: Configure Governance

Add governance settings:
- Compliance: SOC2, GDPR
- SLA: 60 second max latency, 99.9% uptime
- Data retention: ephemeral (deleted after processing)
- Trust score: 0.95

<details>
<summary>Hint (Click to expand)</summary>

```json
"governance": {
  "compliance": ["SOC2", "GDPR"],
  "sla": {
    "max_latency_ms": 60000,
    "uptime_guarantee": 0.999
  },
  "data_retention_policy": "ephemeral",
  "trust_score": 0.95
}
```
</details>

## Step 6: Configure Authentication

Set up OAuth2 authentication:
- Endpoint: `https://api.example.com/security/v1/a2a`
- Auth type: OAuth2
- Grant type: client_credentials
- Scopes: agent_invoke, scan_read, report_read

<details>
<summary>Hint (Click to expand)</summary>

```json
"interaction": {
  "endpoint": "https://api.example.com/security/v1/a2a",
  "auth": {
    "type": "OAuth2",
    "grant_type": "client_credentials",
    "scopes": ["agent_invoke", "scan_read", "report_read"]
  }
}
```
</details>

## Step 7: Add Pricing Information

Add pricing to your capabilities:
- Security scan: $0.10 per scan
- OWASP assessment: $0.25 per assessment

```json
"pricing": {
  "unit": "per_scan",
  "amount": 0.10,
  "currency": "USD"
}
```

## Expected Output

Your completed agent card should include:
- Complete protocol and identity sections
- At least two capabilities with full schemas
- Governance with compliance and SLAs
- OAuth2 authentication configuration
- Pricing for each capability

## Validation Checklist

Before submitting, verify:

- [ ] JSON is valid: `python -m json.tool security_agent.json` prints the file back, reformatted (an error names the line and column instead)
- [ ] All required fields are present in input schemas
- [ ] Output schemas define all expected return fields
- [ ] Governance includes compliance and SLA
- [ ] Authentication is properly configured
- [ ] Pricing is included for each capability
- [ ] Descriptions are clear and helpful

## Bonus Challenges

### Challenge 1: Add Dependency Scan Capability

Add a third capability for dependency vulnerability scanning. It:
- Accepts a `package.json`, `requirements.txt`, or `go.mod` file path
- Returns CVE details for vulnerable dependencies
- Includes severity and remediation suggestions

### Challenge 2: Add Discovery Configuration

Add a discovery section. Other agents use it to find your security agent:

```json
"discovery": {
  "methods": ["registry", "well-known"],
  "registry_registration": {
    "registry_url": "https://registry.example.com/v1/agents",
    "categories": ["security", "code-review", "compliance"],
    "tags": ["owasp", "sast", "vulnerability-scanning"]
  },
  "well_known": {
    "path": "/.well-known/agent-card.json"
  }
}
```

### Challenge 3: Add Multiple Authentication Methods

Support both OAuth2 and API Key authentication:

```json
"auth": {
  "methods": [
    {
      "type": "OAuth2",
      "grant_type": "client_credentials",
      "scopes": ["agent_invoke"]
    },
    {
      "type": "API_Key",
      "header_name": "X-Security-Agent-Key",
      "description": "For automated CI/CD pipelines"
    }
  ],
  "preferred": "OAuth2"
}
```

### Challenge 4: Translate Your Manifest into a Spec Agent Card

Rewrite your finished `security_agent.json` as a spec-conformant Agent Card in the shape of Listing 4-2 (see [`agent-card.json`](../code-examples/a2a-protocol/agent-card.json)). Use these fields:

- `name`, `description`, `version`
- `supportedInterfaces`
- `capabilities`, `defaultInputModes`, `defaultOutputModes`
- a `skills` array

Then check the result:

1. List what carries over: identity, endpoint, and what the agent can do (as skills).
2. List what does not: input/output schemas, pricing, `trust_score`.
3. Decide where the leftover information goes: your service documentation, contracts, or monitoring.

## Solution

<details>
<summary>Complete Solution (Click to expand)</summary>

```json
{
  "manifest_version": "1.0.0",
  "protocol": {
    "name": "A2A",
    "version": "1.0",
    "handshake_type": "standard_discovery"
  },
  "identity": {
    "agent_id": "urn:agent:security-reviewer-v1",
    "name": "SecurityReviewer",
    "description": "Autonomous security review agent specializing in SAST, OWASP Top 10 analysis, and dependency vulnerability scanning.",
    "owner": "Security Team",
    "contact": "security@example.com"
  },
  "capabilities": [
    {
      "id": "task_security_scan",
      "name": "Security Vulnerability Scan",
      "description": "Performs deep static analysis for security vulnerabilities including SAST and dependency scanning.",
      "input_schema": {
        "type": "object",
        "properties": {
          "repository_url": {
            "type": "string",
            "format": "uri",
            "description": "HTTPS URL of the Git repository to scan"
          },
          "branch": {
            "type": "string",
            "default": "main",
            "description": "Git branch to scan"
          },
          "severity_threshold": {
            "type": "string",
            "enum": ["Low", "Medium", "High", "Critical"],
            "default": "Medium",
            "description": "Minimum severity level to include in results"
          },
          "scan_type": {
            "type": "string",
            "enum": ["sast", "dependencies", "full"],
            "default": "full",
            "description": "Type of security scan to perform"
          }
        },
        "required": ["repository_url"]
      },
      "output_schema": {
        "type": "object",
        "properties": {
          "vulnerabilities_found": {
            "type": "integer",
            "description": "Total number of vulnerabilities found"
          },
          "critical_count": { "type": "integer" },
          "high_count": { "type": "integer" },
          "medium_count": { "type": "integer" },
          "low_count": { "type": "integer" },
          "report_url": {
            "type": "string",
            "format": "uri",
            "description": "URL to the full vulnerability report"
          },
          "risk_score": {
            "type": "number",
            "minimum": 0,
            "maximum": 10,
            "description": "Overall risk assessment score (0=safe, 10=critical)"
          },
          "scan_duration_seconds": {
            "type": "integer",
            "description": "Time taken to complete the scan"
          }
        }
      },
      "pricing": {
        "unit": "per_scan",
        "amount": 0.10,
        "currency": "USD"
      }
    },
    {
      "id": "task_owasp_assessment",
      "name": "OWASP Top 10 Assessment",
      "description": "Evaluates codebase against OWASP Top 10 security risks with detailed findings per category.",
      "input_schema": {
        "type": "object",
        "properties": {
          "repository_url": {
            "type": "string",
            "format": "uri",
            "description": "Git repository URL to assess"
          },
          "branch": {
            "type": "string",
            "default": "main"
          },
          "compliance_level": {
            "type": "string",
            "enum": ["basic", "comprehensive"],
            "default": "comprehensive",
            "description": "Depth of OWASP assessment"
          }
        },
        "required": ["repository_url"]
      },
      "output_schema": {
        "type": "object",
        "properties": {
          "overall_compliance": {
            "type": "string",
            "enum": ["compliant", "partial", "non-compliant"]
          },
          "categories": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "category": { "type": "string" },
                "status": { "type": "string" },
                "findings_count": { "type": "integer" },
                "recommendations": {
                  "type": "array",
                  "items": { "type": "string" }
                }
              }
            }
          },
          "report_url": {
            "type": "string",
            "format": "uri"
          }
        }
      },
      "pricing": {
        "unit": "per_assessment",
        "amount": 0.25,
        "currency": "USD"
      }
    }
  ],
  "governance": {
    "compliance": ["SOC2", "GDPR"],
    "sla": {
      "max_latency_ms": 60000,
      "uptime_guarantee": 0.999
    },
    "data_retention_policy": "ephemeral",
    "trust_score": 0.95
  },
  "interaction": {
    "endpoint": "https://api.example.com/security/v1/a2a",
    "auth": {
      "type": "OAuth2",
      "grant_type": "client_credentials",
      "scopes": ["agent_invoke", "scan_read", "report_read"]
    }
  }
}
```
</details>

## Common Mistakes to Avoid

1. **Missing required fields in schema**
   ```jsonc
   // WRONG - No "required" array
   "input_schema": {
     "type": "object",
     "properties": { ... }
   }

   // CORRECT
   "input_schema": {
     "type": "object",
     "properties": { ... },
     "required": ["repository_url"]
   }
   ```

2. **Vague descriptions**
   ```jsonc
   // WRONG
   "description": "Scans code"

   // CORRECT
   "description": "Performs deep static analysis for security vulnerabilities including SQL injection, XSS, and authentication bypass."
   ```

3. **Unrealistic SLAs**
   ```jsonc
   // WRONG - ML-based security scanning can't be this fast
   "sla": { "max_latency_ms": 100 }

   // CORRECT - Realistic for security scanning
   "sla": { "max_latency_ms": 60000 }
   ```

4. **Missing output schema fields**
   ```jsonc
   // WRONG - What does "result" contain?
   "output_schema": {
     "type": "object",
     "properties": {
       "result": { "type": "object" }
     }
   }

   // CORRECT - Explicit fields
   "output_schema": {
     "type": "object",
     "properties": {
       "vulnerabilities_found": { "type": "integer" },
       "risk_score": { "type": "number" },
       // ... all fields defined
     }
   }
   ```

## Next Steps

After completing this exercise:

1. **Validate JSON**: `python -m json.tool security_agent.json` (it prints the file back, or the line of the first syntax error)
2. **Exercise 3**: [Write an AGENTS.md File](./exercise-3-agents-md.md)
3. **Tutorial**: [AGENTS.md Creation Guide](../tutorials/agents-md-guide.md)

## Reference

- [A2A Integration Tutorial](../tutorials/a2a-integration.md)
- [Code Example: agent-card.json](../code-examples/a2a-protocol/agent-card.json) (Listing 4-2, spec-conformant)
- [Code Example: agent_manifest_governance.json](../code-examples/a2a-protocol/agent_manifest_governance.json) (extended teaching manifest, the shape this exercise uses)
- [Code Example: discovery.json](../code-examples/a2a-protocol/discovery.json)
