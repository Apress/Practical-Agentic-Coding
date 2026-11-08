"""
Unit tests for SwarmCoordinator.

Tests the three coordination patterns:
- Manager pattern
- Peer-to-peer pattern
- Blackboard pattern
"""

import pytest
import asyncio
from unittest.mock import Mock, MagicMock, AsyncMock, patch

from starter.swarm_coordinator import SwarmCoordinator, CoordinationPattern, Task
from starter.blackboard import Blackboard, TaskState
from starter.config import SwarmConfig


def _mock_redis():
    """
    Build a mock replacement for redis.asyncio.Redis.

    The real class is constructed synchronously, its data methods are awaited
    (await redis.ping()), and pubsub() is a synchronous call returning an
    object whose methods are awaited. A bare MagicMock fails on the awaits and
    a bare AsyncMock fails on pubsub(), so this builds the hybrid the tests
    need to run fully offline.
    """
    pubsub = AsyncMock()

    async def _no_message(*args, **kwargs):
        # Yield control like a real timeout-based poll, so the message bus
        # listen loop cannot starve the event loop during a test.
        await asyncio.sleep(0.01)
        return None

    pubsub.get_message = AsyncMock(side_effect=_no_message)

    instance = AsyncMock()
    instance.pubsub = MagicMock(return_value=pubsub)
    return MagicMock(return_value=instance)


class _FakePipeline:
    """
    Minimal stand-in for the WATCH/MULTI pipeline claim_task and
    release_task use. Reads before multi() are awaited and hit the store
    directly; writes after multi() are buffered synchronously (matching
    redis-py's buffering behavior) and applied on execute().
    """

    def __init__(self, store):
        self._store = store
        self._queued = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def watch(self, *keys):
        pass

    async def get(self, key):
        return self._store.strings.get(key)

    def multi(self):
        self._queued = []

    def set(self, key, value):
        self._queued.append(("set", key, value))

    def sadd(self, key, *members):
        self._queued.append(("sadd", key, members))

    def srem(self, key, *members):
        self._queued.append(("srem", key, members))

    async def execute(self):
        for op, key, value in self._queued:
            if op == "set":
                self._store.strings[key] = value
            elif op == "sadd":
                self._store.sets.setdefault(key, set()).update(value)
            elif op == "srem":
                self._store.sets.get(key, set()).difference_update(value)
        self._queued = None
        return []


class _FakeRedis:
    """
    In-memory replacement for redis.asyncio.Redis, stateful where
    _mock_redis() is not. The blackboard claim/release tests need reads to
    see earlier writes (post, then claim, then release), so a plain
    AsyncMock is not enough. Patched in the same place as _mock_redis():
    starter.blackboard.aioredis.Redis.
    """

    def __init__(self, *args, **kwargs):
        self.strings = {}
        self.sets = {}

    async def ping(self):
        return True

    async def close(self):
        pass

    async def get(self, key):
        return self.strings.get(key)

    async def set(self, key, value):
        self.strings[key] = value
        return True

    async def sadd(self, key, *members):
        self.sets.setdefault(key, set()).update(members)
        return len(members)

    async def srem(self, key, *members):
        self.sets.get(key, set()).difference_update(members)
        return len(members)

    async def smembers(self, key):
        return set(self.sets.get(key, set()))

    async def scard(self, key):
        return len(self.sets.get(key, set()))

    async def keys(self, pattern):
        import fnmatch
        return [k for k in self.strings if fnmatch.fnmatch(k, pattern)]

    async def delete(self, *keys):
        count = 0
        for key in keys:
            count += self.strings.pop(key, None) is not None
            count += self.sets.pop(key, None) is not None
        return count

    def pipeline(self, transaction=True):
        return _FakePipeline(self)


async def _fake_blackboard(config):
    """Build a Blackboard backed by the in-memory fake, fully offline."""
    with patch('starter.blackboard.aioredis.Redis', _FakeRedis):
        blackboard = Blackboard(config)
        await blackboard.initialize()
    return blackboard


@pytest.fixture
def test_config():
    """Test configuration."""
    return {
        "anthropic_api_key": "test_key",
        "redis_host": "localhost",
        "redis_port": 6379,
        "redis_db": 0,
        "agent_timeout_seconds": 30,
        "dev_agent_model": "claude-sonnet-4-6",
        "qa_agent_model": "claude-sonnet-4-6",
        "scrum_agent_model": "claude-sonnet-4-6",
    }


@pytest.fixture
def sample_task():
    """Sample task for testing."""
    return Task(
        id="task_001",
        description="Implement user authentication feature with JWT tokens",
        status="pending"
    )


