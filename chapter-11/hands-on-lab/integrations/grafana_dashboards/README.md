# Grafana Dashboards

Pre-built dashboard templates for Zero-Downtime Deployer metrics.

For the latest import steps, see the [Grafana documentation](https://grafana.com/docs/grafana/latest/).

## Quick Start

### Import a Dashboard

1. **Start Grafana** (local or cloud)
   ```bash
   # Local Grafana
   docker compose up -d grafana
   open http://localhost:3000
   ```

2. **Import Dashboard**
   - Click **+** (sidebar) → **Import**
   - Click **Upload JSON file**
   - Select a dashboard file from this directory
   - Choose **Prometheus** as data source
   - Click **Import**

3. **View Your Metrics**
   - Dashboard will load with your data
   - Metrics populate as deployments run
   - Customize as needed

---

## Available Dashboards

### 1. deployment-metrics.json

**Purpose**: Overall deployment health and performance

**Panels**:
- **Deployment Success Rate**: Percentage of successful deployments
- **Average Deployment Duration**: How long deployments take
- **Deployments Over Time**: Frequency by service
- **Failed Deployments by Service**: Which services fail most
- **Deployment Duration by Service**: Performance comparison

**Use Cases**:
- Monitor deployment reliability
- Identify slow deployments
- Compare services
- Track trends over time

**Metrics Required**:
```promql
deployment_total              # Counter with labels: service, version, status
deployment_success_total      # Counter of successful deployments
deployment_failed_total       # Counter of failed deployments
deployment_duration_seconds   # Histogram of deployment durations
deployment_in_progress        # Gauge of active deployments
```

**Thresholds**:
- Success rate < 90%: Yellow
- Success rate < 80%: Red
- Duration > 5 minutes: Yellow
- Duration > 10 minutes: Red

---

### 2. error-tracking.json

**Purpose**: Correlate errors with deployments

**Panels**:
- **Overall Error Rate**: System-wide error percentage
- **Error Rate by Service**: Per-service breakdown
- **Error Spikes Around Deployments**: Time-series with deployment annotations
- **Error Rate Before vs After Deployment**: Comparison table
- **Top Error Types**: Most common errors (from Sentry)
- **Time to Detect Errors**: How fast errors are caught

**Use Cases**:
- Spot bad deployments quickly
- Understand error patterns
- Validate canary deployments
- Measure detection speed

**Metrics Required**:
```promql
http_requests_total{status=~"5.."}  # Error requests
http_requests_total                  # Total requests
deployment_total                     # For annotations
sentry_errors_total                  # Optional: Sentry integration
error_detection_duration_seconds     # Time to first error
```

**Alerts**:
- Error rate > 5%: Critical
- Error rate > 1%: Warning
- New error type detected: Info

**Deployment Annotations**:
This dashboard shows deployment events as vertical lines on graphs. You can see whether errors spiked after a deployment.

---

### 3. rollback-analysis.json

**Purpose**: Track rollback patterns and recovery

**Panels**:
- **Rollback Rate**: Percentage of deployments rolled back
- **Mean Time to Rollback (MTTR)**: Average recovery time
- **Rollback Success Rate**: How often rollbacks work
- **Total Rollbacks**: Count over time
- **Rollbacks Over Time**: Frequency trends
- **Rollback Reasons Breakdown**: Pie chart of causes
- **Services with Most Rollbacks**: Which services need attention
- **Rollback Duration Distribution**: Heatmap of recovery times
- **Impact: Users Affected**: Business impact of rollbacks
- **Rollback Patterns**: Day/time heatmap

**Use Cases**:
- Measure system resilience
- Identify problematic services
- Understand failure modes
- Optimize rollback procedures
- Track recovery metrics

**Metrics Required**:
```promql
deployment_rollback_total          # Counter with labels: service, reason
rollback_duration_seconds          # Histogram of rollback durations
rollback_success_total             # Successful rollback counter
rollback_affected_users            # Gauge of impacted users
deployment_total                   # For calculating rollback rate
```

**Reference values**:
- **Low rollback rate**: < 5%
- **Fast MTTR**: < 2 minutes

---

## Customizing Dashboards

### Edit Queries

1. Click panel title → **Edit**
2. Modify PromQL query in query editor
3. Adjust time ranges, functions, labels
4. Click **Apply**

### Add New Panels

1. Click **Add panel** (top right)
2. Choose visualization type
3. Write PromQL query
4. Configure display options
5. Set thresholds and alerts

### Variables

Dashboards can use variables for filtering:

```text
$service      - Filter by service name
$environment  - Filter by environment (lab, prod, staging)
$version      - Filter by version
```

To add a variable:
1. Dashboard settings → **Variables**
2. **Add variable**
3. Query: `label_values(service)`
4. Use in queries: `{service="$service"}`

---

## Metrics to Export

For these dashboards to work, your deployer must export these metrics:

### Required Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Deployment metrics
deployment_total = Counter(
    'deployment_total',
    'Total deployments',
    ['service', 'version', 'status']
)

deployment_duration = Histogram(
    'deployment_duration_seconds',
    'Deployment duration',
    ['service']
)

# Error metrics
http_requests_total = Counter(
    'http_requests_total',
    'HTTP requests',
    ['service', 'method', 'status']
)

# Rollback metrics
rollback_total = Counter(
    'deployment_rollback_total',
    'Rollbacks',
    ['service', 'reason']
)

rollback_duration = Histogram(
    'rollback_duration_seconds',
    'Rollback duration',
    ['service']
)
```

### Exposing Metrics

```python
from prometheus_client import start_http_server

# Start metrics server on port 8000
start_http_server(8000)

# Prometheus scrapes http://localhost:8000/metrics
```

---

## PromQL Query Examples

### Deployment Success Rate
```promql
# Success rate over last hour
rate(deployment_success_total[1h])
/
rate(deployment_total[1h])
```

### Error Rate by Service
```promql
# 5xx error rate by service
sum(rate(http_requests_total{status=~"5.."}[5m])) by (service)
/
sum(rate(http_requests_total[5m])) by (service)
```

### P99 Latency
```promql
# 99th percentile latency
histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)
```

### Active Deployments
```promql
# Currently running deployments
sum(deployment_in_progress)
```

### Top Error Services
```promql
# Top 5 services by error count
topk(5,
  sum(rate(http_requests_total{status=~"5.."}[5m])) by (service)
)
```

---

## Alerting Rules

Configure alerts in Grafana or use these Prometheus alert rules:

```yaml
# prometheus_alerts.yml
groups:
  - name: deployment_alerts
    interval: 1m
    rules:
      - alert: HighDeploymentFailureRate
        expr: |
          rate(deployment_failed_total[1h])
          /
          rate(deployment_total[1h]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High deployment failure rate"
          description: "{{ $value | humanizePercentage }} of deployments failing"

      - alert: DeploymentErrorSpike
        expr: |
          rate(http_requests_total{status=~"5.."}[5m])
          /
          rate(http_requests_total[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Error rate spiked after deployment"

      - alert: SlowRollback
        expr: rollback_duration_seconds > 300
        labels:
          severity: warning
        annotations:
          summary: "Rollback taking longer than 5 minutes"
```

---

## Troubleshooting

### Dashboard Shows "No Data"

**Check**:
1. Is Prometheus running? `docker compose ps prometheus`
2. Are services exposing metrics? `curl http://localhost:8000/metrics`
3. Is Prometheus scraping? http://localhost:9090/targets
4. Does time range include data?
5. Are metric names correct?

**Solutions**:
```bash
# Restart Prometheus
docker compose restart prometheus

# Check Prometheus has data
curl "http://localhost:9090/api/v1/query?query=up"

# Verify metric names in Prometheus
open http://localhost:9090/graph
```

### Wrong Metrics Displayed

**Cause**: Metric names don't match dashboard queries

**Solution**:
1. Check actual metric names: http://localhost:9090/graph
2. Edit panel queries to match
3. Update `__name__` in queries

### Queries Too Slow

**Optimize**:
1. Reduce time range (last 6h instead of 7d)
2. Use recording rules in Prometheus
3. Increase dashboard refresh interval
4. Pre-aggregate with `sum()`, `avg()`

---

## Creating Your Own Dashboards

### Export and Share

1. **Export JSON**
   - Dashboard settings → JSON Model
   - Copy JSON

2. **Save to Repo**
   ```bash
   # Save your custom dashboard
   cat > my-dashboard.json
   # Paste JSON, press Ctrl+D
   ```

3. **Share with Team**
   - Commit to git
   - Others import via Grafana UI

---

## Advanced Features

### Template Variables

Create dynamic dashboards:

```text
Variable: service
Query: label_values(deployment_total, service)

Use: {service="$service"}
Result: Dropdown to filter by service
```

### Dashboard Links

Link related dashboards:

```text
Deployment Dashboard → Error Dashboard → Rollback Dashboard
```

### Annotations

Show events on graphs:

```yaml
- name: Deployments
  datasource: Prometheus
  expr: deployment_total
  tagKeys: service,version
  textFormat: "{{service}} v{{version}}"
```

### Conditional Formatting

Change colors based on values:

```text
Value > 0.95: Green background
Value 0.90-0.95: Yellow background
Value < 0.90: Red background
```

---

## Integration with Sentry

For combined view of metrics and errors:

1. **Install Sentry Data Source** in Grafana
2. **Add Sentry panels** to dashboards
3. **Correlate by deployment_id** tag
4. **See both metrics and error details**

Example panel:
```text
Data source: Sentry
Query: Issues filtered by deployment_id
Display: Table with error message, count, URL
```

---

## Dashboard Maintenance

### Regular Updates

- Review and update thresholds quarterly
- Add new panels for new metrics
- Remove unused panels
- Update descriptions as system changes

### Version Control

```bash
# Export all dashboards
for dashboard in *.json; do
  echo "Exporting $dashboard"
  # Use Grafana API to get latest version
done

# Commit to repo
git add grafana_dashboards/
git commit -m "Update Grafana dashboards"
```

---

## Learning Resources

### PromQL
- **Guide**: https://prometheus.io/docs/prometheus/latest/querying/basics/
- **Examples**: https://prometheus.io/docs/prometheus/latest/querying/examples/
- **Functions**: https://prometheus.io/docs/prometheus/latest/querying/functions/

### Grafana
- **Docs**: https://grafana.com/docs/grafana/latest/
- **Dashboards**: https://grafana.com/grafana/dashboards/ (browse public)
- **Tutorials**: https://grafana.com/tutorials/

### Prometheus
- **Best Practices**: https://prometheus.io/docs/practices/naming/
- **Recording Rules**: https://prometheus.io/docs/prometheus/latest/configuration/recording_rules/
- **Alerting**: https://prometheus.io/docs/alerting/latest/overview/

---

## Next Steps

1. **Import dashboards** into your Grafana instance
2. **Run deployments** to generate metrics
3. **View visualizations** in real-time
4. **Customize** for your needs
5. **Create alerts** for critical metrics
6. **Share** with your team

---

These templates are a starting point. Adjust them to match the metrics your deployer exports.
