"""
Zero-Downtime Deployer - Reference Solution

Complete implementation of the canary deployment, rollback, and
memory-informed deployment agent from Chapter 11, Section 11.6.
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

            # Phase 2: Validate canary
            self._update_phase(DeploymentPhase.VALIDATING_CANARY)
            validation_result = await self.validate_canary(
                deployment_config,
                deployment_config.validation_duration_seconds
            )

            if not validation_result["healthy"]:
                print(f"   Canary validation failed: {validation_result['reason']}")
                # Automatic rollback on validation failure
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

            # Report the window validate_canary actually used, which may be
            # longer than the requested one if memory extended it.
            validated_for = validation_result.get(
                "validation_window_seconds",
                deployment_config.validation_duration_seconds
            )
            print(f"   Canary validated (healthy for {validated_for}s)")

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

        Collect metrics over the validation window, check them against
        thresholds, and adapt both the thresholds and the window itself when
        memory says this service has a history of trouble (the book's
        Section 11.6 listing: a leak-prone service gets a 60s -> 180s canary).
        """
        # Step 1: Check memory for past issues with this service.
        # Memory is optional: without it the deployer still validates, it
        # just cannot adapt its thresholds to history.
        past_issues = []
        if self.memory:
            recalled = await self.memory.recall(
                query=f"deployment failure {deployment_config.service_name}",
                n_results=5
            )
            # recall() returns {"episodic": [...], "semantic": [...], ...}
            past_issues = recalled.get("episodic", []) if recalled else []

        # Step 2: Adjust thresholds based on history. Baseline thresholds live
        # on the global config, loaded from .env, not on the per-deployment
        # config. Keys match what HealthMonitor.check_health expects.
        thresholds = {
            "error_rate": config.thresholds.error_rate,
            "latency_p99_ms": config.thresholds.latency_p99_ms,
            "cpu_percent": config.thresholds.cpu_percent,
            "memory_percent": config.thresholds.memory_percent,
        }
        if any("memory leak" in str(issue) for issue in past_issues):
            # A leak-prone service gets half the usual error budget, so a slow
            # degradation trips the gate instead of sliding through...
            thresholds["error_rate"] = thresholds["error_rate"] * 0.5
            # ...and a canary window three times longer (the book's 60s -> 180s
            # adjustment), because slow-onset issues like leaks will not
            # surface inside the default window.
            duration_seconds = duration_seconds * 3
            print(
                "   Memory: past memory-leak incident, tightening error "
                f"budget and extending canary validation to {duration_seconds}s"
            )

        # Step 3: Collect health metrics over the validation period
        monitoring = await self.health_monitor.monitor_continuously(
            service_name=deployment_config.service_name,
            version=deployment_config.version,
            duration_seconds=duration_seconds,
            thresholds=thresholds,
        )

        issues = monitoring["issues"]
        healthy = len(issues) == 0
        reason = "All metrics within thresholds" if healthy else (
            f"{len(issues)} threshold violations detected: "
            + ", ".join(sorted({issue["type"] for issue in issues}))
        )

        return {
            "healthy": healthy,
            "reason": reason,
            "issues": issues,
            "samples": monitoring["samples"],
            "summary": monitoring["summary"],
            "thresholds": thresholds,
            "duration": monitoring["duration_seconds"],
            # The window actually used, after any history-based extension,
            # so the deployment record explains the decision later.
            "validation_window_seconds": duration_seconds,
        }

    async def rollback(
        self,
        deployment_config: DeploymentConfig,
        reason: str
    ) -> Dict:
        """
        Rollback to previous stable version with memory recording.

        Follows the five-step flow from exercises/exercise-2-rollback.md:
        find the stable version, shift traffic back, remove the failing
        deployment, verify health, record the event.
        """
        self._update_phase(DeploymentPhase.ROLLING_BACK)
        print(f"   Initiating rollback: {reason}")
        rollback_start = datetime.now()

        try:
            # Step 1: Find the stable version: the deployment currently
            # serving the most traffic that is not the version being
            # rolled back.
            deployments = await self.infra.list_deployments(
                deployment_config.service_name
            )
            candidates = [
                d for d in deployments
                if d.get("version") != deployment_config.version
            ]
            if not candidates:
                await self._escalate_rollback_failure(
                    deployment_config,
                    "No stable version found to rollback to"
                )
                return {
                    "success": False,
                    "stable_version": None,
                    "reason": "No stable version found to rollback to"
                }

            stable = max(
                candidates, key=lambda d: d.get("traffic_percentage", 0)
            )
            stable_version = stable["version"]
            print(f"   Rolling back to stable version: {stable_version}")

            # Step 2: Shift all traffic to the stable version. This is the
            # critical operation: it immediately stops routing users to the
            # failing version.
            traffic_result = await self.infra.set_traffic(
                deployment_config.service_name,
                stable_version,
                percentage=100
            )
            if not traffic_result["success"]:
                await self._escalate_rollback_failure(
                    deployment_config,
                    "Traffic shift to stable version failed"
                )
                return {
                    "success": False,
                    "stable_version": stable_version,
                    "reason": "Traffic shift to stable version failed"
                }

            # Step 3: Remove the failing deployment. Traffic is already off
            # it, so a failure here is a cleanup problem, not an outage.
            remove_result = await self.infra.remove_deployment(
                deployment_config.service_name,
                deployment_config.version
            )
            if not remove_result.get("success"):
                print(
                    "   Warning: failing deployment not removed; "
                    "clean it up manually"
                )

            # Step 4: Verify rollback health on the version we rolled back TO
            if self.traffic_stabilization_seconds > 0:
                await asyncio.sleep(self.traffic_stabilization_seconds)
            final_health = await self.health_monitor.collect_metrics(
                deployment_config.service_name,
                stable_version
            )
            is_healthy = (
                final_health["error_rate"] < config.thresholds.error_rate
                and final_health["latency_p99"] < config.thresholds.latency_p99_ms
            )
            if not is_healthy:
                # Rolling back did not fix it, so the problem is bigger than
                # the new version. A human needs to look.
                await self._escalate_rollback_failure(
                    deployment_config,
                    f"Service still unhealthy after rollback: {final_health}"
                )

            # Step 5: Record in memory so future deployments learn from this
            duration_seconds = int(
                (datetime.now() - rollback_start).total_seconds()
            )
            if self.memory:
                await self.memory.remember_session(
                    session_type="rollback",
                    summary=(
                        f"Rolled back {deployment_config.service_name} "
                        f"from v{deployment_config.version} "
                        f"to v{stable_version}"
                    ),
                    details=f"Reason: {reason}. Duration: {duration_seconds}s",
                    outcome="success" if is_healthy else "partial",
                    project=deployment_config.service_name,
                    metadata={
                        "failed_version": deployment_config.version,
                        "stable_version": stable_version,
                        "reason": reason,
                        "duration_seconds": duration_seconds,
                        "final_health": final_health
                    }
                )

            print(f"   Rollback completed in {duration_seconds}s")
            return {
                "success": True,
                "stable_version": stable_version,
                "duration_seconds": duration_seconds,
                "final_health": final_health
            }

        except Exception as e:
            # Rollback itself failed: escalate, never swallow
            await self._escalate_rollback_failure(
                deployment_config,
                f"Rollback exception: {e}"
            )
            return {
                "success": False,
                "stable_version": None,
                "reason": f"Rollback failed: {e}"
            }

    async def _escalate_rollback_failure(
        self,
        deployment_config: DeploymentConfig,
        reason: str
    ):
        """Record a critical rollback failure and alert a human."""
        print(
            f"CRITICAL: Rollback problem for "
            f"{deployment_config.service_name}: {reason}"
        )
        print("CRITICAL: Human intervention required")

        if self.memory:
            await self.memory.remember_session(
                session_type="incident",
                summary=(
                    f"CRITICAL: Rollback problem for "
                    f"{deployment_config.service_name}"
                ),
                details=reason,
                outcome="critical_failure",
                project=deployment_config.service_name,
                metadata={"severity": "critical", "requires_human": True}
            )
        # In production this would page the on-call engineer and open a
        # high-priority incident. The lab records the incident and prints.

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
