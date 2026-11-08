# Claude Code Features for the Challenge Labs

**Reference**: Chapter 8, Sections 8.3 and 8.4

Each challenge lab tells you what to build. This file gives the rule files, sub-agents, hooks, and MCP servers to use while you build it. It is organized by challenge.

What each feature is and when to use it: Chapter 8, Sections 8.3 and 8.4.

Notes on the hook examples:

- The `matcher` values use the string form (`"Bash"`, `"Edit|Write"`). That is what Claude Code reads.
- Timeouts are in seconds.
- A hook that is meant to stop something must exit 2. Any other non-zero exit is a non-blocking error, and the operation goes ahead.
- Reference scripts through `"$CLAUDE_PROJECT_DIR"` so they resolve after Claude changes directory.

---

## Feature Overview

| Feature | What It Does | When to Use |
|---------|--------------|-------------|
| **Constitutional Rules** | Define project standards Claude enforces | Set coding standards, security requirements, operational practices |
| **Specialized Agents** | Domain experts for focused work | Complex debugging, security audits, DevOps automation |
| **Validation Hooks** | Prevent issues before commit/deploy | Block secrets, run tests, validate config, scan security |
| **MCP Integrations** | Connect to external tools | Access production logs, manage secrets, deploy to K8s |

---

## Lab 1: Debugging Features

### Constitutional Rules for Debugging

**File**: `.claude/rules/debugging.md`

```markdown
# Debugging Standards

## Investigation Process
- Read relevant code before suggesting fixes
- Check logs for error messages and stack traces
- Query database to verify actual state
- Create minimal reproduction case

## Fix Requirements
- Include regression test with every fix
- Document root cause in commit message
- Run full test suite before committing
- Update documentation if behavior changes
```

**How to use:**
```text
# Claude automatically follows these rules
# Just ask: "Debug the approval endpoint issue"
```

### Specialized Agents for Debugging

**Debugger Agent** - Systematic bug investigation
```text
"Use the debugger agent to investigate why approval fails for draft responses.
Follow systematic approach: read code -> check database -> identify root cause."
```

**Error Detective Agent** - Pattern analysis across logs
```text
"Use the error-detective agent to analyze the last 1000 log entries.
Find error patterns, frequency, and common causes."
```

**Code Reviewer Agent** - Review fixes before commit
```text
"Use the code-reviewer agent to review my fix for the approval bug.
Check: correctness, test coverage, edge cases, documentation."
```

### Validation Hooks

**Pre-Commit Tests**

**File**: `.claude/hooks/pre-commit-tests.sh`

```bash
#!/bin/bash
# PreToolUse hook (matcher "Bash"): run the tests before any git commit
# Claude makes, and block the commit if they fail.
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# The matcher selects the tool, not the command, so gate on the text here
case "$COMMAND" in
    *"git commit"*) ;;
    *) exit 0 ;;
esac

echo "Running tests before commit..." >&2

# pytest.ini already enforces the 80% coverage floor on models/ and services/
if ! pytest tests/ -q --tb=short >&2; then
    echo "BLOCKED: tests fail; fix them before committing" >&2
    exit 2
fi

# Advisory until the existing strict-mypy errors are cleared
mypy models/ services/ api/ >&2 || echo "WARNING: mypy reports type errors" >&2

exit 0
```

**Configure**: Add to `.claude/settings.json`
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/pre-commit-tests.sh"
      }]
    }]
  }
}
```

### MCP for Debugging

**GitHub Issues MCP** - Track and link bugs
```text
"Search GitHub Issues for existing bugs related to 'approval endpoint'.
If none exist, create new issue with reproduction steps."
```

**Datadog MCP** - Query production logs
```text
"Query Datadog for errors containing 'approval' in the last 24 hours.
Show error count by hour and top 5 error messages."
```

---

## Lab 2: Security Features

### Constitutional Rules for Security

**File**: `.claude/rules/security.md`

```markdown
# Security Standards

## Forbidden Practices
- Never commit secrets, API keys, or passwords
- Never use string concatenation for SQL queries
- Never store passwords in plain text
- Never use == for authentication comparison

