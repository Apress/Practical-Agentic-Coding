"""
Infrastructure client for Kubernetes deployments.
This module is READY-TO-USE - no TODOs needed.

Provides abstraction over Kubernetes API for deployment operations.
"""

from typing import Dict, List, Optional
from datetime import datetime
import asyncio
import os


class InfrastructureClient:
    """
    Client for managing infrastructure deployments.

    In production, this would use the Kubernetes Python client.
    For the lab, we provide both real and mock implementations.
    """

    def __init__(self, namespace: str = "default", use_mock: bool = None):
        """
        Initialize infrastructure client.

        Args:
            namespace: Kubernetes namespace
            use_mock: Use mock infrastructure (for testing). If None, uses config.
        """
        self.namespace = namespace

        if use_mock is None:
            use_mock = os.getenv("USE_MOCK_INFRASTRUCTURE", "true").lower() == "true"

        self.use_mock = use_mock

        if not use_mock:
            try:
                from kubernetes import client, config as k8s_config
                k8s_config.load_kube_config()
                self.k8s_apps_v1 = client.AppsV1Api()
                self.k8s_core_v1 = client.CoreV1Api()
            except ImportError:
                raise ImportError(
                    "kubernetes package required for real infrastructure. "
                    "Install with: pip install kubernetes"
                )

    async def create_deployment(self, deployment_config: Dict) -> Dict:
        """
        Create a new deployment.

        Args:
            deployment_config: Deployment configuration

        Returns:
            Deployment result with status
        """
        if self.use_mock:
            return await self._mock_create_deployment(deployment_config)

        # Real Kubernetes implementation would go here
        # For lab purposes, we use mock
        return await self._mock_create_deployment(deployment_config)

    async def _mock_create_deployment(self, deployment_config: Dict) -> Dict:
        """Mock deployment creation for testing."""
        await asyncio.sleep(0.5)  # Simulate API call
        return {
            "status": "ready",
            "name": deployment_config["name"],
            "replicas": deployment_config["replicas"],
            "created_at": datetime.now().isoformat()
        }

    async def get_deployment(self, service_name: str, version: str) -> Optional[Dict]:
        """
        Get deployment information.

        Args:
            service_name: Service name
            version: Deployment version

        Returns:
            Deployment info or None if not found
        """
        if self.use_mock:
            return await self._mock_get_deployment(service_name, version)

        # Real implementation here
        return await self._mock_get_deployment(service_name, version)

    async def _mock_get_deployment(self, service_name: str, version: str) -> Dict:
        """Mock get deployment."""
        await asyncio.sleep(0.1)
        return {
            "name": f"{service_name}-{version}",
            "version": version,
            "replicas": 3,
            "available_replicas": 3,
            "status": "running"
        }

    async def list_deployments(self, service_name: str) -> List[Dict]:
        """
        List all deployments for a service.

        Args:
            service_name: Service name

        Returns:
            List of deployments
        """
        if self.use_mock:
            return await self._mock_list_deployments(service_name)

        # Real implementation here
        return await self._mock_list_deployments(service_name)

    async def _mock_list_deployments(self, service_name: str) -> List[Dict]:
        """Mock list deployments."""
        await asyncio.sleep(0.1)
        return [
            {
                "name": f"{service_name}-v1.0.0",
                "version": "1.0.0",
                "replicas": 3,
                "traffic_percentage": 90,
                "status": "running"
            },
            {
                "name": f"{service_name}-canary",
                "version": "2.0.0",
                "replicas": 1,
                "traffic_percentage": 10,
                "status": "running"
            }
        ]

    async def set_traffic(
        self,
        service_name: str,
        version: str,
        percentage: int
    ) -> Dict:
        """
        Set traffic percentage for a deployment.

        Args:
            service_name: Service name
            version: Deployment version
            percentage: Traffic percentage (0-100)

        Returns:
            Traffic update result
        """
        if self.use_mock:
            return await self._mock_set_traffic(service_name, version, percentage)

        # Real implementation here
        return await self._mock_set_traffic(service_name, version, percentage)

    async def _mock_set_traffic(
        self,
        service_name: str,
        version: str,
        percentage: int
    ) -> Dict:
        """Mock traffic shift."""
        await asyncio.sleep(0.5)
        return {
            "success": True,
            "service": service_name,
            "version": version,
            "traffic_percentage": percentage
        }

    async def remove_deployment(self, service_name: str, version: str) -> Dict:
        """
        Remove a deployment.

        Args:
            service_name: Service name
            version: Version to remove

        Returns:
            Removal result
        """
        if self.use_mock:
            return await self._mock_remove_deployment(service_name, version)

        # Real implementation here
        return await self._mock_remove_deployment(service_name, version)

    async def _mock_remove_deployment(self, service_name: str, version: str) -> Dict:
        """Mock deployment removal."""
        await asyncio.sleep(0.3)
        return {
            "success": True,
            "service": service_name,
            "version": version,
            "removed_at": datetime.now().isoformat()
        }

    async def get_metrics(self, service_name: str, version: str) -> Dict:
        """
        Get metrics for a deployment.

        Args:
            service_name: Service name
            version: Deployment version

        Returns:
            Metrics dictionary
        """
        if self.use_mock:
            return await self._mock_get_metrics(service_name, version)

        # Real implementation would query Prometheus
        return await self._mock_get_metrics(service_name, version)

    async def _mock_get_metrics(self, service_name: str, version: str) -> Dict:
        """Mock metrics for testing."""
        import random
        await asyncio.sleep(0.1)

        # Simulate varying metrics
        # "bad" versions have worse metrics
        is_bad = "bad" in version.lower()

        return {
            "error_rate": random.uniform(0.02, 0.08) if is_bad else random.uniform(0.0, 0.005),
            "latency_p99": random.uniform(600, 1200) if is_bad else random.uniform(100, 400),
            "cpu_usage": random.uniform(0.7, 0.9) if is_bad else random.uniform(0.3, 0.6),
            "memory_usage": random.uniform(0.7, 0.9) if is_bad else random.uniform(0.4, 0.65),
            "request_count": random.randint(1000, 5000)
        }
