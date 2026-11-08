#!/usr/bin/env python3
"""
Example usage of the multi-agent swarm coordinator.

This script demonstrates how to use the SwarmCoordinator
with all three coordination patterns.

NOTE: This will only work after you complete the TODO exercises
in swarm_coordinator.py.
"""

import asyncio
import logging
from dotenv import load_dotenv

from starter.swarm_coordinator import SwarmCoordinator, CoordinationPattern, Task
from starter.config import load_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def example_manager_pattern():
    """Example: Manager pattern coordination."""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Manager Pattern (Hierarchical Coordination)")
    print("=" * 60 + "\n")

    # Load configuration
    config = load_config()

    # Create coordinator with manager pattern
    coordinator = SwarmCoordinator(config.dict(), CoordinationPattern.MANAGER)

    try:
        # Setup swarm
        await coordinator.setup()
        logger.info("Swarm initialized with Manager pattern")

        # Create a task
        task = Task(
            id="feature_001",
            description="Implement user authentication with JWT tokens and refresh token rotation"
        )

        print(f"Task: {task.description}\n")

        # Coordinate task execution
        result = await coordinator.coordinate_task_manager_pattern(task)

        # Display results
        print("\nResults:")
        print(f"  Task ID: {result.get('task_id')}")
        print(f"  Status: {result.get('status', 'unknown')}")
        print(f"  Coordinator: {result.get('coordinator', 'scrum')}")
        print("\nManager pattern coordination finished.\n")

    except NotImplementedError:
        print("\nNote: manager pattern not yet implemented.")
        print("Complete Exercise 1 in swarm_coordinator.py first.\n")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await coordinator.cleanup()


async def example_peer_pattern():
    """Example: Peer-to-peer pattern coordination."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Peer-to-Peer Pattern (Direct Communication)")
    print("=" * 60 + "\n")

    config = load_config()
    coordinator = SwarmCoordinator(config.dict(), CoordinationPattern.PEER_TO_PEER)

    try:
        await coordinator.setup()
        logger.info("Swarm initialized with Peer-to-Peer pattern")

        task = Task(
            id="feature_002",
            description="Add rate limiting middleware to protect API endpoints"
        )

        print(f"Task: {task.description}\n")

        result = await coordinator.coordinate_task_peer_pattern(task)

        print("\nResults:")
        print(f"  Task ID: {result.get('task_id')}")
        print(f"  Iterations: {result.get('iterations', 'N/A')}")
        print(f"  Final Review: {result.get('final_review', {}).get('approved', 'unknown')}")
        print("\nPeer-to-peer pattern coordination finished.\n")

    except NotImplementedError:
        print("\nNote: peer-to-peer pattern not yet implemented.")
        print("Complete Exercise 2 in swarm_coordinator.py first.\n")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await coordinator.cleanup()


async def example_blackboard_pattern():
    """Example: Blackboard pattern coordination."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Blackboard Pattern (Shared State Coordination)")
    print("=" * 60 + "\n")

    config = load_config()
    coordinator = SwarmCoordinator(config.dict(), CoordinationPattern.BLACKBOARD)

    try:
        await coordinator.setup()
        logger.info("Swarm initialized with Blackboard pattern")

        # Clear any existing tasks
        await coordinator.blackboard.clear()

        task = Task(
            id="feature_003",
            description="Implement database connection pooling with automatic retry logic"
        )

        print(f"Task: {task.description}\n")

        result = await coordinator.coordinate_task_blackboard_pattern(task)

        print("\nResults:")
        print(f"  Task ID: {result.get('task_id')}")
        print(f"  Final State: {result.get('final_state', {}).get('status', 'unknown')}")
        print(f"  History Entries: {len(result.get('history', []))}")
        print("\nBlackboard pattern coordination finished.\n")

        # Display history
        if 'history' in result and result['history']:
            print("Task History:")
            for entry in result['history']:
                print(f"  - {entry.get('action')} by {entry.get('agent_id')} at {entry.get('timestamp')}")

    except NotImplementedError:
        print("\nNote: blackboard pattern not yet implemented.")
        print("Complete Exercise 3 in swarm_coordinator.py first.\n")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        if coordinator.blackboard:  # setup() may fail before Redis connects
            await coordinator.blackboard.clear()
        await coordinator.cleanup()


async def example_compare_patterns():
    """Example: Compare all three patterns with the same task."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Comparing All Coordination Patterns")
    print("=" * 60 + "\n")

    config = load_config()

    task = Task(
        id="feature_compare",
        description="Add error handling and logging across the API"
    )

    print(f"Task: {task.description}\n")
    print("Executing with all three patterns...\n")

    results = {}

    for pattern in [CoordinationPattern.MANAGER, CoordinationPattern.PEER_TO_PEER, CoordinationPattern.BLACKBOARD]:
        coordinator = SwarmCoordinator(config.dict(), pattern)

        try:
            await coordinator.setup()

            if pattern == CoordinationPattern.BLACKBOARD:
                await coordinator.blackboard.clear()

            # Execute task
            result = await coordinator.execute_task(task)
            results[pattern.value] = result

            print(f"OK: {pattern.value.upper()} pattern completed")

        except NotImplementedError:
            print(f"SKIP: {pattern.value.upper()} pattern not yet implemented")
        except Exception as e:
            print(f"FAIL: {pattern.value.upper()} pattern failed: {e}")
        finally:
            if pattern == CoordinationPattern.BLACKBOARD and coordinator.blackboard:
                await coordinator.blackboard.clear()
            await coordinator.cleanup()

    # Summary
    if results:
        print(f"\n{'=' * 60}")
        print("Pattern Comparison Summary")
        print("=" * 60 + "\n")

        for pattern_name, result in results.items():
            print(f"{pattern_name.upper()}:")
            print(f"  - Task ID: {result.get('task_id')}")
            print(f"  - Completed: {result is not None}")
            print()

        print("Key Differences:")
        print("  MANAGER: Centralized coordination, clear hierarchy")
        print("  PEER-TO-PEER: Distributed decision-making, direct communication")
        print("  BLACKBOARD: Opportunistic claiming, shared state")
        print()


async def main():
    """Run all examples."""
    load_dotenv()

    print("\n" + "=" * 60)
    print("Swarm Coordinator - Usage Examples")
    print("=" * 60)

    try:
        # Run examples
        await example_manager_pattern()
        await asyncio.sleep(1)

        await example_peer_pattern()
        await asyncio.sleep(1)

        await example_blackboard_pattern()
        await asyncio.sleep(1)

        await example_compare_patterns()

        print("\n" + "=" * 60)
        print("All examples completed!")
        print("=" * 60 + "\n")

    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
