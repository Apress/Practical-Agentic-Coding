"""
Module: Cost Guardrails (pipeline cost gate)
Concept: Preventive budget enforcement before a deployment incurs charges
Chapter Reference: Section 11.5, "Cost guardrails"

This is the pipeline GATE from the book: it wraps infracost, converts the
estimate into per-category monthly numbers, compares them against budget
limits, and returns a decision (approve, warn, or block) with reasoning that
a CI job can act on.

It is deliberately different from finops-agent.py in this same directory.
The FinOps agent is reactive: it looks at what you already spent and suggests
rightsizing. This gate is preventive: it runs before `terraform apply` and
refuses to let a change through when the projected monthly cost breaks the
budget. Platform cost tools tell you "you spent $800 on unused EBS volumes
last month." This gate says "this deployment would add $1,200/month in
compute, which exceeds your $1,000 budget for this service."

Key patterns demonstrated:
- Parsing infracost JSON output into per-category monthly estimates
- Comparing the monthly delta and per-category totals against budget limits
- Separating the estimate (what it costs) from the policy (what is allowed)
- Graceful degradation when the infracost binary is not installed
- Fail-closed versus fail-open behavior for an unavailable estimator

Runs with no external dependencies and no infracost installed: a sample
infracost payload is bundled in fixtures/ so you can see the gate work
before you wire it to a real Terraform plan.

    python cost-guardrails.py                          # demo, uses the fixture
    python cost-guardrails.py --plan plan.json         # run infracost yourself
    python cost-guardrails.py --breakdown infracost.json \
        --budgets .github/budget-limits.json --json cost-gate.json

Use --plan to have the gate shell out to infracost. Use --breakdown when a CI
step already produced the infracost report (see github-actions-gates.yml in
this directory, which runs infracost in Docker and then applies policy here).

Exit codes: 0 = approve or warn, 1 = block, 2 = bad usage.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import shutil
import sys
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

HERE = Path(__file__).resolve().parent
SAMPLE_BREAKDOWN = HERE / "fixtures" / "infracost-breakdown-sample.json"
SAMPLE_BUDGETS = HERE / "fixtures" / "budget-limits.json"

# The reserved budget key that caps the whole plan rather than one category.
TOTAL_KEY = "total"


class GateAction(Enum):
    """What the pipeline should do with this deployment."""
    APPROVE = "approve"
    WARN = "warn"
    BLOCK = "block"


class CostEstimationError(RuntimeError):
    """Raised when no cost estimate could be produced at all."""


@dataclass
class BudgetViolation:
    """A category (or the plan total) that exceeds its budget limit."""
    category: str
    estimated: float
    limit: float

    @property
    def overage(self) -> float:
        return round(self.estimated - self.limit, 2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "estimated": round(self.estimated, 2),
            "limit": round(self.limit, 2),
            "overage": self.overage,
        }


@dataclass
class BudgetWarning:
    """A category close enough to its limit to be worth flagging."""
    category: str
    estimated: float
    limit: float
    utilization: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "estimated": round(self.estimated, 2),
            "limit": round(self.limit, 2),
            "utilization_pct": round(self.utilization * 100, 1),
        }


@dataclass
class GateDecision:
    """The gate's answer, shaped so CI can parse it and humans can read it."""
    action: GateAction
    reason: str
    estimated_monthly: Dict[str, float] = field(default_factory=dict)
    monthly_delta: float = 0.0
    violations: List[BudgetViolation] = field(default_factory=list)
    warnings: List[BudgetWarning] = field(default_factory=list)
    estimator: str = "infracost"
    estimate_source: str = "infracost"
    notes: List[str] = field(default_factory=list)

    @property
    def approved(self) -> bool:
        """A warn still lets the deployment proceed. A block does not."""
        return self.action is not GateAction.BLOCK

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.action.value,
            "approved": self.approved,
            "reason": self.reason,
            "monthly_delta": round(self.monthly_delta, 2),
            "estimated_monthly": {
                k: round(v, 2) for k, v in sorted(self.estimated_monthly.items())
            },
            "violations": [v.to_dict() for v in self.violations],
            "warnings": [w.to_dict() for w in self.warnings],
            "estimator": self.estimator,
            "estimate_source": self.estimate_source,
            "notes": self.notes,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


