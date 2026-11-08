# Challenge Labs: Shared Reference

**Reference**: Chapter 8, Section 8.7

This file holds the prompts, verification steps, and completion criteria for all three challenge labs. Read the individual challenge first. Come here for the shared steps.

- [Challenge Lab 1: Debug and Fix](challenge-1-debug-and-fix.md)
- [Challenge Lab 2: Security Hardening](challenge-2-security-hardening.md)
- [Challenge Lab 3: Observability and Operations](challenge-3-observability.md)

---

## Using Claude Code Effectively

### Quick Reference: Claude Code Features in Action

#### Creating Constitutional Rules

**Create `.claude/rules/debugging.md`:**
```markdown
# Debugging Rules for SupportFlow

## Investigation Requirements
- Always read the relevant code files before proposing fixes
- Check application logs for error stack traces
- Query database to verify actual state vs expected state
- Reproduce the issue with a minimal test case

## Fix Requirements
- Every bug fix MUST include a regression test
- Document root cause in commit message
- Update related documentation if behavior changes
- Verify fix doesn't break existing functionality

## Validation Requirements
- Run affected tests: pytest tests/path/to/test.py -v
- Run type checking: mypy path/to/fixed/file.py
- Check integration: Test complete workflow end-to-end
- Verify logs: Ensure error no longer appears in logs
```

**Usage:**
```text
# Claude Code will automatically enforce these rules
# When you ask: "Debug the approval endpoint failure"
# Claude will follow the investigation requirements automatically
```

#### Using Specialized Agents

**Example 1: Debug with specialized agent**
```text
# In Claude Code chat:
"Use the debugger agent to investigate why the approval endpoint
returns 'already reviewed' for draft responses. Follow systematic
debugging approach: read code -> check logs -> verify database ->
identify root cause -> suggest fix with tests."
```

**Example 2: Security audit**
```text
# In Claude Code chat:
"Use the security-auditor agent to review authentication code in
api/dependencies.py. Check for: timing attacks, hardcoded secrets,
insufficient validation, and suggest mitigations for each issue found."
```

**Example 3: Performance optimization**
```text
# In Claude Code chat:
"Use the performance-engineer agent to analyze database queries and
suggest optimizations. Add indexes where needed, implement caching
for read-heavy operations, and create load test scenarios."
```

#### Creating Validation Hooks

**Create `.claude/hooks/pre-commit-tests.sh`:**
```bash
#!/bin/bash
# Run tests before allowing commit

# PreToolUse matchers select the tool (a string like "Bash"), not the
# command text, so the script itself checks whether this call is a commit.
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
case "$COMMAND" in
    *"git commit"*) ;;      # a commit: run the checks below
    *) exit 0 ;;            # anything else: allow without testing
esac

echo "Running tests before commit..." >&2

# Run tests when staged changes touch Python files
CHANGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep "\.py$" || true)

if [ -n "$CHANGED_FILES" ]; then
    echo "Changed Python files: $CHANGED_FILES" >&2

    # Only exit code 2 blocks the commit; any other failure would let it through
    if ! pytest tests/ -v --tb=short >&2; then
        echo "BLOCKED: tests fail; fix them before committing" >&2
        exit 2
    fi

    # Advisory until the existing strict-mypy errors are cleared
    mypy models/ services/ api/ database/ >&2 || echo "WARNING: mypy reports type errors" >&2
fi

exit 0
```

