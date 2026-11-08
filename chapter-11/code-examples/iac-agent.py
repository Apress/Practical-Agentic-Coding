"""
Module: Infrastructure as Code Agent
Concept: The agent as a reasoning layer on top of infrastructure MCP servers
Chapter Reference: Section 11.4

Section 11.4 makes one argument: you do not build infrastructure tooling from
scratch. AWS, HashiCorp, and Microsoft already publish MCP servers that
expose their APIs as agent tools. The agent's job is to read your application
code, decide what infrastructure it needs, and call the right MCP tools.

This script shows that split:
- analyze_and_provision reads a project's signals and calls MCP tools
- analyze_drift correlates each drift item with episodic memory before deciding
- Risk drives the response: low-risk drift auto-reverts, high-risk escalates

The MCP client here is a recording fake (FakeMCPClient) so the script runs with
no AWS account and no servers installed. Every AWS call it records is a real
tool on a real server. The Terraform `plan` call stands in for running
`terraform plan -detailed-exitcode`; the Terraform MCP server has no plan tool
(on HCP Terraform, create_run with run_type plan_only, then
get_plan_json_output, is the closest match). The mcpServers block below is
the configuration you would use.

MCP servers referenced (see github.com/aws/agent-toolkit-for-aws and the
HashiCorp docs for the current tool lists):
- aws: the managed AWS MCP Server from the Agent Toolkit for AWS, bridged
  locally by the mcp-proxy-for-aws package. Its API tools center on
  aws___run_script, which executes agent-written Python (boto3) in a sandbox
  with AWS API access. The earlier per-service AWS Labs servers (such as
  cfn-mcp-server and its per-resource create_resource tools) are retired: as
  of November 7, 2026, PyPI lists every release as yanked, superseded by
  awslabs.aws-iac-mcp-server. AWS points new work at the toolkit, so this
  agent targets aws___run_script.
- terraform: HashiCorp's terraform-mcp-server, distributed as a Docker image:
  provider search, modules, workspaces, policy. TFE_TOKEN is needed only for
  the HCP Terraform and Terraform Enterprise features.
"""

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional


# The configuration a reader drops into their agent's MCP settings. The agent
# code below assumes these two servers are reachable under these names. The
# mcp-proxy-for-aws version is pinned on purpose: AWS recommends pinning the
# proxy rather than floating on the latest release to limit supply-chain risk.
# Check PyPI for the current version before copying this.
MCP_SERVERS_CONFIG = {
    "mcpServers": {
        "aws": {
            "command": "uvx",
            "args": ["mcp-proxy-for-aws@1.6.4",
                     "https://aws-mcp.us-east-1.api.aws/mcp",
                     "--metadata", "AWS_REGION=us-west-2"],
        },
        "terraform": {
            "command": "docker",
            "args": ["run", "-i", "--rm", "-e", "TFE_TOKEN",
                     "hashicorp/terraform-mcp-server"],
            "env": {"TFE_TOKEN": "${TFE_TOKEN}"},
        },
    }
}


@dataclass
class MemoryRecord:
    """One episodic memory entry: something that happened, and when."""
    summary: str
    occurred_at: datetime
    actor: str = "unknown"


class SimpleEpisodicMemory:
    """
    Stand-in for the episodic store DevMemory provides in Chapter 9.

    Keyword matching replaces vector similarity so the example has no
    dependencies. The interface matches what Section 11.4 calls: search_memory
    with memory_types=["episodic"].
    """

    MIN_OVERLAP = 2  # shared query terms a record needs before it counts as a match

    def __init__(self, records: Optional[list[MemoryRecord]] = None) -> None:
        self.records = records or []

    async def search_memory(
        self, query: str, memory_types: list[str], limit: int = 3
    ) -> list[MemoryRecord]:
        if "episodic" not in memory_types:
            return []
        terms = {t for t in self._tokenize(query) if len(t) > 2}
        if not terms:
            return []
        scored = []
        for record in self.records:
            record_terms = set(self._tokenize(record.summary))
            overlap = len(terms & record_terms)
            # One shared word (often just the "aws" in a resource type) is
            # not evidence. This floor plays the part of a vector store's
            # similarity cutoff.
            if overlap >= self.MIN_OVERLAP:
                scored.append((overlap, record))
        scored.sort(key=lambda pair: (pair[0], pair[1].occurred_at), reverse=True)
        return [record for _, record in scored[:limit]]

    async def remember_session(
        self, session_type: str, summary: str, outcome: str, project: str
    ) -> None:
        self.records.append(
            MemoryRecord(summary=f"{summary} ({outcome})", occurred_at=datetime.now())
        )

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        cleaned = "".join(ch.lower() if ch.isalnum() else " " for ch in text)
        return cleaned.split()


