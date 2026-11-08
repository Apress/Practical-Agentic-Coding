"""
Module: FinOps Cost Optimization Agent
Concept: Automated cloud cost analysis and optimization
Chapter Reference: Bonus example (extends the cost guardrails in Section 11.5)

Section 11.5 builds a preventive gate: cost-guardrails.py blocks a deployment
before it incurs charges. This example covers the other half, the reactive side
the chapter contrasts it with: analyzing what you already spend, finding
rightsizing opportunities, and forecasting next month's bill.

Key Patterns Demonstrated:
- Multi-dimensional cost analysis
- Resource utilization vs cost correlation
- Automated rightsizing recommendations
- ROI calculation for optimization actions
- Cost anomaly detection
- Budget forecasting
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import random


class ResourceType(Enum):
    """Cloud resource types."""
    COMPUTE = "compute"
    STORAGE = "storage"
    DATABASE = "database"
    NETWORK = "network"
    SERVERLESS = "serverless"


class OptimizationType(Enum):
    """Types of cost optimization recommendations."""
    RIGHTSIZING = "rightsizing"
    RESERVED_INSTANCE = "reserved_instance"
    SPOT_INSTANCE = "spot_instance"
    STORAGE_TIER = "storage_tier"
    IDLE_RESOURCE = "idle_resource"
    UNUSED_RESOURCE = "unused_resource"


class Priority(Enum):
    """Priority levels for recommendations."""
    CRITICAL = "critical"  # Immediate action needed
    HIGH = "high"  # Action recommended soon
    MEDIUM = "medium"  # Action beneficial
    LOW = "low"  # Optional optimization


@dataclass
class ResourceCost:
    """Cost information for a cloud resource."""
    resource_id: str
    resource_type: ResourceType
    resource_name: str
    region: str
    monthly_cost: float
    utilization: float  # 0.0 to 1.0
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class CostOptimization:
    """A cost optimization recommendation."""
    resource_id: str
    resource_name: str
    optimization_type: OptimizationType
    priority: Priority
    current_monthly_cost: float
    projected_monthly_cost: float
    monthly_savings: float
    annual_savings: float
    implementation_effort: str
    risk_level: str
    recommendation: str
    technical_details: str


@dataclass
class CostAnomaly:
    """Detected cost anomaly."""
    resource_id: str
    resource_name: str
    expected_cost: float
    actual_cost: float
    variance_percentage: float
    detection_date: datetime = field(default_factory=datetime.now)
    description: str = ""


class FinOpsAgent:
    """
    FinOps Cost Optimization Agent.

    Demonstrates intelligent cost management including:
    - Cost analysis across resource type and region
    - Resource utilization tracking
    - Optimization opportunity identification
    - ROI calculation and forecasting
    """

    def __init__(self, organization: str, monthly_budget: float):
        """
        Initialize the FinOps agent.

        Args:
            organization: Organization name
            monthly_budget: Monthly cloud budget
        """
        self.organization = organization
        self.monthly_budget = monthly_budget
        self.resources: List[ResourceCost] = []
        self.optimizations: List[CostOptimization] = []
        self.anomalies: List[CostAnomaly] = []

        # Cost thresholds
        self.high_utilization_threshold = 0.80
        self.low_utilization_threshold = 0.20
        self.idle_threshold = 0.05

    def analyze_costs(self, resources: List[ResourceCost]) -> Dict[str, any]:
        """
        Break spend down by resource type, region, and utilization.

        Args:
            resources: List of cloud resources with cost information

        Returns:
            Cost analysis summary
        """
        self.resources = resources

        # Calculate total costs
        total_monthly_cost = sum(r.monthly_cost for r in resources)
        total_annual_cost = total_monthly_cost * 12

        # Cost by resource type
        cost_by_type = {}
        for resource in resources:
            resource_type = resource.resource_type.value
            cost_by_type[resource_type] = cost_by_type.get(resource_type, 0.0) + resource.monthly_cost

        # Cost by region
        cost_by_region = {}
        for resource in resources:
            cost_by_region[resource.region] = cost_by_region.get(resource.region, 0.0) + resource.monthly_cost

        # Utilization analysis
        low_utilization_resources = [r for r in resources if r.utilization < self.low_utilization_threshold]
        high_cost_resources = sorted(resources, key=lambda r: r.monthly_cost, reverse=True)[:10]

        # Budget analysis
        budget_utilization = (total_monthly_cost / self.monthly_budget) * 100
        remaining_budget = self.monthly_budget - total_monthly_cost

        return {
            "total_monthly_cost": total_monthly_cost,
            "total_annual_cost": total_annual_cost,
            "budget_utilization_pct": budget_utilization,
            "remaining_budget": remaining_budget,
            "cost_by_type": cost_by_type,
            "cost_by_region": cost_by_region,
            "total_resources": len(resources),
            "low_utilization_count": len(low_utilization_resources),
            "high_cost_resources": high_cost_resources
        }

    def identify_optimizations(self) -> List[CostOptimization]:
        """
        Identify cost optimization opportunities.

        Returns:
            List of optimization recommendations
        """
        self.optimizations = []

        for resource in self.resources:
            # Check for idle resources
            if resource.utilization < self.idle_threshold:
                self.optimizations.append(self._create_idle_resource_optimization(resource))

            # Check for rightsizing opportunities. Storage has no instance
            # size to shrink, so low-use storage falls through to the tier
            # check below instead.
            elif (resource.utilization < self.low_utilization_threshold
                  and resource.resource_type != ResourceType.STORAGE):
                self.optimizations.append(self._create_rightsizing_optimization(resource))

            # Check for reserved instance opportunities
            elif resource.utilization > self.high_utilization_threshold and resource.resource_type == ResourceType.COMPUTE:
                self.optimizations.append(self._create_reserved_instance_optimization(resource))

            # Check for storage tier optimizations
            elif resource.resource_type == ResourceType.STORAGE and resource.utilization < 0.50:
                self.optimizations.append(self._create_storage_tier_optimization(resource))

        # Sort by potential savings
        self.optimizations.sort(key=lambda o: o.monthly_savings, reverse=True)

        return self.optimizations

    def _create_idle_resource_optimization(self, resource: ResourceCost) -> CostOptimization:
        """Create optimization for idle resource."""
        return CostOptimization(
            resource_id=resource.resource_id,
            resource_name=resource.resource_name,
            optimization_type=OptimizationType.IDLE_RESOURCE,
            priority=Priority.CRITICAL,
            current_monthly_cost=resource.monthly_cost,
            projected_monthly_cost=0.0,
            monthly_savings=resource.monthly_cost,
            annual_savings=resource.monthly_cost * 12,
            implementation_effort="Low",
            risk_level="Low",
            recommendation=f"Terminate idle resource (utilization: {resource.utilization:.1%})",
            technical_details=f"Resource {resource.resource_name} has been idle with {resource.utilization:.1%} utilization. "
                            f"Consider terminating or stopping to save ${resource.monthly_cost:.2f}/month."
        )

    def _create_rightsizing_optimization(self, resource: ResourceCost) -> CostOptimization:
        """Create rightsizing optimization recommendation."""
        # Estimate smaller instance cost (typically 50% savings)
        projected_cost = resource.monthly_cost * 0.50
        savings = resource.monthly_cost - projected_cost

        return CostOptimization(
            resource_id=resource.resource_id,
            resource_name=resource.resource_name,
            optimization_type=OptimizationType.RIGHTSIZING,
            priority=Priority.HIGH,
            current_monthly_cost=resource.monthly_cost,
            projected_monthly_cost=projected_cost,
            monthly_savings=savings,
            annual_savings=savings * 12,
            implementation_effort="Medium",
            risk_level="Low",
            recommendation=f"Downsize resource (current utilization: {resource.utilization:.1%})",
            technical_details=f"Resource {resource.resource_name} shows low utilization at {resource.utilization:.1%}. "
                            f"Recommend downsizing to smaller instance type for ${savings:.2f}/month savings."
        )

    def _create_reserved_instance_optimization(self, resource: ResourceCost) -> CostOptimization:
        """Create reserved instance recommendation."""
        # Reserved instances typically save 30-40%
        projected_cost = resource.monthly_cost * 0.65
        savings = resource.monthly_cost - projected_cost

        return CostOptimization(
            resource_id=resource.resource_id,
            resource_name=resource.resource_name,
            optimization_type=OptimizationType.RESERVED_INSTANCE,
            priority=Priority.MEDIUM,
            current_monthly_cost=resource.monthly_cost,
            projected_monthly_cost=projected_cost,
            monthly_savings=savings,
            annual_savings=savings * 12,
            implementation_effort="Low",
            risk_level="Medium",
            recommendation=f"Convert to reserved instance (utilization: {resource.utilization:.1%})",
            technical_details=f"Resource {resource.resource_name} has consistent high utilization at {resource.utilization:.1%}. "
                            f"Reserved instance commitment could save ${savings:.2f}/month (~35% discount)."
        )

    def _create_storage_tier_optimization(self, resource: ResourceCost) -> CostOptimization:
        """Create storage tier optimization."""
        # Cheaper storage tier typically saves 40-60%
        projected_cost = resource.monthly_cost * 0.50
        savings = resource.monthly_cost - projected_cost

        return CostOptimization(
            resource_id=resource.resource_id,
            resource_name=resource.resource_name,
            optimization_type=OptimizationType.STORAGE_TIER,
            priority=Priority.MEDIUM,
            current_monthly_cost=resource.monthly_cost,
            projected_monthly_cost=projected_cost,
            monthly_savings=savings,
            annual_savings=savings * 12,
            implementation_effort="Low",
            risk_level="Low",
            recommendation=f"Move to cheaper storage tier (access rate: {resource.utilization:.1%})",
            technical_details=f"Storage {resource.resource_name} has low access rate at {resource.utilization:.1%}. "
                            f"Consider moving to infrequent access tier for ${savings:.2f}/month savings."
        )

    def detect_cost_anomalies(self, historical_costs: Dict[str, List[float]]) -> List[CostAnomaly]:
        """
        Detect cost anomalies using statistical analysis.

        Args:
            historical_costs: Historical cost data per resource

        Returns:
            List of detected cost anomalies
        """
        self.anomalies = []

        for resource in self.resources:
            if resource.resource_id not in historical_costs:
                continue

            history = historical_costs[resource.resource_id]
            if len(history) < 3:
                continue

            # Calculate expected cost (average of historical costs)
            expected_cost = sum(history) / len(history)

            # Calculate standard deviation
            variance = sum((cost - expected_cost) ** 2 for cost in history) / len(history)
            std_dev = variance ** 0.5

            # Check if current cost is anomalous (> 2 standard deviations)
            current_cost = resource.monthly_cost
            if abs(current_cost - expected_cost) > (2 * std_dev):
                variance_pct = ((current_cost - expected_cost) / expected_cost) * 100

                self.anomalies.append(CostAnomaly(
                    resource_id=resource.resource_id,
                    resource_name=resource.resource_name,
                    expected_cost=expected_cost,
                    actual_cost=current_cost,
                    variance_percentage=variance_pct,
                    description=f"Cost spike detected: {abs(variance_pct):.1f}% {'increase' if variance_pct > 0 else 'decrease'}"
                ))

        return self.anomalies

    def calculate_optimization_roi(self, implementation_cost: float = 0.0) -> Dict[str, any]:
        """
        Calculate ROI for implementing all recommendations.

        Args:
            implementation_cost: One-time cost to implement optimizations

        Returns:
            ROI analysis
        """
        if not self.optimizations:
            return {"status": "no_optimizations"}

        total_monthly_savings = sum(opt.monthly_savings for opt in self.optimizations)
        total_annual_savings = sum(opt.annual_savings for opt in self.optimizations)

        # Calculate payback period
        if total_monthly_savings > 0:
            payback_months = implementation_cost / total_monthly_savings
        else:
            payback_months = float('inf')

        # Calculate ROI percentage (first year)
        if implementation_cost > 0:
            roi_percentage = ((total_annual_savings - implementation_cost) / implementation_cost) * 100
        else:
            roi_percentage = float('inf')

        # 3-year projection
        three_year_savings = total_annual_savings * 3 - implementation_cost

        return {
            "total_monthly_savings": total_monthly_savings,
            "total_annual_savings": total_annual_savings,
            "implementation_cost": implementation_cost,
            "payback_period_months": payback_months,
            "roi_percentage": roi_percentage,
            "three_year_savings": three_year_savings,
            "optimization_count": len(self.optimizations)
        }

    def generate_budget_forecast(self, months_ahead: int = 6) -> List[Dict[str, any]]:
        """
        Generate budget forecast with and without optimizations.

        Args:
            months_ahead: Number of months to forecast

        Returns:
            List of monthly forecasts
        """
        current_monthly_cost = sum(r.monthly_cost for r in self.resources)
        potential_monthly_savings = sum(opt.monthly_savings for opt in self.optimizations)

        forecasts = []

        for month in range(1, months_ahead + 1):
            # Add small growth factor (5% annually = ~0.4% monthly)
            growth_factor = 1.004 ** month

            baseline_cost = current_monthly_cost * growth_factor
            optimized_cost = (current_monthly_cost - potential_monthly_savings) * growth_factor

            forecasts.append({
                "month": month,
                "baseline_cost": baseline_cost,
                "optimized_cost": optimized_cost,
                "savings": baseline_cost - optimized_cost,
                "budget_remaining_baseline": self.monthly_budget - baseline_cost,
                "budget_remaining_optimized": self.monthly_budget - optimized_cost
            })

        return forecasts

    def get_executive_summary(self) -> str:
        """
        Generate executive summary of cost optimization analysis.

        Returns:
            Formatted executive summary
        """
        if not self.resources:
            return "No cost data available for analysis."

        current_monthly_cost = sum(r.monthly_cost for r in self.resources)
        total_savings = sum(opt.monthly_savings for opt in self.optimizations)
        savings_percentage = (total_savings / current_monthly_cost) * 100 if current_monthly_cost > 0 else 0

        summary = f"""