class TestManagerPattern:
    """Tests for manager pattern coordination."""

    @pytest.mark.asyncio
    async def test_manager_pattern_initialization(self, test_config):
        """Test that manager pattern coordinator initializes correctly."""
        coordinator = SwarmCoordinator(test_config, CoordinationPattern.MANAGER)

        assert coordinator.pattern == CoordinationPattern.MANAGER
        assert coordinator.config == test_config
        assert len(coordinator.agents) == 0  # Not yet set up

    @pytest.mark.asyncio
    async def test_manager_pattern_setup(self, test_config):
        """Test that setup initializes all components."""
        coordinator = SwarmCoordinator(test_config, CoordinationPattern.MANAGER)

        # Mock Redis connections to avoid actual connections in tests
        with patch('starter.message_bus.aioredis.Redis', _mock_redis()), \
             patch('starter.blackboard.aioredis.Redis', _mock_redis()):
            await coordinator.setup()

            # Verify components are initialized
            assert coordinator.message_bus is not None
            assert coordinator.blackboard is not None
            assert "dev" in coordinator.agents
            assert "qa" in coordinator.agents
            assert "scrum" in coordinator.agents

            await coordinator.cleanup()

    @pytest.mark.asyncio
    async def test_manager_pattern_coordination(self, test_config, sample_task):
        """
        Test manager pattern coordination flow.

        This test verifies that your implementation:
        1. Uses Scrum agent as central coordinator
        2. Assigns task to dev agent
        3. Gets implementation from dev
        4. Hands off to QA
        5. Gets validation from QA
        6. Returns complete result

        Note: This test will fail until you implement
        coordinate_task_manager_pattern() in swarm_coordinator.py
        """
        coordinator = SwarmCoordinator(test_config, CoordinationPattern.MANAGER)

        with patch('starter.message_bus.aioredis.Redis', _mock_redis()), \
             patch('starter.blackboard.aioredis.Redis', _mock_redis()):
            await coordinator.setup()

            # Mock agent methods to avoid actual Claude API calls
            coordinator.agents["scrum"].assign_task = AsyncMock(return_value={
                "task_id": sample_task.id,
                "assigned_to": "dev",
                "status": "assigned"
            })

            coordinator.agents["dev"].implement_feature = AsyncMock(return_value={
                "task_id": sample_task.id,
                "status": "implemented",
                "implementation": "User authentication with JWT tokens implemented",
                "complexity": "medium"
            })

            coordinator.agents["scrum"].monitor_progress = AsyncMock(return_value={
                "task_id": sample_task.id,
                "status": "in_progress",
                "assigned_to": "dev"
            })

            coordinator.agents["scrum"].coordinate_handoff = AsyncMock(return_value={
                "task_id": sample_task.id,
                "from_agent": "dev",
                "to_agent": "qa",
                "status": "handed_off"
            })

            coordinator.agents["qa"].test_feature = AsyncMock(return_value={
                "task_id": sample_task.id,
                "status": "tested",
                "test_plan": "Full test plan created",
                "coverage": "high"
            })

            # Execute manager pattern coordination
            # This will raise NotImplementedError until you implement it
            try:
                result = await coordinator.coordinate_task_manager_pattern(sample_task)

                # Verify result structure
                assert result is not None
                assert "task_id" in result
                assert result["task_id"] == sample_task.id

                # Verify Scrum agent was used for coordination
                coordinator.agents["scrum"].assign_task.assert_called_once()
                coordinator.agents["dev"].implement_feature.assert_called_once()
                coordinator.agents["qa"].test_feature.assert_called_once()

                # Verify the workflow happened in order
                assert coordinator.agents["scrum"].monitor_progress.called

            except NotImplementedError:
                pytest.skip("Manager pattern not yet implemented - this is expected")

            await coordinator.cleanup()


