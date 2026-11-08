# Visual overview: the three coordination patterns

Diagrams and checklists for the three methods you implement in this lab.

When to use each pattern and why: Chapter 10, Section 10.2 (hierarchical), Section 10.3 (peer messaging), and Section 10.6 (blackboard).

---

## The Three Patterns at a Glance

```text
┌──────────────────────────────────────────────────────────────────────┐
│                      COORDINATION PATTERNS                            │
└──────────────────────────────────────────────────────────────────────┘

Pattern 1: MANAGER                 Pattern 2: PEER-TO-PEER
──────────────────                 ───────────────────────

   Scrum Master                         Dev ←────→ QA
       ↕  ↕                            [Direct messages]
      Dev  QA                          [Negotiation loop]
  [All via manager]                   [No intermediary]

  Exercise 1                           Exercise 2
  45-60 minutes                        45-60 minutes


Pattern 3: BLACKBOARD
─────────────────────

     ╔════════════╗
     ║ BLACKBOARD ║   ← Shared state
     ║  Tasks     ║   ← Task queue
     ║  History   ║   ← Audit trail
     ╚════════════╝
        ↑  ↑  ↑
        │  │  │
       Dev QA Scrum
    [Agents watch & claim]
    [Opportunistic work]

  Exercise 3
  60-75 minutes
```

---

## Manager Pattern (Exercise 1)

### Architecture

```text
┌─────────────────────────────────────────────┐
│         CENTRALIZED COORDINATION             │
└─────────────────────────────────────────────┘

            ┌─────────────┐
            │   Scrum     │  ← Central coordinator
            │   Master    │  ← Makes all decisions
            └─────────────┘
                 ↕  ↕
        ┌────────┘  └────────┐
        ↓                     ↓
   ┌────────┐            ┌────────┐
   │  Dev   │            │   QA   │
   │ Agent  │            │ Agent  │
   └────────┘            └────────┘
    Workers              Workers
```

### Flow

```text
1. Scrum assigns task to Dev
2. Dev implements feature
3. Scrum monitors progress
4. Scrum coordinates handoff to QA
5. QA validates implementation
6. Scrum aggregates results
```

---

## Peer-to-Peer Pattern (Exercise 2)

### Architecture

```text
┌─────────────────────────────────────────────┐
│        DECENTRALIZED COMMUNICATION           │
└─────────────────────────────────────────────┘

        ┌────────┐ ←──────→ ┌────────┐
        │  Dev   │  Direct   │   QA   │
        │ Agent  │ Messages  │ Agent  │
        └────────┘ ←──────→ └────────┘
           ↕                     ↕
           └─── MessageBus ──────┘
              [Pub/Sub system]
```

### Flow

```text
1. Dev implements feature independently
2. Dev sends review request to QA
3. QA reviews and provides feedback
4. IF issues: Dev responds, QA re-reviews
5. LOOP until approved or max rounds
6. Return negotiation history
```

### Negotiation Loop

```text
Round 1:  Dev impl → QA review → feedback
Round 2:  Dev response → QA review → feedback
Round 3:  Dev response → QA review → APPROVED
          [Max 3 rounds]
```

---

## Blackboard Pattern (Exercise 3)

### Architecture

```text
┌─────────────────────────────────────────────┐
│          SHARED STATE COORDINATION           │
└─────────────────────────────────────────────┘

           ╔═════════════════════╗
           ║    BLACKBOARD       ║
           ║ ┌─────────────────┐ ║
           ║ │ Task Queue      │ ║
           ║ │ - pending       │ ║
           ║ │ - in_progress   │ ║
           ║ │ - ready_review  │ ║
           ║ │ - complete      │ ║
           ║ └─────────────────┘ ║
           ║                     ║
           ║ [Shared state]      ║
           ║ [Full history]      ║
           ╚═════════════════════╝
              ↑     ↑     ↑
              │     │     │
          ┌───┴─┐ ┌─┴──┐ ┌┴────┐
          │ Dev │ │ QA │ │Scrum│
          └─────┘ └────┘ └─────┘
          [Watch] [Claim] [Update]
```

### Flow

```text
1. Post task to blackboard (status: pending)
2. Coordinator claims the task for dev (→ claimed)
3. Dev updates status (→ in_progress)
4. Dev implements and updates (→ ready_for_review)
5. Dev releases its claim (status stays ready_for_review)
6. Coordinator claims for QA (→ claimed), then QA moves it to in_review
7. QA validates and updates (→ complete)
8. Retrieve final state with full history
```

### Task State Machine

```text
pending → claimed → in_progress → ready_for_review → in_review → complete
   ↓                                                                  ↓
 failed ←──────────────────────────────────────────────────────── failed
```

---

## Implementation Checklist

### Exercise 1: Manager Pattern (`coordinate_task_manager_pattern`)

- [ ] Get the Scrum Master agent
- [ ] Assign the task to Dev
- [ ] Dev implements the feature
- [ ] Monitor progress
- [ ] Coordinate the handoff to QA
- [ ] QA validates
- [ ] Return the result with the coordination log

### Exercise 2: Peer-to-Peer Pattern (`coordinate_task_peer_pattern`)

- [ ] Dev implements the feature
- [ ] Dev sends the review request to QA
- [ ] QA reviews the implementation
- [ ] Negotiation loop, capped at a few rounds: Dev responds, QA re-reviews, check approval
- [ ] Record the negotiation history
- [ ] Return the result; success means QA approved

### Exercise 3: Blackboard Pattern (`coordinate_task_blackboard_pattern`)

- [ ] Create a `TaskState` and post it
- [ ] Claim the task for Dev and check the result
- [ ] Dev updates to `in_progress`, implements, marks `ready_for_review` with the data
- [ ] Dev releases its claim
- [ ] Claim for QA, move to `in_review`
- [ ] QA reviews and marks `complete`
- [ ] Return the final state with the full history

---

## Key APIs at a Glance

### Manager Pattern APIs
```python
# Scrum Master
await scrum.assign_task(task, "dev")
await scrum.monitor_progress(task.id)
await scrum.coordinate_handoff(task.id, "dev", "qa", context)

# Workers
result = await dev.implement_feature(task)
result = await qa.test_feature(implementation)
```

### Peer-to-Peer APIs
```python
# Direct messaging
await dev.collaborate_with_qa(task.id, implementation)
await asyncio.sleep(1)  # Message propagation

# Agent actions
result = await dev.implement_feature(task)
review = await qa.review_code(implementation)
response = await dev.respond_to_feedback(feedback)
```

### Blackboard APIs
```python
# Task management
task_state = TaskState(task.id, desc, status="pending")
await blackboard.post_task(task_state)
success = await blackboard.claim_task(task.id, "dev")
await blackboard.update_task(task.id, "dev", status="in_progress")
released = await blackboard.release_task(task.id, "dev")
task = await blackboard.get_task(task.id)

# Helpers
await self._wait_for_claim(task.id, "dev", timeout=30)
await self._wait_for_status_change(task.id, "pending", "claimed")
```

---

## Testing Strategy

```bash
# Test one pattern at a time
pytest starter/tests/test_swarm_coordinator.py::TestManagerPattern -v
pytest starter/tests/test_swarm_coordinator.py::TestPeerPattern -v
pytest starter/tests/test_swarm_coordinator.py::TestBlackboardPattern -v

# Test all patterns
pytest starter/tests/test_swarm_coordinator.py -v

# Debug mode (see print statements)
pytest starter/tests/test_swarm_coordinator.py -v -s
```

---

For API signatures and return values, keep [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) open while you code. Each exercise guide has progressive hints. It also lists the real failure messages for the common mistakes.
