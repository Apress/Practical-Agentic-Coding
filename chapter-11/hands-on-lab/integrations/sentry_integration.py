"""
Sentry Integration for Zero-Downtime Deployer

This module demonstrates integration points for Sentry error tracking.
Students complete the TODOs to implement full integration.

Exercise 3: Sentry Integration

Key Concepts:
- Initializing Sentry SDK with DSN from environment
- Reporting deployment events with context and tags
- Querying error rates for canary validation
- Correlating errors with deployments
- Reporting rollback events

Learning Objectives:
- Understand bi-directional observability integration
- Learn to propagate context through deployment lifecycle
- Practice production-grade error tracking patterns
"""

import sentry_sdk
from sentry_sdk import capture_message, capture_exception
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os


class SentryMonitor:
    """
    Monitor deployments with Sentry error tracking.

    This class provides integration between the Zero-Downtime Deployer
    and Sentry's error tracking platform.

    Responsibilities:
    - Initialize Sentry SDK with proper configuration
    - Report deployment lifecycle events
    - Query error rates during canary validation
    - Report rollback events with context
    - Correlate errors with specific deployments
    """

    def __init__(self):
        """
        Initialize Sentry SDK with configuration from environment.

        TODO Exercise 3, Part 1: Initialize Sentry SDK

        Steps:
        1. Get DSN, environment, and traces_sample_rate from environment variables
        2. Check if DSN is a placeholder (starts with "PLACEHOLDER" or "your-")
        3. If placeholder, print warning and return early
        4. Initialize Sentry SDK with sentry_sdk.init()

        Hints:
        - Use os.getenv() to read environment variables
        - sentry_sdk.init() takes: dsn, environment, traces_sample_rate
        - traces_sample_rate=1.0 means capture 100% of transactions
        - For production, you'd use lower sample rates (0.1 = 10%)

        Environment Variables:
        - SENTRY_DSN: Connection string from Sentry dashboard
        - SENTRY_ENVIRONMENT: Environment name (e.g., "lab", "prod")
        - SENTRY_TRACES_SAMPLE_RATE: Transaction sampling rate (0.0-1.0)

        Example:
            dsn = os.getenv("SENTRY_DSN", "PLACEHOLDER_DSN")
            if dsn == "PLACEHOLDER_DSN":
                print("[WARN] Sentry not configured...")
                return
            sentry_sdk.init(dsn=dsn, ...)
        """
        # Get configuration from environment
        dsn = os.getenv("SENTRY_DSN", "PLACEHOLDER_DSN")
        environment = os.getenv("SENTRY_ENVIRONMENT", "lab")
        traces_sample_rate = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "1.0"))

        # Check if using placeholder
        if dsn == "PLACEHOLDER_DSN" or dsn.startswith("your-"):
            print("[WARN] Sentry DSN not configured")
            print("   Using placeholder mode - events won't be sent to Sentry")
            print("   To enable: Add SENTRY_DSN to .env (see sentry_setup.md)")
            self.enabled = False
            return

        # TODO Exercise 3, Part 1: Initialize Sentry SDK
        # Replace 'pass' with your implementation
        # Hint: Use sentry_sdk.init() with the config variables above
        pass

        # Mark as enabled if initialization succeeds
        self.enabled = True
        print(f"Sentry initialized (environment: {environment})")

    def report_deployment_start(
        self,
        service_name: str,
        version: str,
        deployment_id: str
    ) -> None:
        """
        Report deployment start event to Sentry.

        TODO Exercise 3, Part 2: Report deployment events

        Steps:
        1. Open a scope for this event with sentry_sdk.new_scope()
        2. Set tags for: deployment_id, service, version
        3. Set context dict with deployment details
        4. Inside the same block, use capture_message() with level="info"

        Tags vs Context:
        - Tags: Short key-value pairs for filtering (shown in UI prominently)
        - Context: Rich structured data for debugging (shown in event details)

        Hints:
        - new_scope() returns a context manager (sentry-sdk 2.x; the older
          configure_scope() is deprecated)
        - Use scope.set_tag(key, value) for each tag
        - Use scope.set_context(name, dict) for structured data
        - capture_message(message, level="info") sends the event; call it
          inside the with block so the tags apply to it

        Example:
            with sentry_sdk.new_scope() as scope:
                scope.set_tag("deployment_id", deployment_id)
                scope.set_context("deployment", {...})
                capture_message("Deployment started: ...", level="info")

        Args:
            service_name: Name of service being deployed
            version: Version being deployed
            deployment_id: Unique deployment identifier
        """
        if not self.enabled:
            return

        # TODO Exercise 3, Part 2: Implement deployment start reporting
        # Replace 'pass' with your implementation
        pass

    def report_deployment_complete(
        self,
        service_name: str,
        version: str,
        deployment_id: str,
        success: bool,
        duration_seconds: Optional[float] = None
    ) -> None:
        """
        Report deployment completion to Sentry.

        TODO Exercise 3, Part 2: Report completion events

        Similar to report_deployment_start, but:
        - Set level="info" if success=True
        - Set level="error" if success=False
        - Include duration in context if provided
        - Add "status" tag: "succeeded" or "failed"

        Args:
            service_name: Name of service
            version: Version deployed
            deployment_id: Deployment identifier
            success: Whether deployment succeeded
            duration_seconds: Optional deployment duration
        """
        if not self.enabled:
            return

        level = "info" if success else "error"
        status = "succeeded" if success else "failed"

        # TODO Exercise 3, Part 2: Implement completion reporting
        # Hint: Similar to report_deployment_start but with status and duration
        pass

    def get_error_rate(
        self,
        service_name: str,
        version: str,
        minutes: int = 5
    ) -> float:
        """
        Get error rate from Sentry for a service version.

        TODO Exercise 3, Part 3: Implement error rate calculation

        Two approaches for this lab:

        Option 1 (Simpler - Recommended for Exercise 3):
        - Use simulated error rates
        - Good for learning the integration pattern
        - Allows testing without real traffic

        Option 2 (Advanced - Optional):
        - Query Sentry API for actual error counts
        - Requires Sentry Auth Token
        - Shows production-ready implementation

        For Option 1 (Simulated):
        1. Return 0.0 if not enabled
        2. Generate random error rate based on version name
        3. "bad" versions have higher error rates
        4. Normal versions have low error rates

        For Option 2 (Sentry API):
        1. Use Sentry's REST API to query events
        2. Filter by tags: service=service_name, version=version
        3. Count errors in last N minutes
        4. Calculate: error_rate = errors / total_requests

        Sentry API Example:
            GET /api/0/projects/{org}/{project}/events/
            Headers: Authorization: Bearer {token}
            Params: query=service:{service_name} version:{version}

        Args:
            service_name: Service to check
            version: Version to check
            minutes: Time window for error rate

        Returns:
            Error rate as float (0.0-1.0), e.g., 0.05 = 5% error rate
        """
        if not self.enabled:
            return 0.0

        # TODO Exercise 3, Part 3: Implement error rate calculation
        # Option 1 (Simpler): Use _get_simulated_error_rate() below
        # Option 2 (Advanced): Query Sentry API

        # For now, return simulated rate
        return self._get_simulated_error_rate(service_name, version)

    def _get_simulated_error_rate(
        self,
        service_name: str,
        version: str
    ) -> float:
        """
        Simulated error rate for lab purposes.

        This simulates what you'd get from Sentry API in production.
        Useful for testing rollback logic without generating real errors.

        Simulation Logic:
        - Versions with "bad", "broken", or "canary" have higher error rates
        - Normal versions have low background error rates
        - Adds randomness to simulate real-world variance

        In production, replace this with actual Sentry API query.

        Args:
            service_name: Service name (unused in simulation)
            version: Version string

        Returns:
            Simulated error rate (0.0-1.0)
        """
        import random

        # Simulate problematic versions
        problematic_keywords = ["bad", "broken", "canary", "beta"]
        is_problematic = any(kw in version.lower() for kw in problematic_keywords)

        if is_problematic:
            # 2-8% error rate for problematic versions
            return random.uniform(0.02, 0.08)
        else:
            # 0-0.5% error rate for stable versions
            return random.uniform(0.0, 0.005)

    def get_recent_errors(
        self,
        service_name: str,
        version: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get recent errors for a service version.

        TODO Exercise 3, Part 3: Implement error retrieval (Optional)

        This method provides error details for debugging and rollback decisions.

        For this lab, you can:
        - Return simulated errors (simpler)
        - Query Sentry API for real errors (advanced)

        Simulated Errors:
        Return a list of dicts with structure:
        {
            "message": "Error description",
            "count": Number of occurrences,
            "first_seen": ISO timestamp,
            "last_seen": ISO timestamp,
            "url": Link to Sentry issue
        }

        Sentry API:
        Query /api/0/projects/{org}/{project}/issues/
        Filter by tags and date range

        Args:
            service_name: Service to query
            version: Version to query
            limit: Maximum errors to return

        Returns:
            List of error dictionaries
        """
        if not self.enabled:
            return []

        # TODO Exercise 3, Part 3: Implement error retrieval
        # For lab, return simulated errors

        # Example simulated errors
        now = datetime.now()
        return [
            {
                "message": f"DatabaseConnectionError in {service_name}",
                "count": 23,
                "first_seen": (now - timedelta(minutes=5)).isoformat(),
                "last_seen": now.isoformat(),
                "url": "https://sentry.io/issues/simulated-12345"
            },
            {
                "message": f"NullPointerException in request handler",
                "count": 12,
                "first_seen": (now - timedelta(minutes=3)).isoformat(),
                "last_seen": (now - timedelta(minutes=1)).isoformat(),
                "url": "https://sentry.io/issues/simulated-67890"
            }
        ]

    def report_rollback(
        self,
        service_name: str,
        failed_version: str,
        stable_version: str,
        reason: str
    ) -> None:
        """
        Report rollback event to Sentry.

        TODO Exercise 3, Part 4: Report rollback events

        Rollbacks are critical events that deserve special attention in Sentry.

        Steps:
        1. Open a scope with sentry_sdk.new_scope() for the rollback event
        2. Add tag: rollback=true (for easy filtering)
        3. Set context with rollback details
        4. Inside the same block, use capture_message() with level="warning"

        Hints:
        - Rollbacks are warnings, not errors (the rollback itself succeeded)
        - Include both failed and stable version in context
        - Include reason for rollback
        - Set timestamp for chronological tracking

        Example Context:
        {
            "service": service_name,
            "failed_version": failed_version,
            "stable_version": stable_version,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }

        Args:
            service_name: Service being rolled back
            failed_version: Version that failed
            stable_version: Version rolling back to
            reason: Why rollback occurred
        """
        if not self.enabled:
            return

        # TODO Exercise 3, Part 4: Implement rollback reporting
        # Hint: Similar to deployment reporting but use level="warning"
        # Hint: Add "rollback" tag and context
        pass

    def report_canary_validation(
        self,
        service_name: str,
        version: str,
        validation_result: Dict
    ) -> None:
        """
        Report canary validation results to Sentry.

        TODO Exercise 3, Part 4: Report validation events (Optional)

        This helps track which validations pass or fail over time.

        Steps:
        1. Set tags for service, version, and validation result
        2. Set context with full validation metrics
        3. Use level="info" if healthy, "warning" if unhealthy
        4. Capture message with validation summary

        Args:
            service_name: Service being validated
            version: Version being validated
            validation_result: Dict with healthy, metrics, issues
        """
        if not self.enabled:
            return

        # TODO Exercise 3, Part 4: Implement validation reporting
        # Hint: Extract "healthy" from validation_result
        # Hint: Include metrics in context
        pass


# Example usage and testing
if __name__ == "__main__":
    """
    Test the SentryMonitor integration.

    Run this file directly to test Sentry connection:
        python integrations/sentry_integration.py

    This will:
    1. Initialize Sentry from .env configuration
    2. Send a test deployment event
    3. Simulate error rate check
    4. Send a test rollback event

    Check your Sentry dashboard to see the events!
    """
    print("=" * 60)
    print("Sentry Integration Test")
    print("=" * 60)
    print()

    # Initialize monitor
    print("Initializing Sentry monitor...")
    monitor = SentryMonitor()
    print()

    # In placeholder mode the monitor sends nothing. Say so, rather than
    # reporting events that never left this machine.
    sent = "sent" if monitor.enabled else "skipped (placeholder mode, nothing sent)"

    # Test deployment reporting
    print("Testing deployment event reporting...")
    monitor.report_deployment_start(
        service_name="test-service",
        version="1.0.0-test",
        deployment_id="test-deployment-123"
    )
    print(f"Deployment start event: {sent}")
    print()

    # Test error rate checking
    print("Testing error rate retrieval...")
    error_rate = monitor.get_error_rate("test-service", "1.0.0-test")
    print(f"Error rate for test-service v1.0.0-test: {error_rate:.2%}")
    print()

    # Test getting recent errors
    print("Testing recent errors retrieval...")
    errors = monitor.get_recent_errors("test-service", "1.0.0-test", limit=3)
    print(f"Retrieved {len(errors)} recent errors")
    for error in errors:
        print(f"  - {error['message']} (count: {error['count']})")
    print()

    # Test rollback reporting
    print("Testing rollback event reporting...")
    monitor.report_rollback(
        service_name="test-service",
        failed_version="1.0.0-test",
        stable_version="0.9.0",
        reason="High error rate detected during test"
    )
    print(f"Rollback event: {sent}")
    print()

    # Test deployment completion
    print("Testing deployment completion reporting...")
    monitor.report_deployment_complete(
        service_name="test-service",
        version="1.0.0-test",
        deployment_id="test-deployment-123",
        success=True,
        duration_seconds=45.3
    )
    print(f"Deployment completion event: {sent}")
    print()

    print("=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print()
    print("Next Steps:")
    if not monitor.enabled:
        print("1. Nothing was sent. Add SENTRY_DSN to .env to use a real project")
        print("   (see integrations/sentry_setup.md), or keep working offline")
        print("2. Complete the TODO sections above")
        print("3. Run this test again to verify your implementation")
    else:
        print("1. Check your Sentry dashboard: https://sentry.io/")
        print("2. Navigate to your project: zero-downtime-deployer-lab")
        print("3. Click 'Issues' to see the test events")
        print("4. Complete the TODO sections above to enable full integration")
        print("5. Run this test again to verify your implementation")
    print()
    print("Need help? See:")
    print("- integrations/sentry_setup.md - Setup instructions")
    print("- exercises/exercise-3-sentry.md - Full exercise guide")
    print("=" * 60)
