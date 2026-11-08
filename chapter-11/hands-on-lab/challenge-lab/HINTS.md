# Challenge Lab Hints

Open these hints in order. Try the problem without hints first.

## Hint Levels

- **Hint 1**: Conceptual approach (high-level thinking)
- **Hint 2**: Architectural patterns (design strategies)
- **Hint 3**: Implementation details (code structure)

---

## Hint 1: Conceptual Approach

### Problem Decomposition

Break the challenge into 5 independent sub-problems:

1. **Dependency Graph Construction**
   - Parse service configs into graph structure
   - Nodes = services, Edges = dependencies
   - Example: `api -> database` means API depends on database

2. **Deployment Order Calculation**
   - Input: Dependency graph
   - Output: Linear ordering where dependencies come before dependents
   - Algorithm: Topological sort (Kahn's or DFS-based)

3. **Sequential Deployment Loop**
   - Iterate through services in calculated order
   - For each service: deploy → validate → record state
   - Break loop if any service fails

4. **Failure Handling**
   - If service fails: stop deploying remaining services
   - Identify what was already deployed
   - Rollback in reverse order

5. **State Tracking**
   - Track: deployed, current, pending, failed
   - Update state after each operation
   - Use state to drive rollback decisions

### Key Insight

This builds on your single-service deployer from Exercises 1-2. It adds two things:
- **Ordering logic** (before deployment starts)
- **Coordination state** (during deployment)

Treat it as a transaction. Either all services deploy successfully, or the system rolls back to the initial state.

### Conceptual Flow

```text
1. Parse services → Build dependency graph
2. Sort graph → Get deployment order
3. For each service in order:
   3a. Deploy service (reuse Exercise 1)
   3b. Validate health (reuse Exercise 1)
   3c. If healthy: mark deployed, continue
   3d. If unhealthy: break, go to step 4
4. If any failed: Rollback all deployed (reuse Exercise 2)
5. Record outcome in memory
```

---

## Hint 2: Architectural Patterns

### Pattern 1: Coordinator Pattern

The `MultiServiceDeployer` is a **coordinator**. It does not deploy anything itself. It calls other deployers:

```python
class MultiServiceDeployer:
    def __init__(self, single_service_deployer):
        self.deployer = single_service_deployer  # Delegate actual deployment
        self.state = DeploymentState()           # Track coordination state
```

**Benefits**:
- Separation of concerns
- Reuses existing code
- Easy to test

### Pattern 2: State Machine

Track deployment progress with clear states:

```text
States for entire deployment:
- CALCULATING_ORDER: Determining deployment sequence
- DEPLOYING: Actively deploying services
- ROLLING_BACK: Rolling back due to failure
- COMPLETED: All services deployed successfully
- FAILED: Deployment failed after rollback

States per service:
- PENDING: Not deployed yet
- DEPLOYING: Currently being deployed
- DEPLOYED: Successfully deployed
- FAILED: Deployment failed
- ROLLED_BACK: Was deployed, then rolled back
```

### Pattern 3: Transaction Pattern

Apply database transaction semantics:
- **All or nothing**: Either all services deploy or none do
- **Atomicity**: Deployment as a single unit
- **Consistency**: System always in valid state
- **Rollback on failure**: Automatic cleanup

### Dependency Graph Structure

```python
from collections import defaultdict

# Graph representation
graph = {
    "database": [],              # No dependencies
    "api": ["database"],         # Depends on database
    "frontend": ["api"]          # Depends on api
}

# In-degree (number of dependencies)
in_degree = {
    "database": 0,
    "api": 1,
    "frontend": 1
}
```

### Topological Sort Algorithm (Kahn's)

```text
1. Find all nodes with in-degree 0 (no dependencies)
2. Add them to queue
3. While queue not empty:
   3a. Remove node from queue
   3b. Add to result order
   3c. For each neighbor:
       - Decrease neighbor's in-degree by 1
       - If in-degree becomes 0, add to queue
4. If result length != number of nodes:
   - Circular dependency detected
```

### Rollback Strategy

**Reverse Order Rollback**:
```text
Deployment:  A → B → C → D (D fails)
Rollback:    D (cleanup) ← C ← B ← A

Why reverse?
- C might depend on B
- Rolling back B before C breaks C
- Must rollback in opposite order to maintain dependencies
```

**Rollback Implementation Pattern**:
```python
async def rollback_all(deployed_services):
    # Reverse the list
    for service_name in reversed(deployed_services):
        # Get service config
        service = get_service_by_name(service_name)

        # Rollback using Exercise 2 logic
        result = await self.deployer.rollback(service, reason)

        # Handle rollback failure
        if not result["success"]:
            await escalate_critical_failure(service_name)
            break
```

### State Tracking Design

```python
@dataclass
class DeploymentState:
    """Track multi-service deployment state."""
    pending: List[str]           # Not deployed yet
    deploying: Optional[str]     # Currently deploying
    deployed: List[str]          # Successfully deployed
    failed: Optional[str]        # Service that failed
    rolling_back: List[str]      # Currently rolling back
    rolled_back: List[str]       # Rollback complete

    def mark_deploying(self, service_name: str):
        self.pending.remove(service_name)
        self.deploying = service_name

    def mark_deployed(self, service_name: str):
        self.deploying = None
        self.deployed.append(service_name)

    def mark_failed(self, service_name: str):
        self.deploying = None
        self.failed = service_name
```

### Error Handling Strategy

```python
# Validate before deployment starts
def validate_dependencies(services):
    for service in services:
        for dep in service.depends_on:
            if dep not in [s.name for s in services]:
                raise MissingDependencyError(f"{service.name} depends on missing service: {dep}")

# Detect circular dependencies
def detect_cycles(graph):
    # If topological sort fails, there's a cycle
    try:
        order = topological_sort(graph)
    except ValueError:
        raise CircularDependencyError("Circular dependency detected in services")
```

---

## Hint 3: Implementation Details

### Dependency Graph Construction

```python
def _build_dependency_graph(self, services: List[ServiceConfig]) -> Dict:
    """Build adjacency list and in-degree map."""
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    service_map = {s.name: s for s in services}

    # Initialize all services
    for service in services:
        if service.name not in in_degree:
            in_degree[service.name] = 0

    # Build edges
    for service in services:
        for dependency in service.depends_on:
            # Validate dependency exists
            if dependency not in service_map:
                raise MissingDependencyError(
                    f"Service '{service.name}' depends on non-existent service '{dependency}'"
                )

            # Add edge: dependency -> service
            graph[dependency].append(service.name)
            in_degree[service.name] += 1

    return graph, in_degree, service_map
```

### Topological Sort Implementation

```python
def _calculate_deployment_order(self, services: List[ServiceConfig]) -> List[str]:
    """Calculate deployment order using Kahn's algorithm."""
    from collections import deque

    graph, in_degree, service_map = self._build_dependency_graph(services)

    # Find all nodes with no dependencies
    queue = deque([name for name, degree in in_degree.items() if degree == 0])
    order = []

    while queue:
        # Remove node with no dependencies
        current = queue.popleft()
        order.append(current)

        # For each service that depends on current
        for dependent in graph[current]:
            in_degree[dependent] -= 1

            # If dependent now has no remaining dependencies
            if in_degree[dependent] == 0:
                queue.append(dependent)

    # If we didn't process all services, there's a cycle
    if len(order) != len(services):
        raise CircularDependencyError(
            f"Circular dependency detected. Processed {len(order)}/{len(services)} services."
        )

    return order
```

### Sequential Deployment with State Tracking

```python
async def deploy_all(self, services: List[ServiceConfig]) -> Dict:
    """Deploy all services in dependency order."""
    from datetime import datetime

    deployment_id = f"multi-svc-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    start_time = datetime.now()

    # Calculate deployment order
    try:
        deployment_order = self._calculate_deployment_order(services)
    except (CircularDependencyError, MissingDependencyError) as e:
        return {
            "status": "failed",
            "deployment_id": deployment_id,
            "reason": str(e)
        }

    # Initialize state
    state = DeploymentState(
        pending=deployment_order.copy(),
        deployed=[],
        deploying=None,
        failed=None
    )

    service_map = {s.name: s for s in services}
    service_results = {}

    # Deploy each service sequentially
    for service_name in deployment_order:
        service = service_map[service_name]
        state.mark_deploying(service_name)

        print(f"Deploying {service_name}...")

        # Deploy using single-service deployer
        result = await self.deployer.deploy(service)
        service_results[service_name] = result

        if result["status"] != "success":
            # Deployment failed
            state.mark_failed(service_name)

            print(f"{service_name} deployment failed: {result.get('reason')}")

            # Rollback all deployed services
            rollback_result = await self._rollback_all_deployed(
                state.deployed,
                service_map,
                reason=f"{service_name} deployment failed"
            )

            return {
                "status": "failed",
                "deployment_id": deployment_id,
                "failed_service": service_name,
                "failure_reason": result.get("reason"),
                "services_deployed": state.deployed,
                "services_rolled_back": rollback_result["services_rolled_back"],
                "rollback_duration_seconds": rollback_result["duration_seconds"],
                "service_results": service_results
            }

        # Deployment succeeded
        state.mark_deployed(service_name)
        print(f"{service_name} deployed successfully")

    # All services deployed successfully
    duration = (datetime.now() - start_time).seconds

    # Record in memory
    if self.memory:
        await self._record_multi_service_deployment(
            deployment_id,
            services,
            deployment_order,
            duration,
            "success"
        )

    return {
        "status": "success",
        "deployment_id": deployment_id,
        "services_deployed": state.deployed,
        "deployment_order": deployment_order,
        "total_duration_seconds": duration,
        "service_results": service_results
    }
```

### Coordinated Rollback

```python
async def _rollback_all_deployed(
    self,
    deployed_services: List[str],
    service_map: Dict[str, ServiceConfig],
    reason: str
) -> Dict:
    """Roll back all deployed services in reverse order."""
    from datetime import datetime

    start_time = datetime.now()
    rolled_back = []

    print(f"Starting coordinated rollback: {reason}")

    # Rollback in REVERSE order
    for service_name in reversed(deployed_services):
        service = service_map[service_name]

        print(f"   Rolling back {service_name}...")

        rollback_result = await self.deployer.rollback(
            service,
            reason=f"Cascading rollback due to multi-service deployment failure: {reason}"
        )

        if not rollback_result["success"]:
            # Critical: rollback failed
            print(f"CRITICAL: Rollback of {service_name} failed")

            # Record critical failure in memory
            if self.memory:
                await self.memory.remember_session(
                    session_type="incident",
                    summary=f"CRITICAL: Multi-service rollback failed at {service_name}",
                    details=f"Reason: {reason}. Rollback result: {rollback_result}",
                    outcome="critical_failure",
                    project="multi-service-app"
                )

            # Don't continue rollback - escalate to human
            break

        rolled_back.append(service_name)
        print(f"   {service_name} rolled back")

    duration = (datetime.now() - start_time).seconds

    return {
        "success": len(rolled_back) == len(deployed_services),
        "services_rolled_back": rolled_back,
        "duration_seconds": duration
    }
```

### Memory Integration

```python
async def _record_multi_service_deployment(
    self,
    deployment_id: str,
    services: List[ServiceConfig],
    deployment_order: List[str],
    duration_seconds: int,
    outcome: str
):
    """Record multi-service deployment in memory."""
    if not self.memory:
        return

    await self.memory.remember_session(
        session_type="multi_service_deployment",
        summary=f"Multi-service deployment {deployment_id}: {outcome}",
        details={
            "deployment_id": deployment_id,
            "services": [s.name for s in services],
            "deployment_order": deployment_order,
            "duration_seconds": duration_seconds
        },
        outcome=outcome,
        project="multi-service-app",
        metadata={
            "service_count": len(services),
            "deployment_type": "coordinated_multi_service",
            # The combination is what the pre-deployment check queries later
            "combination": {s.name: s.version for s in services}
        }
    )
```

### Known-Bad Combination Check (Scenario 11)

Run this check at the top of `deploy_all()`. Run it after ordering succeeds and
before any service deploys. The combination lives in each record's metadata
(see above). So the check compares dicts. It does not parse summaries:

```python
async def _check_known_bad_combination(
    self,
    services: List[ServiceConfig]
) -> Optional[Dict]:
    """Return the past failure record if this exact combination failed before."""
    if not self.memory:
        return None

    combination = {s.name: s.version for s in services}
    recalled = await self.memory.recall(
        query="multi-service deployment failed", n_results=20
    )

    for record in recalled.get("episodic", []):
        if (
            record.get("outcome") == "failure"
            and record.get("metadata", {}).get("combination") == combination
        ):
            return record

    return None
```

And in `deploy_all()`:

```python
    bad_record = await self._check_known_bad_combination(services)
    if bad_record and not force:
        combo = ", ".join(
            f"{name} {version}"
            for name, version in bad_record["metadata"]["combination"].items()
        )
        print(f"WARNING: Known-bad combination: {combo} failed last time")
        return {
            "status": "aborted",
            "deployment_id": deployment_id,
            "reason": (
                f"Known-bad combination: {combo} failed last time "
                f"({bad_record.get('details')})"
            ),
            "services_deployed": []
        }
```

Give `deploy_all()` a `force: bool = False` parameter. A human can then retry a
flagged combination on purpose, after fixing the underlying issue.

### Complete Class Structure

```python
from typing import Dict, List, Optional
from dataclasses import dataclass
from collections import defaultdict, deque

@dataclass
class ServiceConfig:
    name: str
    version: str
    image: str
    depends_on: List[str]
    health_check_endpoint: str
    replicas: int = 3
    canary_percentage: int = 10

@dataclass
class DeploymentState:
    pending: List[str]
    deploying: Optional[str]
    deployed: List[str]
    failed: Optional[str]

    def mark_deploying(self, service_name: str):
        self.pending.remove(service_name)
        self.deploying = service_name

    def mark_deployed(self, service_name: str):
        self.deploying = None
        self.deployed.append(service_name)

    def mark_failed(self, service_name: str):
        self.deploying = None
        self.failed = service_name

class CircularDependencyError(Exception):
    pass

class MissingDependencyError(Exception):
    pass

class MultiServiceDeployer:
    def __init__(self, single_service_deployer, memory=None):
        self.deployer = single_service_deployer
        self.memory = memory

    async def deploy_all(self, services: List[ServiceConfig]) -> Dict:
        # See implementation above
        pass

    def _calculate_deployment_order(self, services: List[ServiceConfig]) -> List[str]:
        # See implementation above
        pass

    def _build_dependency_graph(self, services: List[ServiceConfig]) -> tuple:
        # See implementation above
        pass

    async def _rollback_all_deployed(
        self,
        deployed_services: List[str],
        service_map: Dict[str, ServiceConfig],
        reason: str
    ) -> Dict:
        # See implementation above
        pass

    async def _record_multi_service_deployment(self, ...):
        # See implementation above
        pass
```

---

## When to Use Each Hint

- **Stuck on overall approach?** → Use Hint 1 (conceptual)
- **Need design patterns?** → Use Hint 2 (architectural)
- **Having implementation issues?** → Use Hint 3 (code details)

## Learning Strategy

1. **Read Hint 1** to understand the problem decomposition
2. **Try implementing** based on conceptual understanding
3. **If stuck on design**, read Hint 2 for patterns
4. **If implementation is unclear**, reference Hint 3 for code structure
5. **Type the code yourself.** Do not copy-paste it

Use the hints as guidance. Do not copy them as the solution.
