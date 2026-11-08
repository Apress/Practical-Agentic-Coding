"""
Module: Agent Incident Response Procedures
Concept: Detection, containment, and learning loop for agent incidents
Chapter Reference: Chapter 12, Section 12.7

This example demonstrates a structured incident response lifecycle for
autonomous coding agents. When prevention fails, the system detects
anomalies, contains the damage, preserves state for forensics, and
turns every incident into a new guardrail through memory-based learning.

Key Patterns Demonstrated:
- Four-phase incident lifecycle (detect, contain, eradicate, recover)
- Anomaly signal classification by type and severity
- Emergency stop and rollback (simulated)
- State preservation for forensic analysis
- Memory-based learning loop (incident -> guardrail)
- Severity-based response escalation
"""

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class SignalType(Enum):
    """Types of anomaly signals that trigger incident response."""
    GUARDRAIL_VIOLATION = "guardrail_violation"
    ANOMALOUS_TOKEN_USAGE = "anomalous_token_usage"
    UNEXPECTED_TOOL_PATTERN = "unexpected_tool_pattern"
    OUTPUT_QUALITY_REGRESSION = "output_quality_regression"
    GOAL_DRIFT = "goal_drift"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    BUDGET_SPIKE = "budget_spike"
    USER_REPORT = "user_report"


