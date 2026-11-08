# Challenge Problem: Multi-Service Deployment Orchestration

## Problem Statement

Design and implement a `MultiServiceDeployer` class. It runs zero-downtime deployments across several interdependent microservices. When a deployment fails, it rolls back the deployed services together.

## System Architecture

You deploy a 3-tier microservices application:

```text
Frontend (web-ui:3000)
    ↓ depends on
API (backend-api:8000)
    ↓ depends on
Database (postgres:5432)
```

**Dependency Rules**:
- Database has no dependencies (deployed first)
- API depends on Database (deployed second, only if Database is healthy)
- Frontend depends on API (deployed third, only if API is healthy)

## Technical Requirements

### 1. Service Configuration

Each service is represented by a `ServiceConfig` object:

```python
@dataclass
class ServiceConfig:
    name: str                      # Service identifier (e.g., "database")
    version: str                   # Version to deploy (e.g., "2.0.0")
    image: str                     # Container image (e.g., "postgres:14")
    depends_on: List[str]          # Service names this depends on
    health_check_endpoint: str     # Health check path or command
    replicas: int = 3              # Number of instances
    canary_percentage: int = 10    # Canary traffic percentage
```

### 2. Deployment Ordering

**Input**: List of services in ANY order
**Output**: Services deployed in CORRECT dependency order

**Algorithm Required**: Topological sort of dependency graph

**Example**:
```python
# Input (random order)
services = [
    ServiceConfig(name="frontend", depends_on=["api"], ...),
    ServiceConfig(name="database", depends_on=[], ...),
    ServiceConfig(name="api", depends_on=["database"], ...)
]

# Your code must determine order: [database, api, frontend]
```

Start from the book's Section 11.7 `deployment_order(services)` listing. It
returns the services in this order. It has two gaps:

- It accepts a cycle. It returns an order for `a -> b -> c -> a` instead of failing.
- It skips a dependency that is not in the list.

Add both checks before you rely on it (Scenarios 5 and 6 in `test_scenarios.md`).

**Edge Cases to Handle**:
- Circular dependencies → Detect and raise error before deployment
- Missing dependencies → Detect and raise error before deployment
- Multiple independent services → Deploy in any valid order

### 3. Sequential Deployment with Validation

For each service in dependency order:

1. **Deploy** the service using `ZeroDowntimeDeployer` from Exercise 1
2. **Validate** health using canary validation from Exercise 1
3. **Check** if validation passed:
   - **Success**: Record state, move to next service
   - **Failure**: Stop deployment, initiate cascading rollback
4. **Track** deployment state at each step

**State Tracking Required**:
```python
{
    "deployed": ["database", "api"],           # Successfully deployed
    "current": "frontend",                      # Currently deploying
    "pending": [],                              # Not yet deployed
    "failed": None                              # Service that failed (if any)
}
```

### 4. Coordinated Rollback

If ANY service fails validation:

1. **Stop** deploying remaining services
2. **Identify** all successfully deployed services
3. **Rollback** in REVERSE order (last deployed, first rolled back)
4. **Verify** each rollback succeeded
5. **Record** coordinated rollback event in memory

**Rollback Order Example**:
```text
Deployment order: database → api → frontend
                     OK       OK      FAILED

Rollback order:   frontend (remove) → api (rollback) → database (rollback)
```

**Critical**: Must rollback in reverse order to maintain dependency consistency.

### 5. Partial Deployment Recovery

Handle scenarios where deployment is interrupted:

**Scenario A**: Database deployed, API fails
- State: Database is running v2.0.0
- Action: Roll back database to v1.0.0
- Result: System fully on v1.0.0

**Scenario B**: Database and API deployed, Frontend fails
- State: Database and API running v2.0.0
- Action: Roll back API, then Database (in that order)
- Result: System fully on v1.0.0

**Scenario C**: Deployment crashes mid-process
- State: Unknown/inconsistent
- Action: Detect deployed services, initiate cleanup
- Result: System returned to stable state

### 6. Memory Integration

Record multi-service deployment coordination:

