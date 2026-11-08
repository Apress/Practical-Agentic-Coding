"""
Tests for Zero-Downtime Deployer.

These tests verify your implementations of:
- Exercise 1: Canary validation
- Exercise 2: Automatic rollback
"""

import pytest
import asyncio
from datetime import datetime

from ..deployer import ZeroDowntimeDeployer, DeploymentPhase
from ..config import DeploymentConfig, ThresholdConfig
from ..infrastructure_client import InfrastructureClient
from ..health_monitor import HealthMonitor
from ..memory_integration import DeploymentMemory


@pytest.fixture
def deployment_config():
    """Create test deployment configuration."""
    return DeploymentConfig(
        service_name="test-service",
        version="2.0.0",
        image="test-service:2.0.0",
        replicas=3,
        canary_percentage=10,
        validation_duration_seconds=5,  # Short for tests
        traffic_shift_steps=[10, 50, 100]
    )


@pytest.fixture
def mock_infra():
    """Create mock infrastructure client."""
    return InfrastructureClient(use_mock=True)


@pytest.fixture
def mock_memory(tmp_path):
    """Create memory in a per-test temporary directory (no residue on disk)."""
    return DeploymentMemory(persist_dir=str(tmp_path / "memory"))


@pytest.fixture
def deployer(mock_infra, mock_memory):
    """Create deployer instance for testing."""
    health_monitor = HealthMonitor(mock_infra)
    return ZeroDowntimeDeployer(
        infrastructure_client=mock_infra,
        health_monitor=health_monitor,
        memory=mock_memory,
        traffic_stabilization_seconds=0  # Skip production pauses in tests
    )


# ============================================================================
# Exercise 1 Tests: Canary Validation
# ============================================================================

@pytest.mark.asyncio
async def test_canary_validation_healthy(deployer, deployment_config):
    """
    Test canary validation with healthy service.

    This test verifies your Exercise 1 implementation:
    - Metrics collection over validation period
    - Threshold checking
    - Healthy result when all metrics pass
    """
    result = await deployer.validate_canary(deployment_config, duration_seconds=5)

    assert "healthy" in result, "Result should have 'healthy' key"
    assert "reason" in result, "Result should have 'reason' key"
    assert "issues" in result, "Result should have 'issues' key"
    assert "placeholder" not in result["reason"].lower(), (
        "validate_canary() still returns the starter placeholder. "
        "Implement it in Exercise 1."
    )
    assert result["healthy"] is True, (
        f"A healthy version must pass validation: {result['reason']}"
    )
    assert len(result["samples"]) > 0, (
        "Validation must collect at least one metrics sample"
    )
    print(f"Validation result: {result}")


@pytest.mark.asyncio
async def test_canary_validation_unhealthy(deployer):
    """
    Test canary validation with unhealthy service.

    This test verifies your Exercise 1 implementation detects failures.
    """
    # Create config for intentionally bad version
    bad_config = DeploymentConfig(
        service_name="test-service",
        version="2.0.0-bad",  # "bad" triggers high error rates in mock
        image="test-service:2.0.0-bad",
        replicas=3,
        validation_duration_seconds=5
    )

    result = await deployer.validate_canary(bad_config, duration_seconds=5)

    # The mock gives '-bad' versions error rates and latencies above every
    # threshold, so a working implementation must flag them
    assert result["healthy"] is False, (
        "A '-bad' version must fail validation: the mock reports error "
        "rates above every threshold for it"
    )
    assert len(result["issues"]) > 0, (
        "An unhealthy result must list the threshold violations"
    )
    print(f"Validation result for bad version: {result}")


@pytest.mark.asyncio
async def test_canary_validation_memory_integration(deployer, deployment_config, mock_memory):
    """
    Test that canary validation uses memory to inform decisions.

    This test verifies Exercise 1's memory integration:
    - Queries memory for past failures
    - Adjusts thresholds based on history
    """
    # Record a past failure
    await mock_memory.remember_session(
        session_type="deployment",
        summary=f"Deployment failed: {deployment_config.service_name}",
        details="High error rate during validation",
        outcome="failure",
        project=deployment_config.service_name
    )

    # Now validate - should be more conservative
    result = await deployer.validate_canary(deployment_config, duration_seconds=5)

    assert "placeholder" not in result["reason"].lower(), (
        "validate_canary() still returns the starter placeholder. "
        "Implement it (including the memory query) in Exercise 1."
    )

    # The recorded failure must be retrievable while validation runs
    history = await mock_memory.get_service_history(deployment_config.service_name)
    assert len(history) > 0, "Should have deployment history"
    print(f"Service history: {len(history)} records")


# ============================================================================
# Exercise 2 Tests: Automatic Rollback
# ============================================================================