class TestPeerPattern:
    """Tests for peer-to-peer pattern coordination."""

    @pytest.mark.asyncio
    async def test_peer_pattern_initialization(self, test_config):
        """Test that peer pattern coordinator initializes correctly."""
        coordinator = SwarmCoordinator(test_config, CoordinationPattern.PEER_TO_PEER)

        assert coordinator.pattern == CoordinationPattern.PEER_TO_PEER
        assert coordinator.config == test_config

    @pytest.mark.asyncio
    async def test_peer_pattern_coordination(self, test_config, sample_task):
        """
        Test peer-to-peer pattern coordination flow.

        This test verifies that your implementation:
        1. Dev starts implementation
        2. Dev directly contacts QA
        3. QA reviews and provides feedback
        4. Negotiation happens between dev and QA
        5. Final consensus is reached

        Note: This test will fail until you implement
        coordinate_task_peer_pattern() in swarm_coordinator.py
        """
        coordinator = SwarmCoordinator(test_config, CoordinationPattern.PEER_TO_PEER)

        with patch('starter.message_bus.aioredis.Redis', _mock_redis()), \
             patch('starter.blackboard.aioredis.Redis', _mock_redis()):
            await coordinator.setup()

            # Mock agent methods
            coordinator.agents["dev"].implement_feature = AsyncMock(return_value={
                "task_id": sample_task.id,
                "status": "implemented",
                "implementation": "Feature implemented"
            })

            coordinator.agents["dev"].collaborate_with_qa = AsyncMock(return_value={
                "status": "collaboration_initiated",
                "task_id": sample_task.id
            })

            coordinator.agents["qa"].review_code = AsyncMock(return_value={
                "task_id": sample_task.id,
                "status": "reviewed",
                "quality_score": 8.5,
                "approved": True,
                "issues": []
            })

            coordinator.agents["dev"].respond_to_feedback = AsyncMock(
                return_value="Feedback addressed"
            )

            # Execute peer pattern coordination
            try:
                result = await coordinator.coordinate_task_peer_pattern(sample_task)

                # Verify result structure
                assert result is not None
                assert "task_id" in result
                assert result["task_id"] == sample_task.id

                # Verify direct communication between dev and QA
                coordinator.agents["dev"].implement_feature.assert_called_once()
                coordinator.agents["qa"].review_code.assert_called()

                # Verify no central coordinator was used
                # (Scrum agent methods should not be called)

            except NotImplementedError:
                pytest.skip("Peer pattern not yet implemented - this is expected")

            await coordinator.cleanup()

    @pytest.mark.asyncio
    async def test_peer_pattern_negotiation(self, test_config, sample_task):
        """
        Test that peer pattern handles negotiation when QA finds issues.

        This test verifies negotiation loop works correctly.
        """
        coordinator = SwarmCoordinator(test_config, CoordinationPattern.PEER_TO_PEER)

        with patch('starter.message_bus.aioredis.Redis', _mock_redis()), \
             patch('starter.blackboard.aioredis.Redis', _mock_redis()):
            await coordinator.setup()

            # Mock QA to initially reject, then approve
            review_results = [
                {
                    "task_id": sample_task.id,
                    "approved": False,
                    "issues": ["Security issue", "Performance concern"]
                },
                {
                    "task_id": sample_task.id,
                    "approved": True,
                    "issues": []
                }
            ]

            coordinator.agents["dev"].implement_feature = AsyncMock(return_value={
                "task_id": sample_task.id,
                "implementation": "Feature"
            })

            coordinator.agents["qa"].review_code = AsyncMock(side_effect=review_results)
            coordinator.agents["dev"].respond_to_feedback = AsyncMock(
                return_value="Issues addressed"
            )

            try:
                result = await coordinator.coordinate_task_peer_pattern(sample_task)

                # Verify negotiation happened
                assert coordinator.agents["qa"].review_code.call_count >= 2
                coordinator.agents["dev"].respond_to_feedback.assert_called()

            except NotImplementedError:
                pytest.skip("Peer pattern not yet implemented - this is expected")

            await coordinator.cleanup()


