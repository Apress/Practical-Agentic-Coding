# Comparing your three implementations

Read this after all three exercises pass. Use it to measure what your three
methods did with the same task.

When to use each pattern and why: Chapter 10, Section 10.2 (with Table 10.1)
for hierarchical coordination, Section 10.3 for direct peer messaging at
handoffs, and Section 10.6 for the blackboard.

## Run one task through all three

Both commands below run your three methods on one task. Run them from `hands-on-lab/`:

```bash
# Model calls mocked, Redis up: prints which patterns completed
pytest starter/tests/test_integration.py::TestPatternComparison -v -s

# Real model calls with your API key: Example 4 runs one task through each pattern
python example_usage.py
```

## Count model calls and messages offline

1. Start Redis.
2. Save this script as `compare_patterns.py` in `hands-on-lab/`.
3. Run `python compare_patterns.py`.

The script mocks every model call, so it costs nothing:

```python
import asyncio
from unittest.mock import AsyncMock

from starter.swarm_coordinator import SwarmCoordinator, CoordinationPattern, Task

# Model calls are mocked below, so no API key is used and nothing is billed.
CONFIG = {"anthropic_api_key": "unused-calls-are-mocked",
          "redis_host": "localhost", "redis_port": 6379, "redis_db": 1}


async def run(pattern):
    coordinator = SwarmCoordinator(CONFIG, pattern)
    await coordinator.setup()
    await coordinator.blackboard.clear()
    await coordinator.message_bus.clear_history()
    for agent in coordinator.agents.values():
        agent.query_claude = AsyncMock(return_value="Quality score: 9/10. Approved.")

    task = Task(id="compare_001", description="Add rate limiting middleware")
    await coordinator.execute_task(task)
    await asyncio.sleep(1)  # let messages on the bus land

    calls = {name: a.query_claude.call_count for name, a in coordinator.agents.items()}
    sent = {name: len(await coordinator.message_bus.get_message_history(name))
            for name in coordinator.agents}
    await coordinator.blackboard.clear()
    await coordinator.cleanup()
    return calls, sent


async def main():
    for pattern in CoordinationPattern:
        calls, sent = await run(pattern)
        print(f"{pattern.value:<10} model calls {calls}  messages sent {sent}")


asyncio.run(main())
```

Your numbers depend on your implementation. If you followed the exercise
hints, expect this:

- The peer run shows two model calls each for dev and QA.
- The other two runs show one call each.

Your coordinator does not make the extra pair. The `review_request` message
triggers QA's own handler. That handler reviews the work and sends
`qa_feedback`. Then dev's handler answers that feedback. With a real key, those
calls are billed too.

## What to compare

| Question | Where to look |
|----------|---------------|
| How many model calls did each pattern make? | The `calls` line above, or the usage view in the Claude Console after `example_usage.py` |
| How many messages went over the bus? | The `sent` line above. `get_message_history()` returns what each agent sent, newest first |
| How many state changes did the task go through? | `len(result["history"])` for the blackboard; your `coordination_log` and `negotiation_history` for the other two |
| How long did each take? | `duration_seconds`, if your result includes it (the hint shapes do) |
| If a run failed, where would you look first? | The coordination log (manager), the negotiation history (peer), the task history on the board (blackboard) |

## Questions to answer from your results

- Which result lets you reconstruct what happened without reading the logs?
- Which pattern would you change first if a fourth agent (security, say) joined?
- Where did model calls happen that your coordinator did not ask for?

For extensions, see Next steps in the [lab README](../README.md). They include
a fourth agent, two patterns combined in one workflow, and per-step metrics.
