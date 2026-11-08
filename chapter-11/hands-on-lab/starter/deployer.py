"""
Zero-Downtime Deployer - Main Implementation

This module contains the core deployment agent with TODOs for exercises.
Complete the TODOs to implement canary deployment, rollback, and Sentry integration.
"""

from typing import Dict, List
from datetime import datetime, timedelta
from enum import Enum
import asyncio

from .config import DeploymentConfig, config
from .infrastructure_client import InfrastructureClient
from .health_monitor import HealthMonitor


class DeploymentPhase(Enum):
    """Deployment phases."""
    PREPARING = "preparing"
    DEPLOYING_CANARY = "deploying_canary"
    VALIDATING_CANARY = "validating_canary"
    SHIFTING_TRAFFIC = "shifting_traffic"
    COMPLETING = "completing"
    ROLLING_BACK = "rolling_back"
    COMPLETED = "completed"
    FAILED = "failed"


class ZeroDowntimeDeployer:
    """
    Orchestrates zero-downtime deployments with canary validation and automatic rollback.

    This class implements CA/CD (Continuous Agentic Delivery) patterns:
    - Intelligent canary deployment
    - Memory-informed decision making
    - Automatic rollback on failure
    - Integration with observability tools
    """

    def __init__(
        self,
        memory = None,
        infrastructure_client: InfrastructureClient = None,
        health_monitor: HealthMonitor = None,
        traffic_stabilization_seconds: int = None
    ):
        """
        Initialize deployer.

        The first two parameters follow the book's Section 11.6 listing,
        ZeroDowntimeDeployer(memory, infrastructure_client); the tests pass
        everything by keyword.

        Args:
            memory: DevMemory instance (from Chapter 9)
            infrastructure_client: Client for infrastructure operations
            health_monitor: Health monitoring client
            traffic_stabilization_seconds: Pause after each traffic shift before
                the next health check. Defaults to
                TRAFFIC_STABILIZATION_SECONDS from .env (30). Pass 0 in tests so
                the suite does not wait through real production pauses.
        """
        self.infra = infrastructure_client or InfrastructureClient(
            namespace=config.k8s_namespace,
            use_mock=config.use_mock_infrastructure
        )
        self.health_monitor = health_monitor or HealthMonitor(self.infra)
        self.memory = memory  # Will be set up in memory_integration.py
        self.traffic_stabilization_seconds = (
            config.traffic_stabilization_seconds
            if traffic_stabilization_seconds is None
            else traffic_stabilization_seconds
        )

        self.current_phase = DeploymentPhase.PREPARING
        self.deployment_history: List[Dict] = []

    async def deploy(self, deployment_config: DeploymentConfig) -> Dict:
        """
        Execute zero-downtime deployment.

        This is the main entry point for deployments. It orchestrates:
        1. Canary deployment
        2. Health validation
        3. Progressive traffic shifting
        4. Completion or rollback

        Args:
            deployment_config: Deployment configuration

        Returns:
            Deployment result dictionary
        """
        deployment_id = self._generate_deployment_id(deployment_config)
        print(f"\nStarting deployment: {deployment_id}")
        print(f"   Service: {deployment_config.service_name}")
        print(f"   Version: {deployment_config.version}")
        print(f"   Canary: {deployment_config.canary_percentage}%")

        try:
            # Phase 1: Deploy canary
            self._update_phase(DeploymentPhase.DEPLOYING_CANARY)
            canary_result = await self._deploy_canary(deployment_config)

            if not canary_result["success"]:
                return await self._handle_deployment_failure(
                    deployment_id,
                    deployment_config,
                    "Canary deployment failed"
                )

            print(f"   Canary deployed ({deployment_config.canary_percentage}% traffic)")

            # Phase 2: Validate canary (TODO: Exercise 1)
            self._update_phase(DeploymentPhase.VALIDATING_CANARY)
            validation_result = await self.validate_canary(
                deployment_config,
                deployment_config.validation_duration_seconds
            )

            if not validation_result["healthy"]:
                print(f"   Canary validation failed: {validation_result['reason']}")
                # TODO: Exercise 2 - Automatic rollback will be called here
                if config.auto_rollback_enabled:
                    rollback_result = await self.rollback(
                        deployment_config,
                        validation_result["reason"]
                    )
                    return {
                        "deployment_id": deployment_id,
                        "status": "failed",
                        "reason": "Canary validation failed",
                        "validation": validation_result,
                        "rollback": rollback_result
                    }
                else:
                    return {
                        "deployment_id": deployment_id,
                        "status": "failed",
                        "reason": "Canary validation failed (auto-rollback disabled)",
                        "validation": validation_result
                    }

            print(f"   Canary validated (healthy for {deployment_config.validation_duration_seconds}s)")

            # Phase 3: Progressive traffic shift
            self._update_phase(DeploymentPhase.SHIFTING_TRAFFIC)
            for percentage in deployment_config.traffic_shift_steps:
                if percentage <= deployment_config.canary_percentage:
                    continue  # Skip, already at this level

                print(f"   Shifting traffic to {percentage}%...")
                shift_result = await self.infra.set_traffic(
                    deployment_config.service_name,
                    deployment_config.version,
                    percentage
                )

                if not shift_result["success"]:
                    print(f"   Traffic shift to {percentage}% failed")
                    if config.auto_rollback_enabled:
                        rollback_result = await self.rollback(
                            deployment_config,
                            f"Traffic shift to {percentage}% failed"
                        )
                        return {
                            "deployment_id": deployment_id,
                            "status": "failed",
                            "reason": f"Traffic shift failed at {percentage}%",
                            "rollback": rollback_result
                        }

                # Brief validation after each shift
                if self.traffic_stabilization_seconds > 0:
                    # Let traffic stabilize before reading metrics again
                    await asyncio.sleep(self.traffic_stabilization_seconds)
                quick_check = await self.health_monitor.check_health(
                    deployment_config.service_name,
                    deployment_config.version,
                    thresholds={
                        "error_rate": config.thresholds.error_rate,
                        "latency_p99_ms": config.thresholds.latency_p99_ms,
                        "cpu_percent": config.thresholds.cpu_percent,
                        "memory_percent": config.thresholds.memory_percent
                    }
                )

                if not quick_check["healthy"]:
                    print(f"   Health check failed at {percentage}%")
                    if config.auto_rollback_enabled:
                        rollback_result = await self.rollback(
                            deployment_config,
                            f"Unhealthy at {percentage}% traffic"
                        )
                        return {
                            "deployment_id": deployment_id,
                            "status": "failed",
                            "reason": f"Health check failed at {percentage}%",
                            "rollback": rollback_result
                        }

                print(f"   Traffic at {percentage}%")

            # Phase 4: Complete deployment
            self._update_phase(DeploymentPhase.COMPLETING)
            await self._complete_deployment(deployment_config)

            self._update_phase(DeploymentPhase.COMPLETED)
            print(f"   Deployment completed successfully")

            # Record success in memory (if available)
            if self.memory:
                await self._record_deployment_success(deployment_id, deployment_config)

            return {
                "deployment_id": deployment_id,
                "status": "success",
                "version": deployment_config.version,
                "duration_seconds": self._get_deployment_duration()
            }

        except Exception as e:
            print(f"   Deployment exception: {str(e)}")
            if config.auto_rollback_enabled:
                rollback_result = await self.rollback(
                    deployment_config,
                    f"Exception: {str(e)}"
                )
                return {
                    "deployment_id": deployment_id,
                    "status": "failed",
                    "reason": str(e),
                    "rollback": rollback_result
                }
            else:
                return {
                    "deployment_id": deployment_id,
                    "status": "failed",
                    "reason": str(e)
                }

    async def validate_canary(
        self,
        deployment_config: DeploymentConfig,
        duration_seconds: int
    ) -> Dict:
        """
        Validate canary deployment health.

        TODO: Exercise 1 - Implement this method

        This method should:
        1. Collect health metrics over the validation period
        2. Check metrics against thresholds
        3. Query DevMemory for past issues with this service
        4. Adjust thresholds based on history (memory-informed decision)
        5. Return validation result with detailed reasoning

        Args:
            deployment_config: Deployment configuration
            duration_seconds: How long to validate

        Returns:
            Dictionary with:
            - healthy: bool
            - reason: str (why healthy or unhealthy)
            - issues: List[Dict] (threshold violations)
            - samples: List[Dict] (metrics samples)
            - duration: int (actual validation time)

        Hints for Exercise 1:
        - Use self.memory.recall(query=..., n_results=5) to check past issues.
          It returns a dict: {"episodic": [...], "semantic": [...], ...}, so read
          the "episodic" list rather than iterating the dict itself. Guard the
          call with `if self.memory:` first; memory is optional and the
          deployer must still validate without it.
        - Baseline thresholds are on the global `config`, not on
          deployment_config: config.thresholds.error_rate, .latency_p99_ms,
          .cpu_percent, .memory_percent.
        - Build a plain dict with the keys HealthMonitor expects: "error_rate",
          "latency_p99_ms", "cpu_percent", "memory_percent".
        - Tighten those thresholds when memory shows a failure history for this
          service. That is the memory-informed part of the exercise.
        - Then call:
              await self.health_monitor.monitor_continuously(
                  service_name=..., version=...,
                  duration_seconds=..., thresholds=...
              )
          It returns {"samples": [...], "issues": [...], "summary": {...},
          "duration_seconds": int, "healthy": bool}. Note it is a coroutine that
          returns a dict, not an async generator: await it, do not `async for`
          over it.
        """
        # TODO: Your implementation here
        print("TODO: Implement validate_canary() in Exercise 1")

        # Temporary placeholder - remove this when implementing
        await asyncio.sleep(2)  # Simulate validation
        return {
            "healthy": True,
            "reason": "Placeholder - implement in Exercise 1",
            "issues": [],
            "samples": [],
            "duration": duration_seconds
        }

    async def rollback(
        self,
        deployment_config: DeploymentConfig,
        reason: str
    ) -> Dict:
        """
        Rollback to previous stable version.

        TODO: Exercise 2 - Implement this method

        This method should:
        1. Identify the current stable version
        2. Shift 100% traffic back to stable version
        3. Remove the failing deployment
        4. Verify rollback succeeded
        5. Record rollback event in DevMemory
        6. Handle rollback failures (escalation)

        Args:
            deployment_config: The failing deployment config
            reason: Why we're rolling back

        Returns:
            Dictionary with:
            - success: bool
            - stable_version: str (version rolled back to)
            - duration_seconds: int
            - final_health: Dict (health after rollback)

        Hints for Exercise 2:
        - Use self.infra.list_deployments() to find stable version
        - Use self.infra.set_traffic() to shift traffic
        - Use self.infra.remove_deployment() to clean up
        - Use self.health_monitor.collect_metrics() to verify the version you
          rolled back TO
        - Use self.memory.remember_session() to record (guard with
          `if self.memory:`, memory is optional)
        - Handle the case where rollback itself fails
        """
        # TODO: Your implementation here
        print(f"TODO: Implement rollback() in Exercise 2")
        print(f"   Reason: {reason}")

        # Temporary placeholder - remove this when implementing
        await asyncio.sleep(1)
        return {
            "success": True,
            "stable_version": "1.0.0",
            "reason": "Placeholder - implement in Exercise 2"
        }

    # -------------------------------------------------------------------------
    # Helper Methods (READY-TO-USE)
    # -------------------------------------------------------------------------

    async def _deploy_canary(self, deployment_config: DeploymentConfig) -> Dict:
        """Deploy canary version."""
        canary_config = {
            "name": f"{deployment_config.service_name}-canary",
            "image": deployment_config.image,
            "replicas": max(1, deployment_config.replicas // 10),
            "labels": {
                "version": deployment_config.version,
                "canary": "true"
            }
        }

        result = await self.infra.create_deployment(canary_config)

        # Set canary traffic percentage
        await self.infra.set_traffic(
            deployment_config.service_name,
            deployment_config.version,
            deployment_config.canary_percentage
        )

        return {
            "success": result.get("status") == "ready",
            "details": result
        }

    async def _complete_deployment(self, deployment_config: DeploymentConfig):
        """Complete deployment by cleaning up old versions."""
        # In production, this would remove old versions
        # For lab, we just mark as complete
        await asyncio.sleep(0.5)

    def _update_phase(self, phase: DeploymentPhase):
        """Update current deployment phase."""
        self.current_phase = phase
        print(f"   Phase: {phase.value}")

    def _generate_deployment_id(self, deployment_config: DeploymentConfig) -> str:
        """Generate unique deployment ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{deployment_config.service_name}-{deployment_config.version}-{timestamp}"

    def _get_deployment_duration(self) -> int:
        """Get deployment duration in seconds."""
        # This would track actual start time in production
        return 0

    async def _handle_deployment_failure(
        self,
        deployment_id: str,
        deployment_config: DeploymentConfig,
        reason: str
    ) -> Dict:
        """Handle deployment failure."""
        self._update_phase(DeploymentPhase.FAILED)

        if self.memory:
            await self.memory.remember_session(
                session_type="deployment",
                summary=f"Deployment failed: {deployment_config.service_name} v{deployment_config.version}",
                details=reason,
                outcome="failure",
                project=deployment_config.service_name
            )

        return {
            "deployment_id": deployment_id,
            "status": "failed",
            "reason": reason
        }

    async def _record_deployment_success(
        self,
        deployment_id: str,
        deployment_config: DeploymentConfig
    ):
        """Record successful deployment in memory."""
        if self.memory:
            await self.memory.remember_session(
                session_type="deployment",
                summary=f"Deployed {deployment_config.service_name} v{deployment_config.version}",
                details=f"Zero-downtime deployment completed successfully",
                outcome="success",
                project=deployment_config.service_name
            )
