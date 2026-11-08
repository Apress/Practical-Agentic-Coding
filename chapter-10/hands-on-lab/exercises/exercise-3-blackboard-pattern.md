# Exercise 3: Blackboard Coordination Pattern

**Time**: 60-75 minutes
**Difficulty**: Intermediate to advanced
**Prerequisites**: Exercises 1 and 2 completed

## What you'll do

- Post a task to the shared blackboard and move it through its states
- Claim and release work atomically, so dev hands the task to QA cleanly
- Return the final state with the full task history

## Background

In this exercise, the board is Redis. Agents post to it and read from it
instead of messaging each other. Claims are atomic, so two agents cannot hold
the same task. The task moves through these statuses:

- pending
- claimed
- in_progress
- ready_for_review
- in_review
- complete

When to use the blackboard pattern and why: Chapter 10, Section 10.6.

## The Pattern

```text
Manager Pattern         Peer-to-Peer           Blackboard Pattern
───────────────         ────────────           ──────────────────

    Manager              Dev ←→ QA               BLACKBOARD
       ↕                                        ╔═══════════╗
    Dev ← → QA                                  ║  Tasks    ║
                                                ║  State    ║
                                                ║  History  ║
                                                ╚═══════════╝
                                                  ↑ ↓  ↑ ↓
                                                 Dev  QA  Scrum
                                             [Agents watch and claim]
```

### Blackboard Pattern Flow (Detailed)

```text
┌─────────────────────────────────────────────────────────────────┐
│                  BLACKBOARD COORDINATION FLOW                    │
└─────────────────────────────────────────────────────────────────┘

Phase 1: TASK POSTING
    │
    └─> Coordinator posts task to blackboard
        │
        ├─> Create TaskState(task_id, description, status="pending")
        ├─> await blackboard.post_task(task_state)
        └─> Task now visible to all agents

Phase 2: TASK WATCHING (Concurrent)
    │
    ├─> Dev agent watches for pending tasks
    │   └─> Polls: tasks = await blackboard.get_tasks(status="pending")
    │
    ├─> QA agent watches for "ready_for_review" tasks
    │   └─> Polls: tasks = await blackboard.get_tasks(status="ready_for_review")
    │
    └─> All agents continuously monitor blackboard

Phase 3: DEV CLAIMS TASK
    │
    └─> Dev sees pending task and claims it
        │
        ├─> success = await blackboard.claim_task(task_id, "dev")
        ├─> IF success:
        │   ├─> Task status: pending → claimed
        │   ├─> Task assigned_to: "dev"
        │   └─> Dev starts work
        │
        └─> IF failure (someone else claimed):
            └─> Try another task

Phase 4: DEV UPDATES STATE
    │
    └─> Dev works on implementation
        │
        ├─> status = "in_progress"
        ├─> await blackboard.update_task(
        │       task_id, "dev", status="in_progress"
        │   )
        │
        └─> Task history updated with state change

Phase 5: DEV MARKS READY FOR REVIEW
    │
    └─> Dev completes implementation
        │
        ├─> implementation_result = await dev.implement_feature(task)
        ├─> await blackboard.update_task(
        │       task_id, "dev",
        │       status="ready_for_review",
        │       data={"implementation": implementation_result}
        │   )
        ├─> await blackboard.release_task(task_id, "dev")
        │   └─> Claim cleared; status stays "ready_for_review"
        │
        └─> Task now visible to QA agents and free to claim

Phase 6: QA CLAIMS FOR REVIEW
    │
    └─> QA sees "ready_for_review" task
        │
        ├─> Retrieves task: task = await blackboard.get_task(task_id)
        ├─> Claims for review: await blackboard.claim_task(task_id, "qa")
        │   └─> Succeeds because dev released; status → "claimed"
        ├─> Moves it to review: await blackboard.update_task(
        │       task_id, "qa", status="in_review"
        │   )
        │
        └─> QA starts validation

Phase 7: QA COMPLETES REVIEW
    │
    └─> QA performs testing
        │
        ├─> implementation = task.data["implementation"]
        ├─> qa_result = await qa.test_feature(implementation)
        ├─> await blackboard.update_task(
        │       task_id, "qa",
        │       status="complete",
        │       data={"qa_validation": qa_result}
        │   )
        │
        └─> Task marked complete

Phase 8: RESULT RETRIEVAL
    │
    └─> Coordinator retrieves final state
        │
        ├─> final_task = await blackboard.get_task(task_id)
        ├─> Extract implementation and validation
        ├─> Review complete task history
        └─> Return the full result

Task State Machine:
━━━━━━━━━━━━━━━━━━
pending → claimed → in_progress → ready_for_review → in_review → complete
   ↓                                                                  ↓
 failed ←─────────────────────────────────────────────────────── failed
```

