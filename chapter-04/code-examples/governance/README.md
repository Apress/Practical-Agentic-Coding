# Governance Configuration Examples

This directory holds governance configuration examples for the AGILITY framework from Chapter 4.

AGILITY stands for Accountability, Governance, Integrity, Limitations, Intervention, Transparency, and Youth.

When to use AGILITY and why: Chapter 4, Section 4.4.

## Files in This Directory

| File | Description |
|------|-------------|
| `agility_config.json` | The AGILITY decisions for one agent as a single structured file, one block per pillar |
| `ai_robots.txt` | Agent access-control policy in robots.txt syntax (the Limitations pillar) |
| `decision_log_schema.json` | JSON Schema (draft 2020-12) for one decision-log entry, with a full example (the Governance pillar) |

> **No agent tool reads these files on its own.** `agility_config.json` and `ai_robots.txt` are planning and policy artifacts. Enforce what they say with the controls your tools do have (see each section below).

Chapter 12 turns the pillars into executable tests and guardrails ([chapter-12](../../../chapter-12/)).

## Using These Configurations

### 1. AGILITY Configuration

`agility_config.json` collects the decisions for all seven pillars in one file. Its `$schema` URL is a placeholder. An editor that fetches schemas will report that it cannot load it.

```json
{
  "agility": {
    "accountability": { ... },
    "governance": { ... },
    "integrity": { ... },
    "limitations": { ... },
    "intervention": { ... },
    "transparency": { ... },
    "youth": { ... }
  }
}
```

### 2. AI Robots.txt

`ai_robots.txt` is the access-control file for the Limitations pillar. Section 4.4 calls it ai.robots.txt. It uses robots.txt syntax:

```text
User-agent: *
Allow: /src/
Disallow: /infrastructure/
```

No coding agent reads this file on its own. Standard robots.txt (RFC 9309) defines only `User-agent`, `Allow`, and `Disallow`. The `Read-Only`, `Rate-Limit`, `Max-*`, and `Require-*` lines in this file are this repo's extensions.

Keep the file as the human-readable policy. Enforce it with the controls your tool has:

- Claude Code: permission deny rules and hooks (Chapter 8).
- Kiro: steering and hooks (Chapter 5).
- MCP filesystem server: directory arguments ([../mcp-config/](../mcp-config/)).

### 3. Decision Logging

Each log entry must validate against `decision_log_schema.json`. Here is a minimal valid entry. It has the six required fields plus reasoning and confidence:

```json
{
  "log_id": "550e8400-e29b-41d4-a716-446655440001",
  "timestamp": "2025-01-15T10:30:00Z",
  "agent_id": "urn:agent:code-reviewer-v1.2.3",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "action": { "type": "file_write", "target": "/app/src/services/order.py" },
  "reasoning": { "summary": "Added a None check before reading order.customer" },
  "confidence": 0.95,
  "signature": "sha256:a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
}
```

The schema's own `examples` array holds a fuller entry, with reasoning chain, risk assessment, outcome, and metrics.

To check an entry saved as `entry.json`, run this from this directory. Any draft 2020-12 validator works. This one uses the Python `jsonschema` package:

```bash
python3 -m venv .venv && source .venv/bin/activate   # Windows: py -m venv .venv, then .venv\Scripts\activate
pip install jsonschema
python -c "import json, jsonschema; jsonschema.validate(json.load(open('entry.json')), json.load(open('decision_log_schema.json'))); print('valid')"
```

It prints `valid`. Otherwise it stops with a `jsonschema.exceptions.ValidationError` that names the first problem, such as `'log_id' is a required property`.

## Implementation Checklist

Use this checklist when you implement AGILITY:

### Accountability
- [ ] Designated human sponsor for each agent
- [ ] Clear escalation path documented
- [ ] Liability boundaries established
- [ ] Approval workflows defined

### Governance
- [ ] Decision logging enabled for every action
- [ ] Logs are immutable (append-only)
- [ ] Monitoring and alerting configured
- [ ] Anomaly detection active

### Integrity
- [ ] Agent versions pinned
- [ ] Checksums verified on deployment
- [ ] Model provenance tracked
- [ ] Signed deployments required

### Limitations
- [ ] Allowed paths explicitly defined
- [ ] Prohibited paths enforced
- [ ] Resource limits set (time, cost, files)
- [ ] ai.robots.txt in place

### Intervention
- [ ] Emergency stop tested and working
- [ ] Least privilege enforced
- [ ] Timeout guarantees met
- [ ] Rollback procedures documented

### Transparency
- [ ] Decision explanations enabled
- [ ] Audit trail searchable
- [ ] Reports exportable
- [ ] Reasoning chains logged

### Youth (Continuous Improvement)
- [ ] Update pipeline defined
- [ ] Automatic rollback tested
- [ ] Feedback loops active
- [ ] Model update approval process

## Related Resources

- [Governance Tutorial](../../tutorials/governance-guide.md)
- [Kiro Steering Example](../rules-files/steering-code-quality.md)
- [AGENTS_enterprise.md](../agents-md/AGENTS_enterprise.md)
- Chapter 4, Section 4.4: Governance and Responsible AI Frameworks
