# Quick Reference Guide - Chapter 10 Exercises

A one-page reference for the agent, message bus, and blackboard APIs used across all three coordination exercises.

---

## Agent APIs

### Scrum Master Agent (Manager)

```python
scrum = self.agents["scrum"]

# Assign task to specific agent
await scrum.assign_task(task, agent_name="dev")
# Returns: {"task_id": "...", "assigned_to": "dev", "status": "assigned"}

# Monitor task progress
await scrum.monitor_progress(task_id)
# Returns: {"task_id": "...", "status": "...", "assigned_to": "...", "blockers": [...]}

# Coordinate handoff between agents
await scrum.coordinate_handoff(task_id, "dev", "qa", context={...})
# Returns: {"task_id": "...", "from_agent": "dev", "to_agent": "qa", "status": "handed_off"}

# Prioritize tasks
prioritized = await scrum.prioritize_tasks(task_list)
# Returns: List of tasks in priority order

# Resolve blockers
resolution = await scrum.resolve_blockers(blocker_dict)
# Returns: {"task_id": "...", "resolution": "...", "status": "resolved"}
```

### Developer Agent

```python
dev = self.agents["dev"]

# Implement feature
result = await dev.implement_feature(task)
# Returns: {
#     "task_id": "...",
#     "status": "implemented",
#     "implementation": "detailed description",
#     "agent": "dev",
#     "approach": "...",
#     "complexity": "low|medium|high"
# }

# Fix bug
result = await dev.fix_bug(bug_description, context={...})
# Returns: {"bug_description": "...", "status": "fixed", "fix_details": "..."}

# Respond to QA feedback
response = await dev.respond_to_feedback(feedback_dict)
# Returns: String with response to feedback

# Collaborate with QA (peer pattern)
await dev.collaborate_with_qa(task_id, implementation_dict)
# Sends "review_request" message to QA
# Returns: {"status": "collaboration_initiated", "message_sent": "review_request"}

# Get current task
current = dev.get_current_task()
# Returns: task_id string or None

# Get implementation history
history = dev.get_implementation_history()
# Returns: Dict[task_id, implementation_result]
```

### QA Agent

```python
qa = self.agents["qa"]

# Review code
review = await qa.review_code(implementation_dict)
# Returns: {
#     "task_id": "...",
#     "status": "reviewed",
#     "review": "detailed review",
#     "quality_score": 8.5,  # 0-10
#     "approved": True/False,
#     "issues": ["issue1", "issue2"],
#     "agent": "qa"
# }

# Test feature
result = await qa.test_feature(implementation_dict)
# Returns: {
#     "task_id": "...",
#     "status": "tested",
#     "test_plan": "...",
#     "test_cases": [...],
#     "coverage": "full",
#     "agent": "qa"
# }

# Provide feedback
feedback = await qa.provide_feedback(task_id, implementation, issues=[...])
# Returns: {"task_id": "...", "feedback": "...", "issues": [...]}

# Validate quality
validation = await qa.validate_quality(implementation_dict)
# Returns: {
#     "validation": "...",
#     "overall_score": 8.0,
#     "passed": True/False,
#     "dimensions": {...}
# }

# Get review history
history = qa.get_review_history()
# Returns: Dict[task_id, review_result]
```

---

## MessageBus API (Peer-to-Peer Pattern)

### Sending Messages

```python
# Via agent's send_message helper
await agent.send_message(
    to_agent="qa",
    message_type="review_request",
    payload={
        "task_id": task.id,
        "implementation": implementation,
        "from_agent": self.agent_id
    }
)

# Direct MessageBus access
await self.message_bus.publish(
    from_agent="dev",
    to_agent="qa",          # None for broadcast
    message_type="review_request",
    payload={...}
)
```

### Message Structure

```python
class Message:
    from_agent: str         # Sender ID
    to_agent: Optional[str] # Receiver ID (None = broadcast)
    message_type: str       # e.g., "review_request", "qa_feedback"
    payload: Dict[str, Any] # Message data
    timestamp: datetime     # When sent
```

### Message Types in the Starter Code

```python
# Sent by the provided agent methods
"task_assignment"      # Scrum -> Dev, from assign_task()
"task_handoff"         # Scrum -> the receiving agent, from coordinate_handoff()
"review_request"       # Dev -> QA, from collaborate_with_qa()
"qa_feedback"          # QA -> Dev, sent when QA handles a review_request

# Handled in each agent's process_message() (anything else is logged and ignored)
# DevAgent:   "task_assignment", "qa_feedback", "review_complete"
# QAAgent:    "review_request", "test_request", "dev_response"
# ScrumAgent: "task_complete", "blocker_reported", "progress_update", "help_request"
```