# Resource-type prefix to budget category. Deliberately coarse: budget owners
# think in terms of compute, storage, database, and network, not in terms of
# 200 provider resource types. Extend this map for your own stack.
CATEGORY_RULES: List[tuple] = [
    ("database", (
        "aws_db_", "aws_rds", "aws_dynamodb", "aws_elasticache", "aws_redshift",
        "aws_docdb", "aws_neptune", "aws_memorydb",
        "azurerm_mssql", "azurerm_postgresql", "azurerm_mysql", "azurerm_cosmosdb",
        "google_sql_", "google_bigtable", "google_redis",
    )),
    ("compute", (
        "aws_instance", "aws_autoscaling_group", "aws_eks", "aws_ecs",
        "aws_lambda", "aws_batch", "aws_fargate", "aws_launch_",
        "azurerm_linux_virtual_machine", "azurerm_windows_virtual_machine",
        "azurerm_virtual_machine", "azurerm_kubernetes_cluster",
        "azurerm_function_app", "azurerm_container_",
        "google_compute_instance", "google_container_", "google_cloudfunctions",
    )),
    ("storage", (
        "aws_ebs_", "aws_s3_", "aws_efs_", "aws_fsx", "aws_backup",
        "azurerm_storage_", "azurerm_managed_disk",
        "google_storage_", "google_compute_disk",
    )),
    ("network", (
        "aws_lb", "aws_alb", "aws_elb", "aws_nat_gateway", "aws_cloudfront",
        "aws_vpn_", "aws_route53", "aws_api_gateway", "aws_globalaccelerator",
        "azurerm_lb", "azurerm_application_gateway", "azurerm_nat_gateway",
        "azurerm_cdn_", "azurerm_dns_",
        "google_compute_forwarding_rule", "google_compute_router_nat",
        "google_dns_",
    )),
]


def categorize(resource_type: str) -> str:
    """Map an infracost resourceType to a budget category."""
    name = (resource_type or "").lower()
    for category, prefixes in CATEGORY_RULES:
        if name.startswith(prefixes):
            return category
    return "other"


