# Exercise 1: Canary Deployment with Health Validation

**Time**: 45-60 minutes
**Difficulty**: Intermediate
**Prerequisites**: Setup complete (run `python verify_setup.py`)

## Learning Objectives

By the end of this exercise, you will:
- Understand canary deployment patterns
- Implement health validation logic
- Use thresholds to determine deployment success
- Integrate with DevMemory for decision-making

## Background

What a canary deployment is and why it works: Chapter 11, Section 11.6.

## The Pattern

```text
Traditional Deployment          Canary Deployment
────────────────────           ──────────────────
v1.0 (100%)                     v1.0 (90%) + v2.0 (10%)
    ↓                                    ↓
v2.0 (100%)                     Monitor canary
  [All users affected]           If healthy: v2.0 (100%)
                                 If unhealthy: Rollback to v1.0
```

### Canary Deployment Flow (Detailed)

```text
┌─────────────────────────────────────────────────────────────────┐
│                   CANARY DEPLOYMENT LIFECYCLE                    │
└─────────────────────────────────────────────────────────────────┘

Step 1: DEPLOY CANARY (10% traffic)
    │
    ├─> Create new pods with v2.0
    └─> Route 10% traffic to canary

Step 2: VALIDATION PERIOD (configurable duration)
    │
    ├─> Collect metrics every N seconds
    │   ├─> Error rate
    │   ├─> Latency (p99)
    │   ├─> CPU usage
    │   └─> Memory usage
    │
    ├─> Compare against thresholds
    │   ├─> error_rate < 1%
    │   ├─> latency_p99 < 500ms
    │   ├─> cpu_usage < 80%
    │   └─> memory_usage < 80%
    │
    └─> Check DevMemory for past issues
        └─> Adjust thresholds if needed

Step 3: DECISION
    │
    ├─> IF healthy:
    │   └─> Continue to Step 4
    │
    └─> IF unhealthy:
        └─> ROLLBACK (Exercise 2)

Step 4: PROGRESSIVE ROLLOUT
    │
    ├─> 10% → 25% → 50% → 100%
    └─> Monitor at each stage
```

## What You'll Build

You implement the `validate_canary()` method in `starter/deployer.py`. It does four things:
1. Collects health metrics over a validation period
2. Checks metrics against thresholds
3. Determines if canary is healthy
4. Returns validation results with reasoning

## Step 1: Review the Starter Code

Open `starter/deployer.py` and locate the `validate_canary()` method:

```python
async def validate_canary(
    self,
    deployment_config: DeploymentConfig,
    duration_seconds: int
) -> Dict:
    """
    Validate canary deployment health.

    TODO: Exercise 1 - Implement this method
    """
    # TODO: Your implementation here
```

The starter file names the first parameter `deployment_config`. The snippets in
this exercise shorten it to `config`. The tests pass the config positionally, so
either name works. Use one name consistently inside your method.

## Step 2: Understand Available Tools

You can use these tools:

### HealthMonitor (already implemented)
```python
from starter.health_monitor import HealthMonitor

health_monitor = HealthMonitor()

# Collect metrics for a service
metrics = await health_monitor.collect_metrics(
    service_name="api-service",
    version="2.0.0"
)

# Returns:
# {
#     "error_rate": 0.005,        # 0.5%
#     "latency_p99": 245,         # milliseconds
#     "cpu_usage": 0.65,          # 65%
#     "memory_usage": 0.72,       # 72%
#     "request_count": 1500
# }
```

### DevMemory (from Chapter 9)
```python
# Query past deployment issues
past_failures = await self.memory.recall(
    query=f"deployment failure {config.service_name}",
    n_results=5
)

# Returns episodic memories of past deployment problems
```

### Configuration Thresholds
```env
# In .env; starter/config.py loads these into config.thresholds
ERROR_RATE_THRESHOLD=0.01           # 1%
LATENCY_P99_THRESHOLD_MS=500        # 500ms
CPU_THRESHOLD_PERCENT=80            # whole percent; Config converts to 0.80
MEMORY_THRESHOLD_PERCENT=80         # whole percent; Config converts to 0.80
```

