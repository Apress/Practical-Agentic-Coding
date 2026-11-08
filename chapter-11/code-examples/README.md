# Chapter 11 Code Examples: quick reference

Runnable Python for the patterns in Chapter 11, "Integrating Agentic Coding with
DevOps and Cloud Infrastructure." Each script covers one pattern from one
section. Each one prints what the agent decided and why.

When to use these patterns and why: Chapter 11, Sections 11.3, 11.4, and 11.5.

> **Update to Section 11.5: Infracost CLI version 2 (as of November 7, 2026).**
> The Infracost CLI that infracost.io, Homebrew, and Chocolatey install is
> version 2. Version 2 replaces `breakdown` with `scan`.
>
> - Version 2 runs `breakdown` as `scan`. `scan` takes a directory, not a plan file.
> - Version 2 drops `--format json`. So `--plan` never gets the JSON report the gate parses, and the gate blocks.
> - A version 2 `scan --json` report uses a different schema. This gate reads it as $0 and approves. Do not pass one with `--breakdown`.
>
> For `--plan`, install the 0.10 CLI (v0.10.47 from
> github.com/infracost/infracost/releases). Or produce the report with the 0.10
> image the workflow pins, and pass it with `--breakdown`:

```bash
docker run --rm -e INFRACOST_API_KEY -v "$PWD:/src" infracost/infracost:ci-0.10.47 \
    breakdown --path /src/terraform/plan.json --format json --out-file /src/infracost.json
python3 cost-guardrails.py --breakdown infracost.json --budgets .github/budget-limits.json
```

> **Update to Section 11.5: action versions (as of November 7, 2026).** The
> book's sketch uses `actions/checkout@v4`. GitHub's hosted runners do not run
> Node 20 actions. `github-actions-gates.yml` uses the current Node 24 major of
> every action. Its header comment explains the pinning choices.

## Prerequisites

- Python 3.11 or later.
- No external services and no API key. Scanner subprocesses, MCP calls, model
  calls, and cloud APIs are simulated. Every script runs offline.

```bash
cd chapter-11/code-examples
python3 self-healing-pipeline.py   # on Windows: py self-healing-pipeline.py
```

`requirements.txt` lists only optional development extras. You do not need to
install anything to run these.

Optional tools, only if you point an example at real infrastructure:

- `infracost` for the cost gate.
- Docker and Terraform for the CI workflow.

`github-actions-gates.yml` is meant for a real pipeline, not a local run. It
needs credentials. The header comment lists them.

## What maps to what

| Script | Book section | What it shows |
|--------|--------------|---------------|
| `self-healing-pipeline.py` | 11.3 Self-Healing Pipelines | Memory-first failure classification. Successes go to semantic memory, failures to episodic memory |
| `iac-agent.py` | 11.4 Infrastructure as Code with MCP Tools | An agent over the AWS MCP Server (Agent Toolkit for AWS) and the Terraform MCP server, with memory-informed drift analysis |
| `security-gates.py` | 11.5 Security and Cost Gates | `SecurityComplianceAgent` scanner routing (ASH, Trivy, Bandit, npm audit) and the `SecurityGate._apply_policy` chain |
| `cost-guardrails.py` | 11.5 Security and Cost Gates | `CostGuardrails` budget gate over an Infracost breakdown. It returns approve, warn, or block |
| `github-actions-gates.yml` | 11.5 Security and Cost Gates | The production workflow that wires both gates into CI |
| `fixtures/` | Supports 11.5 | A sample Infracost payload and example budget limits, so the cost gate runs with nothing installed |
| `finops-agent.py` | Bonus, extends 11.5 | Cost analysis, rightsizing recommendations, budget forecasting |
| `predictive-scaling.py` | Bonus, extends 11.5 | Reactive, predictive (trend), and scheduled scaling checks over a simulated 08:00 to 10:00 window. With the bundled traffic model, the business-hours schedule fires at 09:00. The load stays inside the 30-70% band, so the predictive and reactive triggers stay quiet |
| `multi-cloud-orchestrator.py` | Bonus, extends 11.7 | Cross-cloud deployment coordination and failover |

