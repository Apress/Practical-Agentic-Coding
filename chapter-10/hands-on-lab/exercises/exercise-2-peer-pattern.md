# Exercise 2: Peer-to-Peer Coordination

**Time**: 45-60 minutes
**Difficulty**: Intermediate
**Prerequisites**: Exercise 1 completed

## What you'll do

- Implement direct Dev-to-QA messaging over the MessageBus, with no manager
- Run a negotiation loop between the two agents, with a round cap
- Record the negotiation history in the result

## Background

In this exercise, the Dev and QA agents talk to each other over the message
bus. They repeat until QA approves or the round cap is reached. The Scrum Master
stays out of it.

When to use handoffs and direct peer messaging and why: Chapter 10, Section 10.3.

## The Pattern

```text
Manager Pattern                Peer-to-Peer Pattern
───────────────               ────────────────────

    Manager                      (No manager)
       ↕
    Dev ← → QA                   Dev ←─────→ QA
  [Via manager]                  [Direct messages]
```

### Peer-to-Peer Flow (Detailed)

```text
┌─────────────────────────────────────────────────────────────────┐
│                 PEER-TO-PEER COORDINATION FLOW                   │
└─────────────────────────────────────────────────────────────────┘

Phase 1: INITIAL IMPLEMENTATION
    │
    └─> Dev starts work independently
        │
        ├─> await dev.implement_feature(task)
        ├─> Dev creates initial implementation
        └─> Dev decides when ready for review

Phase 2: REVIEW REQUEST
    │
    └─> Dev sends message to QA
        │
        ├─> await dev.collaborate_with_qa(task.id, implementation)
        │   └─> Publishes "review_request" to MessageBus
        │       ├─> to_agent: "qa"
        │       ├─> message_type: "review_request"
        │       └─> payload: {task_id, implementation}
        │
        └─> QA receives message via subscription

Phase 3: QA REVIEW
    │
    └─> QA independently reviews the work
        │
        ├─> await qa.review_code(implementation)
        ├─> QA analyzes quality, finds issues
        └─> QA makes approval decision

Phase 4: FEEDBACK EXCHANGE
    │
    ├─> IF QA approves:
    │   │
    │   └─> QA sends "qa_feedback" message
    │       ├─> approved: True
    │       ├─> quality_score: 9.0
    │       └─> Dev receives approval
    │           └─> Collaboration complete!
    │
    └─> IF QA finds issues:
        │
        └─> QA sends "qa_feedback" message
            ├─> approved: False
            ├─> issues: ["issue1", "issue2"]
            └─> Dev receives feedback
                └─> Continue to Phase 5

Phase 5: NEGOTIATION LOOP
    │
    └─> Dev responds to feedback
        │
        ├─> await dev.respond_to_feedback(feedback)
        ├─> Dev proposes changes/fixes
        └─> Send response to QA
            │
            ├─> QA reviews response
            ├─> QA may approve or request more changes
            └─> Loop continues until:
                ├─> QA approves, OR
                ├─> Max iterations reached (e.g., 3)
                └─> Return final negotiation result

Phase 6: RESULT AGGREGATION
    │
    └─> Collect negotiation history
        │
        ├─> All messages exchanged
        ├─> Number of negotiation rounds
        ├─> Final approval status
        └─> Return the full result
```

## What You'll Build

You implement the `coordinate_task_peer_pattern()` method in `starter/swarm_coordinator.py`. The method does these steps:
1. Starts the Dev implementation
2. Lets Dev and QA talk to each other directly
3. Runs the negotiation loop, with a maximum number of rounds
4. Tracks the message history
5. Returns the negotiation results

## Step 1: Review the Starter Code

Open `starter/swarm_coordinator.py` and locate the `coordinate_task_peer_pattern()` method (line 163):

```python
async def coordinate_task_peer_pattern(self, task: Task) -> Dict[str, Any]:
    """
    Coordinate using peer-to-peer pattern (direct communication).

    TODO (Exercise 2): Implement peer coordination
    """
    logger.info(f"Coordinating task {task.id} using PEER-TO-PEER pattern")

    # TODO: Students implement peer-to-peer pattern coordination here
    raise NotImplementedError(
        "Exercise 2: Implement peer-to-peer pattern coordination."
    )
```

## Step 2: Understand the MessageBus

Agents use the MessageBus to send messages directly to each other:

### Publishing Messages (Sending)
```python
# Agent sends message to another agent
await dev.send_message(
    to_agent="qa",
    message_type="review_request",
    payload={
        "task_id": task.id,
        "implementation": implementation,
        "from_agent": "dev"
    }
)
```

