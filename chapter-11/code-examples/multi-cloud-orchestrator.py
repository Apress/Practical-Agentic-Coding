"""
Module: Multi-Cloud Orchestration Agent
Concept: Cross-cloud deployment coordination and failover management
Chapter Reference: Bonus example (extends Section 11.7 challenge lab multi-service patterns)

This example demonstrates how AI agents can orchestrate deployments across
multiple cloud providers, manage provider abstraction, and implement
intelligent failover strategies.

Key Patterns Demonstrated:
- Cloud provider abstraction layer
- Cross-cloud deployment coordination
- Health monitoring across providers
- Intelligent failover decisions
- Cost-aware provider selection
- Multi-region deployment strategies
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import random


class CloudProvider(Enum):
    """Supported cloud providers."""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"


class DeploymentStatus(Enum):
    """Deployment status across clouds."""
    PENDING = "pending"
    DEPLOYING = "deploying"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    FAILED_OVER = "failed_over"


class HealthStatus(Enum):
    """Health check status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class FailoverTrigger(Enum):
    """What triggered a failover."""
    HEALTH_CHECK = "health_check"
    PERFORMANCE = "performance"
    COST = "cost"
    MANUAL = "manual"
    PROVIDER_OUTAGE = "provider_outage"


@dataclass
class CloudRegion:
    """Represents a cloud region."""
    provider: CloudProvider
    region_name: str
    cost_multiplier: float  # Relative cost (1.0 = baseline)
    latency_ms: float  # Average latency
    available: bool = True


@dataclass
class DeploymentTarget:
    """A deployment target in a specific cloud/region."""
    provider: CloudProvider
    region: str
    instance_count: int
    health_status: HealthStatus = HealthStatus.UNKNOWN
    deployment_status: DeploymentStatus = DeploymentStatus.PENDING
    endpoint_url: str = ""
    cost_per_hour: float = 0.0
    response_time_ms: float = 0.0
    error_rate: float = 0.0
    last_health_check: Optional[datetime] = None


@dataclass
class FailoverEvent:
    """Record of a failover event."""
    timestamp: datetime
    trigger: FailoverTrigger
    source_provider: CloudProvider
    source_region: str
    target_provider: CloudProvider
    target_region: str
    reason: str
    success: bool


@dataclass
class DeploymentStrategy:
    """Multi-cloud deployment strategy configuration."""
    primary_provider: CloudProvider
    primary_region: str
    enable_failover: bool = True
    enable_multi_region: bool = True
    enable_cost_optimization: bool = True
    max_providers: int = 2
    target_availability: float = 0.999  # 99.9% SLA


