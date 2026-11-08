"""
Module: Governance as Executable Tests
Concept: Turning AGILITY framework pillars into runnable test suites
Chapter Reference: Chapter 12, Section 12.6

This example demonstrates executable governance tests that verify agent
safety constraints at runtime. Each test corresponds to an AGILITY pillar
(Accountability, Governance, Integrity, Limitations, Intervention,
Transparency, Youth). The tests run alongside application tests in CI/CD,
turning compliance from a document into an automated gate.

Key Patterns Demonstrated:
- GovernanceConfig as a structured policy declaration
- Per-pillar test methods (Limitations, Intervention, Governance)
- ImmutableAuditLog with SHA-256 hash-chained entries
- Tamper detection through chain verification
- Simulated emergency stop with timing assertion
- Test runner with pass/fail reporting
"""

import hashlib
import posixpath
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from enum import Enum


# ---------------------------------------------------------------------------
# Governance configuration
# ---------------------------------------------------------------------------


class OversightLevel(Enum):
    """Level of human oversight required."""
    AUTONOMOUS = "autonomous"
    ASYNC_REVIEW = "async_review"
    PROPOSE_AND_WAIT = "propose_and_wait"
    ESCALATE = "escalate"


@dataclass
class GovernanceConfig:
    """Declarative governance policy for an agent.

    This configuration defines the agent's operational boundaries.
    Tests verify that the enforcement matches this declaration.
    """
    agent_id: str
    human_sponsor: str
    allowed_paths: list[str] = field(default_factory=lambda: ["/src", "/tests"])
    denied_paths: list[str] = field(default_factory=lambda: ["/etc", "/root", "/.ssh"])
    max_tool_invocations: int = 50
    max_cost_usd: float = 5.00
    max_wall_clock_seconds: int = 1800
    emergency_stop_sla_seconds: float = 1.0
    # Pin the exact model the agent is approved to run. Update this
    # when you deliberately move the agent to a new model version.
    model_version: str = "claude-sonnet-5-5"
    model_checksum: str = "sha256:abc123"  # placeholder digest
    default_oversight: OversightLevel = OversightLevel.ASYNC_REVIEW


# ---------------------------------------------------------------------------
# Immutable audit log
# ---------------------------------------------------------------------------