## Required Practices
- Use environment variables for all secrets
- Use parameterized queries or ORM only
- Hash passwords with bcrypt (12+ rounds)
- Use timing-safe comparison (secrets.compare_digest)
- Validate all inputs with Pydantic
- Log all authentication attempts
```

**How to use:**
```text
# Claude blocks violations automatically
# Will refuse: "Store this API key in the code"
# Will approve: "Store this API key in environment variable"
```

### Specialized Agents for Security

**Security Auditor Agent** - Full security scan
```text
"Use the security-auditor agent to audit the authentication system.
Check for: timing attacks, injection vulnerabilities, weak crypto,
missing validation, insufficient logging. Prioritize by CVSS score."
```

**Penetration Tester Agent** - Active security testing
```text
"Use the penetration-tester agent to test for SQL injection.
Try: malformed inputs, special characters, SQL keywords in ticket content."
```

**Compliance Auditor Agent** - Regulatory compliance
```text
"Use the compliance-auditor agent to verify GDPR compliance.
Check: data retention, audit logging, user consent, data deletion."
```

### Validation Hooks for Security

**Secret Scanner Hook**

**File**: `.claude/hooks/check-secrets.sh`

```bash
#!/bin/bash
# PreToolUse hook (matcher "Bash"): scan the staged changes for secrets
# before any git commit, and block the commit if one turns up.
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
case "$COMMAND" in
    *"git commit"*) ;;
    *) exit 0 ;;
esac

echo "Scanning staged changes for secrets..." >&2

# Added lines only, skipping the env template and docs
if git diff --cached -- . ':(exclude)*.env.example' ':(exclude)*.md' \
     | grep -E '^\+[^+]' \
     | grep -iE "(api[_-]?key|password|secret|token|credential)" >&2; then
    echo "BLOCKED: possible secret in the staged changes; secrets belong in environment variables" >&2
    exit 2
fi

# Deeper scan when TruffleHog is installed (its documented pre-commit form)
if command -v trufflehog >/dev/null 2>&1; then
    if ! trufflehog git file://. --since-commit HEAD --results=verified,unknown --fail --trust-local-git-config >&2; then
        echo "BLOCKED: TruffleHog reported a secret" >&2
        exit 2
    fi
fi

exit 0
```

**Security Scan Hook**

**File**: `.claude/hooks/security-scan.sh`

```bash
#!/bin/bash
# Security scan: Bandit for the code, pip-audit for the dependencies.
# Run it as a CI step, or register it like check-secrets.sh above (add the
# same git-commit gate); a failing scan exits 2 so the hook blocks.
echo "Running security scan..." >&2

if ! bandit -r models/ services/ api/ database/ -ll >&2; then
    echo "BLOCKED: Bandit reported medium or high severity issues" >&2
    exit 2
fi

# safety check is deprecated in favor of safety scan, which needs an
# account; pip-audit (pip install pip-audit) does not
if ! pip-audit -r requirements.txt >&2; then
    echo "BLOCKED: pip-audit found vulnerable dependencies" >&2
    exit 2
fi

echo "Security scan passed" >&2
exit 0
```

### MCP for Security

**HashiCorp Vault MCP** - Secure secrets management
```text
"Use Vault MCP to:
1. Store database password at secret/supportflow/prod/db
2. Retrieve password and set DATABASE_URL env var
3. Rotate password and update application"
```

**Snyk MCP** - Vulnerability scanning
```text
"Use Snyk MCP to:
1. Scan Python dependencies for known vulnerabilities
2. Check for outdated packages
3. Suggest secure alternatives for vulnerable packages"
```

**SIEM MCP (Splunk/ELK)** - Security monitoring
```text
"Use SIEM MCP to:
1. Send audit logs to Splunk for analysis
2. Create alert for 10+ failed auth attempts in 5 minutes
3. Dashboard showing authentication patterns"
```

---

## Lab 3: Operations Features

### Constitutional Rules for Operations

**File**: `.claude/rules/devops.md`

```markdown
# DevOps Standards

## Configuration Management
- All configuration from environment variables
- No hardcoded URLs, ports, or credentials
- .env.example must document all required vars
- Fail fast on startup if config missing

## Deployment Standards
- Every deployment must have rollback procedure
- Smoke tests required before production promotion
- Blue-green deployment for zero downtime
- Database migrations must be reversible

## Monitoring Requirements
- All endpoints must export Prometheus metrics
- All errors must be logged with context
- All alerts must have associated runbooks
- SLIs/SLOs defined for critical services

