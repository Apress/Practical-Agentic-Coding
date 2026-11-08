# Visual Overview - Chapter 11 Exercises

One-page visual summary of all three exercises. Print or reference while coding.

---

## The Complete Flow

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│                    ZERO-DOWNTIME DEPLOYMENT LIFECYCLE                           │
└────────────────────────────────────────────────────────────────────────────────┘

    [STABLE v1.0 - 100%]
           │
           ↓
    ┌──────────────────┐
    │  Deploy v2.0     │ ← Exercise 1: Validate this works
    │  Canary (10%)    │
    └──────────────────┘
           │
           ↓
    ┌──────────────────┐
    │  Validate Health │ ← Collect metrics, check thresholds
    │  5 minute window │   Query DevMemory for context
    └──────────────────┘
           │
           ├──────────────────┐
           │                  │
        HEALTHY          UNHEALTHY
           │                  │
           ↓                  ↓
    ┌──────────────┐    ┌──────────────┐
    │ Continue     │    │  ROLLBACK    │ ← Exercise 2: Implement this
    │ Rolling Out  │    │  to v1.0     │   Self-healing recovery
    └──────────────┘    └──────────────┘
           │                  │
           ↓                  ↓
    [v2.0 - 100%]      [v1.0 - 100%]
     SUCCESS!           RECOVERED!
           │                  │
           └────────┬─────────┘
                    ↓
              ┌──────────────┐
              │   Sentry     │ ← Exercise 3: Track everything
              │  Reporting   │   Real observability
              └──────────────┘
```

---

## Exercise 1: Canary Validation

### What You Build
A validation system that monitors a canary deployment and decides if it's healthy.

### Key Algorithm
```text
WHILE validation_period_not_over:
    1. Collect metrics (error rate, latency, CPU, memory)
    2. Compare against thresholds
    3. Record issues if thresholds exceeded
    4. Fail fast if critical issues detected
    5. Wait 10 seconds
    REPEAT

IF no issues: return HEALTHY
ELSE: return UNHEALTHY with details
```

### Critical Thresholds
```text
Error Rate:  < 1.0%
Latency P99: < 500ms
CPU Usage:   < 80%
Memory:      < 80%
```

### Key Methods to Implement
- `validate_canary()` - Main validation loop
- `_adjust_thresholds()` - Modify based on history (optional helper the guide suggests)

### Success Criteria
```text
- Collects metrics every 10 seconds
- Checks all 4 metric types
- Queries DevMemory for past issues
- Adjusts thresholds based on history
- Detects and records failures
- Returns detailed results
```

---

## Exercise 2: Automatic Rollback

### What You Build
Self-healing system that automatically recovers from failed deployments.

### Key Algorithm
```text
TRY:
    1. Find stable version (highest traffic %)
    2. Shift 100% traffic to stable version
    3. Remove failed deployment
    4. Wait 30s for stabilization
    5. Verify stable version is healthy
    6. Record rollback in DevMemory
    RETURN success

CATCH Exception:
    ESCALATE to humans (critical!)
    RETURN failure
```

### State Transitions
```text
[Deploying] → [Unhealthy] → [Rolling Back] → [Stable]
                                    ↓
                              [Escalated] (if rollback fails)
```

### Critical Decision Points
```text
No stable version?     → ESCALATE (critical)
Traffic shift fails?   → ESCALATE (critical)
Deployment removal fails? → LOG (warning, not critical)
Still unhealthy?       → ESCALATE (deeper issue)
```

### Key Methods to Implement
- `rollback()` - Main rollback orchestration
- `_get_stable_version()` - Find version to roll back to (optional helper the guide suggests)
- `_escalate_rollback_failure()` - Handle critical failures

### Success Criteria
```text
- Identifies correct stable version
- Shifts all traffic to stable
- Removes failed deployment
- Verifies rollback success
- Records in DevMemory
- Escalates on failures
```

---

## Exercise 3: Sentry Integration

### What You Build
Integration with Sentry for real error tracking and deployment correlation.

### Key Algorithm
```text
ON deployment start:
    → Report to Sentry (with deployment_id tag)

DURING validation:
    → Query Sentry for error rate
    → If high errors: Get error details for context

ON rollback:
    → Report rollback to Sentry
    → Include: versions, reason, outcome

ON completion:
    → Report final status to Sentry
```

### Integration Points
```text
Agent → Sentry (Reporting)
├─ Deployment events
├─ Validation results
└─ Rollback notifications

Sentry → Agent (Querying)
├─ Error rates
├─ Recent error details
└─ Error patterns
```

### Key Methods to Implement
- `SentryMonitor.__init__()` - Initialize SDK
- `report_deployment_start()` - Tag deployment events
- `report_deployment_complete()` - Final status
- `get_error_rate()` - Query metrics (simulated)
- `report_rollback()` - Rollback notifications

### Success Criteria
```text
- Sentry SDK initialized
- Events tagged with deployment_id
- Error rates queried during validation
- Rollbacks reported with context
- Events visible in dashboard (if real DSN)
```

---

## Key APIs Summary

### HealthMonitor
```python
metrics = await health_monitor.collect_metrics(service, version)
# Returns: error_rate, latency_p99, cpu_usage, memory_usage
```

### DevMemory
```python
# Query
past = await memory.recall(query="deployment failure", n_results=5)

