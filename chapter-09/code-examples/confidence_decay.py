"""Strategic forgetting: confidence decay, reinforcement, consolidation.

Chapter 9, Section 9.2 (Memory Span and Cognitive Efficiency).

The chapter argues that strategic forgetting is decay with purpose, not
deletion. A memory starts at full confidence, loses confidence when nothing
reinforces it, drops out of retrieval results once it falls below the
threshold, and jumps back up when something confirms it.

This script makes that timeline concrete. Run it and you get the same
progression the chapter prints as a sketch, plus the consolidation step that
folds three similar episodes into one semantic fact.

Runs on Python 3.11+ with the standard library only:

    python confidence_decay.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

# Confidence below this is filtered out of retrieval results.
RETRIEVAL_THRESHOLD = 0.5

# Days for an unreinforced memory to lose half its confidence. Exponential
# decay, so confidence falls fast at first and then flattens, which tracks the
# chapter's sketch (about 0.7 at 30 days, filtered out by day 90). Tune this
# per memory type: procedural knowledge decays slower than a failed
# exploration path.
HALF_LIFE_DAYS = 60.0

# Confidence a memory returns to when something confirms it. Not 1.0: a
# reinforced memory is well supported, not beyond question.
REINFORCED_CONFIDENCE = 0.95


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Memory:
    """One stored memory with a decaying confidence score."""

    content: str
    memory_type: str = "semantic"  # "episodic", "semantic", or "procedural"
    base_confidence: float = 1.0
    created: datetime = field(default_factory=_now)
    last_reinforced: datetime = field(default_factory=_now)

    def confidence_at(self, when: datetime) -> float:
        """Confidence on a given date, after decay since last reinforcement."""
        days = max(0, (when - self.last_reinforced).days)
        decayed = self.base_confidence * 0.5 ** (days / HALF_LIFE_DAYS)
        return round(max(0.0, decayed), 2)

    def is_retrievable_at(self, when: datetime) -> bool:
        """Whether this memory still clears the retrieval threshold."""
        return self.confidence_at(when) >= RETRIEVAL_THRESHOLD

    def reinforce(self, when: datetime) -> None:
        """Something confirmed this memory: reset the decay clock."""
        self.base_confidence = REINFORCED_CONFIDENCE
        self.last_reinforced = when


def consolidate(episodes: list[Memory], min_episodes: int = 3) -> Memory | None:
    """Fold repeated episodes into one semantic memory.

    Section 9.2's example: three "fixed null pointer in <module>" episodes
    become "null pointers often indicate uninitialized service dependencies."
    Consolidation here keys on the shared leading phrase, which is enough to
    show the mechanic. The lab's PatternMiner does the real version against
    Mem0, grouping by session type and success outcome
    (hands-on-lab/starter/memory_core.py).
    """
    if len(episodes) < min_episodes:
        return None

    shared = _shared_prefix([e.content for e in episodes])
    if not shared:
        return None

    variants = [
        _strip_prefix(e.content, shared) for e in episodes
    ]
    return Memory(
        content=(
            f'"{shared}" recurred in {len(episodes)} places '
            f"({', '.join(v for v in variants if v)}). "
            "Look for one shared root cause, not three separate bugs."
        ),
        memory_type="semantic",
        base_confidence=min(1.0, 0.6 + 0.1 * len(episodes)),
    )


def _shared_prefix(contents: list[str]) -> str:
    """Longest run of leading words common to every string."""
    word_lists = [c.split() for c in contents]
    shared: list[str] = []
    for words in zip(*word_lists):
        if len({w.lower() for w in words}) != 1:
            break
        shared.append(words[0])
    return " ".join(shared)


def _strip_prefix(content: str, prefix: str) -> str:
    """The part of a memory that differs from the shared prefix."""
    return content[len(prefix):].strip() if content.startswith(prefix) else content


def main() -> None:
    day_one = _now()
    fact = Memory("Team uses pytest for testing")

    print("Confidence decay for a semantic fact")
    print(f"  memory: {fact.content!r}")
    print(f"  retrieval threshold: {RETRIEVAL_THRESHOLD}\n")

    for day in (1, 30, 90):
        when = day_one + timedelta(days=day - 1)
        score = fact.confidence_at(when)
        state = "in results" if fact.is_retrievable_at(when) else "filtered out"
        print(f"  day {day:>3}: confidence {score:.2f}  ({state})")

    day_91 = day_one + timedelta(days=90)
    fact.reinforce(day_91)
    print(
        f"  day  91: confidence {fact.confidence_at(day_91):.2f}  "
        "(reinforced, a developer confirmed pytest)\n"
    )

    print("Consolidation of repeated episodes")
    episodes = [
        Memory("Fixed null pointer in auth module", memory_type="episodic"),
        Memory("Fixed null pointer in payment module", memory_type="episodic"),
        Memory("Fixed null pointer in notification module", memory_type="episodic"),
    ]
    for episode in episodes:
        print(f"  episodic: {episode.content}")

    semantic = consolidate(episodes)
    if semantic is None:
        print("  no pattern: not enough shared structure")
        return

    print(f"  semantic: {semantic.content}")
    print(f"  confidence: {semantic.base_confidence:.2f}")


if __name__ == "__main__":
    main()
