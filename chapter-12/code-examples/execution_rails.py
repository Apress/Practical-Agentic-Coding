"""
Module: Execution Rails for Autonomous Coding Agents
Concept: Four-step intercept pattern (budget, validate, approve, execute)
Chapter Reference: Chapter 12, Section 12.3

This example demonstrates execution rails that sit between an agent's
decision to use a tool and the tool's actual invocation. Every tool call
passes through budget checking, validation, approval gating, and finally
execution with audit logging.

Key Patterns Demonstrated:
- Resource budget enforcement as hard runtime limits
- Four-step intercept pattern (budget -> validate -> approve -> execute)
- Per-tool validator pipelines
- Simulated human approval gate with risk-based routing
- Budget exhaustion detection and clear error reporting
"""

import time
from typing import Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class RiskLevel(Enum):
    """Risk classification for tool calls."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ToolCall:
    """Represents an agent's request to invoke a tool."""
    tool_name: str
    params: dict
    agent_id: str = "default-agent"
    estimated_cost: float = 0.01
    risk_level: RiskLevel = RiskLevel.LOW
    timestamp: datetime = field(default_factory=datetime.now)

    def description(self) -> str:
        """Human-readable summary of the tool call."""
        param_summary = ", ".join(
            f"{k}={repr(v)[:40]}" for k, v in self.params.items()
        )
        return f"{self.tool_name}({param_summary})"


@dataclass
class ToolResult:
    """Result of a tool call after passing through the execution rail."""
    success: bool = False
    blocked: bool = False
    reason: str = ""
    output: str = ""
    cost_incurred: float = 0.0
    execution_time_ms: float = 0.0
    tool_call: Optional[ToolCall] = None


@dataclass
class ValidationResult:
    """Result of running validators on a tool call."""
    passed: bool = False
    blocked: bool = False
    reason: str = ""


class ResourceBudget:
    """Hard limits enforced by runtime, not by the agent.

    The agent cannot modify or override its own budget. When any
    resource is exhausted, the agent receives a clear error and must
    either complete with what it has or escalate to a human.
    """

    def __init__(
        self,
        max_tool_calls: int = 50,
        max_cost_usd: float = 5.00,
        max_files_modified: int = 10,
        max_wall_clock_seconds: int = 1800,
    ) -> None:
        self.limits = {
            "tool_calls": max_tool_calls,
            "cost_usd": max_cost_usd,
            "files_modified": max_files_modified,
            "wall_clock_seconds": max_wall_clock_seconds,
        }
        self.consumed = {
            "tool_calls": 0,
            "cost_usd": 0.0,
            "files_modified": 0,
            "wall_clock_seconds": 0,
        }
        self.start_time = time.time()

    def can_afford(self, tool_call: ToolCall) -> bool:
        """Check whether the budget allows this tool call.

        Args:
            tool_call: The proposed tool invocation.

        Returns:
            True if all resource limits have remaining capacity.
        """
        # Update wall clock
        self.consumed["wall_clock_seconds"] = int(
            time.time() - self.start_time
        )
        return all(
            self.consumed[k] < self.limits[k] for k in self.limits
        )

    def consume(self, tool_call: ToolCall) -> None:
        """Record resource consumption for a tool call.

        Args:
            tool_call: The tool invocation that was executed.
        """
        self.consumed["tool_calls"] += 1
        self.consumed["cost_usd"] += tool_call.estimated_cost
        if tool_call.tool_name in ("file_write", "file_modify"):
            self.consumed["files_modified"] += 1

    def exhausted_resource(self) -> Optional[str]:
        """Return the name of the first exhausted resource, or None."""
        self.consumed["wall_clock_seconds"] = int(
            time.time() - self.start_time
        )
        for key in self.limits:
            if self.consumed[key] >= self.limits[key]:
                return key
        return None

    def summary(self) -> str:
        """Return a human-readable budget summary."""
        lines = []
        for key in self.limits:
            used = self.consumed[key]
            limit = self.limits[key]
            pct = (used / limit * 100) if limit > 0 else 0
            bar = "#" * int(pct / 5) + "-" * (20 - int(pct / 5))
            if isinstance(used, float):
                lines.append(
                    f"  {key:>22s}: ${used:.2f} / ${limit:.2f} "
                    f"[{bar}] {pct:.0f}%"
                )
            else:
                lines.append(
                    f"  {key:>22s}: {used} / {limit} "
                    f"[{bar}] {pct:.0f}%"
                )
        return "\n".join(lines)


