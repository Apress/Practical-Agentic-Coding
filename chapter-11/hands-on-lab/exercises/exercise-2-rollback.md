# Exercise 2: Automatic Rollback

**Time**: 35-50 minutes
**Difficulty**: Intermediate-Advanced
**Prerequisites**: Exercise 1 completed

## Learning Objectives

By the end of this exercise, you will:
- Implement automatic rollback logic
- Handle rollback failures gracefully
- Record rollback decisions in DevMemory
- Understand self-healing pipeline patterns

## Background

Why automatic rollback matters in CA/CD: Chapter 11, Sections 11.3 and 11.6.

## The Rollback Pattern

```text
Deployment Flow with Rollback
──────────────────────────────

v1.0 (100%)
    ↓
Deploy v2.0 canary (10%)
    ↓
Validate health
    ↓
┌───────────────┐
│ Is healthy?   │
└───────┬───────┘
        │
    ┌───┴───┐
    │       │
   YES      NO
    │       │
    ↓       ↓
Continue   ROLLBACK
shifting   to v1.0
traffic    ↓
           Alert team
           ↓
           Record in memory
```

### Deployment State Machine

The rollback logic follows these state transitions:

```text
┌─────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT STATES                         │
└─────────────────────────────────────────────────────────────┘

    [STABLE]                    Initial state - production running
       │
       ↓
   [DEPLOYING]                  New version being deployed
       │
       ├──────────────────┐
       ↓                  ↓
   [VALIDATING]       [DEPLOY_FAILED]
       │                  │
       │                  ↓
       ├────────┐    [ROLLING_BACK]
       ↓        ↓         │
   [HEALTHY] [UNHEALTHY]  │
       │        │         │
       ↓        ↓         ↓
   [ROLLING]  [ROLLING_BACK]
     OUT         │
       │         ├──────────┐
       ↓         ↓          ↓
    [STABLE]  [STABLE]  [ESCALATED]
              (success)   (critical)
```

### Detailed Rollback Flow

```text
ROLLBACK INITIATED
    │
    ↓
Step 1: IDENTIFY STABLE VERSION
    │   └─> Query infrastructure for current deployments
    │   └─> Find version with highest traffic (the stable one)
    │   └─> Verify version exists and is running
    │
    └─> If no stable version: ESCALATE (critical)
    │
    ↓
Step 2: SHIFT TRAFFIC
    │   └─> Set stable version to 100% traffic
    │   └─> This immediately stops routing to bad version
    │
    └─> If traffic shift fails: ESCALATE (critical)
    │
    ↓
Step 3: REMOVE FAILED DEPLOYMENT
    │   └─> Delete pods running bad version
    │   └─> Free up resources
    │
    └─> If removal fails: LOG WARNING (not critical)
    │
    ↓
Step 4: VERIFY ROLLBACK SUCCESS
    │   └─> Wait 30s for stabilization
    │   └─> Collect metrics on stable version
    │   └─> Check: error_rate < 1%, latency < 500ms
    │
    └─> If still unhealthy: ESCALATE (deeper issue)
    │
    ↓
Step 5: RECORD IN MEMORY
    │   └─> Store: what failed, why, how long rollback took
    │   └─> Future deployments learn from this
    │
    ↓
ROLLBACK COMPLETE
```

## What You'll Build

You implement the `rollback()` method in `starter/deployer.py`. It does five things:
1. Stops traffic to the failing version
2. Removes unhealthy pods
3. Ensures stable version is serving 100% traffic
4. Records the rollback event in DevMemory
5. Handles rollback failures

## Step 1: Review the Starter Code

Open `starter/deployer.py` and locate the `rollback()` method:

```python
async def rollback(
    self,
    deployment_config: DeploymentConfig,
    reason: str
) -> Dict:
    """
    Rollback to previous stable version.

    TODO: Exercise 2 - Implement this method
    """
    # TODO: Your implementation here
```

The starter docstring lists the full requirements and hints. It returns a
placeholder success dict for now. Delete that when you implement the method.