class CloudProviderAdapter:
    """
    Abstract adapter for cloud provider operations.

    This demonstrates the adapter pattern for multi-cloud abstraction.
    """

    def __init__(self, provider: CloudProvider):
        """Initialize cloud provider adapter."""
        self.provider = provider

    def deploy_application(
        self,
        app_name: str,
        region: str,
        instance_count: int
    ) -> DeploymentTarget:
        """
        Deploy application to this cloud provider.

        Args:
            app_name: Application name
            region: Target region
            instance_count: Number of instances

        Returns:
            Deployment target information
        """
        # Simulate provider-specific deployment
        print(f"   Deploying to {self.provider.value.upper()} ({region})")
        print(f"      Instances: {instance_count}")

        # Calculate cost based on provider pricing
        base_cost = 0.10  # $0.10/hour per instance
        provider_multipliers = {
            CloudProvider.AWS: 1.0,
            CloudProvider.AZURE: 0.95,
            CloudProvider.GCP: 0.90
        }

        cost = base_cost * instance_count * provider_multipliers[self.provider]

        return DeploymentTarget(
            provider=self.provider,
            region=region,
            instance_count=instance_count,
            deployment_status=DeploymentStatus.DEPLOYING,
            endpoint_url=f"https://{app_name}.{region}.{self.provider.value}.example.com",
            cost_per_hour=cost
        )

    def health_check(self, target: DeploymentTarget) -> HealthStatus:
        """
        Perform health check on deployment.

        Args:
            target: Deployment target to check

        Returns:
            Health status
        """
        # Simulate health check with random results
        rand = random.random()

        if rand > 0.9:
            return HealthStatus.UNHEALTHY
        elif rand > 0.8:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY

    def get_metrics(self, target: DeploymentTarget) -> Dict[str, float]:
        """
        Get performance metrics from deployment.

        Args:
            target: Deployment target

        Returns:
            Dictionary of metrics
        """
        # Simulate metrics
        return {
            "response_time_ms": random.uniform(50, 200),
            "error_rate": random.uniform(0, 0.05),
            "cpu_utilization": random.uniform(0.2, 0.8),
            "requests_per_second": random.uniform(100, 1000)
        }

    def scale_deployment(self, target: DeploymentTarget, new_count: int) -> bool:
        """
        Scale deployment to new instance count.

        Args:
            target: Deployment target
            new_count: New instance count

        Returns:
            True if scaling successful
        """
        print(f"   Scaling {self.provider.value} from {target.instance_count} to {new_count} instances")
        target.instance_count = new_count
        return True

    def terminate_deployment(self, target: DeploymentTarget) -> bool:
        """
        Terminate deployment.

        Args:
            target: Deployment target to terminate

        Returns:
            True if termination successful
        """
        print(f"   Terminating deployment on {self.provider.value} ({target.region})")
        target.deployment_status = DeploymentStatus.FAILED
        return True


