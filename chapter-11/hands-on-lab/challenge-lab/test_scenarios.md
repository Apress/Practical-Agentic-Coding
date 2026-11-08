# Test Scenarios for Multi-Service Deployment Challenge

Test scenarios to verify your `MultiServiceDeployer` implementation.

## Test Setup

Before running tests, ensure you have:
- Completed Exercises 1 & 2
- Working `ZeroDowntimeDeployer` implementation
- Mock infrastructure enabled (`USE_MOCK_INFRASTRUCTURE=true`)

> **Timing note**: the book's Section 11.7 verification list says a full run
> finishes in under 60 seconds. That holds when all three are true:
>
> - You use mock infrastructure.
> - You pass `traffic_stabilization_seconds=0` to the deployer.
> - You use short per-service validation windows (about 5 seconds, as the lab's test fixtures use).
>
> With the production-realistic `.env` defaults (300s validation, 30s
> stabilization), a three-service run takes about 450 seconds. Scenario 1's
> approximate duration below comes from that.

## Test Categories

1. **Happy Path Tests**: Everything works correctly
2. **Failure Tests**: Various failure scenarios
3. **Edge Case Tests**: Circular dependencies, missing services, etc.
4. **Rollback Tests**: Verify rollback coordination
5. **State Tests**: Verify state tracking accuracy
6. **Memory Tests**: Verify past failures block known-bad version combinations

---

## Scenario 1: Successful 3-Service Deployment

### Description
Deploy database, API, and frontend in correct order with all services healthy.

### Input
```python
services = [
    ServiceConfig(
        name="frontend",
        version="2.0.0",
        image="web-ui:2.0.0",
        depends_on=["api"],
        health_check_endpoint="/",
        replicas=3
    ),
    ServiceConfig(
        name="database",
        version="2.0.0",
        image="postgres:14",
        depends_on=[],
        health_check_endpoint="pg_isready",
        replicas=3
    ),
    ServiceConfig(
        name="api",
        version="2.0.0",
        image="backend-api:2.0.0",
        depends_on=["database"],
        health_check_endpoint="/health",
        replicas=5
    )
]

deployer = MultiServiceDeployer(single_service_deployer)
result = await deployer.deploy_all(services)
```

### Expected Output
```python
{
    "status": "success",
    "deployment_id": "multi-svc-...",
    "services_deployed": ["database", "api", "frontend"],
    "deployment_order": ["database", "api", "frontend"],
    "total_duration_seconds": 450,  # Approximate
    "service_results": {
        "database": {"status": "success", ...},
        "api": {"status": "success", ...},
        "frontend": {"status": "success", ...}
    }
}
```

### Assertions
```python
assert result["status"] == "success"
assert result["deployment_order"] == ["database", "api", "frontend"]
assert len(result["services_deployed"]) == 3
assert "database" in result["services_deployed"]
assert "api" in result["services_deployed"]
assert "frontend" in result["services_deployed"]
```

---

## Scenario 2: First Service Fails Deployment

### Description
Database deployment fails immediately. No other services should be deployed.

### Input
```python
services = [
    ServiceConfig(
        name="database",
        version="2.0.0-bad",  # Bad version triggers failure
        image="postgres:14-bad",
        depends_on=[],
        health_check_endpoint="pg_isready",
        replicas=3
    ),
    ServiceConfig(
        name="api",
        version="2.0.0",
        image="backend-api:2.0.0",
        depends_on=["database"],
        health_check_endpoint="/health",
        replicas=5
    )
]

result = await deployer.deploy_all(services)
```

### Expected Output
```python
{
    "status": "failed",
    "deployment_id": "multi-svc-...",
    "failed_service": "database",
    "failure_reason": "...",
    "services_deployed": [],  # Nothing deployed yet
    "services_rolled_back": [],  # Nothing to roll back
    "service_results": {
        "database": {"status": "failed", ...},
        "api": {"status": "not_attempted", ...}
    }
}
```

### Assertions
```python
assert result["status"] == "failed"
assert result["failed_service"] == "database"
assert len(result["services_deployed"]) == 0
assert len(result["services_rolled_back"]) == 0
assert result["service_results"]["api"]["status"] == "not_attempted"
```

---

## Scenario 3: Middle Service Fails Validation

### Description
Database deploys successfully, API fails health validation, Frontend never attempted.
Database must be rolled back.

### Input
```python
services = [
    ServiceConfig(
        name="database",
        version="2.0.0",
        image="postgres:14",
        depends_on=[],
        health_check_endpoint="pg_isready",
        replicas=3
    ),
    ServiceConfig(
        name="api",
        version="2.0.0-unhealthy",  # Deploys but fails validation
        image="backend-api:2.0.0-unhealthy",
        depends_on=["database"],
        health_check_endpoint="/health",
        replicas=5
    ),
    ServiceConfig(
        name="frontend",
        version="2.0.0",
        image="web-ui:2.0.0",
        depends_on=["api"],
        health_check_endpoint="/",
        replicas=3
    )
]

result = await deployer.deploy_all(services)
```

### Expected Output
```python
{
    "status": "failed",
    "deployment_id": "multi-svc-...",
    "failed_service": "api",
    "failure_reason": "API validation failed: high error rate",
    "services_deployed": ["database"],  # Was deployed before failure
    "services_rolled_back": ["database"],  # Rolled back after failure
    "rollback_duration_seconds": 30,
    "service_results": {
        "database": {
            "status": "deployed_then_rolled_back",
            "rollback_result": {"success": True, ...}
        },
        "api": {
            "status": "failed",
            "failure_reason": "High error rate during validation"
        },
        "frontend": {
            "status": "not_attempted"
        }
    }
}
```

### Assertions
```python
assert result["status"] == "failed"
assert result["failed_service"] == "api"
assert result["services_deployed"] == ["database"]
assert result["services_rolled_back"] == ["database"]
assert "database" in result["service_results"]
assert result["service_results"]["database"]["status"] == "deployed_then_rolled_back"
assert result["service_results"]["frontend"]["status"] == "not_attempted"
```

---

## Scenario 4: Last Service Fails

### Description
Database and API deploy successfully, Frontend fails validation.
Both Database and API must be rolled back in reverse order (API then Database).

### Input
```python
services = [
    ServiceConfig(name="database", version="2.0.0", ...),
    ServiceConfig(name="api", version="2.0.0", ...),
    ServiceConfig(
        name="frontend",
        version="2.0.0-bad",  # Fails validation
        image="web-ui:2.0.0-bad",
        depends_on=["api"],
        ...
    )
]

result = await deployer.deploy_all(services)
```

### Expected Output
```python
{
    "status": "failed",
    "failed_service": "frontend",
    "services_deployed": ["database", "api"],
    "services_rolled_back": ["api", "database"],  # Note: reverse order
    "service_results": {
        "database": {"status": "deployed_then_rolled_back", ...},
        "api": {"status": "deployed_then_rolled_back", ...},
        "frontend": {"status": "failed", ...}
    }
}
```

### Assertions
```python
assert result["status"] == "failed"
assert result["failed_service"] == "frontend"
assert set(result["services_deployed"]) == {"database", "api"}
assert result["services_rolled_back"] == ["api", "database"]  # Reverse order
```

### Critical Verification
```python
# Verify rollback happened in reverse order
rollback_order = []
for service_name, service_result in result["service_results"].items():
    if "rollback_timestamp" in service_result:
        rollback_order.append((service_name, service_result["rollback_timestamp"]))

rollback_order.sort(key=lambda x: x[1])
assert rollback_order[0][0] == "api"  # API rolled back first
assert rollback_order[1][0] == "database"  # Database rolled back second
```

---

## Scenario 5: Circular Dependency Detection

### Description
Services have circular dependency. Should be detected before any deployment starts.

### Input
```python
services = [
    ServiceConfig(
        name="service_a",
        version="2.0.0",
        depends_on=["service_b"],  # A depends on B
        ...
    ),
    ServiceConfig(
        name="service_b",
        version="2.0.0",
        depends_on=["service_c"],  # B depends on C
        ...
    ),
    ServiceConfig(
        name="service_c",
        version="2.0.0",
        depends_on=["service_a"],  # C depends on A (cycle!)
        ...
    )
]

result = await deployer.deploy_all(services)
```

### Expected Output
```python
{
    "status": "failed",
    "deployment_id": "multi-svc-...",
    "reason": "CircularDependencyError: Circular dependency detected in services"
}
```

### Assertions
```python
assert result["status"] == "failed"
assert "circular" in result["reason"].lower() or "cycle" in result["reason"].lower()
assert "services_deployed" not in result or len(result["services_deployed"]) == 0
```

---

## Scenario 6: Missing Dependency

### Description
Service depends on another service that doesn't exist in the deployment.

### Input
```python
services = [
    ServiceConfig(
        name="api",
        version="2.0.0",
        depends_on=["database"],  # database not in services list
        ...
    ),
    ServiceConfig(
        name="frontend",
        version="2.0.0",
        depends_on=["api"],
        ...
    )
]

result = await deployer.deploy_all(services)
```

### Expected Output
```python
{
    "status": "failed",
    "deployment_id": "multi-svc-...",
    "reason": "MissingDependencyError: Service 'api' depends on non-existent service 'database'"
}
```

### Assertions
```python
assert result["status"] == "failed"
assert "missing" in result["reason"].lower() or "non-existent" in result["reason"].lower()
assert "database" in result["reason"]
```

---

## Scenario 7: Out-of-Order Input

### Description
Services provided in wrong order. Deployer should calculate correct order.

### Input
```python
services = [
    ServiceConfig(name="frontend", depends_on=["api"], ...),  # Wrong order
    ServiceConfig(name="database", depends_on=[], ...),
    ServiceConfig(name="api", depends_on=["database"], ...)
]

result = await deployer.deploy_all(services)
```

### Expected Output
```python
{
    "status": "success",
    "deployment_order": ["database", "api", "frontend"],  # Correct order
    ...
}
```

### Assertions
```python
assert result["status"] == "success"
assert result["deployment_order"] == ["database", "api", "frontend"]
# Input order doesn't matter, output order is correct
```

---

## Scenario 8: Diamond Dependency

### Description
Multiple services depend on same base service. Verify base deploys first.

### Input
```python
services = [
    ServiceConfig(name="database", depends_on=[], ...),
    ServiceConfig(name="api", depends_on=["database"], ...),
    ServiceConfig(name="worker", depends_on=["database"], ...),
    ServiceConfig(name="frontend", depends_on=["api", "worker"], ...)
]

# Dependency graph:
#     database
#      /    \
#    api    worker
#      \    /
#     frontend
```

### Expected Output
```python
{
    "status": "success",
    "deployment_order": [
        "database",
        # api and worker can be in either order
        "...",  # api or worker
        "...",  # worker or api
        "frontend"  # Must be last
    ]
}
```

### Assertions
```python
assert result["status"] == "success"
order = result["deployment_order"]
assert order[0] == "database"  # Database first
assert order[-1] == "frontend"  # Frontend last
assert set(order[1:3]) == {"api", "worker"}  # api and worker in middle
```

---

## Scenario 9: Empty Service List

### Description
Deploy empty list of services. Should succeed with no operations.

### Input
```python
services = []
result = await deployer.deploy_all(services)
```

### Expected Output
```python
{
    "status": "success",
    "deployment_id": "multi-svc-...",
    "services_deployed": [],
    "deployment_order": [],
    "total_duration_seconds": 0
}
```

### Assertions
```python
assert result["status"] == "success"
assert result["services_deployed"] == []
assert result["deployment_order"] == []
```

---

## Scenario 10: Single Service (No Dependencies)

### Description
Deploy single service with no dependencies. Should work like normal deployment.

### Input
```python
services = [
    ServiceConfig(name="api", version="2.0.0", depends_on=[], ...)
]
result = await deployer.deploy_all(services)
```

### Expected Output
```python
{
    "status": "success",
    "deployment_id": "multi-svc-...",
    "services_deployed": ["api"],
    "deployment_order": ["api"],
    "service_results": {
        "api": {"status": "success", ...}
    }
}
```

### Assertions
```python
assert result["status"] == "success"
assert result["services_deployed"] == ["api"]
```

---

## Scenario 11: Known-Bad Version Combination Flagged

### Description
A version combination that failed before must be flagged BEFORE any service
deploys. This checks the deployment-memory requirement from Section 11.7.
"API v2.1 + Database v3.0 failed last time" stops the second attempt early.

### Setup
First, seed memory with a failed combination. Or run Scenario 3 once with these
versions. That records the failure for you:

```python
await memory.remember_session(
    session_type="multi_service_deployment",
    summary="Failed at api, rolled back 1 service",
    details="API health check failed: high error rate",
    outcome="failure",
    project="multi-service-app",
    metadata={
        "combination": {"database": "3.0.0", "api": "2.1.0"}
    }
)
```

### Input
```python
# Deploy the SAME combination again
services = [
    ServiceConfig(name="database", version="3.0.0", depends_on=[], ...),
    ServiceConfig(name="api", version="2.1.0", depends_on=["database"], ...)
]

result = await deployer.deploy_all(services)
```

### Expected Output
```python
{
    "status": "aborted",
    "deployment_id": "multi-svc-...",
    "reason": "Known-bad combination: database 3.0.0 + api 2.1.0 failed last time (API health check failed: high error rate)",
    "services_deployed": []
}
```

### Assertions
```python
assert result["status"] == "aborted"
assert "combination" in result["reason"].lower()
assert len(result.get("services_deployed", [])) == 0

# An explicit override must still allow the deployment
result = await deployer.deploy_all(services, force=True)
assert result["status"] in ("success", "failed")  # it runs, it is not aborted
```

---

## How to Run These Tests

Nothing here exists yet. You write both the implementation and the tests. Run
everything from the `hands-on-lab` directory, so `starter.*` imports resolve.

### Option 1: A plain script you can run

```python
# challenge-lab/test_multi_service.py
import asyncio
import sys
from pathlib import Path

# Put hands-on-lab/ on the import path so `starter.` resolves no matter
# where the script is run from
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from starter.deployer import ZeroDowntimeDeployer
from multi_service_deployer import MultiServiceDeployer, ServiceConfig

async def test_scenario_3():
    """Test middle service failure with rollback."""
    single_deployer = ZeroDowntimeDeployer(...)
    multi_deployer = MultiServiceDeployer(single_deployer)

    services = [
        ServiceConfig(name="database", version="2.0.0", depends_on=[], ...),
        ServiceConfig(name="api", version="2.0.0-bad", depends_on=["database"], ...),
        ServiceConfig(name="frontend", version="2.0.0", depends_on=["api"], ...)
    ]

    result = await multi_deployer.deploy_all(services)

    assert result["status"] == "failed"
    assert result["failed_service"] == "api"
    assert "database" in result["services_rolled_back"]
    print("Scenario 3 passed")

if __name__ == "__main__":
    asyncio.run(test_scenario_3())
```

Run it with `python challenge-lab/test_multi_service.py` from `hands-on-lab/`.

### Option 2: A pytest suite

```python
# challenge-lab/test_multi_service.py
import pytest
from multi_service_deployer import MultiServiceDeployer, ServiceConfig

@pytest.mark.asyncio
async def test_successful_deployment(multi_deployer):
    """Test Scenario 1: All services deploy successfully."""
    # Implementation based on Scenario 1
    pass

@pytest.mark.asyncio
async def test_first_service_fails(multi_deployer):
    """Test Scenario 2: First service fails."""
    # Implementation based on Scenario 2
    pass

# ... more tests
```

Run with `python -m pytest`, not bare `pytest`. The `-m` form puts the current
directory on the import path. The `starter.` imports need that:

```bash
cd chapter-11/hands-on-lab
python -m pytest challenge-lab/test_multi_service.py -v
```

### Option 3: Reuse the lab's integration fixtures

`starter/tests/test_integration.py` builds a full mock system in its
`full_system` fixture. The system has an infrastructure client, a health
monitor, and memory. Copy that fixture into your test file. You get the same
wiring for the multi-service case, without building the mocks again by hand.

---

## Verification Checklist

Use this checklist to verify your implementation:

- [ ] **Scenario 1**: All services deploy successfully in correct order
- [ ] **Scenario 2**: First service fails, no rollback needed
- [ ] **Scenario 3**: Middle service fails, previous services rolled back
- [ ] **Scenario 4**: Last service fails, all rolled back in reverse order
- [ ] **Scenario 5**: Circular dependency detected before deployment
- [ ] **Scenario 6**: Missing dependency detected before deployment
- [ ] **Scenario 7**: Out-of-order input handled correctly
- [ ] **Scenario 8**: Diamond dependency graph handled correctly
- [ ] **Scenario 9**: Empty list handled gracefully
- [ ] **Scenario 10**: Single service works correctly
- [ ] **Scenario 11**: Previously failed version combination flagged before deployment

## Success Criteria

Your implementation passes the challenge if:
- All 11 scenarios produce expected output
- Rollback always happens in reverse order
- No services deployed when validation fails
- Edge cases handled gracefully
- State tracking is accurate
- Memory flags known-bad version combinations before deploying

## Debugging Tips

If tests fail:

1. **Check deployment order**: Print calculated order vs expected
2. **Verify rollback order**: Ensure reverse of deployment order
3. **Track state changes**: Log state after each operation
4. **Test graph algorithm**: Test topological sort separately
5. **Use small examples**: Test with 2 services before 3