╔═══════════════════════════════════════════════════════════════╗
║              FINOPS COST OPTIMIZATION SUMMARY                 ║
╚═══════════════════════════════════════════════════════════════╝

Organization: {self.organization}
Analysis Date: {datetime.now().strftime('%Y-%m-%d')}

CURRENT STATE:
  • Total Resources: {len(self.resources)}
  • Monthly Cost: ${current_monthly_cost:,.2f}
  • Annual Cost: ${current_monthly_cost * 12:,.2f}
  • Budget Utilization: {(current_monthly_cost / self.monthly_budget) * 100:.1f}%

OPTIMIZATION OPPORTUNITIES:
  • Total Recommendations: {len(self.optimizations)}
  • Potential Monthly Savings: ${total_savings:,.2f}
  • Potential Annual Savings: ${total_savings * 12:,.2f}
  • Savings Percentage: {savings_percentage:.1f}%

TOP RECOMMENDATIONS:
"""

        # Add top 5 recommendations
        for i, opt in enumerate(self.optimizations[:5], 1):
            summary += f"""
  {i}. [{opt.priority.value.upper()}] {opt.resource_name}
     Type: {opt.optimization_type.value}
     Savings: ${opt.monthly_savings:,.2f}/month
     Action: {opt.recommendation}
"""

        if self.anomalies:
            summary += f"""
