"""
Execution rail that intercepts every agent tool call.

This module implements the four-step intercept pattern from
Chapter 12, Section 12.3: budget check, validation, approval
gate, execution. Every tool call passes through all four steps.

The order matters: budget checks are cheapest and fail first.
Human approval is most expensive and triggers only after automated
checks pass.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from starter.governance.validators import (
    ToolCall,
    ToolResult,
    ValidatorPipeline,
)
from starter.governance.budget import ResourceBudget


# ---------------------------------------------------------------------------
# Approval gate (given, simulated)
# ---------------------------------------------------------------------------

class ApprovalGate:
    """Simulated human approval gate.

    In production, this would integrate with Slack, Teams, or a
    custom approval UI. For the lab, it auto-approves unless the
    tool name is in the require_approval list.
    """

    def __init__(
        self,
        require_approval: list[str] | None = None,
        auto_approve: bool = True,
    ) -> None:
        self.require_approval = require_approval or []
        self.auto_approve = auto_approve

    def requires_approval(self, tool_call: ToolCall) -> bool:
        """Check if this tool call needs human approval."""
        return tool_call.tool_name in self.require_approval

    async def request(self, tool_call: ToolCall) -> bool:
        """Request human approval. Returns True if approved."""
        if self.auto_approve:
            return True
        return False


# ---------------------------------------------------------------------------
# ExecutionRail (starter with TODO)
# ---------------------------------------------------------------------------

class ExecutionRail:
    """Intercepts tool calls and enforces constraints before execution.

    The intercept method runs four checks in order:
      1. Budget check (cheapest, fails first)
      2. Tool-specific validators
      3. Human approval gate (most expensive, last)
      4. Execute and record consumption
    """

    def __init__(
        self,
        budget: ResourceBudget,
        approval_gate: ApprovalGate,
    ) -> None:
        self.budget = budget
        self.approval_gate = approval_gate
        self.validators: dict[str, ValidatorPipeline] = {}

    def register_validators(
        self, tool_name: str, pipeline: ValidatorPipeline
    ) -> None:
        """Register a validator pipeline for a specific tool."""
        self.validators[tool_name] = pipeline

    async def intercept(self, tool_call: ToolCall) -> ToolResult:
        """Intercept a tool call and enforce all constraints.

        Follow this exact order:

        Step 1 - Budget check:
          if not self.budget.can_afford(tool_call):
              return ToolResult(blocked=True, reason="Budget exhausted")

        Step 2 - Run tool-specific validators:
          Look up the pipeline in self.validators using
          tool_call.tool_name. If a pipeline exists, call
          await pipeline.validate(tool_call). If the result is
          blocked, return ToolResult(blocked=True, reason=result.reason).

        Step 3 - Human approval:
          if self.approval_gate.requires_approval(tool_call):
              approved = await self.approval_gate.request(tool_call)
              if not approved:
                  return ToolResult(blocked=True, reason="Human denied")

        Step 4 - Execute and record:
          self.budget.consume(tool_call)
          return await tool_call.execute()

        TODO: Implement the four-step intercept pattern.
        """
        # TODO: Implement the four-step intercept pattern
        raise NotImplementedError("TODO: implement intercept()")
