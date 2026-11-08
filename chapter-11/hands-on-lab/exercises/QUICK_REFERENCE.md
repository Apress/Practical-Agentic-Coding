# Quick Reference Guide - Chapter 11 Exercises

A one-page reference for common patterns and APIs used across all exercises.

---

## Async/Await Patterns

### Calling Async Functions
```python
# WRONG
result = async_function()  # Returns coroutine object, doesn't execute

# CORRECT
result = await async_function()  # Executes and returns result
```

### Sleep in Async Context
```python
# WRONG
import time
time.sleep(10)  # Blocks entire event loop!

# CORRECT
import asyncio
await asyncio.sleep(10)  # Yields control, non-blocking
```

### Defining Async Functions
```python
async def my_function():
    result = await some_async_call()
    return result
```

---

## HealthMonitor API

### Collect Metrics
```python
metrics = await self.health_monitor.collect_metrics(
    service_name="api-service",
    version="2.0.0"
)

# Returns:
{
    "error_rate": 0.005,        # 0.5% (0.0 to 1.0 scale)
    "latency_p99": 245,         # milliseconds
    "cpu_usage": 0.65,          # 65% (0.0 to 1.0 scale)
    "memory_usage": 0.72,       # 72% (0.0 to 1.0 scale)
    "request_count": 1500       # number of requests
}
```

### When to Use
- During canary validation (collect every 10-15 seconds)
- After rollback (verify stable version is healthy)
- For threshold checking

---

## DevMemory API

### Query Past Events
```python
past_issues = await self.memory.recall(
    query="deployment failure api-service",
    n_results=5
)

# Returns:
{
    "episodic": [
        {
            "session_type": "deployment",
            "summary": "Canary failed: api-service v1.5.0",
            "outcome": "failure",
            "timestamp": "2026-02-05T10:23:11Z"
        },
        # ... more results
    ]
}
```

### Record Events
```python
await self.memory.remember_session(
    session_type="deployment",      # or "rollback", "incident"
    summary="Brief description",
    details="More detailed information",
    outcome="success" | "failure" | "partial" | "critical_failure",
    project="service-name",
    metadata={
        "custom_key": "custom_value",
        "duration_seconds": 45
    }
)
```

### When to Use
- Query: Before canary validation (check for past issues)
- Record: After validation failure, after rollback, on critical errors

---

## Infrastructure Client API

### List Deployments
```python
deployments = await self.infra.list_deployments("api-service")

# Returns (the mock always reports a stable 1.0.0 and a 2.0.0 canary):
[
    {
        "name": "api-service-v1.0.0",
        "version": "1.0.0",
        "replicas": 3,
        "traffic_percentage": 90,
        "status": "running"
    },
    {
        "name": "api-service-canary",
        "version": "2.0.0",
        "replicas": 1,
        "traffic_percentage": 10,
        "status": "running"
    }
]
```

### Set Traffic Percentage
```python
result = await self.infra.set_traffic(
    service_name="api-service",
    version="1.0.0",
    percentage=100  # 0-100
)

# Returns:
{
    "success": True,
    "service": "api-service",
    "version": "1.0.0",
    "traffic_percentage": 100
}
```

### Remove Deployment
```python
result = await self.infra.remove_deployment(
    service_name="api-service",
    version="2.0.0"  # The version to remove
)

# Returns:
{
    "success": True,
    "service": "api-service",
    "version": "2.0.0",
    "removed_at": "2026-02-05T10:24:02.511432"
}
```

---

## Configuration Access

### Reading Thresholds
```python
from starter.config import config

# Already converted to the 0-to-1 scale collect_metrics reports
error_threshold = config.thresholds.error_rate       # 0.01
latency_threshold = config.thresholds.latency_p99_ms # 500
cpu_threshold = config.thresholds.cpu_percent        # 0.80
memory_threshold = config.thresholds.memory_percent  # 0.80
```

Read thresholds off `config.thresholds`, not raw `os.getenv`. The `.env` file
stores CPU and memory as whole percents (`CPU_THRESHOLD_PERCENT=80`); Config
divides by 100. Reading the raw env var gives 80.0 against a `cpu_usage` of
0.65, and the check never fires.

### Other Environment Variables
```python
from os import getenv

sentry_dsn = getenv("SENTRY_DSN")
if not sentry_dsn:
    print("Sentry not configured")
```

### Default Thresholds (from .env)
```env
ERROR_RATE_THRESHOLD=0.01        # 1% error rate
LATENCY_P99_THRESHOLD_MS=500     # 500ms p99 latency
CPU_THRESHOLD_PERCENT=80         # whole percent; Config converts to 0.80
MEMORY_THRESHOLD_PERCENT=80      # whole percent; Config converts to 0.80
```

---

## DateTime Operations

### Time Tracking
```python
from datetime import datetime, timedelta

# Start timer
start_time = datetime.now()

# Calculate end time
duration_seconds = 300  # 5 minutes
end_time = start_time + timedelta(seconds=duration_seconds)

# Check if time remaining
while datetime.now() < end_time:
    # Do work
    await asyncio.sleep(10)

# Calculate elapsed time
elapsed = (datetime.now() - start_time).seconds  # In seconds
elapsed_str = datetime.now().isoformat()  # As string
```

---

## Sentry SDK API (Exercise 3)

### Initialize (Once)
```python
import sentry_sdk
from os import getenv

sentry_sdk.init(
    dsn=getenv("SENTRY_DSN"),
    environment=getenv("SENTRY_ENVIRONMENT", "lab"),
    traces_sample_rate=1.0
)
```