## Database Standards
- Migrations tested in staging first
- Backup before every migration
- Connection pooling configured
- Indexes on frequently queried columns
```

### Specialized Agents for Operations

**DevOps Engineer Agent** - Infrastructure automation
```text
"Use the devops-engineer agent to:
1. Create CI/CD pipeline with GitHub Actions
2. Add docker-compose with PostgreSQL and Redis
3. Configure nginx reverse proxy with SSL
4. Set up log rotation and compression"
```

**SRE Engineer Agent** - Reliability and SLOs
```text
"Use the sre-engineer agent to:
1. Define SLIs: availability, latency, error rate
2. Set SLOs: 99.9% availability, P95 <500ms, errors <1%
3. Create alerting rules for SLO violations
4. Generate Grafana dashboard with SLI tracking"
```

**Platform Engineer Agent** - Kubernetes infrastructure
```text
"Use the platform-engineer agent to:
1. Create K8s manifests: deployment, service, ingress
2. Configure horizontal pod autoscaling
3. Set resource limits and requests
4. Create Helm chart for easy deployment"
```

**Performance Engineer Agent** - Optimization
```text
"Use the performance-engineer agent to:
1. Analyze database queries for slow operations
2. Add indexes where needed
3. Implement Redis caching for read-heavy endpoints
4. Create locust load test scenarios"
```

**Deployment Engineer Agent** - Release automation
```text
"Use the deployment-engineer agent to:
1. Create blue-green deployment pipeline
2. Add canary deployment stage (10% traffic)
3. Implement automatic rollback on errors
4. Add deployment approval gates"
```

### Validation Hooks for Operations

**Config Validation Hook**

**File**: `.claude/hooks/validate-config.sh`

```text
#!/bin/bash
set -e

echo "Validating configuration..."

# Check .env.example is up to date
REQUIRED_VARS=(
    "DATABASE_URL"
    "API_KEY"
    "LOG_LEVEL"
    "ENVIRONMENT"
)

for var in "${REQUIRED_VARS[@]}"; do
    if ! grep -q "^$var=" .env.example; then
        echo "Missing $var in .env.example"
        exit 1
    fi
done

# Validate docker-compose.yml
docker-compose config > /dev/null

echo "Configuration valid"
```

**Migration Validation Hook**

**File**: `.claude/hooks/check-migrations.sh`

```bash
#!/bin/bash
set -e

echo "Validating database migrations..."

