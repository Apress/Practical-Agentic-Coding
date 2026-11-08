# Exercises: the three coordination patterns

Do the three exercises in order. In each one, you implement one method in
`../starter/swarm_coordinator.py`. Then you run the tests that already exist
for it.

| # | Exercise | Pattern | Time |
|---|----------|---------|------|
| 1 | [exercise-1-manager-pattern.md](./exercise-1-manager-pattern.md) | Manager (hierarchical) | 45-60 min |
| 2 | [exercise-2-peer-pattern.md](./exercise-2-peer-pattern.md) | Peer-to-peer | 45-60 min |
| 3 | [exercise-3-blackboard-pattern.md](./exercise-3-blackboard-pattern.md) | Blackboard (shared state) | 60-75 min |

Total: 2.5 to 3.5 hours.

## Before you start

1. Run `python verify_setup.py` from `hands-on-lab/`. Check that setup passes.
2. Install dependencies: `pip install -r requirements.txt`.
3. Start Redis: run `docker compose up -d` from `hands-on-lab/`. Check it with
   `docker compose exec redis redis-cli ping`. It prints `PONG`.
4. Check that `.env` exists and has your `ANTHROPIC_API_KEY`.

Both test suites mock the Claude API, so running them costs nothing. Only
`example_usage.py` makes real API calls.

## Reference material

| File | What it's for |
|------|---------------|
| [VISUAL_OVERVIEW.md](./VISUAL_OVERVIEW.md) | Diagrams, step flows, and a checklist for each of the three methods. Read this first. |
| [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) | API signatures for the agents, message bus, and blackboard. Keep it open while you code. |
| [PATTERN_COMPARISON.md](./PATTERN_COMPARISON.md) | How to measure and compare your three implementations. Use it after you finish all three. |

Each exercise also has:

- progressive hints
- common pitfalls, as wrong/right code pairs
- debugging tips
- a success checklist

Try something yourself before you open the hints.

## Working loop

Run these from `hands-on-lab/`, not from this directory:

```bash
# Edit the coordinator
vim starter/swarm_coordinator.py

# Exercise 1
pytest starter/tests/test_swarm_coordinator.py::TestManagerPattern -v

# Exercise 2
pytest starter/tests/test_swarm_coordinator.py::TestPeerPattern -v

# Exercise 3
pytest starter/tests/test_swarm_coordinator.py::TestBlackboardPattern -v

# Everything, once all three are done
pytest starter/tests/test_swarm_coordinator.py -v

# Integration tests (need Redis running)
pytest starter/tests/test_integration.py -v -m integration
```

The unit tests mock both Redis and the Claude API. They run fast and offline.
The integration tests use real Redis, so Redis must be running. They still mock
the model calls.

When all three pass, run `python example_usage.py` from `hands-on-lab/`. It runs
the patterns end to end on sample tasks.

## What each exercise builds

**Exercise 1, Manager.** The Scrum Master assigns work. It monitors progress.
It coordinates the handoff to QA. Everything goes through this one agent.

**Exercise 2, Peer-to-peer.** Dev and QA talk to each other over the message
bus. They repeat until QA approves. A round cap stops the loop from running
forever.

**Exercise 3, Blackboard.** You post the task to the board. The task is
claimed and updated. It moves from dev to QA through atomic claims and
releases. The task history keeps every change.

When to use each pattern and why: Chapter 10, Sections 10.2, 10.3, and 10.6.

## Common failure modes

**Exercise 1**
- Missing `await` on an async call
- Dev and QA talking directly. In this pattern, everything goes through the Scrum Master
- Returning a partial result instead of every coordination step

**Exercise 2**
- A negotiation loop with no `max_rounds` cap
- Reading a message before it arrives. Add a short `await asyncio.sleep(...)` after sending
- Treating "hit max rounds" as success. Success means QA approved
- Not recording the negotiation history in the result

**Exercise 3**
- Waiting for an agent to claim the task on its own. The agents have no loop,
  so your coordinator makes each claim
- Not checking whether `claim_task()` returned `True` before proceeding
- Polling with no timeout, so a stuck task hangs the run
- Updating a task from an agent that does not hold the claim
- Skipping `release_task()` after dev marks `ready_for_review`. QA's claim is rejected while dev still holds the task
- Forgetting to pass results through `update_task(..., data={...})`

## Where to look when stuck

1. The error message, read carefully
2. `QUICK_REFERENCE.md` for the exact API signature
3. The exercise's hints section, one level at a time
4. The Common Pitfalls section in the exercise
5. `logger.info()` calls at the points where you are unsure what state you have
6. Redis Commander at http://localhost:8081 (admin/admin) to see messages and blackboard state

## Found a problem?

Open an issue on the companion repository
(github.com/Apress/Practical-Agentic-Coding). Describe what you expected and
what happened.