# Record
await memory.remember_session(
    session_type="deployment",
    summary="...",
    outcome="success" | "failure"
)
```

### Infrastructure Client
```python
# List
deployments = await infra.list_deployments(service)

# Traffic
await infra.set_traffic(service, version, percentage)

# Remove
await infra.remove_deployment(service, version)
```

### Sentry SDK
```python
# Report (sentry-sdk 2.x: capture inside the scope)
with sentry_sdk.new_scope() as scope:
    scope.set_tag("deployment_id", id)
    capture_message("Event", level="info")

# Query (simulated in this lab)
error_rate = sentry.get_error_rate(service, version)
```

---

## Progression Path

```text
┌─────────────┐
│ Exercise 1  │  Learn: Validation, thresholds, monitoring
│   Canary    │  Difficulty: Intermediate
└──────┬──────┘  Time: 45-60 min
       │
       ↓
┌─────────────┐
│ Exercise 2  │  Learn: Self-healing, state management, escalation
│  Rollback   │  Difficulty: Intermediate-Advanced
└──────┬──────┘  Time: 35-50 min
       │
       ↓
┌─────────────┐
│ Exercise 3  │  Learn: External integration, observability
│   Sentry    │  Difficulty: Intermediate-Advanced
└─────────────┘  Time: 30-75 min (Optional)
```

---

## Common Patterns Across All Exercises

### Async/Await
```python
result = await async_function()  # Always await!
await asyncio.sleep(10)          # Non-blocking sleep
```

### Error Handling
```python
try:
    result = await operation()
    if not result["success"]:
        handle_failure()
except Exception as e:
    escalate(str(e))
```

### Result Structures
```python
return {
    "success": True | False,
    "reason": "Description",
    "details": {...}  # Additional context
}
```

---

## Decision Matrix

### When to Fail Fast (Exercise 1)
```text
Critical issue count > 3    → Fail immediately
Error rate > 5%             → Fail immediately
Latency > 2x threshold      → Fail immediately
Otherwise                   → Continue monitoring
```

### When to Escalate (Exercise 2)
```text
No stable version exists    → ESCALATE
Traffic shift fails         → ESCALATE
Service unhealthy after rollback → ESCALATE
Deployment removal fails    → LOG (not critical)
```

### What to Report to Sentry (Exercise 3)
```text
Deployment start            → INFO level
Canary validated            → INFO level
Validation failed           → WARNING level
Rollback initiated          → WARNING level
Rollback completed          → INFO/ERROR based on outcome
Critical failures           → ERROR level
```

---

## Testing Strategy

### Verify Each Phase

Run from the `hands-on-lab` directory:

```text
Exercise 1:
  pytest starter/tests/test_deployer.py -v -k canary

Exercise 2:
  pytest starter/tests/test_deployer.py -v -k rollback

Exercise 3:
  python integrations/test_sentry_connection.py
```

### Debug Mode
```bash
pytest starter/tests/ -v -s  # Verbose + show prints
```

---

## Quick Troubleshooting

### Issue: Nothing happens
→ Check: Did you `await` the async function?

### Issue: Tests timeout
→ Check: Are you using `asyncio.sleep()` not `time.sleep()`?

### Issue: "No stable version"
→ Check: Do any deployments exist before testing rollback?

### Issue: Threshold always exceeded
→ Check: Are you comparing correctly? (`>` vs `<`)

### Issue: Memory queries return empty
→ Check: Memory is empty on first run (this is expected)

### Issue: Sentry events not appearing
→ Check: Are you using placeholder or real DSN?

---

## Success Pattern

```text
1. Read exercise description
2. Look at architecture diagram
3. Review pseudo-code
4. Write skeleton code
5. Check hints if stuck
6. Run tests frequently
7. Debug with prints
8. Refine implementation
9. All tests pass!
10. Understand why it works
```

---

## Remember

### Do This
- Break problems into small steps
- Test frequently (every 5-10 lines)
- Use print statements to debug
- Read error messages carefully
- Check hints when stuck

### Don't Do This
- Write everything at once
- Skip reading the hints
- Copy-paste without understanding
- Give up after first error
- Ask for complete solution

---

## Learning Goals

By completing these exercises, you will:

- Understand canary deployment patterns
- Implement threshold-based validation
- Build self-healing systems
- Handle complex error scenarios
- Integrate with external observability tools
- Make autonomous deployment decisions
- Debug async Python code
- Design CA/CD pipelines

---

Keep this page open while you code.

**Visual Overview Version**: 1.0