`QAAgent` has no handler for `task_handoff`. The handoff message is only
logged. Your coordinator still passes the implementation to QA itself.

A `review_request` triggers QA's handler. The handler runs its own
`review_code()` and sends `qa_feedback` back to dev. With a real API key, these
are extra model calls on top of the ones your coordinator makes.

### Receiving Messages

```python
# Agents automatically receive messages via process_message()
# Already implemented in BaseAgent

async def process_message(self, message: Message):
    """Override to handle messages"""
    if message.message_type == "review_request":
        await self._handle_review_request(message)
```

### Message History

```python
# Get messages sent by agent
messages = await self.message_bus.get_message_history(
    agent_id="dev",
    limit=10
)

# Returns a list of Message objects, newest first
```

---

## Blackboard API (Blackboard Pattern)

### TaskState Object

```python
from starter.blackboard import TaskState

# Create task state
task_state = TaskState(
    task_id="task-123",
    description="Implement login feature",
    status="pending",           # pending, claimed, in_progress, ready_for_review, in_review, complete, failed
    assigned_to=None,            # Agent ID or None
    data={},                     # Additional data
    created_at=datetime.now(),
    updated_at=datetime.now()
)

# Convert to/from dict
task_dict = task_state.to_dict()
task_state = TaskState.from_dict(task_dict)

# Add history entry
task_state.add_history_entry(
    action="claimed",
    agent_id="dev",
    details={"reason": "..."}
)
```

### Post Task

```python
# Post new task to blackboard
success = await self.blackboard.post_task(task_state)
# Returns: True if successful

# Task is now visible to all agents
```

### Claim Task (Atomic)

```python
# Agent attempts to claim task
success = await self.blackboard.claim_task(task_id, agent_id="dev")
# Returns: True if claimed successfully, False if already claimed

# Automatically:
# - Updates status to "claimed"
# - Sets assigned_to = agent_id
# - Adds history entry
```

### Release Task (Atomic)

```python
# Holding agent releases its claim (the dev-to-QA handoff)
success = await self.blackboard.release_task(task_id, agent_id="dev")
# Returns: True if released, False if the agent does not hold the claim

# Automatically:
# - Clears assigned_to so the next agent can claim
# - Keeps the current status (pass status="pending" to reset it too)
# - Adds history entry
```

### Update Task

```python
# Update task status and/or data
success = await self.blackboard.update_task(
    task_id="task-123",
    agent_id="dev",           # Must be assigned agent
    status="in_progress",     # New status (optional)
    data={"progress": "50%"}  # Additional data (optional)
)
# Returns: True if successful

# Only assigned agent can update
# Adds history entry automatically
```

### Get Task

```python
# Retrieve current task state
task_state = await self.blackboard.get_task(task_id)
# Returns: TaskState object or None

# Access properties:
task_state.task_id
task_state.description
task_state.status
task_state.assigned_to
task_state.data
task_state.history          # List of all state changes
task_state.created_at
task_state.updated_at
```

### Query Tasks

```python
# Find tasks by status
pending = await self.blackboard.get_tasks(status="pending")

# Find tasks by agent
dev_tasks = await self.blackboard.get_tasks(assigned_to="dev")

# All tasks (limited)
all_tasks = await self.blackboard.get_tasks(limit=100)

# Returns: List[TaskState]
```

### Watch for Changes

```python
# Watch for tasks with specific status
queue = await self.blackboard.watch_status("ready_for_review")

# Wait for task (blocking)
task = await queue.get()
# Returns: TaskState when a task reaches that status. The watch lives in
# memory, so only changes made through this same Blackboard object notify it.
```

### Statistics

```python
# Get blackboard statistics
stats = await self.blackboard.get_statistics()
# Returns: {
#     "total_tasks": 10,
#     "by_status": {"pending": 2, "in_progress": 3, "complete": 5},
#     "by_agent": {"dev": 5, "qa": 3}
# }
```

### Task Status Flow

```text
pending → claimed → in_progress → ready_for_review → in_review → complete
   ↓                                                                  ↓
 failed ←──────────────────────────────────────────────────────── failed
```

---

## Common Patterns

### Pattern 1: Manager Coordination

```python
# Scrum Master assigns to Dev
await scrum.assign_task(task, "dev")

# Dev implements
result = await dev.implement_feature(task)

# Scrum Master monitors
progress = await scrum.monitor_progress(task.id)

# Scrum Master coordinates handoff
await scrum.coordinate_handoff(task.id, "dev", "qa", context)

# QA validates
qa_result = await qa.test_feature(result)

# All communication via manager
```

