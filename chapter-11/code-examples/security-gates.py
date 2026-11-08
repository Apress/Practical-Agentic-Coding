"""
Module: Security Gates in the Pipeline
Concept: An analysis agent produces an assessment, a gate applies policy to it
Chapter Reference: Section 11.5

Section 11.5 splits the security gate into two objects on purpose:

- SecurityComplianceAgent does the analysis. It routes each file to the right
  scanner (ASH for multi-language SAST and IaC, Trivy for Dockerfile
  misconfigurations, Bandit and npm audit for language specifics), then asks
  the model which controls are affected and whether each finding is
  exploitable in this deployment context.
- SecurityGate turns that assessment into a pipeline decision through
  _apply_policy: critical blocks, high blocks unless policy allows it, medium
  warns, everything else approves.

Keeping them apart means you can change policy thresholds without touching
analysis logic, and improving the analysis does not silently change which
deployments get approved.

Scanner subprocesses and the model call are simulated so this runs anywhere.
Point _run at the real binaries (ASH is the AWS Automated Security Helper,
github.com/awslabs/automated-security-helper) and _llm_assess at your model to
make it production code.

Key Patterns Demonstrated:
- Scanner routing by file type, with ASH as the multi-language baseline
- Contextual assessment: a test fixture credential is not a production secret
- Blast-radius reasoning that downgrades an unreachable CVE from high to medium
- Policy chain separated from risk assessment
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class Severity(str, Enum):
    """Finding severity, ordered from worst to least."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Finding:
    """One scanner finding, before contextual assessment."""
    finding_id: str
    title: str
    severity: Severity
    location: str
    scanner: str
    cve_id: Optional[str] = None
    remediation: str = ""
    # Set by the contextual assessment step, not by the scanner.
    context_note: str = ""
    assessed_severity: Optional[Severity] = None

    @property
    def effective_severity(self) -> Severity:
        return self.assessed_severity or self.severity


@dataclass
class ComplianceCheck:
    """Result of evaluating one control from one framework."""
    framework: str
    control: str
    status: str  # "pass", "fail", or "needs_evidence"
    detail: str
    evidence_required: str = ""


@dataclass
class ScanRun:
    """Everything one gate evaluation produced, for the report."""
    findings: list[Finding] = field(default_factory=list)
    compliance: list[ComplianceCheck] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)


