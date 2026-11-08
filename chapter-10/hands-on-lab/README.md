# Bonus lab: multi-agent coordination with the Anthropic SDK

> **This is a bonus lab.** Chapter 10's primary lab (Section 10.7) runs in
> Claude Code with agent definitions and hooks. Its files are in
> [`../code-examples/`](../code-examples/). Do the main lab first.

> **Model note (as of November 7, 2026).** `claude-sonnet-4-5` retires on
> November 30, 2026. If your `.env` names it, change it. The default model is
> `claude-sonnet-4-6`. See the note in `.env.example` before you switch models.

In this lab you write three of the chapter's coordination patterns in Python.
You use the Anthropic Python SDK, with Redis for messaging. The patterns are:

- a manager agent (hierarchical, Section 10.2)
- direct peer messaging (Section 10.3)
- the blackboard (Section 10.6)

## What you'll learn

1. **Manager pattern**: a central Scrum Master directs the Dev and QA agents.
2. **Peer-to-peer communication**: agents negotiate directly, with no coordinator.
3. **Blackboard architecture**: agents claim and update tasks on shared state.
4. **Trade-offs**: compare how the three patterns handle the same task.
5. **Async agent communication**: run agent operations concurrently over message queues.

## Time required

This budget is for the bonus lab only. The main Chapter 10 lab (Sections 10.7
and 10.8) takes a separate 90-120 minutes.

- **Setup**: 15-20 minutes
- **Exercise 1 (Manager pattern)**: 45-60 minutes
- **Exercise 2 (Peer-to-peer)**: 45-60 minutes
- **Exercise 3 (Blackboard)**: 60-75 minutes
- **Total**: 3-4 hours

## Prerequisites

### Knowledge
- Python 3.11+ with async/await
- Some familiarity with message queues; Redis experience helps but is not required
- Basic use of the Claude Messages API

### Software
- **Docker Desktop**: runs Redis
- **Python 3.11 or 3.12** (both tested) with pip
- **An Anthropic API key**: from the Claude Console at platform.claude.com.
  `verify_setup.py` requires one in `.env`. `example_usage.py` makes real API
  calls. Both test suites mock the model calls, so running the tests costs
  nothing.
- **Git**
- Network access for API calls

`requirements.txt` pins the Anthropic SDK below 1.0 on purpose:

- The agents pass a `temperature` to every `messages.create()` call.
- SDK 1.x removed that argument. It raises `TypeError: AsyncMessages.create() got an unexpected keyword argument
  'temperature'`.
- The agents would catch that error and turn it into `"status": "failed"`
  results.

The default model, `claude-sonnet-4-6`, accepts a temperature. It does not
think unless asked. For the model retirement date, see the model note at the
top of this file.

## Setup Instructions

### Step 1: Start Infrastructure

Start the Redis services with Docker Compose:

```bash
# From the hands-on-lab/ directory
docker compose up -d

# Verify services are running
docker compose ps
```

You should see:
- `redis`: Main Redis instance (port 6379)
- `redis-commander`: Web UI (port 8081)

To inspect messages and state, open Redis Commander at http://localhost:8081
(login admin/admin).

### Step 2: Create Python Virtual Environment

```bash
# Create virtual environment (any Python 3.11 or later)
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your Claude API key
# ANTHROPIC_API_KEY=your_actual_key_here
```

### Step 4: Verify Setup

```bash
# Run verification script
python verify_setup.py
```

The script runs nine checks. It prints a pass or fail line for each check,
with a detail line under it (trimmed here):

```text
Python Version... PASS
Starter Code Files... PASS
Python Dependencies... PASS
Environment Variables... PASS
Docker Services... PASS
Redis Connection... PASS
Message Bus... PASS
Blackboard... PASS
Agent Initialization... PASS

All checks passed! (9/9)
```

If any check fails, the script exits with status 1, so you can wire it into a
script. For failed checks, see Troubleshooting below.

The Docker check runs `docker compose ps` from this directory. If you run Redis
some other way, that one check fails. The three Redis-backed checks still pass.

