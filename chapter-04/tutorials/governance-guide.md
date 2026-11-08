# AGILITY controls: quick reference

**Time Required**: 25-35 minutes
**Difficulty**: Intermediate
**Prerequisites**: Understanding of AGENTS.md, basic security concepts

> **No agent tool reads these files on its own.** `agility_config.json` and `ai.robots.txt` record your policy. Enforce it with your tool's permission rules, hooks, or MCP server arguments. See the [governance README](../code-examples/governance/README.md).

What the AGILITY pillars mean and why each one matters: Chapter 4, Section 4.4.

## What you build

One governance control per AGILITY pillar, written down in your repository.

| Pillar | What you write | Repo file to start from |
|--------|----------------|-------------------------|
| Accountability | A `GOVERNANCE.md` section naming the human sponsor | This guide, Pillar 1 |
| Governance | Decision-log entries that validate against a schema | [`decision_log_schema.json`](../code-examples/governance/decision_log_schema.json) |
| Integrity | Version pins and checksums for the agent | [`agility_config.json`](../code-examples/governance/agility_config.json) |
| Limitations | Allowed and prohibited actions, plus `ai.robots.txt` | [`ai_robots.txt`](../code-examples/governance/ai_robots.txt) |
| Intervention | An emergency stop and access controls | This guide, Pillar 5 |
| Transparency | Explanation and audit-trail settings | [`agility_config.json`](../code-examples/governance/agility_config.json) |
| Youth | An update pipeline with rollback | [`agility_config.json`](../code-examples/governance/agility_config.json) |

## Pillar 1: Accountability (A)

Add a responsibility chain to your project:

```markdown
# GOVERNANCE.md

## Accountability

### Human Sponsor
- **Name**: Jane Smith, Principal Engineer
- **Contact**: jane.smith@example.com
- **Escalation**: +1-555-0123 (for critical incidents)

### Responsibility Scope
- The human sponsor accepts ultimate liability for agent actions
- All production changes require sponsor approval
- Financial transactions over $1000 require dual approval

### Incident Response
1. Agent is immediately halted
2. Human sponsor is notified within 5 minutes
3. Post-incident review within 24 hours
```

## Pillar 2: Governance (G)

1. Write one decision-log entry per agent action.
2. Validate each entry against [`decision_log_schema.json`](../code-examples/governance/decision_log_schema.json).

The validation command is in the governance README, under [Decision Logging](../code-examples/governance/README.md#3-decision-logging).

## Pillar 3: Integrity (I)

Fill in the `integrity` block of [`agility_config.json`](../code-examples/governance/agility_config.json). It has four parts: `agent_identity`, `model_provenance`, `data_verification`, and `supply_chain`.

## Pillar 4: Limitations (L)

### In AGENTS.md

```markdown
## Limitations

### Allowed Actions
- Read files in `/src`, `/tests`, `/docs`
- Write files in `/src`, `/tests`
- Run commands: `pytest`, `make format`, `make lint`
- Create branches matching pattern: `agent/*`

### Prohibited Actions
- Modify files in `/infrastructure`, `/security`, `/billing`
- Access `.env*` files
- Run destructive commands: `rm -rf`, `drop table`, etc.
- Push directly to `main` or `release/*` branches
- Access external URLs not in allowlist

### Resource Limits
- Max 50 files modified per session
- Max 1000 lines changed per file
- Max 30 minutes runtime per task
- Max $10 API cost per task
```

### In ai.robots.txt

Create an `ai.robots.txt` file to define agent access. No agent tool reads this file natively (see the note at the top). The repo's version is [`ai_robots.txt`](../code-examples/governance/ai_robots.txt).

```text
# ai.robots.txt - Agent Access Control

User-agent: *
Allow: /src/
Allow: /tests/
Allow: /docs/

Disallow: /infrastructure/
Disallow: /security/
Disallow: /billing/
Disallow: /.env*
Disallow: /**/secrets/
Disallow: /**/*.pem
Disallow: /**/*.key

# Specific agent permissions
User-agent: code-reviewer-agent
Allow: /src/
Allow: /tests/
Disallow: /src/auth/

User-agent: docs-agent
Allow: /docs/
Disallow: /src/
```

## Pillar 5: Intervention (I)

Record the emergency stop and access controls:

```json
{
  "intervention": {
    "emergency_stop": {
      "enabled": true,
      "methods": [
        {
          "type": "api",
          "endpoint": "/api/v1/agents/{agent_id}/stop",
          "auth": "admin_token"
        },
        {
          "type": "cli",
          "command": "agent-ctl stop --agent-id {agent_id} --force"
        },
        {
          "type": "ui",
          "location": "Dashboard > Agents > Kill Switch"
        }
      ],
      "timeout_ms": 1000,
      "fallback": "kill_process"
    },
    "access_control": {
      "least_privilege": true,
      "permission_escalation": "requires_approval",
      "temporary_permissions": {
        "max_duration_minutes": 60,
        "audit_required": true
      }
    }
  }
}
```

## Pillar 6: Transparency (T)

Fill in the `transparency` block of [`agility_config.json`](../code-examples/governance/agility_config.json). It has three parts: `explainability`, `audit_trail`, and `reporting`.

## Pillar 7: Youth (Y)

Fill in the `youth` block of [`agility_config.json`](../code-examples/governance/agility_config.json). It has four parts: `continuous_improvement`, `update_pipeline`, `model_updates`, and `policy_updates`.

## Verification checklist

### Accountability
- [ ] Human sponsor designated
- [ ] Escalation path documented
- [ ] Approval workflows defined

### Governance
- [ ] Decision logging enabled for every action
- [ ] Logs are immutable
- [ ] Monitoring and alerting configured

### Integrity
- [ ] Agent versions pinned
- [ ] Checksums verified
- [ ] Deployments signed

### Limitations
- [ ] Allowed/prohibited paths defined
- [ ] Resource limits set
- [ ] ai.robots.txt created

### Intervention
- [ ] Emergency stop tested
- [ ] Least privilege enforced
- [ ] Access controls documented

### Transparency
- [ ] Decision explanations enabled
- [ ] Audit trail searchable
- [ ] Reports exportable

### Youth
- [ ] Update pipeline defined
- [ ] Rollback tested
- [ ] Feedback loops active

## Next steps

1. **Apply it to your project**: add the AGILITY controls to your AGENTS.md.
2. **Exercise 1**: [Create MCP Configuration](../exercises/exercise-1-mcp-config.md). Its bonus challenges add governance annotations to the servers.
3. **Chapter 5**: Amazon Kiro steering files.
4. **Chapter 12**: Security, privacy, and ethics. There AGILITY becomes executable tests.

## Reference

- Chapter 4, Section 4.4: Governance and Responsible AI Frameworks
- [Code Example: agility_config.json](../code-examples/governance/agility_config.json)
- [Code Example: steering-code-quality.md](../code-examples/rules-files/steering-code-quality.md)
- [AGENTS_enterprise.md](../code-examples/agents-md/AGENTS_enterprise.md)