### Pattern 2: Peer-to-Peer Negotiation

```python
# Dev implements
implementation = await dev.implement_feature(task)

# Dev requests review directly
await dev.collaborate_with_qa(task.id, implementation)

# Wait for message propagation
await asyncio.sleep(1)

# QA reviews
qa_review = await qa.review_code(implementation)

# Negotiation loop
while not qa_review["approved"] and rounds < max_rounds:
    feedback = qa_review
    dev_response = await dev.respond_to_feedback(feedback)
    qa_review = await qa.review_code(implementation)
    rounds += 1
```

### Pattern 3: Blackboard Coordination

```python
# Post task
task_state = TaskState(task.id, task.description, status="pending")
await blackboard.post_task(task_state)

# Dev claims (the coordinator acts for the agent; nothing claims on its own)
claimed = await blackboard.claim_task(task.id, "dev")

# Dev updates to in_progress
await blackboard.update_task(task.id, "dev", status="in_progress")

# Dev implements
result = await dev.implement_feature(task)

# Dev marks ready for review with data
await blackboard.update_task(
    task.id, "dev",
    status="ready_for_review",
    data={"implementation": result}
)

# Dev releases its claim so QA's claim can succeed
await blackboard.release_task(task.id, "dev")

# QA claims (succeeds because dev released) and starts the review
if await blackboard.claim_task(task.id, "qa"):
    await blackboard.update_task(task.id, "qa", status="in_review")

# QA reviews
task_state = await blackboard.get_task(task.id)
impl = task_state.data["implementation"]
qa_result = await qa.test_feature(impl)

# QA marks complete
await blackboard.update_task(
    task.id, "qa",
    status="complete",
    data={"qa_validation": qa_result}
)
```

---

## Async/Await Patterns

### Calling Async Functions

```python
# Wrong: missing await
result = async_function()  # Returns coroutine, doesn't execute

# Right: using await
result = await async_function()  # Executes and returns result
```

### Async Sleep

```python
# Wrong: blocking sleep
import time
time.sleep(1)  # Blocks entire event loop!

# Right: non-blocking sleep
import asyncio
await asyncio.sleep(1)  # Yields control to event loop
```

### Error Handling

```python
try:
    result = await risky_operation()

    if not result["success"]:
        # Handle operation failure
        logger.error(f"Operation failed: {result}")
        return failure_result(result)

except Exception as e:
    # Handle exceptions
    logger.error(f"Exception: {e}")
    return {"success": False, "error": str(e)}
```

---

## Helper Functions

### Wait for Claim

```python
async def _wait_for_claim(
    self, task_id: str, expected_agent: str, timeout: int = 30
) -> bool:
    """Wait for task to be claimed by specific agent."""
    from datetime import datetime, timedelta
    import asyncio

    end_time = datetime.now() + timedelta(seconds=timeout)

    while datetime.now() < end_time:
        task = await self.blackboard.get_task(task_id)

        if task and task.assigned_to == expected_agent:
            return True

        await asyncio.sleep(1)

    return False  # Timeout
```

### Wait for Status Change

```python
async def _wait_for_status_change(
    self, task_id: str, from_status: str, to_status: str, timeout: int = 30
) -> bool:
    """Wait for task status to change."""
    from datetime import datetime, timedelta
    import asyncio

    end_time = datetime.now() + timedelta(seconds=timeout)

    while datetime.now() < end_time:
        task = await self.blackboard.get_task(task_id)

        if task and task.status == to_status:
            return True

        await asyncio.sleep(1)

    return False  # Timeout
```

---

## Result Structures

### Manager Pattern Result

```python
{
    "pattern": "manager",
    "task_id": "task-123",
    "coordination_log": [
        {"phase": "assignment", "agent": "scrum", "result": {...}},
        {"phase": "implementation", "agent": "dev", "result": {...}},
        {"phase": "handoff", "agent": "scrum", "result": {...}},
        {"phase": "qa_validation", "agent": "qa", "result": {...}}
    ],
    "dev_implementation": {...},
    "qa_validation": {...},
    "duration_seconds": 45.2,
    "manager": "scrum",
    "success": True
}
```

### Peer-to-Peer Pattern Result

