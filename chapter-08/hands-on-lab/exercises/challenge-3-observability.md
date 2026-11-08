# Challenge Lab 3: Observability and Production Operations

**Reference**: Chapter 8, Section 8.7 (third challenge)

In this challenge you add these to SupportFlow:

- Structured logging
- Metrics
- Alerting
- A PostgreSQL database
- A CI/CD pipeline

**Prerequisite**: Finish [Challenge Lab 1](challenge-1-debug-and-fix.md) first. Finish [Challenge Lab 2](challenge-2-security-hardening.md) too, if you can.

**Related chapter**: You wire headless mode into CI here (`claude -p ... --output-format json`). Chapter 11 builds full agentic pipelines on the same mechanism.

---

**Duration**: 3-4 hours
**Difficulty**: Advanced
**Focus**: Monitoring, Logging, Performance, Production Readiness

### Learning Objectives

By completing this lab, you will:
- Implement structured logging for production
- Add metrics and monitoring capabilities
- Set up alerting for critical issues
- Migrate from SQLite to PostgreSQL
- Optimize for production workloads
- Create CI/CD pipeline
- Use Claude Code for infrastructure automation

### Prerequisites

- Completed Challenge Labs 1 and 2
- Understanding of logging and monitoring concepts
- Basic DevOps knowledge
- Docker and docker-compose experience

### Implementation Hints: Use Claude Code's DevOps Capabilities

**Use these Claude Code features:**

- **Create operations rules** in `.claude/rules/devops.md`:
  - "All configuration must come from environment variables, never hardcoded"
  - "Every deployment must have a rollback plan documented"
  - "All metrics must have associated alerts with runbooks"
  - "Database migrations must be reversible and tested"
  - "Log all errors with context: request_id, user_id, trace_id"

- **Build DevOps sub-agents** for infrastructure automation. Define each in `.claude/agents/`. Use the frontmatter format in [`../../code-examples/subagents/`](../../code-examples/subagents/):
  - `devops-engineer`: infrastructure setup
  - `sre-engineer`: reliability improvements and SLO definition
  - `platform-engineer`: Kubernetes manifests and platform design
  - `deployment-engineer`: CI/CD pipeline creation
  - `performance-engineer`: optimization and load testing

- **Add operations hooks** in `.claude/hooks/`:
  - Create `validate-config.sh` to check that all required env vars are documented in `.env.example`
  - Add `check-migrations.sh` to verify Alembic migrations are reversible
  - Use `validate-metrics.sh` to check that new endpoints export Prometheus metrics
  - Add `test-rollback.sh` to verify deployment rollback procedures work
  - Create `check-logging.sh` to check that all API endpoints log request/response

- **Use MCP for operations integrations**:
  - Connect to Prometheus MCP to query metrics and analyze performance trends
  - Integrate with PagerDuty/OpsGenie MCP for alert management and on-call rotation
  - Use Kubernetes MCP to deploy, scale, and monitor pods in production
  - Connect to AWS CloudWatch or Datadog MCP for centralized logging and monitoring
  - Use Terraform MCP to manage infrastructure as code declaratively

**Example Claude Code operations workflow:**
```text
1. Ask Claude: "Set up structured logging with request ID tracking and Prometheus metrics"
2. DevOps agent creates logging config, metrics exporters, and Grafana dashboards
3. Claude generates Alembic migration for PostgreSQL with rollback script
4. Pre-deployment hook validates all env vars present and migrations reversible
5. Claude creates CI/CD pipeline with staging deployment and smoke tests
6. Alert rules auto-generated with runbook links in annotations
7. Claude documents deployment process and rollback procedures
```

**Operations-specific prompts to use:**
- "Create Prometheus metrics for ticket processing: counters, histograms, and gauges with proper labels"
- "Design Alembic migration from SQLite to PostgreSQL preserving all data with integrity checks"
- "Generate GitHub Actions pipeline: test -> build -> push -> deploy with approval gates"
- "Create alerting rules for SLO violations: error rate, latency P95, and availability targets"
- "Build a complete health check endpoint testing database, cache, and external API connectivity"