@pytest.mark.asyncio
async def test_rollback_success(deployer, deployment_config):
    """
    Test successful rollback.

    This test verifies your Exercise 2 implementation:
    - Identifies stable version
    - Shifts traffic to stable
    - Removes failing deployment
    - Verifies rollback succeeded
    """
    result = await deployer.rollback(
        deployment_config,
        reason="Test rollback"
    )

    assert "placeholder" not in str(result.get("reason", "")).lower(), (
        "rollback() still returns the starter placeholder. "
        "Implement it in Exercise 2."
    )
    assert result["success"] is True, f"Rollback should succeed: {result}"
    assert result["stable_version"] == "1.0.0", (
        "Rollback must target the version serving the most traffic "
        "(1.0.0 in the mock infrastructure)"
    )
    assert "duration_seconds" in result, (
        "Result should report how long the rollback took"
    )
    assert "final_health" in result, (
        "Result should include the post-rollback health verification"
    )
    print(f"Rollback result: {result}")


@pytest.mark.asyncio
async def test_rollback_records_in_memory(deployer, deployment_config, mock_memory):
    """
    Test that rollback is recorded in memory.

    This test verifies Exercise 2's memory integration:
    - Rollback event is saved
    - Includes reason and details
    """
    result = await deployer.rollback(deployment_config, reason="High error rate")
    assert result["success"] is True, f"Rollback should succeed: {result}"

    # Check memory for the rollback record
    history = await mock_memory.recall("rollback test-service", n_results=10)
    rollback_records = [
        r for r in history.get("episodic", [])
        if r.get("session_type") == "rollback"
    ]
    assert len(rollback_records) > 0, (
        "Rollback must be recorded in memory (session_type='rollback')"
    )
    assert "High error rate" in rollback_records[0].get("details", ""), (
        "The rollback record must include the reason"
    )
    print(f"Rollback history: {len(rollback_records)} records")


@pytest.mark.asyncio
async def test_automatic_rollback_on_validation_failure(deployer):
    """
    Test that deployment automatically rolls back on validation failure.

    This test verifies integration of Exercise 1 and 2:
    - Canary validation fails
    - Automatic rollback is triggered
    - System returns to stable state
    """
    # Deploy a bad version
    bad_config = DeploymentConfig(
        service_name="test-service",
        version="2.0.0-bad",
        image="test-service:2.0.0-bad",
        replicas=3,
        validation_duration_seconds=5
    )

    result = await deployer.deploy(bad_config)

    # Should have failed during canary validation and rolled back
    assert result["status"] == "failed", "Deployment should fail for bad version"
    assert result["reason"] == "Canary validation failed", (
        "The bad version must be caught by canary validation (Exercise 1), "
        f"not later in the flow. Got: {result.get('reason')}"
    )
    assert "rollback" in result, (
        "Auto-rollback must run when canary validation fails (Exercise 2)"
    )
    assert "placeholder" not in str(result["rollback"].get("reason", "")).lower(), (
        "rollback() still returns the starter placeholder. "
        "Implement it in Exercise 2."
    )
    assert result["rollback"]["success"] is True, (
        f"Rollback should succeed: {result['rollback']}"
    )
    print(f"Auto-rollback executed: {result['rollback']}")


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_full_deployment_flow(deployer, deployment_config):
    """
    Test complete deployment flow.

    This is an end-to-end test that exercises:
    - Canary deployment
    - Canary validation
    - Progressive traffic shifting
    - Completion
    """
    result = await deployer.deploy(deployment_config)

    print(f"Full deployment result: {result}")
    assert "deployment_id" in result
    assert result["status"] == "success", (
        f"A healthy version should deploy end to end: {result}"
    )


@pytest.mark.asyncio
async def test_deployment_phases(deployer, deployment_config):
    """Test that deployment progresses through correct phases."""
    # This test just verifies phases are tracked
    assert deployer.current_phase == DeploymentPhase.PREPARING
    print(f"Initial phase: {deployer.current_phase}")


# ============================================================================
# Helper Tests
# ============================================================================

def test_deployment_config_creation():
    """Test deployment configuration."""
    config = DeploymentConfig(
        service_name="api",
        version="1.0.0",
        image="api:1.0.0",
        replicas=5
    )

    assert config.service_name == "api"
    assert config.canary_percentage == 10  # Default
    assert config.traffic_shift_steps is not None
    print(f"Config: {config}")


def test_threshold_config():
    """Test threshold configuration."""
    thresholds = ThresholdConfig(
        error_rate=0.01,
        latency_p99_ms=500,
        cpu_percent=0.8,
        memory_percent=0.8
    )

    assert thresholds.error_rate == 0.01
    print(f"Thresholds: {thresholds}")


# ============================================================================
# Test Execution Instructions
# ============================================================================

"""
To run these tests:

1. Run all tests:
   pytest complete/tests/test_deployer.py -v

2. Run specific test:
   pytest complete/tests/test_deployer.py::test_canary_validation_healthy -v

3. Run with output:
   pytest complete/tests/test_deployer.py -v -s

4. Run Exercise 1 tests only:
   pytest complete/tests/test_deployer.py -v -k canary

5. Run Exercise 2 tests only:
   pytest complete/tests/test_deployer.py -v -k rollback

Expected behavior:
- This is the reference-solution copy: all tests pass here as shipped.
- The identical suite in starter/tests/ fails on the canary and rollback
  tests until Exercises 1 and 2 are implemented.
"""
