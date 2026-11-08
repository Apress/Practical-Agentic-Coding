"""
Blackboard architecture for shared state coordination.

Provides a shared data structure where agents can post tasks,
claim work, update state, and monitor progress opportunistically.
"""

import json
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from redis import asyncio as aioredis

logger = logging.getLogger(__name__)


class TaskState:
    """Represents a task's state on the blackboard."""

    def __init__(
        self,
        task_id: str,
        description: str,
        status: str = "pending",
        assigned_to: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialize task state.

        Args:
            task_id: Unique task identifier
            description: Task description
            status: Task status (pending, claimed, in_progress,
                ready_for_review, in_review, complete, failed)
            assigned_to: Agent ID that claimed the task
            data: Additional task data and results
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        self.task_id = task_id
        self.description = description
        self.status = status
        self.assigned_to = assigned_to
        self.data = data or {}
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.history: List[Dict[str, Any]] = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "status": self.status,
            "assigned_to": self.assigned_to,
            "data": self.data,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "history": self.history
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskState":
        """Create from dictionary."""
        task = cls(
            task_id=data["task_id"],
            description=data["description"],
            status=data.get("status", "pending"),
            assigned_to=data.get("assigned_to"),
            data=data.get("data", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
        task.history = data.get("history", [])
        return task

    def add_history_entry(
        self,
        action: str,
        agent_id: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add entry to task history.

        Args:
            action: Action performed
            agent_id: Agent performing action
            details: Additional details
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "agent_id": agent_id,
            "details": details or {}
        }
        self.history.append(entry)

    def __repr__(self) -> str:
        """String representation."""
        return f"TaskState({self.task_id}: {self.status}, assigned_to={self.assigned_to})"


class Blackboard:
    """
    Shared blackboard for agent coordination.

    Provides:
    - Task posting and claiming
    - State updates with history
    - Querying and filtering
    - Conflict detection and resolution
    - Watch/notification mechanisms
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize blackboard.

        Args:
            config: Configuration dictionary with Redis settings
        """
        self.config = config
        self.redis: Optional[aioredis.Redis] = None
        self.watchers: Dict[str, List[asyncio.Queue]] = {}

    async def initialize(self) -> None:
        """
        Initialize connection to Redis.

        Raises:
            ConnectionError: If connection fails
        """
        try:
            self.redis = aioredis.Redis(
                host=self.config.get("redis_host", "localhost"),
                port=self.config.get("redis_port", 6379),
                db=self.config.get("redis_db", 0),
                password=self.config.get("redis_password"),
                decode_responses=True
            )
            # Test connection
            await self.redis.ping()
            logger.info("Blackboard initialized and connected to Redis")
        except Exception as e:
            logger.error(f"Failed to initialize blackboard: {e}")
            raise ConnectionError(f"Redis connection failed: {e}")

    async def close(self) -> None:
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()
            logger.info("Blackboard connection closed")

    async def post_task(self, task: TaskState) -> bool:
        """
        Post new task to blackboard.

        Args:
            task: TaskState to post

        Returns:
            True if successful, False otherwise
        """
        if not self.redis:
            raise RuntimeError("Blackboard not initialized")

        try:
            task.add_history_entry("posted", "system", {"status": task.status})

            # Store task
            key = f"blackboard:task:{task.task_id}"
            await self.redis.set(key, json.dumps(task.to_dict()))

            # Add to status index
            await self.redis.sadd(f"blackboard:status:{task.status}", task.task_id)

            # Notify watchers
            await self._notify_watchers(task.status, task)

            logger.info(f"Posted task {task.task_id} to blackboard")
            return True

        except Exception as e:
            logger.error(f"Failed to post task: {e}")
            return False

    async def claim_task(self, task_id: str, agent_id: str) -> bool:
        """
        Claim a task (atomic operation).

        Uses Redis WATCH/MULTI optimistic locking on the task key: the task is
        read under WATCH, and the write transaction aborts if any other client
        touches the key in between. On that conflict the claim is re-checked
        against the new state, so two agents claiming concurrently cannot both
        succeed.

        Args:
            task_id: Task identifier
            agent_id: Agent claiming the task

        Returns:
            True if claimed successfully, False if already claimed
        """
        if not self.redis:
            raise RuntimeError("Blackboard not initialized")

        key = f"blackboard:task:{task_id}"

        try:
            async with self.redis.pipeline(transaction=True) as pipe:
                while True:
                    try:
                        # Read the task under WATCH; any concurrent write to
                        # the key aborts our transaction below.
                        await pipe.watch(key)
                        raw = await pipe.get(key)
                        if raw is None:
                            logger.warning(f"Task {task_id} not found")
                            return False

                        task = TaskState.from_dict(json.loads(raw))
                        if task.assigned_to and task.assigned_to != agent_id:
                            logger.warning(
                                f"Task {task_id} already claimed by {task.assigned_to}"
                            )
                            return False

                        old_status = task.status
                        task.assigned_to = agent_id
                        task.status = "claimed"
                        task.updated_at = datetime.now()
                        task.add_history_entry("claimed", agent_id)

                        # Queue the writes and execute atomically.
                        pipe.multi()
                        pipe.srem(f"blackboard:status:{old_status}", task_id)
                        pipe.sadd("blackboard:status:claimed", task_id)
                        pipe.set(key, json.dumps(task.to_dict()))
                        await pipe.execute()
                        break

                    except aioredis.WatchError:
                        # Another client changed the task between our read and
                        # write. Loop to re-read and re-check the claim.
                        continue

            logger.info(f"Agent {agent_id} claimed task {task_id}")
            await self._notify_watchers("claimed", task)
            return True

        except Exception as e:
            logger.error(f"Failed to claim task: {e}")
            return False

    async def release_task(
        self,
        task_id: str,
        agent_id: str,
        status: Optional[str] = None
    ) -> bool:
        """
        Release a claimed task (atomic operation).

        The counterpart to claim_task: the holding agent clears assigned_to
        so another agent can claim the task. By default the status is left
        alone, which is what a handoff needs (dev marks "ready_for_review",
        releases, QA claims). Pass status to transition in the same atomic
        step, e.g. status="pending" when returning a stuck task to the pool.

        Uses the same WATCH/MULTI optimistic locking as claim_task. Only the
        agent holding the claim may release. Releasing a task that is missing
        or not claimed is a clean no-op that returns False, matching how
        claim_task signals failure.

        Args:
            task_id: Task identifier
            agent_id: Agent releasing the task (must hold the claim)
            status: New status to set with the release (optional)

        Returns:
            True if released successfully, False otherwise
        """
        if not self.redis:
            raise RuntimeError("Blackboard not initialized")

        key = f"blackboard:task:{task_id}"

        try:
            async with self.redis.pipeline(transaction=True) as pipe:
                while True:
                    try:
                        # Read the task under WATCH; any concurrent write to
                        # the key aborts our transaction below.
                        await pipe.watch(key)
                        raw = await pipe.get(key)
                        if raw is None:
                            logger.warning(f"Task {task_id} not found")
                            return False

                        task = TaskState.from_dict(json.loads(raw))
                        if not task.assigned_to:
                            logger.warning(
                                f"Task {task_id} is not claimed; nothing to release"
                            )
                            return False
                        if task.assigned_to != agent_id:
                            logger.warning(
                                f"Agent {agent_id} cannot release task held by {task.assigned_to}"
                            )
                            return False

                        old_status = task.status
                        task.assigned_to = None
                        if status:
                            task.status = status
                        task.updated_at = datetime.now()
                        task.add_history_entry(
                            "released",
                            agent_id,
                            {"old_status": old_status, "new_status": task.status}
                        )

                        # Queue the writes and execute atomically.
                        pipe.multi()
                        if task.status != old_status:
                            pipe.srem(f"blackboard:status:{old_status}", task_id)
                            pipe.sadd(f"blackboard:status:{task.status}", task_id)
                        pipe.set(key, json.dumps(task.to_dict()))
                        await pipe.execute()
                        break

                    except aioredis.WatchError:
                        # Another client changed the task between our read and
                        # write. Loop to re-read and re-check the release.
                        continue

            logger.info(f"Agent {agent_id} released task {task_id}")
            await self._notify_watchers(task.status, task)
            return True

        except Exception as e:
            logger.error(f"Failed to release task: {e}")
            return False

    async def update_task(
        self,
        task_id: str,
        agent_id: str,
        status: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update task state.

        Args:
            task_id: Task identifier
            agent_id: Agent performing update
            status: New status (optional)
            data: Data to merge into task.data (optional)

        Returns:
            True if successful, False otherwise
        """
        if not self.redis:
            raise RuntimeError("Blackboard not initialized")

        try:
            task = await self.get_task(task_id)
            if not task:
                logger.warning(f"Task {task_id} not found")
                return False

            # Verify agent has permission to update
            if task.assigned_to and task.assigned_to != agent_id:
                logger.warning(
                    f"Agent {agent_id} cannot update task assigned to {task.assigned_to}"
                )
                return False

            old_status = task.status

            # Update status if provided
            if status and status != task.status:
                # Remove from old status index
                await self.redis.srem(f"blackboard:status:{old_status}", task_id)
                # Add to new status index
                await self.redis.sadd(f"blackboard:status:{status}", task_id)
                task.status = status

            # Merge data if provided
            if data:
                task.data.update(data)

            task.updated_at = datetime.now()
            task.add_history_entry(
                "updated",
                agent_id,
                {"old_status": old_status, "new_status": status, "data_keys": list(data.keys()) if data else []}
            )

            # Save updated task
            key = f"blackboard:task:{task_id}"
            await self.redis.set(key, json.dumps(task.to_dict()))

            logger.info(f"Agent {agent_id} updated task {task_id} to status {status}")
            await self._notify_watchers(task.status, task)
            return True

        except Exception as e:
            logger.error(f"Failed to update task: {e}")
            return False

    async def get_task(self, task_id: str) -> Optional[TaskState]:
        """
        Get task by ID.

        Args:
            task_id: Task identifier

        Returns:
            TaskState or None if not found
        """
        if not self.redis:
            raise RuntimeError("Blackboard not initialized")

        try:
            key = f"blackboard:task:{task_id}"
            data = await self.redis.get(key)
            if data:
                return TaskState.from_dict(json.loads(data))
            return None
        except Exception as e:
            logger.error(f"Failed to get task: {e}")
            return None

    async def get_tasks(
        self,
        status: Optional[str] = None,
        assigned_to: Optional[str] = None,
        limit: int = 100
    ) -> List[TaskState]:
        """
        Query tasks with filters.

        Args:
            status: Filter by status (optional)
            assigned_to: Filter by assigned agent (optional)
            limit: Maximum number of tasks to return

        Returns:
            List of matching tasks
        """
        if not self.redis:
            raise RuntimeError("Blackboard not initialized")

        try:
            tasks = []

            if status:
                # Get task IDs from status index
                task_ids = await self.redis.smembers(f"blackboard:status:{status}")
            else:
                # Get all task IDs
                keys = await self.redis.keys("blackboard:task:*")
                task_ids = [key.split(":")[-1] for key in keys]

            # Fetch and filter tasks
            for task_id in list(task_ids)[:limit]:
                task = await self.get_task(task_id)
                if task:
                    if assigned_to and task.assigned_to != assigned_to:
                        continue
                    tasks.append(task)

            return tasks

        except Exception as e:
            logger.error(f"Failed to query tasks: {e}")
            return []

    async def watch_status(
        self,
        status: str,
        callback: Optional[Any] = None
    ) -> asyncio.Queue:
        """
        Watch for tasks with specific status.

        Args:
            status: Status to watch
            callback: Optional callback for notifications

        Returns:
            Queue that receives task updates
        """
        if status not in self.watchers:
            self.watchers[status] = []

        queue = asyncio.Queue()
        self.watchers[status].append(queue)

        logger.info(f"Added watcher for status: {status}")
        return queue

    async def _notify_watchers(self, status: str, task: TaskState) -> None:
        """
        Notify watchers of task updates.

        Args:
            status: Task status
            task: Updated task
        """
        if status in self.watchers:
            for queue in self.watchers[status]:
                try:
                    queue.put_nowait(task)
                except asyncio.QueueFull:
                    logger.warning(f"Watcher queue full for status {status}")

    async def clear(self) -> None:
        """Clear all tasks from blackboard."""
        if not self.redis:
            raise RuntimeError("Blackboard not initialized")

        try:
            # Clear all task keys
            keys = await self.redis.keys("blackboard:*")
            if keys:
                await self.redis.delete(*keys)
            logger.info("Cleared all tasks from blackboard")
        except Exception as e:
            logger.error(f"Failed to clear blackboard: {e}")

    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get blackboard statistics.

        Returns:
            Dictionary with statistics
        """
        if not self.redis:
            raise RuntimeError("Blackboard not initialized")

        try:
            stats = {
                "total_tasks": 0,
                "by_status": {},
                "by_agent": {}
            }

            # Count tasks by status (the full lifecycle used by the exercises)
            for status in [
                "pending",
                "claimed",
                "in_progress",
                "ready_for_review",
                "in_review",
                "complete",
                "failed",
            ]:
                count = await self.redis.scard(f"blackboard:status:{status}")
                stats["by_status"][status] = count
                stats["total_tasks"] += count

            # Get all tasks to count by agent
            all_tasks = await self.get_tasks()
            for task in all_tasks:
                if task.assigned_to:
                    stats["by_agent"][task.assigned_to] = stats["by_agent"].get(task.assigned_to, 0) + 1

            return stats

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
