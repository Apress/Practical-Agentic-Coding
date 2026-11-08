# Exercise 1: Manager Pattern Coordination

**Time**: 45-60 minutes
**Difficulty**: Intermediate
**Prerequisites**: Setup complete (run `python verify_setup.py`)

## What you'll do

- Implement centralized coordination with a manager agent
- Route task assignment, progress monitoring, and the QA handoff through it
- Coordinate the developer and QA agents through the Scrum Master

## Background

In this lab, the Scrum Master agent is the manager. Every assignment, progress
check, and handoff goes through it. The Dev and QA agents never message each
other.

When to use hierarchical coordination (the tech lead model) and why: Chapter 10,
Section 10.2.

## The Pattern

```text
Traditional Team                Manager Pattern
────────────────               ─────────────────

   Manager                      Scrum Master
      ↓                              ↓
   Assigns                      assign_task()
      ↓                              ↓
   Developer ─→ QA              Dev ← → QA
   [Direct talk]                [All via manager]
```

### Manager Pattern Flow (Detailed)

```text
┌─────────────────────────────────────────────────────────────────┐
│                   MANAGER PATTERN COORDINATION                   │
└─────────────────────────────────────────────────────────────────┘

Phase 1: TASK ASSIGNMENT
    │
    └─> Scrum Master receives task
        │
        ├─> Analyzes task requirements
        ├─> Selects appropriate agent (Dev)
        └─> await scrum.assign_task(task, "dev")
              │
              └─> Dev receives "task_assignment" message

Phase 2: IMPLEMENTATION
    │
    └─> Dev agent implements feature
        │
        ├─> await dev.implement_feature(task)
        ├─> Returns implementation result
        └─> Dev does NOT directly contact QA

Phase 3: PROGRESS MONITORING
    │
    └─> Scrum Master checks progress
        │
        ├─> await scrum.monitor_progress(task.id)
        ├─> Validates implementation completion
        └─> Decides when ready for QA

Phase 4: HANDOFF COORDINATION
    │
    └─> Scrum Master coordinates Dev → QA handoff
        │
        ├─> await scrum.coordinate_handoff(
        │       task_id, "dev", "qa", context
        │   )
        ├─> QA receives a "task_handoff" message (it only logs it)
        └─> Your coordinator passes the implementation to QA next

Phase 5: QA VALIDATION
    │
    └─> QA agent performs review
        │
        ├─> await qa.test_feature(implementation)
        ├─> Returns validation results
        └─> Results go back to Scrum Master

Phase 6: AGGREGATION
    │
    └─> Scrum Master collects all results
        │
        ├─> Combines Dev implementation
        ├─> Combines QA validation
        ├─> Adds coordination metadata
        └─> Returns the full result
```

## What You'll Build

You implement the `coordinate_task_manager_pattern()` method in `starter/swarm_coordinator.py`. The method does these steps:
1. Uses the Scrum Master as the central coordinator
2. Assigns the task to the Dev agent
3. Monitors implementation progress
4. Coordinates the handoff to the QA agent
5. Collects and returns the combined results

## Step 1: Review the Starter Code

Open `starter/swarm_coordinator.py` and locate the `coordinate_task_manager_pattern()` method (line 118):

```python
async def coordinate_task_manager_pattern(self, task: Task) -> Dict[str, Any]:
    """
    Coordinate using manager pattern (central control).

    TODO (Exercise 1): Implement manager coordination
    """
    logger.info(f"Coordinating task {task.id} using MANAGER pattern")

    # TODO: Students implement manager pattern coordination here
    raise NotImplementedError(
        "Exercise 1: Implement manager pattern coordination."
    )
```

## Step 2: Understand Available Tools

Three agents are already implemented for you:

### Scrum Master Agent (Manager)
```python
# The central coordinator
scrum = self.agents["scrum"]

# Assign task to agent
await scrum.assign_task(task, agent_name="dev")
# Returns: {"task_id": "...", "assigned_to": "dev", "status": "assigned"}

# Monitor progress
await scrum.monitor_progress(task.id)
# Returns: {"task_id": "...", "status": "...", "assigned_to": "...", "blockers": [...]}

# Coordinate handoff between agents
await scrum.coordinate_handoff(task_id, from_agent="dev", to_agent="qa", context={...})
# Returns: {"task_id": "...", "from_agent": "dev", "to_agent": "qa", "status": "handed_off"}
```

### Developer Agent
```python
# Implementation specialist
dev = self.agents["dev"]

# Implement feature
await dev.implement_feature(task)
# Returns: {
#     "task_id": "...",
#     "status": "implemented",
#     "implementation": "detailed implementation description",
#     "agent": "dev",
#     "approach": "...",
#     "complexity": "low|medium|high"
# }
```

### QA Agent
```python
# Quality specialist
qa = self.agents["qa"]

# Test feature implementation
await qa.test_feature(implementation)
# Returns: {
#     "task_id": "...",
#     "status": "tested",
#     "test_plan": "detailed test plan",
#     "test_cases": [...],
#     "coverage": "full",
#     "agent": "qa"
# }
```

## Step 3: Implementation Strategy (Pseudo-code)

Implement this algorithm:

```text
FUNCTION coordinate_task_manager_pattern(task):

    # Initialize tracking
    start_time = current_time()
    coordination_log = []

    # Phase 1: Assignment
    log("Scrum Master assigning task to Dev")
    assignment_result = await scrum.assign_task(task, "dev")
    add_to_log(coordination_log, "assignment", assignment_result)

    # Phase 2: Implementation
    log("Dev implementing feature")
    implementation = await dev.implement_feature(task)
    add_to_log(coordination_log, "implementation", implementation)

    # Verify implementation succeeded
    IF implementation["status"] != "implemented":
        return failure_result(implementation)

    # Phase 3: Monitor Progress
    log("Scrum Master monitoring progress")
    progress = await scrum.monitor_progress(task.id)
    add_to_log(coordination_log, "progress_check", progress)

    # Phase 4: Coordinate Handoff
    log("Scrum Master coordinating handoff to QA")
    handoff_context = {
        "implementation": implementation,
        "complexity": implementation["complexity"],
        "task_description": task.description
    }
    handoff_result = await scrum.coordinate_handoff(
        task.id, "dev", "qa", handoff_context
    )
    add_to_log(coordination_log, "handoff", handoff_result)

    # Phase 5: QA Validation
    log("QA testing feature")
    qa_results = await qa.test_feature(implementation)
    add_to_log(coordination_log, "qa_validation", qa_results)

    # Phase 6: Aggregate Results
    end_time = current_time()
    duration = end_time - start_time

    final_result = {
        "pattern": "manager",
        "task_id": task.id,
        "coordination_log": coordination_log,
        "dev_implementation": implementation,
        "qa_validation": qa_results,
        "duration_seconds": duration,
        "manager": "scrum",
        "success": True
    }

    return final_result
```

## Progressive Hints

<details>
<summary><b>Hint 1: Understanding Agent Roles</b> (Click to expand)</summary>

In the manager pattern:
- **Scrum Master** = Manager (makes all decisions)
- **Dev** = Worker (implements features)
- **QA** = Worker (validates quality)

The workers do not communicate with each other. All communication goes through the Scrum Master.

```python
# Wrong: Workers communicating directly
await dev.collaborate_with_qa(task.id, implementation)

# Right: Manager coordinates everything
await self.agents["scrum"].coordinate_handoff(
    task.id, "dev", "qa", context
)
```
</details>

<details>
<summary><b>Hint 2: Task Assignment</b> (Click to expand)</summary>

Start by having the Scrum Master assign the task to the Dev agent:

