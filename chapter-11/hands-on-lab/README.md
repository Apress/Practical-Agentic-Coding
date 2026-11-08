# Hands-On Lab: Building a Zero-Downtime Deployer

This is the lab for **Chapter 11, Section 11.6**. You build the deployment agent
from that section. It runs a canary, validates health, and shifts traffic in
stages. It rolls back on its own when a check fails. Past deployment history
sets how cautious it is with each service.

Why the deployer works this way: Chapter 11, Section 11.6.

## Coming from the book?

The chapter shows the lab in an idealized form. This repository is the
runnable version. Run everything from this `hands-on-lab/` directory.

- `python verify_setup.py` checks your setup.
- `pytest starter/tests/ -v` runs the test suite. Seven of its sixteen tests fail on purpose before you start. Those failures define Exercises 1 and 2.
- `pytest complete/tests/ -v` shows the reference solution passing all sixteen.
- Docker is optional. `docker compose up -d` starts the Prometheus/Grafana extras in Step 5 below. Every exercise runs against mock infrastructure without it.

How the chapter's illustrative listing maps onto this repository:

| The book's listing | In this repo |
|---------------|--------------|
| `pytest tests/test_deployer.py -v` (the "Testing the deployer" listing, two illustrative tests) | `pytest starter/tests/test_deployer.py -v` (or `complete/tests/...` for the solution). The repo suite is fuller than the book's two-test excerpt. |
| `test_successful_deployment`, `test_automatic_rollback` | `test_full_deployment_flow` and `test_automatic_rollback_on_validation_failure` in `test_deployer.py` cover the same two cases. |
| `mock_infra.set_healthy(False)` | Deploy a version whose name contains `bad` (for example `2.0.0-bad`). The mock reports failing metrics for it. |
| `from zero_downtime_deployer.deployer import ...` | `from starter.deployer import ...` (your working copy) or `from complete.deployer import ...` (the solution). The book's idealized `zero_downtime_deployer` package ships here as the `starter/` and `complete/` packages, same modules inside. |
| `ZeroDowntimeDeployer(memory, infrastructure_client)` | Same order. The repo adds `health_monitor` and `traffic_stabilization_seconds`, which the tests pass by keyword. |
| `self.memory.search_memory(query=..., memory_types=["episodic"], limit=5)`, results read as `f.summary` | `self.memory.recall(query=..., n_results=5)`, which returns a dict of lists (`{"episodic": [...], "semantic": [], "procedural": []}`). The lab's `DeploymentMemory` is a simplified, file-based stand-in for the Chapter 9 memory. |
| The memory check and the 60s to 180s canary extension at the top of `deploy()` | Inside `validate_canary()` (Exercise 1), which `deploy()` calls. |
| Rollback "queries memory for the last known-good version" | `rollback()` takes the version still serving the most traffic from the infrastructure client's live deployment list, then records the rollback in memory so the next deployment can use it. |

## What you do

You work in `starter/`. Four modules are ready to use: `config.py`,
`infrastructure_client.py`, `health_monitor.py`, and `memory_integration.py`.
The TODOs you complete are in `starter/deployer.py`:

- **Exercise 1**: `validate_canary()`. Validate health against thresholds.
  Query memory for past trouble with this service.
- **Exercise 2**: `rollback()`. Find the last known-good version, shift traffic
  back, and record the failure.
- **Exercise 3** (optional): Wire in Sentry, so error rates come from a real
  error-tracking service instead of the mock.

`complete/` holds the reference solution with the same layout. Write your own
first. Check it when you are stuck.

## Learning Objectives

By completing this lab, you will:
- Implement canary deployment with progressive traffic shifting
- Build health validation logic with error threshold detection
- Create automatic rollback triggers based on metrics
- Integrate memory-based decision making (from Chapter 9)
- Connect with Sentry for real-world error tracking (optional)
- Apply CA/CD (Continuous Agentic Delivery) patterns

## Time Required

- **Setup** (first time): 15-30 minutes, plus the Docker install if you want the optional extras
- **Exercise 1** (canary validation): 45-60 minutes
- **Exercise 2** (automatic rollback): 35-50 minutes
- **Exercise 3** (Sentry integration, optional): 30-75 minutes

**Total**: about 2 to 4 hours including setup.

## Prerequisites

### Required