class TestBlackboardPattern:
    """Tests for blackboard pattern coordination."""

    @pytest.mark.asyncio
    async def test_blackboard_pattern_initialization(self, test_config):
        """Test that blackboard pattern coordinator initializes correctly."""
        coordinator = SwarmCoordinator(test_config, CoordinationPattern.BLACKBOARD)

        assert coordinator.pattern == CoordinationPattern.BLACKBOARD
        assert coordinator.config == test_config

    @pytest.mark.asyncio
    async def test_blackboard_pattern_coordination(self, test_config, sample_task):
        """
        Test blackboard pattern coordination flow.

        This test verifies that your implementation:
        1. Posts task to blackboard
        2. Dev claims and implements
        3. Dev updates blackboard with "ready_for_review"
        4. QA claims and reviews
        5. QA updates blackboard with "complete"
        6. Full history is maintained

        Note: This test will fail until you implement
        coordinate_task_blackboard_pattern() in swarm_coordinator.py
        """
        coordinator = SwarmCoordinator(test_config, CoordinationPattern.BLACKBOARD)

        with patch('starter.message_bus.aioredis.Redis', _mock_redis()), \
             patch('starter.blackboard.aioredis.Redis', _mock_redis()):
            await coordinator.setup()

            # Mock blackboard methods
            coordinator.blackboard.post_task = AsyncMock(return_value=True)
            coordinator.blackboard.claim_task = AsyncMock(return_value=True)
            coordinator.blackboard.release_task = AsyncMock(return_value=True)
            coordinator.blackboard.update_task = AsyncMock(return_value=True)

            from starter.blackboard import TaskState
            mock_task_state = TaskState(
                task_id=sample_task.id,
                description=sample_task.description,
                status="complete",
                assigned_to="qa"
            )
            mock_task_state.history = [
                {"action": "posted", "agent_id": "system"},
                {"action": "claimed", "agent_id": "dev"},
                {"action": "updated", "agent_id": "dev"},
                {"action": "claimed", "agent_id": "qa"},
                {"action": "updated", "agent_id": "qa"}
            ]

            coordinator.blackboard.get_task = AsyncMock(return_value=mock_task_state)

            # Mock agent methods
            coordinator.agents["dev"].implement_feature = AsyncMock(return_value={
                "task_id": sample_task.id,
                "implementation": "Feature implemented"
            })

            coordinator.agents["qa"].review_code = AsyncMock(return_value={
                "task_id": sample_task.id,
                "approved": True
            })

            # Execute blackboard pattern coordination
            try:
                result = await coordinator.coordinate_task_blackboard_pattern(sample_task)

                # Verify result structure
                assert result is not None
                assert "task_id" in result

                # Verify blackboard operations
                coordinator.blackboard.post_task.assert_called_once()

                # Verify task history is included
                if "history" in result:
                    assert len(result["history"]) > 0

            except NotImplementedError:
                pytest.skip("Blackboard pattern not yet implemented - this is expected")

            await coordinator.cleanup()

    @pytest.mark.asyncio
    async def test_blackboard_pattern_state_transitions(self, test_config, sample_task):
        """
        Test that blackboard pattern correctly handles state transitions.

        Verifies: pending -> claimed -> in_progress -> ready_for_review -> complete
        """
        coordinator = SwarmCoordinator(test_config, CoordinationPattern.BLACKBOARD)

        with patch('starter.message_bus.aioredis.Redis', _mock_redis()), \
             patch('starter.blackboard.aioredis.Redis', _mock_redis()):
            await coordinator.setup()

            # Track state transitions
            states = []

            async def track_update(task_id, agent_id, status=None, data=None):
                if status:
                    states.append(status)
                return True

            coordinator.blackboard.update_task = AsyncMock(side_effect=track_update)
            coordinator.blackboard.post_task = AsyncMock(return_value=True)
            coordinator.blackboard.claim_task = AsyncMock(return_value=True)
            coordinator.blackboard.release_task = AsyncMock(return_value=True)

            from starter.blackboard import TaskState
            coordinator.blackboard.get_task = AsyncMock(return_value=TaskState(
                task_id=sample_task.id,
                description=sample_task.description,
                status="complete"
            ))

            coordinator.agents["dev"].implement_feature = AsyncMock(return_value={
                "implementation": "Done"
            })
            coordinator.agents["qa"].review_code = AsyncMock(return_value={
                "approved": True
            })

            try:
                result = await coordinator.coordinate_task_blackboard_pattern(sample_task)

                # Verify state transitions occurred
                # Should include transitions like: ready_for_review, complete, etc.
                assert coordinator.blackboard.update_task.called

            except NotImplementedError:
                pytest.skip("Blackboard pattern not yet implemented - this is expected")

            await coordinator.cleanup()