class CostGuardrails:
    """Automated guardrails for cloud spending.

    Wraps `infracost breakdown --path <plan> --format json`, turns the result
    into per-category monthly estimates, and applies budget policy.

    Args:
        budget_limits: Estimated monthly USD ceilings per category, for
            example {"compute": 1000, "storage": 300}. The reserved key
            "total" caps the whole plan.
        warn_threshold: Fraction of a limit that triggers a warning instead
            of silent approval. 0.8 warns at 80% of budget.
        fail_closed: When the estimator cannot run, block (True) or warn and
            let the deployment through (False). Block is the safe default for
            production; teams adopting the gate often start fail-open.
        infracost_binary: Name or path of the infracost executable.
        breakdown_path: An infracost JSON report that has already been
            produced, for example by a CI step that ran infracost in Docker.
            When set, the gate reads this instead of shelling out.
        fixture_path: Optional sample infracost JSON. Used when
            infracost is not installed so the example still runs.
        timeout_seconds: How long to wait for infracost before giving up.
    """

    def __init__(
        self,
        budget_limits: Dict[str, float],
        warn_threshold: float = 0.8,
        fail_closed: bool = True,
        infracost_binary: str = "infracost",
        breakdown_path: Optional[Path] = None,
        fixture_path: Optional[Path] = None,
        timeout_seconds: float = 120.0,
    ):
        self.budgets = dict(budget_limits)
        self.warn_threshold = warn_threshold
        self.fail_closed = fail_closed
        self.infracost_binary = infracost_binary
        self.breakdown_path = breakdown_path
        self.fixture_path = fixture_path
        self.timeout_seconds = timeout_seconds
        # Set by the most recent estimate: "infracost", "precomputed", or
        # "fixture". Recorded in the decision so nobody mistakes a sample for
        # a real estimate.
        self.last_estimate_source = "infracost"
        self.last_notes: List[str] = []

    # ---------------------------------------------------------------- book API

    async def check_deployment(self, terraform_plan: str) -> Dict[str, Any]:
        """Estimate plan cost, compare against budget limits.

        Returns approved=True only if zero violations. This is the shape the
        book shows: a plain dict a pipeline step can branch on.
        """
        estimated, monthly_delta = await self._run_infracost(terraform_plan)
        violations = []
        for category, limit in self.budgets.items():
            actual = monthly_delta if category == TOTAL_KEY else estimated.get(category, 0)
            if actual > limit:
                violations.append({
                    "category": category,
                    "estimated": round(actual, 2),
                    "limit": round(float(limit), 2),
                })
        return {
            "approved": len(violations) == 0,
            "violations": violations,
            "estimated_monthly": {k: round(v, 2) for k, v in estimated.items()},
        }

    # ------------------------------------------------------------- gate policy

    async def evaluate(self, terraform_plan: str) -> GateDecision:
        """Estimate cost, then apply policy to produce a gate decision.

        check_deployment answers "does this fit the budget?" evaluate answers
        "what should the pipeline do?" Keeping them apart means you can change
        thresholds without touching the estimator, the same separation the
        security gate makes between risk assessment and risk policy.
        """
        try:
            estimated, monthly_delta = await self._run_infracost(terraform_plan)
        except CostEstimationError as exc:
            action = GateAction.BLOCK if self.fail_closed else GateAction.WARN
            posture = "fail-closed" if self.fail_closed else "fail-open"
            return GateDecision(
                action=action,
                reason=f"No cost estimate available ({exc}); policy is {posture}",
                estimator=self.infracost_binary,
                estimate_source="unavailable",
                notes=list(self.last_notes),
            )

        violations: List[BudgetViolation] = []
        warnings: List[BudgetWarning] = []

        for category, raw_limit in self.budgets.items():
            limit = float(raw_limit)
            if limit <= 0:
                continue
            actual = monthly_delta if category == TOTAL_KEY else estimated.get(category, 0.0)
            if actual > limit:
                violations.append(BudgetViolation(category, actual, limit))
            elif actual >= limit * self.warn_threshold:
                warnings.append(BudgetWarning(category, actual, limit, actual / limit))

        uncategorized = sorted(set(estimated) - set(self.budgets) - {TOTAL_KEY})
        notes = list(self.last_notes)
        if uncategorized:
            notes.append(
                "No budget limit set for: " + ", ".join(uncategorized)
                + ". These costs are reported but not enforced."
            )

        decision = GateDecision(
            action=GateAction.APPROVE,
            reason="",
            estimated_monthly=estimated,
            monthly_delta=monthly_delta,
            violations=violations,
            warnings=warnings,
            estimator=self.infracost_binary,
            estimate_source=self.last_estimate_source,
            notes=notes,
        )

        if violations:
            worst = max(violations, key=lambda v: v.overage)
            decision.action = GateAction.BLOCK
            decision.reason = (
                f"{len(violations)} budget violation(s); "
                f"{worst.category} is ${worst.overage:,.2f}/month over its "
                f"${worst.limit:,.0f} limit"
            )
        elif warnings:
            hottest = max(warnings, key=lambda w: w.utilization)
            decision.action = GateAction.WARN
            decision.reason = (
                f"Within budget, but {hottest.category} is at "
                f"{hottest.utilization * 100:.0f}% of its "
                f"${hottest.limit:,.0f} limit"
            )
        else:
            decision.reason = (
                f"Estimated ${monthly_delta:,.2f}/month added, within all budget limits"
            )
        return decision

    # ----------------------------------------------------------- estimator I/O

    async def _run_infracost(self, terraform_plan: str) -> tuple:
        """Return (per-category monthly estimate, monthly delta).

        Three sources, in priority order:

        1. A breakdown_path: an infracost report a CI step already produced.
           This is the normal path in a pipeline, where infracost runs in its
           own container and this gate only applies policy to the result.
        2. The infracost binary on PATH, invoked as
           `infracost breakdown --path <plan> --format json`.
        3. A configured fixture, so the example runs with nothing installed.
        """
        self.last_notes = []

        if self.breakdown_path is not None:
            self.last_estimate_source = "precomputed"
            try:
                return self._parse_infracost_json(self.breakdown_path.read_text())
            except OSError as exc:
                raise CostEstimationError(
                    f"could not read the infracost report {self.breakdown_path}: {exc}"
                )

        binary = shutil.which(self.infracost_binary)

        if binary is None:
            if self.fixture_path is None:
                raise CostEstimationError(
                    f"'{self.infracost_binary}' not found on PATH and no fixture configured"
                )
            self.last_estimate_source = "fixture"
            self.last_notes.append(
                f"infracost not found on PATH; using the bundled sample "
                f"{self.fixture_path.name}. Install infracost 0.10 "
                "(github.com/infracost/infracost/releases) before trusting "
                "these numbers."
            )
            return self._parse_infracost_json(self.fixture_path.read_text())

        cmd = [binary, "breakdown", "--path", terraform_plan, "--format", "json"]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=self.timeout_seconds
            )
        except asyncio.TimeoutError:
            raise CostEstimationError(
                f"infracost timed out after {self.timeout_seconds:.0f}s"
            )
        except OSError as exc:
            raise CostEstimationError(f"could not run infracost: {exc}")

        if proc.returncode != 0:
            detail = (stderr or b"").decode("utf-8", "replace").strip().splitlines()
            tail = detail[-1] if detail else f"exit code {proc.returncode}"
            raise CostEstimationError(f"infracost failed: {tail}")

        self.last_estimate_source = "infracost"
        return self._parse_infracost_json(stdout.decode("utf-8", "replace"))

    def _parse_infracost_json(self, raw: str) -> tuple:
        """Turn an infracost JSON payload into per-category monthly numbers.

        Notes on the payload shape that matter in practice:
        - A resource's monthlyCost already includes its subresources, so
          summing both would double-count.
        - Usage-based resources (S3 requests, Lambda invocations) come back
          with monthlyCost=null until you supply a usage file. They are
          counted as unpriced and surfaced as a note, not as $0.
        - infracost reports the plan total and, when a past state exists, the
          delta. The delta is what a budget owner cares about: new spend the
          change adds.
        """
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise CostEstimationError(f"infracost output was not valid JSON: {exc}")

        per_category: Dict[str, float] = {}
        unpriced: List[str] = []

        for project in payload.get("projects") or []:
            resources = (project.get("breakdown") or {}).get("resources")
            if not resources:
                resources = (project.get("diff") or {}).get("resources") or []
            for resource in resources:
                monthly = resource.get("monthlyCost")
                if monthly in (None, ""):
                    unpriced.append(resource.get("name", "unnamed resource"))
                    continue
                category = categorize(resource.get("resourceType", ""))
                per_category[category] = per_category.get(category, 0.0) + float(monthly)

        total_monthly = _as_float(payload.get("totalMonthlyCost"))
        if total_monthly is None:
            total_monthly = sum(per_category.values())
        delta = _as_float(payload.get("diffTotalMonthlyCost"))
        monthly_delta = delta if delta is not None else total_monthly

        if unpriced:
            self.last_notes.append(
                f"{len(unpriced)} usage-based resource(s) have no price estimate "
                f"({', '.join(unpriced[:3])}"
                + (", ..." if len(unpriced) > 3 else "")
                + "). Supply an infracost usage file to include them."
            )
        unsupported = (payload.get("summary") or {}).get("totalUnsupportedResources")
        if unsupported:
            self.last_notes.append(
                f"{unsupported} resource(s) are not supported by infracost and "
                "are excluded from the estimate."
            )
        return per_category, monthly_delta