## Lab structure

```text
hands-on-lab/
├── docker-compose.yml          # Redis + Redis Commander
├── requirements.txt
├── .env.example                # Copy to .env and add your API key
├── verify_setup.py             # Nine setup checks
├── example_usage.py            # Runs all three patterns once you've implemented them
├── pytest.ini
├── exercises/                  # Step-by-step guides, one per pattern, plus reference pages
└── starter/
    ├── README.md               # Component overview and pseudocode for each method
    ├── __init__.py
    ├── swarm_coordinator.py    # YOU IMPLEMENT the three TODO methods here
    ├── base_agent.py           # Ready to use
    ├── dev_agent.py            # Ready to use
    ├── qa_agent.py             # Ready to use
    ├── scrum_agent.py          # Ready to use
    ├── message_bus.py          # Ready to use (Redis pub/sub)
    ├── blackboard.py           # Ready to use (Redis shared state)
    ├── config.py               # Ready to use
    └── tests/
        ├── test_swarm_coordinator.py   # Unit tests (mocked Redis and API)
        └── test_integration.py         # Integration tests (need Redis running)
```

Start with [exercises/README.md](./exercises/README.md). It lists the three
exercises in order and links the reference material.

### What you'll implement

You will complete three methods in `swarm_coordinator.py`:

1. **`coordinate_task_manager_pattern()`**: Manager/hierarchical coordination
2. **`coordinate_task_peer_pattern()`**: Peer-to-peer direct communication
3. **`coordinate_task_blackboard_pattern()`**: Shared state coordination

The supporting classes (agents, message bus, blackboard) are complete. You do not change them.

## Exercise 1: Manager Pattern (Hierarchical Coordination)

### Objective

Implement centralized coordination. The Scrum Master agent is the manager. It assigns tasks to the Dev and QA agents and monitors their progress.

### Pattern Overview

```text
Task → Scrum Master → Dev Agent → Scrum Master → QA Agent → Result
        (assigns)     (implements)  (monitors)   (validates)
```

### Implementation Steps

1. **Task Assignment**: The Scrum Master reads the task and assigns it to the Dev agent.
2. **Development**: The Dev agent implements the feature.
3. **Progress Monitoring**: The Scrum Master tracks dev progress.
4. **QA Handoff**: The Scrum Master requests QA validation.
5. **Result Collection**: The Scrum Master combines the final result.

### Key APIs to Use

```python
# Scrum Master operations
await self.agents["scrum"].assign_task(task, agent_name="dev")
await self.agents["scrum"].monitor_progress(task.id)

# Dev Agent operations
result = await self.agents["dev"].implement_feature(task)

# QA Agent operations
validation = await self.agents["qa"].test_feature(result)

# Handoff (the manager brokers it, rather than dev talking to qa)
await self.agents["scrum"].coordinate_handoff(task.id, "dev", "qa", context)
```

### Success Criteria

- The Scrum agent assigns the task to dev.
- The Dev agent completes the implementation.
- The Scrum agent coordinates the QA handoff.
- The QA agent validates the work.
- The final result includes every agent's contribution.

### Testing

```bash
pytest starter/tests/test_swarm_coordinator.py::TestManagerPattern -v
```

## Exercise 2: Peer-to-Peer Pattern (Direct Communication)

### Objective

Implement decentralized coordination. The agents message each other directly. They negotiate responsibilities and share feedback.

### Pattern Overview

```text
Task → Dev Agent ←→ QA Agent → Result
       (implements) (direct communication) (validates)
```

### Implementation Steps

1. **Dev Starts**: The Dev agent starts the feature implementation.
2. **Direct Message**: Dev sends "ready for review" to QA.
3. **QA Feedback**: QA reviews and sends feedback directly to Dev.
4. **Negotiation**: Dev and QA negotiate until they agree.
5. **Result**: Return the agreed result.

### Key APIs to Use

