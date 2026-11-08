"""
Base agent class for multi-agent swarm.

Provides common functionality for all agents including:
- Message sending/receiving
- Blackboard access
- Claude API integration
- State management
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from anthropic import AsyncAnthropic

from starter.message_bus import MessageBus, Message
from starter.blackboard import Blackboard, TaskState

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the swarm.

    Provides:
    - Message communication via MessageBus
    - Blackboard read/write access
    - Claude API integration
    - Agent lifecycle management
    """

    def __init__(
        self,
        agent_id: str,
        config: Dict[str, Any],
        message_bus: Optional[MessageBus] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """
        Initialize base agent.

        Args:
            agent_id: Unique agent identifier
            config: Configuration dictionary
            message_bus: Shared message bus (optional, can be set later)
            blackboard: Shared blackboard (optional, can be set later)
        """
        self.agent_id = agent_id
        self.config = config
        self.message_bus = message_bus
        self.blackboard = blackboard

        # Initialize Claude client
        api_key = config.get("anthropic_api_key")
        if not api_key:
            raise ValueError("anthropic_api_key required in config")

        self.client = AsyncAnthropic(api_key=api_key)

        # Agent configuration
        self.model = config.get(f"{agent_id}_agent_model", "claude-sonnet-4-6")
        self.max_tokens = config.get("agent_max_tokens", 4096)
        self.temperature = config.get("agent_temperature", 0.7)

        # Message queue for received messages
        self.message_queue: List[Message] = []

        logger.info(f"Initialized agent: {agent_id}")

    def set_message_bus(self, message_bus: MessageBus) -> None:
        """
        Set message bus for communication.

        Args:
            message_bus: MessageBus instance
        """
        self.message_bus = message_bus

    def set_blackboard(self, blackboard: Blackboard) -> None:
        """
        Set blackboard for shared state.

        Args:
            blackboard: Blackboard instance
        """
        self.blackboard = blackboard

    async def setup(self) -> None:
        """
        Setup agent (subscribe to messages, initialize state).

        Called after message_bus and blackboard are set.
        """
        if self.message_bus:
            await self.message_bus.subscribe(self.agent_id, self._handle_incoming_message)
            logger.info(f"Agent {self.agent_id} subscribed to message bus")

    async def cleanup(self) -> None:
        """Cleanup agent resources."""
        if self.message_bus:
            await self.message_bus.unsubscribe(self.agent_id)
        logger.info(f"Agent {self.agent_id} cleaned up")

    async def send_message(
        self,
        to_agent: Optional[str],
        message_type: str,
        payload: Dict[str, Any]
    ) -> None:
        """
        Send message to another agent or broadcast.

        Args:
            to_agent: Recipient agent ID (None for broadcast)
            message_type: Type of message
            payload: Message payload data
        """
        if not self.message_bus:
            raise RuntimeError("Message bus not set")

        await self.message_bus.publish(
            from_agent=self.agent_id,
            to_agent=to_agent,
            message_type=message_type,
            payload=payload
        )
        logger.debug(f"{self.agent_id} sent message: {message_type} to {to_agent or 'broadcast'}")

    async def _handle_incoming_message(self, message: Message) -> None:
        """
        Internal handler for incoming messages.

        Args:
            message: Received message
        """
        logger.debug(f"{self.agent_id} received message: {message}")
        self.message_queue.append(message)
        await self.process_message(message)

    @abstractmethod
    async def process_message(self, message: Message) -> None:
        """
        Process incoming message (implemented by subclasses).

        Args:
            message: Message to process
        """
        pass

    async def read_blackboard(self, task_id: str) -> Optional[TaskState]:
        """
        Read task from blackboard.

        Args:
            task_id: Task identifier

        Returns:
            TaskState or None
        """
        if not self.blackboard:
            raise RuntimeError("Blackboard not set")

        return await self.blackboard.get_task(task_id)

    async def write_blackboard(
        self,
        task_id: str,
        status: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update task on blackboard.

        Args:
            task_id: Task identifier
            status: New status (optional)
            data: Data to update (optional)

        Returns:
            True if successful
        """
        if not self.blackboard:
            raise RuntimeError("Blackboard not set")

        return await self.blackboard.update_task(
            task_id=task_id,
            agent_id=self.agent_id,
            status=status,
            data=data
        )

    async def claim_task(self, task_id: str) -> bool:
        """
        Claim task from blackboard.

        Args:
            task_id: Task identifier

        Returns:
            True if successfully claimed
        """
        if not self.blackboard:
            raise RuntimeError("Blackboard not set")

        return await self.blackboard.claim_task(task_id, self.agent_id)

    async def release_task(self, task_id: str, status: Optional[str] = None) -> bool:
        """
        Release a task this agent holds on the blackboard.

        Clears the claim so another agent can take the task, e.g. dev
        releasing after marking work "ready_for_review" so QA can claim it.

        Args:
            task_id: Task identifier
            status: New status to set with the release (optional)

        Returns:
            True if successfully released
        """
        if not self.blackboard:
            raise RuntimeError("Blackboard not set")

        return await self.blackboard.release_task(task_id, self.agent_id, status=status)

    async def query_claude(
        self,
        system_prompt: str,
        user_message: str,
        temperature: Optional[float] = None
    ) -> str:
        """
        Query Claude API.

        Args:
            system_prompt: System prompt defining agent role
            user_message: User message with task/question
            temperature: Temperature override (optional)

        Returns:
            Claude's response text
        """
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=temperature or self.temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )

            if response.content and len(response.content) > 0:
                return response.content[0].text

            return ""

        except Exception as e:
            logger.error(f"Claude API error for {self.agent_id}: {e}")
            raise

    async def get_pending_messages(self) -> List[Message]:
        """
        Get all pending messages.

        Returns:
            List of pending messages
        """
        messages = self.message_queue.copy()
        self.message_queue.clear()
        return messages

    def get_agent_id(self) -> str:
        """Get agent identifier."""
        return self.agent_id

    @abstractmethod
    def get_role_description(self) -> str:
        """
        Get agent role description (for system prompts).

        Returns:
            Role description string
        """
        pass

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(id={self.agent_id})"