### Subscribing to Messages (Receiving)
```python
# Agents automatically subscribe when setup() is called
# Messages are processed in their process_message() method

# In base_agent.py (already implemented):
async def setup(self):
    if self.message_bus:
        await self.message_bus.subscribe(self.agent_id, self._handle_incoming_message)

# _handle_incoming_message() buffers each arrival (read it later with
# get_pending_messages()) and then calls process_message()
```

### Retrieving Message History
```python
# Get messages sent by an agent
messages = await self.message_bus.get_message_history(
    agent_id="dev",
    limit=10
)

# Returns Message objects, newest first. Each one has the attributes
# from_agent, to_agent, message_type, payload, and timestamp (a datetime).
```

## Step 3: Implementation Strategy (Pseudo-code)

Implement this algorithm:

```text
FUNCTION coordinate_task_peer_pattern(task):

    # Initialize tracking
    start_time = current_time()
    negotiation_history = []
    max_negotiation_rounds = 3
    current_round = 0

    # Phase 1: Dev Implementation
    log("Dev starting implementation")
    implementation = await dev.implement_feature(task)

    IF implementation["status"] != "implemented":
        return failure_result(implementation)

    add_to_history(negotiation_history, "implementation", implementation)

    # Phase 2: Initial Review Request
    log("Dev requesting review from QA")
    await dev.collaborate_with_qa(task.id, implementation)
    # This sends "review_request" message to QA

    # Give QA time to process message
    await asyncio.sleep(1)

    # Phase 3: QA Review
    log("QA reviewing implementation")
    qa_review = await qa.review_code(implementation)
    add_to_history(negotiation_history, "qa_review", qa_review)

    # Phase 4: Negotiation Loop
    WHILE qa_review["approved"] == False AND current_round < max_negotiation_rounds:
        current_round += 1
        log(f"Negotiation round {current_round}")

        # Dev responds to feedback
        feedback = {
            "feedback": qa_review["review"],
            "issues": qa_review["issues"],
            "quality_score": qa_review["quality_score"]
        }

        dev_response = await dev.respond_to_feedback(feedback)
        add_to_history(negotiation_history, f"dev_response_{current_round}", dev_response)

        # Allow message propagation
        await asyncio.sleep(1)

        # QA re-reviews based on response
        qa_review = await qa.review_code({
            "implementation": implementation["implementation"],
            "dev_response": dev_response,
            "round": current_round
        })
        add_to_history(negotiation_history, f"qa_review_{current_round}", qa_review)

    # Phase 5: Determine Final Status
    IF qa_review["approved"]:
        final_status = "approved"
        reason = f"Approved after {current_round} negotiation rounds"
    ELSE IF current_round >= max_negotiation_rounds:
        final_status = "max_iterations_reached"
        reason = f"Max negotiations ({max_negotiation_rounds}) reached without approval"
    ELSE:
        final_status = "approved"
        reason = "Approved on first review"

    # Phase 6: Build Result
    end_time = current_time()
    duration = end_time - start_time

    return {
        "pattern": "peer_to_peer",
        "task_id": task.id,
        "negotiation_history": negotiation_history,
        "negotiation_rounds": current_round,
        "final_status": final_status,
        "reason": reason,
        "final_qa_review": qa_review,
        "dev_implementation": implementation,
        "duration_seconds": duration,
        "success": qa_review["approved"]
    }
```

## Progressive Hints

<details>
<summary><b>Hint 1: Starting Dev Implementation</b> (Click to expand)</summary>

First, have the Dev agent implement the feature on its own:

```python
# Get the Dev agent
dev = self.agents["dev"]

# Dev implements feature (no manager needed)
implementation = await dev.implement_feature(task)

# Check for implementation errors
if implementation.get("status") != "implemented":
    return {
        "pattern": "peer_to_peer",
        "task_id": task.id,
        "success": False,
        "error": "Implementation failed",
        "details": implementation
    }
```

The Dev agent works on its own. It needs no assignment.
</details>

<details>
<summary><b>Hint 2: Initiating Peer Collaboration</b> (Click to expand)</summary>

Have Dev request a review from QA directly:

```python
# Dev sends review request directly to QA
await dev.collaborate_with_qa(task.id, implementation)

# This internally calls send_message():
# await self.message_bus.publish(
#     from_agent="dev",
#     to_agent="qa",
#     message_type="review_request",
#     payload={"task_id": task.id, "implementation": implementation}
# )

# Give QA time to receive and process the message
import asyncio
await asyncio.sleep(1)
```

The message travels through the MessageBus to QA.
</details>

<details>
<summary><b>Hint 3: QA Review Process</b> (Click to expand)</summary>

QA reviews the implementation on its own:

```python
# Get the QA agent
qa = self.agents["qa"]

# QA performs review
qa_review = await qa.review_code(implementation)

# qa_review contains:
# {
#     "task_id": task.id,
#     "status": "reviewed",
#     "review": "detailed review text",
#     "quality_score": 8.5,
#     "approved": True/False,
#     "issues": ["issue1", "issue2"],
#     "agent": "qa"
# }

# Check if approved
if qa_review["approved"]:
    # Success! No negotiation needed
    pass
else:
    # Need to negotiate
    pass
```

QA decides on its own, based on its quality standards.
</details>

<details>
<summary><b>Hint 4: Implementing Negotiation Loop</b> (Click to expand)</summary>

Handle repeated feedback rounds between Dev and QA:

```python
max_rounds = 3
current_round = 0
negotiation_history = []

# Track initial implementation and review
negotiation_history.append({
    "phase": "implementation",
    "agent": "dev",
    "result": implementation
})
negotiation_history.append({
    "phase": "initial_review",
    "agent": "qa",
    "result": qa_review
})

# Negotiation loop
while not qa_review["approved"] and current_round < max_rounds:
    current_round += 1

    # Dev responds to feedback
    feedback = {
        "feedback": qa_review.get("review"),
        "issues": qa_review.get("issues", []),
        "quality_score": qa_review.get("quality_score")
    }

    dev_response = await dev.respond_to_feedback(feedback)
    negotiation_history.append({
        "phase": f"dev_response_round_{current_round}",
        "agent": "dev",
        "result": dev_response
    })

    # Allow message propagation
    await asyncio.sleep(1)

    # QA re-reviews
    qa_review = await qa.review_code(implementation)
    negotiation_history.append({
        "phase": f"qa_review_round_{current_round}",
        "agent": "qa",
        "result": qa_review
    })
```

In each round, Dev improves the work based on QA feedback.
</details>

<details>
<summary><b>Hint 5: Determining Final Status</b> (Click to expand)</summary>

After the negotiation loop, decide the outcome:

```python
# Check final status
if qa_review["approved"]:
    final_status = "approved"
    success = True
    if current_round == 0:
        reason = "Approved on first review"
    else:
        reason = f"Approved after {current_round} negotiation rounds"
elif current_round >= max_rounds:
    final_status = "max_iterations_reached"
    success = False
    reason = f"Max negotiations ({max_rounds}) reached without approval"
else:
    # Shouldn't happen, but handle gracefully
    final_status = "unknown"
    success = False
    reason = "Unexpected termination of negotiation loop"
```

The loop runs at most `max_rounds` rounds. Then it stops.
</details>

<details>
<summary><b>Hint 6: Building the full result</b> (Click to expand)</summary>

Return the details of the peer-to-peer coordination:

```python
from datetime import datetime

# Calculate duration
end_time = datetime.now()
duration = (end_time - start_time).total_seconds()

# Build final result
result = {
    "pattern": "peer_to_peer",
    "task_id": task.id,
    "negotiation_history": negotiation_history,
    "negotiation_rounds": current_round,
    "final_status": final_status,
    "reason": reason,
    "final_qa_review": qa_review,
    "dev_implementation": implementation,
    "duration_seconds": duration,
    "success": success,
    "max_rounds_allowed": max_rounds
}

return result
```

The negotiation history is the audit trail of the peer interaction.
</details>

## Common Pitfalls

### Pitfall 1: Infinite Negotiation Loops

```python
# Wrong: No limit on negotiations
while not qa_review["approved"]:
    dev_response = await dev.respond_to_feedback(feedback)
    qa_review = await qa.review_code(implementation)
    # Could loop forever!
```

```python
# Right: Max iterations limit
max_rounds = 3
current_round = 0

while not qa_review["approved"] and current_round < max_rounds:
    current_round += 1
    dev_response = await dev.respond_to_feedback(feedback)
    qa_review = await qa.review_code(implementation)
```

**Why it matters**: Without a limit, the agents might never agree. The system then hangs.

### Pitfall 2: Reading Messages Before They Arrive

```python
# Wrong: reading QA's inbox straight after sending
await dev.collaborate_with_qa(task.id, implementation)
messages = await qa.get_pending_messages()  # often still empty
```

```python
# Right: give the bus a moment to deliver first
await dev.collaborate_with_qa(task.id, implementation)
await asyncio.sleep(1)
messages = await qa.get_pending_messages()
```

**Why it matters**: Delivery over Redis pub/sub is asynchronous. Wait a moment
after the send before you read an agent's inbox. Calling
`qa.review_code(implementation)` directly does not depend on delivery.

### Pitfall 3: Using Manager Instead of Direct Communication