**More monitoring tasks for Claude Code:**
- Ask Claude to generate SLI/SLO definitions based on business requirements
- Use Claude to create Grafana dashboard JSON with key metrics and alerts
- Have Claude analyze Prometheus metrics and suggest optimization opportunities
- Generate load test scenarios with locust based on production traffic patterns
- Create runbooks for common alerts with investigation and resolution steps

### Challenge Tasks

#### Task 1: Implement Structured Logging

**Goal**: Add complete logging for production observability.

**Claude Code Prompt**:
```text
Implement structured JSON logging for production:

1. Replace print statements with proper logging:
   - Use Python's logging module
   - Configure logging in api/main.py
   - Add log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

2. Implement structured logging with structlog or python-json-logger:
   - Log in JSON format for parsing
   - Include standard fields: timestamp, level, message, request_id, user_id
   - Add context fields: endpoint, method, status_code, duration_ms

3. Add request ID tracking:
   - Generate unique ID for each request
   - Pass through all service layers
   - Include in all log entries
   - Return in response header (X-Request-ID)

4. Log important events:
   - All API requests (with duration)
   - Authentication attempts (success/failure)
   - Ticket creation and analysis
   - Response approval/rejection
   - Database errors
   - Escalation triggers

5. Configure log levels by environment:
   - Development: DEBUG
   - Staging: INFO
   - Production: WARNING

6. Set up log rotation:
   - Max size: 100MB
   - Keep 10 files
   - Compress old logs

Example structured log:
{"timestamp": "2026-02-03T12:00:00Z", "level": "INFO", "message": "Ticket created", "request_id": "abc-123", "user_id": "agent@example.com", "ticket_id": "TKT-001", "category": "billing", "escalated": true, "duration_ms": 45}
```

**Implementation Pattern**:
```python
import structlog

logger = structlog.get_logger()

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    structlog.contextvars.bind_contextvars(request_id=request_id)

    start_time = time.time()
    response = await call_next(request)
    duration = (time.time() - start_time) * 1000

    logger.info("request_completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration
    )

    return response
```

**Validation**:
- [ ] All logs in JSON format
- [ ] Request ID in every log entry
- [ ] Log levels properly configured
- [ ] No print() statements remaining
- [ ] Logs parseable by log aggregators

#### Task 2: Add Prometheus Metrics

**Goal**: Export application metrics for monitoring.

**Claude Code Prompt**:
```text
Add Prometheus metrics for monitoring:

1. Install prometheus-fastapi-instrumentator
2. Add metrics endpoint at /metrics
3. Implement custom metrics:
   - ticket_submissions_total (counter) by category
   - ticket_analysis_duration_seconds (histogram)
   - response_approvals_total (counter)
   - response_rejections_total (counter)
   - escalations_total (counter) by priority
   - api_key_auth_failures_total (counter)
   - database_query_duration_seconds (histogram)
   - active_requests (gauge)

4. Add labels for better filtering:
   - Endpoint, method, status_code
   - Category, sentiment, urgency
   - Priority level

5. Create Prometheus configuration (prometheus.yml)
6. Create Grafana dashboard JSON for SupportFlow
7. Update docker-compose.yml to include Prometheus and Grafana

8. Document key metrics to monitor:
   - Request rate and latency
   - Error rate (4xx, 5xx)
   - Ticket processing time
   - Escalation rate
   - Database connection pool usage

Test metrics: curl http://localhost:8000/metrics
```

**Prometheus Config**:
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'supportflow'
    static_configs:
      - targets: ['supportflow:8000']
```

**Validation**:
- [ ] /metrics endpoint returns Prometheus format
- [ ] Custom metrics recorded correctly
- [ ] Prometheus scraping metrics
- [ ] Grafana dashboard shows real-time data
- [ ] Metrics have meaningful labels

#### Task 3: Migrate from SQLite to PostgreSQL

**Goal**: Use production-grade database.

**Claude Code Prompt**:
```text
Migrate from SQLite to PostgreSQL for production:

1. Update requirements.txt:
   - Add psycopg2-binary for PostgreSQL
   - Keep SQLite support for local development

2. Make database code PostgreSQL-compatible:
   - Change Boolean columns (0/1) to proper BOOLEAN
   - Update JSON column types if needed
   - Test all queries work on PostgreSQL

3. Create database migration script:
   - Export data from SQLite
   - Convert schema to PostgreSQL DDL
   - Import data into PostgreSQL
   - Verify data integrity

4. Update docker-compose.yml:
   - Add PostgreSQL service
   - Add environment variables
   - Add volume for data persistence
   - Add health check for PostgreSQL

5. Create Alembic migrations:
   - Initialize Alembic
   - Generate initial migration
   - Test upgrade/downgrade

6. Update database connection:
   - Use DATABASE_URL environment variable
   - Support both sqlite:// and postgresql:// URLs
   - Add connection pooling for PostgreSQL
   - Configure pool size: min=5, max=20

7. Add database backup script:
   - pg_dump for PostgreSQL
   - Automated daily backups
   - Backup retention policy

Test with PostgreSQL: DATABASE_URL=postgresql://user:pass@localhost:5432/supportflow
```

**PostgreSQL docker-compose Addition**:
```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: supportflow
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: supportflow
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U supportflow"]
      interval: 10s
      timeout: 5s
      retries: 5

  supportflow:
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://supportflow:${DB_PASSWORD}@postgres:5432/supportflow

volumes:
  postgres_data:
```

**Validation**:
- [ ] PostgreSQL container running
- [ ] Application connects to PostgreSQL
- [ ] All endpoints work with PostgreSQL
- [ ] Data persists across restarts
- [ ] Migration script works
- [ ] Backup script creates valid dumps

#### Task 4: Add Alerting and Health Monitoring

**Goal**: Get notified of critical issues immediately.

**Claude Code Prompt**:
```text
Implement alerting for production incidents:

1. Create complete health checks:
   - Database connectivity
   - Disk space available
   - Memory usage
   - Recent error rate
   - Response time P95/P99
   - Last successful ticket processed

2. Add detailed health endpoint at /health/detailed:
   - Return JSON with component statuses
   - Include timing information
   - Include version and build info
   - HTTP 200 if all healthy, 503 if any failing

3. Implement alerting rules in Prometheus:
   - High error rate (>5% 5xx responses)
   - Slow responses (P95 >2 seconds)
   - Database connection failures
   - High memory usage (>90%)
   - Zero tickets processed in 1 hour

4. Add AlertManager configuration:
   - Define alert routing
   - Set up Slack webhook for alerts
   - Configure email notifications
   - Set different severity levels

5. Create runbook documentation:
   - What each alert means
   - How to investigate
   - How to resolve
   - Escalation procedures

6. Add deadman switch:
   - Alert if no metrics received
   - Ensures monitoring is working

Example alert rule:
alert: HighErrorRate
expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
for: 5m
annotations:
  summary: "High error rate detected"
  runbook: "https://wiki/runbooks/high-error-rate"
```

**Validation**:
- [ ] Health checks complete
- [ ] Alerts fire when conditions met
- [ ] Slack/email notifications working
- [ ] Runbook accessible
- [ ] Alert recovery notifications sent

#### Task 5: Performance Optimization

**Goal**: Optimize for production workloads.

**Claude Code Prompt**:
```text
Optimize application performance:

1. Add database query optimization:
   - Add indexes on frequently queried columns (ticket_id, status, created_at)
   - Use SELECT only needed columns
   - Implement query result caching for read-heavy operations
   - Add database query logging to find slow queries

2. Implement response caching:
   - Cache template renders
   - Cache ticket analysis results
   - Use Redis for caching
   - Set appropriate TTLs

3. Add connection pooling:
   - Configure SQLAlchemy pool size
   - Set pool_pre_ping=True for connection health checks
   - Configure pool overflow and timeout

4. Optimize Docker image:
   - Use slim Python image
   - Multi-stage build to reduce size
   - Remove unnecessary dependencies
   - Use .dockerignore properly