**Configure in `.claude/settings.json`** (matcher is a tool-name string; timeout is in seconds):
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/pre-commit-tests.sh",
        "timeout": 60
      }]
    }]
  }
}
```

#### Using MCP Integrations

**Example 1: Query production logs**
```text
# Assuming Datadog MCP is configured
"Query Datadog logs for errors in the last hour related to 'approval'.
Show error frequency and common stack traces."
```

**Example 2: Retrieve secrets securely**
```text
# Assuming Vault MCP is configured
"Retrieve the database password from Vault at secret/supportflow/production/db
and update the DATABASE_URL environment variable in docker-compose.yml."
```

**Example 3: Deploy to Kubernetes**
```text
# Assuming K8s MCP is configured
"Deploy SupportFlow to staging namespace in Kubernetes.
Use the image: supportflow:v1.2.0.
Scale to 3 replicas with resource limits: 512Mi memory, 500m CPU."
```

**Example 4: Create alert in PagerDuty**
```text
# Assuming PagerDuty MCP is configured
"Create PagerDuty alert for HighErrorRate in Prometheus.
Assign to on-call engineer with high priority.
Include runbook link: https://wiki/runbooks/high-error-rate"
```

#### Combining Features

**Example: Complete Security Hardening Workflow**
```text
1. Create security rules:
   "Create .claude/rules/security.md with OWASP Top 10 prevention rules"

2. Use security agent:
   "Use security-auditor agent to scan entire codebase for vulnerabilities"

3. Implement fixes:
   "Fix identified issues: add input validation, implement rate limiting,
   hash API keys with bcrypt"

4. Add validation hook:
   "Create .claude/hooks/security-scan.sh that runs Bandit before commits"

5. Verify with MCP:
   "Use Snyk MCP to verify no vulnerable dependencies remain"

Result: Complete security audit -> fixes -> automated prevention
```

**Example: Complete Production Deployment Workflow**
```text
1. Set operations rules:
   "Create .claude/rules/devops.md requiring env vars, rollback plans, metrics"

2. Use DevOps agents:
   "Use devops-engineer agent to create CI/CD pipeline with GitHub Actions"
   "Use sre-engineer agent to define SLIs/SLOs and create dashboards"

3. Add validation hooks:
   "Create .claude/hooks/validate-config.sh checking required env vars"
   "Create .claude/hooks/test-rollback.sh verifying rollback procedures"

4. Deploy with MCP:
   "Use K8s MCP to deploy to staging, run smoke tests, then promote to prod"
   "Use Prometheus MCP to verify metrics are being collected"

Result: Production-ready deployment with monitoring and validation
```

### Prompting Tips for Challenge Labs

#### 1. **Break Down Large Tasks**

Do not write:
```text
Fix all the bugs in the application
```

Write:
```text
List all API endpoints and test each one systematically.
For each failing endpoint:
1. Document the error
2. Read the relevant code
3. Identify the root cause
4. Propose a fix
5. Test the fix
```

#### 2. **Use Iterative Prompting**

First, investigate:
```text
Investigate why the approval endpoint is failing:
1. Read the endpoint code
2. Check database schema
3. Review error logs
4. Identify the issue
```

Then, fix:
```text
Now that we identified the issue is with status comparison,
fix the logic to properly check for "DRAFT" status.
```

#### 3. **Request Code Reviews**

```text
Review the security of this API key authentication code.
Look for:
- Timing attacks
- Hardcoded secrets
- Insufficient validation
- Missing error handling

Suggest improvements for each issue found.
```

#### 4. **Generate Test Cases**

```text
Create integration tests for the response approval workflow:
1. Submit a ticket
2. Extract response ID
3. Approve the response
4. Verify status changed
5. Check audit log recorded the approval
6. Test edge cases (already approved, invalid ID)
```

#### 5. **Ask for Explanations**

```text
Explain how SQLAlchemy connection pooling works in this application.
Then suggest optimal pool_size and max_overflow values for:
- Development (1-2 users)
- Staging (10-20 users)
- Production (100+ concurrent users)
```

#### 6. **Request Documentation**

```text
Create a runbook for the "HighErrorRate" alert.
Include:
- What triggers this alert
- What it indicates
- How to investigate
- Step-by-step resolution
- When to escalate
```

### Real-World Example Workflows

#### Lab 1 Example: Fixing the Approval Bug with Constitutional Rules

**Step 1: Create debugging rules**
```text
# Create .claude/rules/debugging.md with investigation requirements
# Claude will automatically follow these when debugging
```

**Step 2: Use debugger agent**
```text
Ask Claude:
"Use the debugger agent to investigate the approval endpoint failure.
The endpoint rejects draft responses with 'already reviewed' error.
Follow systematic debugging: read code -> check database -> identify issue."
```

**Step 3: Claude investigates systematically**
```text
Claude reads:
- api/main.py (approval endpoint)
- database/repositories.py (ResponseRepository.approve)
- database/models.py (Response model)