```python
# Wrong: Using manager in peer pattern
await self.agents["scrum"].coordinate_handoff(task.id, "dev", "qa", context)
# This is manager pattern, not peer-to-peer!
```

```python
# Right: Direct peer communication
await dev.collaborate_with_qa(task.id, implementation)
# Dev directly sends message to QA
```

**Why it matters**: Peer-to-peer has no intermediary. The agents communicate directly.

### Pitfall 4: Not Tracking Negotiation History

```python
# Wrong: Losing track of what happened
while not approved and round < max_rounds:
    dev_response = await dev.respond_to_feedback(feedback)
    qa_review = await qa.review_code(implementation)
    # No record of this exchange!
```

```python
# Right: Track all interactions
negotiation_history = []

negotiation_history.append({"phase": "initial", "result": implementation})

while not approved and round < max_rounds:
    dev_response = await dev.respond_to_feedback(feedback)
    negotiation_history.append({"phase": f"round_{round}", "result": dev_response})

    qa_review = await qa.review_code(implementation)
    negotiation_history.append({"phase": f"review_{round}", "result": qa_review})
```

**Why it matters**: You need the negotiation history for debugging and analysis.

### Pitfall 5: Wrong Success Criteria

```python
# Wrong: Assuming success when max rounds reached
if current_round >= max_rounds:
    return {"success": True, "reason": "Completed negotiations"}
    # But QA might not have approved!
```

```python
# Right: Success only if QA approves
if qa_review["approved"]:
    return {"success": True, "reason": "QA approved"}
elif current_round >= max_rounds:
    return {"success": False, "reason": "Max rounds reached without approval"}
```

**Why it matters**: Success means QA approved. Finishing the loop is not enough.

## Testing Your Implementation

### Run the Peer-to-Peer Pattern Tests

```bash
# Test just the peer-to-peer pattern
pytest starter/tests/test_swarm_coordinator.py::TestPeerPattern -v

# Test with detailed output
pytest starter/tests/test_swarm_coordinator.py::TestPeerPattern -v -s
```

### Expected Test Output

Before you implement the method, both coordination tests report SKIPPED ("Peer
pattern not yet implemented - this is expected"). When your implementation is
correct, you see the following output. It is shown with `-o log_cli=false`.
Without that flag, live logging puts agent INFO lines between these lines.

```text
starter/tests/test_swarm_coordinator.py::TestPeerPattern::test_peer_pattern_initialization PASSED
starter/tests/test_swarm_coordinator.py::TestPeerPattern::test_peer_pattern_coordination PASSED
starter/tests/test_swarm_coordinator.py::TestPeerPattern::test_peer_pattern_negotiation PASSED
3 passed
```

The negotiation test feeds QA a rejection and then an approval. It checks that
`review_code()` ran at least twice. It also checks that `respond_to_feedback()`
ran.

### Debugging Tips

The tests report these failures for the common mistakes:

1. **No negotiation loop** (QA reviews once and you return):
   ```text
   AssertionError: assert 1 >= 2
    +  where 1 = <AsyncMock id='...'>.call_count
   ```
   That is `test_peer_pattern_negotiation`. With Redis up, the integration test
   `test_peer_negotiation_with_feedback` fails with
   `AssertionError: Expected multiple QA reviews`.
   Solution: loop while QA has not approved. Re-review after each response

2. **Dev never answers the feedback**:
   ```text
   AssertionError: Expected 'mock' to have been called.
   ```
   Solution: call `dev.respond_to_feedback(review)` inside the loop

3. **Negotiation never ends**: The test run hangs and never prints a result.
   The lab installs no test timeout, so press Ctrl+C.
   Solution: add a `max_rounds` limit to the loop

4. **Result missing the task id**:
   ```text
   AssertionError: assert 'task_id' in {...}
   ```
   Solution: include `"task_id": task.id` in the dict you return

## Success Criteria

You've completed Exercise 2 when:

- All peer-to-peer pattern tests pass
- Dev and QA communicate directly, with no manager
- The negotiation loop has a round cap
- The result records the negotiation history
- Success means QA approved. Running out of rounds is not success

When to use direct peer messaging at handoffs: Chapter 10, Section 10.3. For
the hierarchical alternative you built in Exercise 1, see Section 10.2.

## Next Steps

After completing Exercise 2:

1. **Compare**: Note how this differs from Exercise 1's manager pattern.
2. **Experiment**: Try different `max_rounds` values (1, 3, 5).
3. **Analyze**: Look at the negotiation history. Count how many rounds usually occur.
4. **Optimize**: Look for ways to make the negotiation shorter.

---

**Next:** Exercise 3, shared-state coordination, in `exercise-3-blackboard-pattern.md`.