class SecurityComplianceAgent:
    """Automates security compliance checks in CI/CD."""

    # Which scanner owns which file type. ASH runs over the whole tree first as
    # the multi-language baseline; these handle the deeper per-file checks.
    SCANNER_BY_SUFFIX = {
        "Dockerfile": "trivy",
        ".py": "bandit",
        "package.json": "npm-audit",
    }

    def __init__(self, compliance_frameworks: list[str]) -> None:
        self.frameworks = compliance_frameworks
        # In production this is an Agent with the four methods below registered
        # as tools (see the SecurityComplianceAgent listing in Section 11.5).
        self.system_prompt = self._system_prompt()

    def _system_prompt(self) -> str:
        frameworks = ", ".join(self.frameworks)
        return (
            "You are a security compliance agent in a deployment pipeline. "
            "For each scanner finding, decide which controls it affects, whether "
            "it is exploitable in this deployment context, and what evidence an "
            f"auditor would need. Frameworks in scope: {frameworks}. "
            "Report risk; do not modify code."
        )

    async def scan_vulnerabilities(self, paths: list[str]) -> dict:
        """Run the right scanner for each file type."""
        findings: list[Finding] = []
        # ASH covers SAST across languages + IaC scanning
        ash_result = await self._run(
            "ash", "--source-dir", ".", "--output-dir", "/tmp/ash", paths=paths
        )
        findings.extend(self._parse_ash_findings(ash_result))
        # Language-specific scanners for deeper analysis
        for path in paths:
            scanner = self._scanner_for(path)
            if scanner == "trivy":
                result = await self._run("trivy", "config", path)
            elif scanner == "bandit":
                result = await self._run("bandit", "-r", path)
            elif scanner == "npm-audit":
                result = await self._run("npm", "audit", "--json")
            else:
                continue
            findings.extend(self._parse_findings(result, path))
        return {"findings": findings, "count": len(findings)}

    async def check_compliance(
        self, description: str, resources: list[str]
    ) -> list[ComplianceCheck]:
        """
        Evaluate the change against each configured framework.

        The architecture is framework-agnostic: you supply the frameworks, and
        the agent evaluates each change against them. This is where the model
        adds what a static scanner cannot, judging which controls a change
        actually touches.
        """
        checks: list[ComplianceCheck] = []
        for framework in self.frameworks:
            checks.extend(
                await self._llm_check_framework(framework, description, resources)
            )
        return checks

    async def assess_risk(
        self, vulns: dict, compliance: list[ComplianceCheck]
    ) -> dict:
        """
        Turn findings plus compliance state into one risk level.

        Contextual assessment happens here: the model reads the surrounding code
        and decides whether a finding is exploitable where it actually runs. A
        hardcoded credential in a test fixture is not a production secret. A
        high-severity CVE in a library that only a test utility imports has no
        reachable code path in production.
        """
        findings: list[Finding] = vulns["findings"]
        for finding in findings:
            await self._llm_assess(finding)

        worst = Severity.INFO
        order = [
            Severity.CRITICAL,
            Severity.HIGH,
            Severity.MEDIUM,
            Severity.LOW,
            Severity.INFO,
        ]
        for level in order:
            if any(f.effective_severity == level for f in findings):
                worst = level
                break

        failed_controls = [c for c in compliance if c.status == "fail"]
        if failed_controls and worst in (Severity.LOW, Severity.INFO):
            # A failed control matters even when no scanner found anything.
            worst = Severity.MEDIUM

        return {
            "risk_level": worst.value,
            "finding_count": len(findings),
            "downgraded": [
                f.finding_id
                for f in findings
                if f.assessed_severity and f.assessed_severity != f.severity
            ],
            "failed_controls": [
                f"{c.framework}:{c.control}" for c in failed_controls
            ],
        }

    async def generate_report(
        self, vulns: dict, compliance: list[ComplianceCheck], risk: dict
    ) -> str:
        """Human-readable summary for the pipeline log and the audit trail."""
        lines = [
            "SECURITY GATE REPORT",
            f"Frameworks: {', '.join(self.frameworks)}",
            f"Risk level: {risk['risk_level']}",
            f"Findings: {risk['finding_count']}",
            "",
            "Findings:",
        ]
        for finding in vulns["findings"]:
            line = (
                f"  [{finding.effective_severity.value}] {finding.title} "
                f"({finding.scanner}, {finding.location})"
            )
            if finding.assessed_severity and finding.assessed_severity != finding.severity:
                line += f"  <- downgraded from {finding.severity.value}"
            lines.append(line)
            if finding.context_note:
                lines.append(f"      context: {finding.context_note}")
        lines.append("")
        lines.append("Compliance:")
        for check in compliance:
            lines.append(
                f"  [{check.status}] {check.framework} {check.control}: {check.detail}"
            )
        return "\n".join(lines)

    # ---- scanner plumbing --------------------------------------------------

    def _scanner_for(self, path: str) -> Optional[str]:
        for suffix, scanner in self.SCANNER_BY_SUFFIX.items():
            if path.endswith(suffix):
                return scanner
        return None

    async def _run(
        self, *command: str, paths: Optional[list[str]] = None
    ) -> dict[str, Any]:
        """
        Stand-in for the scanner subprocess.

        Real implementation: asyncio.create_subprocess_exec(*command), then parse
        the tool's JSON output. The stubs below return the shape each scanner
        reports so the parsing code has something to work on. `paths` only exists
        so the stub can produce findings that match the change under review; a
        real ASH run walks the source tree itself.
        """
        await asyncio.sleep(0.02)
        tool = command[0]
        if tool == "ash":
            results = []
            for path in paths or []:
                if path.endswith(".py"):
                    results.append(
                        {
                            "id": f"ASH-SAST-{len(results) + 1:03d}",
                            "title": "Possible SQL injection in query builder",
                            "severity": "high",
                            "location": f"{path}:45",
                            "remediation": "Use parameterized queries",
                        }
                    )
                if path.endswith(".tf"):
                    results.append(
                        {
                            "id": f"ASH-IAC-{len(results) + 1:03d}",
                            "title": "S3 bucket without server-side encryption",
                            "severity": "medium",
                            "location": f"{path}:12",
                            "remediation": "Set server_side_encryption_configuration",
                        }
                    )
            return {"tool": "ash", "results": results}
        if tool == "bandit":
            return {
                "tool": "bandit",
                "results": [
                    {
                        "id": "B105",
                        "title": "Hardcoded password string",
                        "severity": "critical",
                        "location": f"{command[-1]}:12",
                        "remediation": "Load from a secret manager",
                    }
                ],
            }
        if tool == "trivy":
            # Shape of a `trivy config` misconfiguration finding. Image CVE
            # scanning (`trivy image`) runs after the build, outside this gate.
            return {
                "tool": "trivy",
                "results": [
                    {
                        "id": "AVD-DS-0002",
                        "title": "Image runs as root (no USER instruction)",
                        "severity": "high",
                        "location": f"{command[-1]}",
                        "remediation": "Add a non-root USER instruction",
                    }
                ],
            }
        if tool == "npm":
            return {"tool": "npm-audit", "results": []}
        return {"tool": tool, "results": []}

    def _parse_ash_findings(self, result: dict[str, Any]) -> list[Finding]:
        return self._parse_findings(result, source_path="")

    def _parse_findings(
        self, result: dict[str, Any], source_path: str = ""
    ) -> list[Finding]:
        findings = []
        for item in result.get("results", []):
            findings.append(
                Finding(
                    finding_id=item["id"],
                    title=item["title"],
                    severity=Severity(item["severity"]),
                    location=item.get("location", source_path),
                    scanner=result["tool"],
                    cve_id=item.get("cve"),
                    remediation=item.get("remediation", ""),
                )
            )
        return findings

    # ---- model plumbing ----------------------------------------------------

    async def _llm_assess(self, finding: Finding) -> None:
        """
        Stand-in for the contextual assessment call.

        Real implementation sends the finding plus the surrounding code to the
        model and asks whether it is exploitable where it runs. The rules below
        stand in for two judgments the chapter calls out by name.
        """
        await asyncio.sleep(0.02)
        location = finding.location.lower()

        # A credential in a test fixture is not a production secret, and a
        # query built in a test never sees untrusted input.
        if "test" in location or "fixture" in location or "conftest" in location:
            finding.assessed_severity = Severity.LOW
            finding.context_note = (
                "Test-only path: never deployed, inputs are fixtures, not "
                "user data"
            )
            return

        # A high CVE with no production code path is real but not urgent.
        if finding.cve_id and "dev" in location:
            finding.assessed_severity = Severity.MEDIUM
            finding.context_note = (
                "Vulnerable code path is unreachable in production "
                "(dev dependency only)"
            )
            return

        finding.assessed_severity = finding.severity
        finding.context_note = "Reachable in the deployed path"

    async def _llm_check_framework(
        self, framework: str, description: str, resources: list[str]
    ) -> list[ComplianceCheck]:
        """
        Stand-in for the per-framework compliance evaluation.

        Real implementation sends scanner findings plus code context and asks:
        which controls are affected, is the finding exploitable in this
        deployment context, what evidence would an auditor need?
        """
        await asyncio.sleep(0.02)
        checks = []
        unencrypted = any("storage" in r or "bucket" in r for r in resources)
        checks.append(
            ComplianceCheck(
                framework=framework,
                control="encryption-at-rest",
                status="fail" if unencrypted else "pass",
                detail=(
                    "Storage resource in this change has no encryption block"
                    if unencrypted
                    else "All storage resources declare encryption"
                ),
                evidence_required="Terraform plan showing encryption enabled",
            )
        )
        checks.append(
            ComplianceCheck(
                framework=framework,
                control="audit-logging",
                status="needs_evidence",
                detail=f"Change description does not mention logging: {description[:60]}",
                evidence_required="CloudTrail or equivalent log configuration",
            )
        )
        return checks


