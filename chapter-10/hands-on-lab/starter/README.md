# Starter code overview

Starter code for the bonus SDK lab. Most components are already implemented.
Your task is to complete the three coordination methods in `swarm_coordinator.py`.

Run every command below from `hands-on-lab/`, the parent directory. From there,
`starter` imports resolve and pytest finds `pytest.ini`.

## File Status

### Ready to Use (Fully Implemented)

These files are complete. Do not change them:

- **`base_agent.py`**: Abstract base class for all agents. It handles message passing, blackboard access, and Claude API calls
- **`dev_agent.py`**: Developer agent that implements features, fixes bugs, and responds to feedback
- **`qa_agent.py`**: QA agent that reviews code, tests features, and provides feedback
- **`scrum_agent.py`**: Scrum Master agent that coordinates, prioritizes, and resolves blockers
- **`message_bus.py`**: Redis-based pub/sub messaging system for agent communication
- **`blackboard.py`**: Shared state store for blackboard pattern coordination
- **`config.py`**: Configuration management with Pydantic settings

### Your Implementation (TODOs)

Complete these methods in **`swarm_coordinator.py`**:

1. **`coordinate_task_manager_pattern()`** - Exercise 1
2. **`coordinate_task_peer_pattern()`** - Exercise 2
3. **`coordinate_task_blackboard_pattern()`** - Exercise 3

Optional helper methods you may implement:
- `_wait_for_claim()`
- `_wait_for_status_change()`

## Architecture Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                    SwarmCoordinator                         │
│  (Your Implementation: Coordination Pattern Logic)          │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  DevAgent    │    │   QAAgent    │    │ ScrumAgent   │
│ (Complete)   │    │  (Complete)  │    │  (Complete)  │
└──────────────┘    └──────────────┘    └──────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────────┐              ┌──────────────────┐
│   MessageBus     │              │   Blackboard     │
│   (Complete)     │              │   (Complete)     │
│                  │              │                  │
│  Redis Pub/Sub   │              │  Redis Storage   │
└──────────────────┘              └──────────────────┘
```

## Agent Capabilities

### DevAgent (Developer)

**Methods you'll use:**
```python
# Implement a feature
result = await dev_agent.implement_feature(task)

# Fix a bug
fix = await dev_agent.fix_bug(bug_description, context)

# Respond to feedback
response = await dev_agent.respond_to_feedback(feedback)

# Collaborate with QA (peer pattern)
await dev_agent.collaborate_with_qa(task_id, implementation)
```

**What it does:**
- Calls the Claude API to generate implementation approaches
- Returns detailed technical responses
- Keeps an implementation history
- Responds to feedback

### QAAgent (Quality Assurance)

**Methods you'll use:**
```python
# Review code
review = await qa_agent.review_code(implementation)

# Test feature
test_result = await qa_agent.test_feature(implementation)

# Provide feedback
feedback = await qa_agent.provide_feedback(task_id, implementation, issues)

# Validate quality
validation = await qa_agent.validate_quality(implementation)
```

**What it does:**
- Reviews implementations for quality and correctness
- Generates test plans and test cases
- Gives feedback with quality scores
- Approves or rejects work against a quality threshold

### ScrumAgent (Scrum Master)

**Methods you'll use:**
```python
# Prioritize tasks
prioritized = await scrum_agent.prioritize_tasks(tasks)

# Assign task
assignment = await scrum_agent.assign_task(task, agent_name="dev")

# Monitor progress
progress = await scrum_agent.monitor_progress(task_id)

# Coordinate handoff
handoff = await scrum_agent.coordinate_handoff(task_id, "dev", "qa", context)

# Resolve blockers
resolution = await scrum_agent.resolve_blockers(blocker)
```

**What it does:**
- Coordinates the team workflow
- Decides assignments
- Tracks progress across agents
- Resolves blockers

## Infrastructure Components

### MessageBus (Redis Pub/Sub)

**Methods you'll use:**
```python
# Publish message
await message_bus.publish(from_agent, to_agent, message_type, payload)