## Step 3: Implement Validation Logic

### Implementation Strategy (Pseudo-code)

Here is the algorithm in pseudo-code:

```python
# PSEUDO-CODE: validate_canary() algorithm

FUNCTION validate_canary(config, duration_seconds):
    # Phase 1: Initialize
    start_time = current_time()
    end_time = start_time + duration_seconds
    samples = empty_list()
    issues = empty_list()

    # Phase 2: Query historical context
    past_issues = query_memory("deployment failures for " + config.service_name)

    # Phase 3: Adjust thresholds based on history
    thresholds = get_default_thresholds()
    IF past_issues exist:
        thresholds = make_more_strict(thresholds)

    # Phase 4: Monitoring loop
    WHILE current_time() < end_time:
        # Collect current metrics
        metrics = collect_metrics(config.service_name, config.version)
        samples.append(metrics)

        # Check each metric against threshold
        FOR each metric in [error_rate, latency, cpu, memory]:
            IF metric > threshold:
                issues.append(violation_details)

        # Fail-fast: If too many critical issues, abort early
        critical_issues = count_critical(issues)
        IF critical_issues > CRITICAL_THRESHOLD:
            RETURN {healthy: false, reason: "fail-fast"}

        # Wait before next sample
        sleep(sampling_interval)

    # Phase 5: Final decision
    is_healthy = (len(issues) == 0)

    # Phase 6: Record outcome in memory
    IF NOT is_healthy:
        record_failure_in_memory(config, issues)

    RETURN {
        healthy: is_healthy,
        reason: summary_of_issues,
        issues: detailed_list,
        samples: all_samples
    }
```

### Progressive Implementation Hints

<details>
<summary>Hint 1: Setting up the monitoring loop (Click to expand)</summary>

You'll need to:
1. Import `asyncio` for async sleep
2. Import `datetime` and `timedelta` for time tracking
3. Create a while loop that runs until `end_time`
4. Use `await asyncio.sleep(interval)` between samples

Example structure:
```python
while datetime.now() < end_time:
    # Your metric collection here
    await asyncio.sleep(10)  # Sample every 10 seconds
```
</details>

<details>
<summary>Hint 2: Collecting metrics (Click to expand)</summary>

The `HealthMonitor` is already implemented. Use it like:
```python
metrics = await self.health_monitor.collect_metrics(
    service_name=config.service_name,
    version=config.version
)
# Returns dict with: error_rate, latency_p99, cpu_usage, memory_usage
```
</details>

<details>
<summary>Hint 3: Checking thresholds (Click to expand)</summary>

For each metric, compare against threshold:
```python
if metrics["error_rate"] > adjusted_thresholds["error_rate"]:
    issues.append({
        "type": "error_rate",
        "value": metrics["error_rate"],
        "threshold": adjusted_thresholds["error_rate"],
        "message": f"Error rate {metrics['error_rate']:.2%} exceeds threshold"
    })
```

Repeat this pattern for: `latency_p99`, `cpu_usage`, `memory_usage`
</details>

<details>
<summary>Hint 4: Querying DevMemory (Click to expand)</summary>

DevMemory recall is async and returns episodic memories:
```python
past_issues = await self.memory.recall(
    query=f"deployment failure {config.service_name}",
    n_results=5
)

# recall() returns a dict of memory types, so read the list you want
if past_issues.get("episodic"):
    # Adjust thresholds to be more conservative
    pass
```
</details>

<details>
<summary>Hint 5: Fail-fast logic (Click to expand)</summary>

If critical issues appear, do not wait the full duration:
```python
# Count critical issues (error_rate and latency are most critical)
critical_count = len([
    i for i in issues
    if i["type"] in ["error_rate", "latency_p99"]
])

if critical_count > 3:  # Threshold for fail-fast
    return {
        "healthy": False,
        "reason": "Multiple critical issues detected - failing fast",
        "issues": issues
    }
```
</details>

