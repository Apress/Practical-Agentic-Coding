"""
Listing 4-5: Simple model router for task-appropriate model selection

This example demonstrates dynamic model selection based on task characteristics.
Instead of hardcoding model names, production systems use routing logic to
select the most appropriate model for each subtask.

Key Concepts:
- Task-fit matching (reasoning vs. generation vs. RAG)
- Cost-quality tradeoffs
- Latency budget management
- Policy-driven routing

Usage:
    python model_router.py

"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import re


class TaskType(Enum):
    """Types of tasks that require different model capabilities."""
    REASONING = "reasoning"          # Complex problem solving
    GENERATION = "generation"        # Code/text generation
    CLASSIFICATION = "classification" # Categorization tasks
    RAG = "rag"                      # Retrieval-augmented generation
    SIMPLE = "simple"                # Basic tasks


class ModelTier(Enum):
    """Model tiers balancing capability and cost."""
    REASONING_HEAVY = "reasoning-heavy"   # frontier reasoning models
    BALANCED = "balanced"                 # mid-tier general-purpose models
    FAST_GENERATION = "fast-generation"   # small, fast, low-cost models
    EMBEDDING = "embedding"               # embedding models


@dataclass
class ModelConfig:
    """Configuration for a slot in the catalog.

    `name` is a slot identifier, not a vendor model ID. Section 4.3 of the
    book makes the case for this: hard-coded model names scattered through a
    codebase age badly, so treat models as interchangeable compute backends
    behind a capability abstraction. Bind each slot to a concrete model in
    configuration (see RoutingPolicy below), and change that binding without
    touching routing logic.
    """
    name: str
    tier: ModelTier
    cost_per_1k_tokens: float
    avg_latency_ms: int
    max_context_tokens: int
    strengths: List[str] = field(default_factory=list)


# Catalog of capability slots.
#
# The cost, latency, and context numbers below are illustrative placeholders so
# the routing logic has something to compare. Replace them with the published
# figures for whichever models you bind each slot to, and re-check them: vendor
# pricing, context windows, and model names all change on a scale of months.
MODEL_CATALOG: Dict[str, ModelConfig] = {
    "reasoning-primary": ModelConfig(
        name="reasoning-primary",
        tier=ModelTier.REASONING_HEAVY,
        cost_per_1k_tokens=0.075,
        avg_latency_ms=5000,
        max_context_tokens=200000,
        strengths=["reasoning", "debugging", "architecture"]
    ),
    "reasoning-secondary": ModelConfig(
        name="reasoning-secondary",
        tier=ModelTier.REASONING_HEAVY,
        cost_per_1k_tokens=0.06,
        avg_latency_ms=4500,
        max_context_tokens=200000,
        strengths=["reasoning", "analysis", "complex-tasks"]
    ),
    "balanced-primary": ModelConfig(
        name="balanced-primary",
        tier=ModelTier.BALANCED,
        cost_per_1k_tokens=0.015,
        avg_latency_ms=1500,
        max_context_tokens=200000,
        strengths=["coding", "general", "long-context"]
    ),
    "balanced-secondary": ModelConfig(
        name="balanced-secondary",
        tier=ModelTier.BALANCED,
        cost_per_1k_tokens=0.03,
        avg_latency_ms=2000,
        max_context_tokens=128000,
        strengths=["general", "coding", "analysis"]
    ),
    "fast-primary": ModelConfig(
        name="fast-primary",
        tier=ModelTier.FAST_GENERATION,
        cost_per_1k_tokens=0.0005,
        avg_latency_ms=400,
        max_context_tokens=200000,
        strengths=["fast", "simple-tasks", "cost-effective"]
    ),
    "fast-secondary": ModelConfig(
        name="fast-secondary",
        tier=ModelTier.FAST_GENERATION,
        cost_per_1k_tokens=0.00075,
        avg_latency_ms=500,
        max_context_tokens=128000,
        strengths=["fast", "simple-tasks", "bulk"]
    ),
}


def route_task(task_description):
    """
    Simple model router from Listing 4-5, exactly as printed in the book.

    Routes tasks to appropriate models based on keywords. The keyword check
    is case-sensitive, as in the listing, so callers pass a lowercased
    description (see demo_simple_router). In your own router, normalize case
    inside the function instead.

    Args:
        task_description: Description of the task

    Returns:
        Model identifier string
    """
    if "architect" in task_description or "debug" in task_description:
        return "model-reasoning-heavy"   # a frontier reasoning model
    elif "write documentation" in task_description:
        return "model-fast-generation"   # a small, fast, low-cost model
    else:
        return "model-balanced"   # a mid-tier general-purpose model


@dataclass
class RoutingPolicy:
    """
    Policy-driven routing configuration.

    This is an externalized, declarative approach that allows
    non-developers to influence routing decisions.
    """
    name: str
    description: str

    # Task type mappings
    task_patterns: Dict[str, TaskType] = field(default_factory=dict)

    # Tier mappings for task types
    tier_mappings: Dict[TaskType, ModelTier] = field(default_factory=dict)

    # Constraints. The cost ceiling is enforced against an estimated request
    # cost: cost_per_1k_tokens * assumed_request_tokens / 1000. Tune
    # assumed_request_tokens to your workload's typical prompt + output size.
    max_cost_per_request: float = 1.0
    max_latency_ms: int = 10000
    assumed_request_tokens: int = 4000

    # Fallback slot, used when no candidate meets the constraints
    fallback_model: str = "balanced-primary"


class AdvancedModelRouter:
    """
    Production-ready model router with policy-driven selection.

    Features:
    - Externalized policy management
    - Observability on every routing decision
    - Dynamic feedback and optimization
    """

    def __init__(self, policy: RoutingPolicy):
        """Initialize router with a routing policy."""
        self.policy = policy
        self.routing_history: List[Dict[str, Any]] = []

    def classify_task(self, task_description: str) -> TaskType:
        """
        Classify a task based on description patterns.

        Args:
            task_description: Description of the task

        Returns:
            Classified TaskType
        """
        task_lower = task_description.lower()

        # Check policy patterns first
        for pattern, task_type in self.policy.task_patterns.items():
            if re.search(pattern, task_lower):
                return task_type

        # Default classification based on keywords
        if any(kw in task_lower for kw in ["architect", "debug", "design", "analyze"]):
            return TaskType.REASONING
        elif any(kw in task_lower for kw in ["write", "generate", "create", "draft"]):
            return TaskType.GENERATION
        elif any(kw in task_lower for kw in ["classify", "categorize", "label"]):
            return TaskType.CLASSIFICATION
        elif any(kw in task_lower for kw in ["search", "find", "retrieve"]):
            return TaskType.RAG
        else:
            return TaskType.SIMPLE

    def select_model(
        self,
        task_description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ModelConfig:
        """
        Select the most appropriate model for a task.

        Args:
            task_description: Description of the task
            metadata: Optional metadata (user_id, priority, etc.)

        Returns:
            Selected ModelConfig
        """
        metadata = metadata or {}

        # Classify the task
        task_type = self.classify_task(task_description)

        # Get target tier from policy
        target_tier = self.policy.tier_mappings.get(
            task_type,
            ModelTier.BALANCED  # Default tier
        )

        # Filter models by tier and constraints (latency AND cost ceiling)
        candidates = [
            model for model in MODEL_CATALOG.values()
            if model.tier == target_tier
            and model.avg_latency_ms <= self.policy.max_latency_ms
            and self._estimated_request_cost(model) <= self.policy.max_cost_per_request
        ]

        if not candidates:
            # No candidate in the target tier satisfies the policy's cost and
            # latency ceilings: route to the fallback slot, and log that the
            # constraints (not the task type) drove the decision.
            selected = MODEL_CATALOG[self.policy.fallback_model]
            self._log_routing_decision(
                task_description, task_type, selected, metadata, fallback=True
            )
            return selected

        # Select based on cost (could be more sophisticated)
        selected = min(candidates, key=lambda m: m.cost_per_1k_tokens)

        # Log routing decision
        self._log_routing_decision(task_description, task_type, selected, metadata)

        return selected

    def _estimated_request_cost(self, model: ModelConfig) -> float:
        """Estimate the cost of one request against this model."""
        return model.cost_per_1k_tokens * self.policy.assumed_request_tokens / 1000

    def _log_routing_decision(
        self,
        task_description: str,
        task_type: TaskType,
        selected_model: ModelConfig,
        metadata: Dict[str, Any],
        fallback: bool = False
    ):
        """Log routing decision for observability."""
        decision = {
            "task_description": task_description[:100],
            "task_type": task_type.value,
            "selected_model": selected_model.name,
            "model_tier": selected_model.tier.value,
            "estimated_cost": self._estimated_request_cost(selected_model),
            "estimated_latency_ms": selected_model.avg_latency_ms,
            "constraint_fallback": fallback,
            "metadata": metadata,
        }
        self.routing_history.append(decision)
        note = " (cost/latency ceiling hit, using fallback)" if fallback else ""
        print(f"[Router] Task: {task_type.value} -> Model: {selected_model.name}{note}")

    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics for optimization."""
        if not self.routing_history:
            return {"total_requests": 0}

        model_counts = {}
        tier_counts = {}
        total_cost = 0

        for decision in self.routing_history:
            model = decision["selected_model"]
            tier = decision["model_tier"]

            model_counts[model] = model_counts.get(model, 0) + 1
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
            total_cost += decision["estimated_cost"]

        return {
            "total_requests": len(self.routing_history),
            "model_distribution": model_counts,
            "tier_distribution": tier_counts,
            "estimated_total_cost": total_cost,
        }