In this lab, the agents run no background loop. Your coordinator performs the
steps "Dev sees the task" and "QA sees the task":

1. After posting, it calls `claim_task()` for dev.
2. After dev releases, it calls `claim_task()` for QA.

## What You'll Build

You implement the `coordinate_task_blackboard_pattern()` method in `starter/swarm_coordinator.py`. The method does these steps:
1. Posts the task to the blackboard
2. Waits for Dev to claim and implement
3. Monitors the state transitions
4. Waits for QA to claim and validate
5. Gets the final state with the full history

## Step 1: Review the Starter Code

Open `starter/swarm_coordinator.py` and locate the `coordinate_task_blackboard_pattern()` method (line 207):

```python
async def coordinate_task_blackboard_pattern(self, task: Task) -> Dict[str, Any]:
    """
    Coordinate using blackboard pattern (shared state).

    TODO (Exercise 3): Implement blackboard coordination
    """
    logger.info(f"Coordinating task {task.id} using BLACKBOARD pattern")

    # TODO: Students implement blackboard pattern coordination here
    raise NotImplementedError(
        "Exercise 3: Implement blackboard pattern coordination."
    )
```

## Step 2: Understand the Blackboard API

The Blackboard has atomic operations for managing shared state:

### TaskState Object
```python
from starter.blackboard import TaskState

# Create task state
task_state = TaskState(
    task_id=task.id,
    description=task.description,
    status="pending",          # Initial status
    assigned_to=None,          # No agent assigned yet
    data={}                    # Additional data
)
```

### Post Task
```python
# Post task to blackboard
success = await self.blackboard.post_task(task_state)

# Task is now visible to all agents
# Status: "pending"
```

### Claim Task (Atomic)
```python
# Agent attempts to claim task
success = await self.blackboard.claim_task(task_id, agent_id="dev")

# Returns True if claimed successfully
# Returns False if already claimed by another agent
# Automatically updates status to "claimed"
```

### Release Task (Atomic)
```python
# Holding agent releases its claim
success = await self.blackboard.release_task(task_id, agent_id="dev")

# Returns True if released
# Returns False if the agent does not hold the claim (or nothing is claimed)
# Clears assigned_to so the next agent can claim
# Status is left unchanged by default; pass status="pending" to reset it too
```

The dev-to-QA handoff works like this:

1. Dev marks the task `ready_for_review`.
2. Dev releases its claim.
3. QA's claim then succeeds.

### Update Task
```python
# Update task status and data
success = await self.blackboard.update_task(
    task_id=task.id,
    agent_id="dev",
    status="in_progress",
    data={"progress": "50%"}
)

# Only assigned agent can update
# Adds entry to task history
```

### Get Task
```python
# Retrieve current task state
task_state = await self.blackboard.get_task(task_id)

# Returns TaskState object with:
# - task_id
# - description
# - status
# - assigned_to
# - data
# - history (list of all state changes)
```

### Query Tasks
```python
# Find tasks by status
pending_tasks = await self.blackboard.get_tasks(status="pending")

# Find tasks by agent
dev_tasks = await self.blackboard.get_tasks(assigned_to="dev")
```