class TestBlackboardClaimRelease:
    """
    Tests for release_task and the dev-to-QA claim handoff.

    These exercise the real Blackboard logic against the in-memory fake
    Redis, so claim ownership rules behave as they do on a live server.
    """

    @pytest.mark.asyncio
    async def test_release_task_by_holder(self, test_config):
        """The holding agent can release; status can transition atomically."""
        blackboard = await _fake_blackboard(test_config)
        await blackboard.post_task(TaskState("task_001", "Implement auth"))
        assert await blackboard.claim_task("task_001", "dev") is True

        released = await blackboard.release_task("task_001", "dev", status="pending")

        assert released is True
        state = await blackboard.get_task("task_001")
        assert state.assigned_to is None
        assert state.status == "pending"
        assert state.history[-1]["action"] == "released"

        # The status index moved along with the release
        pending = await blackboard.get_tasks(status="pending")
        assert [t.task_id for t in pending] == ["task_001"]

    @pytest.mark.asyncio
    async def test_release_task_by_non_holder_rejected(self, test_config):
        """An agent that does not hold the claim cannot release it."""
        blackboard = await _fake_blackboard(test_config)
        await blackboard.post_task(TaskState("task_001", "Implement auth"))
        assert await blackboard.claim_task("task_001", "dev") is True

        assert await blackboard.release_task("task_001", "qa") is False

        state = await blackboard.get_task("task_001")
        assert state.assigned_to == "dev"
        assert state.status == "claimed"

    @pytest.mark.asyncio
    async def test_release_unclaimed_task_is_noop(self, test_config):
        """Releasing an unclaimed or missing task returns False, changes nothing."""
        blackboard = await _fake_blackboard(test_config)
        await blackboard.post_task(TaskState("task_001", "Implement auth"))

        assert await blackboard.release_task("task_001", "dev") is False

        state = await blackboard.get_task("task_001")
        assert state.assigned_to is None
        assert state.status == "pending"
        assert all(entry["action"] != "released" for entry in state.history)

        # Missing task is the same clean False
        assert await blackboard.release_task("no_such_task", "dev") is False

    @pytest.mark.asyncio
    async def test_dev_release_then_qa_claim_handoff(self, test_config):
        """
        The Exercise 3 handoff sequence: dev works the task, marks it
        ready_for_review, releases the claim, then QA claims and completes.
        """
        blackboard = await _fake_blackboard(test_config)
        await blackboard.post_task(TaskState("task_001", "Implement auth"))

        # Dev claims and works the task
        assert await blackboard.claim_task("task_001", "dev") is True
        assert await blackboard.update_task(
            "task_001", "dev", status="in_progress"
        ) is True
        assert await blackboard.update_task(
            "task_001", "dev",
            status="ready_for_review",
            data={"implementation": "auth module"}
        ) is True

        # QA cannot claim while dev still holds the task
        assert await blackboard.claim_task("task_001", "qa") is False

        # Dev releases; by default the status set above survives
        assert await blackboard.release_task("task_001", "dev") is True
        state = await blackboard.get_task("task_001")
        assert state.assigned_to is None
        assert state.status == "ready_for_review"

        # QA claims and completes the review
        assert await blackboard.claim_task("task_001", "qa") is True
        assert await blackboard.update_task(
            "task_001", "qa", status="in_review"
        ) is True
        assert await blackboard.update_task(
            "task_001", "qa",
            status="complete",
            data={"qa_validation": {"approved": True}}
        ) is True

        final = await blackboard.get_task("task_001")
        assert final.status == "complete"
        assert final.assigned_to == "qa"
        assert final.data["implementation"] == "auth module"
        actions = [entry["action"] for entry in final.history]
        assert actions.count("claimed") == 2  # dev's claim and QA's claim
        assert "released" in actions


class TestCoordinatorHelpers:
    """Tests for helper methods."""

    @pytest.mark.asyncio
    async def test_execute_task_routes_to_manager(self, test_config, sample_task):
        """Test that execute_task routes to correct pattern method."""
        coordinator = SwarmCoordinator(test_config, CoordinationPattern.MANAGER)

        with patch('starter.message_bus.aioredis.Redis', _mock_redis()), \
             patch('starter.blackboard.aioredis.Redis', _mock_redis()):
            await coordinator.setup()

            # Mock the pattern method
            coordinator.coordinate_task_manager_pattern = AsyncMock(return_value={
                "task_id": sample_task.id,
                "status": "complete"
            })

            try:
                result = await coordinator.execute_task(sample_task)
                coordinator.coordinate_task_manager_pattern.assert_called_once_with(sample_task)
            except NotImplementedError:
                pytest.skip("Pattern methods not yet implemented")

            await coordinator.cleanup()

    @pytest.mark.asyncio
    async def test_get_metrics(self, test_config):
        """Test metrics collection."""
        coordinator = SwarmCoordinator(test_config, CoordinationPattern.MANAGER)

        with patch('starter.message_bus.aioredis.Redis', _mock_redis()), \
             patch('starter.blackboard.aioredis.Redis', _mock_redis()):
            await coordinator.setup()

            metrics = await coordinator.get_metrics()

            assert "pattern" in metrics
            assert metrics["pattern"] == "manager"
            assert "agents" in metrics
            assert set(metrics["agents"]) == {"dev", "qa", "scrum"}

            await coordinator.cleanup()


# Run from hands-on-lab/: pytest starter/tests/test_swarm_coordinator.py -v