Claude checks database:
- Queries responses with status='draft'
- Verifies status field type

Claude identifies issue:
- Conditional logic incorrectly rejects draft status
- Should allow approval when status='draft'
```

**Step 4: Implement fix with validation**
```text
Claude suggests fix and creates test:
- Updates conditional to allow draft status
- Adds integration test for approval workflow
- Pre-commit hook runs tests automatically
```

**Result**: Bug fixed in 10 minutes vs 1+ hour manual debugging

#### Lab 2 Example: Security Hardening with Specialized Agents

**Step 1: Create security rules**
```text
# Create .claude/rules/security.md
# Rules enforce: no secrets in code, bcrypt for passwords, timing-safe comparison
```

**Step 2: Full security audit**
```text
Ask Claude:
"Use security-auditor agent to scan the entire codebase.
Check for: hardcoded secrets, SQL injection, XSS, timing attacks,
weak crypto, missing validation. Prioritize by severity."
```

**Step 3: Claude scans systematically**
```text
Security-auditor agent finds:
- HIGH: API key hardcoded in api/dependencies.py
- HIGH: Plain text API key comparison (timing attack risk)
- MEDIUM: No rate limiting on authentication
- MEDIUM: Missing input size limits
- LOW: Some log messages contain sensitive data
```

**Step 4: Fix with agents and hooks**
```text
Ask Claude:
"Implement fixes for high-severity issues:
1. Move API key to environment variable
2. Hash API keys with bcrypt and use timing-safe comparison
3. Add rate limiting with slowapi"

Then create .claude/hooks/check-secrets.sh to prevent future leaks.
```

**Step 5: Validate with MCP**
```text
Ask Claude:
"Use Snyk MCP to verify no vulnerable dependencies.
Use Vault MCP to store API keys securely."
```

**Result**: Complete security audit and fixes in 2 hours vs 1+ day manual review

#### Lab 3 Example: Production Deployment with Full Automation

**Step 1: Set operational standards**
```text
# Create .claude/rules/devops.md
# Enforce: all config from env, metrics on all endpoints, rollback plans
```

**Step 2: Build infrastructure with agents**
```text
Ask Claude:
"Use devops-engineer agent to:
1. Migrate SQLite to PostgreSQL with data integrity checks
2. Create CI/CD pipeline with test -> build -> deploy stages
3. Add Prometheus metrics and Grafana dashboards
4. Configure structured logging with request ID tracking"
```

**Step 3: Claude orchestrates multiple agents**
```text
DevOps agent:
- Creates Alembic migration script
- Writes docker-compose.yml with PostgreSQL
- Builds GitHub Actions workflow

SRE agent:
- Defines SLIs: error rate <1%, latency P95 <500ms
- Creates alerting rules with runbooks
- Generates Grafana dashboard JSON