class FakeMCPClient:
    """
    Records the MCP calls an agent would make, and returns plausible shapes.

    Replace this with a real MCP client (any MCP-capable harness gives you one)
    and the agent code above it does not change. That is the point of the tool
    layer: the servers know how to talk to the cloud, the agent knows what to ask
    for.
    """

    def __init__(self) -> None:
        self.calls: list[tuple[str, str, dict[str, Any]]] = []

    async def call(self, server: str, tool: str, args: dict[str, Any]) -> Any:
        self.calls.append((server, tool, args))
        await asyncio.sleep(0.02)

        if tool == "aws___run_script":
            # The real AWS MCP Server executes the agent-written script in a
            # sandboxed environment with AWS API access and returns its output.
            return {"status": "success", "output": "script executed in sandbox"}
        if tool == "plan":
            # Shape of `terraform plan -detailed-exitcode` reduced to drift items.
            return {
                "exit_code": 2,
                "drift": [
                    {
                        "resource": "aws_security_group.db_access",
                        "change": "ingress rule removed",
                    },
                    {
                        "resource": "aws_rds_cluster.main",
                        "change": "backup_retention changed 7 -> 3",
                    },
                ],
            }
        raise ValueError(f"FakeMCPClient has no stub for {server}.{tool}")


class IaCAgent:
    """
    Reasoning layer over infrastructure MCP servers.

    The MCP servers know how to create a CloudFormation stack or run a Terraform
    plan. This agent knows what the application needs and how risky a given
    change is, which is the part no server can tell you.
    """

    # Application signal -> the boto3 provisioning script the agent hands to
    # the AWS MCP Server's sandbox (aws___run_script). In production the model
    # writes these scripts; a lookup keeps the example deterministic. Extend
    # this map as you add signals; the agent's reasoning lives here, not in
    # the MCP server.
    PROVISION_SCRIPTS = {
        "postgresql": (
            "import boto3\n"
            "rds = boto3.client('rds')\n"
            "rds.create_db_instance(\n"
            "    DBInstanceIdentifier='app-db-01',\n"
            "    Engine='postgres',\n"
            "    DBInstanceClass='db.t3.micro',\n"
            "    AllocatedStorage=20,\n"
            "    StorageEncrypted=True,\n"
            ")\n"
        ),
        "redis-cache": (
            "import boto3\n"
            "ec = boto3.client('elasticache')\n"
            "ec.create_replication_group(\n"
            "    ReplicationGroupId='user-sessions',\n"
            "    ReplicationGroupDescription='Session store: primary plus replica',\n"
            "    Engine='redis',\n"
            "    CacheNodeType='cache.t3.medium',\n"
            "    NumCacheClusters=2,\n"
            "    AutomaticFailoverEnabled=True,\n"
            ")\n"
        ),
        "container-runtime": (
            "import boto3\n"
            "ecs = boto3.client('ecs')\n"
            "ecs.create_service(\n"
            "    serviceName='app-service',\n"
            "    launchType='FARGATE',\n"
            "    desiredCount=2,\n"
            ")\n"
        ),
    }

    # Resource name fragments that make a drift item high risk. A security group
    # change can cut production traffic; a tag change cannot.
    HIGH_RISK_FRAGMENTS = ("security", "iam", "policy", "kms", "role")

    def __init__(self, mcp: FakeMCPClient, memory: SimpleEpisodicMemory) -> None:
        self.mcp = mcp
        self.memory = memory

    async def analyze_and_provision(self, project_dir: Path) -> dict:
        """Read app code, infer infra needs, call MCP tools."""
        # Step 1: Read application signals
        dockerfile = self._read(project_dir / "Dockerfile")
        requirements = self._read(project_dir / "requirements.txt")

        # Step 2: Infer infrastructure from signals
        needs = []
        if "psycopg2" in requirements:
            needs.append("postgresql")
        if "redis" in requirements:
            needs.append("redis-cache")
        if "FROM node" in dockerfile or "FROM python" in dockerfile:
            needs.append("container-runtime")

        # Step 3: Provision through the AWS MCP Server.
        # aws___run_script runs agent-written Python (boto3)
        # in a sandbox with AWS API access, a better fit for
        # multi-step provisioning than one call per resource.
        for need in needs:
            await self.mcp.call(
                "aws", "aws___run_script",
                {"code": self._provision_script(need)},
            )
        return {"provisioned": needs}

    async def detect_drift(self, workspace: str) -> list[dict]:
        """Ask the Terraform MCP server what has changed outside Terraform."""
        result = await self.mcp.call("terraform", "plan", {"workspace": workspace})
        if result["exit_code"] == 0:
            return []
        return result["drift"]

    async def analyze_drift(self, drift_items: list[dict]) -> list[dict]:
        """Correlate drift with recent changes from memory."""
        analyzed = []
        for item in drift_items:
            resource = item["resource"]
            past = await self.memory.search_memory(
                query=f"{resource} changes", memory_types=["episodic"], limit=3
            )
            risk = "HIGH" if self._is_high_risk(resource) else "LOW"
            cause = past[0].summary if past else "unknown"
            analyzed.append(
                {
                    "resource": resource,
                    "change": item.get("change", ""),
                    "risk": risk,
                    "likely_cause": cause,
                    "action": "escalate" if risk == "HIGH" else "auto-revert",
                }
            )
        return analyzed

    async def remediate_drift(self, analyzed: list[dict]) -> list[dict]:
        """
        Apply the graduated autonomy model from Section 11.1.

        Low-risk drift reverts on its own. High-risk drift goes to the blackboard
        (Chapter 10) with the likely cause attached, so the human reviewing it
        starts from an explanation rather than a mystery.
        """
        outcomes = []
        for item in analyzed:
            if item["action"] == "auto-revert":
                outcomes.append(
                    {
                        "resource": item["resource"],
                        "result": "reverted",
                        "detail": "Low risk, reverted to declared state",
                    }
                )
                await self.memory.remember_session(
                    session_type="drift_remediation",
                    summary=f"{item['resource']} auto-reverted",
                    outcome="success",
                    project="infrastructure",
                )
            else:
                outcomes.append(
                    {
                        "resource": item["resource"],
                        "result": "escalated",
                        "detail": (
                            f"High risk. Likely cause: {item['likely_cause']}. "
                            f"Posted to blackboard for human review."
                        ),
                    }
                )
        return outcomes

    def generate_terraform(self, purpose: str) -> str:
        """
        Emit Terraform with the reasoning attached.

        Section 11.4 argues agent-generated infrastructure should always carry
        the reasoning behind the choice, because that is what makes the human
        review fast: the reviewer checks the assumptions instead of
        reverse-engineering intent from resource types.
        """
        if "session" in purpose.lower() or "key-value" in purpose.lower():
            return (
                f'# Agent-generated Terraform for "{purpose}"\n'
                'resource "aws_elasticache_replication_group" "sessions" {\n'
                '  replication_group_id       = "user-sessions"\n'
                '  description                = "Session store: one primary, one replica"\n'
                '  engine                     = "redis"\n'
                '  node_type                  = "cache.t3.medium"\n'
                "  num_cache_clusters         = 2  # 1 primary + 1 read replica\n"
                "  automatic_failover_enabled = true\n"
                "  port                       = 6379\n"
                "  # Agent reasoning: ephemeral data, key-value access pattern,\n"
                "  # 30-minute TTL, no durable writes needed. Cheaper than RDS\n"
                "  # for this workload.\n"
                "}\n"
            )
        return (
            f'# Agent-generated Terraform for "{purpose}"\n'
            'resource "aws_db_instance" "main" {\n'
            '  engine            = "postgres"\n'
            '  instance_class    = "db.t3.micro"\n'
            "  allocated_storage = 20\n"
            "  storage_encrypted = true\n"
            "  # Agent reasoning: relational access pattern with durability\n"
            "  # requirements, so a managed relational database fits.\n"
            "}\n"
        )

    def _provision_script(self, need: str) -> str:
        try:
            return self.PROVISION_SCRIPTS[need]
        except KeyError:
            raise ValueError(
                f"No provisioning script mapped for '{need}'. Add it to "
                f"PROVISION_SCRIPTS."
            ) from None

    def _is_high_risk(self, resource: str) -> bool:
        return any(fragment in resource.lower() for fragment in self.HIGH_RISK_FRAGMENTS)

    @staticmethod
    def _read(path: Path) -> str:
        return path.read_text() if path.exists() else ""


