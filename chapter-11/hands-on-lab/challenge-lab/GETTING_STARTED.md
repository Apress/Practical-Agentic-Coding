# Getting Started with the Challenge Lab

This guide shows how to start the Multi-Service Deployment Orchestration challenge.

## Prerequisites

Before starting this challenge, ensure you have:

### Completed Exercises
- [x] Exercise 1: Canary Deployment (`exercises/exercise-1-canary.md`)
- [x] Exercise 2: Automatic Rollback (`exercises/exercise-2-rollback.md`)

### Working Code
- [x] `ZeroDowntimeDeployer` with implemented `validate_canary()` method
- [x] `ZeroDowntimeDeployer` with implemented `rollback()` method
- [x] All tests passing for Exercises 1 & 2

### Environment Setup
- [x] Python virtual environment activated
- [x] Dependencies installed (`pip install -r requirements.txt`)
- [x] Mock infrastructure working (`USE_MOCK_INFRASTRUCTURE=true`)
- [x] Setup verified (`python verify_setup.py` passes)

## Challenge Overview

**Goal**: Build a `MultiServiceDeployer`. It deploys several interdependent microservices and rolls them back together on failure.

**Time**: 2-3 hours

**Difficulty**: Advanced

**Key Concepts**:
- Dependency graph algorithms (topological sort)
- Multi-service state tracking
- Coordinated rollback orchestration
- Transaction pattern (all-or-nothing deployment)

## File Structure

```text
challenge-lab/
├── README.md                 # Overview and introduction (START HERE)
├── GETTING_STARTED.md        # This file
├── PROBLEM.md                # Detailed technical requirements
├── HINTS.md                  # Progressive hints (3 levels)
├── APPROACH.md               # High-level solution strategy
├── test_scenarios.md         # Test cases to verify solution
├── INSTRUCTOR_NOTES.md       # Teaching notes for running this as a session
└── .challenge-index.md       # Reading order and time estimates
```

Everything here is documentation. You write the implementation and the tests.

## Recommended Workflow

### Step 1: Understand the Problem (30 minutes)

1. **Read README.md** (5 minutes)
   - Understand the challenge overview
   - Review learning objectives
   - Check prerequisites

2. **Read PROBLEM.md** (25 minutes)
   - Study technical requirements
   - Review input/output specifications
   - Understand edge cases
   - Review API design

**Checkpoint**: Can you explain the problem in your own words?

### Step 2: Design Your Solution (30 minutes)

1. **Sketch dependency graph** (10 minutes)
   ```text
   Database (no deps)
       ↓
   API (depends on database)
       ↓
   Frontend (depends on API)
   ```

2. **Design state machine** (10 minutes)
   - What states do you need?
   - What are the transitions?
   - How do you track progress?

3. **Plan algorithm** (10 minutes)
   - How will you calculate deployment order?
   - How will you handle failures?
   - How will you coordinate rollback?

**Checkpoint**: Have you sketched out your approach on paper?

### Step 3: Implement Incrementally (1.5-2 hours)

#### Phase 1: Dependency Graph (30 minutes)
```python
# Start here
def _build_dependency_graph(self, services):
    # TODO: Build adjacency list
    pass

def _calculate_deployment_order(self, services):
    # TODO: Topological sort
    pass
```

**Test**: Can you correctly order [database, api, frontend]?

#### Phase 2: Sequential Deployment (45 minutes)
```python
async def deploy_all(self, services):
    # TODO: Calculate order
    # TODO: Deploy each service sequentially
    # TODO: Track state
    pass
```

**Test**: Can you deploy all services when everything succeeds?

#### Phase 3: Failure Handling (30 minutes)
```python
async def _rollback_all_deployed(self, deployed_services, reason):
    # TODO: Rollback in reverse order
    # TODO: Handle rollback failures
    pass
```

**Test**: Does rollback happen when a service fails?

#### Phase 4: Edge Cases (15 minutes)
- Circular dependency detection
- Missing dependency validation
- Empty input handling

**Test**: Do edge cases raise appropriate errors?

### Step 4: Test and Refine (30-45 minutes)

1. **Run test scenarios** from `test_scenarios.md`
   - Scenario 1: Happy path
   - Scenario 3: Middle service fails
   - Scenario 5: Circular dependency
   - All 11 scenarios

2. **Verify rollback order**
   - Ensure reverse order
   - Check state tracking
   - Verify memory integration

3. **Refine and improve**
   - Add better error messages
   - Improve logging
   - Clean up code

**Checkpoint**: Do all test scenarios pass?

## When to Use Hints

### Use Hint 1 (Conceptual) If:
- You don't know where to start
- You're unclear on the overall approach
- You need problem decomposition help

### Use Hint 2 (Architectural) If:
- You have an approach but need design patterns
- You're stuck on architecture decisions
- You need algorithm guidance

### Use Hint 3 (Implementation) If:
- Your design is clear but implementation is stuck
- You need code structure examples
- You want to verify your approach

**Important**: Try to solve as much as you can before you open a hint.

## Common Stumbling Blocks

### Block 1: "I don't know how to do topological sort"
**Solution**: Read Hint 2 for algorithm explanation, or search "Kahn's algorithm Python"

