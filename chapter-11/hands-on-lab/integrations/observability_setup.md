# Observability Stack: quick reference

The observability setup around the Zero-Downtime Deployer.

Why a deployment agent reads metrics and errors: Chapter 11, Section 11.6.

For the latest setup steps, see the vendor docs: [Prometheus](https://prometheus.io/docs/), [Sentry](https://docs.sentry.io/), and [Grafana](https://grafana.com/docs/).

**What runs in this lab and what does not.** The diagrams below show the
production shape. In the lab:

- `health_monitor.py` simulates the Prometheus query. It returns generated numbers.
- `SentryMonitor` simulates error-rate queries.
- The one real connection you can make is Sentry event reporting in Exercise 3.
- Wiring the deployer to a live Prometheus is an extension.

## Architecture Overview

The Zero-Downtime Deployer uses this observability stack:

```text
┌─────────────────────────────────────────────────────────────┐
│                    Your Application                          │
│              (Deployed Services/Containers)                  │
└───────┬─────────────────────────────────────────────┬───────┘
        │                                             │
        │ Exposes /metrics endpoint                   │ Errors/Events
        │                                             │
┌───────▼─────────────────┐               ┌───────────▼─────────┐
│      Prometheus          │               │       Sentry        │
│   (Metrics Storage)      │               │   (Error Tracking)  │
│   - Time-series DB       │               │   - Exception logs  │
│   - Query language       │               │   - Performance     │
│   - Local deployment     │               │   - Cloud service   │
└───────┬─────────────────┘               └──────────┬──────────┘
        │                                            │
        │ Queries                                    │ Queries
        │                                            │
┌───────▼─────────────────────────────────────────┬──▼──────────┐
│            Zero-Downtime Deployer                             │
│                 (Your CA/CD Agent)                            │
│  - Queries Prometheus for health metrics                      │
│  - Queries Sentry for error rates                             │
│  - Makes deployment decisions                                 │
│  - Triggers rollbacks if unhealthy                            │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         │ Optional: Visualization
                         │
              ┌──────────▼─────────────┐
              │       Grafana          │
              │   (Visualization)      │
              │   - Dashboards         │
              │   - Alerts             │
              │   - Cloud/Local        │
              └────────────────────────┘
```

This diagram is the production shape the lab imitates. In the exercises, the
health monitor simulates the metric reads (`USE_MOCK_INFRASTRUCTURE=true`). You
do not need any of these services to finish the lab. Use them when you want the
real stack around your deployer.

---

## Components

### 1. Prometheus (Included - No Signup)

**What it is**: Open-source time-series database for metrics

**Role in Lab**:
- Stores metrics from deployed services
- Provides query interface for health checks
- Runs locally via docker-compose
- No external signup required

**What You Get**:
- HTTP request rates
- Latency percentiles (p50, p99)
- CPU and memory usage
- Custom application metrics

**Setup**:
- Already configured in `docker-compose.yml`
- Runs at: http://localhost:9090
- Config file: `prometheus.yml`

**How a production deployer uses it** (the lab's health monitor simulates
these reads):
```python
# Query error rate
error_rate = await prometheus.query(
    'rate(http_requests_total{status=~"5.."}[5m])'
)

# Query latency
p99_latency = await prometheus.query(
    'histogram_quantile(0.99, http_request_duration_seconds)'
)
```

**Access Dashboard**:
```bash
# Start Prometheus
docker compose up -d prometheus

# Open browser
open http://localhost:9090
```

### 2. Sentry (Exercise 3 - Free Signup)

**What it is**: Error tracking platform

**Role in Lab**:
- Tracks application errors in real-time
- Correlates errors with deployments
- Provides error rate metrics
- Alerts on error spikes

**What You Get** (Free Tier):
- A free tier that covers this lab (check sentry.io/pricing for current quotas)
- Full error tracking
- Email alerts
- Stack traces and context

**Setup**:
- Sign up: https://sentry.io/signup/
- Follow: `integrations/sentry_setup.md`
- Configure in: `.env` file

**How Deployer Uses It**:
```python
# Initialize Sentry
from integrations.sentry_integration import SentryMonitor
sentry = SentryMonitor()

# Report deployment
sentry.report_deployment_start(service, version, deployment_id)

# Check error rate during canary
error_rate = sentry.get_error_rate(service, version, minutes=5)

# Rollback if errors spike
if error_rate > threshold:
    sentry.report_rollback(service, failed_ver, stable_ver, reason)
```

**Access Dashboard**:
- Web: https://sentry.io/
- View errors, trends, releases

### 3. Grafana (Optional - Advanced)

**What it is**: Visualization and dashboarding platform

**Role in Lab**:
- Visualizes Prometheus metrics
- Creates deployment dashboards
- Sets up alerts
- Optional: Not required for exercises

**What You Get** (Free Cloud):
- 14-day full-featured trial
- 10K Prometheus series
- 50GB logs
- 14 days retention after trial

**Setup Options**:

**Option A: Grafana Cloud** (production-like)
```bash
# See grafana_setup.md for detailed steps
# 1. Sign up at grafana.com
# 2. Create an access policy token
# 3. Add to .env
```

**Option B: Local Grafana** (Simpler, recommended for the lab)
```bash
# Already in docker-compose.yml
docker compose up -d grafana

# Access at http://localhost:3000
# The lab compose enables anonymous access with admin rights, no login needed
# (admin/admin if you are ever prompted)
```

**Pre-built Dashboards**:
- `grafana_dashboards/deployment-metrics.json`
- `grafana_dashboards/error-tracking.json`
- `grafana_dashboards/rollback-analysis.json`

---

## Data Flow

### Deployment Lifecycle with Observability

```text
1. Deployment Starts
   ├─> Deployer reports to Sentry: "Deployment started"
   └─> Tags: service, version, deployment_id

2. Canary Deployed
   ├─> Service exposes /metrics endpoint
   ├─> Prometheus scrapes metrics every 15s
   └─> Service reports errors to Sentry

3. Validation Phase
   ├─> Deployer queries Prometheus:
   │   ├─ Error rate from http_requests_total
   │   ├─ Latency from http_request_duration
   │   └─ Resource usage from container metrics
   └─> Deployer queries Sentry:
       ├─ Real-time error count
       └─ Error details for debugging

4. Decision Point
   If healthy:
       ├─> Continue deployment
       ├─> Shift more traffic to canary
       └─> Report success to Sentry
   If unhealthy:
       ├─> Trigger rollback
       ├─> Report rollback to Sentry
       └─> Include error context in report

5. Completion
   ├─> Deployer reports final status to Sentry
   ├─> Metrics continue to Prometheus
   └─> Grafana shows deployment timeline (optional)
```

### Context Propagation

The deployment_id flows through all systems:

```text
deployment_id: "api-v2.0.1-20260205123045"
    │
    ├─> Sentry events tagged with deployment_id
    ├─> Prometheus metrics labeled with version
    ├─> Grafana annotations show deployment events
    └─> Logs include deployment_id for correlation
```

With a shared `deployment_id` you can:
- Filter Sentry errors by deployment
- Compare metrics before/after deploy
- Correlate errors with specific versions
- Debug issues by tracing context

---

## What You Need for Each Exercise

### Exercise 1: Canary Deployment
**Required**:
- Nothing beyond the lab setup; the health monitor simulates metrics

**Optional**:
- Prometheus and Grafana (`docker compose up -d`) to watch the run

**Setup Time**: 0 minutes (already configured)

### Exercise 2: Rollback
**Required**:
- Nothing new; same mock metrics and thresholds as Exercise 1

**Optional**:
- Grafana for a rollback dashboard

**Setup Time**: 0 minutes (builds on Exercise 1)

### Exercise 3: Sentry Integration
**Required**:
- Sentry (free signup required)

**Setup Time**: 10-15 minutes
- Create Sentry account
- Get DSN
- Configure .env

**Optional**:
- Grafana for combined metrics view

---

## Configuration Reference

### .env Configuration

```env
# Prometheus (included, no signup)
PROMETHEUS_URL=http://localhost:9090

# Sentry (Exercise 3, free signup)
SENTRY_DSN=https://your-key@o123.ingest.sentry.io/456
SENTRY_ENVIRONMENT=lab
SENTRY_TRACES_SAMPLE_RATE=1.0

# Grafana (optional)
GRAFANA_URL=http://localhost:3000
GRAFANA_API_KEY=your_service_account_token
```

### Docker Services

```yaml
# docker-compose.yml includes:
services:
  prometheus:
    ports: 9090
    volumes: ./prometheus.yml

  grafana:  # Optional
    ports: 3000
```

---

## Troubleshooting

### Prometheus Not Accessible

**Symptom**: Can't reach http://localhost:9090

**Solutions**:
```bash
# Check if Prometheus is running
docker compose ps

# Start Prometheus
docker compose up -d prometheus

# Check logs
docker compose logs prometheus

# Verify prometheus.yml syntax
docker compose config
```

### No Metrics Available

**Symptom**: Prometheus has no data

**Solutions**:
1. Check if services expose /metrics endpoint
2. Verify `prometheus.yml` has correct scrape configs
3. Check Prometheus targets page: http://localhost:9090/targets
4. Services must be labeled correctly

### Sentry Not Receiving Events

**Symptom**: Events not appearing in dashboard

**Solutions**:
1. Verify DSN in .env is correct
2. Check network connectivity to sentry.io
3. Test with simple script (see sentry_setup.md)
4. Check Sentry project settings
5. Look for rate limiting (unlikely with free tier)

### Grafana Can't Connect to Prometheus

**Symptom**: Grafana shows "No data"

**Solutions**:
1. Add Prometheus data source in Grafana
2. Use URL: http://prometheus:9090 (Docker) or http://localhost:9090 (local)
3. Test connection in data source settings
4. Check both are on same network

---

## Monitoring the Monitor

Check that your observability stack is working:

### Quick Health Check

```bash
# Check all services
docker compose ps

# Test Prometheus
curl http://localhost:9090/-/healthy

# Test Grafana (if using)
curl http://localhost:3000/api/health

# Test Sentry connection
python integrations/test_sentry_connection.py
```

### Metrics to Watch

**Prometheus**:
- Scrape duration: Should be < 1s
- Scrape success rate: Should be 100%
- Storage usage: Should have space

**Sentry**:
- Event quota: stay inside the free tier (current quota on the vendor's pricing page)
- Ingestion lag: Should be < 1 minute
- Alert delivery: Test with dummy events

---

## Cost Optimization

All tools in this lab have free tiers:

| Tool       | Free Tier           | Cost if Exceeded        |
|------------|---------------------|-------------------------|
| Prometheus | Unlimited (local)   | Storage only            |
| Sentry     | Free tier covers the lab | See sentry.io/pricing |
| Grafana    | Local unlimited     | See grafana.com/pricing |

**Staying Free**:
- Use local Prometheus (no cost)
- Use Sentry free tier (plenty for lab)
- Use local Grafana or skip it
- Sample transactions if needed

---

## Next Steps

1. **Complete Setup**:
   - Verify Prometheus: `docker compose up -d prometheus`
   - For Exercise 3: Setup Sentry (see `sentry_setup.md`)

2. **Run Exercises**:
   - Exercise 1: Use Prometheus metrics
   - Exercise 2: Add rollback logic
   - Exercise 3: Integrate Sentry

3. **Explore Dashboards**:
   - Prometheus: http://localhost:9090
   - Sentry: https://sentry.io
   - Grafana (optional): http://localhost:3000

4. **Learn More**:
   - Prometheus query language (PromQL)
   - Sentry SDK features
   - Grafana dashboard creation

---

## Reference Documentation

### Official Docs
- **Prometheus**: https://prometheus.io/docs/
- **Sentry**: https://docs.sentry.io/
- **Grafana**: https://grafana.com/docs/

### Lab-Specific Guides
- `sentry_setup.md` - Sentry account and configuration
- `grafana_setup.md` - Optional Grafana setup
- `exercises/exercise-3-sentry.md` - Full Sentry integration guide

### Book References
- **Chapter 11, Section 11.2**: Sentry Seer, CodeRabbit, and the rest of the AI DevOps tool landscape
- **Chapter 11, Section 11.3**: self-healing pipelines, which is what these metrics feed
- **Chapter 11, Section 11.6**: the deployer these dashboards observe

The Prometheus and Grafana wiring is repo-only material. The book does not cover
how to run a metrics stack.

---

Next, start the exercises.
