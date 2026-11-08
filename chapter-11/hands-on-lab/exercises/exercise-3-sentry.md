# Exercise 3: Sentry Integration (Optional)

**Time**: 30-75 minutes
**Difficulty**: Intermediate-Advanced
**Prerequisites**: Exercises 1 & 2 completed

## Learning Objectives

By the end of this exercise, you will:
- Integrate real error tracking with Sentry
- Use production-grade observability in deployments
- Correlate deployment events with error spikes
- Connect a commercial tool to a CA/CD agent

## Background

Exercises 1 and 2 use synthetic metrics. In this exercise you add Sentry error
tracking, so canary validation can see real application errors.

How Sentry Seer and similar tools fit into CA/CD: Chapter 11, Section 11.2.

For the latest Sentry setup steps, see the [Sentry Python SDK docs](https://docs.sentry.io/platforms/python/).

### Sentry Integration Architecture

```text
┌───────────────────────────────────────────────────────────────┐
│                    SENTRY INTEGRATION FLOW                     │
└───────────────────────────────────────────────────────────────┘

Your Deployer                        Sentry Platform
─────────────                        ───────────────

[Deploy Start]
     │
     ├──────────────────────────────> Report deployment event
     │                                 - service: api-service
     │                                 - version: 2.0.0
     │                                 - deployment_id: abc-123
     │
[Validate Canary]
     │
     ├──────────────────────────────> Query error rate
     │                                 - Filter by: service + version
     │                                 - Time window: last 5 minutes
     │
     │ <────────────────────────────── Return: error_rate = 2.3%
     │
     ├─> Decision: error_rate > 1%
     │   → Trigger rollback
     │
[Rollback]
     │
     ├──────────────────────────────> Query recent errors
     │                                 - Get top 5 errors
     │                                 - Include stack traces
     │
     │ <────────────────────────────── Return: error details
     │
     ├──────────────────────────────> Report rollback event
     │                                 - from_version: 2.0.0
     │                                 - to_version: 1.0.0
     │                                 - reason: "High error rate"
     │
[Post-Rollback]
     │
     └──────────────────────────────> Report rollback complete
                                       - success: true
                                       - duration: 45s
```

## What You'll Build

You extend your deployer to:
1. Report deployment events to Sentry
2. Query Sentry for real-time error rates during validation
3. Trigger rollback when error spikes are detected
4. Correlate rollbacks with specific errors

## Step 1: Create Sentry Account (Free Tier)

### Sign Up
1. Go to [sentry.io/signup](https://sentry.io/signup/)
2. Sign up with email or GitHub
3. The free Developer plan is plenty for this lab (see [sentry.io/pricing](https://sentry.io/pricing/))

### Create Project
1. Click **Create Project**
2. Select platform: **Python**
3. Alert frequency: **Alert me on high priority issues** (the default)
4. Project name: `zero-downtime-deployer-lab`
5. Click **Create Project**

### Get Your DSN
1. After you create the project, Sentry shows setup instructions
2. Copy your **DSN** (Data Source Name)
   - Looks like: `https://abc123@o123.ingest.sentry.io/456`
3. Save this for Step 2

## Step 2: Configure Sentry Integration

### Update Environment Variables

Edit `.env` and add:

```env
# Sentry Integration
SENTRY_DSN=https://your-dsn-here@o123.ingest.sentry.io/456
SENTRY_ENVIRONMENT=lab
SENTRY_TRACES_SAMPLE_RATE=1.0
```

### Understanding Sentry DSN

The DSN (Data Source Name) works like an API key for Sentry:

```text
https://PUBLIC_KEY@ORGANIZATION.ingest.sentry.io/PROJECT_ID
        ─┬───────  ─────┬──────                      ──┬───
         │              │                              │
    Public Key    Organization ID                Project ID
```

**Important**:
- DSN is safe to commit. It is public by design
- DSN only allows *sending* events, not reading them
- API queries need an Auth Token. This lab does not cover it

### Using Placeholder vs Real Sentry

<details>
<summary>Option A: Use Placeholder (Quick Start) - Click to expand</summary>

You can use a **placeholder DSN** while you learn:

```env
SENTRY_DSN=https://placeholder@o123456.ingest.sentry.io/789
```

**What happens with placeholder:**
- Your code runs without errors
- You can still write and run the integration code
- No external dependencies
- Limitation: events don't actually send to Sentry
- Limitation: you don't see real Sentry dashboard

**When to use:** Quick iteration, offline development, CI/CD tests
</details>

<details>
<summary>Option B: Use Real Sentry (Recommended) - Click to expand</summary>

Sign up for real Sentry (the free Developer plan is enough):

1. Go to [sentry.io/signup](https://sentry.io/signup/)
2. Create project: Platform = Python
3. Copy your real DSN
4. Add to `.env`

**What happens with real Sentry:**
- Events appear in your dashboard
- See real error tracking in action
- Correlate deployments with errors
- Note: requires internet connection
- Note: uses your event quota

**When to use:** When you want to see real events in Sentry
</details>

### Verify Sentry Connection

The repo ships a connection check. Run it from the `hands-on-lab` directory:

```bash
python integrations/test_sentry_connection.py
```

It runs these checks in order:
```text
[PASS] Environment variables loaded from .env
[PASS] Sentry SDK installed (version: ...)
[PASS] SENTRY_DSN configured: https://...
[PASS] Sentry initialized successfully
[PASS] Test event sent successfully
```

If you still use a placeholder DSN, the script says so, and no events are sent.
That is fine for working through the exercise offline.

## Step 3: Implement Sentry Error Tracking

### Implementation Strategy

The `SentryMonitor` class needs to:
1. **Initialize** Sentry SDK with your DSN
2. **Report events** (deployment start, completion, rollback)
3. **Query metrics** (error rate, recent errors)
4. **Tag events** for correlation (deployment_id, version, service)

### Key Integration Points

```text
┌────────────────────────────────────────────────────────┐
│           When to Report to Sentry                      │
├────────────────────────────────────────────────────────┤
│                                                         │
│    Deployment Start       → Info-level event           │
│    Canary Validation      → Query error rate           │
│    Validation Failed      → Warning + error details    │
│    Rollback Initiated     → Warning-level event        │
│    Rollback Complete      → Info/error based on result │
│    Deployment Success     → Info-level event           │
│                                                         │
└────────────────────────────────────────────────────────┘
```

### Progressive Implementation Hints

<details>
<summary>Hint 1: Initializing Sentry SDK (Click to expand)</summary>

Initialize the Sentry SDK like this:

```python
import sentry_sdk
from os import getenv

sentry_sdk.init(
    dsn=getenv("SENTRY_DSN"),
    environment=getenv("SENTRY_ENVIRONMENT", "lab"),
    traces_sample_rate=float(getenv("SENTRY_TRACES_SAMPLE_RATE", "1.0"))
)
```

**Important**: Initialize once in `__init__()`, not on every method call.
</details>

<details>
<summary>Hint 2: Reporting events with context (Click to expand)</summary>

Use Sentry's scope to add context to events. `new_scope()` is the sentry-sdk
2.x API. The older `configure_scope()` is deprecated. Capture the event inside
the `with` block, so the tags apply to it:

```python
import sentry_sdk
from sentry_sdk import capture_message

def report_deployment_start(self, service_name, version, deployment_id):
    # Set tags for filtering
    with sentry_sdk.new_scope() as scope:
        scope.set_tag("deployment_id", deployment_id)
        scope.set_tag("service", service_name)
        scope.set_tag("version", version)

        # Set context for additional data
        scope.set_context("deployment", {
            "service": service_name,
            "version": version,
            "started_at": datetime.now().isoformat()
        })

        # Send the event
        capture_message(
            f"Deployment started: {service_name} v{version}",
            level="info"
        )
```

**Tags**: Filter the Sentry dashboard by `deployment_id` to see all events from one deployment.
</details>

<details>
<summary>Hint 3: Simulating vs Real error rate queries (Click to expand)</summary>

This lab **simulates** error rate queries. Sentry API access requires auth tokens:

```python
def get_error_rate(self, service_name, version, minutes=5) -> float:
    """
    Get error rate for a service version.

    NOTE: In production, this would query Sentry API:
        - GET /api/0/projects/{org}/{project}/issues/
        - Filter by tags: service, version
        - Calculate: error_count / total_requests

    For this lab, we simulate based on version name.
    """
    # Simulation logic
    if "bad" in version or "canary" in version:
        return random.uniform(0.01, 0.05)  # 1-5% errors
    return random.uniform(0.0, 0.005)  # 0-0.5% errors
```

**To upgrade to real queries:**
1. Get a Sentry Auth Token from dashboard
2. Use `requests` to call Sentry REST API
3. Parse JSON response for error counts
</details>

<details>
<summary>Hint 4: Reporting rollback events (Click to expand)</summary>

Rollbacks are critical events. Tag them clearly:

```python
def report_rollback(self, service_name, failed_version, stable_version, reason):
    with sentry_sdk.new_scope() as scope:
        scope.set_tag("rollback", "true")  # Easy to filter for all rollbacks
        scope.set_tag("service", service_name)

        scope.set_context("rollback", {
            "service": service_name,
            "failed_version": failed_version,
            "stable_version": stable_version,
            "reason": reason
        })

        capture_message(
            f"Rollback: {service_name} v{failed_version} -> v{stable_version}",
            level="warning"  # Rollbacks are warnings, not errors
        )
```
</details>

### Implement It

A scaffold already exists at `integrations/sentry_integration.py`. It has the
same class and method signatures, with TODO markers where the bodies go. Open
that file and fill in the TODOs. Do not start a new file. For reference, here is
a finished version:

```python
"""Sentry integration for deployment error tracking."""

import sentry_sdk
from sentry_sdk import capture_message, capture_exception
from datetime import datetime, timedelta
from typing import List, Dict
import os


class SentryMonitor:
    """Monitor deployment errors using Sentry."""

    def __init__(self):
        """Initialize Sentry SDK."""
        dsn = os.getenv("SENTRY_DSN")
        environment = os.getenv("SENTRY_ENVIRONMENT", "lab")

        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "1.0")),
            profiles_sample_rate=1.0,
        )

    def report_deployment_start(
        self,
        service_name: str,
        version: str,
        deployment_id: str
    ):
        """Report deployment start to Sentry."""
        with sentry_sdk.new_scope() as scope:
            scope.set_tag("deployment_id", deployment_id)
            scope.set_tag("service", service_name)
            scope.set_tag("version", version)
            scope.set_context("deployment", {
                "service": service_name,
                "version": version,
                "deployment_id": deployment_id,
                "started_at": datetime.now().isoformat()
            })
            capture_message(
                f"Deployment started: {service_name} v{version}",
                level="info"
            )

    def report_deployment_complete(
        self,
        service_name: str,
        version: str,
        deployment_id: str,
        success: bool
    ):
        """Report deployment completion to Sentry."""
        level = "info" if success else "error"
        status = "succeeded" if success else "failed"

        capture_message(
            f"Deployment {status}: {service_name} v{version}",
            level=level
        )

    def get_error_rate(
        self,
        service_name: str,
        version: str,
        minutes: int = 5
    ) -> float:
        """
        Get error rate for a service version.

        In production, this would query Sentry API.
        For this lab, we use Sentry SDK to report errors
        and calculate rate from recent events.
        """
        # TODO: Implement using Sentry API
        # For lab purposes, we'll simulate based on tags

        # In real implementation:
        # 1. Query Sentry API for errors with matching tags
        # 2. Get total request count from metrics
        # 3. Calculate error_rate = errors / total_requests

        # For lab, we'll use a simplified approach
        return self._get_simulated_error_rate(service_name, version)

    def _get_simulated_error_rate(
        self,
        service_name: str,
        version: str
    ) -> float:
        """
        Simulated error rate for lab purposes.

        In production, replace with actual Sentry API query.
        """
        import random

        # Simulate: new versions have slight chance of higher errors
        if "bad" in version or "canary" in version:
            return random.uniform(0.01, 0.05)  # 1-5% errors
        return random.uniform(0.0, 0.005)  # 0-0.5% errors

    def get_recent_errors(
        self,
        service_name: str,
        version: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get recent errors for analysis.

        Returns structured error data for rollback decisions.
        """
        # TODO: Query Sentry API for recent errors

        # Example return format:
        return [
            {
                "message": "NullPointerException in user service",
                "count": 47,
                "first_seen": "2025-02-05T10:23:11Z",
                "last_seen": "2025-02-05T10:28:45Z",
                "url": "https://sentry.io/issues/12345"
            }
        ]

    def report_rollback(
        self,
        service_name: str,
        failed_version: str,
        stable_version: str,
        reason: str
    ):
        """Report rollback event to Sentry."""
        with sentry_sdk.new_scope() as scope:
            scope.set_tag("rollback", "true")
            scope.set_context("rollback", {
                "service": service_name,
                "failed_version": failed_version,
                "stable_version": stable_version,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            })
            capture_message(
                f"Rollback: {service_name} v{failed_version} -> v{stable_version}",
                level="warning"
            )
```

## Step 4: Integrate with Deployer

Update `starter/deployer.py` to use Sentry:

```python
from integrations.sentry_integration import SentryMonitor

class ZeroDowntimeDeployer:
    def __init__(self, memory: DevMemory, infrastructure_client):
        self.memory = memory
        self.infra = infrastructure_client
        self.health_monitor = HealthMonitor()
        self.sentry = SentryMonitor()  # Add Sentry

    async def deploy(self, config: DeploymentConfig) -> dict:
        """Execute zero-downtime deployment."""
        deployment_id = f"{config.service_name}-{config.version}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Report deployment start to Sentry
        self.sentry.report_deployment_start(
            config.service_name,
            config.version,
            deployment_id
        )

        try:
            # ... existing deployment logic ...

            # Report success
            self.sentry.report_deployment_complete(
                config.service_name,
                config.version,
                deployment_id,
                success=True
            )

            return result

        except Exception as e:
            # Report failure
            self.sentry.report_deployment_complete(
                config.service_name,
                config.version,
                deployment_id,
                success=False
            )
            raise

    async def validate_canary(
        self,
        config: DeploymentConfig,
        duration_seconds: int
    ) -> dict:
        """Validate canary using Sentry error tracking."""

        # Use Sentry for error rate instead of (or in addition to) mock metrics
        error_rate = self.sentry.get_error_rate(
            config.service_name,
            config.version,
            minutes=5
        )

        if error_rate > 0.01:  # >1% error rate
            # Get specific errors for context
            recent_errors = self.sentry.get_recent_errors(
                config.service_name,
                config.version,
                limit=5
            )

            return {
                "healthy": False,
                "reason": f"High error rate: {error_rate:.2%}",
                "sentry_errors": recent_errors
            }

        # ... rest of validation ...

    async def rollback(
        self,
        config: DeploymentConfig,
        reason: str
    ) -> dict:
        """Rollback with Sentry reporting."""

        # Get stable version
        stable_version = await self._get_stable_version(config.service_name)

        # Report rollback to Sentry
        self.sentry.report_rollback(
            config.service_name,
            config.version,
            stable_version,
            reason
        )

        # ... rest of rollback logic ...
```

## Step 5: Test Sentry Integration

### Test 1: Verify Sentry Connection

Test that the Sentry SDK is configured. A check ships in the repo. Run it from
the `hands-on-lab` directory:

```bash
python integrations/test_sentry_connection.py
```

It checks four things:

- Your `.env` loads.
- The SDK is installed.
- The DSN is set.
- A test event reaches Sentry.

Or test your own class directly:

```python
from integrations.sentry_integration import SentryMonitor

monitor = SentryMonitor()
monitor.report_deployment_start("test-service", "1.0.0", "test-123")
print("Event sent to Sentry, check your dashboard")
```

Then check your Sentry dashboard:
1. Go to sentry.io → Your Project
2. Click **Issues**
3. You should see the test deployment event

### Test 2: Deploy with Sentry Wired In

The shipped suite has no Sentry-specific tests. You verify this exercise by the
events in your Sentry dashboard, or by the placeholder-mode log lines. First,
re-run the full suite to confirm your Sentry wiring did not break the deployer:

```bash
pytest starter/tests/ -v
```

Then create a simple deployment test script:

```python
# test_deployment_with_sentry.py
import asyncio
from starter.deployer import ZeroDowntimeDeployer
from starter.config import DeploymentConfig

async def test():
    deployer = ZeroDowntimeDeployer(...)  # with Sentry configured

    config = DeploymentConfig(
        service_name="test-api",
        version="1.0.0",
        image="test:1.0.0",
        replicas=3
    )

    result = await deployer.deploy(config)
    print(f"Deployment result: {result}")

asyncio.run(test())
```

After running, check Sentry dashboard for:
- Deployment start event
- Any errors during deployment
- Deployment completion event
- Events correlated by deployment_id

## Step 6: Advanced Sentry Features

### Correlate Errors with Deployments

Sentry can correlate error spikes with deployments:

1. In Sentry, go to **Explore** → **Releases**
2. Add this to your deployer:

```python
def report_deployment_start(self, service_name, version, deployment_id):
    # ... existing code ...

    # Create a release in Sentry
    sentry_sdk.set_tag("release", version)
```

Sentry now shows which releases introduced new errors.

### Set Up Alerts

In Sentry dashboard:
1. Go to **Monitors** → **Alerts** → **Create Alert**
2. Rule: "When error count increases by 50%"
3. Action: "Send webhook to deployer"
4. The deployer can now roll back before the validation period ends

## Verification Checklist

- [ ] Sentry account created and DSN configured
- [ ] `SentryMonitor` class implemented
- [ ] Deployment events reported to Sentry
- [ ] Error rate queried from Sentry during validation
- [ ] Rollback events reported to Sentry
- [ ] Test deployments visible in Sentry dashboard
- [ ] Error correlation working
- [ ] All tests pass with Sentry integration

## Reference: Integration Diagrams and Examples

Why agents query observability tools during deployment: Chapter 11, Section 11.2.

### Bi-Directional Integration

```text
┌─────────────────────────────────────────────────────────┐
│          Agent ↔ Sentry Communication Pattern            │
└─────────────────────────────────────────────────────────┘

Direction: Agent → Sentry (Reporting)
────────────────────────────────────
• Deployment started/completed
• Canary validation results
• Rollback events
• Error context and stack traces

Direction: Sentry → Agent (Querying)
────────────────────────────────────
• Current error rate
• Recent error details
• Error trends over time
• Alert webhooks (advanced)
```

### Context Propagation

All events in a deployment lifecycle share a `deployment_id`:

```text
Deployment: api-service v2.0.0
deployment_id: api-service-v2.0.0-20260205143022

Events with this deployment_id:
├─ [INFO] Deployment started
├─ [INFO] Canary deployed (10% traffic)
├─ [WARN] High error rate detected: 2.3%
├─ [WARN] Rollback initiated
└─ [INFO] Rollback complete → v1.0.0

In Sentry dashboard:
Filter by deployment_id → See entire deployment story
```

### Decision Enhancement

**Traditional Monitoring**:
```text
High error rate → Alert human → Human investigates → Human decides → Human acts
```

**CA/CD with Sentry**:
```text
High error rate → Agent queries Sentry → Agent correlates with deployment
              → Agent decides to rollback → Agent executes rollback
              → Agent verifies success → Agent learns for future
```

### Success Criteria: How to know you're done

Your Sentry integration is complete when:
- Sentry SDK initializes without errors
- Deployment events are reported with proper tags
- `deployment_id` is used consistently across events
- Error rate queries return simulated data
- Rollback events include full context (versions, reason)
- Events appear in Sentry dashboard (if using real DSN)
- Tests pass with Sentry integration enabled
- You can filter Sentry dashboard by deployment_id
- Service, version, and environment tags are set correctly

### Real-World Production Patterns

**Pattern 1: Error Budget Management**
```python
# In production, track error budget
total_requests = 1_000_000
allowed_errors = total_requests * 0.001  # 0.1% SLO
current_errors = sentry.get_error_count(last_hour)

if current_errors > allowed_errors:
    # Error budget exhausted - pause deployments
    pause_all_deployments()
```

**Pattern 2: Gradual Rollout with Error Tracking**
```python
# Deploy in stages, checking errors at each stage
stages = [10, 25, 50, 100]
for percentage in stages:
    deploy_to(percentage)
    error_rate = sentry.get_error_rate(minutes=5)
    if error_rate > threshold:
        rollback()
        break
    # Only proceed if errors are low
```

**Pattern 3: Automated Error Diagnosis**
```python
# When rollback occurs, analyze what errors triggered it
recent_errors = sentry.get_recent_errors(limit=10)
error_types = analyze_error_patterns(recent_errors)

# Store in memory for future deployments
memory.remember({
    "deployment": failed_version,
    "error_pattern": error_types,
    "action": "rolled_back"
})

# Next deployment of this service:
# - Check memory for past error patterns
# - Be extra cautious if similar code changes
```

## Real-World Patterns

**Sentry Seer integration**: see Chapter 11, Section 11.2.

## Next Steps

Extend your implementation:
- [ ] Implement Sentry API queries (not simulated)
- [ ] Add webhook receiver for Sentry alerts
- [ ] Integrate with Sentry Seer for automated fixes
- [ ] Create custom Sentry dashboards for deployments
- [ ] Set up Slack notifications via Sentry

## Common Pitfalls and Debugging

### Common Mistakes Students Make

1. **Initializing Sentry multiple times**
   ```python
   # WRONG - Initializes on every call
   def report_deployment_start(self, ...):
       sentry_sdk.init(dsn=...)  # Don't do this here!

   # CORRECT - Initialize once in __init__
   def __init__(self):
       sentry_sdk.init(dsn=...)  # Once, at startup
   ```

2. **Not checking if DSN is configured**
   ```python
   # WRONG - Will crash if DSN is missing
   sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"))

   # CORRECT - Check first
   dsn = os.getenv("SENTRY_DSN")
   if not dsn:
       print("Warning: SENTRY_DSN not configured")
       return
   sentry_sdk.init(dsn=dsn)
   ```

3. **Using synchronous calls in async context**
   ```python
   # Note: Sentry SDK calls are synchronous (blocking)
   # This is OK for most cases, but in async functions:

   async def validate_canary(self, ...):
       # Sentry calls are synchronous, but fast
       error_rate = self.sentry.get_error_rate(...)  # No await needed
   ```

4. **Not using tags for correlation**
   ```python
   # WRONG - Can't correlate events
   capture_message(f"Deployment started")

   # CORRECT - Use tags, and capture inside the scope
   with sentry_sdk.new_scope() as scope:
       scope.set_tag("deployment_id", deployment_id)
       capture_message(f"Deployment started")
   ```

5. **Assuming placeholder DSN sends real events**
   - Placeholder DSN: no real events are sent
   - Real DSN: events appear in the dashboard
   - Check which mode you are in

### Placeholder vs Real Sentry Behavior

| Aspect | Placeholder DSN | Real Sentry DSN |
|--------|----------------|-----------------|
| Code runs | Yes | Yes |
| Events send | Silently dropped | Sent to Sentry |
| Dashboard updates | No | Yes |
| Error queries | Simulated | Simulated (need API token) |
| Internet required | No | Yes |
| Good for | Testing, CI/CD | Learning, production |

### Debugging Tips

**Problem: Events not appearing in Sentry dashboard**
1. Check DSN is correct (copy-paste from Sentry dashboard)
2. Verify internet connectivity
3. Check Sentry project settings (events accepted?)
4. Look for error messages in console
5. Try manual test: `sentry_sdk.capture_message("test")`

**Problem: "sentry_sdk module not found"**
```bash
pip install sentry-sdk
```

**Problem: Events send but can't query error rate**
- Expected behavior with free tier
- Sentry API queries require Auth Token (separate from DSN)
- For this lab, use simulated error rates
- In production, add Auth Token and implement real queries

**Problem: Too many events sent (quota exceeded)**
- Use `traces_sample_rate=0.1` (10% sampling)
- Only report critical events (deployments, rollbacks)
- Don't report every metric sample

**Problem: Can't correlate events with specific deployment**
- Ensure `deployment_id` tag is set on all related events
- Use same `deployment_id` throughout deployment lifecycle
- Filter Sentry dashboard by tag: `deployment_id:abc-123`

### Common Issues

### Issue: Events not appearing in Sentry
**Solution**: Check DSN is correct, verify network connectivity. If using placeholder DSN, events won't appear (expected behavior).

### Issue: "Module 'sentry_sdk' not found"
**Solution**: `pip install sentry-sdk`

### Issue: Error rate always 0%
**Solution**: The lab uses simulated error rates. To see variance, deploy versions with "bad" or "canary" in the name.

### Issue: Integration works in code but tests fail
**Solution**: Tests may mock Sentry. Check that the test setup uses a mock SentryMonitor, not the real one.

## Reference

- **Sentry Documentation**: [docs.sentry.io](https://docs.sentry.io/)
- **Sentry Python SDK**: [docs.sentry.io/platforms/python](https://docs.sentry.io/platforms/python/)
- **Chapter 11, Section 11.2**: Sentry Seer and the AI-native tool landscape
- **Scaffold with TODOs**: `integrations/sentry_integration.py` (there is no completed reference for this optional exercise: filling in the TODOs is the exercise)

---

**Done.** Your zero-downtime deployer now has:
- Canary deployments
- Automatic rollback
- Real error tracking
- Memory-informed decisions
- Commercial tool integration