### Send Event with Context
```python
import sentry_sdk
from sentry_sdk import capture_message

# new_scope() is the sentry-sdk 2.x API (configure_scope() is deprecated).
# Tags apply to events captured inside the block.
with sentry_sdk.new_scope() as scope:
    # Add tags for filtering
    scope.set_tag("deployment_id", deployment_id)
    scope.set_tag("service", service_name)
    scope.set_tag("version", version)

    # Add context for additional data
    scope.set_context("deployment", {
        "service": service_name,
        "version": version,
        "started_at": datetime.now().isoformat()
    })

    # Send the event
    capture_message(
        "Deployment started: api-service v2.0.0",
        level="info"  # or "warning", "error"
    )
```

---

## Common Patterns

### Checking Thresholds
```python
issues = []

# Check each metric against threshold
if metrics["error_rate"] > thresholds["error_rate"]:
    issues.append({
        "type": "error_rate",
        "value": metrics["error_rate"],
        "threshold": thresholds["error_rate"],
        "message": f"Error rate {metrics['error_rate']:.2%} exceeds {thresholds['error_rate']:.2%}"
    })

# Repeat for latency_p99, cpu_usage, memory_usage
```

### Fail-Fast Detection
```python
# Count critical issues
critical_count = len([
    issue for issue in issues
    if issue["type"] in ["error_rate", "latency_p99"]
])

# Abort early if too many critical issues
if critical_count > 3:
    return {
        "healthy": False,
        "reason": "Multiple critical issues - failing fast",
        "issues": issues
    }
```

### Finding Stable Version
```python
deployments = await self.infra.list_deployments(service_name)

# Never pick the version you are rolling back from
candidates = [d for d in deployments if d.get("version") != failed_version]
if not candidates:
    return None  # Nothing to roll back to

# The stable version is the one serving the most traffic
stable = max(candidates, key=lambda d: d.get("traffic_percentage", 0))
return stable["version"]
```

### Error Handling
```python
try:
    result = await risky_operation()

    if not result["success"]:
        # Handle failure
        await escalate_issue(...)
        return {"success": False}

    # Continue with success path

except Exception as e:
    # Handle exceptions
    await escalate_issue(str(e))
    return {"success": False, "error": str(e)}
```

---

## Return Value Structures

### Validation Result
```python
{
    "healthy": True | False,
    "reason": "Description of outcome",
    "issues": [
        {
            "type": "error_rate",
            "value": 0.023,
            "threshold": 0.01,
            "message": "Error rate 2.3% exceeds 1%"
        }
    ],
    "samples": [
        {
            "timestamp": "2026-02-05T10:23:11Z",
            "metrics": { ... }
        }
    ],
    "duration": 300  # seconds
}
```

### Rollback Result
```python
{
    "success": True | False,
    "stable_version": "1.0.0",
    "duration_seconds": 45,
    "final_health": {
        "error_rate": 0.003,
        "latency_p99": 230
    }
}
```

---

## Testing Commands

### Run Specific Test
```bash
# Exercise 1
pytest starter/tests/test_deployer.py -v -k canary

# Exercise 2
pytest starter/tests/test_deployer.py -v -k rollback

# Exercise 3 (no Sentry tests in the suite; this checks your DSN and SDK)
python integrations/test_sentry_connection.py
```

### Run All Tests
```bash
pytest starter/tests/ -v
```

### Run with Debug Output
```bash
pytest starter/tests/test_deployer.py -v -s
```

---

## Debugging Checklist

When something doesn't work:

### Async Issues
- [ ] Did I `await` all async function calls?
- [ ] Am I using `asyncio.sleep()` not `time.sleep()`?
- [ ] Is my function defined as `async def`?

### API Issues
- [ ] Is the method name spelled correctly?
- [ ] Am I passing all required parameters?
- [ ] Is the return value what I expected? (print it)

### Logic Issues
- [ ] Are my threshold comparisons correct (`>` vs `<`)?
- [ ] Am I checking for `None` before using values?
- [ ] Am I handling both success and failure cases?

### Integration Issues
- [ ] Is `.env` file configured correctly?
- [ ] Are dependencies installed? (`pip install -r requirements.txt`)
- [ ] Is mock infrastructure enabled? (`USE_MOCK_INFRASTRUCTURE=true`)

---

## Key Concepts Reminder

### Exercise 1: Canary Validation
- **Goal**: Detect problems before full rollout
- **Method**: Sample metrics over time, check thresholds
- **Output**: Healthy or unhealthy with detailed reasons

### Exercise 2: Automatic Rollback
- **Goal**: Self-healing - recover from failures automatically
- **Method**: Shift traffic to stable version, verify success
- **Output**: Return to stable state or escalate

### Exercise 3: Sentry Integration
- **Goal**: Real observability integration
- **Method**: Bi-directional communication (report and query)
- **Output**: Events in Sentry dashboard, real error rates

---

## When to Ask for Help

**Try First**:
1. Read the error message carefully
2. Check this quick reference
3. Look at the relevant hint section
4. Review the common pitfalls section

**Ask When**:
- Stuck for 10+ minutes on same issue
- Error message doesn't make sense
- Tests fail with unclear reasons
- You are confused about a concept, not only the syntax

**Don't Ask**:
- "What's the answer?" or "Can you write it for me?"
- Before reading the hints
- Before trying at least one approach

---

## Success Indicators

You're on the right track when:
- Tests are passing (even if not all of them yet)
- Code runs without exceptions
- You can explain what your code does
- You've handled both success and failure cases
- You've added print statements to see what's happening

You're done when:
- All tests pass
- Code handles edge cases
- You understand why it works
- You could explain it to another student

---

**Quick Reference Version**: 1.0
**Covers**: Exercises 1, 2, and 3