```python
# Successful deployment
await memory.remember_session(
    session_type="multi_service_deployment",
    summary=f"Deployed 3 services: database, api, frontend",
    details={
        "services": ["database", "api", "frontend"],
        "order": ["database", "api", "frontend"],
        "total_duration_seconds": 450
    },
    outcome="success",
    project="multi-service-app"
)

# Failed deployment with rollback
await memory.remember_session(
    session_type="multi_service_deployment",
    summary=f"Failed at api, rolled back 1 service",
    details={
        "failed_service": "api",
        "services_rolled_back": ["database"],
        "failure_reason": "API health check failed: high error rate"
    },
    outcome="failure",
    project="multi-service-app"
)
```

**Known-bad version combinations** (Section 11.7 requires this):

Record which service **version combination** was deployed together, and whether
it succeeded. Use that history before the next deployment:

1. On every outcome (success or failure), include the combination in the
   record's metadata, e.g. `{"database": "3.0.0", "api": "2.1.0",
   "frontend": "2.0.0"}`.
2. Before deploying, check memory for the exact combination you are about to
   deploy. It may have failed before ("API v2.1 + Database v3.0 failed last
   time"). If so, flag it:
   - Warn with the past failure reason.
   - Abort with `status: "aborted"`, unless the caller explicitly overrides
     (e.g. `deploy_all(services, force=True)`).

The second attempt at a bad combination stops before any service deploys. The
API does not fail at 50% traffic again. See Scenario 11 in `test_scenarios.md`
and the combination-check hint in `HINTS.md` (Hint 3).

## Input/Output Specifications

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
        version="2.0.0",
        image="backend-api:2.0.0",
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

deployer = MultiServiceDeployer(single_service_deployer)
result = await deployer.deploy_all(services)
```

### Output (Success Case)

```python
{
    "status": "success",
    "deployment_id": "multi-svc-20260205143022",
    "services_deployed": ["database", "api", "frontend"],
    "deployment_order": ["database", "api", "frontend"],
    "total_duration_seconds": 450,
    "service_results": {
        "database": {
            "status": "success",
            "version": "2.0.0",
            "duration_seconds": 120,
            "validation": {"healthy": True, ...}
        },
        "api": {
            "status": "success",
            "version": "2.0.0",
            "duration_seconds": 180,
            "validation": {"healthy": True, ...}
        },
        "frontend": {
            "status": "success",
            "version": "2.0.0",
            "duration_seconds": 150,
            "validation": {"healthy": True, ...}
        }
    }
}
```

### Output (Failure Case)

```python
{
    "status": "failed",
    "deployment_id": "multi-svc-20260205143022",
    "failed_service": "api",
    "failure_reason": "API validation failed: error rate 2.5% exceeds threshold 1.0%",
    "services_deployed": ["database"],          # Before failure
    "services_rolled_back": ["database"],       # After rollback
    "rollback_duration_seconds": 30,
    "service_results": {
        "database": {
            "status": "deployed_then_rolled_back",
            "version": "2.0.0",
            "deployment_duration_seconds": 120,
            "rollback_result": {"success": True, ...}
        },
        "api": {
            "status": "failed",
            "version": "2.0.0",
            "failure_reason": "High error rate during validation",
            "validation": {"healthy": False, ...}
        },
        "frontend": {
            "status": "not_attempted",
            "reason": "Deployment stopped due to api failure"
        }
    }
}
```

## API Design

### Main Class Interface