### Implement It

Edit `starter/deployer.py` and implement `validate_canary()`:

```python
async def validate_canary(
    self,
    config: DeploymentConfig,
    duration_seconds: int
) -> dict:
    """Validate canary deployment health."""
    from datetime import datetime, timedelta
    import asyncio

    # TODO 1: Initialize tracking
    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=duration_seconds)
    samples = []
    issues = []

    print(f"Starting canary validation for {duration_seconds}s...")

    # TODO 2: Check DevMemory for past issues
    past_issues = await self.memory.recall(
        query=f"deployment failure {config.service_name}",
        n_results=5
    )

    # If this service has history of specific issues, adjust thresholds
    # (This demonstrates memory-informed decision making from Chapter 9)
    adjusted_thresholds = self._adjust_thresholds(config, past_issues)

    # TODO 3: Collect metrics over validation period
    while datetime.now() < end_time:
        metrics = await self.health_monitor.collect_metrics(
            service_name=config.service_name,
            version=config.version
        )

        samples.append({
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        })

        # TODO 4: Check thresholds in real-time
        # Check error rate
        if metrics["error_rate"] > adjusted_thresholds["error_rate"]:
            issues.append({
                "type": "error_rate",
                "value": metrics["error_rate"],
                "threshold": adjusted_thresholds["error_rate"],
                "message": f"Error rate {metrics['error_rate']:.2%} exceeds {adjusted_thresholds['error_rate']:.2%}"
            })

        # TODO: Add checks for latency, CPU, memory
        # (Similar pattern to error_rate check above)

        # If critical issues detected, fail fast
        if len([i for i in issues if i["type"] in ["error_rate", "latency"]]) > 3:
            return {
                "healthy": False,
                "reason": "Multiple critical issues detected",
                "issues": issues,
                "samples": samples,
                "duration": (datetime.now() - start_time).seconds
            }

        # Wait before next sample (e.g., every 10 seconds)
        await asyncio.sleep(10)

    # TODO 5: Final assessment
    healthy = len(issues) == 0

    result = {
        "healthy": healthy,
        "reason": "All metrics within thresholds" if healthy else f"{len(issues)} threshold violations",
        "issues": issues,
        "samples": samples,
        "duration": duration_seconds
    }

    # TODO 6: Record in DevMemory
    if not healthy:
        await self.memory.remember_session(
            session_type="deployment",
            summary=f"Canary validation failed for {config.service_name} v{config.version}",
            details=f"Issues: {[i['type'] for i in issues]}",
            outcome="failure",
            project=config.service_name
        )

    return result
```

## Step 4: Implement Threshold Adjustment Helper

Add this helper method to adjust thresholds based on memory:

```python
from .config import config   # the global Config, loaded from .env

def _adjust_thresholds(
    self,
    deployment_config: DeploymentConfig,
    past_issues: dict
) -> dict:
    """Adjust thresholds based on past deployment history."""
    # Start from the configured baselines. Read them off config.thresholds
    # rather than os.getenv: Config already converted the percent values in
    # .env (CPU_THRESHOLD_PERCENT=80) into the 0-to-1 fractions that
    # collect_metrics reports. Reading the raw env var gives you 80.0 against
    # a cpu_usage of 0.65, and the CPU check never fires.
    #
    # Keys here match what collect_metrics returns, so the comparisons below
    # line up: error_rate, latency_p99, cpu_usage, memory_usage.
    thresholds = {
        "error_rate": config.thresholds.error_rate,
        "latency_p99": config.thresholds.latency_p99_ms,
        "cpu_usage": config.thresholds.cpu_percent,
        "memory_usage": config.thresholds.memory_percent,
    }

    # If the service has a history of issues, be more conservative
    episodic = past_issues.get("episodic") if past_issues else None
    if episodic:
        print(f"Found {len(episodic)} past issues, tightening thresholds...")
        thresholds["error_rate"] *= 0.5   # Half the usual error budget
        thresholds["latency_p99"] *= 0.8  # 20% tighter latency ceiling

    return thresholds
```