class SecurityGate:
    """Security gate that blocks or approves deployments."""

    def __init__(
        self,
        compliance_agent: SecurityComplianceAgent,
        policy: dict,
    ) -> None:
        self.agent = compliance_agent
        self.policy = policy

    async def evaluate(self, deployment: dict) -> dict:
        """Scan -> check compliance -> assess risk -> apply policy."""
        vulns = await self.agent.scan_vulnerabilities(
            deployment["affected_paths"]
        )
        compliance = await self.agent.check_compliance(
            deployment["description"], deployment["resources"]
        )
        risk = await self.agent.assess_risk(vulns, compliance)
        decision = self._apply_policy(risk)
        return {
            "decision": decision["action"],
            "reason": decision["reason"],
            "risk": risk,
            "report": await self.agent.generate_report(
                vulns, compliance, risk
            ),
        }

    def _apply_policy(self, risk: dict) -> dict:
        """Policy decision chain: critical -> block,
        high -> block (unless allowed), medium -> warn,
        everything else -> approve."""
        risk_level = risk.get("risk_level", "unknown")
        if risk_level == "critical":
            return {"action": "block", "reason": "Critical risk"}
        if risk_level == "high":
            if not self.policy.get("allow_high_risk"):
                return {"action": "block", "reason": "High risk"}
        if risk_level in ["medium", "high"]:
            return {
                "action": "warn",
                "reason": f"{risk_level} risk - review recommended",
            }
        return {"action": "approve", "reason": "Acceptable risk"}


