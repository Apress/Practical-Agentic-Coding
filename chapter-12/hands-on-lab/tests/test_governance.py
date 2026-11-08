"""
Governance pipeline test suite for Chapter 12 hands-on lab.

These tests validate the student's implementations of the governance
components described in Section 12.8. They pass when TODOs are
correctly implemented and fail with clear messages otherwise.

Each test class is tagged with the AGILITY pillar it exercises. This
lab covers three of the seven pillars: Limitations, Intervention, and
Governance. For the same pattern applied across all seven (including
which pillars need manual verification), see
../code-examples/governance_tests.py.

Run with: pytest tests/test_governance.py -v
"""

from __future__ import annotations

import time

import pytest

from starter.governance.validators import (
    AbsoluteBoundary,
    CredentialDetector,
    PathRestrictionValidator,
    ToolCall,
    ValidatorPipeline,
)
from starter.governance.budget import ResourceBudget
from starter.governance.audit import ImmutableAuditLog
from starter.governance.drift_monitor import (
    GoalDriftMonitor,
    linear_regression_slope,
    semantic_similarity,
)
from starter.governance.execution_rail import ApprovalGate, ExecutionRail


# -----------------------------------------------------------------------
# Path restriction tests (Section 12.8)
# -----------------------------------------------------------------------

class TestPathRestriction:
    """[Limitations] Tests for PathRestrictionValidator."""

    def test_path_restriction_blocks(self) -> None:
        """Denied paths must be blocked even if they match an allowed prefix."""
        validator = PathRestrictionValidator(
            allowed_paths=["/src", "/tests"],
            denied_paths=["/src/secrets"],
        )
        tool_call = ToolCall(
            tool_name="file_write",
            params={"file_path": "/src/secrets/api_keys.json"},
        )
        result = validator.check(tool_call)
        assert result.blocked, (
            "PathRestrictionValidator should block paths in the denied list. "
            "Did you check denied paths before allowed paths?"
        )
        assert "denied" in result.reason.lower(), (
            "Blocked result should mention 'denied' in the reason."
        )

    def test_path_restriction_allows(self) -> None:
        """Paths within allowed directories should pass validation."""
        validator = PathRestrictionValidator(
            allowed_paths=["/src", "/tests"],
        )
        tool_call = ToolCall(
            tool_name="file_write",
            params={"file_path": "/src/app/main.py"},
        )
        result = validator.check(tool_call)
        assert result.passed, (
            "PathRestrictionValidator should allow paths under allowed directories. "
            "Check that you return ValidationResult(passed=True) for valid paths."
        )

    def test_path_restriction_blocks_unknown(self) -> None:
        """Paths not in any allowed directory should be blocked."""
        validator = PathRestrictionValidator(
            allowed_paths=["/src", "/tests"],
        )
        tool_call = ToolCall(
            tool_name="file_write",
            params={"file_path": "/etc/passwd"},
        )
        result = validator.check(tool_call)
        assert result.blocked, (
            "PathRestrictionValidator should block paths not in the allowed list."
        )
        assert "not in allowed" in result.reason.lower(), (
            "Blocked result should mention 'not in allowed' in the reason."
        )


# -----------------------------------------------------------------------
# Credential detection tests
# -----------------------------------------------------------------------

class TestCredentialDetector:
    """[Limitations] Tests for CredentialDetector."""

    def test_detects_api_key(self) -> None:
        """API key patterns should be detected and blocked."""
        detector = CredentialDetector()
        tool_call = ToolCall(
            tool_name="file_write",
            params={"content": "api_key: sk-abc123def456ghi789jkl012mno345pq"},
        )
        result = detector.check(tool_call)
        assert result.blocked, (
            "CredentialDetector should block parameters containing API key patterns."
        )

    def test_allows_clean_content(self) -> None:
        """Content without credential patterns should pass."""
        detector = CredentialDetector()
        tool_call = ToolCall(
            tool_name="file_write",
            params={"content": "def hello():\n    return 'world'"},
        )
        result = detector.check(tool_call)
        assert result.passed, (
            "CredentialDetector should pass content without credential patterns."
        )

    def test_detects_aws_key(self) -> None:
        """AWS access key IDs should be detected."""
        detector = CredentialDetector()
        tool_call = ToolCall(
            tool_name="shell",
            params={"command": "export AWS_KEY=AKIAIOSFODNN7EXAMPLE"},
        )
        result = detector.check(tool_call)
        assert result.blocked, (
            "CredentialDetector should block AWS access key patterns (AKIA...)."
        )