Sections 11.1 and 11.2 have no code here. Section 11.6's Zero-Downtime Deployer
and Section 11.7's multi-service extension live in `../hands-on-lab/`.

## What each script prints

### self-healing-pipeline.py

1. It handles the same failure twice and prints both timings side by side. The
   first pass classifies through the model. The second reads the answer from
   semantic memory.
2. It runs a mixed batch of four failures against a seeded memory.
3. It reports the fast-path ratio.

Where to look in the code:

- `classify_failure` checks memory first.
- A 0.8 confidence threshold picks the fast path or the slow path.
- `learn_from_incident` writes successes to semantic memory and failures to episodic memory.

### iac-agent.py

1. It prints the `mcpServers` configuration the agent expects.
2. It reads a sample project's `Dockerfile` and `requirements.txt`, infers the
   infrastructure, and shows every MCP tool call it makes.
3. It runs drift detection on two drifted resources. It checks each one against
   episodic memory. It auto-reverts one and escalates the other, based on risk.

The printed configuration is the Agent Toolkit for AWS setup from Section 11.4:

- The managed AWS MCP Server, bridged locally by `mcp-proxy-for-aws`.
- HashiCorp's Terraform MCP server, run from its Docker image.

Provisioning goes through `aws___run_script`. It runs agent-written boto3
scripts in a sandbox with AWS API access. The proxy version in the config is
pinned on purpose. Check PyPI for the current `mcp-proxy-for-aws` release before
you copy it.

The MCP client is a recording fake. Swap in a real MCP client, and the agent
code above it does not change. One exception: the drift check's `plan` call
stands in for running `terraform plan -detailed-exitcode`. The Terraform MCP
server has no plan tool.

### security-gates.py

It runs three cases through the same `SecurityComplianceAgent`:

1. A change touches application code, Terraform, and a Dockerfile. Scanners
   fire. One finding is critical. The gate blocks.
2. The same finding patterns sit in test paths. Contextual assessment downgrades
   them (a fixture credential is not a live secret). The gate approves.
3. Two gates with different policies evaluate one assessment. The risk level is
   the same. The decisions differ.

### cost-guardrails.py

This is the pipeline cost gate. It is a different script from `finops-agent.py`.
It runs before `terraform apply`. It blocks a change whose projected monthly
cost breaks the budget.

What it does:

1. It wraps `infracost breakdown --path <plan> --format json`.
2. It sorts resources into budget categories: compute, storage, database, network.
3. It compares the monthly delta and each category against limits.
4. It returns a decision with the reasoning attached.

Before you use `--plan`, read the Infracost version 2 note at the top of this file.

```bash
# Demo. Uses the bundled sample in fixtures/, so it runs with nothing installed.
python3 cost-guardrails.py

# Against a real plan, if you have infracost installed
python3 cost-guardrails.py --plan terraform/plan.json --budgets .github/budget-limits.json

# In CI, where an earlier step already produced the Infracost report
python3 cost-guardrails.py --breakdown infracost.json \
    --budgets .github/budget-limits.json --json cost-decision.json
```

The demo prints three scenarios: fits the budget, breaks the budget, and no
estimator available. Then it prints the machine-readable decision a pipeline
reads.

Exit codes:

| Code | Meaning |
|------|---------|
| `0` | Approve or warn |
| `1` | Block |
| `2` | Bad usage |

Behavior to know:

- `check_deployment` answers one question: does this fit the budget? `evaluate`
  decides what the pipeline does about it.
- A missing estimator returns a decision. It does not crash. The default is to
  fail closed. `--fail-open` warns and lets the deployment through.
- Infracost returns usage-based resources with `monthlyCost: null` until you
  supply a usage file. The gate reports them as unpriced. It does not count
  them as free.
- Every decision records `estimate_source`. This keeps the bundled sample from
  being mistaken for a real estimate.
- The reserved `total` budget key caps the whole plan. Every other key caps one
  category. Categories with no limit are reported but not enforced. The
  decision notes say so.

### github-actions-gates.yml

