"""
Module: Self-Healing CI/CD Pipeline
Concept: Memory-first failure classification and two-path learning
Chapter Reference: Section 11.3

The key insight from Section 11.3 is that memory is the difference between an
agent that investigates every failure from scratch and one that resolves known
patterns in milliseconds. This script makes that difference visible: the same
failure is handled twice, first through the slow LLM path and then through the
fast memory path, and the timings are printed side by side.

Key Patterns Demonstrated:
- classify_failure checks semantic memory before asking the LLM
- Confidence threshold (0.8) decides fast path vs slow path
- Remediation strategy selected per FailureType
- learn_from_incident: success -> semantic memory, failure -> episodic memory
- Compounding returns: the fast-path ratio rises as memory fills

The LLM call and the remediation actions are simulated so the script runs with
no API key and no cloud access. Swap _llm_classify for a real model call and
_run_remediation for real infrastructure calls to make this production code.
"""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class FailureType(Enum):
    """Failure classes from Section 11.3, each with its own remediation path."""
    TRANSIENT = "transient"           # Retry with backoff
    CONFIGURATION = "configuration"   # Analyze and fix (with approval)
    DEPENDENCY = "dependency"         # Wait and retry upstream
    CODE = "code"                     # Escalate to developers
    INFRASTRUCTURE = "infrastructure" # Failover or scale (with approval)
    UNKNOWN = "unknown"               # Escalate


@dataclass
class PipelineFailure:
    """A single pipeline step failure."""
    step: str
    error_message: str
    logs: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MemoryRecord:
    """One memory entry. Mirrors what a vector store returns for a query."""
    text: str
    confidence: float
    metadata: dict[str, Any] = field(default_factory=dict)
    summary: str = ""


