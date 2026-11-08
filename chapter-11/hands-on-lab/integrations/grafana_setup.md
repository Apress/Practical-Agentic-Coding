# Grafana Setup Guide (Optional)

Grafana charts the metrics that Prometheus and Sentry collect. This guide covers local and cloud setup.

These steps summarize Grafana's own docs. For the latest, see the [Grafana documentation](https://grafana.com/docs/).

**Note**: Grafana is **optional** for the hands-on labs. You can complete all exercises without it. Use Grafana if you want to:
- Visualize deployment metrics over time
- Create custom dashboards
- Set up advanced alerting
- Learn production observability tools

---

## Option 1: Local Grafana (Recommended for Lab)

Run Grafana locally with Docker. No signup is required.

### Start Grafana

Grafana is already configured in `docker-compose.yml`:

```bash
# Start Grafana
cd /path/to/Practical-Agentic-Coding/chapter-11/hands-on-lab
docker compose up -d grafana

# Verify it's running
docker compose ps grafana
```

### Access Grafana

1. Open browser to: **http://localhost:3000**
2. The lab's `docker-compose.yml` enables anonymous access with admin rights,
   so no login is required
3. If you are prompted anyway (for example, on your own Grafana instance), the
   default is `admin` / `admin`, and you can skip the change-password prompt
   for the lab

### Add Prometheus Data Source

Tell Grafana where to get metrics:

1. In Grafana, open **Connections** → **Data sources** (Grafana 10 and later; older versions put this under the gear icon)
2. Click **Add data source**
3. Select **Prometheus**
4. Configure:
   - **Name**: `Prometheus`
   - **URL**: `http://prometheus:9090` (Docker network) or `http://localhost:9090`
   - Leave other settings default
5. Click **Save & Test**
6. You should see: "Data source is working"

### Import Pre-built Dashboards

The lab includes dashboard templates:

1. In Grafana, click **+** → **Import**
2. Click **Upload JSON file**
3. Select a dashboard from `integrations/grafana_dashboards/`:
   - `deployment-metrics.json` - Deployment success, duration, frequency
   - `error-tracking.json` - Error rates over time
   - `rollback-analysis.json` - Rollback frequency and causes
4. Select **Prometheus** as data source
5. Click **Import**

### Stop Grafana

When done:
```bash
docker compose stop grafana
```

---

## Option 2: Grafana Cloud (Advanced)

Use Grafana's cloud service for a setup closer to production.

### Sign Up

1. Go to: **https://grafana.com/auth/sign-up/create-user**
2. Sign up with email or Google/GitHub
3. Choose:
   - Free tier (14-day full trial, then limited free forever)
   - No credit card required

### What You Get (Free Tier)

**During 14-day trial**:
- Full features
- 10K Prometheus series
- 50GB logs
- 50GB traces

**After trial (Free Forever tier)**:
- 10K Prometheus series
- 14 days metrics retention
- 3 users
- Community support

This is enough for the lab and small projects.

### Create Stack

After signup:

1. Create a **Stack** (your Grafana instance)
   - Name: `zero-downtime-lab`
   - Region: Choose closest to you
2. Wait for stack provisioning (~1 minute)
3. Click **Launch** to open your Grafana instance

### Create an Access Policy Token

Grafana Cloud API keys are deprecated. Access policy tokens replace them. To send metrics from your lab to Grafana Cloud:

1. In the Grafana Cloud portal, select your organization, then under **Security** select **Access Policies**
2. Click **Create access policy** and configure:
   - **Display name**: `lab-metrics`
   - **Realm**: your `zero-downtime-lab` stack
   - **Scopes**: `metrics:write` and `metrics:read`
3. Click **Create**
4. On the new policy, click **Add token**, enter a name, optionally set an **Expiration date**, and click **Create**
5. **IMPORTANT**: Copy the token now. You cannot see it again.

### Configure Lab Environment

Add Grafana Cloud settings to your `.env`:

```bash
cd /path/to/Practical-Agentic-Coding/chapter-11/hands-on-lab
```

Edit `.env` and add:

```env
# Grafana Cloud Configuration
GRAFANA_CLOUD_URL=https://your-stack-name.grafana.net
GRAFANA_CLOUD_API_KEY=your_access_policy_token_here
GRAFANA_CLOUD_PROMETHEUS_URL=https://prometheus-prod-XX-prod-us-central-0.grafana.net
GRAFANA_CLOUD_PROMETHEUS_USER=123456
```

**Finding your URLs**:
1. In Grafana Cloud home page
2. Click **Details** on Prometheus card
3. Copy **Remote Write Endpoint** URL and user ID

### Add Prometheus Data Source (Cloud)

