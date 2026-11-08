"""Context window budgeting: allocate by task, place by position.

Chapter 9, Section 9.2 (Context Window as Working Memory).

Two ideas from the chapter, made executable:

  Budget allocation. Debugging, code review, architecture, and a quick fix want
  different splits between memories, code, and conversation history. Section
  9.2 gives the shape of each split as high/medium/low; this turns that into
  token counts you can act on.

  Positional placement. LLMs attend most strongly to the start and end of the
  window, least to the middle ("lost in the middle"). So instructions and
  constraints go first, the current request goes last, and retrieved reference
  material goes in the middle where weaker attention costs you least.

The point is not the exact numbers. It is that "what goes in the window" is a
decision with a budget, not a side effect of stuffing everything in.

Runs on Python 3.11+ with the standard library only:

    python context_budget.py
"""

from __future__ import annotations

from dataclasses import dataclass

# Share of the window kept free for the model's own output plus slack. Fill the
# window to the brim and the reply gets truncated.
RESERVED_FRACTION = 0.25

# Section 9.2's high/medium/low table, as weights. Weights are relative: they
# get normalized against the usable budget, so they do not need to sum to 1.
TASK_WEIGHTS: dict[str, dict[str, float]] = {
    "debugging":    {"memories": 4, "code": 4, "history": 1},
    "code_review":  {"memories": 2, "code": 7, "history": 1},
    "architecture": {"memories": 4, "code": 2, "history": 4},
    "quick_fix":    {"memories": 1, "code": 3, "history": 2},
}

# How much of the usable budget each task actually fills. A quick fix trades
# depth for speed and cost, so it does not fill the window just because it can.
TASK_FILL = {
    "debugging": 1.0,
    "code_review": 1.0,
    "architecture": 1.0,
    "quick_fix": 0.4,
}

# Where each content kind belongs, given the attention curve.
PLACEMENT = {
    "instructions": "beginning",  # System prompt, constraints, identity
    "memories":     "middle",     # Retrieved reference material
    "code":         "middle",     # Files under discussion
    "history":      "end",        # Recent turns
    "request":      "end",        # The actual ask, last
}


@dataclass
class Budget:
    """A token budget for one task type against one context window."""

    task: str
    window_tokens: int
    allocations: dict[str, int]

    @property
    def usable_tokens(self) -> int:
        return sum(self.allocations.values())

    def report(self) -> str:
        lines = [f"{self.task} (window {self.window_tokens:,} tokens)"]
        for kind, tokens in self.allocations.items():
            share = tokens / self.window_tokens * 100
            lines.append(
                f"    {kind:<10} {tokens:>7,} tokens  {share:>5.1f}%  "
                f"-> {PLACEMENT[kind]}"
            )
        unused = self.window_tokens - self.usable_tokens
        lines.append(f"    {'unused':<10} {unused:>7,} tokens  "
                     f"{unused / self.window_tokens * 100:>5.1f}%  "
                     "-> output, slack, headroom")
        return "\n".join(lines)


def plan_budget(task: str, window_tokens: int) -> Budget:
    """Split a context window across content kinds for one task type."""
    if task not in TASK_WEIGHTS:
        raise ValueError(
            f"Unknown task {task!r}. Known: {', '.join(sorted(TASK_WEIGHTS))}"
        )

    weights = TASK_WEIGHTS[task]
    usable = int(window_tokens * (1 - RESERVED_FRACTION) * TASK_FILL[task])
    total_weight = sum(weights.values())

    return Budget(
        task=task,
        window_tokens=window_tokens,
        allocations={
            kind: int(usable * weight / total_weight)
            for kind, weight in weights.items()
        },
    )


def assemble(budget: Budget) -> list[str]:
    """Order the sections so the important ones land where attention is highest.

    Retrieval quality is what the budget buys you. Ten memories that matter beat
    a hundred loosely related ones, and the ten only help if they are not buried
    behind a wall of low-value context.
    """
    order = {"beginning": 0, "middle": 1, "end": 2}
    sections = [
        ("instructions", None),
        *[(kind, budget.allocations[kind]) for kind in budget.allocations],
        ("request", None),
    ]
    sections.sort(key=lambda pair: order[PLACEMENT[pair[0]]])
    return [
        f"{kind}" + (f" (<= {tokens:,} tokens)" if tokens else "")
        for kind, tokens in sections
    ]


def main() -> None:
    window = 200_000

    print("Budget allocation by task type\n")
    for task in TASK_WEIGHTS:
        print("  " + plan_budget(task, window).report())
        print()

    print("Assembly order for a debugging task")
    print("  (start and end get the strongest attention, middle the weakest)\n")
    for position, section in enumerate(assemble(plan_budget("debugging", window)), 1):
        print(f"  {position}. {section}")

    print()
    print("A bigger window does not remove the problem. Attention quality still")
    print("degrades as the window fills, and every token you add costs money and")
    print("dilutes what matters. Selecting beats stuffing.")


if __name__ == "__main__":
    main()