class SimpleDevMemory:
    """
    Stand-in for DevMemory from Chapter 9.

    Chapter 9 builds this on a vector store with real embeddings. Here the
    similarity is keyword overlap so the example stays dependency-free, but the
    interface is the same one Section 11.3 calls: search_memory, learn_fact,
    remember_session.
    """

    def __init__(self) -> None:
        self.semantic: list[MemoryRecord] = []
        self.episodic: list[MemoryRecord] = []

    async def search_memory(
        self,
        query: str,
        memory_types: list[str],
        limit: int = 3,
    ) -> list[MemoryRecord]:
        """Return records ranked by similarity to the query."""
        await asyncio.sleep(0.05)  # memory lookup: tens of milliseconds
        pool: list[MemoryRecord] = []
        if "semantic" in memory_types:
            pool.extend(self.semantic)
        if "episodic" in memory_types:
            pool.extend(self.episodic)

        query_terms = set(self._tokenize(query))
        if not query_terms:
            return []

        scored: list[tuple[float, MemoryRecord]] = []
        for record in pool:
            record_terms = set(self._tokenize(record.text))
            if not record_terms:
                continue
            # How much of the query the record covers. A record that quotes the
            # error verbatim scores 1.0, which is what a vector store would also
            # return for near-identical text.
            coverage = len(query_terms & record_terms) / len(query_terms)
            if coverage == 0:
                continue
            # Stored confidence caps how much the match can be trusted.
            scored.append((coverage * record.confidence, record))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [
            MemoryRecord(
                text=record.text,
                confidence=round(score, 2),
                metadata=record.metadata,
                summary=record.summary or record.text,
            )
            for score, record in scored[:limit]
        ]

    async def learn_fact(
        self,
        fact: str,
        category: str,
        domain: str,
        confidence: float,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Store reusable knowledge in semantic memory."""
        record_metadata = {"category": category, "domain": domain}
        record_metadata.update(metadata or {})
        self.semantic.append(
            MemoryRecord(
                text=fact,
                confidence=confidence,
                metadata=record_metadata,
                summary=fact,
            )
        )

    async def remember_session(
        self,
        session_type: str,
        summary: str,
        details: str,
        outcome: str,
        project: str,
    ) -> None:
        """Store a full incident record in episodic memory."""
        self.episodic.append(
            MemoryRecord(
                text=f"{summary} {details}",
                confidence=0.6,
                metadata={
                    "session_type": session_type,
                    "outcome": outcome,
                    "project": project,
                },
                summary=summary,
            )
        )

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        cleaned = "".join(ch.lower() if ch.isalnum() else " " for ch in text)
        return [token for token in cleaned.split() if len(token) > 2]


class SelfHealingPipeline:
    """
    Pipeline that diagnoses and heals failures autonomously.

    In production the agent field holds a real LLM agent with classify_failure,
    lookup_remediation, execute_remediation, and retry_step registered as tools
    (see the SelfHealingPipeline listing in Section 11.3). This version keeps the
    same method names and control flow so the memory logic is easy to follow.
    """

    CONFIDENCE_THRESHOLD = 0.8

    # Remediation strategy per failure class, from the table in Section 11.3.
    STRATEGIES: dict[FailureType, str] = {
        FailureType.TRANSIENT: "retry_with_backoff",
        FailureType.CONFIGURATION: "apply_config_fix",
        FailureType.DEPENDENCY: "wait_for_upstream",
        FailureType.CODE: "escalate_to_developers",
        FailureType.INFRASTRUCTURE: "scale_or_failover",
        FailureType.UNKNOWN: "escalate_to_developers",
    }

    # Failure classes an agent may act on without a human in the loop.
    AUTONOMOUS = {
        FailureType.TRANSIENT,
        FailureType.CONFIGURATION,
        FailureType.DEPENDENCY,
    }

    def __init__(self, memory: SimpleDevMemory, project: str = "pipeline") -> None:
        self.memory = memory
        self.project = project
        self.fast_path_count = 0
        self.slow_path_count = 0

    async def handle_failure(self, failure: PipelineFailure) -> dict[str, Any]:
        """Classify, remediate, learn. This is the cycle Figure 11.3 shows."""
        started = time.perf_counter()

        failure_type, path, source = await self.classify_failure(
            failure.step, failure.error_message, failure.logs
        )
        remediation = await self.lookup_remediation(failure, failure_type)
        result = await self.execute_remediation(failure, failure_type, remediation)
        # Only novel failures need to be written back; a fast-path hit already
        # has its fact in memory and re-storing it just duplicates the record.
        if path == "slow":
            await self.learn_from_incident(failure, failure_type, result)

        elapsed_ms = (time.perf_counter() - started) * 1000
        return {
            "failure_type": failure_type.value,
            "path": path,
            "classification_source": source,
            "status": result["status"],
            "strategy": result.get("strategy"),
            "elapsed_ms": round(elapsed_ms, 1),
        }

    async def classify_failure(
        self, step: str, error: str, logs: str
    ) -> tuple[FailureType, str, str]:
        """
        Classify a failure, checking memory before spending tokens.

        Returns the failure type plus which path produced it, so the caller can
        report the fast-path ratio.
        """
        past = await self.memory.search_memory(
            query=error, memory_types=["semantic"], limit=3
        )
        if past and past[0].confidence > self.CONFIDENCE_THRESHOLD:
            # A stored classification is only usable if the record carries one.
            stored_type = past[0].metadata.get("failure_type")
            if stored_type:
                self.fast_path_count += 1
                return (
                    FailureType(stored_type),
                    "fast",
                    f"memory match (confidence={past[0].confidence})",
                )

        # No usable match: ask the LLM, sending only the tail of the logs.
        classification = await self._llm_classify(step, error, logs[-2000:])
        self.slow_path_count += 1
        return FailureType(classification), "slow", "llm classification"

    async def lookup_remediation(
        self, failure: PipelineFailure, failure_type: FailureType
    ) -> dict[str, Any]:
        """Prefer a remediation that memory already proved, else use the default."""
        matches = await self.memory.search_memory(
            query=failure.error_message, memory_types=["semantic"], limit=3
        )
        for match in matches:
            if match.confidence <= self.CONFIDENCE_THRESHOLD:
                continue
            strategy = match.metadata.get("strategy")
            if strategy:
                return {"strategy": strategy, "proven": True}
        return {"strategy": self.STRATEGIES[failure_type], "proven": False}

    async def execute_remediation(
        self,
        failure: PipelineFailure,
        failure_type: FailureType,
        remediation: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Run the chosen remediation, or escalate when the class needs a human.

        Replace the body with real calls (kubectl, terraform, cloud SDK, MCP
        tools) to make this act on live infrastructure.
        """
        strategy = remediation["strategy"]
        if failure_type not in self.AUTONOMOUS:
            return {
                "status": "escalated",
                "strategy": strategy,
                "detail": (
                    f"'{failure_type.value}' failures need a human: the agent "
                    f"reports, it does not act"
                ),
            }

        await asyncio.sleep(0.05)  # stands in for the remediation call
        return {
            "status": "success",
            "strategy": strategy,
            "detail": f"Applied {strategy} to step '{failure.step}'",
        }

    async def retry_step(self, step: str) -> dict[str, Any]:
        """Re-run a pipeline step after remediation."""
        await asyncio.sleep(0.05)
        return {"step": step, "status": "success"}

    async def learn_from_incident(
        self,
        failure: PipelineFailure,
        failure_type: FailureType,
        remediation_result: dict,
    ) -> None:
        """Two-path learning: success -> semantic, failure -> episodic."""
        if remediation_result["status"] == "success":
            await self.memory.learn_fact(
                fact=(
                    f"For '{failure.error_message}', "
                    f"strategy '{remediation_result.get('strategy')}' "
                    f"succeeded"
                ),
                category="remediation",
                domain="pipeline",
                confidence=0.9,
                # Carrying the class and strategy is what lets the next
                # classify_failure call skip the LLM entirely.
                metadata={
                    "failure_type": failure_type.value,
                    "strategy": remediation_result.get("strategy"),
                },
            )
        else:
            await self.memory.remember_session(
                session_type="failed_remediation",
                summary=f"Failed to remediate {failure.step}",
                details=str(remediation_result),
                outcome="failure",
                project=self.project,
            )

    async def _llm_classify(self, step: str, error: str, logs: str) -> str:
        """
        Stand-in for the LLM classification call.

        Real classification sends the step name, error message, and log tail to
        a model and takes seconds. The sleep below represents that latency so the
        fast-path saving is measurable; the keyword rules represent the answer.
        """
        await asyncio.sleep(1.2)

        lowered = error.lower()
        if any(k in lowered for k in ("timeout", "rate limit", "temporarily")):
            return FailureType.TRANSIENT.value
        if any(k in lowered for k in ("connection refused", "credential", "env var")):
            return FailureType.CONFIGURATION.value
        if any(k in lowered for k in ("unavailable", "version conflict", "upstream")):
            return FailureType.DEPENDENCY.value
        if any(k in lowered for k in ("assertion", "test failed", "compile")):
            return FailureType.CODE.value
        if any(k in lowered for k in ("out of memory", "no capacity", "region")):
            return FailureType.INFRASTRUCTURE.value
        return FailureType.UNKNOWN.value

    def path_report(self) -> dict[str, Any]:
        """Fast-path ratio. This is the number that climbs as memory fills."""
        total = self.fast_path_count + self.slow_path_count
        return {
            "total_failures": total,
            "fast_path": self.fast_path_count,
            "slow_path": self.slow_path_count,
            "fast_path_ratio": (
                round(self.fast_path_count / total, 2) if total else 0.0
            ),
        }


def seed_known_incident(memory: SimpleDevMemory) -> None:
    """
    Pre-load one incident the team already solved.

    This is what a pipeline agent's memory looks like after a few weeks: the
    error text, the class it belongs to, and the fix that worked. It is the
    incident from the Section 11.3 log. The fix changes the pipeline's own
    deploy configuration, which is what makes it safe to auto-apply; a fix
    that modified a security group would escalate for human approval instead.
    """
    memory.semantic.append(
        MemoryRecord(
            text=(
                "Connection refused to db-old.internal:5432 during "
                "deploy-staging: DB_HOST in staging deploy config still "
                "pointed at old endpoint after database migration"
            ),
            confidence=0.95,
            metadata={
                "failure_type": FailureType.CONFIGURATION.value,
                "strategy": "apply_config_fix",
            },
            summary=(
                "DB_HOST in staging deploy config still pointed at old "
                "endpoint after database migration"
            ),
        )
    )


async def main() -> None:
    print("=== Self-Healing Pipeline: the memory advantage ===\n")

    # ---- Run 1: novel failure, no memory to draw on -------------------------
    memory = SimpleDevMemory()
    pipeline = SelfHealingPipeline(memory)

    failure = PipelineFailure(
        step="deploy-staging",
        error_message="Connection refused to db-old.internal:5432",
        logs="...\nStep 7/12: Deploy to staging\nError: Connection refused\n",
    )

    print("Run 1: first encounter (memory is empty)")
    first = await pipeline.handle_failure(failure)
    print(f"  path:     {first['path']} ({first['classification_source']})")
    print(f"  class:    {first['failure_type']}")
    print(f"  strategy: {first['strategy']}")
    print(f"  status:   {first['status']}")
    print(f"  elapsed:  {first['elapsed_ms']} ms\n")

    # ---- Run 2: same failure, now the fix is in semantic memory -------------
    print("Run 2: same error, after learn_from_incident stored the fix")
    second = await pipeline.handle_failure(failure)
    print(f"  path:     {second['path']} ({second['classification_source']})")
    print(f"  class:    {second['failure_type']}")
    print(f"  strategy: {second['strategy']}")
    print(f"  status:   {second['status']}")
    print(f"  elapsed:  {second['elapsed_ms']} ms")

    speedup = first["elapsed_ms"] / max(second["elapsed_ms"], 0.1)
    print(f"\n  Fast path was {speedup:.0f}x quicker on identical input.\n")

    # ---- A mixed batch against seeded memory -------------------------------
    print("Batch: four failures against memory seeded with one known incident")
    seeded = SimpleDevMemory()
    seed_known_incident(seeded)
    batch_pipeline = SelfHealingPipeline(seeded)

    batch = [
        PipelineFailure(
            step="deploy-staging",
            error_message="Connection refused to db-old.internal:5432",
        ),
        PipelineFailure(
            step="integration-test",
            error_message="Request timeout calling payments sandbox",
        ),
        PipelineFailure(
            step="unit-test",
            error_message="Assertion failed in test_invoice_total",
        ),
        PipelineFailure(
            step="deploy-prod",
            error_message="Connection refused to db-old.internal:5432",
        ),
    ]

    for item in batch:
        outcome = await batch_pipeline.handle_failure(item)
        print(
            f"  {item.step:<18} {outcome['path']:<5} "
            f"{outcome['failure_type']:<14} {outcome['status']:<10} "
            f"{outcome['elapsed_ms']:>7} ms"
        )

    report = batch_pipeline.path_report()
    print(
        f"\n  {report['fast_path']} of {report['total_failures']} resolved from "
        f"memory (fast-path ratio {report['fast_path_ratio']})"
    )
    print(f"  semantic memory: {len(seeded.semantic)} proven fix(es)")
    print(f"  episodic memory: {len(seeded.episodic)} escalated incident(s)")

    print(
        "\nEvery slow-path resolution feeds memory, so the ratio above climbs "
        "with each incident the agent handles."
    )


if __name__ == "__main__":
    asyncio.run(main())