5. Add async processing for slow operations:
   - Use background tasks for escalation evaluation
   - Queue audit log writes
   - Async notification sending

6. Implement request compression:
   - Enable gzip compression middleware
   - Compress responses >1KB

7. Load test the application:
   - Use locust or k6
   - Test 100 concurrent users
   - Identify bottlenecks
   - Fix performance issues found

Create load_test.py with locust to test endpoints.
```

**Load Test Example**:
```python
from locust import HttpUser, task, between

class SupportFlowUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.headers = {"X-API-Key": "demo-key-12345"}

    @task(3)
    def submit_ticket(self):
        self.client.post("/tickets",
            json={"content": "I need help"},
            headers=self.headers
        )

    @task(1)
    def list_pending(self):
        self.client.get("/responses/pending",
            headers=self.headers
        )
```

**Validation**:
- [ ] Database indexes added
- [ ] Caching implemented
- [ ] Load test runs successfully
- [ ] P95 response time <500ms at 100 users
- [ ] Docker image size reduced
- [ ] Zero memory leaks detected

#### Task 6: CI/CD Pipeline

**Goal**: Automate testing and deployment.

**Claude Code Prompt**:
```text
Create GitHub Actions CI/CD pipeline:

1. Create .github/workflows/test.yml:
   - Trigger on push and pull request
   - Set up Python 3.11
   - Install dependencies
   - Run pytest with coverage
   - Run mypy type checking
   - Fail if coverage <80%

2. Create .github/workflows/security.yml:
   - Run Bandit security linter
   - Run Safety to check dependencies
   - Run Trivy to scan Docker image
   - Fail on high severity issues

3. Create .github/workflows/deploy.yml:
   - Trigger on tag push (v*.*.*)
   - Build Docker image
   - Tag with version number
   - Push to Docker Hub / GitHub Container Registry
   - Deploy to staging automatically
   - Require approval for production

4. Add pre-commit hooks:
   - Black code formatting
   - Isort import sorting
   - Flake8 linting
   - Pytest tests
   - Mypy type checking

5. Create deployment documentation:
   - Staging deployment process
   - Production deployment process
   - Rollback procedure
   - Blue-green deployment strategy

6. Add status badges to README:
   - Build status
   - Test coverage
   - Security scan status
   - Docker image version
```

**GitHub Actions Example**:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v7

    - name: Set up Python
      uses: actions/setup-python@v7
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest-cov

    - name: Run tests
      run: |
        pytest tests/ --cov=. --cov-report=xml

    - name: Check coverage
      run: |
        coverage report --fail-under=80

    - name: Run type checking
      run: mypy models/ services/ api/ database/
```

**Validation**:
- [ ] CI pipeline runs on every commit
- [ ] Tests must pass to merge
- [ ] Type checking enforced
- [ ] Security scans automated
- [ ] Deployment pipeline functional
- [ ] Pre-commit hooks installed

### Bonus Challenges

1. **Add Distributed Tracing**: Implement OpenTelemetry for request tracing across services
2. **Implement Blue-Green Deployment**: Zero-downtime deployments
3. **Add Chaos Engineering**: Use Chaos Monkey to test failure scenarios
4. **Create Kubernetes Manifests**: Deploy to K8s with Helm charts
5. **Add APM Integration**: Integrate with New Relic or DataDog
6. **Implement Feature Flags**: LaunchDarkly or similar for gradual rollouts
7. **Add Synthetic Monitoring**: Pingdom/Uptime Robot checks
8. **Create SLI/SLO Dashboard**: Track service level objectives

### Expected Outcomes

After completing this lab, you should have:
- Structured JSON logging
- Prometheus metrics and Grafana dashboards
- PostgreSQL database
- Alerting configured
- Performance optimized
- CI/CD pipeline
- Production-ready application
- Complete monitoring
- Automated deployments

---

## Shared Reference

Techniques, prompt patterns, and completion criteria common to all three challenges are in [`challenge-labs-reference.md`](challenge-labs-reference.md).