class MultiCloudOrchestrator:
    """
    Multi-Cloud Orchestration Agent.

    Demonstrates intelligent multi-cloud management including:
    - Cross-cloud deployment coordination
    - Health monitoring and failover
    - Cost-aware provider selection
    - Performance-based routing
    """

    def __init__(self, app_name: str, strategy: DeploymentStrategy):
        """
        Initialize multi-cloud orchestrator.

        Args:
            app_name: Application name
            strategy: Deployment strategy configuration
        """
        self.app_name = app_name
        self.strategy = strategy
        self.deployments: List[DeploymentTarget] = []
        self.failover_history: List[FailoverEvent] = []

        # Initialize cloud provider adapters
        self.providers = {
            CloudProvider.AWS: CloudProviderAdapter(CloudProvider.AWS),
            CloudProvider.AZURE: CloudProviderAdapter(CloudProvider.AZURE),
            CloudProvider.GCP: CloudProviderAdapter(CloudProvider.GCP)
        }

        # Available regions per provider
        self.available_regions = {
            CloudProvider.AWS: ["us-east-1", "us-west-2", "eu-west-1"],
            CloudProvider.AZURE: ["eastus", "westus", "westeurope"],
            CloudProvider.GCP: ["us-central1", "us-west1", "europe-west1"]
        }

    def deploy_multi_cloud(self, instance_count: int = 3) -> List[DeploymentTarget]:
        """
        Deploy application across multiple clouds.

        Args:
            instance_count: Total instance count to distribute

        Returns:
            List of deployment targets
        """
        print(f"\nMulti-Cloud Deployment: {self.app_name}")
        print(f"   Strategy: {self.strategy.primary_provider.value} primary")
        print(f"   Failover: {'Enabled' if self.strategy.enable_failover else 'Disabled'}")
        print(f"   Multi-Region: {'Enabled' if self.strategy.enable_multi_region else 'Disabled'}\n")

        # Deploy to primary provider
        primary_deployment = self._deploy_to_provider(
            self.strategy.primary_provider,
            self.strategy.primary_region,
            instance_count
        )
        self.deployments.append(primary_deployment)

        # Deploy to secondary providers for redundancy
        if self.strategy.enable_failover:
            secondary_providers = self._select_secondary_providers()

            for provider, region in secondary_providers:
                # Deploy with fewer instances (standby)
                standby_count = max(1, instance_count // 2)
                secondary_deployment = self._deploy_to_provider(
                    provider,
                    region,
                    standby_count
                )
                self.deployments.append(secondary_deployment)

        print(f"\nDeployed to {len(self.deployments)} locations")
        return self.deployments

    def _deploy_to_provider(
        self,
        provider: CloudProvider,
        region: str,
        instance_count: int
    ) -> DeploymentTarget:
        """Deploy to a specific provider and region."""
        adapter = self.providers[provider]
        target = adapter.deploy_application(self.app_name, region, instance_count)

        # Simulate deployment completing
        target.deployment_status = DeploymentStatus.HEALTHY
        target.health_status = HealthStatus.HEALTHY
        target.last_health_check = datetime.now()

        print(f"      Deployment complete: {target.endpoint_url}")
        return target

    def _select_secondary_providers(self) -> List[tuple[CloudProvider, str]]:
        """
        Select secondary providers for failover.

        Returns:
            List of (provider, region) tuples
        """
        secondary = []
        used_providers = {self.strategy.primary_provider}

        # Select different providers for redundancy
        for provider in CloudProvider:
            if provider not in used_providers and len(secondary) < (self.strategy.max_providers - 1):
                regions = self.available_regions[provider]
                # Select region with best cost/performance
                selected_region = regions[0]  # Simplified selection
                secondary.append((provider, selected_region))
                used_providers.add(provider)

        return secondary

    def monitor_health(self) -> Dict[str, any]:
        """
        Monitor health of all deployments.

        Returns:
            Health monitoring report
        """
        print(f"\nHealth Check: {self.app_name}")

        healthy_count = 0
        degraded_count = 0
        unhealthy_count = 0

        for deployment in self.deployments:
            adapter = self.providers[deployment.provider]

            # Perform health check
            health = adapter.health_check(deployment)
            deployment.health_status = health
            deployment.last_health_check = datetime.now()

            # Get metrics
            metrics = adapter.get_metrics(deployment)
            deployment.response_time_ms = metrics["response_time_ms"]
            deployment.error_rate = metrics["error_rate"]

            # Count health statuses
            if health == HealthStatus.HEALTHY:
                healthy_count += 1
                status_icon = "[OK]  "
            elif health == HealthStatus.DEGRADED:
                degraded_count += 1
                status_icon = "[WARN]"
            else:
                unhealthy_count += 1
                status_icon = "[FAIL]"

            print(f"   {status_icon} {deployment.provider.value}/{deployment.region}: "
                  f"{health.value} (RT: {deployment.response_time_ms:.0f}ms, "
                  f"Errors: {deployment.error_rate:.1%})")

        return {
            "total_deployments": len(self.deployments),
            "healthy": healthy_count,
            "degraded": degraded_count,
            "unhealthy": unhealthy_count,
            "overall_health": self._calculate_overall_health(
                healthy_count, degraded_count, unhealthy_count
            )
        }

    def _calculate_overall_health(
        self,
        healthy: int,
        degraded: int,
        unhealthy: int
    ) -> HealthStatus:
        """Calculate overall health status."""
        total = healthy + degraded + unhealthy

        if total == 0:
            return HealthStatus.UNKNOWN

        health_ratio = healthy / total

        if health_ratio >= 0.8:
            return HealthStatus.HEALTHY
        elif health_ratio >= 0.5:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.UNHEALTHY

    def evaluate_failover_need(self) -> Optional[FailoverEvent]:
        """
        Evaluate if failover is needed based on health and performance.

        Returns:
            Failover event if failover should occur, None otherwise
        """
        if not self.strategy.enable_failover:
            return None

        # Find unhealthy primary deployment
        primary_deployments = [
            d for d in self.deployments
            if d.provider == self.strategy.primary_provider
        ]

        if not primary_deployments:
            return None

        primary = primary_deployments[0]

        # Check if failover needed
        if primary.health_status == HealthStatus.UNHEALTHY:
            trigger = FailoverTrigger.HEALTH_CHECK
            reason = "Primary deployment unhealthy"
        elif primary.error_rate > 0.10:  # >10% error rate
            trigger = FailoverTrigger.PERFORMANCE
            reason = f"High error rate: {primary.error_rate:.1%}"
        elif primary.response_time_ms > 500:  # >500ms response time
            trigger = FailoverTrigger.PERFORMANCE
            reason = f"High response time: {primary.response_time_ms:.0f}ms"
        else:
            return None  # No failover needed

        # Select best failover target
        failover_target = self._select_failover_target(primary)

        if failover_target:
            return FailoverEvent(
                timestamp=datetime.now(),
                trigger=trigger,
                source_provider=primary.provider,
                source_region=primary.region,
                target_provider=failover_target.provider,
                target_region=failover_target.region,
                reason=reason,
                success=False  # Will be updated after execution
            )

        return None

    def _select_failover_target(
        self,
        failed_deployment: DeploymentTarget
    ) -> Optional[DeploymentTarget]:
        """
        Select best failover target.

        Args:
            failed_deployment: The failed deployment

        Returns:
            Best failover target deployment
        """
        # Find healthy deployments in different providers
        candidates = [
            d for d in self.deployments
            if d.provider != failed_deployment.provider
            and d.health_status == HealthStatus.HEALTHY
        ]

        if not candidates:
            return None

        # Select best candidate based on performance and cost
        best_target = min(
            candidates,
            key=lambda d: (d.response_time_ms * 0.7 + d.cost_per_hour * 100 * 0.3)
        )

        return best_target

    def execute_failover(self, failover: FailoverEvent) -> bool:
        """
        Execute failover to secondary provider.

        Args:
            failover: Failover event to execute

        Returns:
            True if failover successful
        """
        print(f"\nEXECUTING FAILOVER")
        print(f"   Trigger: {failover.trigger.value}")
        print(f"   Reason: {failover.reason}")
        print(f"   From: {failover.source_provider.value}/{failover.source_region}")
        print(f"   To: {failover.target_provider.value}/{failover.target_region}")

        # Find source and target deployments
        source = next(
            (d for d in self.deployments
             if d.provider == failover.source_provider
             and d.region == failover.source_region),
            None
        )

        target = next(
            (d for d in self.deployments
             if d.provider == failover.target_provider
             and d.region == failover.target_region),
            None
        )

        if not source or not target:
            print("   Failover failed: invalid source or target")
            failover.success = False
            return False

        # Scale up target to handle traffic
        target_adapter = self.providers[target.provider]
        target_adapter.scale_deployment(target, source.instance_count)

        # Update deployment statuses
        source.deployment_status = DeploymentStatus.FAILED_OVER
        target.deployment_status = DeploymentStatus.HEALTHY

        print(f"   Failover completed successfully")
        print(f"   Traffic now routed to {target.provider.value}")

        failover.success = True
        self.failover_history.append(failover)

        return True

    def optimize_costs(self) -> Dict[str, any]:
        """
        Analyze and optimize multi-cloud costs.

        Returns:
            Cost optimization report
        """
        current_cost = sum(d.cost_per_hour for d in self.deployments)
        current_monthly = current_cost * 24 * 30

        print(f"\nCost Optimization Analysis")
        print(f"   Current hourly cost: ${current_cost:.2f}")
        print(f"   Projected monthly: ${current_monthly:.2f}\n")

        # Identify optimization opportunities
        optimizations = []

        for deployment in self.deployments:
            # Check for underutilized deployments
            if deployment.health_status == HealthStatus.HEALTHY:
                # Could move to cheaper provider
                cheaper_providers = [
                    p for p in CloudProvider
                    if p != deployment.provider
                ]

                for provider in cheaper_providers:
                    adapter = self.providers[provider]
                    # Estimate cost for alternative provider
                    alternative_cost = deployment.cost_per_hour * 0.9  # Assume 10% savings

                    if alternative_cost < deployment.cost_per_hour:
                        optimizations.append({
                            "current_provider": deployment.provider.value,
                            "target_provider": provider.value,
                            "current_cost": deployment.cost_per_hour,
                            "target_cost": alternative_cost,
                            "monthly_savings": (deployment.cost_per_hour - alternative_cost) * 24 * 30
                        })

        return {
            "current_hourly_cost": current_cost,
            "current_monthly_cost": current_monthly,
            "optimizations": optimizations[:3],  # Top 3
            "potential_monthly_savings": sum(o["monthly_savings"] for o in optimizations[:3])
        }

    def get_deployment_summary(self) -> str:
        """
        Generate deployment summary report.

        Returns:
            Formatted summary
        """
        total_instances = sum(d.instance_count for d in self.deployments)
        total_cost = sum(d.cost_per_hour for d in self.deployments)
        healthy = sum(1 for d in self.deployments if d.health_status == HealthStatus.HEALTHY)

        summary = f"""
╔═══════════════════════════════════════════════════════════════╗
║             MULTI-CLOUD DEPLOYMENT SUMMARY                    ║
╚═══════════════════════════════════════════════════════════════╝

Application: {self.app_name}
Deployment Locations: {len(self.deployments)}
Total Instances: {total_instances}
Healthy Deployments: {healthy}/{len(self.deployments)}

DEPLOYMENTS:
"""

        for deployment in self.deployments:
            summary += f"""
  {deployment.provider.value.upper()} - {deployment.region}
    Status: {deployment.deployment_status.value}
    Health: {deployment.health_status.value}
    Instances: {deployment.instance_count}
    Endpoint: {deployment.endpoint_url}
    Cost: ${deployment.cost_per_hour:.2f}/hour
"""

        if self.failover_history:
            summary += f"\nFAILOVER HISTORY:\n"
            for event in self.failover_history[-5:]:  # Last 5
                status = "[OK]  " if event.success else "[FAIL]"
                summary += f"  {status} {event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}: "
                summary += f"{event.source_provider.value} -> {event.target_provider.value}\n"

        summary += f"\nCOST SUMMARY:\n"
        summary += f"  Hourly: ${total_cost:.2f}\n"
        summary += f"  Monthly (projected): ${total_cost * 24 * 30:.2f}\n"

        return summary


if __name__ == "__main__":
    print("=== Multi-Cloud Orchestration Demo ===")

    # Configure deployment strategy
    strategy = DeploymentStrategy(
        primary_provider=CloudProvider.AWS,
        primary_region="us-east-1",
        enable_failover=True,
        enable_multi_region=True,
        enable_cost_optimization=True,
        max_providers=3
    )

    # Initialize orchestrator
    orchestrator = MultiCloudOrchestrator(
        app_name="global-web-service",
        strategy=strategy
    )

    # Deploy across multiple clouds
    print("\n" + "=" * 70)
    print("PHASE 1: Multi-Cloud Deployment")
    print("=" * 70)
    deployments = orchestrator.deploy_multi_cloud(instance_count=6)

    # Monitor health
    print("\n" + "=" * 70)
    print("PHASE 2: Health Monitoring")
    print("=" * 70)
    health_report = orchestrator.monitor_health()
    print(f"\nOverall Health: {health_report['overall_health'].value.upper()}")

    # Check for failover need
    print("\n" + "=" * 70)
    print("PHASE 3: Failover Evaluation")
    print("=" * 70)
    failover = orchestrator.evaluate_failover_need()

    if failover:
        orchestrator.execute_failover(failover)
    else:
        print("   All deployments healthy, no failover needed")

    # Cost optimization
    print("\n" + "=" * 70)
    print("PHASE 4: Cost Optimization")
    print("=" * 70)
    cost_report = orchestrator.optimize_costs()

    if cost_report["optimizations"]:
        print("\n   Optimization Opportunities:")
        for opt in cost_report["optimizations"]:
            print(f"   • Move from {opt['current_provider']} to {opt['target_provider']}")
            print(f"     Savings: ${opt['monthly_savings']:.2f}/month")

    # Final summary
    print("\n" + "=" * 70)
    print(orchestrator.get_deployment_summary())

    print("\nMulti-cloud orchestration demonstration complete.")
