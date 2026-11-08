# Solution Approach (No Code)

This document describes the high-level solution approach. It has no implementation code. Use it to check your design. Do not use it as a code template.

## Overview

You build a coordination layer on top of your single-service deployer. It adds orchestration logic. It reuses the deployment and rollback code from Exercises 1-2.

## Core Components

### 1. Dependency Resolution Engine

**Problem**: Given services in any order with dependencies, determine the correct deployment sequence.

**Approach**: Graph algorithms
- Represent services as nodes in a directed graph
- Dependencies are edges (A → B means B depends on A)
- Use topological sort to find valid ordering
- Detect cycles (circular dependencies) during sort
- Validate all dependencies exist before sorting

**Algorithm Choice**: Kahn's Algorithm
- Efficient O(V + E) time complexity
- Naturally detects cycles
- Easy to implement with queue
- Produces intuitive ordering

**Alternative**: DFS-based topological sort also works

### 2. Sequential Deployment Orchestrator

**Problem**: Deploy services one at a time, ensuring each is healthy before proceeding.

**Approach**: State machine with sequential processing
- Calculate deployment order first (fail fast if invalid)
- Iterate through services in order
- For each service:
  - Deploy using existing `ZeroDowntimeDeployer`
  - Validate using existing canary validation
  - Update state (deployed, deploying, failed)
  - Break on first failure

**Key point**: Do not reimplement deployment. Call the existing deployers.

**Design Pattern**: Coordinator Pattern
- Delegates work to specialized components
- Tracks overall state and progress
- Makes coordination decisions

### 3. State Management System

**Problem**: Track which services are deployed, deploying, pending, or failed.

**Approach**: Explicit state tracking with immutable transitions

**State Structure**:
```text
DeploymentState:
  - pending: List of services not yet deployed
  - deploying: Currently deploying service (max 1)
  - deployed: Successfully deployed services
  - failed: Service that caused failure (if any)
```

**State Transitions**:
```text
pending → deploying → deployed (success)
pending → deploying → failed (failure)
deployed → rolling_back → rolled_back (on failure)
```

**Why Important**:
- Makes debugging easier (clear state at each step)
- Enables rollback decisions (know what to rollback)
- Supports interruption recovery (can resume/cleanup)

### 4. Coordinated Rollback Orchestrator

**Problem**: When one service fails, roll back all previously deployed services safely.

**Approach**: Reverse-order rollback with transaction semantics

**Rollback Algorithm**:
1. Identify all services in "deployed" state
2. Reverse the list (last deployed becomes first to rollback)
3. For each service (in reverse):
   - Call existing `rollback()` from Exercise 2
   - Verify rollback succeeded
   - Update state (rolled_back)
   - If rollback fails, escalate to human

**Why Reverse Order**:
- Services may depend on each other at runtime
- Frontend might be serving traffic that calls API
- Rolling back API before Frontend breaks Frontend
- Must maintain dependency consistency

**Transaction Semantics**:
- Either all services deploy successfully
- Or system returns to initial state
- No partial deployments left running

### 5. Edge Case Handling

**Circular Dependencies**:
- Detect during topological sort
- Happens when sort produces fewer nodes than input
- Fail before any deployment starts
- Return clear error message

**Missing Dependencies**:
- Validate during graph construction
- Check each dependency exists in service list
- Fail before any deployment starts
- Return specific missing dependency name

**Rollback Failures**:
- Critical situation - deployed service can't be rolled back
- Don't continue rollback (might make things worse)
- Escalate to human immediately
- Record as critical incident in memory

**Empty Input**:
- Handle gracefully
- Return success with empty results

**Single Service**:
- Simplify to single-service deployment
- Still works through orchestration layer

## Design Patterns Used

### Coordinator Pattern
```text
MultiServiceDeployer (coordinator)
    ├── Uses ZeroDowntimeDeployer (worker)
    ├── Tracks DeploymentState (state)
    └── Records in DevMemory (memory)
```

**Benefits**:
- Separation of concerns
- Reusability of existing code
- Clear responsibility boundaries

### State Machine Pattern

**States**: Explicit enumeration of deployment phases
**Transitions**: Well-defined state changes
**Immutability**: Previous states preserved for debugging

**Benefits**:
- Easy to reason about
- Testable state transitions
- Clear error handling

