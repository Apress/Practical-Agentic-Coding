"""
Module: Safety Contracts for Multi-Agent Systems
Concept: Compositional safety verification at agent boundaries
Chapter Reference: Chapter 12, Section 12.4

This example demonstrates safety contracts that declare what each agent
requires (preconditions) and guarantees (postconditions). The orchestrator
verifies compositional consistency by checking that upstream postconditions
satisfy downstream preconditions at every handoff.

DELIBERATE DEVIATION: the book's snippet has `verify_handoff` return a
plain `list[str]` of violation messages. This file returns a
`HandoffReport` instead: the same violations, plus the agent pair and a
`passed` property, so the pipeline-wide verification can print one
summary per handoff. The check logic is identical.

Key Patterns Demonstrated:
- Safety contracts with preconditions, postconditions, and invariants
- Handoff verification between agents in a pipeline
- Contract registry for centralized lookup
- Full pipeline verification detecting gaps in safety guarantees
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class HandoffViolation:
    """A single contract violation at an agent boundary."""
    upstream_agent: str
    downstream_agent: str
    missing_guarantee: str
    severity: str = "error"
    # Set when the handoff cannot be checked at all (no contract registered).
    detail: Optional[str] = None

    def __str__(self) -> str:
        if self.detail:
            return f"[{self.severity.upper()}] {self.detail}"
        return (
            f"[{self.severity.upper()}] {self.downstream_agent} requires "
            f"'{self.missing_guarantee}' but {self.upstream_agent} "
            f"does not guarantee it"
        )


@dataclass
class HandoffReport:
    """Report from verifying a handoff between two agents."""
    upstream_agent: str
    downstream_agent: str
    violations: list[HandoffViolation] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0

    def summary(self) -> str:
        if self.passed:
            return (
                f"  {self.upstream_agent} -> {self.downstream_agent}: "
                f"PASSED (all preconditions satisfied)"
            )
        lines = [
            f"  {self.upstream_agent} -> {self.downstream_agent}: "
            f"FAILED ({len(self.violations)} violation(s))"
        ]
        for v in self.violations:
            lines.append(f"    - {v}")
        for w in self.warnings:
            lines.append(f"    [WARN] {w}")
        return "\n".join(lines)


class SafetyContract:
    """Each agent declares safety invariants.

    The orchestrator verifies compositional consistency by checking
    that an upstream agent's postconditions (guarantees) satisfy the
    downstream agent's preconditions (requirements).

    This is the same principle as Design by Contract (DbC) applied
    to multi-agent system boundaries.
    """

    def __init__(self, agent_id: str, description: str = "") -> None:
        self.agent_id = agent_id
        self.description = description
        self.preconditions: list[str] = []
        self.postconditions: list[str] = []
        self.invariants: list[str] = []

    def requires(self, *conditions: str) -> "SafetyContract":
        """Add preconditions (what must be true before this agent acts).

        Args:
            conditions: One or more precondition descriptions.

        Returns:
            Self, for method chaining.
        """
        self.preconditions.extend(conditions)
        return self

    def guarantees(self, *conditions: str) -> "SafetyContract":
        """Add postconditions (what this agent guarantees after acting).

        Args:
            conditions: One or more postcondition descriptions.

        Returns:
            Self, for method chaining.
        """
        self.postconditions.extend(conditions)
        return self

    def maintains(self, *conditions: str) -> "SafetyContract":
        """Add invariants (what must remain true throughout).

        Args:
            conditions: One or more invariant descriptions.

        Returns:
            Self, for method chaining.
        """
        self.invariants.extend(conditions)
        return self

    def verify_handoff(
        self, upstream_contract: "SafetyContract"
    ) -> HandoffReport:
        """Check that upstream postconditions satisfy our preconditions.

        Args:
            upstream_contract: The contract of the agent handing off to us.

        Returns:
            HandoffReport with any violations found.
        """
        report = HandoffReport(
            upstream_agent=upstream_contract.agent_id,
            downstream_agent=self.agent_id,
        )

        for pre in self.preconditions:
            if pre not in upstream_contract.postconditions:
                report.violations.append(
                    HandoffViolation(
                        upstream_agent=upstream_contract.agent_id,
                        downstream_agent=self.agent_id,
                        missing_guarantee=pre,
                    )
                )

        # Check invariant compatibility
        for inv in self.invariants:
            if inv in upstream_contract.invariants:
                continue  # Both maintain it, good
            # Check if upstream might violate our invariant
            # (heuristic: if upstream doesn't declare it, warn)
            if inv not in upstream_contract.postconditions:
                report.warnings.append(
                    f"Invariant '{inv}' is not explicitly maintained "
                    f"by {upstream_contract.agent_id}"
                )

        return report

    def __repr__(self) -> str:
        return (
            f"SafetyContract('{self.agent_id}', "
            f"pre={len(self.preconditions)}, "
            f"post={len(self.postconditions)}, "
            f"inv={len(self.invariants)})"
        )


class ContractRegistry:
    """Registry for looking up safety contracts by agent_id.

    Provides centralized contract storage and pipeline-level
    verification across a sequence of agents.
    """

    def __init__(self) -> None:
        self._contracts: dict[str, SafetyContract] = {}

    def register(self, contract: SafetyContract) -> None:
        """Register a safety contract for an agent.

        Args:
            contract: The safety contract to register.
        """
        self._contracts[contract.agent_id] = contract

    def get(self, agent_id: str) -> Optional[SafetyContract]:
        """Look up a contract by agent_id.

        Args:
            agent_id: The identifier of the agent.

        Returns:
            The SafetyContract, or None if not registered.
        """
        return self._contracts.get(agent_id)

    def verify_pipeline(
        self, agent_ids: list[str]
    ) -> list[HandoffReport]:
        """Verify all handoffs in a pipeline of agents.

        Checks each consecutive pair: agent[i] -> agent[i+1].

        Args:
            agent_ids: Ordered list of agent identifiers in the pipeline.

        Returns:
            List of HandoffReports, one per handoff.
        """
        reports: list[HandoffReport] = []
        for i in range(len(agent_ids) - 1):
            upstream = self._contracts.get(agent_ids[i])
            downstream = self._contracts.get(agent_ids[i + 1])

            if upstream is None or downstream is None:
                missing = agent_ids[i] if upstream is None else agent_ids[i + 1]
                report = HandoffReport(
                    upstream_agent=agent_ids[i],
                    downstream_agent=agent_ids[i + 1],
                )
                report.violations.append(
                    HandoffViolation(
                        upstream_agent=agent_ids[i],
                        downstream_agent=agent_ids[i + 1],
                        missing_guarantee="(no contract registered)",
                        severity="error",
                        detail=(
                            f"No safety contract registered for '{missing}', "
                            f"so the handoff {agent_ids[i]} -> "
                            f"{agent_ids[i + 1]} cannot be verified"
                        ),
                    )
                )
                reports.append(report)
                continue

            report = downstream.verify_handoff(upstream)
            reports.append(report)

        return reports

    def list_agents(self) -> list[str]:
        """Return all registered agent IDs."""
        return list(self._contracts.keys())


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------


def _section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    print("=== Safety Contracts Demo ===")
    print("Chapter 12, Section 12.4\n")

    # ------------------------------------------------------------------
    # Define contracts for a three-agent coding pipeline
    # ------------------------------------------------------------------
    _section("1. Defining Agent Safety Contracts")

    # Code generator contract
    code_gen = SafetyContract("code-generator", "Generates source code from specs")
    code_gen.requires(
        "input_sanitized",
        "task_specification_provided",
    )
    code_gen.guarantees(
        "input_sanitized",
        "code_compiles",
        "no_hardcoded_credentials",
        "type_annotations_present",
        "code_follows_project_style",
    )
    code_gen.maintains(
        "no_pii_in_output",
        "no_hardcoded_credentials",
    )
    print(f"  {code_gen}")
    print(f"    Requires: {code_gen.preconditions}")
    print(f"    Guarantees: {code_gen.postconditions}")

    # Test generator contract
    test_gen = SafetyContract("test-generator", "Generates tests for code")
    test_gen.requires(
        "code_compiles",
        "type_annotations_present",
        "no_hardcoded_credentials",
    )
    test_gen.guarantees(
        "code_compiles",
        "tests_pass",
        "coverage_above_80_percent",
        "no_hardcoded_credentials",
        "edge_cases_covered",
    )
    test_gen.maintains(
        "no_pii_in_output",
        "no_hardcoded_credentials",
    )
    print(f"\n  {test_gen}")
    print(f"    Requires: {test_gen.preconditions}")
    print(f"    Guarantees: {test_gen.postconditions}")

    # Code reviewer contract
    code_reviewer = SafetyContract("code-reviewer", "Reviews code for quality and safety")
    code_reviewer.requires(
        "code_compiles",
        "tests_pass",
        "coverage_above_80_percent",
        "no_hardcoded_credentials",
    )
    code_reviewer.guarantees(
        "code_compiles",
        "tests_pass",
        "coverage_above_80_percent",
        "no_hardcoded_credentials",
        "no_known_vulnerabilities",
        "review_comments_provided",
    )
    code_reviewer.maintains(
        "no_pii_in_output",
        "no_hardcoded_credentials",
    )
    print(f"\n  {code_reviewer}")
    print(f"    Requires: {code_reviewer.preconditions}")
    print(f"    Guarantees: {code_reviewer.postconditions}")

    # ------------------------------------------------------------------
    # Register contracts and verify pipeline
    # ------------------------------------------------------------------
    _section("2. Verifying Pipeline: code-generator -> test-generator -> code-reviewer")

    registry = ContractRegistry()
    registry.register(code_gen)
    registry.register(test_gen)
    registry.register(code_reviewer)

    pipeline = ["code-generator", "test-generator", "code-reviewer"]
    reports = registry.verify_pipeline(pipeline)

    all_passed = True
    for report in reports:
        print(report.summary())
        if not report.passed:
            all_passed = False

    if all_passed:
        print("\n  Pipeline verification: ALL HANDOFFS PASSED")
    else:
        print("\n  Pipeline verification: VIOLATIONS DETECTED")

    # ------------------------------------------------------------------
    # Demonstrate a contract violation
    # ------------------------------------------------------------------
    _section("3. Introducing a Contract Gap")

    # Create a weaker code generator that does NOT guarantee type annotations
    weak_code_gen = SafetyContract("weak-code-generator", "Generates code without types")
    weak_code_gen.requires(
        "input_sanitized",
        "task_specification_provided",
    )
    weak_code_gen.guarantees(
        "input_sanitized",
        "code_compiles",
        "no_hardcoded_credentials",
        # Missing: "type_annotations_present"
        # Missing: "code_follows_project_style"
    )
    weak_code_gen.maintains(
        "no_pii_in_output",
    )

    print("  Replaced code-generator with weak-code-generator")
    print("  (does NOT guarantee 'type_annotations_present')")

    registry.register(weak_code_gen)
    weak_pipeline = ["weak-code-generator", "test-generator", "code-reviewer"]
    reports = registry.verify_pipeline(weak_pipeline)

    print()
    for report in reports:
        print(report.summary())

    # ------------------------------------------------------------------
    # Demonstrate missing agent in pipeline
    # ------------------------------------------------------------------
    _section("4. Missing Agent Contract")

    missing_pipeline = ["code-generator", "security-scanner", "code-reviewer"]
    reports = registry.verify_pipeline(missing_pipeline)

    for report in reports:
        print(report.summary())

    # ------------------------------------------------------------------
    # Show individual handoff verification
    # ------------------------------------------------------------------
    _section("5. Direct Handoff Verification")

    print("  Checking: code-generator -> code-reviewer (skipping test-generator)")
    report = code_reviewer.verify_handoff(code_gen)
    print(report.summary())
    if not report.passed:
        print("\n  The code-reviewer requires tests_pass and")
        print("  coverage_above_80_percent, which the code-generator")
        print("  does not guarantee. The test-generator is needed in between.")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    _section("Summary")
    print("  Safety contracts make agent boundary expectations explicit.")
    print("  Each agent declares:")
    print("    - Preconditions: what must be true before it acts")
    print("    - Postconditions: what it guarantees after acting")
    print("    - Invariants: what it preserves throughout")
    print()
    print("  The orchestrator verifies at every handoff that upstream")
    print("  guarantees satisfy downstream requirements. Violations")
    print("  are caught at design time, before agents run.")
    print("\n=== Demo complete ===")