`check_health()` and `monitor_continuously()` in `health_monitor.py` use
different key names: `latency_p99_ms`, `cpu_percent`, and `memory_percent`. You
may pass your threshold dict to those methods instead of comparing metrics
yourself. If you do, rename the keys to match. Otherwise the lookups fall back
to their defaults, and your adjustment is silently ignored.

The book's Section 11.6 listing also adapts the canary duration. A past
memory-leak failure triples the validation window (60s to 180s). The reference
solution in `complete/deployer.py` does the same. It extends `duration_seconds`
when the recall finds a memory-leak record. The tests do not require it. Add it
if you want your deployer to match the book exactly.

## Step 5: Test Your Implementation

Run the tests:

```bash
pytest starter/tests/test_deployer.py -v -k canary
```

Expected output (abridged):
```text
starter/tests/test_deployer.py::test_canary_validation_healthy PASSED
starter/tests/test_deployer.py::test_canary_validation_unhealthy PASSED
starter/tests/test_deployer.py::test_canary_validation_memory_integration PASSED
```

## Step 6: Run the End-to-End Suite

The integration tests run a complete deployment against the mock
infrastructure. A deployment covers the canary, validation, and progressive
traffic shift:

```bash
pytest starter/tests/test_integration.py -v
```

The successful-deployment test should pass. The failed-deployment test keeps
failing until you write a working `rollback()` in Exercise 2.

## Verification Checklist

- [ ] `validate_canary()` collects metrics over validation period
- [ ] Error rate is checked against threshold
- [ ] Latency is checked against threshold
- [ ] CPU and memory usage are checked
- [ ] DevMemory is queried for past issues
- [ ] Thresholds are adjusted based on history
- [ ] Validation result includes reasoning
- [ ] Failed validations are recorded in memory
- [ ] Tests pass: `pytest starter/tests/test_deployer.py -v -k canary`

## Common Pitfalls and Debugging

### Common Mistakes Students Make

1. **Forgetting `await` on async calls**
   ```python
   # WRONG - Missing await
   metrics = self.health_monitor.collect_metrics(...)

   # CORRECT
   metrics = await self.health_monitor.collect_metrics(...)
   ```
   **Symptom**: Code returns coroutine objects or hangs
   **Fix**: Add `await` before all async function calls

2. **Not handling exceptions from metrics collection**
   ```python
   # WRONG - No error handling
   metrics = await self.health_monitor.collect_metrics(...)

   # CORRECT
   try:
       metrics = await self.health_monitor.collect_metrics(...)
   except Exception as e:
       print(f"Failed to collect metrics: {e}")
       # Decide: fail fast or retry?
   ```

3. **Hardcoding threshold values instead of using config**
   ```python
   # WRONG - Hardcoded
   if metrics["error_rate"] > 0.01:

   # CORRECT - Use config
   if metrics["error_rate"] > adjusted_thresholds["error_rate"]:
   ```

4. **Not storing samples for debugging**
   - Always append metrics to `samples` list
   - Include timestamp with each sample
   - You need this data to see what went wrong

5. **Infinite loop - forgetting to advance time**
   ```python
   # WRONG - Loop never ends
   while datetime.now() < end_time:
       metrics = await self.health_monitor.collect_metrics(...)
       # Missing: await asyncio.sleep()

   # CORRECT
   while datetime.now() < end_time:
       metrics = await self.health_monitor.collect_metrics(...)
       await asyncio.sleep(10)  # Important!
   ```

### Debugging Tips

**Problem: Validation always passes even with bad metrics**
- Check threshold comparison logic - are you using `>` or `<` correctly?
- Print threshold values to ensure they're loaded from config
- Verify that the code uses `adjusted_thresholds` and not the default values