```python
# Get the Scrum Master agent
scrum = self.agents["scrum"]

# Assign task to developer
assignment_result = await scrum.assign_task(task, "dev")

# The assignment_result contains:
# {
#     "task_id": task.id,
#     "assigned_to": "dev",
#     "status": "assigned",
#     "agent": "scrum"
# }
```

This sends the Dev agent a message about the assignment.
</details>

<details>
<summary><b>Hint 3: Getting Implementation from Dev</b> (Click to expand)</summary>

After assignment, have the Dev agent implement the feature:

```python
# Get the Dev agent
dev = self.agents["dev"]

# Dev implements the feature
implementation = await dev.implement_feature(task)

# Check if implementation was successful
if implementation.get("status") != "implemented":
    # Handle implementation failure
    return {
        "pattern": "manager",
        "task_id": task.id,
        "success": False,
        "error": "Implementation failed",
        "details": implementation
    }
```

The implementation holds the approach, the complexity, and a detailed description.
</details>

<details>
<summary><b>Hint 4: Progress Monitoring</b> (Click to expand)</summary>

The Scrum Master should monitor progress after implementation:

```python
# Monitor the task progress
progress = await scrum.monitor_progress(task.id)

# Progress includes:
# {
#     "task_id": task.id,
#     "status": "implemented",  # or other status
#     "assigned_to": "dev",
#     "blockers": [],
#     "agent": "scrum"
# }
```

This step checks that the task is ready for the QA handoff.
</details>

<details>
<summary><b>Hint 5: Coordinating Handoff to QA</b> (Click to expand)</summary>

The Scrum Master coordinates the handoff from Dev to QA:

```python
# Prepare context for QA
handoff_context = {
    "implementation": implementation,
    "task_description": task.description,
    "complexity": implementation.get("complexity", "unknown")
}

# Coordinate the handoff
handoff_result = await scrum.coordinate_handoff(
    task_id=task.id,
    from_agent="dev",
    to_agent="qa",
    context=handoff_context
)

# Now QA can perform testing
qa = self.agents["qa"]
qa_results = await qa.test_feature(implementation)
```

The context tells QA what it is testing.
</details>

<details>
<summary><b>Hint 6: Aggregating Results</b> (Click to expand)</summary>

Finally, collect all results into the response:

```python
from datetime import datetime

# Track timing
start_time = datetime.now()
# ... do all the work ...
end_time = datetime.now()
duration = (end_time - start_time).total_seconds()

# Build coordination log
coordination_log = [
    {"phase": "assignment", "agent": "scrum", "result": assignment_result},
    {"phase": "implementation", "agent": "dev", "result": implementation},
    {"phase": "progress_check", "agent": "scrum", "result": progress},
    {"phase": "handoff", "agent": "scrum", "result": handoff_result},
    {"phase": "qa_validation", "agent": "qa", "result": qa_results}
]

# Return final aggregated result
return {
    "pattern": "manager",
    "task_id": task.id,
    "coordination_log": coordination_log,
    "dev_implementation": implementation,
    "qa_validation": qa_results,
    "duration_seconds": duration,
    "manager": "scrum",
    "success": True
}
```

This gives an audit trail of every coordination step.
</details>

## Common Pitfalls

### Pitfall 1: Workers Communicating Directly

```python
# Wrong: Dev directly contacting QA
dev_result = await dev.implement_feature(task)
await dev.collaborate_with_qa(task.id, dev_result)  # Bypasses manager!
```

```python
# Right: Manager coordinates everything
dev_result = await dev.implement_feature(task)
await scrum.coordinate_handoff(task.id, "dev", "qa", {"implementation": dev_result})
qa_result = await qa.test_feature(dev_result)
```

**Why it matters**: In the manager pattern, all coordination goes through the manager.

### Pitfall 2: Not Checking Implementation Status

```python
# Wrong: Assuming implementation always succeeds
implementation = await dev.implement_feature(task)
# Immediately proceed to QA without checking status
qa_results = await qa.test_feature(implementation)
```

