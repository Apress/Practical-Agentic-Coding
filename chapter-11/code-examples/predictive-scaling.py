"""
Module: Predictive Resource Scaling Agent
Concept: ML-based predictive autoscaling for cloud resources
Chapter Reference: Bonus example (extends Section 11.5 cost and scaling patterns)

This example demonstrates how AI agents can predict resource needs and
proactively scale infrastructure. The agent collects metrics, analyzes
patterns, and makes intelligent scaling decisions.

Key Patterns Demonstrated:
- Time-series metric collection and analysis
- Simple ML-based prediction (moving averages and trend analysis)
- Proactive vs reactive scaling decisions
- Multi-metric scaling strategies
- Scale-up and scale-down policies
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import random


class MetricType(Enum):
    """Types of resource metrics."""
    CPU_UTILIZATION = "cpu_utilization"
    MEMORY_UTILIZATION = "memory_utilization"
    REQUEST_RATE = "request_rate"
    RESPONSE_TIME = "response_time"
    QUEUE_DEPTH = "queue_depth"


class ScalingDirection(Enum):
    """Scaling direction decisions."""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    NO_CHANGE = "no_change"


class ScalingTrigger(Enum):
    """What triggered the scaling decision."""
    REACTIVE = "reactive"  # Current metrics exceeded threshold
    PREDICTIVE = "predictive"  # Predicted future need
    SCHEDULED = "scheduled"  # Known traffic patterns
    MANUAL = "manual"  # Human override


@dataclass
class MetricDataPoint:
    """Single metric observation."""
    metric_type: MetricType
    value: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ScalingDecision:
    """A scaling decision made by the agent."""
    direction: ScalingDirection
    trigger: ScalingTrigger
    current_capacity: int
    target_capacity: int
    confidence: float  # 0.0 to 1.0
    reasoning: str
    predicted_metrics: Dict[MetricType, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ResourceMetrics:
    """Collection of metrics for a time period."""
    cpu_utilization: float
    memory_utilization: float
    request_rate: float
    response_time: float
    timestamp: datetime = field(default_factory=datetime.now)


class PredictiveScalingAgent:
    """
    Predictive Resource Scaling Agent.

    Demonstrates intelligent autoscaling including:
    - Metric collection and time-series analysis
    - Trend detection and pattern recognition
    - Predictive scaling decisions
    - Multi-metric evaluation
    """

    def __init__(
        self,
        resource_name: str,
        min_capacity: int = 1,
        max_capacity: int = 10,
        prediction_window_minutes: int = 15
    ):
        """
        Initialize the predictive scaling agent.

        Args:
            resource_name: Name of the resource being scaled
            min_capacity: Minimum number of instances
            max_capacity: Maximum number of instances
            prediction_window_minutes: How far ahead to predict
        """
        self.resource_name = resource_name
        self.min_capacity = min_capacity
        self.max_capacity = max_capacity
        self.prediction_window = timedelta(minutes=prediction_window_minutes)
        self.current_capacity = min_capacity

        # Metric storage (time-series data)
        self.metric_history: List[ResourceMetrics] = []
        self.scaling_history: List[ScalingDecision] = []

        # Scaling thresholds
        self.scale_up_threshold = 0.70  # 70% utilization
        self.scale_down_threshold = 0.30  # 30% utilization
        self.cooldown_period = timedelta(minutes=5)
        self.last_scaling_action: Optional[datetime] = None

    def collect_metrics(self, metrics: ResourceMetrics) -> None:
        """
        Collect and store resource metrics.

        Args:
            metrics: Current resource metrics
        """
        self.metric_history.append(metrics)

        # Keep only last 24 hours of data, measured on the samples' clock
        cutoff_time = metrics.timestamp - timedelta(hours=24)
        self.metric_history = [
            m for m in self.metric_history
            if m.timestamp > cutoff_time
        ]

    def _now(self) -> datetime:
        """
        Current time on the metrics' clock.

        The demo replays two simulated hours in well under a second, so the
        agent reads time from the latest sample instead of the wall clock.
        With live metrics the two are the same.
        """
        if self.metric_history:
            return self.metric_history[-1].timestamp
        return datetime.now()

    def analyze_and_scale(self) -> Optional[ScalingDecision]:
        """
        Analyze metrics and make scaling decision.

        This is the main agent decision-making function that combines
        reactive and predictive approaches.

        Returns:
            Scaling decision if action is needed, None otherwise
        """
        if not self.metric_history:
            return None

        # Check cooldown period
        if self._in_cooldown_period():
            print("   In cooldown period, skipping scaling decision")
            return None

        # Get current metrics
        current_metrics = self.metric_history[-1]

        # 1. Check for immediate reactive scaling needs
        reactive_decision = self._evaluate_reactive_scaling(current_metrics)
        if reactive_decision and reactive_decision.direction != ScalingDirection.NO_CHANGE:
            return self._execute_scaling_decision(reactive_decision)

        # 2. Perform predictive analysis
        predictive_decision = self._evaluate_predictive_scaling()
        if predictive_decision and predictive_decision.direction != ScalingDirection.NO_CHANGE:
            return self._execute_scaling_decision(predictive_decision)

        # 3. Check for scheduled scaling (known patterns)
        scheduled_decision = self._evaluate_scheduled_scaling()
        if scheduled_decision and scheduled_decision.direction != ScalingDirection.NO_CHANGE:
            return self._execute_scaling_decision(scheduled_decision)

        return None

    def _evaluate_reactive_scaling(self, metrics: ResourceMetrics) -> ScalingDecision:
        """
        Evaluate need for immediate reactive scaling.

        Args:
            metrics: Current resource metrics

        Returns:
            Scaling decision based on current state
        """
        # Calculate average utilization across metrics
        avg_utilization = (metrics.cpu_utilization + metrics.memory_utilization) / 2

        if avg_utilization > self.scale_up_threshold:
            # Calculate how many instances we need
            utilization_ratio = avg_utilization / self.scale_up_threshold
            additional_instances = math.ceil((self.current_capacity * utilization_ratio) - self.current_capacity)
            target_capacity = min(self.current_capacity + additional_instances, self.max_capacity)

            return ScalingDecision(
                direction=ScalingDirection.SCALE_UP,
                trigger=ScalingTrigger.REACTIVE,
                current_capacity=self.current_capacity,
                target_capacity=target_capacity,
                confidence=0.95,
                reasoning=f"Current utilization {avg_utilization:.1%} exceeds threshold {self.scale_up_threshold:.1%}"
            )

        elif avg_utilization < self.scale_down_threshold:
            # Calculate how many instances we can remove
            utilization_ratio = avg_utilization / self.scale_down_threshold
            instances_to_remove = math.floor(self.current_capacity - (self.current_capacity * utilization_ratio))
            target_capacity = max(self.current_capacity - instances_to_remove, self.min_capacity)

            if target_capacity < self.current_capacity:
                return ScalingDecision(
                    direction=ScalingDirection.SCALE_DOWN,
                    trigger=ScalingTrigger.REACTIVE,
                    current_capacity=self.current_capacity,
                    target_capacity=target_capacity,
                    confidence=0.85,
                    reasoning=f"Current utilization {avg_utilization:.1%} below threshold {self.scale_down_threshold:.1%}"
                )

        return ScalingDecision(
            direction=ScalingDirection.NO_CHANGE,
            trigger=ScalingTrigger.REACTIVE,
            current_capacity=self.current_capacity,
            target_capacity=self.current_capacity,
            confidence=1.0,
            reasoning="Metrics within acceptable range"
        )

    def _evaluate_predictive_scaling(self) -> Optional[ScalingDecision]:
        """
        Evaluate need for predictive scaling based on trends.

        This uses simple time-series analysis to predict future needs.

        Returns:
            Scaling decision based on predicted future state
        """
        if len(self.metric_history) < 10:
            return None  # Need sufficient history for prediction

        # Predict future metrics using trend analysis
        predicted_cpu = self._predict_metric_value(MetricType.CPU_UTILIZATION)
        predicted_memory = self._predict_metric_value(MetricType.MEMORY_UTILIZATION)
        predicted_request_rate = self._predict_metric_value(MetricType.REQUEST_RATE)

        predicted_avg_utilization = (predicted_cpu + predicted_memory) / 2

        print(f"   Predicted metrics (in {self.prediction_window.seconds//60}min):")
        print(f"     CPU: {predicted_cpu:.1%}, Memory: {predicted_memory:.1%}, "
              f"Requests: {predicted_request_rate:.1f}/s")

        # Make proactive scaling decision
        if predicted_avg_utilization > self.scale_up_threshold:
            utilization_ratio = predicted_avg_utilization / self.scale_up_threshold
            additional_instances = math.ceil((self.current_capacity * utilization_ratio) - self.current_capacity)
            target_capacity = min(self.current_capacity + additional_instances, self.max_capacity)

            # Only scale if prediction is confident
            if self._is_trend_consistent():
                return ScalingDecision(
                    direction=ScalingDirection.SCALE_UP,
                    trigger=ScalingTrigger.PREDICTIVE,
                    current_capacity=self.current_capacity,
                    target_capacity=target_capacity,
                    confidence=0.75,
                    reasoning=f"Predicted utilization {predicted_avg_utilization:.1%} will exceed threshold",
                    predicted_metrics={
                        MetricType.CPU_UTILIZATION: predicted_cpu,
                        MetricType.MEMORY_UTILIZATION: predicted_memory,
                        MetricType.REQUEST_RATE: predicted_request_rate
                    }
                )

        elif predicted_avg_utilization < self.scale_down_threshold * 0.8:
            # More conservative for scale-down predictions
            target_capacity = max(self.current_capacity - 1, self.min_capacity)

            if target_capacity < self.current_capacity and self._is_trend_consistent():
                return ScalingDecision(
                    direction=ScalingDirection.SCALE_DOWN,
                    trigger=ScalingTrigger.PREDICTIVE,
                    current_capacity=self.current_capacity,
                    target_capacity=target_capacity,
                    confidence=0.65,
                    reasoning=f"Predicted utilization {predicted_avg_utilization:.1%} will remain low",
                    predicted_metrics={
                        MetricType.CPU_UTILIZATION: predicted_cpu,
                        MetricType.MEMORY_UTILIZATION: predicted_memory,
                        MetricType.REQUEST_RATE: predicted_request_rate
                    }
                )

        return None

    def _predict_metric_value(self, metric_type: MetricType) -> float:
        """
        Predict future metric value using trend analysis.

        This uses a simple linear regression approach with weighted recent values.

        Args:
            metric_type: Type of metric to predict

        Returns:
            Predicted metric value
        """
        # Extract metric values from history
        recent_history = self.metric_history[-30:]  # Last 30 data points

        if metric_type == MetricType.CPU_UTILIZATION:
            values = [m.cpu_utilization for m in recent_history]
        elif metric_type == MetricType.MEMORY_UTILIZATION:
            values = [m.memory_utilization for m in recent_history]
        elif metric_type == MetricType.REQUEST_RATE:
            values = [m.request_rate for m in recent_history]
        else:
            return 0.0

        if not values:
            return 0.0

        # Calculate weighted moving average (more weight on recent values)
        weights = [i + 1 for i in range(len(values))]
        weighted_sum = sum(v * w for v, w in zip(values, weights))
        weight_sum = sum(weights)
        weighted_avg = weighted_sum / weight_sum

        # Calculate trend (simple linear trend)
        if len(values) >= 2:
            recent_avg = sum(values[-5:]) / len(values[-5:])
            older_avg = sum(values[:5]) / len(values[:5])
            trend = (recent_avg - older_avg) / len(values)

            # Project trend forward
            prediction = weighted_avg + (trend * 10)  # Project 10 time periods ahead
        else:
            prediction = weighted_avg

        # Clamp prediction to reasonable bounds. Utilization is a fraction;
        # request rate is per second and only needs a floor.
        if metric_type == MetricType.REQUEST_RATE:
            return max(0.0, prediction)
        return max(0.0, min(1.0, prediction))

    def _is_trend_consistent(self) -> bool:
        """
        Check if the trend is consistent enough to trust prediction.

        Returns:
            True if trend is consistent and reliable
        """
        if len(self.metric_history) < 5:
            return False

        # Check if recent metrics show consistent direction
        recent_cpu = [m.cpu_utilization for m in self.metric_history[-5:]]
        recent_memory = [m.memory_utilization for m in self.metric_history[-5:]]

        # Simple consistency check: are values moving in same direction?
        cpu_trend = sum(recent_cpu[i+1] > recent_cpu[i] for i in range(len(recent_cpu)-1))
        memory_trend = sum(recent_memory[i+1] > recent_memory[i] for i in range(len(recent_memory)-1))

        # Trend is consistent if 3 or 4 out of 4 comparisons go same direction
        return cpu_trend >= 3 or memory_trend >= 3

    def _evaluate_scheduled_scaling(self) -> Optional[ScalingDecision]:
        """
        Evaluate scheduled scaling based on known patterns.

        This demonstrates scaling for predictable traffic patterns
        (e.g., business hours, batch jobs).

        Returns:
            Scaling decision based on schedule
        """
        current_hour = self._now().hour

        # Example: Scale up during business hours (9 AM - 5 PM)
        if 9 <= current_hour < 17:
            if self.current_capacity < 4:
                return ScalingDecision(
                    direction=ScalingDirection.SCALE_UP,
                    trigger=ScalingTrigger.SCHEDULED,
                    current_capacity=self.current_capacity,
                    target_capacity=4,
                    confidence=1.0,
                    reasoning="Scheduled scale-up for business hours"
                )

        # Example: Scale down during night hours (10 PM - 6 AM)
        elif current_hour >= 22 or current_hour < 6:
            if self.current_capacity > self.min_capacity:
                return ScalingDecision(
                    direction=ScalingDirection.SCALE_DOWN,
                    trigger=ScalingTrigger.SCHEDULED,
                    current_capacity=self.current_capacity,
                    target_capacity=self.min_capacity,
                    confidence=1.0,
                    reasoning="Scheduled scale-down for off-hours"
                )

        return None

    def _execute_scaling_decision(self, decision: ScalingDecision) -> ScalingDecision:
        """
        Execute a scaling decision.

        Args:
            decision: Scaling decision to execute

        Returns:
            The executed decision
        """
        print(f"\n   Scaling Decision:")
        print(f"     Direction: {decision.direction.value.upper()}")
        print(f"     Trigger: {decision.trigger.value}")
        print(f"     Capacity: {decision.current_capacity} -> {decision.target_capacity}")
        print(f"     Confidence: {decision.confidence:.1%}")
        print(f"     Reasoning: {decision.reasoning}")

        # Update capacity
        old_capacity = self.current_capacity
        self.current_capacity = decision.target_capacity
        self.last_scaling_action = self._now()

        # Record decision
        self.scaling_history.append(decision)

        print(f"     Scaled from {old_capacity} to {self.current_capacity} instances")

        return decision

    def _in_cooldown_period(self) -> bool:
        """Check if we're in cooldown period after recent scaling."""
        if self.last_scaling_action is None:
            return False

        time_since_last_action = self._now() - self.last_scaling_action
        return time_since_last_action < self.cooldown_period

    def get_scaling_report(self) -> Dict[str, any]:
        """
        Generate scaling activity report.

        Returns:
            Dictionary with scaling statistics
        """
        if not self.scaling_history:
            # Full key set with zeros, so report consumers never need to
            # special-case an idle period
            return {
                "status": "no_scaling_activity",
                "total_scaling_decisions": 0,
                "scale_ups": 0,
                "scale_downs": 0,
                "current_capacity": self.current_capacity,
                "trigger_distribution": {},
                "average_confidence": 0.0
            }

        total_decisions = len(self.scaling_history)
        scale_ups = sum(1 for d in self.scaling_history if d.direction == ScalingDirection.SCALE_UP)
        scale_downs = sum(1 for d in self.scaling_history if d.direction == ScalingDirection.SCALE_DOWN)

        trigger_counts = {}
        for decision in self.scaling_history:
            trigger = decision.trigger.value
            trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1

        return {
            "status": "ok",
            "total_scaling_decisions": total_decisions,
            "scale_ups": scale_ups,
            "scale_downs": scale_downs,
            "current_capacity": self.current_capacity,
            "trigger_distribution": trigger_counts,
            "average_confidence": sum(d.confidence for d in self.scaling_history) / total_decisions
        }


