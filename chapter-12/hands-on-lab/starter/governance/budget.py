"""
Resource budget enforcement for agent tool calls.

This module implements hard runtime limits that prevent unbounded
resource consumption (OWASP LLM10). The budget is enforced by the
runtime, not by the agent. An agent cannot override its own budget.

Reference: Chapter 12, Section 12.3.
"""

from __future__ import annotations

import time

from starter.governance.validators import ToolCall


class ResourceBudget:
    """Hard limits enforced by runtime, not by agent.

    Tracks consumption of tool calls, cost, and wall-clock time
    against configured maximums.
    """

    def __init__(
        self,
        max_tool_calls: int = 50,
        max_cost_usd: float = 5.0,
        max_wall_clock_seconds: int = 1800,
    ) -> None:
        self.limits: dict[str, int | float] = {
            "tool_calls": max_tool_calls,
            "cost_usd": max_cost_usd,
            "wall_clock": max_wall_clock_seconds,
        }
        self.consumed: dict[str, int | float] = {
            "tool_calls": 0,
            "cost_usd": 0.0,
            "wall_clock": 0,
        }
        self.start = time.monotonic()

    def can_afford(self, tool_call: ToolCall) -> bool:
        """Check whether the budget allows another tool invocation.

        First refresh the wall-clock reading:
        self.consumed["wall_clock"] = time.monotonic() - self.start
        Then return True if ALL consumed values are still below their
        corresponding limits. Return False if any resource is
        exhausted.

        TODO: Update consumed["wall_clock"], then compare
        self.consumed[k] < self.limits[k] for every key in
        self.limits. Return True only if all comparisons pass.
        """
        # TODO: Implement budget check
        raise NotImplementedError("TODO: implement can_afford()")

    def consume(self, tool_call: ToolCall) -> None:
        """Record consumption of resources for this tool call.

        Update self.consumed:
          - Increment "tool_calls" by 1
          - Add tool_call.estimated_cost to "cost_usd"

        TODO: Implement resource consumption tracking.
        """
        # TODO: Implement consumption tracking
        raise NotImplementedError("TODO: implement consume()")
