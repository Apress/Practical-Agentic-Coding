"""
DevMemory integration for deployment history and decision-making.

This module provides integration with DevMemory from Chapter 9.
For the lab, we provide a simplified memory interface.
"""

from typing import Dict, List, Optional
from datetime import datetime
import json
import os
from pathlib import Path


class DeploymentMemory:
    """
    Simplified memory interface for deployment history.

    In production, this would integrate with DevMemory from Chapter 9:
    - Episodic memory: Past deployment successes/failures
    - Semantic memory: Patterns and best practices
    - Procedural memory: Learned deployment workflows

    For this lab, we use a simplified file-based implementation.
    """

    def __init__(self, persist_dir: Optional[str] = None):
        """
        Initialize deployment memory.

        Args:
            persist_dir: Directory to persist memory. Defaults to
                MEMORY_PERSIST_DIR from .env, or ./data/memory if unset.
        """
        if persist_dir is None:
            persist_dir = os.getenv("MEMORY_PERSIST_DIR", "./data/memory")
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.memory_file = self.persist_dir / "deployments.json"
        self._load_memory()

    def _load_memory(self):
        """Load memory from disk."""
        if self.memory_file.exists():
            with open(self.memory_file, "r") as f:
                self.memories = json.load(f)
        else:
            self.memories = {}
        # The canonical buckets always exist, even in a hand-edited file
        for bucket in ("deployments", "rollbacks", "incidents"):
            self.memories.setdefault(bucket, [])

    def _save_memory(self):
        """Save memory to disk."""
        with open(self.memory_file, "w") as f:
            json.dump(self.memories, f, indent=2)

    async def recall(
        self,
        query: str,
        n_results: int = 5,
        memory_type: str = "episodic"
    ) -> Dict:
        """
        Recall relevant memories.

        Args:
            query: Search query (e.g., "deployment failure api-service")
            n_results: Number of results to return
            memory_type: Type of memory (episodic, semantic, procedural)

        Returns:
            Dictionary with:
            - episodic: List of past events
            - semantic: List of patterns/concepts
            - procedural: List of learned workflows
        """
        # Simple keyword search for lab
        # Production would use vector similarity
        results = {"episodic": [], "semantic": [], "procedural": []}

        query_words = query.lower().split()

        # Search every bucket (deployments, rollbacks, incidents, and any
        # custom session types such as the challenge lab's
        # multi_service_deployment records)
        for records in self.memories.values():
            for record in records:
                summary = record.get("summary", "").lower()
                if any(word in summary for word in query_words):
                    results["episodic"].append(record)
                    if len(results["episodic"]) >= n_results:
                        return results

        return results

    async def remember_session(
        self,
        session_type: str,
        summary: str,
        outcome: str,
        project: str,
        details: str = "",
        metadata: Optional[Dict] = None
    ):
        """
        Remember a deployment session.

        All callers in the lab pass keyword arguments; `details` is optional
        so the shorter call shown in the book (summary/outcome/project only)
        also works.

        Args:
            session_type: Type (deployment, rollback, incident, or a custom type)
            summary: Brief summary
            outcome: Result (success, failure, partial, critical_failure)
            project: Project/service name
            details: Detailed information (optional)
            metadata: Additional metadata
        """
        memory = {
            "session_type": session_type,
            "summary": summary,
            "details": details,
            "outcome": outcome,
            "project": project,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }

        # Store by type. Known types map to their canonical bucket; any other
        # type (e.g. the challenge lab's "multi_service_deployment") gets its
        # own bucket so no record is ever silently dropped.
        bucket = {
            "deployment": "deployments",
            "rollback": "rollbacks",
            "incident": "incidents",
        }.get(session_type, session_type)
        self.memories.setdefault(bucket, []).append(memory)

        # Keep only recent memories (last 100 per bucket)
        for bucket_name in self.memories:
            if len(self.memories[bucket_name]) > 100:
                self.memories[bucket_name] = self.memories[bucket_name][-100:]

        self._save_memory()

    async def get_service_history(
        self,
        service_name: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get deployment history for a service.

        Args:
            service_name: Service name
            limit: Maximum results

        Returns:
            List of deployment records
        """
        history = []

        for deployment in reversed(self.memories["deployments"]):
            if deployment.get("project") == service_name:
                history.append(deployment)
                if len(history) >= limit:
                    break

        return history

    async def get_failure_patterns(
        self,
        service_name: Optional[str] = None
    ) -> Dict:
        """
        Analyze failure patterns.

        Args:
            service_name: Optional service name to filter

        Returns:
            Dictionary of failure statistics and patterns
        """
        failures = []
        rollbacks = []

        # Collect failures
        for deployment in self.memories["deployments"]:
            if deployment.get("outcome") in ["failure", "partial"]:
                if not service_name or deployment.get("project") == service_name:
                    failures.append(deployment)

        # Collect rollbacks
        for rollback in self.memories["rollbacks"]:
            if not service_name or rollback.get("project") == service_name:
                rollbacks.append(rollback)

        return {
            "total_failures": len(failures),
            "total_rollbacks": len(rollbacks),
            "recent_failures": failures[:5],
            "recent_rollbacks": rollbacks[:5],
            "failure_rate": len(failures) / max(len(self.memories["deployments"]), 1)
        }


# For integration with full DevMemory from Chapter 9
class DevMemoryAdapter:
    """
    Adapter for full DevMemory from Chapter 9.

    If readers have completed Chapter 9, they can use this adapter
    to integrate the full DevMemory system.
    """

    def __init__(self, devmemory_instance):
        """
        Initialize with DevMemory instance.

        Args:
            devmemory_instance: DevMemory instance from Chapter 9
        """
        self.devmemory = devmemory_instance

    async def recall(self, query: str, n_results: int = 5) -> Dict:
        """Recall using DevMemory."""
        # Delegate to DevMemory's recall method
        return await self.devmemory.recall(
            query=query,
            n_results=n_results
        )

    async def remember_session(self, **kwargs):
        """Remember using DevMemory."""
        # Delegate to DevMemory's remember method
        return await self.devmemory.remember_session(**kwargs)

    async def get_service_history(self, service_name: str, limit: int = 10):
        """Get service history using DevMemory."""
        query = f"deployment {service_name}"
        results = await self.devmemory.recall(query=query, n_results=limit)
        return results.get("episodic", [])

    async def get_failure_patterns(self, service_name: Optional[str] = None):
        """Get failure patterns using DevMemory."""
        query = f"failure {service_name}" if service_name else "failure"
        results = await self.devmemory.recall(query=query, n_results=20)

        failures = [r for r in results.get("episodic", []) if "failure" in r.get("outcome", "")]
        rollbacks = [r for r in results.get("episodic", []) if r.get("session_type") == "rollback"]

        return {
            "total_failures": len(failures),
            "total_rollbacks": len(rollbacks),
            "recent_failures": failures[:5],
            "recent_rollbacks": rollbacks[:5],
            "failure_rate": len(failures) / 20 if failures else 0
        }