## Step 3: Implementation Strategy (Pseudo-code)

Implement this algorithm:

```text
FUNCTION coordinate_task_blackboard_pattern(task):

    # Initialize tracking
    start_time = current_time()

    # Phase 1: Post Task to Blackboard
    log("Posting task to blackboard")
    task_state = TaskState(
        task_id=task.id,
        description=task.description,
        status="pending"
    )
    await blackboard.post_task(task_state)

    # Phase 2: Dev Claims the Task
    # The agents run no background loop, so the coordinator claims on dev's
    # behalf. Without this call the wait below runs out its timeout.
    log("Dev claiming task")
    IF NOT await blackboard.claim_task(task.id, "dev"):
        return failure_result("Dev could not claim task")

    claimed = await _wait_for_claim(task.id, "dev", timeout=30)

    IF NOT claimed:
        return timeout_result("Dev did not claim task")

    # Phase 3: Update to In Progress
    await blackboard.update_task(task.id, "dev", status="in_progress")

    # Phase 4: Simulate Dev Implementation
    # In real system, Dev would watch blackboard and implement
    # For exercise, we explicitly call Dev
    log("Dev implementing feature")
    implementation = await agents["dev"].implement_feature(task)

    IF implementation["status"] != "implemented":
        await blackboard.update_task(task.id, "dev", status="failed")
        return failure_result(implementation)

    # Phase 5: Dev Marks Ready for Review, Then Releases the Claim
    await blackboard.update_task(
        task.id, "dev",
        status="ready_for_review",
        data={"implementation": implementation}
    )
    # QA cannot claim while dev holds the task, so dev hands it off.
    # The status stays "ready_for_review"; only assigned_to is cleared.
    await blackboard.release_task(task.id, "dev")

    # Phase 6: QA Claims for Review
    # Again the coordinator acts for the agent: QA's claim succeeds only
    # because dev released, and QA then moves the task to in_review.
    log("QA claiming task for review")
    IF await blackboard.claim_task(task.id, "qa"):
        await blackboard.update_task(task.id, "qa", status="in_review")

    in_review = await _wait_for_status_change(
        task.id, "ready_for_review", "in_review", timeout=30
    )

    IF NOT in_review:
        return timeout_result("QA did not claim for review")

    # Phase 7: Simulate QA Review
    log("QA reviewing implementation")
    task_state = await blackboard.get_task(task.id)
    implementation_data = task_state.data["implementation"]
    qa_result = await agents["qa"].test_feature(implementation_data)

    # Phase 8: QA Marks Complete
    await blackboard.update_task(
        task.id, "qa",
        status="complete",
        data={"qa_validation": qa_result}
    )

    # Phase 9: Retrieve Final State
    final_task = await blackboard.get_task(task.id)

    end_time = current_time()
    duration = end_time - start_time

    return {
        "pattern": "blackboard",
        "task_id": task.id,
        "final_state": final_task.to_dict(),
        "task_history": final_task.history,
        "dev_implementation": implementation,
        "qa_validation": qa_result,
        "duration_seconds": duration,
        "success": final_task.status == "complete"
    }


# Helper Function 1: Wait for Claim
FUNCTION _wait_for_claim(task_id, expected_agent, timeout):
    end_time = current_time() + timeout

    WHILE current_time() < end_time:
        task = await blackboard.get_task(task_id)

        IF task.assigned_to == expected_agent AND task.status == "claimed":
            return True

        await asyncio.sleep(1)  # Poll every second

    return False  # Timeout


# Helper Function 2: Wait for Status Change
FUNCTION _wait_for_status_change(task_id, from_status, to_status, timeout):
    end_time = current_time() + timeout

    WHILE current_time() < end_time:
        task = await blackboard.get_task(task_id)

        IF task.status == to_status:
            return True

        await asyncio.sleep(1)  # Poll every second

    return False  # Timeout
```

