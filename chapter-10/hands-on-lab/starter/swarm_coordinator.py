"""
SwarmCoordinator: Multi-agent coordination system

Coordinates multiple agents using different patterns:
- Manager pattern: Central coordination
- Peer-to-peer: Direct agent communication
- Blackboard: Shared state coordination
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel

from starter.dev_agent import DevAgent
from starter.qa_agent import QAAgent
from starter.scrum_agent import ScrumAgent
from starter.message_bus import MessageBus
from starter.blackboard import Blackboard, TaskState

logger = logging.getLogger(__name__)


class CoordinationPattern(Enum):
    """Coordination patterns supported by the swarm."""
    MANAGER = "manager"           # Central coordinator
    PEER_TO_PEER = "peer"        # Direct agent communication
    BLACKBOARD = "blackboard"     # Shared state


class Task(BaseModel):
    """Task for swarm to complete."""
    id: str
    description: str
    assigned_to: Optional[str] = None
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class SwarmCoordinator:
    """
    Main swarm coordination system.

    Manages Dev, QA, and Scrum Master agents using
    different coordination patterns.
    """

    def __init__(self, config: Dict[str, Any], pattern: CoordinationPattern):
        """
        Initialize swarm coordinator.

        Args:
            config: Configuration dictionary
            pattern: Coordination pattern to use
        """
        self.config = config
        self.pattern = pattern
        self.agents: Dict[str, Any] = {}
        self.message_bus: Optional[MessageBus] = None
        self.blackboard: Optional[Blackboard] = None
        self.tasks: Dict[str, Task] = {}

        logger.info(f"Initializing SwarmCoordinator with pattern: {pattern.value}")

    async def setup(self) -> None:
        """
        Initialize swarm components.

        Sets up agents, message bus, and blackboard.
        """
        logger.info("Setting up swarm components")

        # Initialize message bus
        self.message_bus = MessageBus(self.config)
        await self.message_bus.connect()
        logger.info("Message bus connected")

        # Initialize blackboard
        self.blackboard = Blackboard(self.config)
        await self.blackboard.initialize()
        logger.info("Blackboard initialized")

        # Initialize agents
        self.agents["dev"] = DevAgent(self.config)
        self.agents["qa"] = QAAgent(self.config)
        self.agents["scrum"] = ScrumAgent(self.config)

        # Set message bus and blackboard for all agents
        for agent in self.agents.values():
            agent.set_message_bus(self.message_bus)
            agent.set_blackboard(self.blackboard)
            await agent.setup()

        logger.info(f"All agents initialized: {list(self.agents.keys())}")

    async def cleanup(self) -> None:
        """Cleanup swarm resources."""
        logger.info("Cleaning up swarm")

        # Cleanup agents
        for agent in self.agents.values():
            await agent.cleanup()

        # Cleanup infrastructure
        if self.message_bus:
            await self.message_bus.disconnect()

        if self.blackboard:
            await self.blackboard.close()

        logger.info("Swarm cleanup complete")

    async def coordinate_task_manager_pattern(self, task: Task) -> Dict[str, Any]:
        """
        Coordinate using manager pattern (central control).

        In this pattern, the Scrum Master agent acts as a central coordinator:
        1. Scrum Master receives the task
        2. Scrum Master assigns task to Dev agent
        3. Dev agent implements the feature
        4. Scrum Master monitors progress
        5. Scrum Master requests QA validation
        6. QA agent performs review/testing
        7. Scrum Master collects results and returns final output

        TODO (Exercise 1): Implement manager coordination

        Steps to implement:
        - Use self.agents["scrum"] to coordinate the workflow
        - Assign task to dev agent using: await self.agents["scrum"].assign_task(task, "dev")
        - Get implementation from dev: await self.agents["dev"].implement_feature(task)
        - Monitor progress: await self.agents["scrum"].monitor_progress(task.id)
        - Hand off to QA: await self.agents["scrum"].coordinate_handoff(task.id, "dev", "qa", context)
        - Get QA validation: await self.agents["qa"].test_feature(implementation)
        - Return final result with all agent contributions

        Hints:
        - The Scrum agent should be the only one making decisions
        - All communication goes through the Scrum agent
        - Track task status throughout the workflow
        - Include timing/metrics in the result

        Args:
            task: Task to coordinate

        Returns:
            Dictionary with coordination results including all agent outputs
        """
        logger.info(f"Coordinating task {task.id} using MANAGER pattern")

        # TODO: Students implement manager pattern coordination here
        # Remove this placeholder and implement the pattern
        raise NotImplementedError(
            "Exercise 1: Implement manager pattern coordination. "
            "See docstring above for detailed steps."
        )

    async def coordinate_task_peer_pattern(self, task: Task) -> Dict[str, Any]:
        """
        Coordinate using peer-to-peer pattern (direct communication).

        In this pattern, agents communicate directly without a central coordinator:
        1. Dev agent starts implementation
        2. Dev directly messages QA when ready for review
        3. QA reviews and sends feedback directly to Dev
        4. Dev and QA negotiate until reaching consensus
        5. Final result reflects collaborative agreement

        TODO (Exercise 2): Implement peer coordination

        Steps to implement:
        - Start dev implementation: await self.agents["dev"].implement_feature(task)
        - Dev sends review request to QA: await self.agents["dev"].collaborate_with_qa(task.id, implementation)
        - Wait for and process messages between agents
        - QA reviews: await self.agents["qa"].review_code(implementation)
        - If issues found, dev responds: await self.agents["dev"].respond_to_feedback(feedback)
        - Continue negotiation until approved or max iterations reached
        - Return result with negotiation history

        Hints:
        - Use message_bus to carry direct agent-to-agent messages
        - Agents should use send_message() to communicate
        - Implement a loop for negotiation (max 3 rounds recommended)
        - Track the conversation/negotiation history
        - No central coordinator - agents decide together

        Args:
            task: Task to coordinate

        Returns:
            Dictionary with coordination results including negotiation history
        """
        logger.info(f"Coordinating task {task.id} using PEER-TO-PEER pattern")

        # TODO: Students implement peer-to-peer pattern coordination here
        # Remove this placeholder and implement the pattern
        raise NotImplementedError(
            "Exercise 2: Implement peer-to-peer pattern coordination. "
            "See docstring above for detailed steps."
        )

    async def coordinate_task_blackboard_pattern(self, task: Task) -> Dict[str, Any]:
        """
        Coordinate using blackboard pattern (shared state).

        In this pattern, agents coordinate through a shared blackboard:
        1. Task is posted to the blackboard
        2. Agents watch the blackboard for relevant tasks
        3. Dev claims task when ready, updates status to "in_progress"
        4. Dev updates blackboard with implementation progress
        5. Dev marks as "ready_for_review" when complete, then releases its claim
        6. QA sees status change, claims for review (possible only after the release)
        7. QA updates with review results
        8. Task marked complete with full history

        TODO (Exercise 3): Implement blackboard coordination

        Steps to implement:
        - Create TaskState from task: TaskState(task.id, task.description)
        - Post to blackboard: await self.blackboard.post_task(task_state)
        - Poll for dev to claim: await self._wait_for_claim(task.id, "dev")
        - Dev implements and updates: await self.agents["dev"].implement_feature(task)
        - Dev updates blackboard: await self.blackboard.update_task(task.id, "dev", status="ready_for_review", data=result)
        - Dev releases its claim so QA can take the task: await self.blackboard.release_task(task.id, "dev")
        - Poll for QA to claim: await self._wait_for_status_change(task.id, "ready_for_review", "claimed")
        - QA reviews: await self.agents["qa"].review_code(implementation)
        - QA updates blackboard: await self.blackboard.update_task(task.id, "qa", status="complete", data=review)
        - Retrieve final state and return with full history

        Hints:
        - Use self.blackboard.post_task(), claim_task(), release_task(), update_task(), get_task()
        - Agents opportunistically claim tasks (simulate with asyncio.sleep polling)
        - All coordination happens through blackboard state changes
        - Implement helper methods like _wait_for_claim() and _wait_for_status_change()
        - Include full task history from blackboard in result
        - Handle timeouts appropriately

        Args:
            task: Task to coordinate

        Returns:
            Dictionary with coordination results including full task history
        """
        logger.info(f"Coordinating task {task.id} using BLACKBOARD pattern")

        # TODO: Students implement blackboard pattern coordination here
        # Remove this placeholder and implement the pattern
        raise NotImplementedError(
            "Exercise 3: Implement blackboard pattern coordination. "
            "See docstring above for detailed steps."
        )

    # Helper methods (students may find these useful)

    async def _wait_for_claim(
        self,
        task_id: str,
        expected_agent: str,
        timeout: int = 30
    ) -> bool:
        """
        Wait for a task to be claimed by specific agent.

        Args:
            task_id: Task identifier
            expected_agent: Agent expected to claim
            timeout: Timeout in seconds

        Returns:
            True if claimed by expected agent, False if timeout
        """
        # TODO: Students may implement this helper for Exercise 3
        # Poll blackboard until task is claimed or timeout
        pass

    async def _wait_for_status_change(
        self,
        task_id: str,
        from_status: str,
        to_status: str,
        timeout: int = 30
    ) -> bool:
        """
        Wait for task status to change.

        Args:
            task_id: Task identifier
            from_status: Expected current status
            to_status: Expected new status
            timeout: Timeout in seconds

        Returns:
            True if status changed, False if timeout
        """
        # TODO: Students may implement this helper for Exercise 3
        # Poll blackboard until status changes or timeout
        pass

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """
        Execute task using configured coordination pattern.

        This is a convenience method that routes to the appropriate
        coordination method based on self.pattern.

        Args:
            task: Task to execute

        Returns:
            Coordination result dictionary
        """
        logger.info(f"Executing task {task.id} with pattern {self.pattern.value}")

        # Store task
        self.tasks[task.id] = task

        # Route to appropriate coordination method
        if self.pattern == CoordinationPattern.MANAGER:
            result = await self.coordinate_task_manager_pattern(task)
        elif self.pattern == CoordinationPattern.PEER_TO_PEER:
            result = await self.coordinate_task_peer_pattern(task)
        elif self.pattern == CoordinationPattern.BLACKBOARD:
            result = await self.coordinate_task_blackboard_pattern(task)
        else:
            raise ValueError(f"Unknown coordination pattern: {self.pattern}")

        # Update task with result
        task.result = result
        task.status = "complete"

        logger.info(f"Task {task.id} execution complete")
        return result

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks."""
        return list(self.tasks.values())

    def get_pattern(self) -> CoordinationPattern:
        """Get current coordination pattern."""
        return self.pattern

    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get coordination metrics.

        Returns:
            Dictionary with metrics
        """
        metrics = {
            "pattern": self.pattern.value,
            "total_tasks": len(self.tasks),
            "agents": list(self.agents.keys()),
        }

        # Get blackboard statistics if available
        if self.blackboard:
            metrics["blackboard_stats"] = await self.blackboard.get_statistics()

        return metrics