### Transaction Pattern

**Atomicity**: All services or none
**Consistency**: System always in valid state
**Rollback**: Automatic on failure

**Benefits**:
- Predictable failure handling
- No orphaned resources
- Clear success/failure outcomes

### Strategy Pattern

**Deployment Strategy**: Pluggable via `ZeroDowntimeDeployer`
**Validation Strategy**: Reuses canary validation
**Rollback Strategy**: Reuses automatic rollback

**Benefits**:
- Flexibility to change strategies
- Testing with mock strategies
- Extension for other deployment types

## Implementation Strategy

### Phase 1: Dependency Resolution (30 minutes)
1. Implement graph construction
2. Implement topological sort
3. Add cycle detection
4. Add missing dependency detection
5. Test with various dependency patterns

### Phase 2: Sequential Deployment (45 minutes)
1. Create deployment loop
2. Integrate with existing deployer
3. Add state tracking
4. Handle deployment success
5. Test happy path

### Phase 3: Failure Handling (30 minutes)
1. Detect deployment failures
2. Implement coordinated rollback
3. Update state on rollback
4. Handle rollback failures
5. Test failure scenarios

### Phase 4: Polish & Testing (30 minutes)
1. Add memory integration
2. Improve error messages
3. Add logging/monitoring
4. Test all edge cases
5. Verify with test scenarios

## Testing Strategy

### Unit Tests
- Dependency graph construction
- Topological sort correctness
- State transitions
- Edge case handling

### Integration Tests
- Happy path (all succeed)
- Failure scenarios (first, middle, last fails)
- Rollback verification
- Memory recording

### Test Data Patterns
```text
Simple chain: A → B → C
Diamond: A → B, A → C, B → D, C → D
Multiple roots: A → C, B → C
Circular: A → B → C → A
Missing: A → B (but B not in list)
```

## Common Mistakes to Avoid

### Mistake 1: Rewriting Deployment Logic
**Wrong**: Implement canary deployment inside `MultiServiceDeployer`
**Right**: Call existing `ZeroDowntimeDeployer.deploy()`

### Mistake 2: Wrong Rollback Order
**Wrong**: Roll back in deployment order
**Right**: Roll back in REVERSE order (last deployed, first rolled back)

### Mistake 3: Not Tracking State
**Wrong**: Rely on infrastructure to tell you what's deployed
**Right**: Track state explicitly in your code

### Mistake 4: Ignoring Edge Cases
**Wrong**: Assume input is always valid
**Right**: Validate input, detect cycles, handle empty lists

### Mistake 5: Overcomplicating
**Wrong**: Try to handle every possible scenario
**Right**: Focus on core requirements, keep it simple

## Extension Ideas (After Core Challenge)

### Parallel Deployment
Deploy independent services simultaneously:
```text
A → C    Can deploy A and B in parallel
B → C    Both can deploy simultaneously
```

### Partial Rollback
Only roll back affected services:
```text
If C fails, only roll back services that depend on C
```

### Health Check Retries
Retry validation before declaring failure:
```text
If health check fails, wait and retry 3 times
```

### Deployment Versioning
Track entire deployment as a unit:
```text
deployment-v1: database:1.0, api:1.0, frontend:1.0
deployment-v2: database:2.0, api:2.0, frontend:2.0
```

### Progressive Rollout
After initial deployment, gradually shift more traffic:
```text
Deploy → 10% → 25% → 50% → 100%
With validation at each step
```

## Success Indicators

You know your solution works when:

- Services always deploy in correct dependency order
- Failure in any service triggers complete rollback
- Circular dependencies detected before deployment
- Missing dependencies reported clearly
- State is tracked accurately throughout
- Existing deployer code is reused, not reimplemented
- Tests pass for all scenarios
- Code is readable and maintainable

## Time Allocation

Suggested breakdown for 2-3 hour challenge:

- **Understanding requirements**: 30 min
- **Design sketch**: 15 min
- **Graph algorithms**: 30 min
- **Deployment loop**: 45 min
- **Rollback coordination**: 30 min
- **Testing**: 30 min
- **Refinement**: 15 min

Adjust based on your experience level.

## Further Reading

Where these deployment patterns fit in CA/CD: Chapter 11, Section 11.7.

---

Start with dependency graph construction, then build incrementally.