1. In your Grafana Cloud instance
2. Go to **Connections** → **Data sources**
3. Click **Add data source**
4. Select **Prometheus**
5. Configure:
   - **Name**: `Prometheus`
   - **URL**: Your Prometheus Cloud URL (from setup)
   - **Basic Auth**: Enabled
   - **User**: Your Prometheus user ID
   - **Password**: Your access policy token
6. Click **Save & Test**

### Import Dashboards

Same as local Grafana:
1. Click **+** → **Import**
2. Upload JSON from `integrations/grafana_dashboards/`
3. Select Prometheus data source
4. Click **Import**

---

## Dashboard Overview

### Deployment Metrics Dashboard

Shows overall deployment health:

**Panels**:
- Deployment success rate over time
- Average deployment duration
- Deployments per day
- Failed deployments by service
- Deployment frequency heatmap

**Use Cases**:
- Track if deployments are getting slower
- Identify which services fail most often
- See deployment patterns by day and time

### Error Tracking Dashboard

Correlates errors with deployments:

**Panels**:
- Error rate by service version
- Error spikes correlated with deployments
- Top 10 error types
- Error rate before/after deployment
- Time to detect errors

**Use Cases**:
- See if new deployments introduce errors
- Measure how quickly errors are detected
- Compare error rates across versions

### Rollback Analysis Dashboard

Tracks rollback patterns:

**Panels**:
- Rollback frequency
- Time to rollback (how fast can you recover)
- Rollback reasons breakdown
- Services with most rollbacks
- Rollback success rate

**Use Cases**:
- Identify problematic services
- Measure recovery time
- Understand why rollbacks happen

---

## Creating Custom Dashboards

### Basic Panel Creation

1. Click **+** → **Create Dashboard**
2. Click **Add new panel**
3. In query editor, enter PromQL query:
   ```promql
   # Example: Request rate by service
   rate(http_requests_total[5m])
   ```
4. Choose visualization type (Graph, Stat, Gauge, etc.)
5. Configure panel options (title, unit, thresholds)
6. Click **Apply**

### Example Queries

**Deployment Success Rate**:
```promql
rate(deployment_success_total[1h])
/
rate(deployment_total[1h])
```

**Error Rate**:
```promql
rate(http_requests_total{status=~"5.."}[5m])
/
rate(http_requests_total[5m])
```

**P99 Latency**:
```promql
histogram_quantile(0.99,
  rate(http_request_duration_seconds_bucket[5m])
)
```

**Current Active Deployments**:
```promql
sum(deployment_in_progress)
```

### Dashboard Variables

Create variables for filtering:

1. Dashboard settings → **Variables** → **Add variable**
2. Common variables:
   - **service**: `label_values(service)`
   - **environment**: `label_values(environment)`
   - **version**: `label_values(version)`
3. Use in queries: `{service="$service"}`

---

## Alerting with Grafana

Set up alerts for deployment issues:

### Create Alert Rule

1. Edit a panel with a critical metric
2. Click **Alert** tab
3. Click **Create alert**
4. Configure:
   - **Name**: "High Error Rate After Deployment"
   - **Condition**: `WHEN avg() OF query(A, 5m) IS ABOVE 0.05`
   - **For**: 2m (wait 2 minutes before alerting)
5. Add **Notification channel** (email, Slack, webhook)

### Example Alert Rules

**High Error Rate**:
```text
Error rate > 5% for 2 minutes
→ Alert: Possible bad deployment
```

**Slow Deployments**:
```text
Deployment duration > 10 minutes
→ Alert: Deployment stuck?
```

**Rollback Detected**:
```text
Rollback event occurs
→ Notify: Automatic rollback triggered
```

### Notification Channels

Configure where alerts go:

1. **Alerting** → **Notification channels** → **Add channel**
2. Choose type:
   - **Email**: Get alerts via email
   - **Slack**: Post to Slack channel
   - **Webhook**: Call your deployer API
   - **PagerDuty**: For critical issues
3. Configure and test

---

## Annotations for Deployments

Show deployment events on graphs:

### Manual Annotations

API keys are deprecated in Grafana. Use a service account token:

1. In Grafana, open **Administration** → **Users and access** → **Service accounts** → **Add service account**.
2. Enter a display name, set **Role** to **Editor**, and click **Create**.
3. Click **Add service account token** → **Generate token**, and copy the token.
4. Use it for `YOUR_SERVICE_ACCOUNT_TOKEN` below and as `GRAFANA_API_KEY` in the Python example.

```bash
# POST annotation to Grafana API
curl -X POST http://localhost:3000/api/annotations \
  -H "Authorization: Bearer YOUR_SERVICE_ACCOUNT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Deployed api v2.0.1",
    "tags": ["deployment", "api"],
    "time": 1612137600000
  }'
```

### Automatic Annotations

In your deployer code:

```python
import requests

def report_deployment_to_grafana(service, version, timestamp):
    """Add deployment annotation to Grafana."""
    url = os.getenv("GRAFANA_URL") + "/api/annotations"
    headers = {
        "Authorization": f"Bearer {os.getenv('GRAFANA_API_KEY')}",
        "Content-Type": "application/json"
    }
    data = {
        "text": f"Deployed {service} v{version}",
        "tags": ["deployment", service],
        "time": timestamp * 1000  # Grafana uses milliseconds
    }
    requests.post(url, headers=headers, json=data)
```

---

## Grafana with Sentry

Connect Sentry data to Grafana to see both in one place:

### Sentry Data Source Plugin

1. In Grafana, go to **Administration** → **Plugins and data** → **Plugins**
2. Search for "Sentry"
3. Install **Sentry** plugin
4. Configure:
   - **Organization**: Your Sentry org slug
   - **Auth Token**: Create in Sentry Settings → Auth Tokens
5. Create panels querying Sentry data

### Unified Dashboard

Combine Prometheus and Sentry:
- Left panels: Prometheus metrics (latency, throughput)
- Right panels: Sentry errors (error count, types)
- See correlation: "Latency spike → Error spike"

---

## Troubleshooting

### Dashboard Shows "No Data"

**Check**:
1. Data source connected? (Connections → Data sources)
2. Prometheus has data? (http://localhost:9090)
3. Query correct? (test in Prometheus first)
4. Time range includes data?

**Solutions**:
```bash
# Test Prometheus connection
curl http://localhost:9090/api/v1/query?query=up

# Check Grafana logs
docker compose logs grafana

# Restart services
docker compose restart grafana prometheus
```

### "Origin not allowed" Error

**Cause**: CORS issue with Grafana Cloud

**Solution**:
Add to `.env`:
```env
GF_SERVER_ROOT_URL=http://localhost:3000
GF_AUTH_ANONYMOUS_ENABLED=true
```

### Dashboards Not Importing

**Cause**: JSON format or data source mismatch

**Solutions**:
1. Check JSON is valid (use jsonlint.com)
2. Update data source UIDs in JSON
3. Manually recreate if needed

---

## Exporting and Sharing

### Export Dashboard JSON

1. Dashboard → Settings (gear icon) → JSON Model
2. Copy JSON
3. Save to `integrations/grafana_dashboards/my-dashboard.json`
4. Commit to repo for team sharing

### Import Dashboard

```bash
# Using Grafana API
curl -X POST http://localhost:3000/api/dashboards/db \
  -H "Authorization: Bearer YOUR_SERVICE_ACCOUNT_TOKEN" \
  -H "Content-Type: application/json" \
  -d @integrations/grafana_dashboards/deployment-metrics.json
```

---

## Cost Management

### Staying Free (Cloud)

- Monitor your usage in Grafana Cloud home
- Active series count should stay under 10K
- Delete unused dashboards
- Use sampling for high-cardinality metrics

### When to Upgrade

Consider paid plan if:
- Need > 10K active series
- Need longer retention (> 14 days)
- Need more users (> 3)
- Need advanced features (SLOs, synthetic monitoring)

**Pricing**: check the current plans at grafana.com/pricing

---

## Next Steps

### If Using Local Grafana:
1. Start: `docker compose up -d grafana`
2. Access: http://localhost:3000
3. Add Prometheus data source
4. Import dashboards
5. Explore during exercises

### If Using Grafana Cloud:
1. Sign up at grafana.com
2. Create stack
3. Create an access policy token
4. Configure .env
5. Connect Prometheus data source

### Skip for Now?
- That is fine. Grafana is optional
- Complete exercises using Prometheus directly
- Add Grafana later if you want visualization
- All functionality works without it

---

## Learning Resources

### Official Documentation
- **Getting Started**: https://grafana.com/docs/grafana/latest/getting-started/
- **Dashboards**: https://grafana.com/docs/grafana/latest/dashboards/
- **Alerting**: https://grafana.com/docs/grafana/latest/alerting/

### Community Dashboards
- Browse: https://grafana.com/grafana/dashboards/
- Search for: "Kubernetes", "Prometheus", "Deployment"
- Import dashboard ID in Grafana

### Video Tutorials
- Grafana YouTube: https://www.youtube.com/c/Grafana
- Prometheus and Grafana tutorials
- Dashboard creation guides

---

## Reference

- **Grafana Docs**: https://grafana.com/docs/
- **PromQL**: https://prometheus.io/docs/prometheus/latest/querying/basics/
- **Lab Dashboards**: `integrations/grafana_dashboards/`
- **Book chapter**: Chapter 11, Section 11.6, the deployer these dashboards observe (the Grafana setup itself is repo-only material)

---

Grafana charts whatever your deployer exports. The dashboards here are a starting point.