```python
# Direct agent-to-agent messaging. Note the parameter is to_agent, not to.
await self.agents["dev"].send_message(
    to_agent="qa",
    message_type="review_request",
    payload={"task_id": task.id, "implementation": result}
)

# Or the convenience wrapper, which sends the same message
await self.agents["dev"].collaborate_with_qa(task.id, result)

# Reading what arrived. Delivery is async, so allow a moment first.
await asyncio.sleep(1)
messages = await self.agents["qa"].get_pending_messages()

# Negotiation
review = await self.agents["qa"].review_code(result)
feedback = await self.agents["qa"].provide_feedback(task.id, result, issues)
response = await self.agents["dev"].respond_to_feedback(feedback)
```

### Success Criteria

- Dev and QA communicate directly, with no manager.
- The agents negotiate and reach agreement.
- The message flow has little back-and-forth.
- The final result records the joint decision.

### Testing

```bash
pytest starter/tests/test_swarm_coordinator.py::TestPeerPattern -v
```

## Exercise 3: Blackboard Pattern (Shared State Coordination)

### Objective

Implement shared-state coordination. Agents watch a shared blackboard and claim tasks when ready. They update the state so other agents can see it.

### Pattern Overview

```text
     Blackboard (Shared State)
         ↑   ↓   ↑   ↓
    Dev Agent   QA Agent   Scrum Agent
    (watches)   (watches)  (watches)
```

### Implementation Steps

1. **Post Task**: Write the task to the blackboard.
2. **Agent Watching**: All agents watch the blackboard for relevant tasks.
3. **Task Claiming**: Dev claims the task and sets the status to "in_progress".
4. **State Updates**: Dev writes progress to the blackboard and marks "ready_for_review". Then Dev releases its claim.
5. **QA Observes**: QA sees "ready_for_review" and claims the task for validation.
6. **Final State**: The task is marked complete, with full history.

The agents in this lab run no background loop of their own. Your coordinator
makes their moves on the board:

1. After posting, call `claim_task(task.id, "dev")`.
2. After dev releases, call `claim_task(task.id, "qa")`.

If you wait for a claim that nothing makes, the wait only runs out the polling
timeout. The `_wait_for_claim()` and `_wait_for_status_change()` helpers ship
as stubs that return `None`. Implement them before you rely on them.

### Key APIs to Use

```python
# Post a TaskState (not the Task itself) to the board
task_state = TaskState(task.id, task.description, status="pending")
await self.blackboard.post_task(task_state)

# Agent watching and claiming. claim_task returns False if someone else has it.
available_tasks = await self.blackboard.get_tasks(status="pending")
claimed = await self.blackboard.claim_task(task.id, "dev")

# State updates. agent_id is required and must hold the claim.
await self.blackboard.update_task(
    task_id=task.id,
    agent_id="dev",
    status="in_progress",
    data={"progress": "50%"}
)

# Handoff. The holder releases its claim so the next agent's claim succeeds.
# Status is left as-is (e.g. "ready_for_review") unless you pass status=...
released = await self.blackboard.release_task(task.id, "dev")

# Query state
task_state = await self.blackboard.get_task(task.id)
```

### Success Criteria

- The task is posted to the blackboard.
- Agents claim and update the task on the board.
- No race conditions or conflicts occur.
- The history records every state change.
- The task completes with every agent's contribution.

### Testing

```bash
pytest starter/tests/test_swarm_coordinator.py::TestBlackboardPattern -v
```

### Manual verification on real Redis

The unit tests run against mocked Redis. Watch the dev-to-QA claim handoff
once on real Redis. Run these steps from the `hands-on-lab/` directory, with
the virtual environment active:

1. Start Redis:

   ```bash
   docker compose up -d
   docker compose ps
   ```

   Check that the `redis` service shows a running/`Up` status.

2. Run the handoff integration test:

   ```bash
   pytest starter/tests/test_integration.py::TestBlackboardPatternIntegration::test_claim_release_handoff -v -s
   ```

   Expected output (trimmed):

   ```text
   OK: QA claim rejected while dev held the task
   OK: Dev released the claim after ready_for_review
   OK: QA claimed and completed the review
   ... 1 passed ...
   ```

