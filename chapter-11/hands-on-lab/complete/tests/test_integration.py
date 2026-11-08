"""
Integration tests for Zero-Downtime Deployer.

These tests verify the complete system working together.
"""

import pytest
import asyncio

from ..deployer import ZeroDowntimeDeployer
from ..config import DeploymentConfig
from ..infrastructure_client import InfrastructureClient
from ..health_monitor import HealthMonitor
from ..memory_integration import DeploymentMemory


@pytest.fixture
def full_system(tmp_path):
    """Create complete system for integration testing."""
    infra = InfrastructureClient(use_mock=True)
    health_monitor = HealthMonitor(infra)
    # Memory lives in a per-test temporary directory (no residue on disk)
    memory = DeploymentMemory(persist_dir=str(tmp_path / "memory"))

    deployer = ZeroDowntimeDeployer(
        infrastructure_client=infra,
        health_monitor=health_monitor,
        memory=memory,
        traffic_stabilization_seconds=0  # Skip production pauses in tests
    )

    return {
        "deployer": deployer,
        "infra": infra,
        "health_monitor": health_monitor,
        "memory": memory
    }


@pytest.mark.asyncio
async def test_end_to_end_successful_deployment(full_system):
    """
    Test complete successful deployment flow.

    This test verifies:
    - Infrastructure client works
    - Health monitor collects metrics
    - Deployer orchestrates correctly
    - Memory records success
    """
    deployer = full_system["deployer"]
    memory = full_system["memory"]

    config = DeploymentConfig(
        service_name="integration-test",
        version="1.0.0",
        image="test:1.0.0",
        replicas=3,
        validation_duration_seconds=5
    )

    # Execute deployment
    result = await deployer.deploy(config)

    # Verify result
    print(f"Integration test result: {result}")
    assert "deployment_id" in result
    assert result["status"] == "success"

    # Check memory recorded the deployment
    history = await memory.get_service_history("integration-test")
    assert len(history) >= 1, "Successful deployment must be recorded in memory"
    print(f"Service history after deployment: {len(history)} records")


@pytest.mark.asyncio
async def test_end_to_end_failed_deployment_with_rollback(full_system):
    """
    Test deployment failure and automatic rollback.

    This test verifies:
    - Bad deployment is detected
    - Rollback is triggered automatically
    - System returns to stable state
    - Failure is recorded in memory
    """
    deployer = full_system["deployer"]
    memory = full_system["memory"]

    config = DeploymentConfig(
        service_name="integration-test",
        version="1.0.0-bad",  # Intentionally bad
        image="test:1.0.0-bad",
        replicas=3,
        validation_duration_seconds=5
    )

    # Execute deployment (should fail)
    result = await deployer.deploy(config)

    print(f"Failed deployment result: {result}")
    assert result["status"] == "failed"

    # Rollback must have run and succeeded
    assert "rollback" in result, "Auto-rollback should run for a failed deployment"
    assert result["rollback"]["success"] is True, (
        f"Rollback should succeed: {result['rollback']}"
    )

    # Check the rollback was recorded
    patterns = await memory.get_failure_patterns("integration-test")
    assert patterns["total_rollbacks"] >= 1, (
        "The rollback must be recorded in deployment memory"
    )
    print(f"Failure patterns: {patterns}")


@pytest.mark.asyncio
async def test_infrastructure_client_operations(full_system):
    """Test infrastructure client operations."""
    infra = full_system["infra"]

    # Test create deployment
    deployment = await infra.create_deployment({
        "name": "test-deployment",
        "image": "test:1.0.0",
        "replicas": 3
    })
    assert deployment["status"] == "ready"

    # Test list deployments
    deployments = await infra.list_deployments("test-service")
    assert isinstance(deployments, list)

    # Test set traffic
    traffic_result = await infra.set_traffic("test-service", "1.0.0", 50)
    assert traffic_result["success"] is True

    print("Infrastructure client operations: OK")


@pytest.mark.asyncio
async def test_health_monitor_continuous_monitoring(full_system):
    """Test continuous health monitoring."""
    health_monitor = full_system["health_monitor"]

    result = await health_monitor.monitor_continuously(
        service_name="test-service",
        version="1.0.0",
        duration_seconds=10,
        thresholds={
            "error_rate": 0.01,
            "latency_p99_ms": 500,
            "cpu_percent": 0.8,
            "memory_percent": 0.8
        },
        sample_interval=2
    )

    assert "samples" in result
    assert len(result["samples"]) > 0
    assert "summary" in result

    print(f"Health monitoring: {len(result['samples'])} samples collected")


@pytest.mark.asyncio
async def test_memory_operations(full_system):
    """Test memory operations."""
    memory = full_system["memory"]

    # Record a deployment
    await memory.remember_session(
        session_type="deployment",
        summary="Test deployment",
        details="Integration test deployment",
        outcome="success",
        project="test-service"
    )

    # Recall the deployment
    results = await memory.recall("test deployment", n_results=5)
    assert "episodic" in results

    # Get service history
    history = await memory.get_service_history("test-service")
    assert isinstance(history, list)

    print("Memory operations: OK")


@pytest.mark.asyncio
async def test_multiple_sequential_deployments(full_system):
    """
    Test multiple deployments in sequence.

    Verifies that memory accumulates correctly and later deployments
    can learn from earlier ones.
    """
    deployer = full_system["deployer"]
    memory = full_system["memory"]

    # First deployment
    config1 = DeploymentConfig(
        service_name="multi-deploy-test",
        version="1.0.0",
        image="test:1.0.0",
        replicas=3,
        validation_duration_seconds=3
    )
    result1 = await deployer.deploy(config1)
    print(f"First deployment: {result1['status']}")

    # Second deployment (should benefit from history)
    config2 = DeploymentConfig(
        service_name="multi-deploy-test",
        version="1.1.0",
        image="test:1.1.0",
        replicas=3,
        validation_duration_seconds=3
    )
    result2 = await deployer.deploy(config2)
    print(f"Second deployment: {result2['status']}")

    # Check accumulated history
    history = await memory.get_service_history("multi-deploy-test")
    print(f"Accumulated history: {len(history)} deployments")
    assert len(history) >= 2


"""
Integration Test Guidelines:

These tests verify the complete system working together. They should pass
once you complete Exercises 1 and 2.

To run integration tests:

1. Run all integration tests:
   pytest complete/tests/test_integration.py -v

2. Run specific test:
   pytest complete/tests/test_integration.py::test_end_to_end_successful_deployment -v

3. Run with detailed output:
   pytest complete/tests/test_integration.py -v -s

4. Run both unit and integration tests:
   pytest complete/tests/ -v

Integration tests take longer to run than unit tests because they:
- Exercise the full system
- Include wait times for monitoring
- Test multiple sequential operations
"""
