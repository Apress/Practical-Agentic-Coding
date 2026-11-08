"""Memory scopes: write-local, promote-on-confidence, resolve conflicts.

Chapter 9, Section 9.5 (Memory Architecture for Autonomous Development).

The chapter defines three scopes (agent-level, shared project, organizational)
and three rules that move knowledge between them:

  1. Write-local, promote-on-confidence. Facts start in the agent's own scope
     and widen only when the evidence justifies it.
  2. Read-through with scoping. A query reads all three scopes but weights the
     narrowest one highest.
  3. Conflict resolution by scope hierarchy. An organizational policy beats a
     project convention, but an agent-level exception raises a flag for a human
     instead of being silently dropped.

`MemoryPromotion` here matches the class in Section 9.5. The rest is the
surrounding machinery the chapter describes in prose, made runnable so you can
change a threshold and watch what promotes.

Runs on Python 3.11+ with the standard library only:

    python memory_promotion.py
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Scopes, narrowest first. Index order is the read priority and the conflict
# hierarchy: a later scope overrides an earlier one on policy conflicts.
AGENT, PROJECT, ORGANIZATION = "agent", "project", "organization"
SCOPES = (AGENT, PROJECT, ORGANIZATION)

# Read weight per scope, from the table in Section 9.5: your own notes first,
# then the project knowledge base, then the company one.
READ_WEIGHTS = {AGENT: 1.0, PROJECT: 0.8, ORGANIZATION: 0.5}


def _plural(count: int, noun: str) -> str:
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


@dataclass
class Fact:
    """A stored fact with the provenance that promotion decisions need."""

    content: str
    confidence: float
    source_count: int = 1           # Episodes backing this fact
    cross_project_count: int = 1    # Projects where it has held
    scope: str = AGENT
    is_policy: bool = False         # Policies win conflicts; observations do not
    tags: set[str] = field(default_factory=set)


class MemoryPromotion:
    """Promotes knowledge across memory scopes based on confidence.

    Matches the class in Chapter 9, Section 9.5. Two gates, and both halves of
    each gate must hold: a confident one-off does not promote, and neither does
    a weak pattern seen everywhere.
    """

    def __init__(self, thresholds: dict):
        self.thresholds = thresholds  # e.g. {"project": 0.7, "org": 0.9}

    def evaluate_promotion(self, fact: Fact, current_scope: str) -> str:
        """Determine if a fact should be promoted to a wider scope."""

        if current_scope == AGENT:
            if (fact.confidence >= self.thresholds["project"]
                    and fact.source_count >= 3):
                return PROJECT

        if current_scope == PROJECT:
            if (fact.confidence >= self.thresholds["org"]
                    and fact.cross_project_count >= 2):
                return ORGANIZATION

        return current_scope  # No promotion

    def explain(self, fact: Fact) -> str:
        """One line saying what happened to this fact and why."""
        target = self.evaluate_promotion(fact, fact.scope)
        if target == fact.scope:
            return f"stays at {fact.scope}: {self._blocking_reason(fact)}"
        if target == PROJECT:
            return (
                f"{fact.scope} -> {target}: confidence {fact.confidence:.2f}, "
                f"backed by {_plural(fact.source_count, 'episode')}"
            )
        return (
            f"{fact.scope} -> {target}: confidence {fact.confidence:.2f}, "
            f"held in {_plural(fact.cross_project_count, 'project')}"
        )

    def _blocking_reason(self, fact: Fact) -> str:
        if fact.scope == ORGANIZATION:
            return "already the widest scope"
        if fact.scope == AGENT:
            if fact.confidence < self.thresholds["project"]:
                return (
                    f"confidence {fact.confidence:.2f} below "
                    f"{self.thresholds['project']}"
                )
            return f"only {_plural(fact.source_count, 'episode')}, needs 3"
        if fact.confidence < self.thresholds["org"]:
            return (
                f"confidence {fact.confidence:.2f} below "
                f"{self.thresholds['org']}"
            )
        return f"seen in {_plural(fact.cross_project_count, 'project')}, needs 2"


def read_through(store: list[Fact], tag: str, agent_scope_only: bool = False) -> list[Fact]:
    """Read all scopes for one topic, ranked by confidence times read weight.

    This is the read-through pattern from Section 9.5. The narrow scope is not
    searched *instead of* the wide one, it is searched *first*, and its results
    outrank the wide ones at equal confidence.
    """
    candidates = [f for f in store if tag in f.tags]
    if agent_scope_only:
        candidates = [f for f in candidates if f.scope == AGENT]
    return sorted(
        candidates,
        key=lambda f: f.confidence * READ_WEIGHTS[f.scope],
        reverse=True,
    )


def resolve_conflict(facts: list[Fact]) -> tuple[Fact, list[Fact]]:
    """Pick the winner among contradicting facts and flag what needs review.

    Scope hierarchy decides: the widest policy wins. A narrower fact that
    contradicts a wider policy is returned as a flag, not discarded, because it
    may be a legitimate exception a human needs to sign off on.
    """
    policies = [f for f in facts if f.is_policy]
    ranked = sorted(
        policies or facts,
        key=lambda f: SCOPES.index(f.scope),
        reverse=True,
    )
    winner = ranked[0]
    flagged = [f for f in facts if f is not winner]
    return winner, flagged


def main() -> None:
    promotion = MemoryPromotion({"project": 0.7, "org": 0.9})

    candidates = [
        Fact(
            "Timeout investigations start with the container logs",
            confidence=0.86, source_count=5, scope=AGENT, tags={"timeout"},
        ),
        Fact(
            "This one flaky test fails on my machine only",
            confidence=0.91, source_count=1, scope=AGENT, tags={"tests"},
        ),
        Fact(
            "Null pointers on startup mean missing dependency injection",
            confidence=0.94, source_count=11, cross_project_count=4,
            scope=PROJECT, tags={"nullpointer"},
        ),
        Fact(
            "We name feature branches feature/<ticket>",
            confidence=0.97, source_count=30, cross_project_count=1,
            scope=PROJECT, tags={"branching"},
        ),
    ]

    print("Promotion decisions (thresholds: project 0.7, org 0.9)")
    for fact in candidates:
        print(f"  {fact.content}")
        print(f"    {promotion.explain(fact)}")
    print()

    store = [
        Fact("Retry with backoff, 3 attempts, 100ms base",
             confidence=0.80, scope=PROJECT, tags={"retry"}),
        Fact("Retries must carry an idempotency key",
             confidence=0.95, scope=ORGANIZATION, tags={"retry"}),
        Fact("The billing client retries internally, do not wrap it",
             confidence=0.70, scope=AGENT, tags={"retry"}),
    ]

    print("Read-through for 'retry' (score = confidence x scope weight)")
    for fact in read_through(store, "retry"):
        score = fact.confidence * READ_WEIGHTS[fact.scope]
        print(f"  [{score:.2f}] ({fact.scope}) {fact.content}")
    print()

    conflict = [
        Fact("Never store credentials in environment variables",
             confidence=0.99, scope=ORGANIZATION, is_policy=True, tags={"secrets"}),
        Fact("We keep secrets in .env files",
             confidence=0.85, scope=PROJECT, is_policy=True, tags={"secrets"}),
        Fact("legacy-report-service needs env-var credentials to boot",
             confidence=0.90, scope=AGENT, tags={"secrets"}),
    ]

    winner, flagged = resolve_conflict(conflict)
    print("Conflict resolution for 'secrets'")
    print(f"  applies:  ({winner.scope}) {winner.content}")
    for fact in flagged:
        print(f"  flagged:  ({fact.scope}) {fact.content}")
    print("  A flagged narrower fact goes to a human, not to the bin. It may be")
    print("  a real exception, and silently dropping it is how agents lose trust.")


if __name__ == "__main__":
    main()
