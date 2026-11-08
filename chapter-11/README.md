# Chapter 11: Integrating Agentic Coding with DevOps and Cloud Infrastructure

Code examples, hands-on lab, and challenge lab for Chapter 11.

> **Update to Section 11.2 (as of November 7, 2026).**
>
> - Amazon DevOps Guru stopped accepting new customers on October 29, 2026. It reaches end of support on September 30, 2027. AWS points anomaly detection to Amazon CloudWatch. It points AI-assisted investigation to AWS DevOps Agent, which is generally available. See the [DevOps Guru end-of-support notice](https://docs.aws.amazon.com/devops-guru/latest/userguide/devops-guru-end-of-support.html).
> - Microsoft archived the AI Shell project in January 2026 and does not maintain it. Azure Copilot runs in the Azure portal and the Azure mobile app ([Azure Copilot overview](https://learn.microsoft.com/en-us/azure/copilot/overview)).
> - Sentry's MCP server searches each dataset with its own tool: `search_errors`, `search_logs`, `search_traces`, `search_metrics`, `search_profiles`, and `search_replays`. The `search_events` tool that Section 11.2 names remains only as a deprecated alias. It does not appear in the tool list. `search_issues` is unchanged ([Sentry changelog](https://sentry.io/changelog/), [toolkit pull request](https://github.com/getsentry/toolkit/pull/1374)).

## What's here

| Directory | What it is | Book section |
|-----------|-----------|--------------|
| `code-examples/` | Standalone Python scripts for the chapter's patterns. Each one runs on its own. | 11.3, 11.4, 11.5 |
| `hands-on-lab/` | The Zero-Downtime Deployer you build. It covers canary deploy, health validation, progressive traffic shift, and automatic rollback. | 11.6 |
| `hands-on-lab/challenge-lab/` | Open-ended extension. Deploy several services and roll them back in reverse dependency order. | 11.7 |

## Directory structure

```text
chapter-11/
├── README.md                        # This file
├── code-examples/                   # Patterns from the chapter sections
│   ├── README.md
│   ├── self-healing-pipeline.py     # 11.3: memory-first failure classification
│   ├── iac-agent.py                 # 11.4: IaC via MCP tools + drift analysis
│   ├── security-gates.py            # 11.5: SecurityComplianceAgent + SecurityGate
│   ├── cost-guardrails.py           # 11.5: budget gate on a Terraform plan
│   ├── github-actions-gates.yml     # 11.5: wiring the gates into CI/CD
│   ├── fixtures/                    # Sample Infracost payload + budget limits
│   ├── finops-agent.py              # Bonus: cost analysis and rightsizing
│   ├── predictive-scaling.py        # Bonus: predictive autoscaling
│   ├── multi-cloud-orchestrator.py  # Bonus: cross-cloud failover
│   └── requirements.txt
└── hands-on-lab/                    # Zero-Downtime Deployer (Section 11.6)
    ├── README.md                    # Setup and instructions, start here
    ├── docker-compose.yml           # Optional Prometheus + Grafana + mock API
    ├── prometheus.yml               # Scrape config for the above
    ├── requirements.txt
    ├── .env.example                 # Configuration template
    ├── verify_setup.py              # Prerequisite check
    ├── starter/                     # Your working copy, with TODOs
    │   ├── deployer.py              # The TODOs you complete
    │   ├── config.py                # Settings loaded from .env
    │   ├── infrastructure_client.py # Deploy/traffic operations (ready to use)
    │   ├── health_monitor.py        # Metric collection (ready to use)
    │   ├── memory_integration.py    # Simplified deployment memory (ready to use)
    │   └── tests/                   # Tests that check your implementation
    ├── complete/                    # Reference solution, same structure
    ├── exercises/                   # Step-by-step exercise guides
    ├── integrations/                # Optional Sentry, Prometheus, Grafana wiring
    ├── challenge-lab/               # Multi-service deployment (Section 11.7)
    └── data/memory/                 # Where your deployment memory persists
                                     # (tests use per-test temp dirs instead)
```

## Section map

| Section | Topic | Where the code is |
|---------|-------|-------------------|
| 11.1 | The shift from CI/CD to CA/CD | Conceptual (no code) |
| 11.2 | The AI DevOps ecosystem: what already exists | Conceptual (tool survey) |
| 11.3 | Self-healing pipelines | `code-examples/self-healing-pipeline.py` |
| 11.4 | Infrastructure as Code with MCP tools | `code-examples/iac-agent.py` |
| 11.5 | Security and cost gates in the pipeline | `code-examples/security-gates.py`, `cost-guardrails.py`, `github-actions-gates.yml` |
| 11.6 | Hands-on lab: Zero-Downtime Deployer | `hands-on-lab/` |
| 11.7 | Challenge lab: multi-service deployment | `hands-on-lab/challenge-lab/` |

## Go further with AI DevOps tools

These capabilities build on Chapter 11. Plans, pricing, and availability change. Each item links to the vendor page with current details.

- **Seer Agent with Grafana.** Seer Agent investigates problems in Sentry from natural-language questions. After you link a Grafana account, it correlates your Sentry errors, traces, and logs with Grafana telemetry. Introduced in November 2026. [Sentry changelog](https://sentry.io/changelog/)
- **CodeRabbit CLI severity gate.** `cr review --gate major` exits with code 2 when the review finds a major or critical issue. A pipeline step can then fail on review results like any other quality gate. Introduced in CodeRabbit CLI v0.9.1 (October 2026). [CodeRabbit changelog](https://docs.coderabbit.ai/changelog)
- **CodeRabbit Security merge check.** On GitHub Cloud, admins can publish a CodeRabbit Security check with a severity threshold. Once you make that check required in GitHub, it blocks merges while Security comments are unresolved. Introduced in October 2026. [CodeRabbit changelog](https://docs.coderabbit.ai/changelog)
- **CodeRabbit Fix comments and Autofix.** Fix comments (`@coderabbitai fix comments`) fixes the review comments you pick. Autofix works a coding agent's pull request through review feedback and failing CI to completion. Introduced in October 2026. At that time CodeRabbit renamed its earlier Autofix to Fix comments and its earlier Autopilot to Autofix. [CodeRabbit changelog](https://docs.coderabbit.ai/changelog)
- **AWS Continuum for code vulnerabilities.** Finds code vulnerabilities. It checks in an isolated sandbox whether each one is exploitable, ranks findings by business impact, and opens fix pull requests. It starts in Learn mode, where you approve each fix. Once it shows enough precision, it can move to Enforce mode, where it acts within guardrails you set. Consider it when you decide whether to adopt or build your security gate. Introduced in October 2026. [AWS announcement](https://aws.amazon.com/about-aws/whats-new/2026/10/aws-continuum-for-code-vulnerabilities-is-now-generally-available)

## Quick start

### Code examples

Every script runs standalone on Python 3.11+ with no external services (on Windows, use `py` in place of `python3`):

```bash
cd code-examples
python3 self-healing-pipeline.py
python3 iac-agent.py
python3 security-gates.py
python3 cost-guardrails.py
```

The scanner, MCP, and cloud calls are simulated, so the scripts run anywhere.
`github-actions-gates.yml` is a workflow file. Copy it into `.github/workflows/`
in your own repository.

### Hands-on lab: Zero-Downtime Deployer

You build a deployment agent. It runs a canary, validates health, and shifts
traffic in stages. It rolls back on its own when a check fails. Memory from past
deployments sets how cautious it is.

**Prerequisites**: Python 3.11+ and Git.

- Docker and an API key are optional.
- You need no Kubernetes cluster. The lab runs against mock infrastructure.

**Time**: about 2 to 4 hours including first-time setup.

Start with [hands-on-lab/README.md](./hands-on-lab/README.md).

### Challenge lab: multi-service deployment

Extend the deployer to three interdependent services: database, API, and
frontend. Deploy them in dependency order. When any one fails, roll all of them
back in reverse order. See [hands-on-lab/challenge-lab/README.md](./hands-on-lab/challenge-lab/README.md).

**Time**: 2-3 hours, on top of the hands-on lab.

## Suggested order

1. Read Chapter 11, Sections 11.1 and 11.2.
2. Run the `code-examples/` scripts alongside Sections 11.3 to 11.5.
3. Build the hands-on lab (Section 11.6).
4. Try the challenge lab (Section 11.7).

## Related chapters

- **Chapter 9**: Agent Memory and Context Models. This lab's deployment memory is a simplified version of the Chapter 9 memory system.
- **Chapter 10**: Orchestrating Multiple AI Agents. The drift and gate agents escalate through its coordination and blackboard patterns.
- **Chapter 12**: Security, Privacy, and Ethical Considerations. It covers safety for agents that hold infrastructure access.