def _as_float(value: Any) -> Optional[float]:
    """infracost emits money as strings. Return None rather than guessing."""
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def load_budgets(path: Path) -> Dict[str, float]:
    """Read a budget-limits.json file, ignoring _comment style metadata."""
    data = json.loads(path.read_text())
    budgets: Dict[str, float] = {}
    for key, value in data.items():
        if key.startswith("_"):
            continue
        numeric = _as_float(value)
        if numeric is not None:
            budgets[key] = numeric
    if not budgets:
        raise ValueError(f"{path} contains no numeric budget limits")
    return budgets


def render_report(decision: GateDecision) -> str:
    """Human-readable summary for a PR comment or a job log."""
    icon = {
        GateAction.APPROVE: "PASS",
        GateAction.WARN: "WARN",
        GateAction.BLOCK: "BLOCK",
    }[decision.action]

    lines = [
        "=" * 68,
        f"COST GATE: {icon}",
        "=" * 68,
        f"Reason:          {decision.reason}",
        f"Monthly delta:   ${decision.monthly_delta:,.2f}",
        f"Estimate source: {decision.estimate_source}",
        "",
        "Estimated monthly cost by category:",
    ]
    if decision.estimated_monthly:
        for category, amount in sorted(decision.estimated_monthly.items()):
            lines.append(f"  {category:<12} ${amount:>12,.2f}")
    else:
        lines.append("  (no priced resources)")

    if decision.violations:
        lines += ["", "Budget violations:"]
        for violation in decision.violations:
            lines.append(
                f"  {violation.category:<12} ${violation.estimated:>12,.2f}  "
                f"limit ${violation.limit:,.2f}  over by ${violation.overage:,.2f}"
            )
    if decision.warnings:
        lines += ["", "Approaching budget:"]
        for warning in decision.warnings:
            lines.append(
                f"  {warning.category:<12} ${warning.estimated:>12,.2f}  "
                f"limit ${warning.limit:,.2f}  ({warning.utilization * 100:.0f}% used)"
            )
    if decision.notes:
        lines += ["", "Notes:"]
        lines += [f"  - {note}" for note in decision.notes]
    lines.append("=" * 68)
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Preventive cost gate for CI/CD (Chapter 11, Section 11.5).",
    )
    parser.add_argument(
        "--plan",
        help="Path passed to infracost (a Terraform plan JSON file or a "
             "directory). Omit to run the bundled sample.",
    )
    parser.add_argument(
        "--breakdown",
        type=Path,
        help="An infracost JSON report that already exists. Use this in CI "
             "when a previous step ran infracost (for example in Docker); the "
             "gate then only applies budget policy. Takes precedence over --plan.",
    )
    parser.add_argument(
        "--budgets",
        type=Path,
        default=SAMPLE_BUDGETS,
        help=f"Budget limits JSON file (default: {SAMPLE_BUDGETS.name} in fixtures/).",
    )
    parser.add_argument(
        "--fixture",
        default=str(SAMPLE_BREAKDOWN),
        help="Sample infracost JSON to fall back on when infracost is not "
             "installed. Pass --fixture '' to disable the fallback.",
    )
    parser.add_argument(
        "--warn-threshold",
        type=float,
        default=0.8,
        help="Warn when a category reaches this fraction of its limit (default: 0.8).",
    )
    parser.add_argument(
        "--fail-open",
        action="store_true",
        help="Warn instead of blocking when no cost estimate can be produced.",
    )
    parser.add_argument(
        "--json",
        dest="json_out",
        type=Path,
        help="Write the machine-readable decision to this file (for CI artifacts).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress the text report; useful when only --json matters.",
    )
    return parser