The starter ships `_wait_for_claim()` and `_wait_for_status_change()` as stubs
that return `None`. Implement them (Hints 2 and 5) before you call them.
Otherwise the `IF NOT claimed` check above returns early on the first wait.

## Progressive Hints

<details>
<summary><b>Hint 1: Posting Task to Blackboard</b> (Click to expand)</summary>

First, create and post a TaskState:

```python
from starter.blackboard import TaskState

# Create task state object
task_state = TaskState(
    task_id=task.id,
    description=task.description,
    status="pending",        # Initial state
    assigned_to=None,        # Not yet assigned
    data={}                  # Will store results later
)

# Post to blackboard
success = await self.blackboard.post_task(task_state)

if not success:
    return {
        "pattern": "blackboard",
        "task_id": task.id,
        "success": False,
        "error": "Failed to post task to blackboard"
    }
```

All agents watching the blackboard can now see the task.
</details>

<details>
<summary><b>Hint 2: Implementing Wait for Claim Helper</b> (Click to expand)</summary>

You need a helper that waits for agents to claim tasks:

```python
async def _wait_for_claim(
    self,
    task_id: str,
    expected_agent: str,
    timeout: int = 30
) -> bool:
    """Wait for task to be claimed by specific agent."""
    from datetime import datetime, timedelta
    import asyncio

    end_time = datetime.now() + timedelta(seconds=timeout)

    while datetime.now() < end_time:
        # Check current task state
        task_state = await self.blackboard.get_task(task_id)

        if not task_state:
            await asyncio.sleep(1)
            continue

        # Check if claimed by expected agent
        if (task_state.assigned_to == expected_agent and
            task_state.status == "claimed"):
            logger.info(f"Task {task_id} claimed by {expected_agent}")
            return True

        # Wait before checking again
        await asyncio.sleep(1)

    logger.warning(f"Timeout waiting for {expected_agent} to claim {task_id}")
    return False
```

This polls the blackboard until the task is claimed or the timeout passes.
</details>

<details>
<summary><b>Hint 3: Simulating Agent Behavior</b> (Click to expand)</summary>

In a real system, agents watch the blackboard on their own. In this exercise, trigger each agent action yourself:

```python
# After posting task, simulate Dev claiming it
dev = self.agents["dev"]

# Dev claims task
claim_success = await self.blackboard.claim_task(task.id, "dev")

if not claim_success:
    return {
        "pattern": "blackboard",
        "task_id": task.id,
        "success": False,
        "error": "Dev failed to claim task"
    }

# Wait briefly for claim to be processed
await asyncio.sleep(0.5)

# Verify claim
claimed = await self._wait_for_claim(task.id, "dev", timeout=5)

if not claimed:
    return {
        "pattern": "blackboard",
        "task_id": task.id,
        "success": False,
        "error": "Claim verification failed"
    }
```

This stands in for agents claiming tasks on their own.
</details>

<details>
<summary><b>Hint 4: Managing State Transitions</b> (Click to expand)</summary>

Update the task state as work moves forward:

```python
# Update to in_progress
await self.blackboard.update_task(
    task_id=task.id,
    agent_id="dev",
    status="in_progress"
)

# Dev does the work
implementation = await dev.implement_feature(task)

# Check if successful
if implementation.get("status") != "implemented":
    # Mark as failed
    await self.blackboard.update_task(
        task_id=task.id,
        agent_id="dev",
        status="failed",
        data={"error": implementation}
    )
    return failure_result(implementation)

# Mark ready for review with implementation data
await self.blackboard.update_task(
    task_id=task.id,
    agent_id="dev",
    status="ready_for_review",
    data={"implementation": implementation}
)
```

The task history records each state transition.
</details>

<details>
<summary><b>Hint 5: Implementing Status Change Watcher</b> (Click to expand)</summary>

Create a helper that waits for status transitions:

```python
async def _wait_for_status_change(
    self,
    task_id: str,
    from_status: str,
    to_status: str,
    timeout: int = 30
) -> bool:
    """Wait for task status to change."""
    from datetime import datetime, timedelta
    import asyncio

    end_time = datetime.now() + timedelta(seconds=timeout)

    while datetime.now() < end_time:
        task_state = await self.blackboard.get_task(task_id)

        if not task_state:
            await asyncio.sleep(1)
            continue

        # Check if status has changed to target
        if task_state.status == to_status:
            logger.info(f"Task {task_id} status changed to {to_status}")
            return True

        await asyncio.sleep(1)

    logger.warning(f"Timeout waiting for status change to {to_status}")
    return False
```

This waits for a specific state transition.
</details>

<details>
<summary><b>Hint 6: QA Review and Completion</b> (Click to expand)</summary>

Handle QA claiming and reviewing:

```python
# Dev is done: release the claim so QA can take the task.
# The "ready_for_review" status set in Hint 4 survives the release.
await self.blackboard.release_task(task.id, "dev")

# Simulate QA claiming for review
qa = self.agents["qa"]

# QA claims (claim_task sets status to "claimed")
claim_success = await self.blackboard.claim_task(task.id, "qa")

if claim_success:
    # QA holds the task; move it to in_review
    await self.blackboard.update_task(
        task_id=task.id,
        agent_id="qa",
        status="in_review"
    )

# Get implementation from blackboard
task_state = await self.blackboard.get_task(task.id)
implementation_data = task_state.data.get("implementation")

# QA performs review
qa_result = await qa.test_feature(implementation_data)

# Mark complete with QA results
await self.blackboard.update_task(
    task_id=task.id,
    agent_id="qa",
    status="complete",
    data={"qa_validation": qa_result}
)
```

QA reads the implementation from the blackboard and writes its results back.

Watch ownership here:

- `claim_task` and `update_task` reject any agent that does not hold the claim.
- Dev still holds the claim after it marks `ready_for_review`.
- The `release_task` call at the top of this hint lets QA's claim succeed on
  real Redis.

The graded unit tests mock the blackboard, so they pass either way. The
integration tests (`test_claim_release_handoff` and the full workflow test)
check the real sequence.
</details>

<details>
<summary><b>Hint 7: Building Final Result with History</b> (Click to expand)</summary>

Get the final state and build the full result:

```python
from datetime import datetime

# Calculate duration
end_time = datetime.now()
duration = (end_time - start_time).total_seconds()

# Get final task state from blackboard
final_task = await self.blackboard.get_task(task.id)

# Extract data
implementation = final_task.data.get("implementation")
qa_validation = final_task.data.get("qa_validation")

# Build result with complete history
result = {
    "pattern": "blackboard",
    "task_id": task.id,
    "final_state": final_task.to_dict(),
    "task_history": final_task.history,
    "state_transitions": [
        entry["action"] for entry in final_task.history
    ],
    "dev_implementation": implementation,
    "qa_validation": qa_validation,
    "duration_seconds": duration,
    "success": final_task.status == "complete"
}

return result
```

The history shows every state change.
</details>

## Common Pitfalls

### Pitfall 1: Race Conditions in Claiming

```python
# Wrong: Not handling claim conflicts
await blackboard.claim_task(task.id, "dev")
# What if another agent claimed first?
```

```python
# Right: Check claim result
claim_success = await blackboard.claim_task(task.id, "dev")

if not claim_success:
    # Task already claimed by another agent
    logger.warning(f"Task {task.id} already claimed")
    # Find another task or handle gracefully
    return handle_claim_failure()
```

**Why it matters**: Several agents might try to claim the same task at the same time.

### Pitfall 2: Waiting for a State Change Nothing Will Make

```python
# Wrong: waiting for QA to pick the task up on its own
await blackboard.update_task(task.id, "dev", status="ready_for_review")
await blackboard.release_task(task.id, "dev")
in_review = await self._wait_for_status_change(
    task.id, "ready_for_review", "in_review", timeout=30
)
# Nothing moves the task to in_review, so this waits 30 seconds and fails
```