# Subscribe to messages
await message_bus.subscribe(agent_id, callback)

# Get message history
history = await message_bus.get_message_history(agent_id)
```

**Channels:**
- `agent:{agent_id}` - Direct messages to specific agent
- `agent:broadcast` - Broadcast messages to all agents

### Blackboard (Shared State)

**Methods you'll use:**
```python
# Post task
await blackboard.post_task(task_state)

# Claim task
success = await blackboard.claim_task(task_id, agent_id)

# Release task (handoff: only the holder can release)
success = await blackboard.release_task(task_id, agent_id)

# Update task
await blackboard.update_task(task_id, agent_id, status="in_progress", data={})

# Get task
task_state = await blackboard.get_task(task_id)

# Query tasks
tasks = await blackboard.get_tasks(status="pending")

# Watch for changes
queue = await blackboard.watch_status("ready_for_review")
```

**Task statuses:**
- `pending` - Newly posted, awaiting claim
- `claimed` - Claimed by agent
- `in_progress` - Work in progress
- `ready_for_review` - Implementation done, awaiting review
- `in_review` - Review in progress
- `complete` - Completed
- `failed` - Failed

## Implementation Guidelines

### Exercise 1: Manager Pattern

**What your method must do:**
- The Scrum agent makes all decisions
- All communication goes through the manager
- The hierarchy is Manager → Dev/QA
- The manager tracks all work

**Pseudocode:**
```python
async def coordinate_task_manager_pattern(self, task):
    # 1. Scrum assigns to dev
    await self.agents["scrum"].assign_task(task, "dev")

    # 2. Dev implements
    implementation = await self.agents["dev"].implement_feature(task)

    # 3. Scrum monitors
    progress = await self.agents["scrum"].monitor_progress(task.id)

    # 4. Scrum coordinates handoff to QA
    await self.agents["scrum"].coordinate_handoff(...)

    # 5. QA validates
    validation = await self.agents["qa"].test_feature(implementation)

    # 6. Return aggregated result
    return {
        "pattern": "manager",
        "task_id": task.id,
        "implementation": implementation,
        "validation": validation,
        "coordinator": "scrum"
    }
```

### Exercise 2: Peer-to-Peer Pattern

**What your method must do:**
- Use no central coordinator
- Send messages directly from agent to agent
- Negotiate until the agents agree

**Pseudocode:**
```python
async def coordinate_task_peer_pattern(self, task):
    # 1. Dev starts work
    implementation = await self.agents["dev"].implement_feature(task)

    # 2. Dev contacts QA directly
    await self.agents["dev"].collaborate_with_qa(task.id, implementation)

    # 3. QA reviews and responds
    review = await self.agents["qa"].review_code(implementation)

    # 4. Negotiation loop (if issues found)
    max_iterations = 3
    for i in range(max_iterations):
        if review.get("approved"):
            break
        # Dev addresses feedback
        response = await self.agents["dev"].respond_to_feedback(review)
        # QA re-reviews
        review = await self.agents["qa"].review_code(updated_implementation)

    # 5. Return with negotiation history
    return {
        "pattern": "peer_to_peer",
        "task_id": task.id,
        "implementation": implementation,
        "final_review": review,
        "iterations": i + 1
    }