```python
# Right: Validate before proceeding
implementation = await dev.implement_feature(task)

if implementation.get("status") != "implemented":
    return {
        "pattern": "manager",
        "task_id": task.id,
        "success": False,
        "error": "Implementation failed",
        "details": implementation
    }

# Now safe to proceed to QA
qa_results = await qa.test_feature(implementation)
```

**Why it matters**: Agents can fail. Check each result before you go to the next phase.

### Pitfall 3: Missing await Keywords

```python
# Wrong: Forgetting await
implementation = dev.implement_feature(task)  # Returns coroutine, doesn't execute!
# implementation is now a coroutine object, not a dict
```

```python
# Right: Using await
implementation = await dev.implement_feature(task)  # Actually executes and waits
# implementation is now a dict with results
```

**Why it matters**: Without `await`, an async function does not run. It only returns a coroutine object.

### Pitfall 4: Incomplete Result Aggregation

```python
# Wrong: Returning only partial information
return {
    "success": True,
    "implementation": implementation
}
# Missing QA results, coordination log, timing, etc.
```

```python
# Right: Complete audit trail
return {
    "pattern": "manager",
    "task_id": task.id,
    "coordination_log": full_log,
    "dev_implementation": implementation,
    "qa_validation": qa_results,
    "duration_seconds": duration,
    "manager": "scrum",
    "success": True
}
```

**Why it matters**: The manager pattern gives you visibility. Return the full result, with every step.

## Testing Your Implementation

### Run the Manager Pattern Tests

```bash
# Test just the manager pattern
pytest starter/tests/test_swarm_coordinator.py::TestManagerPattern -v

# Test with detailed output
pytest starter/tests/test_swarm_coordinator.py::TestManagerPattern -v -s
```

### Expected Test Output

Before you implement the method, the coordination test reports SKIPPED
("Manager pattern not yet implemented - this is expected"). When your
implementation is correct, you see the following output. It is shown with
`-o log_cli=false`. The lab's `pytest.ini` turns on live logging, so agent INFO
lines normally appear between these lines.

```text
starter/tests/test_swarm_coordinator.py::TestManagerPattern::test_manager_pattern_initialization PASSED
starter/tests/test_swarm_coordinator.py::TestManagerPattern::test_manager_pattern_setup PASSED
starter/tests/test_swarm_coordinator.py::TestManagerPattern::test_manager_pattern_coordination PASSED
3 passed
```

The coordination test checks these points:

- Your result carries the `task_id`.
- `assign_task()`, `implement_feature()`, and `test_feature()` each ran once.
- `monitor_progress()` ran.

With Redis up, the integration test `test_full_manager_workflow` also checks
that the Scrum Master sent dev a `task_assignment` message.

### Debugging Tips

If tests fail, check:

1. **Missing await keywords**:
   ```text
   RuntimeWarning: coroutine 'method_name' was never awaited
   ```
   Solution: Add `await` before async function calls

2. **KeyError in results**:
   ```text
   KeyError: 'implementation'
   ```
   Solution: Check that you return all required fields

3. **Agent not found**:
   ```text
   KeyError: 'dev'
   ```
   Solution: Use `self.agents["dev"]` to access agents

4. **Type errors**:
   ```text
   TypeError: object dict can't be used in 'await' expression
   ```
   Solution: Don't await non-async operations

## Success Criteria

You've completed Exercise 1 when:

- All manager pattern tests pass
- The Scrum Master coordinates every interaction
- Dev and QA never communicate directly
- Results include the coordination log and timing

When to choose the hierarchical pattern: Chapter 10, Section 10.2 and Table 10.1.

## Next Steps

After completing Exercise 1:

1. **Review your implementation**: Check that it follows the pattern.
2. **Experiment**: Add more agents to the coordination.
3. **Compare**: Keep this result to compare with peer-to-peer in Exercise 2.
4. **Optimize**: Look for manager decisions you can improve.

---

**Next:** Exercise 2, decentralized coordination, in `exercise-2-peer-pattern.md`.
