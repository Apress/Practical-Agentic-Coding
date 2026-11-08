"""
Health monitoring for deployments.
This module is READY-TO-USE - no TODOs needed.

Provides health checking and metrics collection for deployed services.
"""

from typing import Dict
from datetime import datetime
import asyncio


class HealthMonitor:
    """
    Monitors health of deployed services.

    Collects metrics and performs health checks.
    """

    def __init__(self, infrastructure_client=None):
        """
        Initialize health monitor.

        Args:
            infrastructure_client: Infrastructure client for metrics
        """
        self.infra = infrastructure_client

    async def collect_metrics(
        self,
        service_name: str,
        version: str
    ) -> Dict:
        """
        Collect metrics for a service version.

        Args:
            service_name: Service name
            version: Service version

        Returns:
            Dictionary of metrics:
            - error_rate: Float (0.0-1.0)
            - latency_p99: Float (milliseconds)
            - cpu_usage: Float (0.0-1.0)
            - memory_usage: Float (0.0-1.0)
            - request_count: Int
        """
        if self.infra:
            return await self.infra.get_metrics(service_name, version)

        # Fallback: query Prometheus directly
        return await self._query_prometheus(service_name, version)

    async def _query_prometheus(
        self,
        service_name: str,
        version: str
    ) -> Dict:
        """Query Prometheus for metrics."""
        # This would use prometheus_client in production
        # For lab, we simulate metrics
        import random
        await asyncio.sleep(0.1)

        return {
            "error_rate": random.uniform(0.0, 0.01),
            "latency_p99": random.uniform(200, 400),
            "cpu_usage": random.uniform(0.4, 0.7),
            "memory_usage": random.uniform(0.5, 0.75),
            "request_count": random.randint(1000, 3000),
            "timestamp": datetime.now().isoformat()
        }

    async def check_health(
        self,
        service_name: str,
        version: str,
        thresholds: Dict
    ) -> Dict:
        """
        Check if service is healthy based on thresholds.

        Args:
            service_name: Service name
            version: Service version
            thresholds: Dictionary of threshold values

        Returns:
            Health check result with issues list
        """
        metrics = await self.collect_metrics(service_name, version)
        issues = []

        # Check error rate
        if metrics["error_rate"] > thresholds.get("error_rate", 0.01):
            issues.append({
                "type": "error_rate",
                "value": metrics["error_rate"],
                "threshold": thresholds["error_rate"],
                "message": f"Error rate {metrics['error_rate']:.2%} exceeds threshold"
            })

        # Check latency
        if metrics["latency_p99"] > thresholds.get("latency_p99_ms", 500):
            issues.append({
                "type": "latency",
                "value": metrics["latency_p99"],
                "threshold": thresholds["latency_p99_ms"],
                "message": f"P99 latency {metrics['latency_p99']:.0f}ms exceeds threshold"
            })

        # Check CPU
        if metrics["cpu_usage"] > thresholds.get("cpu_percent", 0.8):
            issues.append({
                "type": "cpu",
                "value": metrics["cpu_usage"],
                "threshold": thresholds["cpu_percent"],
                "message": f"CPU usage {metrics['cpu_usage']:.0%} exceeds threshold"
            })

        # Check memory
        if metrics["memory_usage"] > thresholds.get("memory_percent", 0.8):
            issues.append({
                "type": "memory",
                "value": metrics["memory_usage"],
                "threshold": thresholds["memory_percent"],
                "message": f"Memory usage {metrics['memory_usage']:.0%} exceeds threshold"
            })

        return {
            "healthy": len(issues) == 0,
            "metrics": metrics,
            "issues": issues,
            "checked_at": datetime.now().isoformat()
        }

    async def monitor_continuously(
        self,
        service_name: str,
        version: str,
        duration_seconds: int,
        thresholds: Dict,
        sample_interval: int = 10
    ) -> Dict:
        """
        Monitor service health continuously over a period.

        Args:
            service_name: Service name
            version: Service version
            duration_seconds: How long to monitor
            thresholds: Health check thresholds
            sample_interval: Seconds between samples

        Returns:
            Monitoring result with all samples and issues
        """
        start_time = datetime.now()
        samples = []
        all_issues = []

        elapsed = 0
        while elapsed < duration_seconds:
            # Collect sample
            health_check = await self.check_health(service_name, version, thresholds)
            samples.append({
                "timestamp": datetime.now().isoformat(),
                "elapsed_seconds": elapsed,
                "metrics": health_check["metrics"],
                "healthy": health_check["healthy"]
            })

            # Track issues
            if health_check["issues"]:
                all_issues.extend(health_check["issues"])

            # Wait for next sample
            await asyncio.sleep(sample_interval)
            elapsed = (datetime.now() - start_time).seconds

        # Calculate summary statistics
        error_rates = [s["metrics"]["error_rate"] for s in samples]
        latencies = [s["metrics"]["latency_p99"] for s in samples]

        return {
            "service": service_name,
            "version": version,
            "duration_seconds": elapsed,
            "samples_count": len(samples),
            "samples": samples,
            "issues": all_issues,
            "healthy": len(all_issues) == 0,
            "summary": {
                "avg_error_rate": sum(error_rates) / len(error_rates),
                "max_error_rate": max(error_rates),
                "avg_latency_p99": sum(latencies) / len(latencies),
                "max_latency_p99": max(latencies)
            }
        }