```python
{
    "pattern": "peer_to_peer",
    "task_id": "task-123",
    "negotiation_history": [
        {"phase": "implementation", "agent": "dev", "result": {...}},
        {"phase": "initial_review", "agent": "qa", "result": {...}},
        {"phase": "dev_response_round_1", "agent": "dev", "result": {...}},
        {"phase": "qa_review_round_1", "agent": "qa", "result": {...}}
    ],
    "negotiation_rounds": 1,
    "final_status": "approved",
    "reason": "Approved after 1 negotiation round",
    "final_qa_review": {...},
    "dev_implementation": {...},
    "duration_seconds": 38.7,
    "success": True,
    "max_rounds_allowed": 3
}
```

### Blackboard Pattern Result

```python
{
    "pattern": "blackboard",
    "task_id": "task-123",
    "final_state": {
        "task_id": "task-123",
        "description": "...",
        "status": "complete",
        "assigned_to": "qa",
        "data": {
            "implementation": {...},
            "qa_validation": {...}
        },
        "history": [
            {"timestamp": "...", "action": "posted", "agent_id": "system"},
            {"timestamp": "...", "action": "claimed", "agent_id": "dev"},
            {"timestamp": "...", "action": "updated", "agent_id": "dev"},   # in_progress
            {"timestamp": "...", "action": "updated", "agent_id": "dev"},   # ready_for_review
            {"timestamp": "...", "action": "released", "agent_id": "dev"},
            {"timestamp": "...", "action": "claimed", "agent_id": "qa"},
            {"timestamp": "...", "action": "updated", "agent_id": "qa"},    # in_review
            {"timestamp": "...", "action": "updated", "agent_id": "qa"}     # complete
        ]
    },
    "task_history": [...],  # Same as final_state.history
    "state_transitions": ["posted", "claimed", "updated", "updated",
                          "released", "claimed", "updated", "updated"],
    "dev_implementation": {...},
    "qa_validation": {...},
    "duration_seconds": 52.1,
    "success": True
}
```

---

## Testing Commands

### Run Specific Pattern Tests

```bash
# Exercise 1: Manager Pattern
pytest starter/tests/test_swarm_coordinator.py::TestManagerPattern -v

# Exercise 2: Peer-to-Peer Pattern
pytest starter/tests/test_swarm_coordinator.py::TestPeerPattern -v

# Exercise 3: Blackboard Pattern
pytest starter/tests/test_swarm_coordinator.py::TestBlackboardPattern -v
```

### Run All Tests

```bash
# All swarm coordinator tests
pytest starter/tests/test_swarm_coordinator.py -v

# All tests including integration
pytest starter/tests/ -v
```

### Run with Debug Output

```bash
pytest starter/tests/test_swarm_coordinator.py::TestManagerPattern -v -s
```

---

## Debugging Checklist

### Async Issues
- [ ] Did I `await` all async function calls?
- [ ] Am I using `asyncio.sleep()` not `time.sleep()`?
- [ ] Is my function defined as `async def`?

### Agent Communication Issues
- [ ] Did I allow time for message propagation (`await asyncio.sleep(1)`)?
- [ ] Are agents subscribed to MessageBus (done in `setup()`)?
- [ ] Am I checking message types correctly?

### Blackboard Issues
- [ ] Did I check if `claim_task()` succeeded?
- [ ] Am I using the assigned agent's ID in `update_task()`?
- [ ] Did I retrieve fresh data from blackboard (not using stale local vars)?
- [ ] Do my polling loops have timeout limits?

### Logic Issues
- [ ] Am I checking operation results before proceeding?
- [ ] Do I handle both success and failure cases?
- [ ] Are my while loops properly bounded?
- [ ] Am I returning all required fields in results?

---

## Common Error Messages

### `RuntimeWarning: coroutine was never awaited`
**Problem**: Missing `await` keyword
**Fix**: Add `await` before async function call

### `KeyError: 'implementation'`
**Problem**: Missing required field in result dictionary
**Fix**: Ensure all required fields are included in return value

### `TypeError: object dict can't be used in 'await' expression`
**Problem**: Awaiting a non-async operation
**Fix**: Remove `await` from non-async operations

### `Agent qa cannot update task assigned to dev`
**Problem**: The blackboard logs this warning when an agent that does not hold
the claim tries to update the task. `update_task()` then returns `False`.
**Fix**: Release the claim first (`release_task(task.id, "dev")`). Then claim as
the next agent. Check `task.assigned_to`.

### The test run hangs with no result
**Problem**: An infinite loop. Usually a negotiation or polling loop has no cap.
The lab installs no test timeout, so pytest waits forever.
**Fix**: Press Ctrl+C. Then add a round cap or a deadline to every while loop.

---

When to use each pattern and why: Chapter 10, Sections 10.2, 10.3, and 10.6.