```python
# Right: the coordinator makes QA's claim, then waits (or just proceeds)
await blackboard.update_task(task.id, "dev", status="ready_for_review")
await blackboard.release_task(task.id, "dev")

if await blackboard.claim_task(task.id, "qa"):
    await blackboard.update_task(task.id, "qa", status="in_review")

in_review = await self._wait_for_status_change(
    task.id, "ready_for_review", "in_review", timeout=30
)
```

**Why it matters**: The agents here have no loop of their own watching the
board. Every state change comes from a call your coordinator makes. A wait
succeeds only after the call that causes it.

### Pitfall 3: Updating Without Ownership

```python
# Wrong: Agent updating task they don't own
await blackboard.update_task(task.id, "qa", status="in_progress")
# But task is assigned to "dev"!
```

```python
# Right: Only assigned agent updates
task_state = await blackboard.get_task(task.id)

if task_state.assigned_to == "dev":
    await blackboard.update_task(task.id, "dev", status="in_progress")
else:
    logger.error(f"Cannot update task owned by {task_state.assigned_to}")
```

**Why it matters**: The blackboard enforces ownership. Only the assigned agent can update. In the handoff, the same mistake shows up when dev never releases. QA's claim and updates are then rejected. Call `release_task` when you hand work to the next agent.

### Pitfall 4: Infinite Polling Loops

```python
# Wrong: No timeout
while True:
    task = await blackboard.get_task(task.id)
    if task.status == "complete":
        break
    await asyncio.sleep(1)
# Could loop forever if task fails!
```

```python
# Right: Timeout protection
from datetime import datetime, timedelta

end_time = datetime.now() + timedelta(seconds=30)

while datetime.now() < end_time:
    task = await blackboard.get_task(task.id)
    if task.status == "complete":
        break
    await asyncio.sleep(1)
else:
    # Timeout occurred
    return timeout_result()
```

**Why it matters**: A polling loop without a timeout can hang. Give every polling loop a timeout.

### Pitfall 5: Not Retrieving Data from Blackboard

```python
# Wrong: Using stale local variable
implementation = await dev.implement_feature(task)
# ... later ...
qa_result = await qa.test_feature(implementation)
# But implementation might have been updated on blackboard!
```

```python
# Right: Get fresh data from blackboard
implementation = await dev.implement_feature(task)
await blackboard.update_task(
    task.id, "dev", status="ready_for_review",
    data={"implementation": implementation}
)

# ... later ...
task_state = await blackboard.get_task(task.id)
fresh_implementation = task_state.data["implementation"]
qa_result = await qa.test_feature(fresh_implementation)
```

**Why it matters**: The blackboard is the source of truth. Read the current state from it.

## Testing Your Implementation

### Run the Blackboard Pattern Tests

```bash
# Test just the blackboard pattern
pytest starter/tests/test_swarm_coordinator.py::TestBlackboardPattern -v

# Test with detailed output
pytest starter/tests/test_swarm_coordinator.py::TestBlackboardPattern -v -s

# Test the claim release / handoff behavior (runs offline, no Redis needed)
pytest starter/tests/test_swarm_coordinator.py::TestBlackboardClaimRelease -v

# Test all three patterns together
pytest starter/tests/test_swarm_coordinator.py -v
```

To watch the handoff on real Redis, see "Manual verification on real Redis"
under Exercise 3 in the lab README.

### Expected Test Output

Before you implement the method, the two coordination tests report SKIPPED
("Blackboard pattern not yet implemented - this is expected"). When your
implementation is correct, you see the following output. It is shown with
`-o log_cli=false`. Without that flag, live logging puts agent INFO lines
between these lines.

```text
starter/tests/test_swarm_coordinator.py::TestBlackboardPattern::test_blackboard_pattern_initialization PASSED
starter/tests/test_swarm_coordinator.py::TestBlackboardPattern::test_blackboard_pattern_coordination PASSED
starter/tests/test_swarm_coordinator.py::TestBlackboardPattern::test_blackboard_pattern_state_transitions PASSED
3 passed
```

