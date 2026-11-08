# Exercise 5: Trust Scoring

**File to edit**: `starter/trust.py`
**Verify**: inline snippet below, then `python starter/demo.py` (no test file)
**Reference**: Chapter 9, Section 9.6 (Phase 5)

## Goal

Implement `calculate_trust()` and `filter_by_trust()`.

Why shared memories need a trust gate: Chapter 9, Section 9.5.

## Steps

### calculate_trust(memory, now)

1. Get base score from `metadata.get("confidence", 0.5)`
2. If `metadata.source == "pattern_mining"`: multiply by `(1 + 0.1 * min(episode_count, 10))`
3. If `metadata.contributed_by_human` is True: multiply by 1.2
4. Apply age decay: `max(0.3, 1.0 - (days_old / 365))`
5. Cap at 1.0

For step 4, use the two helpers already in the file:

```python
created = _memory_created_at(memory)      # checks top level and metadata
created_dt = _parse_timestamp(created) if created else None
if created_dt is not None:
    days_old = (now - created_dt).days
    score *= max(0.3, 1.0 - (days_old / 365))
```

The helpers handle two details that would otherwise be bugs:

- Mem0 returns `created_at` at the top level of the memory dict, not inside
  `metadata`. If you read only `metadata`, you find nothing, and the decay
  never applies.
- Mem0's timestamps are timezone-aware. Subtracting one from a naive
  `datetime.utcnow()` raises `TypeError`. Keep everything timezone-aware, in
  UTC.

### filter_by_trust(memories, min_trust)

1. Calculate trust for each memory
2. Add `trust_score` to each memory dict
3. Drop memories below `min_trust`
4. Sort by `trust_score` descending

## Verify

This exercise has no test file. Trust scoring needs stored memories to
filter. First, check the scoring logic directly. Run this from the
`hands-on-lab` directory:

```bash
python - <<'PY'
import sys
sys.path.insert(0, "starter")
from datetime import datetime, timezone
from trust import calculate_trust

now = datetime(2026, 1, 1, tzinfo=timezone.utc)

# High trust: pattern-mined, backed by five episodes
m1 = {"metadata": {"confidence": 0.9, "source": "pattern_mining", "episode_count": 5}}
assert calculate_trust(m1, now=now) > 0.9, calculate_trust(m1, now=now)

# Low trust: two years stale. created_at sits at the top level, as Mem0 returns it.
m2 = {"created_at": "2024-01-01T00:00:00+00:00", "metadata": {"confidence": 0.5}}
assert calculate_trust(m2, now=now) < 0.5, calculate_trust(m2, now=now)

print("trust scoring OK")
PY
```

It prints `trust scoring OK`. The `python - <<'PY'` wrapper is bash syntax. On
Windows PowerShell, save the lines between the two `PY` markers as
`check_trust.py` in `hands-on-lab/`. Then run `python check_trust.py`.

Then run the full demo. It runs `filter_by_trust()` against real Mem0 results:

```bash
python starter/demo.py
```

To read a working version without Mem0, see
`../../code-examples/trust_scoring.py`. It has the same scoring logic over
plain dataclasses.
