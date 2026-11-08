"""
Memory scope management: agent-level and shared project scopes.

Reference: Chapter 9, Section 9.6 (Phase 3)
"""
from memory_core import DevMemory
from config import DevMemoryConfig


class ScopedMemory:
    """Memory with agent-level and shared project scopes.

    Agent-level memory belongs to one agent: a debugging agent's
    heuristics won't confuse a deployment agent. Shared project
    memory is visible to all agents on the project.
    """

    SHARED_SCOPE = "__project_shared__"

    def __init__(self, config: DevMemoryConfig):
        self.memory = DevMemory(config)
        self.project = config.project_name

    def remember_private(
        self, content: str, agent_id: str, metadata: dict = None
    ) -> dict:
        """Store in agent-level memory (visible only to this agent)."""
        meta = {"scope": "agent", **(metadata or {})}
        return self.memory.remember(content, agent_id=agent_id, metadata=meta)

    def remember_shared(
        self, content: str, agent_id: str, metadata: dict = None
    ) -> dict:
        """Store in shared project memory (visible to all agents)."""
        meta = {
            "scope": "project",
            "contributed_by": agent_id,
            **(metadata or {})
        }
        return self.memory.remember(
            content, agent_id=self.SHARED_SCOPE, metadata=meta
        )

    def recall_for_agent(
        self, query: str, agent_id: str, n_results: int = 5
    ) -> dict:
        """Read-through recall: agent scope first, then shared.

        TODO (Exercise 3): Implement this method.

        Steps:
        1. Query agent's private memories using self.memory.recall()
           with agent_id=agent_id
        2. Query shared project memories using self.memory.recall()
           with agent_id=self.SHARED_SCOPE
        3. Return dict with "agent" and "shared" keys

        This implements the read-through pattern from Section 9.5:
        check your own notes first, then the project knowledge base.

        Args:
            query: Search query.
            agent_id: Agent requesting recall.
            n_results: Max results per scope.

        Returns:
            dict: {"agent": [...], "shared": [...]}
        """
        # TODO: Implement read-through recall
        raise NotImplementedError("TODO: Implement recall_for_agent() in Exercise 3")
