# Integrations Directory

This directory holds guides, skeleton code, and configuration. Use them to connect the Zero-Downtime Deployer to observability tools.

For the latest setup steps, see each vendor's own docs: [Sentry](https://docs.sentry.io/platforms/python/), [Prometheus](https://prometheus.io/docs/), and [Grafana](https://grafana.com/docs/).

## Overview

The files cover three tools:

- **Sentry**: Error tracking and performance monitoring
- **Prometheus**: Metrics collection and querying
- **Grafana**: Visualization and dashboarding

---

## Directory Structure

```text
integrations/
├── README.md                      # This file
├── INDEX.md                       # Shorter navigation guide
├── observability_setup.md         # Architecture overview
├── sentry_setup.md                # Sentry account and configuration guide
├── sentry_integration.py          # SentryMonitor scaffold with TODOs
├── test_sentry_connection.py      # Verifies your DSN and SDK setup
├── grafana_setup.md               # Grafana setup (optional)
└── grafana_dashboards/            # Pre-built dashboard templates
    ├── README.md                  # How to import them
    ├── deployment-metrics.json    # Deployment success and duration
    ├── error-tracking.json        # Error correlation with deployments
    └── rollback-analysis.json     # Rollback patterns and recovery time
```

Everything here is optional. The hands-on lab exercises complete without any of
it. Use these files for two things:

- Real error tracking (Exercise 3).
- Adding metrics to the deployer and charting them. The dashboards are templates. The deployer does not export metrics yet.

---

## Files Guide

### Documentation Files

#### `observability_setup.md`
**Purpose**: See how the observability stack fits together

**Contains**:
- Architecture diagram of all components
- How each tool fits together
- What you need for each exercise
- Data flow through the system

**Read this first.**

---

#### `sentry_setup.md`
**Purpose**: Step-by-step guide to set up Sentry (for Exercise 3)

**Contains**:
- Account creation process (free tier)
- Project setup instructions
- How to get your DSN
- Configuring `.env` file
- Verifying connection
- Troubleshooting common issues

**Estimated time**: 10-15 minutes

**When to read**: Before starting Exercise 3

---

#### `grafana_setup.md`
**Purpose**: Optional visualization with Grafana

**Contains**:
- Local vs cloud Grafana setup
- Dashboard import instructions
- Creating custom visualizations
- Alerting configuration

**Note**: Grafana is **optional** - you can complete all exercises without it

**When to read**: After exercises, if you want advanced visualization

---

### Code Files

#### `sentry_integration.py`
**Type**: Skeleton code with TODOs

**Purpose**: Integration module for Sentry error tracking

**Contains**:
- `SentryMonitor` class with TODO sections
- Detailed hints and examples
- Test script to verify integration

**Key Methods**:
```python
class SentryMonitor:
    def __init__(self):
        # TODO: Initialize Sentry SDK

    def report_deployment_start(service, version, deployment_id):
        # TODO: Report deployment events

    def get_error_rate(service, version, minutes=5):
        # TODO: Query error rate

    def report_rollback(service, failed_ver, stable_ver, reason):
        # TODO: Report rollback events
```

**How to use**:
1. Follow TODOs in order (Part 1, Part 2, Part 3, Part 4)
2. Run the file directly to test: `python integrations/sentry_integration.py`
3. Import in your deployer: `from integrations.sentry_integration import SentryMonitor`

**Modes**:
- Placeholders let you run the code without a signup
- Use simulated mode or real Sentry

---

### Dashboard Files

#### `grafana_dashboards/`
**Type**: JSON dashboard definitions

**Contains**:
1. **deployment-metrics.json**
   - Deployment success rate
   - Average deployment duration
   - Deployments over time
   - Failed deployments by service

2. **error-tracking.json**
   - Overall error rate
   - Error rate by service
   - Error spikes correlated with deployments
   - Top error types

3. **rollback-analysis.json**
   - Rollback rate and frequency
   - Mean time to rollback (MTTR)
   - Rollback reasons breakdown
   - Services with most rollbacks

**How to use**:
1. Start Grafana (local or cloud)
2. Go to Dashboards → Import
3. Upload JSON file
4. Select Prometheus data source
5. View metrics from your deployments

**Note**: These are templates. Your deployer must export the metrics

---

## Integration Patterns

### Pattern 1: Placeholder-Based Learning

All integrations use **placeholders**, so you do not need to sign up first:

```python
# Works without Sentry account
dsn = os.getenv("SENTRY_DSN", "PLACEHOLDER_DSN")

if dsn == "PLACEHOLDER_DSN":
    print("Using placeholder mode")
    return

# Real implementation only runs with actual DSN
sentry_sdk.init(dsn=dsn)
```

You can complete the exercises in simulation mode and add a real service later.

---

### Pattern 2: Progressive Enhancement

Add one integration at a time:

**Exercises 1-2**: The built-in mock supplies metrics
```python
# Simple health check
metrics = {"error_rate": random.uniform(0, 0.01)}
```

**Exercise 3**: Add Sentry integration
```python
# Real errors from Sentry
error_rate = sentry.get_error_rate(service, version)
recent_errors = sentry.get_recent_errors(service, version)
```

**Post-exercises**: Swap the mock for real Prometheus queries
```python
# Real metrics from Prometheus
metrics = await prometheus.query("rate(http_requests_total[5m])")
```

**Post-exercises**: Add Grafana visualization
```python
# Visual dashboards in Grafana
grafana.add_deployment_annotation(service, version, timestamp)
```

---

### Pattern 3: Bi-Directional Integration

Your deployer both sends and receives data:

**Outbound** (Deployer → Observability):
```python
# Report events
sentry.report_deployment_start(service, version, deployment_id)
sentry.report_rollback(service, failed_ver, stable_ver, reason)
```

**Inbound** (Observability → Deployer):
```python
# Query for decisions
error_rate = sentry.get_error_rate(service, version)
if error_rate > threshold:
    await deployer.rollback(config, reason="High error rate")
```


---

## Using This Directory

### For Exercise 3 (Sentry Integration)

**Step 1: Read the overview**
```bash
cat integrations/observability_setup.md
```

**Step 2: Set up Sentry account**
```bash
# Follow guide
cat integrations/sentry_setup.md

# Takes 10-15 minutes
# Free Developer plan: see https://sentry.io/pricing/
```

**Step 3: Implement integration**
```bash
# Open skeleton code
code integrations/sentry_integration.py

# Complete TODOs:
# - Part 1: Initialize Sentry
# - Part 2: Report events
# - Part 3: Query error rates
# - Part 4: Report rollbacks
```

**Step 4: Test integration**
```bash
# Run test script
python integrations/sentry_integration.py

# Check Sentry dashboard
open https://sentry.io
```

**Step 5: Use in deployer**
```python
# In your starter/deployer.py
from integrations.sentry_integration import SentryMonitor

class ZeroDowntimeDeployer:
    def __init__(self, ...):
        self.sentry = SentryMonitor()

    async def deploy(self, config):
        self.sentry.report_deployment_start(...)
        # ... deployment logic ...
        self.sentry.report_deployment_complete(...)
```

---

### For Optional Grafana Visualization

**After completing exercises**, add visualization:

**Step 1: Choose setup**
```bash
# Option A: Local (easier)
docker compose up -d grafana
open http://localhost:3000

# Option B: Cloud (more features)
# See grafana_setup.md
```

**Step 2: Import dashboards**
1. Open Grafana
2. Dashboards → Import
3. Upload from `grafana_dashboards/`
4. Select Prometheus data source

**Step 3: View your deployments**
- See deployment success rates
- Correlate errors with deployments
- Analyze rollback patterns

---

## Requirements

### Minimum (Exercises 1-2)
- Python 3.11+
- Nothing else: metrics are mocked, no signup needed
- Docker only if you want the optional Prometheus and Grafana views

**Setup time**: 0 minutes (already configured)

### For Exercise 3 (Sentry)
- Everything above
- Sentry account (free)
- `sentry-sdk` package (included in requirements.txt)

**Setup time**: 10-15 minutes

### For Grafana (Optional)
- Local: Docker (already have it)
- Cloud: Grafana Cloud account (free)

**Setup time**: 5-10 minutes (local) or 15-20 minutes (cloud)

---

## Dependencies

The only Python package these integrations import is already in the main
`requirements.txt`:

```txt
sentry-sdk>=2.0.0,<3.0   # Sentry integration
```

Prometheus and Grafana run as Docker containers (`docker compose up -d` in
`hands-on-lab/`). They need no extra Python packages.

Install all:
```bash
pip install -r requirements.txt
```

---

## Configuration

All configuration goes in `.env` file (copy from `.env.example`):