These unit tests mock the blackboard. They check that you posted the task and
called `update_task()`. They do not check that the handoff works. With Redis
up, the integration test `test_full_blackboard_workflow` checks the real
sequence. The task must finish `complete`, with QA holding the claim.

### Debugging Tips

The tests report these failures for the common mistakes:

1. **Dev never releases its claim** (unit tests still pass):
   ```text
   AssertionError: assert 'ready_for_review' == 'complete'
   ```
   That is `test_full_blackboard_workflow` with Redis up. QA's claim and
   updates were rejected while dev held the task. The log shows
   `Task task_001 already claimed by dev` and
   `Agent qa cannot update task assigned to dev`.
   Solution: call `release_task(task.id, "dev")` after `ready_for_review`

2. **Waiting on the helper stubs**: If you follow the pseudo-code while the
   starter's `_wait_for_claim()` is still a stub, the method returns at the
   first wait. Nothing after it runs:
   ```text
   AssertionError: assert False
    +  where False = <AsyncMock id='...'>.called
   ```
   That is `test_blackboard_pattern_state_transitions` (`update_task` never
   ran). The integration test reports `assert 'pending' == 'complete'`.
   Solution: implement the helpers (Hints 2 and 5). Make the claims yourself
   before you wait on them (Hint 3)

3. **Missing data**:
   ```text
   KeyError: 'implementation'
   ```
   Solution: store the result with `update_task(..., data={"implementation": ...})`
   before reading `task_state.data["implementation"]`

## Success Criteria

You've completed Exercise 3 when:

- All blackboard pattern tests pass. The integration tests pass with Redis up
- The task moves through its states and finishes `complete`, held by QA
- Your polling helpers time out instead of looping forever
- The result includes the full task history

When to use the blackboard pattern and why: Chapter 10, Section 10.6. For when
durable shared state fits better than direct messages, see Section 10.3.

## Advanced Topics

### Optimizing Blackboard Performance

The first two items use the API as it exists in `starter/blackboard.py`:

1. **Watch instead of Poll**:
   ```python
   # Instead of polling every second
   queue = await blackboard.watch_status("ready_for_review")
   task = await queue.get()  # Blocks until status appears
   ```

2. **Partial Solutions**:
   ```python
   # Agents contribute incrementally
   await blackboard.update_task(
       task.id, "agent1",
       data={"partial_result": result, "progress": "50%"}
   )
   ```

3. **Priority Queues** (extension): `get_tasks()` only filters by `status` and
   `assigned_to`. To claim high-priority work first, choose one option:
   - Store a priority in `task.data` and sort the returned list yourself.
   - Extend `get_tasks()` in `blackboard.py` with sort parameters.

### Handling Failures

Once a task is claimed, its `assigned_to` changes only through
`release_task()`. Only the holder passes the ownership check in
`update_task()`. This covers the cooperative handoff: dev releases, QA claims.

To recover from a stuck agent, use the same call. A supervisor releases the
task for the holder and resets the status in the same atomic step:

```python
# If the owner has not updated the task within a deadline, release it
if task.updated_at < (now - timeout):
    await blackboard.release_task(task.id, task.assigned_to, status="pending")

# Any agent can then re-claim it
claimed = await blackboard.claim_task(task.id, self.agent_id)
```

## Next Steps

After completing Exercise 3:

1. **Compare all three patterns**: [PATTERN_COMPARISON.md](./PATTERN_COMPARISON.md)
   walks you through measuring your three implementations side by side
2. **Analyze performance**: Find which pattern took longest, and note why.
3. **Review test results**: Look at the coordination logs.
4. **Experiment**: Process several tasks in parallel with the blackboard.
5. **Extend**: Add more agents (e.g., SecurityAgent, DocAgent).

This completes the three coordination exercises:

- centralized coordination (manager)
- direct negotiation (peer-to-peer)
- shared state (blackboard)
