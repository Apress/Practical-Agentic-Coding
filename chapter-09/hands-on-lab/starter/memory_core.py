"""
DevMemory: Cognitive memory system using Mem0 for orchestration.

This is the main memory class that students will implement.
Mem0 handles deduplication, conflict detection, and update logic.
ChromaDB provides the vector storage backend.

Reference: Chapter 9, Section 9.6 (Phase 1)
"""
from collections import Counter  # used by PatternMiner (Exercise 4)

from mem0 import Memory
from config import DevMemoryConfig


class DevMemory:
    """Cognitive memory system using Mem0 for orchestration."""

    def __init__(self, config: DevMemoryConfig):
        self.config = config
        mem0_config = {
            "vector_store": {
                "provider": "chroma",
                "config": {
                    "collection_name": f"devmemory_{config.project_name}",
                    "host": config.chromadb_host,
                    "port": config.chromadb_port,
                }
            },
            # As of November 7, 2026, OpenAI does not serve Mem0 1.x's default
            # LLM, gpt-4.1-nano-2025-04-14, so name a current model here.
            "llm": {"provider": "openai", "config": {"model": "gpt-5.6-luna"}},
        }
        self.memory = Memory.from_config(mem0_config)

    def remember(
        self,
        content: str,
        agent_id: str,
        metadata: dict = None,
        infer: bool = True
    ) -> dict:
        """Store a memory through Mem0's orchestration layer.

        TODO (Exercise 1): Implement this method.

        Steps:
        1. Call self.memory.add() with content, user_id=agent_id,
           metadata, and infer=infer
        2. Return the result

        By default Mem0 extracts key facts and handles deduplication
        and conflict detection. Callers pass infer=False to store
        content verbatim: episodic records must survive word for word
        so Pattern Mining can count repeats.

        Args:
            content: Text content to remember.
            agent_id: Identifier for the agent storing this memory.
            metadata: Optional metadata dict.
            infer: Pass through to Mem0. False stores content verbatim.

        Returns:
            dict: Result from Mem0 including memory ID.
        """
        # TODO: Implement - call self.memory.add()
        raise NotImplementedError("TODO: Implement remember() in Exercise 1")

    def recall(
        self,
        query: str,
        agent_id: str = None,
        n_results: int = 5
    ) -> list:
        """Retrieve relevant memories by semantic similarity.

        TODO (Exercise 1): Implement this method.

        Steps:
        1. Call self.memory.search() with query, user_id=agent_id, limit=n_results
        2. Mem0 returns a dict with the matches under a "results" key.
           Unwrap it and return the plain list:
           response.get("results", [])

        Args:
            query: Search query.
            agent_id: Filter to specific agent (optional).
            n_results: Maximum number of results.

        Returns:
            list: Matching memories sorted by relevance.
        """
        # TODO: Implement - call self.memory.search()
        raise NotImplementedError("TODO: Implement recall() in Exercise 1")

    def recall_all(self, agent_id: str) -> list:
        """Get all memories for an agent.

        TODO (Exercise 1): Implement this method.

        Steps:
        1. Call self.memory.get_all() with user_id=agent_id
        2. Like search(), get_all() returns a dict with a "results" key.
           Unwrap it and return the plain list:
           self.memory.get_all(user_id=agent_id).get("results", [])

        Args:
            agent_id: Agent identifier.

        Returns:
            list: All memories for this agent.
        """
        # TODO: Implement - call self.memory.get_all()
        raise NotImplementedError("TODO: Implement recall_all() in Exercise 1")


class PatternMiner:
    """Consolidates episodic memories into semantic knowledge.

    Reference: Chapter 9, Section 9.6 (Phase 4)
    """

    def __init__(self, memory: DevMemory, config: DevMemoryConfig):
        self.memory = memory
        self.config = config

    def mine(self, agent_id: str) -> list[dict]:
        """Extract patterns from an agent's episodic memories.

        TODO (Exercise 4): Implement this method.

        Steps:
        1. Get all episodes using self.memory.recall_all(agent_id)
        2. Filter to episodes only (metadata.type == "episode")
        3. Check if there are enough episodes (>= consolidation_min_episodes)
        4. Group episodes by session_type
        5. For each group with enough episodes, call _extract_pattern()
        6. Store discovered patterns as semantic knowledge using self.memory.remember()
        7. Return list of discovered patterns

        Args:
            agent_id: Agent whose memories to mine.

        Returns:
            list[dict]: Discovered patterns with knowledge and confidence.
        """
        # TODO: Implement pattern mining
        raise NotImplementedError("TODO: Implement mine() in Exercise 4")

    def _extract_pattern(
        self, session_type: str, episodes: list[dict]
    ) -> dict:
        """Extract a semantic pattern from a group of episodes.

        TODO (Exercise 4): Implement this method.

        Steps:
        1. Filter to successful episodes (metadata.outcome == "success")
        2. Collect first_check values from successful episodes
        3. Find the most common first_check using Counter
        4. Calculate confidence as frequency / total successful
        5. Return dict with knowledge string, confidence, and episode_count

        Args:
            session_type: Type of sessions in this group.
            episodes: List of episode memories.

        Returns:
            dict: Pattern with "knowledge", "confidence", "episode_count" keys.
                  Returns None if no pattern found.
        """
        # TODO: Implement pattern extraction
        raise NotImplementedError("TODO: Implement _extract_pattern() in Exercise 4")