def simulate_traffic_pattern(timestamp: datetime) -> ResourceMetrics:
    """
    Simulate realistic traffic patterns for demonstration.

    Args:
        timestamp: Simulated time of the sample

    Returns:
        Simulated resource metrics, stamped with the simulated time
    """
    # Create daily traffic pattern
    hour = timestamp.hour

    # Base load
    base_cpu = 0.20
    base_memory = 0.25
    base_requests = 10.0

    # Add time-of-day variation
    if 9 <= hour < 17:  # Business hours
        multiplier = 2.0 + timestamp.minute / 120.0  # Gradual increase
    elif 17 <= hour < 22:  # Evening
        multiplier = 1.5
    else:  # Night
        multiplier = 0.8

    # Add random noise
    noise = random.uniform(-0.1, 0.1)

    cpu = min(0.95, base_cpu * multiplier + noise)
    memory = min(0.95, base_memory * multiplier + noise)
    requests = max(1.0, base_requests * multiplier + (noise * 20))

    return ResourceMetrics(
        cpu_utilization=max(0.0, cpu),
        memory_utilization=max(0.0, memory),
        request_rate=requests,
        response_time=50 + (cpu * 100),  # Response time increases with CPU
        timestamp=timestamp,
    )


if __name__ == "__main__":
    print("=== Predictive Resource Scaling Demo ===\n")

    # Initialize agent
    agent = PredictiveScalingAgent(
        resource_name="web-service",
        min_capacity=2,
        max_capacity=10,
        prediction_window_minutes=15
    )

    print(f"Resource: {agent.resource_name}")
    print(f"Capacity Range: {agent.min_capacity}-{agent.max_capacity} instances")
    print(f"Initial Capacity: {agent.current_capacity} instances\n")

    # Simulate 2 hours of operation, one sample every 5 minutes. The window
    # starts at 08:00 so it crosses into business hours at 09:00. Every time
    # check (cooldown, schedule) reads this simulated clock, not the wall clock.
    start = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
    print("=" * 70)
    print("Simulating resource scaling from 08:00 to 10:00...")
    print("=" * 70)

    for minute in range(0, 120, 5):
        now = start + timedelta(minutes=minute)
        print(f"\nTime: {now:%H:%M} (+{minute} min)")

        # Collect metrics
        metrics = simulate_traffic_pattern(now)
        agent.collect_metrics(metrics)

        print(f"   Current Metrics:")
        print(f"     CPU: {metrics.cpu_utilization:.1%}")
        print(f"     Memory: {metrics.memory_utilization:.1%}")
        print(f"     Requests: {metrics.request_rate:.1f}/s")
        print(f"     Current Capacity: {agent.current_capacity} instances")

        # Analyze and potentially scale
        decision = agent.analyze_and_scale()

    # Generate final report
    print("\n" + "=" * 70)
    print("SCALING ACTIVITY REPORT")
    print("=" * 70)

    report = agent.get_scaling_report()
    print(f"Total scaling decisions: {report['total_scaling_decisions']}")
    print(f"Scale-up actions: {report['scale_ups']}")
    print(f"Scale-down actions: {report['scale_downs']}")
    print(f"Final capacity: {report['current_capacity']} instances")

    if report["total_scaling_decisions"] > 0:
        print(f"Average confidence: {report['average_confidence']:.1%}")
        print(f"\nTrigger distribution:")
        for trigger, count in report['trigger_distribution'].items():
            print(f"  - {trigger}: {count}")
    else:
        print("\nNo scaling was needed: utilization stayed inside the "
              "30-70% band at minimum capacity.")

    print("\nPredictive scaling demonstration complete.")