class SimpleValidator:
    """Minimal validator for demonstration purposes.

    In production, use the full ValidatorPipeline from
    composable_validators.py.
    """

    def __init__(self, blocked_patterns: Optional[list[str]] = None) -> None:
        self.blocked_patterns = blocked_patterns or []

    def validate(self, tool_call: ToolCall) -> ValidationResult:
        """Check tool call against blocked patterns."""
        text = str(tool_call.params).lower()
        for pattern in self.blocked_patterns:
            if pattern.lower() in text:
                return ValidationResult(
                    blocked=True,
                    reason=f"Blocked pattern: '{pattern}'",
                )
        return ValidationResult(passed=True)


class ApprovalGate:
    """Simulated human approval gate.

    Routes actions requiring human review based on risk level.
    In production, this would integrate with Slack, PagerDuty,
    or a custom approval UI.
    """

    def __init__(
        self,
        approval_threshold: RiskLevel = RiskLevel.HIGH,
        auto_approve_below: RiskLevel = RiskLevel.MEDIUM,
    ) -> None:
        self.approval_threshold = approval_threshold
        self.auto_approve_below = auto_approve_below
        self._risk_order = {
            RiskLevel.LOW: 0,
            RiskLevel.MEDIUM: 1,
            RiskLevel.HIGH: 2,
            RiskLevel.CRITICAL: 3,
        }
        self.pending_approvals: list[ToolCall] = []
        self.approval_log: list[dict] = []

    def requires_approval(self, tool_call: ToolCall) -> bool:
        """Determine if this tool call needs human approval.

        Args:
            tool_call: The proposed tool invocation.

        Returns:
            True if the risk level meets or exceeds the threshold.
        """
        call_risk = self._risk_order[tool_call.risk_level]
        threshold = self._risk_order[self.approval_threshold]
        return call_risk >= threshold

    def request(self, tool_call: ToolCall) -> bool:
        """Request human approval for a tool call (simulated).

        In this simulation, CRITICAL risk is always denied,
        HIGH risk is approved 50% of the time (simulating human
        judgment), and everything else is approved.

        Args:
            tool_call: The tool call requiring approval.

        Returns:
            True if approved, False if denied.
        """
        self.pending_approvals.append(tool_call)

        # Simulate human decision based on risk
        if tool_call.risk_level == RiskLevel.CRITICAL:
            approved = False
            reason = "CRITICAL risk: human denied"
        elif tool_call.risk_level == RiskLevel.HIGH:
            # Simulate: approve if the tool is well-known
            approved = tool_call.tool_name in (
                "file_write", "git_commit", "pytest"
            )
            reason = (
                "HIGH risk: approved (known tool)"
                if approved
                else "HIGH risk: denied (unknown tool)"
            )
        else:
            approved = True
            reason = "Below threshold: auto-approved"

        self.approval_log.append({
            "tool_call": tool_call.description(),
            "risk": tool_call.risk_level.value,
            "approved": approved,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
        })

        return approved


