"""
Trust scoring for shared memories.

Prevents context poisoning by filtering low-trust memories
before they reach agent context.

Reference: Chapter 9, Section 9.6 (Phase 5)
"""
from datetime import datetime, timezone


def _memory_created_at(memory: dict) -> str | None:
    """Find the creation timestamp in a Mem0 result.

    Mem0 returns `created_at` at the top level of each memory dict, not inside
    `metadata`, so check both. Provided for you: it is plumbing, not the
    exercise.
    """
    return memory.get("created_at") or memory.get("metadata", {}).get("created_at")


def _parse_timestamp(value: str) -> datetime | None:
    """Parse an ISO timestamp and return it timezone-aware in UTC.

    Mem0 writes timezone-aware ISO strings ("...+00:00"). Comparing one of those
    against a naive datetime raises TypeError, so normalize here and keep
    everything aware. Provided for you.
    """
    try:
        parsed = datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def calculate_trust(memory: dict, now: datetime = None) -> float:
    """Score memory trustworthiness based on provenance.

    TODO (Exercise 5): Implement this function.

    Factors to implement:
    1. Start with base confidence from metadata (default 0.5)
    2. Boost for pattern-mined knowledge: multiply by (1 + 0.1 * min(episode_count, 10))
       when metadata.source == "pattern_mining"
    3. Boost for human-contributed knowledge: multiply by 1.2
       when metadata.contributed_by_human is True
    4. Decay for age: multiply by max(0.3, 1.0 - (days_old / 365)).
       Use _memory_created_at(memory) to find the timestamp and
       _parse_timestamp() to parse it; both are provided above. Skip the decay
       when there is no usable timestamp.
    5. Cap at 1.0

    Args:
        memory: Memory dict as returned by Mem0.
        now: Current time, timezone-aware UTC. Defaults to
             datetime.now(timezone.utc). Tests pass a fixed value.

    Returns:
        float: Trust score between 0.0 and 1.0.
    """
    now = now or datetime.now(timezone.utc)
    # TODO: Implement trust scoring
    raise NotImplementedError("TODO: Implement calculate_trust() in Exercise 5")


def filter_by_trust(
    memories: list[dict], min_trust: float = 0.5
) -> list[dict]:
    """Filter memories below trust threshold.

    TODO (Exercise 5): Implement this function.

    Steps:
    1. For each memory, calculate trust score using calculate_trust()
    2. Add "trust_score" key to memory dict
    3. Keep only memories with trust >= min_trust
    4. Sort by trust_score descending
    5. Return filtered and sorted list

    Args:
        memories: List of memory dicts.
        min_trust: Minimum trust threshold.

    Returns:
        list[dict]: Filtered memories sorted by trust score.
    """
    # TODO: Implement trust filtering
    raise NotImplementedError("TODO: Implement filter_by_trust() in Exercise 5")
