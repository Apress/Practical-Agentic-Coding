"""
Redis-based message bus for agent communication.

Provides pub/sub messaging for agent-to-agent communication
with support for direct messages and broadcast channels.
"""

import json
import asyncio
import logging
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from redis import asyncio as aioredis

logger = logging.getLogger(__name__)


class Message:
    """Structured message for agent communication."""

    def __init__(
        self,
        from_agent: str,
        to_agent: Optional[str],
        message_type: str,
        payload: Dict[str, Any],
        timestamp: Optional[datetime] = None
    ):
        """
        Initialize message.

        Args:
            from_agent: Sender agent identifier
            to_agent: Receiver agent identifier (None for broadcast)
            message_type: Type of message (e.g., "task_assignment", "review_request")
            payload: Message payload data
            timestamp: Message timestamp (defaults to now)
        """
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.message_type = message_type
        self.payload = payload
        self.timestamp = timestamp or datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "message_type": self.message_type,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create message from dictionary."""
        return cls(
            from_agent=data["from_agent"],
            to_agent=data.get("to_agent"),
            message_type=data["message_type"],
            payload=data["payload"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )

    def __repr__(self) -> str:
        """String representation."""
        to = self.to_agent or "broadcast"
        return f"Message({self.from_agent} -> {to}: {self.message_type})"


class MessageBus:
    """
    Redis-based message bus for agent communication.

    Supports:
    - Direct agent-to-agent messaging
    - Broadcast messages
    - Channel subscriptions
    - Message history
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize message bus.

        Args:
            config: Configuration dictionary with Redis settings
        """
        self.config = config
        self.redis: Optional[aioredis.Redis] = None
        self.pubsub: Optional[aioredis.client.PubSub] = None
        self.subscriptions: Dict[str, List[Callable]] = {}
        self._listening = False
        self._listen_task: Optional[asyncio.Task] = None

    async def connect(self) -> None:
        """
        Connect to Redis server.

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
            logger.info("Connected to Redis message bus")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise ConnectionError(f"Redis connection failed: {e}")

    async def disconnect(self) -> None:
        """Disconnect from Redis and cleanup."""
        if self._listen_task:
            self._listening = False
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass

        if self.pubsub:
            await self.pubsub.unsubscribe()
            await self.pubsub.close()

        if self.redis:
            await self.redis.close()

        logger.info("Disconnected from Redis message bus")

    async def publish(
        self,
        from_agent: str,
        to_agent: Optional[str],
        message_type: str,
        payload: Dict[str, Any]
    ) -> None:
        """
        Publish message to appropriate channel.

        Args:
            from_agent: Sender agent identifier
            to_agent: Receiver agent identifier (None for broadcast)
            message_type: Type of message
            payload: Message payload data
        """
        if not self.redis:
            raise RuntimeError("Not connected to Redis")

        message = Message(from_agent, to_agent, message_type, payload)
        message_json = json.dumps(message.to_dict())

        # Determine channel
        if to_agent:
            channel = f"agent:{to_agent}"
        else:
            channel = "agent:broadcast"

        # Publish message
        await self.redis.publish(channel, message_json)

        # Store in message history
        await self._store_message(message)

        logger.debug(f"Published message: {message}")

    async def subscribe(
        self,
        agent_id: str,
        callback: Callable[[Message], None]
    ) -> None:
        """
        Subscribe agent to its message channel.

        Args:
            agent_id: Agent identifier
            callback: Callback function to handle messages
        """
        if not self.redis:
            raise RuntimeError("Not connected to Redis")

        # Create pubsub if needed
        if not self.pubsub:
            self.pubsub = self.redis.pubsub()

        # Subscribe to agent-specific and broadcast channels
        channels = [f"agent:{agent_id}", "agent:broadcast"]
        await self.pubsub.subscribe(*channels)

        # Store callback
        if agent_id not in self.subscriptions:
            self.subscriptions[agent_id] = []
        self.subscriptions[agent_id].append(callback)

        # Start listening if not already
        if not self._listening:
            self._listening = True
            self._listen_task = asyncio.create_task(self._listen_loop())

        logger.info(f"Agent {agent_id} subscribed to channels: {channels}")

    async def unsubscribe(self, agent_id: str) -> None:
        """
        Unsubscribe agent from channels.

        Args:
            agent_id: Agent identifier
        """
        if not self.pubsub:
            return

        channels = [f"agent:{agent_id}", "agent:broadcast"]
        await self.pubsub.unsubscribe(*channels)

        if agent_id in self.subscriptions:
            del self.subscriptions[agent_id]

        logger.info(f"Agent {agent_id} unsubscribed")

    async def _listen_loop(self) -> None:
        """Internal message listening loop."""
        if not self.pubsub:
            return

        try:
            while self._listening:
                message = await self.pubsub.get_message(
                    ignore_subscribe_messages=True,
                    timeout=1.0
                )
                if message and message["type"] == "message":
                    await self._handle_message(message)
        except asyncio.CancelledError:
            logger.debug("Listen loop cancelled")
        except Exception as e:
            logger.error(f"Error in listen loop: {e}")
            self._listening = False

    async def _handle_message(self, raw_message: Dict[str, Any]) -> None:
        """
        Handle incoming message.

        Args:
            raw_message: Raw Redis message
        """
        try:
            message_data = json.loads(raw_message["data"])
            message = Message.from_dict(message_data)

            # Route to appropriate callbacks
            if message.to_agent and message.to_agent in self.subscriptions:
                for callback in self.subscriptions[message.to_agent]:
                    await self._safe_callback(callback, message)
            elif not message.to_agent:
                # Broadcast - deliver to all
                for callbacks in self.subscriptions.values():
                    for callback in callbacks:
                        await self._safe_callback(callback, message)

        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def _safe_callback(
        self,
        callback: Callable[[Message], None],
        message: Message
    ) -> None:
        """
        Safely execute callback.

        Args:
            callback: Callback function
            message: Message to pass to callback
        """
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(message)
            else:
                callback(message)
        except Exception as e:
            logger.error(f"Error in message callback: {e}")

    async def _store_message(self, message: Message) -> None:
        """
        Store message in history.

        Args:
            message: Message to store
        """
        if not self.redis:
            return

        try:
            key = f"messages:{message.from_agent}"
            await self.redis.lpush(key, json.dumps(message.to_dict()))
            # Keep only last 1000 messages per agent
            await self.redis.ltrim(key, 0, 999)
        except Exception as e:
            logger.warning(f"Failed to store message: {e}")

    async def get_message_history(
        self,
        agent_id: str,
        limit: int = 100
    ) -> List[Message]:
        """
        Get message history for agent.

        Args:
            agent_id: Agent identifier
            limit: Maximum number of messages to retrieve

        Returns:
            List of messages in chronological order (newest first)
        """
        if not self.redis:
            return []

        try:
            key = f"messages:{agent_id}"
            messages_json = await self.redis.lrange(key, 0, limit - 1)
            return [
                Message.from_dict(json.loads(msg))
                for msg in messages_json
            ]
        except Exception as e:
            logger.error(f"Failed to retrieve message history: {e}")
            return []

    async def clear_history(self, agent_id: Optional[str] = None) -> None:
        """
        Clear message history.

        Args:
            agent_id: Agent identifier (None to clear all)
        """
        if not self.redis:
            return

        try:
            if agent_id:
                await self.redis.delete(f"messages:{agent_id}")
            else:
                # Clear all message histories
                keys = await self.redis.keys("messages:*")
                if keys:
                    await self.redis.delete(*keys)
            logger.info(f"Cleared message history for {agent_id or 'all agents'}")
        except Exception as e:
            logger.error(f"Failed to clear message history: {e}")
