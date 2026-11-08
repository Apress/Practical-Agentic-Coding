# Exercise 4: Pattern Mining

**File to edit**: `starter/memory_core.py` (PatternMiner class)
**Verify**: inline snippet below (no test file; `demo.py` needs exercise 5 first)
**Reference**: Chapter 9, Section 9.6 (Phase 4)

## Goal

Implement `mine()` and `_extract_pattern()` in `PatternMiner`.

## Steps

### mine(agent_id)

1. Get all episodes: `self.memory.recall_all(agent_id=agent_id)`
2. Filter to type "episode": `[e for e in episodes if e.get("metadata", {}).get("type") == "episode"]`
3. Return `[]` if fewer than `self.config.consolidation_min_episodes`
4. Group by session_type
5. For groups with enough episodes, call `self._extract_pattern()`
6. Store patterns as semantic knowledge via `self.memory.remember()`
7. Return list of patterns

### _extract_pattern(session_type, episodes)

1. Filter to successful episodes (outcome == "success")
2. Collect first_check values
3. Use `Counter(first_checks).most_common(1)` to find most common
4. Confidence = count / total successful
5. Return `{"knowledge": "...", "confidence": ..., "episode_count": ...}`

## Verify

This exercise has no test file. The miner needs several captured sessions
before it produces anything. The snippet below creates three identical sessions
with `ApprenticeCapture` (exercise 2), then runs the miner. Run it from the
`hands-on-lab` directory, with ChromaDB up and your API key exported:

```bash
python - <<'PY'
import sys
sys.path.insert(0, "starter")
from config import DevMemoryConfig
from memory_core import DevMemory, PatternMiner
from capture import ApprenticeCapture

config = DevMemoryConfig(project_name="mining-check")
memory = DevMemory(config)
capture = ApprenticeCapture(memory, agent_id="debug-agent")

# Three identical successful sessions: the consolidation minimum
for _ in range(3):
    capture.start_session("debugging")
    capture.record_action("command", "docker logs api-service")
    capture.record_action("edit", "config/timeouts.yaml")
    capture.end_session("success")

patterns = PatternMiner(memory, config).mine(agent_id="debug-agent")
assert len(patterns) >= 1, "expected at least one mined pattern"
for p in patterns:
    print(f"{p['knowledge']} (confidence: {p['confidence']})")
PY
```

The `python - <<'PY'` wrapper is bash syntax. On Windows PowerShell, save the
lines between the two `PY` markers as `check_mining.py` in `hands-on-lab/`.
Then run `python check_mining.py`.

The miner works if it prints one line like `For debugging sessions, checking
'docker logs api-service' first leads to success (3 of 3 times) (confidence:
1.0)`.

`project_name="mining-check"` keeps these throwaway episodes in their own
ChromaDB collection, away from the demo's. They persist. Running the check
again reports `(6 of 6 times)`. This is expected. It is the same pattern over
more episodes.

Do not use `python starter/demo.py` as the check yet. It calls
`filter_by_trust()` from `trust.py`, which raises `NotImplementedError` until
exercise 5. If you run it anyway, look for the `Discovered 1 patterns:` lines
before the traceback. They show that exercise 4 works.