# -----------------------------------------------------------------------
# Absolute boundary tests
# -----------------------------------------------------------------------

class TestAbsoluteBoundary:
    """[Limitations] Tests for AbsoluteBoundary validator."""

    def test_blocks_production_delete(self) -> None:
        """DELETE FROM production must always be blocked."""
        boundary = AbsoluteBoundary()
        tool_call = ToolCall(
            tool_name="database",
            params={"query": "DELETE FROM production WHERE id > 0"},
        )
        result = boundary.check(tool_call)
        assert result.blocked, (
            "AbsoluteBoundary should block 'DELETE FROM production'."
        )
        assert "absolute boundary" in result.reason.lower()

    def test_allows_safe_commands(self) -> None:
        """Safe commands should pass absolute boundary checks."""
        boundary = AbsoluteBoundary()
        tool_call = ToolCall(
            tool_name="shell",
            params={"command": "pytest tests/ -v"},
        )
        result = boundary.check(tool_call)
        assert result.passed, (
            "AbsoluteBoundary should allow safe commands like pytest."
        )


# -----------------------------------------------------------------------
# Validator pipeline tests
# -----------------------------------------------------------------------

class TestValidatorPipeline:
    """[Limitations] Tests for ValidatorPipeline."""

    @pytest.mark.asyncio
    async def test_pipeline_short_circuits(self) -> None:
        """Pipeline should stop at the first blocking validator."""
        pipeline = (
            ValidatorPipeline()
            .add(PathRestrictionValidator(allowed_paths=["/src"]))
            .add(CredentialDetector())
        )
        tool_call = ToolCall(
            tool_name="file_write",
            params={"file_path": "/etc/shadow"},
        )
        result = await pipeline.validate(tool_call)
        assert result.blocked, (
            "ValidatorPipeline.validate() should return a blocked result "
            "when any validator blocks."
        )

    @pytest.mark.asyncio
    async def test_pipeline_passes_all(self) -> None:
        """Pipeline should pass when all validators pass."""
        pipeline = (
            ValidatorPipeline()
            .add(PathRestrictionValidator(allowed_paths=["/src"]))
            .add(AbsoluteBoundary())
        )
        tool_call = ToolCall(
            tool_name="file_write",
            params={"file_path": "/src/app.py", "content": "print('hi')"},
        )
        result = await pipeline.validate(tool_call)
        assert result.passed, (
            "ValidatorPipeline.validate() should return passed=True when "
            "all validators pass."
        )


# -----------------------------------------------------------------------
# Budget exhaustion test (Section 12.8)
# -----------------------------------------------------------------------

class TestResourceBudget:
    """[Limitations] Tests for ResourceBudget."""

    def test_budget_exhaustion(self) -> None:
        """Budget should deny tool calls after limit is reached."""
        budget = ResourceBudget(max_tool_calls=3, max_cost_usd=1.0)
        tool_call = ToolCall(tool_name="shell", estimated_cost=0.10)

        # Consume 3 tool calls to exhaust the budget
        for _ in range(3):
            assert budget.can_afford(tool_call), (
                "Budget should allow calls before limit is reached."
            )
            budget.consume(tool_call)

        # Fourth call should be denied
        assert not budget.can_afford(tool_call), (
            "Budget should deny calls after tool_calls limit is exhausted. "
            "Check that can_afford compares consumed[k] < limits[k]."
        )

    def test_budget_tracks_cost(self) -> None:
        """Budget should track cumulative cost."""
        budget = ResourceBudget(max_tool_calls=100, max_cost_usd=0.25)
        expensive_call = ToolCall(tool_name="llm", estimated_cost=0.10)

        budget.consume(expensive_call)
        budget.consume(expensive_call)
        assert budget.can_afford(expensive_call), (
            "Budget should allow when cost is below limit (0.20 < 0.25)."
        )

        budget.consume(expensive_call)
        assert not budget.can_afford(expensive_call), (
            "Budget should deny when cost exceeds limit (0.30 >= 0.25)."
        )


# -----------------------------------------------------------------------
# Audit chain integrity test (Section 12.8)
# -----------------------------------------------------------------------

