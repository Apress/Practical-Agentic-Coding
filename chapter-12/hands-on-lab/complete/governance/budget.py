"""
Resource budget enforcement for agent tool calls (reference solution).

Hard runtime limits that prevent unbounded resource consumption
(OWASP LLM10). The budget is enforced by the runtime, not by the agent.
An agent cannot override its own budget.

Reference: Chapter 12, Section 12.3.
"""

from __future__ import annotations

import time

from complete.governance.validators import ToolCall


class ResourceBudget:
    """Hard limits enforced by runtime, not by agent.

    Tracks consumption of tool calls, cost, and wall-clock time against
    configured maximums.
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
        """Return True only if every resource is still below its limit."""
        self.consumed["wall_clock"] = time.monotonic() - self.start
        return all(
            self.consumed[key] < self.limits[key] for key in self.limits
        )

    def consume(self, tool_call: ToolCall) -> None:
        """Record consumption of resources for this tool call."""
        self.consumed["tool_calls"] += 1
        self.consumed["cost_usd"] += tool_call.estimated_cost
