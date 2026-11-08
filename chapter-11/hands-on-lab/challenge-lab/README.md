# Challenge Lab: Multi-Service Deployment Orchestration

This is the challenge lab for **Chapter 11, Section 11.7**. It extends the
Zero-Downtime Deployer you built in Section 11.6 (`../starter/`, `../complete/`).

## Overview

You extend your Zero-Downtime Deployer to deploy several interdependent
microservices with coordinated rollback.

**Scenario**: A microservices application has three services that depend on each
other.

1. Each service deploys in dependency order.
2. Each service is validated on its own.
3. If any one fails, every service already deployed rolls back in reverse order.

There is **no reference solution** here. The design decisions are the exercise.
`HINTS.md` gives graduated help. `APPROACH.md` describes a strategy without
code.

Why multi-service deployments need coordinated rollback: Chapter 11, Section 11.7.

## Coming from the book?

| The book (Section 11.7) | In this directory |
|-------------------------|-------------------|
| `pytest tests/test_multi_service.py -v` | You write the test file. Put it at `challenge-lab/test_multi_service.py` and run `python -m pytest challenge-lab/test_multi_service.py -v` from `hands-on-lab/` (see "Where your code goes" below). |
| "Extend `ZeroDowntimeDeployer` to accept a list of `ServiceConfig` objects" | `PROBLEM.md` specifies a `MultiServiceDeployer` that wraps your single-service deployer. A subclass of `ZeroDowntimeDeployer` that takes the list works too; the scenarios test behavior, not the class layout. |
| The `deployment_order(services)` listing | Use it as your starting point. It returns `ServiceConfig` objects in order. It does not reject a cycle or a missing dependency. Scenarios 5 and 6 require both. `PROBLEM.md` names the method `_calculate_deployment_order`. |

## What's in this directory

| File | What it gives you |
|------|-------------------|
| `PROBLEM.md` | The technical requirements and interface you build against |
| `GETTING_STARTED.md` | How to approach the work, step by step |
| `HINTS.md` | Three escalating levels: conceptual, architectural, implementation |
| `APPROACH.md` | A solution strategy in prose, no code |
| `test_scenarios.md` | The cases your implementation has to handle |
| `INSTRUCTOR_NOTES.md` | Teaching notes if you are running this as a session |
| `.challenge-index.md` | Reading order and time estimates |

## Learning Objectives

By completing this challenge, you will:
- Understand service dependency management in deployments
- Implement deployment ordering based on dependency graphs
- Handle cascading failures across multiple services
- Coordinate multi-service rollbacks
- Apply canary and rollback patterns from Exercises 1-2 at scale
- Build stateful deployment coordination logic

## The Challenge

Build a `MultiServiceDeployer` that orchestrates the deployment of interdependent services:

1. **Dependency-Aware Ordering**: Deploy services in correct dependency order (e.g., database before API, API before frontend)
2. **Sequential Validation**: Validate each service independently before deploying the next
3. **Coordinated Rollback**: If any service fails, roll back ALL previously deployed services
4. **State Tracking**: Maintain deployment state to support partial deployment scenarios
5. **Memory Integration**: Record which version combinations deployed together successfully. Before you deploy a combination again, flag it if it failed before (e.g., "API v2.1 + Database v3.0 failed last time")

## Difficulty Level

**Advanced** - This challenge requires:
- Completing Exercises 1 & 2
- Graph algorithms (topological sort)
- State machine design
- Coordination logic
- Error handling across boundaries

## Time Estimate

- **Understanding requirements**: 30 minutes
- **Design and implementation**: 1.5-2 hours
- **Testing and refinement**: 30-45 minutes

**Total**: 2-3 hours

## Architecture

```text
┌─────────────────────────────────────────────────┐
│         MultiServiceDeployer                    │
│                                                 │
│  ┌──────────────────────────────────────┐     │
│  │  Dependency Graph                    │     │
│  │  ┌─────────┐      ┌─────────┐       │     │
│  │  │Database │◄─────│   API   │◄──┐   │     │
│  │  └─────────┘      └─────────┘   │   │     │
│  │       ▲                          │   │     │
│  │       │           ┌──────────┐  │   │     │
│  │       └───────────│ Frontend │──┘   │     │
│  │                   └──────────┘      │     │
│  └──────────────────────────────────────┘     │
│                                                 │
│  ┌──────────────────────────────────────┐     │
│  │  Deployment Coordination             │     │
│  │  • Order calculation                 │     │
│  │  • Sequential deployment             │     │
│  │  • Health validation                 │     │
│  │  • Rollback orchestration            │     │
│  └──────────────────────────────────────┘     │
│                                                 │
│  Reuses: ZeroDowntimeDeployer (Ex 1 & 2)      │
└─────────────────────────────────────────────────┘
```

## Where your code goes

There is no starter scaffold. Create your own module next to the lab code. Then
you can import the deployer you already built:

```bash
cd chapter-11/hands-on-lab
touch challenge-lab/multi_service_deployer.py
touch challenge-lab/test_multi_service.py
```

Then import from your finished work:

```python
from starter.deployer import ZeroDowntimeDeployer   # or complete.deployer
from starter.config import DeploymentConfig
```

Run your tests from the `hands-on-lab` directory with `python -m pytest`, not
bare `pytest`. The `-m` form puts the current directory on the import path. The
`starter.` imports need that, because `challenge-lab/` is not a package:

```bash
python -m pytest challenge-lab/test_multi_service.py -v
```

## Getting Started

### Step 1: Read the Problem
Start by reading `PROBLEM.md` for complete technical requirements.

### Step 2: Design Your Approach
Before coding, sketch out:
- How will you represent service dependencies?
- How will you calculate deployment order?
- What state needs to be tracked?
- How will cascading rollback work?

### Step 3: Implement Incrementally
Build in phases:
1. Dependency graph parsing
2. Deployment ordering (topological sort)
3. Sequential deployment with validation
4. Rollback coordination
5. State management and memory integration

### Step 4: Use Hints Strategically
- **Stuck on approach?** → Read Hint 1 (conceptual)
- **Need design patterns?** → Read Hint 2 (architectural)
- **Implementation issues?** → Read Hint 3 (code details)

Try to solve as much as you can before you open a hint.

### Step 5: Verify with Tests
Use `test_scenarios.md` to create test cases that verify:
- Correct deployment order
- Validation at each step
- Cascading rollback on failures
- Edge case handling

## Success Criteria

Your solution should:
- Deploy services in correct dependency order
- Validate each service before proceeding to next
- Roll back all services if any service fails
- Handle edge cases (circular dependencies, missing dependencies)
- Maintain deployment state throughout
- Record coordination events in memory
- Flag known-bad version combinations before deploying
- Reuse `ZeroDowntimeDeployer` from Exercises 1-2

## Key Concepts Reinforced

### From Exercise 1 (Canary Deployment)
- Health validation per service
- Threshold checking
- Memory-informed decisions

### From Exercise 2 (Automatic Rollback)
- Rollback logic
- State verification
- Failure escalation

### New Concepts (Challenge)
- Dependency management
- Deployment ordering (graph algorithms)
- Multi-service state tracking
- Coordinated rollback (transaction pattern)
- Partial deployment handling

## Hints Preview

Need help? Three levels of hints available:

**Hint 1**: Conceptual approach and problem decomposition
**Hint 2**: Architectural patterns and design strategies
**Hint 3**: Implementation details and code structure

Each hint shows more detail. Try the problem without hints first.

## Testing Strategy

Create tests for these scenarios:
1. **Happy path**: All services deploy successfully
2. **First service fails**: No rollback needed (nothing deployed yet)
3. **Middle service fails**: Roll back previously deployed services
4. **Last service fails**: Roll back all previous services
5. **Circular dependency**: Detect and reject before deployment
6. **Missing dependency**: Detect and reject before deployment
7. **Known-bad combination**: A version combination that failed before is flagged before any service deploys

See `test_scenarios.md` for detailed test specifications.

## Bonus Challenges (Optional)

After completing the core challenge:

1. **Parallel Deployment**: Deploy independent services simultaneously
2. **Partial Rollback**: Only roll back affected services and dependents
3. **Deployment Versioning**: Track entire multi-service deployment as a unit
4. **Health Check Retries**: Retry validation before declaring failure
5. **Deployment Visualization**: Generate dependency graph diagrams

## Common Pitfalls

- **Not reusing Exercise 1-2 code**: Build on your existing deployer, don't rewrite
- **Wrong rollback order**: Must roll back in reverse of deployment order
- **Forgetting state management**: Leads to confusion about what's deployed
- **Not handling edge cases**: Circular dependencies will break your solution
- **Overcomplicating**: Keep it simple, follow patterns from exercises

## What You'll Practice

- Topological sort for dependencies
- Tracking deployment states
- All-or-nothing deployments
- Coordinating multiple units
- Handling failures across service boundaries

## Next Steps

After completing this challenge:
1. Re-read `APPROACH.md` and compare it against the design you landed on
2. Refactor for clarity and maintainability
3. Improve the error messages: a failed multi-service deploy should say which service failed, what rolled back, and in what order
4. Implement bonus challenges
5. Apply to your own multi-service projects

## Resources

- **Exercise 1**: `exercises/exercise-1-canary.md` - Canary deployment patterns
- **Exercise 2**: `exercises/exercise-2-rollback.md` - Rollback implementation
- **Chapter 11, Section 11.6**: the Zero-Downtime Deployer this challenge extends
- **Chapter 10**: Multi-agent coordination patterns

---

Next, open `PROBLEM.md` for the detailed requirements.

**Tip**: Your code does not need to be perfect. Get each part working, then improve it.