COST ANOMALIES DETECTED:
  • {len(self.anomalies)} anomalies requiring investigation
"""

        return summary


def generate_sample_resources() -> List[ResourceCost]:
    """Generate sample cloud resources for demonstration."""
    resources = []

    # Compute instances
    for i in range(15):
        resources.append(ResourceCost(
            resource_id=f"i-{i:04d}",
            resource_type=ResourceType.COMPUTE,
            resource_name=f"web-server-{i}",
            region="us-east-1" if i < 8 else "us-west-2",
            monthly_cost=random.uniform(50, 500),
            utilization=random.uniform(0.05, 0.95),
            tags={"environment": "production" if i < 10 else "development"}
        ))

    # Storage buckets
    for i in range(8):
        resources.append(ResourceCost(
            resource_id=f"s3-{i:04d}",
            resource_type=ResourceType.STORAGE,
            resource_name=f"data-bucket-{i}",
            region="us-east-1",
            monthly_cost=random.uniform(100, 1000),
            utilization=random.uniform(0.1, 0.8),
            tags={"type": "storage"}
        ))

    # Databases
    for i in range(5):
        resources.append(ResourceCost(
            resource_id=f"db-{i:04d}",
            resource_type=ResourceType.DATABASE,
            resource_name=f"postgres-db-{i}",
            region="us-east-1",
            monthly_cost=random.uniform(200, 800),
            utilization=random.uniform(0.3, 0.9),
            tags={"type": "database"}
        ))

    return resources


if __name__ == "__main__":
    print("=== FinOps Cost Optimization Agent Demo ===\n")

    # Initialize agent
    agent = FinOpsAgent(
        organization="Example Corp",
        monthly_budget=15000.0
    )

    # Generate sample resources
    resources = generate_sample_resources()

    print("1. Analyzing Cloud Costs")
    print("=" * 70)
    analysis = agent.analyze_costs(resources)

    print(f"Total Monthly Cost: ${analysis['total_monthly_cost']:,.2f}")
    print(f"Total Annual Cost: ${analysis['total_annual_cost']:,.2f}")
    print(f"Budget Utilization: {analysis['budget_utilization_pct']:.1f}%")
    print(f"Remaining Budget: ${analysis['remaining_budget']:,.2f}\n")

    print("Cost by Resource Type:")
    for resource_type, cost in analysis['cost_by_type'].items():
        percentage = (cost / analysis['total_monthly_cost']) * 100
        print(f"  • {resource_type}: ${cost:,.2f} ({percentage:.1f}%)")

    print("\n2. Identifying Optimization Opportunities")
    print("=" * 70)
    optimizations = agent.identify_optimizations()

    print(f"Found {len(optimizations)} optimization opportunities\n")

    for i, opt in enumerate(optimizations[:5], 1):
        print(f"{i}. {opt.resource_name}")
        print(f"   Type: {opt.optimization_type.value}")
        print(f"   Priority: {opt.priority.value.upper()}")
        print(f"   Monthly Savings: ${opt.monthly_savings:.2f}")
        print(f"   Annual Savings: ${opt.annual_savings:.2f}")
        print(f"   Recommendation: {opt.recommendation}\n")

    print("3. Detecting Cost Anomalies")
    print("=" * 70)

    # Generate mock historical cost data
    historical_costs = {}
    for resource in resources[:5]:
        # Create consistent historical pattern with one anomaly
        base_cost = resource.monthly_cost * 0.8
        historical_costs[resource.resource_id] = [
            base_cost,
            base_cost * 1.05,
            base_cost * 0.95,
            base_cost * 1.02
        ]

    anomalies = agent.detect_cost_anomalies(historical_costs)
    print(f"Detected {len(anomalies)} cost anomalies\n")

    for anomaly in anomalies:
        print(f"[ANOMALY] {anomaly.resource_name}")
        print(f"   Expected: ${anomaly.expected_cost:.2f}")
        print(f"   Actual: ${anomaly.actual_cost:.2f}")
        print(f"   Variance: {anomaly.variance_percentage:+.1f}%")
        print(f"   {anomaly.description}\n")

    print("4. Calculating Optimization ROI")
    print("=" * 70)
    roi = agent.calculate_optimization_roi(implementation_cost=5000.0)

    print(f"Total Monthly Savings: ${roi['total_monthly_savings']:,.2f}")
    print(f"Total Annual Savings: ${roi['total_annual_savings']:,.2f}")
    print(f"Implementation Cost: ${roi['implementation_cost']:,.2f}")
    print(f"Payback Period: {roi['payback_period_months']:.1f} months")
    print(f"First Year ROI: {roi['roi_percentage']:.1f}%")
    print(f"3-Year Net Savings: ${roi['three_year_savings']:,.2f}\n")

    print("5. Budget Forecast")
    print("=" * 70)
    forecasts = agent.generate_budget_forecast(months_ahead=6)

    print(f"{'Month':<8} {'Baseline':<15} {'Optimized':<15} {'Savings':<12}")
    print("-" * 70)
    for forecast in forecasts:
        print(f"{forecast['month']:<8} "
              f"${forecast['baseline_cost']:<14,.2f} "
              f"${forecast['optimized_cost']:<14,.2f} "
              f"${forecast['savings']:<11,.2f}")

    # Executive Summary
    print("\n" + "=" * 70)
    print(agent.get_executive_summary())

    print("\nFinOps agent demonstration complete.")