- As in Exercise 1, the snippets below shorten `deployment_config` to `config`. The tests pass the config positionally, so either name works.
- Keep `reason` as the second parameter name. The tests pass it as a keyword.

## Step 2: Understand the Context

When `rollback()` is called:
- **Current state**: New version (v2.0) is deployed as canary
- **Desired state**: Old version (v1.0) serving 100% traffic, v2.0 removed
- **Reason**: Why the rollback runs (e.g., "High error rate")

## Step 3: Implement Rollback Logic

### Implementation Strategy (Pseudo-code)

Here is the rollback algorithm in pseudo-code:

```python
# PSEUDO-CODE: rollback() algorithm

FUNCTION rollback(config, reason):
    print("Starting rollback:", reason)
    start_time = now()

    TRY:
        # Phase 1: Find the stable version to roll back to
        stable_version = find_stable_version(config.service_name)

        IF stable_version is None:
            # Critical: No stable version to roll back to!
            escalate("Cannot find stable version")
            RETURN failure_result

        # Phase 2: Shift traffic to stable version
        traffic_result = shift_traffic_to(
            service=config.service_name,
            version=stable_version,
            percentage=100
        )

        IF traffic_result failed:
            # Critical: Traffic shift is the most important operation
            escalate("Traffic shift failed")
            RETURN failure_result

        # Phase 3: Remove the failing deployment
        remove_deployment(
            service=config.service_name,
            version=config.version  # The bad version
        )

        # Phase 4: Verify rollback succeeded
        wait(traffic_stabilization_seconds)  # Let things stabilize
        health = check_health(stable_version)

        IF health is bad:
            # Rollback completed but service still unhealthy
            # This suggests a deeper problem
            escalate("Service still unhealthy after rollback")

        # Phase 5: Record in memory for learning
        duration = now() - start_time
        record_rollback_event(
            from_version=config.version,
            to_version=stable_version,
            reason=reason,
            duration=duration,
            final_health=health
        )

        RETURN success_result

    CATCH Exception:
        # Something went catastrophically wrong
        escalate("Rollback failed: " + exception)
        RETURN failure_result
```

### Progressive Implementation Hints

<details>
<summary>Hint 1: Finding the stable version (Click to expand)</summary>

Query the infrastructure client to find which version serves the most traffic right now:

```python
async def _get_stable_version(self, service_name: str) -> str:
    """Get the current stable version."""
    # Query infrastructure for all deployments of this service
    deployments = await self.infra.list_deployments(service_name)

    # Find deployment with highest traffic percentage
    # This is the "stable" version we want to roll back to
    stable = max(deployments, key=lambda d: d.get("traffic_percentage", 0))

    return stable["version"]
```

**Edge case to handle**: `deployments` may be empty. Return `None`, and handle that case in the caller.
</details>

<details>
<summary>Hint 2: Shifting traffic (Click to expand)</summary>

The infrastructure client provides a `set_traffic` method:

```python
traffic_result = await self.infra.set_traffic(
    service_name=config.service_name,
    version=stable_version,
    percentage=100  # All traffic to stable version
)

# Check if it succeeded
if not traffic_result["success"]:
    # This is CRITICAL - traffic shift must succeed
    # If this fails, you're in a bad state
    await self._escalate_rollback_failure(config, "Traffic shift failed")
    return {"success": False, ...}
```
</details>

<details>
<summary>Hint 3: Removing failed deployment (Click to expand)</summary>

Clean up the bad deployment:

```python
remove_result = await self.infra.remove_deployment(
    service_name=config.service_name,
    version=config.version  # This is the FAILED version
)

# Note: If removal fails, it's not critical
# Traffic is already shifted away, so users aren't affected
# Just log it and continue
```
</details>

<details>
<summary>Hint 4: Verifying rollback (Click to expand)</summary>

After rollback, check that the service is healthy:

```python
# Wait for traffic to stabilize. Use the configurable pause, not a literal 30,
# so the test suite (which passes 0) does not sit through a production wait.
if self.traffic_stabilization_seconds > 0:
    await asyncio.sleep(self.traffic_stabilization_seconds)

# Check health of the stable version
verification = await self.health_monitor.collect_metrics(
    service_name=config.service_name,
    version=stable_version  # Check the version we rolled back TO
)

# Define "healthy" criteria
is_healthy = (
    verification["error_rate"] < 0.01 and  # < 1%
    verification["latency_p99"] < 500      # < 500ms
)

if not is_healthy:
    # Rollback succeeded but service still has issues
    # This means the problem wasn't just the new version
    await self._escalate_rollback_failure(
        config,
        f"Service unhealthy after rollback: {verification}"
    )
```
</details>

<details>
<summary>Hint 5: Recording in memory (Click to expand)</summary>

Use DevMemory to record the rollback event:

```python
await self.memory.remember_session(
    session_type="rollback",
    summary=f"Rolled back {config.service_name} from v{config.version} to v{stable_version}",
    details=f"Reason: {reason}. Duration: {rollback_duration}s",
    outcome="success" if is_healthy else "partial",
    project=config.service_name,
    metadata={
        "failed_version": config.version,
        "stable_version": stable_version,
        "reason": reason,
        "duration_seconds": rollback_duration,
        "final_health": verification
    }
)
```

This creates an episodic memory that future deployments can read.
</details>

<details>
<summary>Hint 6: Escalation logic (Click to expand)</summary>

When rollback fails, escalate to a human:

```python
async def _escalate_rollback_failure(self, config, reason):
    """Handle critical rollback failures."""
    print(f"CRITICAL: Rollback failed - {reason}")

    # Record in memory as critical incident
    await self.memory.remember_session(
        session_type="incident",
        summary=f"CRITICAL: Rollback failed for {config.service_name}",
        details=reason,
        outcome="critical_failure",
        project=config.service_name,
        metadata={
            "severity": "critical",
            "requires_human": True
        }
    )

    # In production:
    # - PagerDuty alert
    # - Slack/Teams notification
    # - Create high-priority ticket
    # - Trigger incident response
```
</details>

### Implement It

Edit `starter/deployer.py` and implement `rollback()`:

```python
async def rollback(
    self,
    config: DeploymentConfig,
    reason: str
) -> dict:
    """Rollback to previous stable version."""
    from datetime import datetime

    print(f"Initiating rollback: {reason}")

    rollback_start = datetime.now()

    try:
        # TODO 1: Identify stable version
        # The stable version is the one currently serving most traffic
        stable_version = await self._get_stable_version(config.service_name)

        if not stable_version:
            return {
                "success": False,
                "reason": "Could not identify stable version",
                "details": "No previous deployment found"
            }

        print(f"Rolling back to stable version: {stable_version}")

        # TODO 2: Shift 100% traffic to stable version
        traffic_result = await self.infra.set_traffic(
            service_name=config.service_name,
            version=stable_version,
            percentage=100
        )

        if not traffic_result["success"]:
            # Critical: traffic shift failed
            await self._escalate_rollback_failure(config, reason)
            return {
                "success": False,
                "reason": "Traffic shift failed",
                "details": traffic_result
            }

        print(f"Traffic shifted to {stable_version}")

        # TODO 3: Remove failing deployment
        remove_result = await self.infra.remove_deployment(
            service_name=config.service_name,
            version=config.version
        )

        print(f"Removed failing deployment v{config.version}")

        # TODO 4: Verify rollback success
        # Wait a bit for traffic to stabilize. The pause is configurable and the
        # tests pass 0, so this does not slow the suite down.
        if self.traffic_stabilization_seconds > 0:
            await asyncio.sleep(self.traffic_stabilization_seconds)

        verification = await self.health_monitor.collect_metrics(
            service_name=config.service_name,
            version=stable_version
        )

        is_healthy = (
            verification["error_rate"] < 0.01 and
            verification["latency_p99"] < 500
        )

        if not is_healthy:
            # Rollback completed but service still unhealthy
            # This suggests a deeper issue
            await self._escalate_rollback_failure(
                config,
                f"Rollback completed but service still unhealthy: {verification}"
            )

        # TODO 5: Record rollback in DevMemory
        rollback_duration = (datetime.now() - rollback_start).seconds

        await self.memory.remember_session(
            session_type="rollback",
            summary=f"Rolled back {config.service_name} from v{config.version} to v{stable_version}",
            details=f"Reason: {reason}. Duration: {rollback_duration}s",
            outcome="success" if is_healthy else "partial",
            project=config.service_name,
            metadata={
                "failed_version": config.version,
                "stable_version": stable_version,
                "reason": reason,
                "duration_seconds": rollback_duration,
                "final_health": verification
            }
        )

        print(f"Rollback completed in {rollback_duration}s")

        return {
            "success": True,
            "stable_version": stable_version,
            "duration_seconds": rollback_duration,
            "final_health": verification
        }

    except Exception as e:
        # Rollback failed catastrophically
        await self._escalate_rollback_failure(config, str(e))
        return {
            "success": False,
            "reason": f"Rollback exception: {str(e)}"
        }
```