async def main() -> None:
    print("=== Security gate: assessment separated from policy ===\n")

    agent = SecurityComplianceAgent(
        compliance_frameworks=["internal-baseline", "SOC2"]
    )
    strict_gate = SecurityGate(agent, policy={"allow_high_risk": False})

    # A change touching application code, IaC, and the container image.
    production_change = {
        "description": "Add invoice export endpoint and its S3 bucket",
        "affected_paths": [
            "src/api/invoices.py",
            "terraform/storage.tf",
            "Dockerfile",
        ],
        "resources": ["terraform/storage.tf", "aws_s3_bucket.exports"],
    }

    # ---- Case 1: real findings in production code --------------------------
    print("Case 1: findings in the deployed path")
    print("-" * 62)
    result = await strict_gate.evaluate(production_change)
    print(result["report"])
    print(f"\n  DECISION: {result['decision'].upper()} ({result['reason']})")

    # ---- Case 2: same scanners, findings only in test paths ----------------
    print("\n\nCase 2: the same scanners, same change, but in test paths")
    print("-" * 62)
    result = await strict_gate.evaluate(
        {
            "description": "Add contract tests, with logging assertions",
            "affected_paths": ["tests/test_invoices.py"],
            "resources": [],
        }
    )
    print(result["report"])
    print(f"\n  DECISION: {result['decision'].upper()} ({result['reason']})")
    print(
        "  The scanners fired on identical patterns. Contextual assessment "
        "downgraded them,\n  because a fixture credential is not a live secret."
    )

    # ---- Case 3: one assessment, two policies ------------------------------
    print("\n\nCase 3: one assessment, two policies")
    print("-" * 62)
    # A container-only change: Trivy reports high, nothing critical.
    image_bump = {
        "description": "Bump base image to pick up upstream patches",
        "affected_paths": ["Dockerfile"],
        "resources": [],
    }
    permissive_gate = SecurityGate(agent, policy={"allow_high_risk": True})

    strict_result = await strict_gate.evaluate(image_bump)
    permissive_result = await permissive_gate.evaluate(image_bump)

    print(f"  risk level (both gates): {strict_result['risk']['risk_level']}")
    print(
        f"  allow_high_risk=False -> "
        f"{strict_result['decision'].upper()} ({strict_result['reason']})"
    )
    print(
        f"  allow_high_risk=True  -> "
        f"{permissive_result['decision'].upper()} ({permissive_result['reason']})"
    )

    print(
        "\nSame analysis, same risk level, different decision. That is the "
        "separation the\nchapter argues for: policy thresholds move without "
        "touching analysis logic."
    )


if __name__ == "__main__":
    asyncio.run(main())