```env
# Prometheus (included, no signup)
PROMETHEUS_URL=http://localhost:9090

# Sentry (Exercise 3)
SENTRY_DSN=https://your-key@sentry.io/project
SENTRY_ENVIRONMENT=lab
SENTRY_TRACES_SAMPLE_RATE=1.0

# Grafana (optional)
GRAFANA_URL=http://localhost:3000
GRAFANA_API_KEY=your_service_account_token
```

---

## Testing Integration

### Test Sentry Connection
```bash
python integrations/sentry_integration.py
```

Output with `SENTRY_DSN` set (abridged; the simulated error rate differs per
run):
```text
============================================================
Sentry Integration Test
============================================================

Initializing Sentry monitor...
Sentry initialized (environment: lab)

Testing deployment event reporting...
Deployment start event: sent

Testing error rate retrieval...
Error rate for test-service v1.0.0-test: 0.23%

...
```

Without a DSN it prints `[WARN] Sentry DSN not configured`, and each event
line reads `skipped (placeholder mode, nothing sent)`.

### Test Prometheus Queries
```bash
# Query Prometheus directly
curl "http://localhost:9090/api/v1/query?query=up"

# Or use Python
python -c "
import requests
response = requests.get('http://localhost:9090/api/v1/query', params={'query': 'up'})
print(response.json())
"
```

### Test Complete Integration
```bash
# Run the deployer end to end against mock infrastructure.
# With SentryMonitor wired into your deployer, events fire during these runs.
pytest starter/tests/test_integration.py -v

# Check Sentry for deployment events
# Check Prometheus for metrics
# Check Grafana for visualizations (if configured)
```

---

## Common Issues

### Sentry Events Not Appearing

**Symptom**: Events sent but not in dashboard

**Solutions**:
1. Check DSN is correct in `.env`
2. Verify network connectivity: `curl https://sentry.io`
3. Check Sentry dashboard filters (environment, time range)
4. Look for rate limiting (unlikely with free tier)
5. Run test script: `python integrations/sentry_integration.py`

### Prometheus Has No Data

**Symptom**: Grafana shows "No Data"

**Solutions**:
1. Check Prometheus is running: `docker compose ps prometheus`
2. Check targets: http://localhost:9090/targets
3. Verify services expose /metrics endpoints
4. Check prometheus.yml configuration
5. Restart: `docker compose restart prometheus`

### Import Errors

**Symptom**: `ModuleNotFoundError: No module named 'sentry_sdk'`

**Solution**:
```bash
pip install -r requirements.txt
```

---

## Learning Resources

### Official Documentation
- **Sentry**: https://docs.sentry.io/platforms/python/
- **Prometheus**: https://prometheus.io/docs/
- **Grafana**: https://grafana.com/docs/

### Hands-On Labs
- **Exercise 3**: `exercises/exercise-3-sentry.md`
- **Integration guide**: `sentry_setup.md`
- **Architecture overview**: `observability_setup.md`

### Book References
- **Chapter 11, Section 11.2**: Sentry Seer, CodeRabbit, and the rest of the AI DevOps tool landscape
- **Chapter 11, Section 11.3**: self-healing pipelines, which is what these metrics feed
- **Chapter 11, Section 11.6**: the deployer these dashboards observe

The Prometheus and Grafana wiring is repo-only material. The book does not cover
how to run a metrics stack.

---

## Support

### Getting Help

**Lab-specific questions**:
1. Check the relevant guide in this directory
2. Review exercise instructions
3. Run test scripts to verify setup
4. Check common issues above

**Tool-specific questions**:
1. Consult official documentation (links above)
2. Search community forums
3. Check GitHub issues for known bugs

**Bug reports**:
- Open issue in companion-repo
- Include error messages and logs
- Specify which exercise/integration

---

## Next Steps

1. **Read `observability_setup.md`** for the architecture
2. **Complete Exercises 1-2** without external services
3. **Set up Sentry** when ready for Exercise 3
4. **Explore Grafana** after completing exercises
5. **Customize** dashboards and metrics for your use case

---

## Contributing

To improve these integrations:

**Contribute by**:
- Improving documentation clarity
- Adding more dashboard examples
- Contributing additional integrations
- Sharing production patterns

**Submit**:
- Pull requests to companion-repo
- Include examples and documentation
- Test with clean environment

---

Start with `observability_setup.md` for how the pieces fit, then work through Exercise 3.