```python
class MultiServiceDeployer:
    """Orchestrates multi-service deployments with coordinated rollback."""

    def __init__(
        self,
        single_service_deployer: ZeroDowntimeDeployer,
        memory = None
    ):
        """
        Initialize multi-service deployer.

        Args:
            single_service_deployer: Deployer from Exercises 1-2
            memory: DevMemory instance for recording coordination
        """
        pass

    async def deploy_all(
        self,
        services: List[ServiceConfig]
    ) -> Dict:
        """
        Deploy multiple services in dependency order.

        Args:
            services: List of services to deploy (any order)

        Returns:
            Deployment result with status, deployed services, rollback info

        Raises:
            CircularDependencyError: If circular dependency detected
            MissingDependencyError: If service depends on non-existent service
        """
        pass

    def _calculate_deployment_order(
        self,
        services: List[ServiceConfig]
    ) -> List[str]:
        """
        Calculate deployment order using topological sort.

        Args:
            services: List of services

        Returns:
            List of service names in deployment order

        Raises:
            CircularDependencyError: If cycle detected
        """
        pass

    async def _deploy_service(
        self,
        service: ServiceConfig
    ) -> Dict:
        """
        Deploy a single service using ZeroDowntimeDeployer.

        Args:
            service: Service to deploy

        Returns:
            Deployment result
        """
        pass

    async def _rollback_all_deployed(
        self,
        deployed_services: List[str],
        reason: str
    ) -> Dict:
        """
        Roll back all deployed services in reverse order.

        Args:
            deployed_services: Services to roll back (in deployment order)
            reason: Why rollback is happening

        Returns:
            Rollback result with success status
        """
        pass
```

## Constraints

1. **Reuse Exercise Code**: Must use `ZeroDowntimeDeployer` for individual service deployments
2. **No Modifications to Starter Code**: Extend the existing deployer. Do not modify it
3. **Async Operations**: All deployment operations must be async
4. **State Immutability**: Don't modify input service configs
5. **Memory Optional**: Should work even if memory is None

## Edge Cases to Handle

### 1. Circular Dependencies

```python
# A depends on B, B depends on A
services = [
    ServiceConfig(name="A", depends_on=["B"], ...),
    ServiceConfig(name="B", depends_on=["A"], ...)
]

# Expected: Raise CircularDependencyError before deployment
```

### 2. Missing Dependencies

```python
# API depends on "database" but database not in list
services = [
    ServiceConfig(name="api", depends_on=["database"], ...)
]

# Expected: Raise MissingDependencyError before deployment
```

### 3. First Service Fails

```python
# Database deployment fails immediately
# Expected: No rollback needed (nothing deployed yet)
```

### 4. Rollback Failure

```python
# Service deployment fails, rollback attempted but also fails
# Expected: Escalate to human, record critical incident
```

### 5. Empty Service List

```python
services = []
# Expected: Return success with no services deployed
```

### 6. Single Service

```python
services = [ServiceConfig(name="api", depends_on=[], ...)]
# Expected: Deploy single service normally
```

## Performance Considerations

- **Timeouts**: Each deployment has timeout (default 10 minutes)
- **Rollback Speed**: Rollback should be faster than deployment (no canary needed)
- **Memory Usage**: Track deployment state efficiently
- **Error Handling**: Fast-fail on critical errors

## Validation Requirements

Your solution must pass these checks:

1. Correctly orders services by dependencies
2. Deploys services sequentially
3. Validates each service before proceeding
4. Stops on first failure
5. Rolls back in reverse order
6. Handles circular dependencies
7. Handles missing dependencies
8. Records events in memory
9. Flags previously failed version combinations before deploying
10. Returns structured results

## Testing

See `test_scenarios.md` for test cases covering:
- Happy path (all services succeed)
- Failure scenarios (first, middle, last service fails)
- Edge cases (circular deps, missing deps)
- Rollback verification

## Implementation Tips

1. **Start with ordering**: Get topological sort working first
2. **Add sequential deployment**: Deploy one service at a time
3. **Integrate validation**: Use existing canary validation
4. **Implement rollback**: Handle failures with coordinated rollback
5. **Add state tracking**: Track what's deployed at each step
6. **Handle edge cases**: Circular deps, missing deps, etc.

## Success Metrics

- **Correctness**: All test scenarios pass
- **Code Quality**: Clean, readable, well-documented
- **Reusability**: Uses existing deployer effectively
- **Error Handling**: Graceful failure handling
- **State Management**: Clear state tracking throughout

---

If you get stuck, check `HINTS.md`, or read `APPROACH.md` for the high-level strategy.

Your code does not need to be perfect. Get it working, then improve it.