Performance agent:
- Adds database indexes
- Implements connection pooling
- Creates load test with locust
```

**Step 4: Add validation hooks**
```text
Ask Claude:
"Create validation hooks:
- .claude/hooks/validate-config.sh (check env vars)
- .claude/hooks/test-rollback.sh (verify rollback works)
- .claude/hooks/check-metrics.sh (ensure metrics exported)"
```

**Step 5: Deploy with MCP**
```text
Ask Claude:
"Use K8s MCP to:
1. Deploy to staging namespace
2. Run smoke tests
3. If tests pass, promote to production
4. Use Prometheus MCP to verify metrics collection"
```

**Result**: Production-ready deployment with full observability in 3 hours vs 1+ week manual setup

### Claude Code Commands to Use

Use these built-in commands during the labs. Run `/help` for the current list. The list grows with each release.

| Command | When to use it |
|---------|-----------------------------|
| `/code-review` | Bundled skill that reviews the current diff. Run it before every commit. |
| `/plan` (or Shift+Tab) | Propose before editing. Use it for every task where the approach matters. |
| `/rewind` | Roll back to a checkpoint when a fix makes things worse. |
| `/effort` | Raise reasoning depth for threat modeling and multi-file refactors. |
| `/memory` | Inspect and prune what Claude has learned about the project. |
| `/sandbox` | OS-level isolation for Bash, so experiments stay inside the project. |
| `/usage` | Watch token spend. These labs are long-running. |
| `/agents` | Prints a reminder of how sub-agents are managed. Ask Claude to create the ones each challenge asks for, or write them in `.claude/agents/`. |
| `/mcp` | Connect and authenticate the MCP servers each challenge names. |
| `/doctor` | Diagnose installation and configuration problems. |

To make another task repeatable, such as "run our security checklist" or "write a release note", write it as a skill in `.claude/skills/`. It then runs as `/your-skill-name`. Section 8.3 covers the format.

### Verification Strategy

After each task:

1. **Run tests**: `pytest tests/ -v`
2. **Check types**: `mypy models/ services/ api/ database/`
3. **Test manually**: Use curl or Swagger UI
4. **Check logs**: `docker-compose logs --tail=50`
5. **Verify database**: Query tables to confirm changes
6. **Create commit**: Document what you fixed/added

---

## Additional Resources

### Documentation to Reference

- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Pydantic**: https://docs.pydantic.dev/
- **Prometheus**: https://prometheus.io/docs/
- **Docker**: https://docs.docker.com/
- **GitHub Actions**: https://docs.github.com/en/actions

### Security Resources

- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **OWASP API Security Top 10**: https://owasp.org/API-Security/
- **NIST Cybersecurity Framework**: https://www.nist.gov/cyberframework

### Observability Resources

- **12 Factor App**: https://12factor.net/
- **SRE Book**: https://sre.google/books/
- **Distributed Tracing**: https://opentelemetry.io/

---

## Completion Criteria

You have completed all challenge labs when:

**Lab 1 - Debugging**
- All identified bugs fixed and tested
- Approval workflow working end-to-end
- Sentiment detection accurate
- Thorough test coverage added

**Lab 2 - Security**
- No hardcoded secrets remain
- RBAC implemented and working
- Rate limiting active
- HTTPS configured
- Input validation complete

**Lab 3 - Operations**
- Structured logging in place
- Metrics exported to Prometheus
- PostgreSQL database in use
- Alerting configured
- CI/CD pipeline functional
- Performance optimized

### Final Validation

Run this end-to-end test:

```bash
# Start the application
docker-compose up -d

# Run all tests
pytest tests/ -v --cov=. --cov-report=term

# Check type safety
mypy models/ services/ api/ database/

# Exercise every endpoint (each one is documented with example
# payloads in supportflow/API_GUIDE.md)
curl -X POST http://localhost:8000/tickets \
  -H "X-API-Key: demo-key-12345" -H "Content-Type: application/json" \
  -d '{"content": "Final validation ticket: I was charged twice."}'
curl -H "X-API-Key: demo-key-12345" http://localhost:8000/responses/pending

# Check metrics
curl http://localhost:8000/metrics | grep supportflow

# Verify logs are JSON
docker-compose logs supportflow | tail -1 | python3 -m json.tool

# Test rate limiting
for i in {1..200}; do curl -H "X-API-Key: demo-key-12345" http://localhost:8000/health; done

# Check health
curl http://localhost:8000/health/detailed | python3 -m json.tool

# Success!
echo "SupportFlow is production-ready!"
```

---

## Next Steps

After completing all challenge labs:

1. **Deploy to Cloud**: AWS/GCP/Azure deployment
2. **Scale Horizontally**: Multiple instances behind load balancer
3. **Add Advanced Features**: Real-time webhooks, email notifications
4. **Integrate with Tools**: Slack, Jira, Zendesk integrations
5. **Mobile API**: Build mobile app using the API
6. **Analytics Dashboard**: Business intelligence and reporting
7. **ML Enhancement**: Replace keyword matching with trained models
8. **Multi-tenancy**: Support multiple organizations

**Congratulations on improving SupportFlow!**
