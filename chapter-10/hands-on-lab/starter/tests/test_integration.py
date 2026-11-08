"""
Integration tests for multi-agent swarm system.

These tests verify end-to-end coordination patterns with real
Redis connections (but mocked Claude API calls).
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from starter.swarm_coordinator import SwarmCoordinator, CoordinationPattern, Task
from starter.blackboard import Blackboard, TaskState


@pytest.fixture
def test_config():
    """Test configuration with real Redis."""
    return {
        "anthropic_api_key": "test_key",
        "redis_host": "localhost",
        "redis_port": 6379,
        "redis_db": 1,  # Use different DB for tests
        "agent_timeout_seconds": 30,
        "dev_agent_model": "claude-sonnet-4-6",
        "qa_agent_model": "claude-sonnet-4-6",
        "scrum_agent_model": "claude-sonnet-4-6",
    }


@pytest.fixture
def sample_tasks():
    """Multiple sample tasks for testing."""
    return [
        Task(
            id="task_001",
            description="Implement user authentication with JWT tokens",
            status="pending"
        ),
        Task(
            id="task_002",
            description="Add database connection pooling",
            status="pending"
        ),
        Task(
            id="task_003",
            description="Implement rate limiting middleware",
            status="pending"
        )
    ]


@pytest.mark.integration
class TestManagerPatternIntegration:
    """Integration tests for manager pattern."""

    @pytest.mark.asyncio
    async def test_full_manager_workflow(self, test_config, sample_tasks):
        """
        Test complete manager pattern workflow with real Redis.

        This test requires:
        - Redis running on localhost:6379
        - Your manager pattern implementation complete
        """
        coordinator = SwarmCoordinator(test_config, CoordinationPattern.MANAGER)

        try:
            await coordinator.setup()
            # Start from an empty message history, so the check below sees
            # only this run's messages, not leftovers from earlier tests.
            await coordinator.message_bus.clear_history()

            # Mock Claude API calls to avoid actual API usage
            with patch.object(coordinator.agents["dev"], 'query_claude', new=AsyncMock(return_value="Implementation complete")), \
                 patch.object(coordinator.agents["qa"], 'query_claude', new=AsyncMock(return_value="Quality score: 9/10. Approved.")), \
                 patch.object(coordinator.agents["scrum"], 'query_claude', new=AsyncMock(return_value="dev")):

                task = sample_tasks[0]

                try:
                    result = await coordinator.coordinate_task_manager_pattern(task)

                    # Verify result structure
                    assert result is not None
                    assert "task_id" in result
                    assert result["task_id"] == task.id

                    # Verify message history shows coordination. In this
                    # pattern the Scrum Master sends the messages (the
                    # assignment to dev, the handoff to QA); dev sends none.
                    # get_message_history() returns what an agent sent.
                    scrum_messages = await coordinator.message_bus.get_message_history("scrum")
                    assert any(
                        m.message_type == "task_assignment" and m.to_agent == "dev"
                        for m in scrum_messages
                    )

                    print("OK: Manager pattern workflow completed")
                    print(f"  Task: {task.id}")
                    print(f"  Messages sent by the Scrum Master: {len(scrum_messages)}")

                except NotImplementedError:
                    pytest.skip("Manager pattern not yet implemented")

        finally:
            await coordinator.cleanup()

    @pytest.mark.asyncio
    async def test_manager_concurrent_tasks(self, test_config, sample_tasks):
        """
        Test manager pattern handling multiple concurrent tasks.

        Verifies that Scrum agent can coordinate multiple tasks in parallel.
        """
        coordinator = SwarmCoordinator(test_config, CoordinationPattern.MANAGER)

        try:
            await coordinator.setup()

            with patch.object(coordinator.agents["dev"], 'query_claude', new=AsyncMock(return_value="Done")), \
                 patch.object(coordinator.agents["qa"], 'query_claude', new=AsyncMock(return_value="Approved")), \
                 patch.object(coordinator.agents["scrum"], 'query_claude', new=AsyncMock(return_value="dev")):

                try:
                    # Execute multiple tasks concurrently
                    results = await asyncio.gather(
                        coordinator.coordinate_task_manager_pattern(sample_tasks[0]),
                        coordinator.coordinate_task_manager_pattern(sample_tasks[1]),
                        return_exceptions=True
                    )

                    # gather(return_exceptions=True) returns the exception
                    # instead of raising it, so detect the unimplemented case
                    # here rather than in the except clause below.
                    if all(isinstance(r, NotImplementedError) for r in results):
                        pytest.skip("Manager pattern not yet implemented")

                    # Check that tasks completed
                    successful = [r for r in results if not isinstance(r, Exception)]
                    assert len(successful) > 0

                    print(f"OK: Concurrent tasks completed: {len(successful)}/{len(sample_tasks[:2])}")

                except NotImplementedError:
                    pytest.skip("Manager pattern not yet implemented")

        finally:
            await coordinator.cleanup()


@pytest.mark.integration
class TestPeerPatternIntegration:
    """Integration tests for peer-to-peer pattern."""

    @pytest.mark.asyncio
    async def test_full_peer_workflow(self, test_config, sample_tasks):
        """
        Test complete peer-to-peer workflow with real Redis.

        Verifies direct communication between Dev and QA agents.
        """
        coordinator = SwarmCoordinator(test_config, CoordinationPattern.PEER_TO_PEER)

        try:
            await coordinator.setup()

            with patch.object(coordinator.agents["dev"], 'query_claude', new=AsyncMock(return_value="Implementation complete")), \
                 patch.object(coordinator.agents["qa"], 'query_claude', new=AsyncMock(return_value="Score: 8/10. Approved.")):

                task = sample_tasks[0]

                try:
                    result = await coordinator.coordinate_task_peer_pattern(task)

                    # Verify result
                    assert result is not None
                    assert "task_id" in result

                    # Verify direct messaging occurred
                    dev_messages = await coordinator.message_bus.get_message_history("dev")
                    qa_messages = await coordinator.message_bus.get_message_history("qa")

                    print(f"OK: Peer-to-peer workflow completed successfully")
                    print(f"  Dev messages: {len(dev_messages)}")
                    print(f"  QA messages: {len(qa_messages)}")

                except NotImplementedError:
                    pytest.skip("Peer pattern not yet implemented")

        finally:
            await coordinator.cleanup()

    @pytest.mark.asyncio
    async def test_peer_negotiation_with_feedback(self, test_config, sample_tasks):
        """
        Test peer pattern negotiation when QA provides feedback.

        Simulates multiple rounds of feedback and iteration.
        """
        coordinator = SwarmCoordinator(test_config, CoordinationPattern.PEER_TO_PEER)

        try:
            await coordinator.setup()

            # Mock QA to provide feedback first, then approve
            qa_responses = [
                "Score: 6/10. Issues: Security concerns, performance issues.",
                "Score: 9/10. Much improved. Approved."
            ]

            qa_call_count = [0]

            async def qa_mock(*args, **kwargs):
                response = qa_responses[min(qa_call_count[0], len(qa_responses) - 1)]
                qa_call_count[0] += 1
                return response

            with patch.object(coordinator.agents["dev"], 'query_claude', new=AsyncMock(return_value="Fixed")), \
                 patch.object(coordinator.agents["qa"], 'query_claude', new=AsyncMock(side_effect=qa_mock)):

                task = sample_tasks[0]

                try:
                    result = await coordinator.coordinate_task_peer_pattern(task)

                    # Verify negotiation occurred
                    assert qa_call_count[0] > 1, "Expected multiple QA reviews"

                    print(f"OK: Peer negotiation completed")
                    print(f"  Negotiation rounds: {qa_call_count[0]}")

                except NotImplementedError:
                    pytest.skip("Peer pattern not yet implemented")

        finally:
            await coordinator.cleanup()


@pytest.mark.integration
class TestBlackboardPatternIntegration:
    """Integration tests for blackboard pattern."""

    @pytest.mark.asyncio
    async def test_full_blackboard_workflow(self, test_config, sample_tasks):
        """
        Test complete blackboard workflow with real Redis.

        Verifies shared state coordination through blackboard.
        """
        coordinator = SwarmCoordinator(test_config, CoordinationPattern.BLACKBOARD)

        try:
            await coordinator.setup()

            # Clear any existing tasks
            await coordinator.blackboard.clear()

            with patch.object(coordinator.agents["dev"], 'query_claude', new=AsyncMock(return_value="Implementation done")), \
                 patch.object(coordinator.agents["qa"], 'query_claude', new=AsyncMock(return_value="Quality: 9/10. Approved.")):

                task = sample_tasks[0]

                try:
                    result = await coordinator.coordinate_task_blackboard_pattern(task)

                    # Verify result
                    assert result is not None
                    assert "task_id" in result

                    # Verify task was posted to blackboard
                    task_state = await coordinator.blackboard.get_task(task.id)
                    assert task_state is not None

                    # Verify history
                    assert len(task_state.history) > 0

                    # The QA handoff must succeed on real Redis: dev releases
                    # the claim after ready_for_review (release_task), then QA
                    # claims and completes. A task left with dev holding the
                    # claim means the QA-side updates were rejected.
                    assert task_state.status == "complete"
                    assert task_state.assigned_to == "qa"

                    print(f"OK: Blackboard workflow completed successfully")
                    print(f"  Final status: {task_state.status}")
                    print(f"  History entries: {len(task_state.history)}")

                except NotImplementedError:
                    pytest.skip("Blackboard pattern not yet implemented")

        finally:
            if coordinator.blackboard:  # setup() may have failed before Redis connected
                await coordinator.blackboard.clear()
            await coordinator.cleanup()

    @pytest.mark.asyncio
    async def test_blackboard_concurrent_tasks(self, test_config, sample_tasks):
        """
        Test blackboard pattern with concurrent tasks.

        Verifies that multiple tasks can be on blackboard simultaneously
        and agents can claim them appropriately.
        """
        coordinator = SwarmCoordinator(test_config, CoordinationPattern.BLACKBOARD)

        try:
            await coordinator.setup()
            await coordinator.blackboard.clear()

            with patch.object(coordinator.agents["dev"], 'query_claude', new=AsyncMock(return_value="Done")), \
                 patch.object(coordinator.agents["qa"], 'query_claude', new=AsyncMock(return_value="Approved")):

                try:
                    # Post multiple tasks
                    for task in sample_tasks:
                        task_state = TaskState(task.id, task.description)
                        await coordinator.blackboard.post_task(task_state)

                    # Verify all posted
                    all_tasks = await coordinator.blackboard.get_tasks()
                    assert len(all_tasks) >= len(sample_tasks)

                    print(f"OK: Multiple tasks on blackboard: {len(all_tasks)}")

                    # Execute one task through coordination
                    result = await coordinator.coordinate_task_blackboard_pattern(sample_tasks[0])

                    print(f"OK: Coordinated task from blackboard with concurrent tasks")

                except NotImplementedError:
                    pytest.skip("Blackboard pattern not yet implemented")

        finally:
            if coordinator.blackboard:  # setup() may have failed before Redis connected
                await coordinator.blackboard.clear()
            await coordinator.cleanup()

    @pytest.mark.asyncio
    async def test_claim_release_handoff(self, test_config, sample_tasks):
        """
        Test the dev-to-QA claim handoff against real Redis.

        While dev holds the claim, QA's claim is rejected. After dev marks
        the work ready_for_review and calls release_task, QA claims and
        completes. This drives the blackboard directly, so it runs even
        before coordinate_task_blackboard_pattern is implemented.
        """
        blackboard = Blackboard(test_config)

        try:
            await blackboard.initialize()
            await blackboard.clear()

            task = sample_tasks[0]
            await blackboard.post_task(TaskState(task.id, task.description))

            # Dev claims and works the task
            assert await blackboard.claim_task(task.id, "dev") is True
            assert await blackboard.update_task(
                task.id, "dev", status="in_progress"
            ) is True
            assert await blackboard.update_task(
                task.id, "dev",
                status="ready_for_review",
                data={"implementation": "stub implementation"}
            ) is True

            # QA cannot claim while dev still holds the task
            assert await blackboard.claim_task(task.id, "qa") is False
            print("OK: QA claim rejected while dev held the task")

            # Dev releases; the ready_for_review status survives
            assert await blackboard.release_task(task.id, "dev") is True
            state = await blackboard.get_task(task.id)
            assert state.assigned_to is None
            assert state.status == "ready_for_review"
            print("OK: Dev released the claim after ready_for_review")

            # QA claims and completes the review
            assert await blackboard.claim_task(task.id, "qa") is True
            assert await blackboard.update_task(
                task.id, "qa", status="in_review"
            ) is True
            assert await blackboard.update_task(
                task.id, "qa",
                status="complete",
                data={"qa_validation": {"approved": True}}
            ) is True

            final = await blackboard.get_task(task.id)
            assert final.status == "complete"
            assert final.assigned_to == "qa"
            assert any(entry["action"] == "released" for entry in final.history)
            print("OK: QA claimed and completed the review")

        finally:
            await blackboard.clear()
            await blackboard.close()

    @pytest.mark.asyncio
    async def test_blackboard_state_persistence(self, test_config, sample_tasks):
        """
        Test that blackboard state persists across coordinator instances.

        Verifies Redis persistence works correctly.
        """
        task = sample_tasks[0]

        # First coordinator posts task
        coordinator1 = SwarmCoordinator(test_config, CoordinationPattern.BLACKBOARD)
        try:
            await coordinator1.setup()
            await coordinator1.blackboard.clear()

            task_state = TaskState(task.id, task.description, status="pending")
            await coordinator1.blackboard.post_task(task_state)

            print(f"OK: Task posted by coordinator 1")

        finally:
            await coordinator1.cleanup()

        # Second coordinator retrieves task
        coordinator2 = SwarmCoordinator(test_config, CoordinationPattern.BLACKBOARD)
        try:
            await coordinator2.setup()

            retrieved_task = await coordinator2.blackboard.get_task(task.id)
            assert retrieved_task is not None
            assert retrieved_task.task_id == task.id
            assert retrieved_task.description == task.description

            print(f"OK: Task retrieved by coordinator 2")
            print(f"  State persisted across instances")

        finally:
            if coordinator2.blackboard:
                await coordinator2.blackboard.clear()
            await coordinator2.cleanup()


@pytest.mark.integration
class TestPatternComparison:
    """Integration tests comparing all three patterns."""

    @pytest.mark.asyncio
    async def test_all_patterns_with_same_task(self, test_config, sample_tasks):
        """
        Execute same task through all three patterns and compare.

        This test demonstrates the differences in coordination approaches.
        """
        task = sample_tasks[0]
        results = {}

        for pattern in [CoordinationPattern.MANAGER, CoordinationPattern.PEER_TO_PEER, CoordinationPattern.BLACKBOARD]:
            coordinator = SwarmCoordinator(test_config, pattern)

            try:
                await coordinator.setup()

                if pattern == CoordinationPattern.BLACKBOARD:
                    await coordinator.blackboard.clear()

                with patch.object(coordinator.agents["dev"], 'query_claude', new=AsyncMock(return_value="Done")), \
                     patch.object(coordinator.agents["qa"], 'query_claude', new=AsyncMock(return_value="Approved")), \
                     patch.object(coordinator.agents.get("scrum", coordinator.agents["dev"]), 'query_claude', new=AsyncMock(return_value="dev")):

                    try:
                        if pattern == CoordinationPattern.MANAGER:
                            result = await coordinator.coordinate_task_manager_pattern(task)
                        elif pattern == CoordinationPattern.PEER_TO_PEER:
                            result = await coordinator.coordinate_task_peer_pattern(task)
                        else:  # BLACKBOARD
                            result = await coordinator.coordinate_task_blackboard_pattern(task)

                        results[pattern.value] = result
                        print(f"OK: Completed with {pattern.value} pattern")

                    except NotImplementedError:
                        print(f"SKIP: {pattern.value} pattern not yet implemented")

            finally:
                if pattern == CoordinationPattern.BLACKBOARD and coordinator.blackboard:
                    await coordinator.blackboard.clear()
                await coordinator.cleanup()

        # Compare results if all patterns completed
        if len(results) == 3:
            print(f"\nOK: All patterns completed successfully")
            print(f"  Patterns compared: {list(results.keys())}")
            print(f"\n  Pattern characteristics:")
            print(f"    - Manager: Centralized coordination through Scrum agent")
            print(f"    - Peer-to-peer: Direct communication between Dev and QA")
            print(f"    - Blackboard: Shared state with opportunistic claiming")


# Run from hands-on-lab/: pytest starter/tests/test_integration.py -v -m integration
# Requires Redis running on localhost:6379