# Check migrations are reversible
if ls alembic/versions/*.py 1> /dev/null 2>&1; then
    for migration in alembic/versions/*.py; do
        if ! grep -q "def downgrade" "$migration"; then
            echo "Migration $migration missing downgrade()"
            exit 1
        fi
    done
fi

# Test migrations in test database
export DATABASE_URL="sqlite:///./test_migration.db"
alembic upgrade head
alembic downgrade -1
alembic upgrade head
rm test_migration.db

echo "Migrations valid and reversible"
```

**Metrics Validation Hook**

**File**: `.claude/hooks/validate-metrics.sh`

```bash
#!/bin/bash
set -e

echo "Validating Prometheus metrics..."

# Check metrics endpoint exists
if ! grep -r "/metrics" api/; then
    echo "No /metrics endpoint found"
    exit 1
fi

# Verify metrics are exported
if ! grep -r "Counter\|Histogram\|Gauge" api/ services/; then
    echo "No Prometheus metrics defined"
    exit 1
fi

echo "Metrics configured"
```

### MCP for Operations

**Prometheus MCP** - Metrics and monitoring
```text
"Use Prometheus MCP to:
1. Query error rate for last hour: rate(http_errors_total[1h])
2. Check P95 latency: histogram_quantile(0.95, http_request_duration)
3. Alert if error rate >1%: create alert rule
4. Export results to CSV for reporting"
```

**Kubernetes MCP** - Container orchestration
```text
"Use Kubernetes MCP to:
1. Deploy supportflow:v1.2.0 to staging namespace
2. Scale to 3 replicas
3. Check pod health status
4. If healthy, promote to production
5. Monitor rolling update progress"
```

**PagerDuty/OpsGenie MCP** - Incident management
```text
"Use PagerDuty MCP to:
1. Create alert for HighErrorRate incident
2. Assign to on-call engineer
3. Set priority to P1 (critical)
4. Include runbook link in incident description
5. Auto-resolve when metric returns to normal"
```

**AWS CloudWatch MCP** - Cloud monitoring
```text
"Use CloudWatch MCP to:
1. Stream application logs to CloudWatch Logs
2. Create metric filter for 'ERROR' log level
3. Set up dashboard with key metrics
4. Configure SNS alerts for critical errors"
```

**Terraform MCP** - Infrastructure as code
```text
"Use Terraform MCP to:
1. Create VPC with public and private subnets
2. Provision RDS PostgreSQL instance
3. Set up Application Load Balancer
4. Deploy ECS Fargate service for SupportFlow
5. Apply changes with plan review"
```

---

## Complete Workflow Examples

### Example 1: Fix Bug with Full Stack

```text
# 1. Create debugging rules
"Create .claude/rules/debugging.md with systematic investigation requirements"

# 2. Investigate with agent
"Use debugger agent to investigate approval endpoint failure.
Read code, check database, identify root cause."

# 3. Implement fix
"Fix the identified issue and add regression test"

# 4. Validate with hook
git commit -m "Fix approval logic"
# Pre-commit hook automatically runs tests

# 5. Review
"Use code-reviewer agent to review the fix before pushing"

# 6. Track with MCP
"Create GitHub issue tracking this bug and link commit SHA"
```

### Example 2: Complete Security Hardening

```text
# 1. Set security standards
"Create .claude/rules/security.md enforcing OWASP Top 10 prevention"

# 2. Audit entire codebase
"Use security-auditor agent to scan for vulnerabilities.
Prioritize by severity (Critical -> High -> Medium -> Low)."

# 3. Fix critical issues
"Implement fixes for all HIGH and CRITICAL issues:
- Hash API keys with bcrypt
- Add rate limiting
- Validate all inputs
- Use parameterized queries"

# 4. Prevent future issues
"Create .claude/hooks/check-secrets.sh to scan commits
Create .claude/hooks/security-scan.sh to run Bandit"

# 5. Integrate security tools
"Use Vault MCP for secrets management
Use Snyk MCP for dependency scanning"

# 6. Verify fixes
"Use penetration-tester agent to verify fixes are effective"
```

### Example 3: Production Deployment Pipeline

```text
# 1. Set operational standards
"Create .claude/rules/devops.md with deployment and monitoring requirements"

# 2. Build infrastructure
"Use devops-engineer agent to:
- Migrate to PostgreSQL
- Create GitHub Actions CI/CD
- Add Prometheus metrics
- Configure structured logging"

# 3. Define reliability targets
"Use sre-engineer agent to:
- Define SLIs and SLOs
- Create alert rules
- Build Grafana dashboards
- Write runbooks"

# 4. Optimize performance
"Use performance-engineer agent to:
- Add database indexes
- Implement caching
- Create load tests
- Profile and optimize"

# 5. Add validation gates
"Create hooks:
- .claude/hooks/validate-config.sh
- .claude/hooks/check-migrations.sh
- .claude/hooks/validate-metrics.sh"

# 6. Deploy with orchestration
"Use K8s MCP to:
- Deploy to staging
- Run smoke tests
- Promote to production
- Monitor rollout"

# 7. Monitor with MCP
"Use Prometheus MCP to verify metrics
Use PagerDuty MCP to ensure alerts are configured"
```

---

## Workflow Prompts

### Combining Features

**1. Rules + Agents + Hooks**
```text
Constitutional rules set the standards
-> Agents implement the standards
-> Hooks enforce the standards
-> MCP integrates with external tools
```

**2. Iterative Workflow**
```text
Investigation (Agent) -> Implementation (Claude) -> Validation (Hook) -> Integration (MCP)
```

**3. Progressive Enhancement**
```text
Start: Basic rules for immediate value
Add: Specialized agents for complex tasks
Enhance: Validation hooks for automation
Integrate: MCP for external systems
```

### Common Patterns

**Pattern 1: Security Review**
```text
1. Rules: Define security standards
2. Agent: Security auditor scans code
3. Claude: Implements fixes
4. Hook: Prevents future violations
5. MCP: Integrates security tools
```

**Pattern 2: Production Deployment**
```text
1. Rules: Define deployment standards
2. Agent: DevOps builds infrastructure
3. Claude: Creates configuration
4. Hook: Validates before deploy
5. MCP: Deploys to production
```

**Pattern 3: Debugging**
```text
1. Rules: Define debugging process
2. Agent: Debugger investigates
3. Claude: Implements fix
4. Hook: Runs tests
5. MCP: Tracks in issue tracker
```

---

## Further Reading

- **Claude Code Documentation**: https://code.claude.com/docs
- **Constitutional AI**: How rules guide AI behavior
- **MCP Protocol**: https://modelcontextprotocol.io
- **Task Agents**: Specialized subagent capabilities

---

## Quick Checklist

Before starting Challenge Labs:

- [ ] Create `.claude/rules/` directory for constitutional rules
- [ ] Create `.claude/hooks/` directory for validation hooks
- [ ] Configure `.claude/settings.json` for hook triggers
- [ ] Understand available specialized agents
- [ ] Know which MCP integrations are available
- [ ] Review example workflows above

Now start the Challenge Labs.