3. Or walk the same sequence by hand with a bash heredoc. On Windows
   PowerShell, save the snippet between the `EOF` markers to a file and run
   `python file.py`.

   ```bash
   python - <<'EOF'
   import asyncio
   from starter.blackboard import Blackboard, TaskState

   async def main():
       bb = Blackboard({"redis_host": "localhost", "redis_port": 6379, "redis_db": 1})
       await bb.initialize()
       await bb.clear()
       await bb.post_task(TaskState("handoff_demo", "Verify the claim handoff"))
       print("dev claims:          ", await bb.claim_task("handoff_demo", "dev"))
       print("dev ready_for_review:", await bb.update_task("handoff_demo", "dev", status="ready_for_review"))
       print("qa claim (dev holds):", await bb.claim_task("handoff_demo", "qa"))
       print("dev releases:        ", await bb.release_task("handoff_demo", "dev"))
       print("qa claims:           ", await bb.claim_task("handoff_demo", "qa"))
       print("qa completes:        ", await bb.update_task("handoff_demo", "qa", status="complete"))
       state = await bb.get_task("handoff_demo")
       print("final state:         ", state.status, "held by", state.assigned_to)
       await bb.clear()
       await bb.close()

   asyncio.run(main())
   EOF
   ```

   Expected output:

   ```text
   dev claims:           True
   dev ready_for_review: True
   qa claim (dev holds): False
   dev releases:         True
   qa claims:            True
   qa completes:         True
   final state:          complete held by qa
   ```

   The `False` on the third line comes from the ownership check. QA cannot
   take the task until dev releases it. At the same moment, the log shows
   `Task handoff_demo already claimed by dev`. This line is the blackboard's
   warning for the rejected claim. It is not an error. Everything after the
   release succeeds.

   You can also watch the `blackboard:task:handoff_demo` key change in Redis
   Commander (http://localhost:8081) while you run this. The snippet and the
   integration tests use Redis DB 1. The UI lists it as the `tests`
   connection. `example_usage.py` uses DB 0, listed as `local`.

   When you finish, stop Redis with `docker compose down` (see Shutting down
   at the end of this README). The script already clears its own
   `handoff_demo` task from the board.

## Key APIs reference

The signatures below match the code in `starter/`. For return-value examples,
see `exercises/QUICK_REFERENCE.md`.

### SwarmCoordinator

```python
coordinator = SwarmCoordinator(config, CoordinationPattern.MANAGER)
await coordinator.setup()
result = await coordinator.coordinate_task_manager_pattern(task)
metrics = await coordinator.get_metrics()
await coordinator.cleanup()
```

`config` is a plain dict. `example_usage.py` builds it with `load_config().dict()`.

### Agent base methods

Every agent inherits these from `BaseAgent`:

```python
await agent.send_message(to_agent, message_type, payload)   # to_agent=None broadcasts
await agent.get_pending_messages()
state = await agent.read_blackboard(task_id)
await agent.write_blackboard(task_id, status=..., data=...)
claimed = await agent.claim_task(task_id)                   # uses the agent's own id
released = await agent.release_task(task_id)                # gives the claim back
```

### DevAgent

```python
result = await dev_agent.implement_feature(task)
fix = await dev_agent.fix_bug(bug_description, context=None)
response = await dev_agent.respond_to_feedback(feedback)
await dev_agent.collaborate_with_qa(task_id, implementation)
```

### QAAgent

```python
review = await qa_agent.review_code(implementation)
test_result = await qa_agent.test_feature(implementation)
feedback = await qa_agent.provide_feedback(task_id, implementation, issues=None)
validation = await qa_agent.validate_quality(implementation)
```

### ScrumAgent

```python
prioritized = await scrum_agent.prioritize_tasks(tasks)
assignment = await scrum_agent.assign_task(task, agent_name="dev")
progress = await scrum_agent.monitor_progress(task_id)
handoff = await scrum_agent.coordinate_handoff(task_id, "dev", "qa", context)
resolution = await scrum_agent.resolve_blockers(blocker)
```

### MessageBus

```python
await message_bus.connect()
await message_bus.subscribe(agent_id, callback)      # callback receives a Message
await message_bus.publish(from_agent, to_agent, message_type, payload)
history = await message_bus.get_message_history(agent_id)
await message_bus.disconnect()
```

Delivery is push-based through the subscription callback. There is no
`listen()` generator. `BaseAgent` registers its own callback in `setup()` and
buffers incoming messages. Read them with `get_pending_messages()`.

### Blackboard

```python
await blackboard.initialize()
await blackboard.post_task(task_state)                  # a TaskState, not a Task
claimed = await blackboard.claim_task(task_id, agent_id)
released = await blackboard.release_task(task_id, agent_id, status=None)
await blackboard.update_task(task_id, agent_id, status=..., data=...)
state = await blackboard.get_task(task_id)
tasks = await blackboard.get_tasks(status="pending")
queue = await blackboard.watch_status("ready_for_review")
await blackboard.close()
```

- `claim_task` is atomic. It returns `False` if another agent already holds
  the task.
- `update_task` requires the `agent_id` that holds the claim.
- `release_task` is the handoff. The holder clears its claim. The status stays
  the same unless you pass `status=...`. Only then can the next agent claim.
  It returns `False` if the caller does not hold the claim or nothing is
  claimed.

## Running Tests

### Run All Tests

```bash
pytest starter/tests/ -v
```

The integration tests need Redis running (`docker compose up -d`). To run
only the offline unit tests, deselect the integration tests:

```bash
pytest starter/tests/ -v -m "not integration"
```

The suite has 24 tests: 15 unit and 9 integration. Expect these results:

- A test that reaches an unimplemented method reports SKIPPED ("not yet
  implemented - this is expected"). It does not report FAILED.
- A fresh checkout shows 10 passed and 5 skipped for the unit tests.
- With Redis up, a fresh checkout shows 13 passed and 11 skipped.
- Each method you finish turns its skips into passes.
- With all three methods done, the full run reports 24 passed.

If you see a SKIPPED line for the pattern you just implemented, the method
still raises `NotImplementedError` somewhere.

### Run Specific Test File

```bash
pytest starter/tests/test_swarm_coordinator.py -v
pytest starter/tests/test_integration.py -v
```

### Run Specific Test

```bash
pytest starter/tests/test_swarm_coordinator.py::TestManagerPattern::test_manager_pattern_coordination -v
```

### With Coverage

```bash
pytest starter/tests/ --cov=starter --cov-report=html
open htmlcov/index.html       # macOS; xdg-open on Linux, start on Windows
```

## Troubleshooting

### Redis Connection Errors

**Error**: `redis.exceptions.ConnectionError: Error connecting to Redis`

**Solution**:
```bash
# Check if Redis is running
docker compose ps

# Restart Redis
docker compose restart redis

# Check Redis logs
docker compose logs redis
```

### Port Already in Use

**Error**: `port is already allocated`

**Solution**:
```bash
# Find process using port 6379
lsof -i :6379  # On Mac/Linux
netstat -ano | findstr :6379  # On Windows

# Kill the process or change port in docker-compose.yml
```

Port 8081 (Redis Commander) is also the default port of the challenge lab's
inventory service (`../challenge-lab/`). Don't run both at once. Or override
one side: change the `127.0.0.1:8081:8081` mapping here, or set `INVENTORY_PORT` there.

### Redis Not Reachable from WSL

**Error**: `ConnectionError` to `localhost:6379` from a WSL distro, while Redis
Commander (http://localhost:8081) opens in a Windows browser

**Solution**: `docker-compose.yml` publishes Redis and Redis Commander on
`127.0.0.1` only. This keeps them off your network. Redis has no password, and
Redis Commander's login is admin/admin. With Docker Desktop on Windows and the
lab inside WSL, do this:

1. Remove the `127.0.0.1:` prefix from both `ports` entries (`"6379:6379"`
   and `"8081:8081"`).
2. Restart:

```bash
docker compose up -d
```

This publishes the ports on every interface. Do it only on a network you trust.

### Module Import Errors

**Error**: `ModuleNotFoundError: No module named 'starter'`

**Solution**:
```bash
# Ensure you're in the hands-on-lab directory
pwd

# Reinstall dependencies
pip install -r requirements.txt

# Add current directory to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

On Windows PowerShell, use `$env:PYTHONPATH = (Get-Location).Path`.

### Claude API Errors

**Error**: `AuthenticationError: Invalid API key`

**Solution**:
```bash
# Verify .env file exists and has correct key
cat .env | grep ANTHROPIC_API_KEY

# Ensure no extra spaces or quotes
# Should be: ANTHROPIC_API_KEY=sk-ant-...
```

### Async Test Warnings

**Warning**: `RuntimeWarning: coroutine was never awaited`

**Solution**:
- Check that every async call uses `await`.
- Mark test functions with `@pytest.mark.asyncio`.
- Check that pytest-asyncio is installed.

### Rate Limiting

**Error**: `rate_limit_error: Too many requests`

**Solution**:
- Add delays between agent operations.
- Use exponential backoff for retries.
- Cache agent responses during testing.

## Best Practices

### 1. Error Handling

Wrap agent operations in try-except blocks:

```python
try:
    result = await self.agents["dev"].implement_feature(task)
except Exception as e:
    # Log error and handle gracefully
    logger.error(f"Dev agent failed: {e}")
    # Potentially reassign or retry
```

### 2. Timeouts

Set timeouts on agent operations:

```python
import asyncio

try:
    result = await asyncio.wait_for(
        self.agents["dev"].implement_feature(task),
        timeout=30.0
    )
except asyncio.TimeoutError:
    # Handle timeout
```

### 3. Message Cleanup

Clean up subscriptions and connections:

```python
try:
    # Your coordination logic
    pass
finally:
    await self.message_bus.unsubscribe(self.agent_id)
    await self.message_bus.disconnect()
```

### 4. Logging

Add logging for debugging:

```python
import logging

logger = logging.getLogger(__name__)
logger.info(f"Coordinating task {task.id} using {self.pattern}")
```

### 5. Testing Patterns

Use pytest fixtures for common setup:

```python
@pytest.fixture
async def coordinator():
    coord = SwarmCoordinator(test_config, CoordinationPattern.MANAGER)
    await coord.setup()
    yield coord
    await coord.cleanup()
```

## Next steps

After completing all three exercises:

1. **Compare patterns**: note which pattern suited which task.
2. **Extend the team**: add a security or performance agent.
3. **Hybrid patterns**: combine two patterns in one workflow.
4. **Add monitoring**: emit metrics for each coordination step.
5. **Production hardening**: add error recovery, persistence, and backpressure.

If you skipped the main lab, go back to Section 10.7. The native agent approach
reaches the same coordination results without a message bus of your own.
Compare the two approaches.

## Shutting down

```bash
docker compose down          # stop Redis and the web UI
docker compose down -v       # same, and also drop the persisted Redis data
```

Redis keeps its data in the `redis-data` named volume. The data survives a
plain `docker compose down`. To start clean, add `-v`.

## Additional resources

- **Redis docs**: https://redis.io/docs/
- **Python asyncio**: https://docs.python.org/3/library/asyncio.html
- **Claude API docs**: https://platform.claude.com/docs
- **Chapter 10** of *Practical Agentic Coding*: when to use each pattern and why (Sections 10.2, 10.3, and 10.6)

## Getting unstuck

This bonus lab ships no `complete/` reference solution. Use these instead:

- The unit test assertions define what each coordinator method must return.
- The pseudocode in `starter/README.md` and each exercise's progressive hints
  cover the rest.

When you get stuck, check these in order:

1. The Troubleshooting section above.
2. The test output. The assertions describe what the coordinator should return.
3. The pseudocode in `starter/README.md` and the hints in each exercise file.
4. Redis Commander (http://localhost:8081, admin/admin), to inspect messages and blackboard state.
5. Chapter 10, Sections 10.2, 10.3, and 10.6, for the pattern explanations.