class Severity(Enum):
    """Incident severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ContainmentAction(Enum):
    """Actions taken during containment phase."""
    EMERGENCY_STOP = "emergency_stop"
    ROLLBACK = "rollback"
    ISOLATE = "isolate"
    PRESERVE_STATE = "preserve_state"
    RATE_LIMIT = "rate_limit"
    REVOKE_PERMISSIONS = "revoke_permissions"
    NOTIFY_HUMAN = "notify_human"


@dataclass
class AnomalySignal:
    """A signal indicating potential agent misbehavior.

    Signals come from guardrail violations, anomalous resource usage,
    unexpected tool call patterns, or user reports.
    """
    signal_type: SignalType
    agent_id: str
    value: float = 0.0
    baseline: float = 0.0
    description: str = ""
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    metadata: dict = field(default_factory=dict)


@dataclass
class ContainmentRecord:
    """Record of a single containment action taken."""
    action: ContainmentAction
    target_agent: str
    success: bool
    duration_seconds: float
    details: str
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass
class IncidentReport:
    """Complete report of an incident from detection through containment.

    Produced by the IncidentResponder.detect_and_contain() method.
    Includes severity classification, containment actions taken,
    and the learning fact stored in memory.
    """
    incident_id: str
    severity: Severity
    signal: AnomalySignal
    contained: bool
    containment_actions: list[ContainmentRecord] = field(
        default_factory=list
    )
    learning_fact: str = ""
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    root_cause_hypothesis: str = ""
    recommended_followup: str = ""

    def summary(self) -> str:
        """Human-readable incident summary."""
        lines = [
            f"  Incident: {self.incident_id}",
            f"  Severity: {self.severity.value.upper()}",
            f"  Signal: {self.signal.signal_type.value} "
            f"from agent '{self.signal.agent_id}'",
            f"  Description: {self.signal.description}",
            f"  Contained: {self.contained}",
        ]
        if self.containment_actions:
            lines.append("  Containment actions:")
            for action in self.containment_actions:
                status = "OK" if action.success else "FAILED"
                lines.append(
                    f"    - {action.action.value}: {status} "
                    f"({action.duration_seconds:.3f}s)"
                )
                lines.append(f"      {action.details}")
        if self.learning_fact:
            lines.append(f"  Learning fact: {self.learning_fact}")
        if self.root_cause_hypothesis:
            lines.append(
                f"  Root cause hypothesis: {self.root_cause_hypothesis}"
            )
        if self.recommended_followup:
            lines.append(
                f"  Recommended followup: {self.recommended_followup}"
            )
        return "\n".join(lines)


class SimulatedMemory:
    """Simulated semantic memory for storing incident learning facts.

    In production, this integrates with the memory system from
    Chapter 9 (Section 9.5) to store facts that inform future
    governance checks.
    """

    def __init__(self) -> None:
        self.facts: list[dict] = []

    def learn_fact(
        self,
        fact: str,
        category: str,
        domain: str,
        confidence: float,
    ) -> None:
        """Store a learning fact in memory.

        Args:
            fact: The fact to store.
            category: Category (e.g., "incident", "pattern").
            domain: Domain (e.g., "governance", "security").
            confidence: Confidence score (0.0 to 1.0).
        """
        entry = {
            "fact": fact,
            "category": category,
            "domain": domain,
            "confidence": confidence,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.facts.append(entry)
        print(f"    [Memory] Stored: {fact}")
        print(f"             category={category}, domain={domain}, "
              f"confidence={confidence}")


class IncidentResponder:
    """Handles detection, containment, and learning for agent incidents.

    Implements the four-phase incident lifecycle:
    1. Detection: classify the anomaly signal
    2. Containment: stop damage based on severity
    3. Eradication: (manual, not automated)
    4. Recovery and Learning: store incident as guardrail

    The detect_and_contain() method handles phases 1, 2, and 4.
    Phase 3 (eradication / root cause analysis) requires human
    judgment and happens offline with preserved state.
    """

    def __init__(self, memory: Optional[SimulatedMemory] = None) -> None:
        self.memory = memory or SimulatedMemory()
        self.incidents: list[IncidentReport] = []
        self._incident_counter: int = 0

    def detect_and_contain(self, signal: AnomalySignal) -> IncidentReport:
        """Detection -> containment -> learning in one flow.

        Args:
            signal: The anomaly signal that triggered the response.

        Returns:
            Complete IncidentReport.
        """
        self._incident_counter += 1
        incident_id = (
            f"INC-{datetime.now(timezone.utc).strftime('%Y%m%d')}-"
            f"{self._incident_counter:04d}"
        )

        print(f"\n  --- Incident Response: {incident_id} ---")

        # Phase 1: Classify the signal
        severity = self._classify_severity(signal)
        print(f"  Phase 1 (Detect): severity={severity.value}, "
              f"type={signal.signal_type.value}")

        # Phase 2: Contain based on severity
        actions = self._contain(signal, severity)

        # Phase 4: Turn incident into guardrail (learning loop)
        learning_fact = (
            f"Agent '{signal.agent_id}' triggered "
            f"{signal.signal_type.value}: {signal.description}"
        )
        self.memory.learn_fact(
            fact=learning_fact,
            category="incident",
            domain="governance",
            confidence=1.0,
        )

        # Build report
        report = IncidentReport(
            incident_id=incident_id,
            severity=severity,
            signal=signal,
            contained=all(a.success for a in actions),
            containment_actions=actions,
            learning_fact=learning_fact,
            root_cause_hypothesis=self._hypothesize(signal),
            recommended_followup=self._recommend_followup(signal, severity),
        )
        self.incidents.append(report)
        return report

    def _classify_severity(self, signal: AnomalySignal) -> Severity:
        """Classify signal severity based on type and magnitude.

        Args:
            signal: The anomaly signal to classify.

        Returns:
            Severity level.
        """
        # Guardrail violations and unauthorized access are always critical
        if signal.signal_type in (
            SignalType.GUARDRAIL_VIOLATION,
            SignalType.UNAUTHORIZED_ACCESS,
        ):
            return Severity.CRITICAL

        # Token usage anomalies: severity based on deviation from baseline
        if signal.signal_type == SignalType.ANOMALOUS_TOKEN_USAGE:
            if signal.baseline > 0:
                ratio = signal.value / signal.baseline
                if ratio > 3.0:
                    return Severity.HIGH
                if ratio > 1.5:
                    return Severity.MEDIUM
            return Severity.LOW

        # Budget spikes
        if signal.signal_type == SignalType.BUDGET_SPIKE:
            if signal.value > signal.baseline * 2:
                return Severity.HIGH
            return Severity.MEDIUM

        # Goal drift
        if signal.signal_type == SignalType.GOAL_DRIFT:
            return Severity.MEDIUM

        # User reports default to high (humans usually report real issues)
        if signal.signal_type == SignalType.USER_REPORT:
            return Severity.HIGH

        return Severity.LOW

    def _contain(
        self, signal: AnomalySignal, severity: Severity
    ) -> list[ContainmentRecord]:
        """Execute containment actions based on severity.

        Args:
            signal: The anomaly signal.
            severity: Classified severity level.

        Returns:
            List of containment actions taken.
        """
        actions: list[ContainmentRecord] = []

        if severity in (Severity.CRITICAL, Severity.HIGH):
            # Emergency stop
            actions.append(self._emergency_stop(signal.agent_id))
            # Rollback changes
            actions.append(self._rollback_changes(signal.agent_id))
            # Preserve state for forensics
            actions.append(self._preserve_state(signal.agent_id))
            # Notify human
            actions.append(self._notify_human(signal, severity))

        elif severity == Severity.MEDIUM:
            # Rate limit the agent
            actions.append(self._rate_limit(signal.agent_id))
            # Preserve state
            actions.append(self._preserve_state(signal.agent_id))
            # Notify human (async)
            actions.append(self._notify_human(signal, severity))

        else:
            # Low severity: log and monitor
            actions.append(ContainmentRecord(
                action=ContainmentAction.NOTIFY_HUMAN,
                target_agent=signal.agent_id,
                success=True,
                duration_seconds=0.0,
                details="Low severity: logged for monitoring, no action needed",
            ))

        return actions

    def _emergency_stop(self, agent_id: str) -> ContainmentRecord:
        """Simulate emergency stop of an agent.

        Args:
            agent_id: The agent to stop.

        Returns:
            ContainmentRecord documenting the action.
        """
        start = time.time()
        # Simulate the stop (in production: docker stop, process kill, etc.)
        print(f"    [Containment] Emergency stop: agent '{agent_id}'")
        # Minimal latency simulation
        elapsed = time.time() - start
        return ContainmentRecord(
            action=ContainmentAction.EMERGENCY_STOP,
            target_agent=agent_id,
            success=True,
            duration_seconds=elapsed,
            details=f"Agent '{agent_id}' stopped via process termination",
        )

    def _rollback_changes(self, agent_id: str) -> ContainmentRecord:
        """Simulate rolling back changes made by an agent.

        Args:
            agent_id: The agent whose changes to roll back.

        Returns:
            ContainmentRecord documenting the action.
        """
        start = time.time()
        print(f"    [Containment] Rolling back changes by '{agent_id}'")
        # Simulate rollback (in production: git revert, terraform destroy, etc.)
        elapsed = time.time() - start
        return ContainmentRecord(
            action=ContainmentAction.ROLLBACK,
            target_agent=agent_id,
            success=True,
            duration_seconds=elapsed,
            details=f"Rolled back uncommitted changes by '{agent_id}'",
        )

    def _preserve_state(self, agent_id: str) -> ContainmentRecord:
        """Simulate preserving agent state for forensic analysis.

        Args:
            agent_id: The agent whose state to preserve.

        Returns:
            ContainmentRecord documenting the action.
        """
        start = time.time()
        print(f"    [Containment] Preserving state for '{agent_id}'")
        # Simulate state capture (context window, memory, logs)
        elapsed = time.time() - start
        return ContainmentRecord(
            action=ContainmentAction.PRESERVE_STATE,
            target_agent=agent_id,
            success=True,
            duration_seconds=elapsed,
            details=(
                f"Captured context window, memory snapshot, and "
                f"audit trail for '{agent_id}'"
            ),
        )

    def _rate_limit(self, agent_id: str) -> ContainmentRecord:
        """Simulate rate-limiting an agent.

        Args:
            agent_id: The agent to rate limit.

        Returns:
            ContainmentRecord documenting the action.
        """
        start = time.time()
        print(f"    [Containment] Rate-limiting agent '{agent_id}'")
        elapsed = time.time() - start
        return ContainmentRecord(
            action=ContainmentAction.RATE_LIMIT,
            target_agent=agent_id,
            success=True,
            duration_seconds=elapsed,
            details=f"Applied rate limit: max 5 calls/minute for '{agent_id}'",
        )

    def _notify_human(
        self, signal: AnomalySignal, severity: Severity
    ) -> ContainmentRecord:
        """Simulate notifying a human responder.

        Args:
            signal: The anomaly signal.
            severity: The classified severity.

        Returns:
            ContainmentRecord documenting the notification.
        """
        start = time.time()
        channel = "PagerDuty" if severity == Severity.CRITICAL else "Slack"
        print(f"    [Containment] Notifying human via {channel}")
        elapsed = time.time() - start
        return ContainmentRecord(
            action=ContainmentAction.NOTIFY_HUMAN,
            target_agent=signal.agent_id,
            success=True,
            duration_seconds=elapsed,
            details=(
                f"Sent {severity.value} alert to {channel} for "
                f"agent '{signal.agent_id}'"
            ),
        )

    def _hypothesize(self, signal: AnomalySignal) -> str:
        """Generate a root cause hypothesis based on signal type.

        Args:
            signal: The anomaly signal.

        Returns:
            Human-readable hypothesis string.
        """
        hypotheses = {
            SignalType.GUARDRAIL_VIOLATION: (
                "Agent attempted action outside defined boundaries. "
                "Possible prompt injection or context pollution."
            ),
            SignalType.ANOMALOUS_TOKEN_USAGE: (
                "Token consumption deviated from baseline. "
                "Possible infinite loop or excessive reasoning chain."
            ),
            SignalType.UNEXPECTED_TOOL_PATTERN: (
                "Agent used tools in an unexpected sequence. "
                "Possible goal drift or compromised context."
            ),
            SignalType.OUTPUT_QUALITY_REGRESSION: (
                "Agent output quality dropped below threshold. "
                "Possible model degradation or context window overflow."
            ),
            SignalType.GOAL_DRIFT: (
                "Agent alignment with specification decayed over session. "
                "Specification re-injection may have been missed."
            ),
            SignalType.UNAUTHORIZED_ACCESS: (
                "Agent accessed resources outside its permission scope. "
                "Possible privilege escalation or injection attack."
            ),
            SignalType.BUDGET_SPIKE: (
                "Resource consumption spiked unexpectedly. "
                "Possible runaway automation or recursive tool calls."
            ),
            SignalType.USER_REPORT: (
                "Human reported unexpected agent behavior. "
                "Manual investigation required."
            ),
        }
        return hypotheses.get(signal.signal_type, "Unknown signal type")

    def _recommend_followup(
        self, signal: AnomalySignal, severity: Severity
    ) -> str:
        """Recommend followup actions.

        Args:
            signal: The anomaly signal.
            severity: The classified severity.

        Returns:
            Recommended followup string.
        """
        if severity == Severity.CRITICAL:
            return (
                "1. Review full decision chain in audit trail. "
                "2. Check for prompt injection in input sources. "
                "3. Add new guardrail test before re-enabling agent. "
                "4. Conduct blameless post-mortem."
            )
        if severity == Severity.HIGH:
            return (
                "1. Review recent agent actions in audit trail. "
                "2. Tighten resource budgets. "
                "3. Add regression test for this signal pattern."
            )
        if severity == Severity.MEDIUM:
            return (
                "1. Monitor agent for recurrence. "
                "2. Consider reducing autonomy level. "
                "3. Log for weekly governance review."
            )
        return "1. Log for trend analysis. 2. No immediate action required."

    def incident_summary(self) -> str:
        """Return a summary of all incidents handled."""
        if not self.incidents:
            return "  No incidents recorded."

        lines = [f"  Total incidents: {len(self.incidents)}"]
        severity_counts: dict[str, int] = {}
        for inc in self.incidents:
            key = inc.severity.value
            severity_counts[key] = severity_counts.get(key, 0) + 1

        for sev in ["critical", "high", "medium", "low"]:
            count = severity_counts.get(sev, 0)
            if count:
                lines.append(f"    {sev.upper():>10s}: {count}")

        contained = sum(1 for i in self.incidents if i.contained)
        lines.append(f"  Contained: {contained}/{len(self.incidents)}")
        lines.append(f"  Learning facts stored: {len(self.memory.facts)}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------


def _section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    print("=== Incident Response Demo ===")
    print("Chapter 12, Section 12.7\n")

    memory = SimulatedMemory()
    responder = IncidentResponder(memory=memory)

    # ------------------------------------------------------------------
    # Scenario 1: Critical guardrail violation
    # ------------------------------------------------------------------
    _section("Scenario 1: Guardrail Violation (CRITICAL)")

    signal_1 = AnomalySignal(
        signal_type=SignalType.GUARDRAIL_VIOLATION,
        agent_id="code-generator-prod",
        description=(
            "Agent attempted to write to /etc/passwd. "
            "Path restriction validator blocked the action."
        ),
    )
    report_1 = responder.detect_and_contain(signal_1)
    print()
    print(report_1.summary())

    # ------------------------------------------------------------------
    # Scenario 2: Anomalous token usage (HIGH)
    # ------------------------------------------------------------------
    _section("Scenario 2: Anomalous Token Usage (HIGH)")

    signal_2 = AnomalySignal(
        signal_type=SignalType.ANOMALOUS_TOKEN_USAGE,
        agent_id="refactoring-agent",
        value=45000,
        baseline=10000,
        description=(
            "Token usage at 4.5x baseline. Agent may be in an "
            "infinite reasoning loop."
        ),
    )
    report_2 = responder.detect_and_contain(signal_2)
    print()
    print(report_2.summary())

    # ------------------------------------------------------------------
    # Scenario 3: Goal drift detected (MEDIUM)
    # ------------------------------------------------------------------
    _section("Scenario 3: Goal Drift (MEDIUM)")

    signal_3 = AnomalySignal(
        signal_type=SignalType.GOAL_DRIFT,
        agent_id="feature-builder",
        value=0.45,
        baseline=0.85,
        description=(
            "Alignment score dropped from 0.85 to 0.45 over "
            "30 steps. Agent is modifying unrelated modules."
        ),
    )
    report_3 = responder.detect_and_contain(signal_3)
    print()
    print(report_3.summary())

    # ------------------------------------------------------------------
    # Scenario 4: Budget spike (MEDIUM)
    # ------------------------------------------------------------------
    _section("Scenario 4: Budget Spike (MEDIUM)")

    # $2.30 is below the 2x-baseline cutoff ($2.40), so the classifier
    # returns MEDIUM. At 2x or more it would escalate to HIGH.
    signal_4 = AnomalySignal(
        signal_type=SignalType.BUDGET_SPIKE,
        agent_id="test-generator",
        value=2.30,
        baseline=1.20,
        description=(
            "Cost spiked to $2.30 (baseline $1.20). Agent is "
            "generating excessive test permutations."
        ),
    )
    report_4 = responder.detect_and_contain(signal_4)
    print()
    print(report_4.summary())

    # ------------------------------------------------------------------
    # Scenario 5: Low severity output quality issue
    # ------------------------------------------------------------------
    _section("Scenario 5: Output Quality Regression (LOW)")

    signal_5 = AnomalySignal(
        signal_type=SignalType.OUTPUT_QUALITY_REGRESSION,
        agent_id="docs-agent",
        value=0.65,
        baseline=0.80,
        description=(
            "Documentation quality score dropped to 0.65 "
            "(threshold 0.70). Minor style degradation."
        ),
    )
    report_5 = responder.detect_and_contain(signal_5)
    print()
    print(report_5.summary())

    # ------------------------------------------------------------------
    # Overall summary
    # ------------------------------------------------------------------
    _section("Overall Incident Summary")
    print(responder.incident_summary())

    # ------------------------------------------------------------------
    # Memory (learning) contents
    # ------------------------------------------------------------------
    _section("Learning Facts in Memory")
    for i, fact in enumerate(memory.facts):
        print(f"  [{i}] {fact['fact']}")
        print(f"      category={fact['category']}, "
              f"domain={fact['domain']}")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    _section("Summary")
    print("  The incident response lifecycle turns failures into")
    print("  guardrails through a structured four-phase process:")
    print("    Phase 1: Detect and classify the anomaly signal")
    print("    Phase 2: Contain based on severity (stop, rollback, isolate)")
    print("    Phase 3: Eradicate (manual root cause analysis)")
    print("    Phase 4: Recover and learn (store in memory)")
    print()
    print("  Each incident produces a learning fact stored in semantic")
    print("  memory (Chapter 9), so future governance checks benefit")
    print("  from past failures. The system gets stronger with every")
    print("  incident.")
    print("\n=== Demo complete ===")