class TestAuditLog:
    """[Governance] Tests for ImmutableAuditLog."""

    def test_audit_chain_integrity(self) -> None:
        """Audit chain should verify intact and detect tampering."""
        log = ImmutableAuditLog()
        log.append("agent-1", "file_write", "success")
        log.append("agent-1", "shell_exec", "success")
        log.append("agent-2", "deploy", "success")

        # Chain should be valid
        assert log.verify_chain(), (
            "verify_chain() should return True for an untampered log. "
            "Check that you compare entry['previous_hash'] to the "
            "tracked hash, starting from 'genesis'."
        )

        # Tamper with an entry
        log.entries[1]["action"] = "TAMPERED"

        # Chain should now be invalid
        assert not log.verify_chain(), (
            "verify_chain() should return False after tampering with an entry. "
            "The hash of entry[1] no longer matches because the content changed."
        )

    def test_audit_chain_links(self) -> None:
        """Each entry's previous_hash should link to the prior entry."""
        log = ImmutableAuditLog()
        log.append("agent-1", "action-a", "ok")
        log.append("agent-1", "action-b", "ok")

        assert log.entries[0]["previous_hash"] == "genesis", (
            "First entry should have previous_hash='genesis'."
        )
        assert log.entries[1]["previous_hash"] == log.entries[0]["hash"], (
            "Second entry's previous_hash should equal the first entry's hash."
        )

    def test_audit_empty_chain_valid(self) -> None:
        """An empty audit log should verify as valid."""
        log = ImmutableAuditLog()
        assert log.verify_chain(), (
            "An empty chain should verify as True."
        )

    def test_audit_chain_truncation_detected(self) -> None:
        """A stored chain head should expose deletion of tail entries."""
        log = ImmutableAuditLog()
        log.append("agent-1", "file_write", "success")
        log.append("agent-1", "shell_exec", "success")
        log.append("agent-2", "deploy", "success")
        head = log.entries[-1]["hash"]

        # Delete the last entry: the shorter chain is still internally
        # consistent, so plain verification cannot catch it.
        log.entries.pop()
        assert log.verify_chain(), (
            "A truncated chain is still internally valid; only the "
            "stored head can expose it."
        )

        assert not log.verify_chain(expected_head=head), (
            "verify_chain(expected_head=...) should return False when "
            "the last entry's hash no longer matches the stored chain "
            "head. Compare the tracked hash after the walk to "
            "expected_head."
        )


# -----------------------------------------------------------------------
# Emergency stop within SLA test (Section 12.8, simulated)
# -----------------------------------------------------------------------

class TestEmergencyStop:
    """[Intervention] Tests for emergency stop behavior (simulated)."""

    @pytest.mark.asyncio
    async def test_emergency_stop_within_sla(self) -> None:
        """Execution rail should block a call within 100ms when budget
        is exhausted, simulating an emergency stop SLA.

        This test verifies that the budget check (the cheapest check)
        fires quickly, acting as a fast-path emergency stop.
        """
        budget = ResourceBudget(max_tool_calls=0)  # Already exhausted
        gate = ApprovalGate(auto_approve=True)
        rail = ExecutionRail(budget=budget, approval_gate=gate)

        tool_call = ToolCall(tool_name="shell", params={"command": "rm -rf /"})

        start = time.monotonic()
        result = await rail.intercept(tool_call)
        elapsed_ms = (time.monotonic() - start) * 1000

        assert result.blocked, (
            "ExecutionRail should block when budget is exhausted. "
            "Check that intercept() calls budget.can_afford() first."
        )
        assert "budget" in result.reason.lower(), (
            "Blocked reason should mention 'budget'."
        )
        assert elapsed_ms < 100, (
            f"Emergency stop took {elapsed_ms:.1f}ms, should be under 100ms. "
            "Budget check should be the fastest path to rejection."
        )


# -----------------------------------------------------------------------
# Execution rail integration test
# -----------------------------------------------------------------------