class ExecutionRail:
    """Intercepts tool calls and enforces constraints before execution.

    Implements the four-step intercept pattern:
    1. Budget check (cheapest, fails first)
    2. Tool-specific validation
    3. Human approval gate (most expensive, last)
    4. Execute and record

    The order matters: budget checks are O(1) and should short-circuit
    before expensive validation or human-in-the-loop approval.
    """

    def __init__(
        self,
        budget: ResourceBudget,
        approval_gate: ApprovalGate,
    ) -> None:
        self.budget = budget
        self.approval_gate = approval_gate
        self.validators: dict[str, SimpleValidator] = {}
        self.audit_trail: list[dict] = []
        self._tool_handlers: dict[str, Callable] = {}

    def register_validator(
        self, tool_name: str, validator: SimpleValidator
    ) -> None:
        """Register a validator for a specific tool type."""
        self.validators[tool_name] = validator

    def register_tool(
        self, tool_name: str, handler: Callable
    ) -> None:
        """Register a simulated tool handler."""
        self._tool_handlers[tool_name] = handler

    def intercept(self, tool_call: ToolCall) -> ToolResult:
        """Run the four-step intercept on a tool call.

        Args:
            tool_call: The proposed tool invocation.

        Returns:
            ToolResult with success/blocked status and details.
        """
        start = time.time()

        # Step 1: Check resource budget
        if not self.budget.can_afford(tool_call):
            exhausted = self.budget.exhausted_resource()
            result = ToolResult(
                blocked=True,
                reason=f"Budget exhausted: {exhausted}",
                tool_call=tool_call,
            )
            self._log(tool_call, result, "budget_exhausted")
            return result

        # Step 2: Run tool-specific validators
        validator = self.validators.get(tool_call.tool_name)
        if validator:
            v_result = validator.validate(tool_call)
            if v_result.blocked:
                result = ToolResult(
                    blocked=True,
                    reason=v_result.reason,
                    tool_call=tool_call,
                )
                self._log(tool_call, result, "validation_blocked")
                return result

        # Step 3: Check if human approval is required
        if self.approval_gate.requires_approval(tool_call):
            approved = self.approval_gate.request(tool_call)
            if not approved:
                result = ToolResult(
                    blocked=True,
                    reason="Human denied approval",
                    tool_call=tool_call,
                )
                self._log(tool_call, result, "approval_denied")
                return result

        # Step 4: Execute and record
        self.budget.consume(tool_call)
        elapsed_ms = (time.time() - start) * 1000

        handler = self._tool_handlers.get(tool_call.tool_name)
        if handler:
            output = handler(tool_call)
        else:
            output = f"[simulated] {tool_call.tool_name} executed"

        result = ToolResult(
            success=True,
            output=output,
            cost_incurred=tool_call.estimated_cost,
            execution_time_ms=elapsed_ms,
            tool_call=tool_call,
        )
        self._log(tool_call, result, "executed")
        return result

    def _log(
        self, tool_call: ToolCall, result: ToolResult, outcome: str
    ) -> None:
        """Append an entry to the audit trail."""
        self.audit_trail.append({
            "timestamp": datetime.now().isoformat(),
            "agent_id": tool_call.agent_id,
            "tool": tool_call.tool_name,
            "action": tool_call.description(),
            "outcome": outcome,
            "blocked": result.blocked,
            "reason": result.reason,
        })


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------