def build_sample_project(root: Path) -> Path:
    """Write a small project so analyze_and_provision has real files to read."""
    project = root / "sample-app"
    project.mkdir(parents=True, exist_ok=True)
    (project / "Dockerfile").write_text(
        "FROM python:3.12-slim\nCOPY . /app\nCMD [\"python\", \"main.py\"]\n"
    )
    (project / "requirements.txt").write_text(
        "fastapi==0.115.0\npsycopg2-binary==2.9.9\nredis==5.0.8\n"
    )
    return project


async def main() -> None:
    import tempfile

    print("=== IaC Agent: reasoning layer over MCP servers ===\n")

    print("MCP servers this agent expects:")
    print(json.dumps(MCP_SERVERS_CONFIG, indent=2))
    print()

    mcp = FakeMCPClient()
    memory = SimpleEpisodicMemory(
        [
            MemoryRecord(
                summary=(
                    "infra-team modified aws_security_group db_access for the "
                    "VPN migration"
                ),
                occurred_at=datetime.now() - timedelta(hours=2),
                actor="infra-team",
            ),
            # Benign, recurring drift the agent has learned to expect. It
            # names no resource, so it does not match either drift item
            # below: a tag update cannot explain a backup-retention change.
            MemoryRecord(
                summary="cost-allocation automation retags resources nightly",
                occurred_at=datetime.now() - timedelta(days=1),
                actor="finops-bot",
            ),
        ]
    )
    agent = IaCAgent(mcp, memory)

    # ---- 1. Read the app, infer the infrastructure, provision it ------------
    print("1. Reading application signals and provisioning")
    print("-" * 60)
    with tempfile.TemporaryDirectory() as tmp:
        project = build_sample_project(Path(tmp))
        result = await agent.analyze_and_provision(project)

    for need in result["provisioned"]:
        print(f"  inferred need: {need}")

    print("\n  MCP calls the agent made (the boto3 call inside each script):")
    for server, tool, args in mcp.calls:
        detail = next(
            (line.strip().rstrip("(") for line in args["code"].splitlines()
             if ".create_" in line),
            "",
        )
        print(f"    {server}.{tool}({detail})")

    # ---- 2. Semantic understanding: purpose drives the resource choice ------
    print("\n2. Generating Terraform from a stated purpose")
    print("-" * 60)
    print(agent.generate_terraform("store user sessions with fast reads"))

    # ---- 3. Drift: detect, correlate with memory, respond by risk -----------
    print("3. Drift detection with memory-informed analysis")
    print("-" * 60)
    drift = await agent.detect_drift(workspace="production")
    print(f"  terraform plan reported {len(drift)} resource(s) changed outside Terraform")

    analyzed = await agent.analyze_drift(drift)
    for item in analyzed:
        print(f"\n  {item['resource']}")
        print(f"    change:       {item['change']}")
        print(f"    risk:         {item['risk']}")
        print(f"    likely cause: {item['likely_cause']}")
        print(f"    action:       {item['action']}")

    print("\n4. Remediation under graduated autonomy")
    print("-" * 60)
    for outcome in await agent.remediate_drift(analyzed):
        print(f"  {outcome['resource']}: {outcome['result']}")
        print(f"    {outcome['detail']}")

    print(
        "\nWithout memory, every drift item is a mystery. With it, a security "
        "group change made two hours ago explains itself."
    )


if __name__ == "__main__":
    asyncio.run(main())