## Step 4: Implement Helper Methods

Add these helper methods:

### Get Stable Version
```python
async def _get_stable_version(self, service_name: str) -> str:
    """Get the current stable (primary) version of a service."""
    deployments = await self.infra.list_deployments(service_name)

    # Find the deployment with highest traffic percentage
    stable = max(
        deployments,
        key=lambda d: d.get("traffic_percentage", 0)
    )

    return stable["version"]
```

### Escalate Rollback Failure
```python
async def _escalate_rollback_failure(
    self,
    config: DeploymentConfig,
    reason: str
):
    """Handle critical rollback failures."""
    print(f"CRITICAL: Rollback failed - {reason}")

    # Record critical failure in memory
    await self.memory.remember_session(
        session_type="incident",
        summary=f"CRITICAL: Rollback failed for {config.service_name}",
        details=reason,
        outcome="critical_failure",
        project=config.service_name,
        metadata={
            "severity": "critical",
            "requires_human": True
        }
    )

    # In production, this would:
    # - Page on-call engineer
    # - Create high-priority incident ticket
    # - Trigger emergency response procedures

    # For this lab, we log and alert
    print("CRITICAL: Human intervention required")
```

## Step 5: Confirm the Deployment Flow Wiring

No edits are needed here. The starter's `deploy()` already calls your
`rollback()` at four points. Each one is guarded by `config.auto_rollback_enabled`:

1. When canary validation fails.
2. When a traffic shift fails.
3. When a health check between shifts fails.
4. When any exception escapes.

Open `starter/deployer.py` and trace those call sites, so you know when your
method runs. The sketch below shows the shape of that wiring:

```python
async def deploy(self, config: DeploymentConfig) -> dict:
    """Execute zero-downtime deployment."""
    try:
        # ... existing canary deployment code ...

        # Validate canary
        validation = await self.validate_canary(config, duration_seconds=300)

        if not validation["healthy"]:
            # Automatic rollback on validation failure
            rollback_result = await self.rollback(
                config,
                reason=validation["reason"]
            )

            return {
                "status": "failed",
                "reason": "Canary validation failed",
                "validation": validation,
                "rollback": rollback_result
            }

        # ... continue with traffic shifting ...

    except Exception as e:
        # Rollback on any deployment exception
        rollback_result = await self.rollback(
            config,
            reason=f"Deployment exception: {str(e)}"
        )

        return {
            "status": "failed",
            "reason": str(e),
            "rollback": rollback_result
        }
```

## Step 6: Test Your Implementation

Run the rollback tests:

```bash
pytest starter/tests/test_deployer.py -v -k rollback
```

Expected output (abridged):
```text
starter/tests/test_deployer.py::test_rollback_success PASSED
starter/tests/test_deployer.py::test_rollback_records_in_memory PASSED
starter/tests/test_deployer.py::test_automatic_rollback_on_validation_failure PASSED
```

## Step 7: Test End-to-End Failure Scenario

Test automatic rollback with integration tests:

```bash
pytest starter/tests/test_integration.py::test_end_to_end_failed_deployment_with_rollback -v
```

This test simulates a bad deployment and checks that automatic rollback runs.

Expected behavior:
- Canary deployment with "bad" version
- Validation detects high error rate
- Automatic rollback triggered
- System returns to stable state
- Failure recorded in memory

## Verification Checklist

- [ ] `rollback()` identifies stable version correctly
- [ ] Traffic is shifted to stable version
- [ ] Failing deployment is removed
- [ ] Rollback success is verified with health checks
- [ ] Rollback event is recorded in DevMemory
- [ ] Rollback failures trigger escalation
- [ ] `deploy()` calls `rollback()` on validation failure (already wired in the starter; confirm by reading `deploy()`)
- [ ] Tests pass: `pytest starter/tests/test_deployer.py -v -k rollback`
- [ ] End-to-end failure test completes successfully

## Common Pitfalls and Debugging

### Common Mistakes Students Make

1. **Rolling back to the wrong version**
   ```python
   # WRONG - Rolling back to the failed version!
   await self.infra.set_traffic(
       version=config.version  # This is the BAD version
   )

   # CORRECT - Roll back to stable version
   stable_version = await self._get_stable_version(config.service_name)
   await self.infra.set_traffic(
       version=stable_version  # This is the GOOD version
   )
   ```

2. **Not checking if traffic shift succeeded**
   ```python
   # WRONG - Assuming it worked
   await self.infra.set_traffic(...)
   # Continue with rollback

   # CORRECT - Check result
   result = await self.infra.set_traffic(...)
   if not result["success"]:
       await self._escalate_rollback_failure(...)
       return {"success": False}
   ```

3. **Forgetting to handle the "no stable version" case**
   ```python
   # WRONG - Will crash if no stable version
   stable = await self._get_stable_version(service_name)
   await self.infra.set_traffic(version=stable)

   # CORRECT - Check for None
   stable = await self._get_stable_version(service_name)
   if not stable:
       return {"success": False, "reason": "No stable version"}
   ```

4. **Not recording the rollback in memory**
   - Future deployments read past rollbacks from memory
   - Always call `memory.remember_session()` at the end

5. **Treating all rollback failures the same**
   - Traffic shift failure = CRITICAL (users affected)
   - Deployment removal failure = WARNING (cleanup issue)
   - Post-rollback unhealthy = CRITICAL (deeper problem)

### Error Scenarios and How to Handle Them

**Scenario 1: No stable version exists**
- **When**: First deployment of a new service fails
- **Handle**: Return failure, escalate, don't attempt rollback
- **Code**: Check if `_get_stable_version()` returns `None`

**Scenario 2: Traffic shift fails**
- **When**: Network issues, Kubernetes problems, misconfiguration
- **Handle**: CRITICAL escalation, immediate human intervention needed
- **Why critical**: Users may be experiencing partial outages

**Scenario 3: Deployment removal fails**
- **When**: Kubernetes pod stuck in terminating state
- **Handle**: Log warning, continue (not critical)
- **Why not critical**: Traffic already shifted, users unaffected

**Scenario 4: Service unhealthy after rollback**
- **When**: Problem wasn't just the new version (DB issue, upstream service down)
- **Handle**: CRITICAL escalation, broader system problem
- **Why critical**: Rolling back didn't fix it, need deeper investigation

### Debugging Tips

**Problem: Rollback reports success but service still broken**
- Check if you're verifying health on the correct version (stable, not failed)
- Ensure health check waits for stabilization (`self.traffic_stabilization_seconds`)
- Look at actual metrics - are thresholds too lenient?

**Problem: "No deployments found" error**
- Verify `list_deployments()` is working correctly
- Check mock infrastructure is properly initialized
- Ensure service_name matches exactly (case-sensitive)

**Problem: Rollback takes too long**
- Check your stabilization pause: hardcoding `asyncio.sleep(30)` instead of using `self.traffic_stabilization_seconds` makes the test suite wait through every production pause
- Verify `remove_deployment()` isn't hanging
- Look for missing `await` keywords (causes hanging)