def _section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    print("=== Execution Rails Demo ===")
    print("Chapter 12, Section 12.3\n")

    # ------------------------------------------------------------------
    # Set up budget, approval gate, and execution rail
    # ------------------------------------------------------------------
    _section("1. Setting Up Execution Rail")

    budget = ResourceBudget(
        max_tool_calls=5,
        max_cost_usd=0.50,
        max_files_modified=3,
        max_wall_clock_seconds=300,
    )
    print("  Budget configured:")
    print(f"    max_tool_calls: 5")
    print(f"    max_cost_usd: $0.50")
    print(f"    max_files_modified: 3")

    gate = ApprovalGate(
        approval_threshold=RiskLevel.HIGH,
    )
    print(f"  Approval gate: requires approval for HIGH+ risk")

    rail = ExecutionRail(budget=budget, approval_gate=gate)

    # Register validators
    rail.register_validator(
        "shell_command",
        SimpleValidator(blocked_patterns=["rm -rf", "chmod 777"]),
    )
    rail.register_validator(
        "file_write",
        SimpleValidator(blocked_patterns=["password=", "api_key="]),
    )
    print("  Validators registered for: shell_command, file_write")

    # Register simulated tool handlers
    rail.register_tool("file_write", lambda tc: f"Wrote {len(tc.params.get('content', ''))} bytes")
    rail.register_tool("shell_command", lambda tc: f"Ran: {tc.params.get('command', '')}")
    rail.register_tool("git_commit", lambda tc: f"Committed: {tc.params.get('message', '')}")
    rail.register_tool("deploy", lambda tc: f"Deployed to {tc.params.get('env', 'unknown')}")

    # ------------------------------------------------------------------
    # Process a series of tool calls
    # ------------------------------------------------------------------
    _section("2. Processing Tool Calls")

    tool_calls = [
        ToolCall(
            tool_name="file_write",
            params={"file_path": "/src/app.py", "content": "print('hello')"},
            agent_id="code-gen",
            estimated_cost=0.02,
            risk_level=RiskLevel.LOW,
        ),
        ToolCall(
            tool_name="shell_command",
            params={"command": "pytest tests/ -v"},
            agent_id="test-runner",
            estimated_cost=0.05,
            risk_level=RiskLevel.LOW,
        ),
        ToolCall(
            tool_name="shell_command",
            params={"command": "rm -rf /tmp/important"},
            agent_id="cleanup-agent",
            estimated_cost=0.01,
            risk_level=RiskLevel.MEDIUM,
        ),
        ToolCall(
            tool_name="git_commit",
            params={"message": "fix: resolve CSS layout bug"},
            agent_id="code-gen",
            estimated_cost=0.03,
            risk_level=RiskLevel.HIGH,
        ),
        ToolCall(
            tool_name="deploy",
            params={"env": "production", "version": "2.1.0"},
            agent_id="deploy-agent",
            estimated_cost=0.10,
            risk_level=RiskLevel.CRITICAL,
        ),
        ToolCall(
            tool_name="file_write",
            params={"file_path": "/src/utils.py", "content": "# utils"},
            agent_id="code-gen",
            estimated_cost=0.02,
            risk_level=RiskLevel.LOW,
        ),
    ]

    for i, tc in enumerate(tool_calls, 1):
        result = rail.intercept(tc)
        status = "EXECUTED" if result.success else "BLOCKED"
        print(f"\n  [{i}] {tc.description()}")
        print(f"      Risk: {tc.risk_level.value}")
        print(f"      Status: {status}")
        if result.blocked:
            print(f"      Reason: {result.reason}")
        elif result.output:
            print(f"      Output: {result.output}")

    # ------------------------------------------------------------------
    # Show budget state
    # ------------------------------------------------------------------
    _section("3. Budget Status After Processing")
    print(budget.summary())

    exhausted = budget.exhausted_resource()
    if exhausted:
        print(f"\n  Budget EXHAUSTED on: {exhausted}")
    else:
        print(f"\n  Budget still has capacity")

    # ------------------------------------------------------------------
    # Try one more call to demonstrate budget exhaustion
    # ------------------------------------------------------------------
    _section("4. Budget Exhaustion Demo")

    # Four of the five allowed tool calls are spent. The first extra call
    # takes the last slot; the second hits the hard limit.
    for filename in ("extra.py", "one_more.py"):
        extra_call = ToolCall(
            tool_name="file_write",
            params={"file_path": f"/src/{filename}", "content": "# extra"},
            agent_id="code-gen",
            estimated_cost=0.02,
        )
        result = rail.intercept(extra_call)
        print(f"  Tool call: {extra_call.description()}")
        print(f"  Status: {'EXECUTED' if result.success else 'BLOCKED'}")
        if result.blocked:
            print(f"  Reason: {result.reason}")

    # ------------------------------------------------------------------
    # Show audit trail
    # ------------------------------------------------------------------
    _section("5. Audit Trail")

    for entry in rail.audit_trail:
        print(f"  [{entry['timestamp'][:19]}] "
              f"agent={entry['agent_id']:12s} "
              f"tool={entry['tool']:15s} "
              f"outcome={entry['outcome']}")

    # ------------------------------------------------------------------
    # Show approval log
    # ------------------------------------------------------------------
    _section("6. Approval Gate Log")

    for entry in gate.approval_log:
        approved = "APPROVED" if entry["approved"] else "DENIED"
        print(f"  {entry['tool_call'][:50]:50s} "
              f"risk={entry['risk']:8s} {approved}")
        print(f"    Reason: {entry['reason']}")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    _section("Summary")
    executed = sum(1 for e in rail.audit_trail if e["outcome"] == "executed")
    blocked = sum(1 for e in rail.audit_trail if e["outcome"] != "executed")
    print(f"  Total calls processed: {len(rail.audit_trail)}")
    print(f"  Executed: {executed}")
    print(f"  Blocked: {blocked}")
    print(f"  Budget consumed: {budget.consumed['tool_calls']} / "
          f"{budget.limits['tool_calls']} tool calls")
    print(f"  Cost consumed: ${budget.consumed['cost_usd']:.2f} / "
          f"${budget.limits['cost_usd']:.2f}")
    print("\n=== Demo complete ===")