This is the production version of the workflow the book sketches in about 25
lines. Install it in your own repository:

```bash
cp github-actions-gates.yml /path/to/repo/.github/workflows/agentic-quality-gates.yml
cp cost-guardrails.py /path/to/repo/scripts/cost_gate.py
cp fixtures/budget-limits.json /path/to/repo/.github/budget-limits.json
```

Then edit the budget limits. Add the secrets listed at the top of the workflow
file.

What it adds over the printed version:

- **Docker setup.** Trivy and Infracost run from pinned images. A scanner
  release cannot change a gate verdict overnight. The same commands work on a
  self-hosted runner.
- **Authentication.** Set `AUTH_MODE` to one of three options:
  - An API key from secrets.
  - AWS workload identity federation into Amazon Bedrock.
  - Google Cloud workload identity federation into Vertex AI.

  A personal subscription login is never an option. CI needs a credential a
  platform team can rotate and audit. Usage is billed to the credential a run
  uses. A personal login would put pipeline spend on one developer's plan. The
  workflow fails the job if it finds interactive login credentials on the
  runner.
- **Error handling on every gate.**
  - A scanner that fails to run fails the gate.
  - Agent output that cannot be parsed blocks the change.
  - A missing cost estimate fails closed.
- **Conditional execution.** A `change-scope` job classifies the diff. A
  docs-only pull request skips both deep gates. Deployment runs only on `main`,
  and only when no in-scope gate failed.
- **Artifact upload for the audit trail.** Each gate writes a decision record
  with the commit and run ID. The summary job combines them and comments on the
  pull request. It keeps the bundle for 90 days.
- **Current action versions.** See the action versions note at the top of this
  file.
- **Fast and deep gates.** Secret detection and dependency checks run on every
  push in seconds. The full security scan and cost estimate run on pull
  requests that target `main`.

## Adapting these for real use

Each script marks its simulation boundary in a docstring or comment. To turn one
into production code:

1. Replace the simulated call with the real one:
   - `asyncio.create_subprocess_exec` for scanners.
   - A real MCP client for `FakeMCPClient`.
   - Your model client for the `_llm_*` stand-ins.
2. Swap the in-memory `SimpleDevMemory` / `SimpleEpisodicMemory` for the memory
   system from Chapter 9, which persists to a vector store.
3. Add the error handling and retry logic the examples leave out.
4. Widen the mapping tables to cover your stack: `PROVISION_SCRIPTS`,
   `SCANNER_BY_SUFFIX`, `STRATEGIES`, and `CATEGORY_RULES`. These tables are
   meant to be edited.

Most of this code is simplified. Error handling is thin, and nothing persists
between runs. Two files are closer to production-ready:

- `cost-guardrails.py` parses real Infracost output and handles a missing estimator.
- `github-actions-gates.yml` is a workflow you can install as-is.

Review the policy thresholds and the auth mode before you rely on either.

## Reproducible output

Some examples use randomness. For identical output every time, set a seed at the
top of a file (`random.seed(42)`). `cost-guardrails.py` is deterministic. The
same breakdown and the same budgets always produce the same decision.

## Troubleshooting

**The cost gate reports `estimate_source: fixture`.** Infracost is not on your
PATH, so the gate used the bundled sample. Install the 0.10 CLI (see the
Infracost note at the top of this file) before you trust the numbers. Or pass
`--fixture ''` to make a missing estimator a hard failure.

**The cost gate blocks when you expected an approval.** Check the budget file.
The reserved `total` key caps the whole plan. Every other key caps one category.
The decision notes list any category with no limit. Those are reported but not
enforced.

**The workflow's cost gate fails with "scripts/cost_gate.py is missing".** Copy
`cost-guardrails.py` into your repository at that path. The workflow keeps the
policy script in the repository under test. It does not fetch it at run time.
So a gate cannot change behavior without a reviewed commit.

## Related

- Chapter 11 hands-on lab: `../hands-on-lab/`
- Chapter 9 for the memory system these examples simplify
- Chapter 10 for the blackboard the drift and gate agents escalate through
