"""Decision Journal: architectural decisions as queryable memory.

Chapter 9, Section 9.4 (Knowledge Capture Patterns).

A decision record in a docs folder answers "what did we choose?" for a human
who goes looking. The Decision Journal pattern makes it answer "why, and what
did we rule out?" for an agent that never goes looking, because the record is
in the memory store the agent already queries.

This script loads the YAML record from Section 9.4, validates the fields that
make a record useful, and shows the two queries the pattern is for:

  What did we decide about X, and why?
  What decisions constrain component Y?

Requires PyYAML (pip install pyyaml). Runs offline:

    python decision_journal.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    raise SystemExit("This example needs PyYAML: pip install pyyaml")

RECORD_PATH = Path(__file__).parent / "decisions" / "postgresql-for-user-data.yaml"

# A record missing any of these cannot answer "why," which is the whole point.
REQUIRED_FIELDS = ("title", "context", "decision", "rationale")


@dataclass
class Option:
    name: str
    pros: list[str] = field(default_factory=list)
    cons: list[str] = field(default_factory=list)


@dataclass
class Decision:
    """One architectural decision, with the reasoning kept attached."""

    title: str
    context: str
    decision: str
    rationale: str
    date: str = ""
    options_considered: list[Option] = field(default_factory=list)
    consequences: list[str] = field(default_factory=list)
    affects: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, raw: dict) -> "Decision":
        missing = [f for f in REQUIRED_FIELDS if not raw.get(f)]
        if missing:
            raise ValueError(
                f"Decision record is missing required field(s): {', '.join(missing)}. "
                "A record without context and rationale is just a changelog entry."
            )
        return cls(
            title=raw["title"],
            context=raw["context"],
            decision=raw["decision"],
            rationale=raw["rationale"],
            date=str(raw.get("date", "")),
            options_considered=[
                Option(
                    name=o["name"],
                    pros=list(o.get("pros", [])),
                    cons=list(o.get("cons", [])),
                )
                for o in raw.get("options_considered", [])
            ],
            consequences=list(raw.get("consequences", [])),
            affects=list(raw.get("affects", [])),
        )

    def rejected_options(self) -> list[Option]:
        """The options that lost. Agents need these to avoid re-proposing them."""
        return [o for o in self.options_considered if o.name != self.decision]

    def as_memory_text(self) -> str:
        """Flatten to the single string a vector store indexes.

        Keep the rejected options in the text. Retrieval on "should we move to
        MongoDB?" should surface this record, and it only will if MongoDB
        appears in the indexed content.
        """
        rejected = ", ".join(o.name for o in self.rejected_options()) or "none recorded"
        return (
            f"Decision: {self.title}. "
            f"Chose {self.decision} over {rejected}. "
            f"Context: {self.context} "
            f"Rationale: {self.rationale} "
            f"Affects: {', '.join(self.affects) or 'unspecified'}."
        )


def load_decision(path: Path = RECORD_PATH) -> Decision:
    """Read one decision record from YAML."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return Decision.from_dict(raw["decision"])


def decisions_affecting(decisions: list[Decision], component: str) -> list[Decision]:
    """Vector search cannot answer this reliably; a relationship can.

    That gap is why the challenge lab (Section 9.7) puts decisions in a graph:
    `Decision -[:AFFECTS]-> Component` makes this a traversal instead of a
    hope that the component name happens to embed close to the query.
    """
    return [d for d in decisions if component in d.affects]


def main() -> None:
    decision = load_decision()

    print(f"{decision.title}  ({decision.date})\n")
    print(f"  chose:     {decision.decision}")
    print(f"  because:   {decision.rationale}")
    print(f"  affects:   {', '.join(decision.affects)}\n")

    print("  rejected, and why (so no agent re-proposes them):")
    for option in decision.rejected_options():
        print(f"    {option.name}")
        for con in option.cons:
            print(f"      against: {con}")
    print()

    print("  consequences the team accepted:")
    for consequence in decision.consequences:
        print(f"    {consequence}")
    print()

    print("  indexed as memory text:")
    print(f"    {decision.as_memory_text()}\n")

    hits = decisions_affecting([decision], "user-service")
    print(f'  decisions affecting "user-service": {len(hits)}')
    for hit in hits:
        print(f"    {hit.title}")


if __name__ == "__main__":
    main()