### Block 2: "My rollback order is wrong"
**Solution**: Roll back in REVERSE deployment order. The last service deployed is the first rolled back.

### Block 3: "I'm tracking state wrong"
**Solution**: Create explicit state object. Track: pending, deploying, deployed, failed.

### Block 4: "Tests are failing"
**Solution**: Add print statements. Log state changes. Verify deployment order matches expected.

### Block 5: "I'm rewriting deployment logic"
**Solution**: Stop. Reuse `ZeroDowntimeDeployer.deploy()` from Exercise 1. Do not reimplement it.

## Where to Create Your Code

Either layout works. Your code must import the deployer you already built. So
run pytest from `hands-on-lab/`.

### Option 1: In the challenge-lab directory (simplest)
```text
challenge-lab/
├── multi_service_deployer.py   # Your implementation
└── test_multi_service.py       # Your tests
```
```python
from starter.deployer import ZeroDowntimeDeployer
from multi_service_deployer import MultiServiceDeployer
```
```bash
cd chapter-11/hands-on-lab
python -m pytest challenge-lab/test_multi_service.py -v
```

Use `python -m pytest`, not bare `pytest`. The `-m` form puts the current
directory on the import path. The `starter.` import needs that.

### Option 2: Alongside the starter package
```text
starter/
├── deployer.py                 # Your Exercise 1-2 code
├── multi_service_deployer.py   # Your challenge code
└── tests/test_multi_service.py
```
```python
from .deployer import ZeroDowntimeDeployer
```
```bash
pytest starter/tests/test_multi_service.py -v
```

- Option 2 gives you relative imports and the existing test fixtures.
- Option 1 keeps your challenge work separate from the graded exercises.

## Success Metrics

You've successfully completed the challenge when:

- All 11 test scenarios pass
- Rollback happens in correct (reverse) order
- Circular dependencies detected before deployment
- Missing dependencies reported clearly
- Code reuses Exercise 1-2 deployer
- State tracking is accurate
- You understand the patterns

## What You'll Practice

1. **Graph Algorithms**: Topological sort
2. **State Machines**: State transitions
3. **Coordination**: Running several units in order
4. **All-or-Nothing Operations**: Full rollback on failure
5. **Error Propagation**: Failures across boundaries

## Getting Help

### Resources Available
1. **PROBLEM.md** - Detailed requirements
2. **HINTS.md** - Progressive hints (use strategically)
3. **APPROACH.md** - High-level strategy
4. **test_scenarios.md** - Verification tests

### Debugging Strategy
1. Add print statements for state changes
2. Log deployment order before deploying
3. Test graph algorithm separately
4. Start with 2 services before 3
5. Verify each phase works before moving on

### If Really Stuck
1. Review Exercise 1-2 code (build on it)
2. Read APPROACH.md (high-level strategy)
3. Use Hint 1 (conceptual approach)
4. Draw diagrams on paper
5. Break problem into smaller pieces

## Time Management

Suggested schedule for 2-3 hour challenge:

- **00:00-00:30**: Read and understand problem
- **00:30-00:45**: Design approach
- **00:45-01:15**: Implement graph algorithms
- **01:15-02:00**: Implement deployment loop
- **02:00-02:30**: Implement rollback coordination
- **02:30-03:00**: Test and refine

Adjust the schedule to your pace.

## After Completion

Once you finish the core challenge:

1. **Compare your design against `APPROACH.md`** (there is no reference solution for this challenge)
2. **Refactor for clarity**
3. **Add logging at each state change**
4. **Try bonus challenges**:
   - Parallel deployment of independent services
   - Partial rollback (only affected services)
   - Health check retries
   - Deployment visualization

5. **Reflect on learning**:
   - What was most challenging?
   - What patterns did you learn?
   - Where else can you apply these patterns?

## Quick Start Commands

Work from `hands-on-lab/`, not from inside `challenge-lab/`. Your code imports
the deployer you built in `starter/` (or `complete/`). Those imports only
resolve from the parent directory.

```bash
cd chapter-11/hands-on-lab

# Read the overview and the requirements
cat challenge-lab/README.md
cat challenge-lab/PROBLEM.md

# Create your files
touch challenge-lab/multi_service_deployer.py
touch challenge-lab/test_multi_service.py

# Run your tests as you go (python -m puts the current directory on the
# import path, which the starter. imports need)
python -m pytest challenge-lab/test_multi_service.py -v

# One scenario at a time
python -m pytest challenge-lab/test_multi_service.py -v -k rollback
```

Nothing in `challenge-lab/` is importable as a package yet. Choose one:

- Add an `__init__.py` there if you want `from challenge_lab...` imports.
- Import by module name from the `hands-on-lab` directory.

## Final Tips

1. **Take your time**: Make sure you understand each step
2. **Test incrementally**: Test each phase before moving on
3. **Use hints wisely**: Try solving first, then check hints
4. **Draw diagrams**: Visualize the dependency graph and state machine
5. **Reuse code**: Build on Exercises 1-2, don't rewrite
6. **Ask for help**: Stuck for 30+ minutes? Check hints or ask for help

---

Next, open `PROBLEM.md` to read the detailed requirements.

**Tip**: Your code does not need to be perfect. Make sure you can explain how it works.