def demo_simple_router():
    """Demonstrate the simple router from Listing 4-5."""
    print("=" * 60)
    print("DEMO: Simple Model Router (Listing 4-5)")
    print("=" * 60)

    tasks = [
        "Architect a new microservices system",
        "Debug the race condition in the payment module",
        "Write documentation for the API endpoints",
        "Generate unit tests for the user service",
        "Review this pull request",
    ]

    for task in tasks:
        # The listing matches lowercase keywords case-sensitively, so
        # normalize first; "Architect ..." would otherwise miss "architect".
        model = route_task(task.lower())
        print(f"Task: {task[:50]:<50} -> {model}")


def demo_advanced_router():
    """Demonstrate the advanced policy-driven router."""
    print("\n" + "=" * 60)
    print("DEMO: Advanced Policy-Driven Router")
    print("=" * 60)

    # Create a routing policy
    policy = RoutingPolicy(
        name="enterprise-policy",
        description="Enterprise routing with cost controls",
        task_patterns={
            r"security|vulnerability|audit": TaskType.REASONING,
            r"test|unittest": TaskType.GENERATION,
            r"boilerplate|scaffold": TaskType.SIMPLE,
        },
        tier_mappings={
            TaskType.REASONING: ModelTier.REASONING_HEAVY,
            TaskType.GENERATION: ModelTier.BALANCED,
            TaskType.CLASSIFICATION: ModelTier.FAST_GENERATION,
            TaskType.RAG: ModelTier.BALANCED,
            TaskType.SIMPLE: ModelTier.FAST_GENERATION,
        },
        max_cost_per_request=0.10,
        max_latency_ms=8000,
    )

    # Create router
    router = AdvancedModelRouter(policy)

    # Route various tasks
    tasks = [
        "Architect a distributed caching layer",
        "Write boilerplate CRUD endpoints",
        "Perform security audit of authentication",
        "Generate unit tests for OrderService",
        "Classify these support tickets by urgency",
        "Search the codebase for deprecated API usage",
    ]

    # With max_cost_per_request=0.10 and assumed_request_tokens=4000, the
    # reasoning-tier models (estimated $0.24-$0.30 per request) exceed the
    # ceiling, so reasoning tasks route to the fallback slot: the cost control
    # visibly overrides the tier preference.
    print("\nRouting decisions:")
    print("-" * 60)

    for task in tasks:
        router.select_model(task, metadata={"user": "dev-team"})

    # Show statistics
    print("\n" + "-" * 60)
    print("Routing Statistics:")
    stats = router.get_routing_stats()
    print(f"  Total requests: {stats['total_requests']}")
    print(f"  Model distribution: {stats['model_distribution']}")
    print(f"  Tier distribution: {stats['tier_distribution']}")


def main():
    """Run all demonstrations."""
    demo_simple_router()
    demo_advanced_router()

    print("\n" + "=" * 60)
    print("KEY TAKEAWAYS")
    print("=" * 60)
    print("""
1. MODEL SELECTION is task-dependent
   - Reasoning tasks need powerful models
   - Simple tasks can use fast, cheap models

2. EXTERNALIZE routing policies
   - Define rules in YAML/JSON, not code
   - Allow non-developers to tune routing

3. OBSERVE all routing decisions
   - Log model, cost, latency for each request
   - Use data to optimize routing over time

4. IMPLEMENT feedback loops
   - If fast model fails, route to powerful model
   - If powerful model is overkill, downshift
""")


if __name__ == "__main__":
    main()
