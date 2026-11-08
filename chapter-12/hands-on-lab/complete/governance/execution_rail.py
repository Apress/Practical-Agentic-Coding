"""
Execution rail that intercepts every agent tool call (reference solution).

Implements the four-step intercept pattern from Chapter 12, Section 12.3:
budget check, validation, approval gate, execution. Every tool call passes
through all four steps.

The order matters: budget checks are cheapest and fail first. Human
approval is most expensive and triggers only after automated checks pass.
"""

from __future__ import annotations

from complete.governance.validators import (
    ToolCall,
    ToolResult,
    ValidatorPipeline,
)
from complete.governance.budget import ResourceBudget


# ---------------------------------------------------------------------------
# Approval gate (simulated)
# ---------------------------------------------------------------------------

class ApprovalGate:
    """Simulated human approval gate.

    In production this would integrate with Slack, Teams, or a custom
    approval UI. For the lab it auto-approves unless the tool name is in
    the require_approval list.
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
        return self.auto_approve


# ---------------------------------------------------------------------------
# ExecutionRail
# ---------------------------------------------------------------------------

class ExecutionRail:
    """Intercepts tool calls and enforces constraints before execution."""

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
        """Intercept a tool call and enforce all constraints, in order."""
        # Step 1: budget check (cheapest, so it fails first)
        if not self.budget.can_afford(tool_call):
            return ToolResult(blocked=True, reason="Budget exhausted")

        # Step 2: tool-specific validators
        pipeline = self.validators.get(tool_call.tool_name)
        if pipeline is not None:
            result = await pipeline.validate(tool_call)
            if result.blocked:
                return ToolResult(blocked=True, reason=result.reason)

        # Step 3: human approval (most expensive, so it runs last)
        if self.approval_gate.requires_approval(tool_call):
            approved = await self.approval_gate.request(tool_call)
            if not approved:
                return ToolResult(blocked=True, reason="Human denied")

        # Step 4: execute and record consumption
        self.budget.consume(tool_call)
        return await tool_call.execute()