| Tool | Version | Purpose | Installation |
|------|---------|---------|--------------|
| **Python** | 3.11+ | Everything in the lab | [Download](https://www.python.org/downloads/) |
| **Git** | Any recent | Clone the repository | [Download](https://git-scm.com/downloads) |

### Optional

| Tool or service | What it adds | Where |
|-----------------|--------------|-------|
| **Docker Desktop** | The optional Prometheus and Grafana stack (Step 5); a local Kubernetes cluster if you take on the real-cluster extension in Next Steps | [docker.com](https://www.docker.com/products/docker-desktop/) |
| **kubectl** | The real-cluster extension only (ships with Docker Desktop) | Included with Docker Desktop |
| **Sentry** | Real error rates in Exercise 3 (free tier is enough) | [sentry.io](https://sentry.io/signup/) |

### Knowledge Prerequisites

From the book:
- **Chapter 9**: Agent Memory and Context Models (the memory system this lab simplifies)
- **Chapter 10**: Orchestrating Multiple AI Agents (coordination patterns)
- **Chapter 11, Sections 11.1 to 11.5**: the CA/CD model, the tool landscape, self-healing pipelines, IaC via MCP, and the gate patterns

## Setup Instructions

### Step 1: Clone the Repository

```bash
git clone https://github.com/Apress/Practical-Agentic-Coding.git
cd Practical-Agentic-Coding/chapter-11/hands-on-lab
```

### Step 2: Kubernetes (skip this)

The lab runs against **mock infrastructure** (`USE_MOCK_INFRASTRUCTURE=true` in
`.env`). The mock simulates deployments, traffic shifting, and metrics. You do
not need a cluster for any exercise or test. Keep the default and go to Step 3.

There is no real-cluster mode to switch on yet. Setting
`USE_MOCK_INFRASTRUCTURE=false` only loads your kubeconfig. Every method in
`infrastructure_client.py` still returns mock results. Each one marks where the
real Kubernetes call goes. Wiring those methods up is an extension (see Next
Steps). If you take it on:

1. Enable Kubernetes in Docker Desktop: **Settings**, then **Kubernetes**, then **Enable Kubernetes**.
2. Confirm the cluster answers before you write any code:

```bash
kubectl cluster-info
```

### Step 3: Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**What gets installed**:
- `pytest`, `pytest-asyncio`, `pytest-cov` - the test suite that checks your work
- `python-dotenv` - reads your `.env`
- `kubernetes` - only imported when you switch off mock mode, and then only to load your kubeconfig
- `sentry-sdk` - only needed for Exercise 3
- `anthropic` - not used by the exercises. It is there if you extend the deployer with your own model calls

All pins are bounded to tested major versions. The install behaves the same
whenever you run it.

### Step 4: Configure Environment

```bash
cp .env.example .env
```

The defaults work for every exercise. To change the deployment behavior, open
`.env`:

```env
CANARY_PERCENTAGE=10                 # Initial canary traffic share
VALIDATION_DURATION_SECONDS=300      # How long to watch the canary
TRAFFIC_STABILIZATION_SECONDS=30     # Pause after each traffic shift
ERROR_RATE_THRESHOLD=0.01            # Rollback above 1% errors
USE_MOCK_INFRASTRUCTURE=true         # Keep true unless you have a cluster
```

**No API key is required.** The exercises run against mock infrastructure.
Nothing calls a paid API.

**Optional (for Exercise 3 only)**:
```env
SENTRY_DSN=https://...   # From your Sentry project settings
SENTRY_ENVIRONMENT=lab
```

### Step 5: Start Local Infrastructure (optional)

The exercises do not need this. It starts Prometheus and Grafana, so you can
explore them next to the lab. The deployer does not export metrics yet. There
is nothing of the deployer's to watch until you add an exporter.
`integrations/grafana_dashboards/README.md` lists the metrics the dashboards
expect.

```bash
docker compose up -d
docker compose ps
```

This starts three services:

- A mock API service on port 5678.
- Prometheus on 9090.
- Grafana on 3000. It has anonymous admin access and no login, so keep it on your own machine.

Prometheus lists the mock API target as down. That is expected: http-echo
answers with plain text, not metrics.

### Step 6: Verify Setup

```bash
python verify_setup.py
```

Required checks must pass. Optional checks print `[SKIP]` when the tool is
absent. That is fine. Here is abridged output on a machine with only Python.
Each `[SKIP]` line is followed by a one-line note:

```text
Required for the exercises:
----------------------------------------
[PASS] Python 3.11+ installed
[PASS] Python dependencies installed
[PASS] Environment file (.env) exists
[PASS] Starter files present

Optional extras:
----------------------------------------
[SKIP] Docker running (optional)
[SKIP] Lab services running (optional)
[SKIP] Kubernetes cluster reachable (optional)
[SKIP] Anthropic API key set (optional)

Setup complete. Ready to start the exercises.
```

If you have not run `cp .env.example .env` yet, the `.env` check prints
`[FAIL]` and the script exits with code 1.

## Lab Structure

```text
hands-on-lab/
├── README.md                          # This file
├── docker-compose.yml                 # Local mock infrastructure
├── prometheus.yml                     # Prometheus scrape config
├── requirements.txt                   # Python dependencies
├── .env.example                       # Configuration template
├── verify_setup.py                    # Setup verification script
│
├── starter/                           # Your working directory
│   ├── README.md                      # Module-by-module API reference
│   ├── config.py                      # Settings from .env (ready to use)
│   ├── deployer.py                    # Main deployer (TODOs to complete)
│   ├── infrastructure_client.py       # Deploy and traffic ops (ready to use)
│   ├── health_monitor.py              # Metric collection (ready to use)
│   ├── memory_integration.py          # Simplified deployment memory (ready to use)
│   └── tests/
│       ├── test_deployer.py           # Unit tests for your methods
│       └── test_integration.py        # End-to-end tests
│
├── complete/                          # Reference solution, same structure
│
├── exercises/                         # Step-by-step guides
│   ├── README.md                      # How to work through them
│   ├── exercise-1-canary.md           # Canary validation
│   ├── exercise-2-rollback.md         # Automatic rollback
│   ├── exercise-3-sentry.md           # Sentry integration (optional)
│   ├── QUICK_REFERENCE.md             # API cheat sheet, keep it open
│   └── VISUAL_OVERVIEW.md             # One-page diagram of the system
│
├── integrations/                      # Optional third-party wiring
│   ├── README.md                      # Guide to this directory
│   ├── INDEX.md                       # Shorter navigation guide
│   ├── sentry_integration.py          # SentryMonitor scaffold with TODOs
│   ├── test_sentry_connection.py      # Checks your DSN works
│   ├── sentry_setup.md                # Account and project setup
│   ├── observability_setup.md         # How the stack fits together
│   ├── grafana_setup.md               # Optional dashboards
│   └── grafana_dashboards/            # Importable dashboard JSON
│
├── challenge-lab/                     # Section 11.7: multi-service deployment
│
└── data/memory/                       # Where deployment memory persists
```

## Key APIs Reference

You use these ready-to-use modules in the exercises:

### Health Monitor API
```python
# Collect metrics
metrics = await health_monitor.collect_metrics(service_name, version)
# Returns: {"error_rate": 0.005, "latency_p99": 245, "cpu_usage": 0.65, ...}

# Check health against thresholds
result = await health_monitor.check_health(service_name, version, thresholds)
# Returns: {"healthy": True/False, "metrics": {...}, "issues": [...]}
```

### Memory API
```python
# Recall past events
results = await memory.recall(query="deployment failure api-service", n_results=5)
# Returns: {"episodic": [{...}, {...}], "semantic": [], "procedural": []}

# Remember a session
await memory.remember_session(
    session_type="deployment",
    summary="Deployed api-service v2.0.0",
    outcome="success",
    project="api-service"
)
```

### Infrastructure Client API
```python
# List deployments
deployments = await infra.list_deployments(service_name)
# Returns: [{"name": "...", "version": "1.0.0", "traffic_percentage": 90, ...}]

# Set traffic percentage
result = await infra.set_traffic(service_name, version, percentage)
# Returns: {"success": True, "service": "...", "version": "...", ...}
```

See `starter/README.md` for complete API documentation.

## Exercises

Work through the exercises in order:

### Exercise 1: Canary Deployment with Health Validation
**File**: `exercises/exercise-1-canary.md`
**Time**: 45-60 minutes
**Goal**: Implement canary deployment logic with health checking

### Exercise 2: Automatic Rollback
**File**: `exercises/exercise-2-rollback.md`
**Time**: 35-50 minutes
**Goal**: Add automatic rollback based on error thresholds

### Exercise 3: Sentry Integration (Optional)
**File**: `exercises/exercise-3-sentry.md`
**Time**: 30-75 minutes
**Goal**: Integrate real-world error tracking

## Running Tests

Run these from the `hands-on-lab` directory, not from inside `starter/`. The
package imports only resolve from there:

```bash
# Everything
pytest starter/tests/ -v

# Just the exercise you are on
pytest starter/tests/test_deployer.py -v -k canary
pytest starter/tests/test_deployer.py -v -k rollback

# End-to-end
pytest starter/tests/test_integration.py -v

# With coverage
pytest starter/tests/ --cov=starter --cov-report=html
```

Before you start, seven tests fail:

- The three canary tests in `test_deployer.py`.
- The three rollback tests in `test_deployer.py`.
- The failed-deployment integration test.

These failures are expected. Their messages tell you what the TODOs need to do.
When all of `test_deployer.py` passes, Exercises 1 and 2 are done. Run the same
commands against `complete/tests/` to see the reference solution pass all 16.
If a book command does not work for you, see the command map in "Coming from
the book?" at the top of this file.

## Troubleshooting

### Import errors when running pytest

Run pytest from `hands-on-lab/`, not from `starter/`. The tests import
`starter.deployer`. That import only resolves from the parent directory.

```bash
pwd   # should end with /hands-on-lab
pytest starter/tests/ -v
```

If imports still fail, activate the virtual environment:

```bash
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Prometheus or Grafana not reachable from WSL

`docker-compose.yml` publishes Prometheus (9090) and Grafana (3000) on
`127.0.0.1` only. This keeps them off your network. Grafana runs with anonymous
admin access.

This fix applies if you run Docker Desktop on Windows and the lab inside a WSL
distro, and `http://localhost:3000` answers in Windows but not in WSL:

1. Remove the `127.0.0.1:` prefix from the two `ports` entries (`"9090:9090"` and `"3000:3000"`).
2. Run `docker compose up -d` again.

This publishes the ports on every interface. Do it only on a network you trust.

### Tests hang or time out

Two settings control how long a deployment takes. Both default to
production-realistic values in `.env`:

```env
VALIDATION_DURATION_SECONDS=30    # instead of 300
TRAFFIC_STABILIZATION_SECONDS=0   # instead of 30
```

The test fixtures already pass `traffic_stabilization_seconds=0` to the deployer
and short validation windows to `DeploymentConfig`. The supplied suite runs in
about two minutes. If your own runs are slow, check two things:

- You may be hardcoding a sleep instead of reading `self.traffic_stabilization_seconds`.
- You may be passing the `.env` default of 300 as the validation duration.

### Memory is not persisting between runs

The memory file lives at the path in `MEMORY_PERSIST_DIR` (default
`./data/memory`). If the directory is missing, create it:

```bash
mkdir -p data/memory
```

### Optional services not responding

```bash
docker compose down
docker compose up -d
docker compose logs -f
```

### Kubernetes cluster not starting

This applies only to the real-cluster extension. No exercise needs a cluster.
Reset the cluster from Docker Desktop: **Settings**, then **Kubernetes**, then
**Reset Kubernetes Cluster**. Or keep mock mode on and continue with the
exercises.

## Getting Help

1. **Check the `complete/` directory** for the reference implementation
2. **Re-read Chapter 11, Section 11.6**. It walks through the same design
3. **Refer to the main repository README** for support channels

## Next Steps

After completing the lab:
1. **Take the challenge lab** in `challenge-lab/` (Section 11.7). It covers multi-service deployment with coordinated rollback
2. **Try other strategies**, such as blue-green or rolling updates
3. **Add the security and cost gates** from Section 11.5 (`../code-examples/security-gates.py`, `cost-guardrails.py`)
4. **Wire up a real cluster** (EKS, GKE, AKS, or Docker Desktop's). Implement the real-cluster branches in `infrastructure_client.py`. Today they fall back to the mock. Then set `USE_MOCK_INFRASTRUCTURE=false`

## Related Resources

- **Chapter 9**: the memory system this lab's `memory_integration.py` simplifies
- **Chapter 10**: multi-agent coordination patterns
- **Chapter 12**: safety and governance for agents with infrastructure access
- **Claude Code documentation**: [code.claude.com/docs](https://code.claude.com/docs)
- **Kubernetes Python client**: [kubernetes.io/docs](https://kubernetes.io/docs/reference/using-api/client-libraries/)

---

Start with [exercises/exercise-1-canary.md](./exercises/exercise-1-canary.md).