@dataclass
class AuditEntry:
    """A single entry in the hash-chained audit log."""
    agent_id: str
    action: str
    result: str
    timestamp: str
    previous_hash: str
    entry_hash: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for hashing (excluding entry_hash)."""
        return {
            "agent_id": self.agent_id,
            "action": self.action,
            "result": self.result,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
        }


class ImmutableAuditLog:
    """Hash-chained log entries for tamper evidence.

    Each entry includes a SHA-256 hash of its contents plus the
    previous entry's hash, creating a chain. Tampering with any
    entry breaks the chain, making modifications detectable.
    """

    def __init__(self) -> None:
        self.entries: list[AuditEntry] = []
        self._previous_hash: str = "genesis"

    def append(self, agent_id: str, action: str, result: str) -> AuditEntry:
        """Add a new entry to the audit log.

        Args:
            agent_id: Identifier of the agent that performed the action.
            action: Description of the action taken.
            result: Outcome of the action.

        Returns:
            The newly created AuditEntry.
        """
        entry = AuditEntry(
            agent_id=agent_id,
            action=action,
            result=result,
            timestamp=datetime.now(timezone.utc).isoformat(),
            previous_hash=self._previous_hash,
        )
        # Compute hash over the entry contents
        entry_dict = entry.to_dict()
        entry.entry_hash = hashlib.sha256(
            json.dumps(entry_dict, sort_keys=True).encode()
        ).hexdigest()
        self._previous_hash = entry.entry_hash
        self.entries.append(entry)
        return entry

    @property
    def chain_head(self) -> str:
        """Hash of the most recent entry ("genesis" if the log is empty).

        Store this value out of band (a separate database, a signed
        release note) and pass it to verify_chain() to detect truncation.
        """
        return self._previous_hash

    def verify_chain(self, expected_head: Optional[str] = None) -> bool:
        """Verify that no entries have been tampered with.

        Recomputes each entry's hash and checks the chain linkage.
        A plain walk cannot detect truncation: deleting entries from
        the tail leaves a shorter chain that still verifies. Passing
        expected_head (the chain_head value recorded out of band)
        closes that gap.

        Args:
            expected_head: The chain head hash recorded out of band.
                If provided, the final entry's hash must match it.

        Returns:
            True if the chain is intact, False if tampering detected.
        """
        prev = "genesis"
        for entry in self.entries:
            if entry.previous_hash != prev:
                return False
            # Recompute hash
            expected = hashlib.sha256(
                json.dumps(entry.to_dict(), sort_keys=True).encode()
            ).hexdigest()
            if entry.entry_hash != expected:
                return False
            prev = entry.entry_hash
        if expected_head is not None and prev != expected_head:
            # Tail entries were deleted (or the log was replaced)
            return False
        return True

    def find_tampered(self) -> Optional[int]:
        """Find the index of the first tampered entry, or None."""
        prev = "genesis"
        for i, entry in enumerate(self.entries):
            if entry.previous_hash != prev:
                return i
            expected = hashlib.sha256(
                json.dumps(entry.to_dict(), sort_keys=True).encode()
            ).hexdigest()
            if entry.entry_hash != expected:
                return i
            prev = entry.entry_hash
        return None

    def __len__(self) -> int:
        return len(self.entries)


# ---------------------------------------------------------------------------
# Simulated agent for testing
# ---------------------------------------------------------------------------


def _is_under(path: str, directory: str) -> bool:
    """True when a normalized path is the directory itself or inside it."""
    directory = posixpath.normpath(directory)
    return path == directory or path.startswith(directory.rstrip("/") + "/")


class SimulatedAgent:
    """A minimal agent that supports governance testing.

    This agent simulates tool execution with path checking and budget
    enforcement, providing a testable target for governance tests.
    """

    def __init__(self, config: GovernanceConfig) -> None:
        self.config = config
        self.audit_log = ImmutableAuditLog()
        self._tool_calls: int = 0
        self._cost_usd: float = 0.0
        self._running: bool = False
        self._start_time: Optional[float] = None

    def execute(self, action: str) -> "ActionResult":
        """Execute an action through the governance layer.

        Args:
            action: Description of the action to execute.

        Returns:
            ActionResult with success/blocked status.
        """
        # Budget check
        if self._tool_calls >= self.config.max_tool_invocations:
            result = ActionResult(
                blocked=True,
                reason="Budget exhausted: max tool invocations reached",
            )
            self.audit_log.append(
                self.config.agent_id, action, f"BLOCKED: {result.reason}"
            )
            return result

        # Path restriction check
        if action.startswith("modify "):
            # Normalize first, so "/src/../etc/passwd" is judged as
            # "/etc/passwd", and match whole path components, so "/srcevil"
            # is not under "/src" (the same rules as PathRestrictionValidator
            # in composable_validators.py).
            path = posixpath.normpath(action[len("modify "):])
            for denied in self.config.denied_paths:
                if _is_under(path, denied):
                    result = ActionResult(
                        blocked=True,
                        reason=f"Path restriction: {path} is denied",
                    )
                    self.audit_log.append(
                        self.config.agent_id, action,
                        f"BLOCKED: {result.reason}",
                    )
                    return result

            if not any(_is_under(path, a) for a in self.config.allowed_paths):
                result = ActionResult(
                    blocked=True,
                    reason=f"Path restriction: {path} not in allowed list",
                )
                self.audit_log.append(
                    self.config.agent_id, action,
                    f"BLOCKED: {result.reason}",
                )
                return result

        # Execute
        self._tool_calls += 1
        self._cost_usd += 0.05
        result = ActionResult(success=True, output=f"Executed: {action}")
        self.audit_log.append(
            self.config.agent_id, action, "SUCCESS"
        )
        return result

    def start_task(self, task_name: str) -> None:
        """Start a long-running task (for emergency stop testing)."""
        self._running = True
        self._start_time = time.time()
        self.audit_log.append(
            self.config.agent_id, f"start_task: {task_name}", "STARTED"
        )

    def emergency_stop(self) -> float:
        """Trigger emergency stop and return time to halt in seconds."""
        if not self._running:
            return 0.0
        stop_start = time.time()
        # Simulate minimal stop latency
        self._running = False
        elapsed = time.time() - stop_start
        self.audit_log.append(
            self.config.agent_id, "emergency_stop",
            f"STOPPED in {elapsed:.4f}s",
        )
        return elapsed

    def get_audit_log(self) -> list[AuditEntry]:
        """Return all audit log entries."""
        return self.audit_log.entries


@dataclass
class ActionResult:
    """Result of an agent action."""
    success: bool = False
    blocked: bool = False
    reason: str = ""
    output: str = ""


# ---------------------------------------------------------------------------
# Governance test suite
# ---------------------------------------------------------------------------


@dataclass
class TestResult:
    """Result of a single governance test."""
    test_name: str
    pillar: str
    passed: bool
    message: str
    duration_ms: float = 0.0


class GovernanceTestSuite:
    """Executable governance tests compiled from AGILITY policies.

    Each test method corresponds to a specific AGILITY pillar and
    verifies that the enforcement actually works at runtime.
    """

    def __init__(
        self,
        agent: SimulatedAgent,
        config: GovernanceConfig,
    ) -> None:
        self.agent = agent
        self.config = config
        self.results: list[TestResult] = []

    def run_all(self) -> list[TestResult]:
        """Run all governance tests and return results."""
        self.results = []
        tests = [
            self.test_config_has_sponsor,
            self.test_path_restrictions_block,
            self.test_path_traversal_blocked,
            self.test_path_restrictions_allow,
            self.test_budget_enforcement,
            self.test_emergency_stop,
            self.test_audit_trail_completeness,
            self.test_audit_chain_integrity,
            self.test_audit_tamper_detection,
            self.test_audit_truncation_detection,
        ]
        for test_fn in tests:
            start = time.time()
            try:
                test_fn()
            except AssertionError as e:
                elapsed_ms = (time.time() - start) * 1000
                self.results.append(TestResult(
                    test_name=test_fn.__name__,
                    pillar=test_fn.__doc__.split("]")[0].strip("[") if test_fn.__doc__ else "?",
                    passed=False,
                    message=str(e),
                    duration_ms=elapsed_ms,
                ))
                continue
            elapsed_ms = (time.time() - start) * 1000
            self.results.append(TestResult(
                test_name=test_fn.__name__,
                pillar=test_fn.__doc__.split("]")[0].strip("[") if test_fn.__doc__ else "?",
                passed=True,
                message="OK",
                duration_ms=elapsed_ms,
            ))
        return self.results

    # --- Accountability (A) ---

    def test_config_has_sponsor(self) -> None:
        """[Accountability] Governance config has a named human sponsor."""
        assert self.config.human_sponsor, (
            "GovernanceConfig must have a non-empty human_sponsor"
        )
        assert len(self.config.human_sponsor) >= 2, (
            f"human_sponsor '{self.config.human_sponsor}' is too short"
        )

    # --- Limitations (L) ---

    def test_path_restrictions_block(self) -> None:
        """[Limitations] Agent cannot modify files in denied paths."""
        # Fresh agent for isolation
        agent = SimulatedAgent(self.config)
        result = agent.execute("modify /etc/passwd")
        assert result.blocked, (
            "Agent should be blocked from modifying /etc/passwd"
        )
        assert "path restriction" in result.reason.lower(), (
            f"Reason should mention path restriction, got: {result.reason}"
        )

    def test_path_traversal_blocked(self) -> None:
        """[Limitations] Traversal and look-alike prefixes do not slip past."""
        agent = SimulatedAgent(self.config)
        for action in ("modify /src/../etc/passwd", "modify /srcevil/x.py"):
            result = agent.execute(action)
            assert result.blocked, f"Agent should be blocked: {action}"

    def test_path_restrictions_allow(self) -> None:
        """[Limitations] Agent can modify files in allowed paths."""
        agent = SimulatedAgent(self.config)
        result = agent.execute("modify /src/app.py")
        assert result.success, (
            "Agent should be allowed to modify /src/app.py"
        )

    def test_budget_enforcement(self) -> None:
        """[Limitations] Agent stops when budget is exhausted."""
        # Create agent with a tiny budget
        tiny_config = GovernanceConfig(
            agent_id="budget-test-agent",
            human_sponsor=self.config.human_sponsor,
            max_tool_invocations=3,
        )
        agent = SimulatedAgent(tiny_config)

        # Use up the budget
        for i in range(3):
            r = agent.execute(f"task_{i}")
            assert r.success, f"Task {i} should succeed within budget"

        # Next call should be blocked
        result = agent.execute("task_overflow")
        assert result.blocked, "Agent should be blocked after budget exhaustion"
        assert "budget" in result.reason.lower(), (
            f"Reason should mention budget, got: {result.reason}"
        )

    # --- Intervention (I) ---

    def test_emergency_stop(self) -> None:
        """[Intervention] Emergency stop halts agent within SLA."""
        agent = SimulatedAgent(self.config)
        agent.start_task("long running refactor")
        # Small delay to simulate work in progress
        time.sleep(0.01)
        stop_time = agent.emergency_stop()
        assert stop_time < self.config.emergency_stop_sla_seconds, (
            f"Emergency stop took {stop_time:.3f}s, "
            f"SLA is {self.config.emergency_stop_sla_seconds}s"
        )
        assert not agent._running, "Agent should not be running after stop"

    # --- Governance (G) ---

    def test_audit_trail_completeness(self) -> None:
        """[Governance] Every agent action produces an audit log entry."""
        agent = SimulatedAgent(self.config)
        agent.execute("modify /src/models.py")
        agent.execute("modify /tests/test_models.py")
        agent.execute("modify /etc/shadow")  # Should be blocked

        logs = agent.get_audit_log()
        assert len(logs) == 3, (
            f"Expected 3 audit entries (including blocked), got {len(logs)}"
        )
        for entry in logs:
            assert entry.agent_id, "Audit entry must have agent_id"
            assert entry.timestamp, "Audit entry must have timestamp"
            assert entry.action, "Audit entry must have action"

    def test_audit_chain_integrity(self) -> None:
        """[Governance] Audit log chain is cryptographically valid."""
        agent = SimulatedAgent(self.config)
        agent.execute("modify /src/app.py")
        agent.execute("modify /src/utils.py")
        agent.execute("modify /tests/test_app.py")

        assert agent.audit_log.verify_chain(), (
            "Audit chain should be valid after normal operations"
        )

    def test_audit_tamper_detection(self) -> None:
        """[Governance] Tampering with audit log is detectable."""
        log = ImmutableAuditLog()
        log.append("agent-1", "modify /src/app.py", "SUCCESS")
        log.append("agent-1", "modify /src/utils.py", "SUCCESS")
        log.append("agent-1", "delete /src/secrets.py", "SUCCESS")

        # Verify chain is initially valid
        assert log.verify_chain(), "Chain should be valid before tampering"

        # Tamper: modify an entry to hide the deletion
        log.entries[2].action = "modify /src/config.py"

        # Chain should now be broken
        assert not log.verify_chain(), (
            "Chain should be invalid after tampering"
        )
        tampered_idx = log.find_tampered()
        assert tampered_idx == 2, (
            f"Tampered entry should be at index 2, got {tampered_idx}"
        )

    def test_audit_truncation_detection(self) -> None:
        """[Governance] Deleting entries from the log tail is detectable."""
        log = ImmutableAuditLog()
        log.append("agent-1", "modify /src/app.py", "SUCCESS")
        log.append("agent-1", "modify /src/utils.py", "SUCCESS")
        log.append("agent-1", "delete /src/secrets.py", "SUCCESS")

        # Record the chain head out of band (in practice: a separate store)
        head = log.chain_head

        # Truncate: drop the last entry to hide the deletion
        log.entries.pop()

        # A plain walk cannot see the missing tail
        assert log.verify_chain(), (
            "Truncated chain still passes a plain walk (that is the gap)"
        )
        # The out-of-band head catches the truncation
        assert not log.verify_chain(expected_head=head), (
            "Chain should be invalid when the recorded head is missing"
        )


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------


def _section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    print("=== Governance as Executable Tests Demo ===")
    print("Chapter 12, Section 12.6\n")

    # ------------------------------------------------------------------
    # Define governance configuration
    # ------------------------------------------------------------------
    _section("1. Governance Configuration")

    config = GovernanceConfig(
        agent_id="coding-agent-prod",
        human_sponsor="Abhijeet Patil",
        allowed_paths=["/src", "/tests", "/docs"],
        denied_paths=["/etc", "/root", "/.ssh", "/var/secrets"],
        max_tool_invocations=50,
        max_cost_usd=5.00,
        max_wall_clock_seconds=1800,
        emergency_stop_sla_seconds=1.0,
        model_version="claude-sonnet-5-5",
    )

    print(f"  Agent: {config.agent_id}")
    print(f"  Sponsor: {config.human_sponsor}")
    print(f"  Allowed paths: {config.allowed_paths}")
    print(f"  Denied paths: {config.denied_paths}")
    print(f"  Max tool calls: {config.max_tool_invocations}")
    print(f"  Emergency stop SLA: {config.emergency_stop_sla_seconds}s")

    # ------------------------------------------------------------------
    # Create agent and test suite
    # ------------------------------------------------------------------
    _section("2. Running Governance Test Suite")

    agent = SimulatedAgent(config)
    suite = GovernanceTestSuite(agent=agent, config=config)
    results = suite.run_all()

    # Display results
    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)

    for r in results:
        status = "PASSED" if r.passed else "FAILED"
        print(f"  {status:6s}  [{r.pillar:16s}]  {r.test_name}")
        if not r.passed:
            print(f"          Message: {r.message}")

    print(f"\n  Results: {passed} passed, {failed} failed, "
          f"{len(results)} total")

    # ------------------------------------------------------------------
    # Demonstrate ImmutableAuditLog independently
    # ------------------------------------------------------------------
    _section("3. ImmutableAuditLog Demo")

    log = ImmutableAuditLog()
    log.append("code-gen", "file_write /src/app.py", "SUCCESS")
    log.append("test-runner", "shell_command pytest", "SUCCESS")
    log.append("code-gen", "file_write /src/utils.py", "SUCCESS")
    log.append("reviewer", "code_review PR #42", "APPROVED")

    print(f"  Entries: {len(log)}")
    print(f"  Chain valid: {log.verify_chain()}")

    print("\n  Log entries:")
    for i, entry in enumerate(log.entries):
        print(f"    [{i}] {entry.agent_id:12s} {entry.action:35s} "
              f"{entry.result}")
        print(f"        hash: {entry.entry_hash[:16]}...")

    # Tamper with an entry
    print("\n  Tampering with entry [1] (changing result to FAILED)...")
    log.entries[1].result = "FAILED"
    print(f"  Chain valid after tampering: {log.verify_chain()}")
    tampered = log.find_tampered()
    print(f"  First tampered entry: index {tampered}")

    # ------------------------------------------------------------------
    # AGILITY pillar mapping
    # ------------------------------------------------------------------
    _section("4. AGILITY Pillar Coverage")

    pillar_map = {
        "Accountability": "Config has named human sponsor",
        "Governance": "All actions produce immutable audit entries",
        "Integrity": "Model version pinned, checksums verified",
        "Limitations": "Path restrictions and budget enforcement",
        "Intervention": "Emergency stop within SLA",
        "Transparency": "Hash-chained audit trail, reasoning traces",
        "Youth": "Rollback procedure tested in staging",
    }

    for pillar, description in pillar_map.items():
        tested = any(
            pillar.lower() in r.pillar.lower()
            for r in results
        )
        marker = "[TESTED]" if tested else "[MANUAL]"
        print(f"  {marker:10s} {pillar:16s}: {description}")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    _section("Summary")
    print("  Governance policies become executable tests that run in CI/CD.")
    print("  Each AGILITY pillar maps to one or more test methods.")
    print("  The ImmutableAuditLog provides tamper-evident logging with")
    print("  SHA-256 hash chaining. Tampering with any entry breaks the")
    print("  chain, making modifications cryptographically detectable.")
    print()
    print(f"  Test results: {passed}/{len(results)} passed")
    print("\n=== Demo complete ===")