async def run_cli(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        budgets = load_budgets(args.budgets)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: could not read budgets: {exc}", file=sys.stderr)
        return 2

    fixture = Path(args.fixture) if args.fixture.strip() else None
    if fixture is not None and not fixture.is_file():
        print(f"error: fixture is not a readable file: {fixture}", file=sys.stderr)
        return 2

    if args.breakdown is not None and not args.breakdown.is_file():
        print(
            f"error: infracost report not found: {args.breakdown}",
            file=sys.stderr,
        )
        return 2

    guardrails = CostGuardrails(
        budget_limits=budgets,
        warn_threshold=args.warn_threshold,
        fail_closed=not args.fail_open,
        breakdown_path=args.breakdown,
        fixture_path=fixture,
    )

    # With neither --breakdown nor --plan there is nothing for infracost to
    # read, so fall back to the bundled sample. This is what makes the
    # example runnable out of the box.
    plan = args.plan
    if args.breakdown is None and plan is None:
        if fixture is None:
            print(
                "error: pass --breakdown or --plan, or keep --fixture so the "
                "demo has data",
                file=sys.stderr,
            )
            return 2
        guardrails.infracost_binary = "__demo_no_infracost__"

    decision = await guardrails.evaluate(plan or "(sample)")

    if not args.quiet:
        print(render_report(decision))
    if args.json_out:
        args.json_out.write_text(decision.to_json() + "\n")
        if not args.quiet:
            print(f"\nDecision written to {args.json_out}")

    return 0 if decision.approved else 1


async def demo() -> None:
    """Three scenarios: within budget, over budget, estimator unavailable."""
    budgets = load_budgets(SAMPLE_BUDGETS)

    print("\n" + "=" * 68)
    print("SCENARIO 1: generous budgets, deployment fits")
    print("=" * 68)
    generous = dict(budgets, total=5000, compute=2000, database=1000)
    gate = CostGuardrails(generous, fixture_path=SAMPLE_BREAKDOWN,
                          infracost_binary="__demo_no_infracost__")
    print(render_report(await gate.evaluate("(sample)")))

    print("\n" + "=" * 68)
    print("SCENARIO 2: real service budgets, deployment blocked")
    print("=" * 68)
    gate = CostGuardrails(budgets, fixture_path=SAMPLE_BREAKDOWN,
                          infracost_binary="__demo_no_infracost__")
    decision = await gate.evaluate("(sample)")
    print(render_report(decision))
    print("\nMachine-readable form the pipeline consumes:")
    print(decision.to_json())

    print("\n" + "=" * 68)
    print("SCENARIO 3: infracost missing and no fixture (fail-closed)")
    print("=" * 68)
    gate = CostGuardrails(budgets, fixture_path=None,
                          infracost_binary="__demo_no_infracost__")
    print(render_report(await gate.evaluate("terraform/plan.json")))

    print("\n" + "=" * 68)
    print("Same estimate through the book's check_deployment() shape")
    print("=" * 68)
    gate = CostGuardrails(budgets, fixture_path=SAMPLE_BREAKDOWN,
                          infracost_binary="__demo_no_infracost__")
    print(json.dumps(await gate.check_deployment("(sample)"), indent=2))

    print("\nKey insights:")
    print("  - Platform cost tools are reactive; this gate is preventive")
    print("  - The estimate and the policy are separate, so thresholds can")
    print("    change without touching the estimator")
    print("  - A warn lets the deployment proceed; a block does not")
    print("  - An unavailable estimator is a decision, not a crash")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        sys.exit(asyncio.run(run_cli()))
    asyncio.run(demo())