**Problem: Validation takes too long**
- Check your `asyncio.sleep()` interval - 10 seconds is recommended
- Verify `duration_seconds` is reasonable (60-300 seconds for testing)
- Use fail-fast logic to abort early on critical issues

**Problem: DevMemory queries return empty results**
- Check that memory is initialized properly
- Try a broader query string
- Remember: memory might be empty on first run (expected behavior)

**Problem: Tests fail with timeout**
- Reduce `duration_seconds` in tests (use 30-60 seconds)
- Ensure mock infrastructure is enabled
- Check async/await syntax is correct

### Common Issues

### Issue: Tests failing with "Mock infrastructure not available"
**Solution**: Ensure `USE_MOCK_INFRASTRUCTURE=true` in `.env`

### Issue: DevMemory import errors
**Solution**: There is nothing to install. This lab ships its own simplified
memory in `starter/memory_integration.py`. The class is `DeploymentMemory`, a
file-backed stand-in for the Chapter 9 system. The test fixtures construct it
for you. If the import fails, you are running pytest from the wrong directory.
Run it from `chapter-11/hands-on-lab`, not from inside `starter/`. The full
Mem0-and-ChromaDB DevMemory is the Chapter 9 lab, at `chapter-09/hands-on-lab/`.

### Issue: Kubernetes connection errors
**Solution**: Check `kubectl cluster-info` works

### Issue: AttributeError on self.health_monitor
**Solution**: The starter's `__init__` already creates `self.health_monitor`, a
`HealthMonitor` around the infrastructure client. You do not need to add one. If
you see this error, `__init__` has probably been edited. Compare it with the
same method in `complete/deployer.py` and restore it.

## Reference: Success Criteria and API Examples

Why the validator samples over time, adjusts thresholds from history, and fails fast: Chapter 11, Section 11.6.

### Success Criteria: How to know you're done

Your implementation is complete when:
- Validation period runs for specified duration (or fails fast)
- Metrics are collected at regular intervals (every 10-15 seconds)
- Each metric type is checked against its threshold
- Issues are recorded with type, value, threshold, and message
- DevMemory is queried and influences threshold adjustment
- Unhealthy validations return `healthy: False` with detailed reasons
- Healthy validations return `healthy: True` with samples
- Failed validations are recorded in DevMemory
- All unit tests pass
- Integration tests show realistic behavior

### API Usage Examples

**Complete example of using the tools together:**

```python
# 1. Query memory for context
past_issues = await self.memory.recall(
    query=f"deployment failure {config.service_name}",
    n_results=5
)

# 2. Get default thresholds from config (already parsed from .env)
from starter.config import config
error_threshold = config.thresholds.error_rate

# 3. Adjust based on history
if past_issues["episodic"]:
    error_threshold *= 0.5  # More strict

# 4. Collect metrics
metrics = await self.health_monitor.collect_metrics(
    service_name=config.service_name,
    version=config.version
)

# 5. Check and record issues
if metrics["error_rate"] > error_threshold:
    issues.append({
        "type": "error_rate",
        "value": metrics["error_rate"],
        "threshold": error_threshold,
        "message": f"Error rate {metrics['error_rate']:.2%} exceeds {error_threshold:.2%}"
    })

# 6. Record failure in memory
if not healthy:
    await self.memory.remember_session(
        session_type="deployment",
        summary=f"Canary failed: {config.service_name} v{config.version}",
        details=f"Issues: {[i['type'] for i in issues]}",
        outcome="failure",
        project=config.service_name
    )
```

## Next Steps

Once your implementation passes tests, move to:
- **Exercise 2**: Automatic Rollback (`exercises/exercise-2-rollback.md`)

## Reference

- **Complete implementation**: `complete/deployer.py`
- **Chapter 11, Section 11.6**: Zero-Downtime Deployer
- **Chapter 9**: DevMemory integration patterns