**Problem: Tests pass but integration fails**
- Unit tests may use mocks that don't reflect real behavior
- Check actual infrastructure client implementation
- Verify Kubernetes permissions and connectivity

### Common Issues

### Issue: "No stable version found"
**Solution**: Ensure at least one deployment exists before testing rollback

### Issue: Traffic shift hangs
**Solution**: Check if Kubernetes service is properly configured

### Issue: Rollback succeeds but tests fail
**Solution**: Verify health check thresholds in test mocks match implementation

### Issue: Rollback completes but memory record fails
**Solution**: This is not critical. The rollback worked, and memory is optional. Check the DevMemory connection.

## Reference: Success Criteria and Examples

How self-healing works in CA/CD: Chapter 11, Section 11.3.

### Success Criteria: How to know you're done

Your implementation is complete when:
- `rollback()` identifies the stable version correctly
- Traffic is shifted to 100% on stable version
- Failed deployment is removed from infrastructure
- Post-rollback health verification is performed
- Rollback success/failure is determined correctly
- Rollback events are recorded in DevMemory with full context
- Rollback failures trigger escalation with `_escalate_rollback_failure()`
- `deploy()` method calls `rollback()` on validation failure
- Unit tests pass: `pytest starter/tests/test_deployer.py -v -k rollback`
- Integration tests demonstrate end-to-end failure recovery

### Helper Method Usage Examples

**Example: Using infrastructure client methods**

```python
# List all deployments for a service
deployments = await self.infra.list_deployments("api-service")
# Returns: [
#   {"version": "1.0.0", "traffic_percentage": 90, "replicas": 5},
#   {"version": "2.0.0", "traffic_percentage": 10, "replicas": 1}
# ]

# Set traffic distribution
result = await self.infra.set_traffic(
    service_name="api-service",
    version="1.0.0",
    percentage=100
)
# Returns: {"success": True, "message": "Traffic updated"}

# Remove a deployment
result = await self.infra.remove_deployment(
    service_name="api-service",
    version="2.0.0"
)
# Returns: {"success": True, "message": "Deployment removed"}
```

**Example: Complete rollback flow**

```python
async def rollback(self, config, reason):
    try:
        # 1. Find stable version
        stable = await self._get_stable_version(config.service_name)
        if not stable:
            await self._escalate_rollback_failure(config, "No stable version")
            return {"success": False}

        # 2. Shift traffic
        traffic_result = await self.infra.set_traffic(
            service_name=config.service_name,
            version=stable,
            percentage=100
        )
        if not traffic_result["success"]:
            await self._escalate_rollback_failure(config, "Traffic shift failed")
            return {"success": False}

        # 3. Remove failed version
        await self.infra.remove_deployment(
            service_name=config.service_name,
            version=config.version
        )

        # 4. Verify health
        if self.traffic_stabilization_seconds > 0:
            await asyncio.sleep(self.traffic_stabilization_seconds)
        health = await self.health_monitor.collect_metrics(
            service_name=config.service_name,
            version=stable
        )

        is_healthy = health["error_rate"] < 0.01 and health["latency_p99"] < 500

        # 5. Record in memory
        await self.memory.remember_session(
            session_type="rollback",
            summary=f"Rollback: {config.service_name} {config.version} → {stable}",
            outcome="success" if is_healthy else "partial",
            project=config.service_name
        )

        return {"success": True, "stable_version": stable}

    except Exception as e:
        await self._escalate_rollback_failure(config, str(e))
        return {"success": False}
```

## Next Steps

Once your implementation passes tests, move to:
- **Exercise 3**: Sentry Integration (`exercises/exercise-3-sentry.md`)

Or explore:
- Implement blue-green deployment as alternative to canary
- Add progressive rollback (roll back in stages)
- Create rollback time budgets (max rollback time before escalation)

## Reference

- **Complete implementation**: `complete/deployer.py`
- **Chapter 11 Section 11.3**: Self-Healing Pipelines
- **Chapter 11, Section 11.6**: Zero-Downtime Deployer