```

### Exercise 3: Blackboard Pattern

**What your method must do:**
- Coordinate through shared state
- Claim tasks on the board
- Move the task through its statuses
- Keep the full history

**Pseudocode:**
```python
async def coordinate_task_blackboard_pattern(self, task):
    # 1. Post to blackboard
    task_state = TaskState(task.id, task.description)
    await self.blackboard.post_task(task_state)

    # 2. Dev claims the task. The agents have no background loop, so the
    #    coordinator makes the claim on dev's behalf and checks the result.
    claimed = await self.blackboard.claim_task(task.id, "dev")

    # 3. Dev implements, updates blackboard, and releases its claim
    implementation = await self.agents["dev"].implement_feature(task)
    await self.blackboard.update_task(
        task.id, "dev",
        status="ready_for_review",
        data={"implementation": implementation}
    )
    await self.blackboard.release_task(task.id, "dev")

    # 4. QA claims; this succeeds only because dev released
    await self.blackboard.claim_task(task.id, "qa")

    # 5. QA reviews and updates
    review = await self.agents["qa"].review_code(implementation)
    await self.blackboard.update_task(
        task.id, "qa",
        status="complete",
        data={"review": review}
    )

    # 6. Get final state with history
    final_state = await self.blackboard.get_task(task.id)

    return {
        "pattern": "blackboard",
        "task_id": task.id,
        "final_state": final_state.to_dict(),
        "history": final_state.history
    }
```

## Common Patterns

### Error Handling

```python
try:
    result = await self.agents["dev"].implement_feature(task)
except Exception as e:
    logger.error(f"Implementation failed: {e}")
    return {
        "status": "failed",
        "error": str(e),
        "task_id": task.id
    }
```

### Timeouts

```python
import asyncio

try:
    result = await asyncio.wait_for(
        self.agents["dev"].implement_feature(task),
        timeout=30.0
    )
except asyncio.TimeoutError:
    logger.error("Operation timed out")
    # Handle timeout
```

### Polling for State Changes

```python
async def _wait_for_claim(self, task_id, expected_agent, timeout=30):
    start_time = asyncio.get_event_loop().time()

    while True:
        # Check current state
        task_state = await self.blackboard.get_task(task_id)

        if task_state and task_state.assigned_to == expected_agent:
            return True

        # Check timeout
        if asyncio.get_event_loop().time() - start_time > timeout:
            logger.warning(f"Timeout waiting for {expected_agent} to claim {task_id}")
            return False

        # Wait before next poll
        await asyncio.sleep(1)
```

## Testing Your Implementation

### Run Specific Pattern Tests

```bash
# Test manager pattern
pytest starter/tests/test_swarm_coordinator.py::TestManagerPattern -v

# Test peer pattern
pytest starter/tests/test_swarm_coordinator.py::TestPeerPattern -v

# Test blackboard pattern
pytest starter/tests/test_swarm_coordinator.py::TestBlackboardPattern -v
```

### Run Integration Tests

```bash
pytest starter/tests/test_integration.py -v -m integration
```

### Debug Tips

1. **Check Redis**: Use Redis Commander at http://localhost:8081 (login admin/admin)
2. **Enable Debug Logging**: Run pytest with `--log-cli-level=DEBUG`, or change
   `level=logging.INFO` in `example_usage.py`. The `LOG_LEVEL` value in `.env`
   is loaded into the config. Nothing applies it to the loggers.
3. **Inspect Messages**: Use `message_bus.get_message_history(agent_id)`
4. **Check Blackboard State**: Use `blackboard.get_task(task_id)`
5. **Add Logging**: Use `logger.info()` at key points

## Common Issues

### Task Not Claimed

**Problem**: The task is posted but no agent claims it

**Solution**: The agents have no background loop. Make the claim from your coordinator, or implement a watcher

### Messages Not Delivered

**Problem**: An agent sends a message, but the recipient does not receive it

**Solution**: Check that the agent subscribed to the message bus and that the callback is async

### Coordination Timeout

**Problem**: Coordination takes too long and times out

**Solution**: Increase the timeouts, or check for deadlocks in agent communication

## Next Steps

1. Start with Exercise 1 (Manager Pattern). It is the simplest.
2. Do Exercise 2 (Peer-to-Peer). It adds direct communication.
3. Do Exercise 3 (Blackboard). It has the most complex coordination.
4. Run the integration tests to check that all patterns work.
5. Try hybrid approaches that combine patterns.
