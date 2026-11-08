"""Provenance and trust scoring for shared memories.

Chapter 9, Section 9.5 (Memory Provenance and Trust).

In a multi-agent system with shared memory, one agent's bad inference reaches
every other agent on the project. Trust scoring is the gate: score each memory
from its provenance, then filter before anything reaches agent context.

`calculate_trust_score` here is the function from Section 9.5, working against
a `Memory` object with real provenance fields. The lab's `trust.py` is the
dict-shaped variant that runs against what Mem0 returns
(hands-on-lab/starter/trust.py). Same factors, different input shape.

Runs on Python 3.11+ with the standard library only:

    python trust_scoring.py
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

# Memories scoring below this never enter agent context.
MIN_TRUST = 0.5


def now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Memory:
    """A memory plus the provenance that trust scoring reads."""

    content: str
    base_confidence: float
    source_type: str = "agent"      # "agent" or "human"
    validation_count: int = 0       # Other agents that confirmed it
    contradiction_count: int = 0    # Times it was contradicted
    last_validated: datetime = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.last_validated is None:
            self.last_validated = now()


def calculate_trust_score(memory: Memory) -> float:
    """Score memory trustworthiness based on provenance.

    Matches Chapter 9, Section 9.5. Four factors:

      Boost for a human author. A developer who wrote something down was more
      deliberate than an agent that inferred it in passing.
      Boost per independent validation, capped by the multiplier staying small.
      Decay with age since last validation, floored at 0.3 so an old memory
      degrades rather than disappearing.
      Halve on any contradiction. One contradiction is enough to make a memory
      unsafe to act on without a human looking at it.
    """
    score = memory.base_confidence

    # Boost: created by human developer
    if memory.source_type == "human":
        score *= 1.2

    # Boost: validated by multiple agents
    score *= (1 + 0.1 * memory.validation_count)

    # Decay: old without reinforcement (Section 9.2 pattern)
    days_since_validated = (now() - memory.last_validated).days
    score *= max(0.3, 1.0 - (days_since_validated / 365))

    # Penalty: has been contradicted
    if memory.contradiction_count > 0:
        score *= 0.5

    return min(score, 1.0)


def filter_by_trust(
    memories: list[Memory], min_trust: float = MIN_TRUST
) -> tuple[list[Memory], list[Memory]]:
    """Split memories into what an agent may read and what it may not.

    Returns (admitted, blocked). Keep the blocked list: "why did the agent not
    know that?" is a question you will be asked, and the answer lives here.
    """
    scored = [(m, calculate_trust_score(m)) for m in memories]
    admitted = [m for m, s in sorted(scored, key=lambda p: p[1], reverse=True)
                if s >= min_trust]
    blocked = [m for m, s in scored if s < min_trust]
    return admitted, blocked


def main() -> None:
    memories = [
        Memory(
            "Payment retries need an idempotency key",
            base_confidence=0.8, source_type="human", validation_count=4,
        ),
        Memory(
            "Mined pattern: timeout investigations start at the container logs",
            base_confidence=0.75, validation_count=2,
        ),
        Memory(
            "The staging database accepts writes from any service",
            base_confidence=0.7, contradiction_count=1,
        ),
        Memory(
            "Deploys go out on Thursdays",
            base_confidence=0.9,
            last_validated=now() - timedelta(days=400),
        ),
        Memory(
            "Guessing the cache TTL is 60 seconds",
            base_confidence=0.35,
        ),
    ]

    print(f"Trust scores (admission threshold {MIN_TRUST})\n")
    for memory in memories:
        score = calculate_trust_score(memory)
        verdict = "admit " if score >= MIN_TRUST else "block "
        age = (now() - memory.last_validated).days
        print(f"  [{score:.2f}] {verdict} {memory.content}")
        print(
            f"           base {memory.base_confidence:.2f}, "
            f"source {memory.source_type}, "
            f"validations {memory.validation_count}, "
            f"contradictions {memory.contradiction_count}, "
            f"age {age}d"
        )

    admitted, blocked = filter_by_trust(memories)
    print(f"\n{len(admitted)} memories reach agent context, {len(blocked)} blocked.")
    print("Blocked memories are logged, not deleted. A contradicted memory is a")
    print("signal that two sources disagree, which a human should settle.")


if __name__ == "__main__":
    main()