class TestExecutionRail:
    """[Limitations + Intervention] Integration tests for the full
    execution rail pipeline: validators enforce boundaries
    (Limitations), the approval gate is a human intervention point
    (Intervention)."""

    @pytest.mark.asyncio
    async def test_rail_allows_valid_call(self) -> None:
        """A valid tool call should pass through all four steps."""
        budget = ResourceBudget(max_tool_calls=10)
        gate = ApprovalGate(auto_approve=True)
        rail = ExecutionRail(budget=budget, approval_gate=gate)

        pipeline = (
            ValidatorPipeline()
            .add(PathRestrictionValidator(allowed_paths=["/src"]))
        )
        rail.register_validators("file_write", pipeline)

        tool_call = ToolCall(
            tool_name="file_write",
            params={"file_path": "/src/main.py"},
        )
        result = await rail.intercept(tool_call)
        assert not result.blocked, (
            "ExecutionRail should allow valid calls that pass all checks."
        )

    @pytest.mark.asyncio
    async def test_rail_blocks_on_validation(self) -> None:
        """A tool call failing validation should be blocked."""
        budget = ResourceBudget(max_tool_calls=10)
        gate = ApprovalGate(auto_approve=True)
        rail = ExecutionRail(budget=budget, approval_gate=gate)

        pipeline = (
            ValidatorPipeline()
            .add(PathRestrictionValidator(allowed_paths=["/src"]))
        )
        rail.register_validators("file_write", pipeline)

        tool_call = ToolCall(
            tool_name="file_write",
            params={"file_path": "/etc/passwd"},
        )
        result = await rail.intercept(tool_call)
        assert result.blocked, (
            "ExecutionRail should block calls that fail validation."
        )

    @pytest.mark.asyncio
    async def test_rail_blocks_unapproved(self) -> None:
        """A tool call requiring approval that is denied should be blocked."""
        budget = ResourceBudget(max_tool_calls=10)
        gate = ApprovalGate(
            require_approval=["deploy"],
            auto_approve=False,
        )
        rail = ExecutionRail(budget=budget, approval_gate=gate)

        tool_call = ToolCall(tool_name="deploy", params={})
        result = await rail.intercept(tool_call)
        assert result.blocked, (
            "ExecutionRail should block calls denied by the approval gate."
        )
        assert "denied" in result.reason.lower(), (
            "Blocked reason should mention 'denied'."
        )


# -----------------------------------------------------------------------
# Drift monitor tests
# -----------------------------------------------------------------------

class TestDriftMonitor:
    """[Intervention] Tests for GoalDriftMonitor and helper functions.
    Drift alerts exist to trigger intervention (specification
    re-injection) before misalignment compounds."""

    def test_semantic_similarity_identical(self) -> None:
        """Identical texts should have similarity of 1.0."""
        score = semantic_similarity("build a REST API", "build a REST API")
        assert score == pytest.approx(1.0), (
            "Identical texts should return similarity 1.0."
        )

    def test_semantic_similarity_different(self) -> None:
        """Completely different texts should have low similarity."""
        score = semantic_similarity(
            "build a REST API for users",
            "paint the kitchen walls blue",
        )
        assert score < 0.3, (
            f"Unrelated texts should have low similarity, got {score:.2f}."
        )

    def test_linear_regression_slope_declining(self) -> None:
        """A declining series should produce a negative slope."""
        scores = [0.9, 0.85, 0.78, 0.70, 0.60]
        slope = linear_regression_slope(scores)
        assert slope < 0, (
            f"Declining scores should produce negative slope, got {slope:.4f}."
        )

    def test_drift_detection(self) -> None:
        """Monitor should alert when alignment trend is strongly negative."""
        monitor = GoalDriftMonitor(
            original_spec="build a REST API with user authentication",
            drift_threshold=0.05,
        )
        # Simulate outputs that progressively diverge from the spec
        outputs = [
            "implementing REST API with user auth endpoints",
            "adding REST API routes for authentication",
            "refactoring database schema for performance",
            "optimizing cache layer and adding metrics",
            "building monitoring dashboard with graphs",
            "redesigning the entire frontend layout",
            "migrating to a different programming language",
        ]
        alert = None
        for step, output in enumerate(outputs):
            result = monitor.check(output, step)
            if result is not None:
                alert = result
                break

        assert alert is not None, (
            "GoalDriftMonitor should fire an alert when outputs diverge "
            "from the original specification. Check that you compute the "
            "trend with linear_regression_slope and compare against "
            "-self.threshold."
        )
        assert alert.severity == "WARNING"
        assert "re-inject" in alert.recommendation.lower()
