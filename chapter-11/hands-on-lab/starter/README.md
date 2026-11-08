# Starter Code - Zero-Downtime Deployer

This directory holds the starter code for the Chapter 11 hands-on lab. Complete the TODOs in the exercises to build a working deployment agent.

## File Structure

```text
starter/
├── README.md                    # This file
├── __init__.py                  # Package initialization
├── config.py                    # Configuration (ready to use)
├── infrastructure_client.py     # Mock deploy and traffic ops (ready to use)
├── health_monitor.py            # Health checking (ready to use)
├── memory_integration.py        # DevMemory adapter (ready to use)
├── deployer.py                  # Main deployer (TODOs for you)
└── tests/
    ├── __init__.py
    ├── test_deployer.py         # Unit tests
    └── test_integration.py      # Integration tests
```

## Files Overview

### Ready to Use (No Changes Needed)

#### `config.py`
- Loads configuration from `.env` file
- Provides `DeploymentConfig` and `ThresholdConfig` classes
- `DeploymentConfig` fills any field you leave out (canary percentage,
  validation window, traffic steps) from `.env`
- Carries `config.traffic_stabilization_seconds` (default 30). This is the pause
  the deployer takes after each traffic shift. Read it from
  `self.traffic_stabilization_seconds`. Do not hardcode a sleep. The tests pass
  0, so the suite does not wait through production pauses.

**Usage:**
```python
from starter.config import config, DeploymentConfig

# Access global config
print(config.canary_percentage)

# Create deployment config
deploy_config = DeploymentConfig(
    service_name="api-service",
    version="2.0.0",
    image="api:2.0.0",
    replicas=3
)
```

#### `infrastructure_client.py`
- Abstracts the deployment operations the deployer needs
- Runs everything against a mock. The real Kubernetes branches are
  placeholders that fall back to the mock
- Handles deployments, traffic shifting, metrics

**Usage:**
```python
from starter.infrastructure_client import InfrastructureClient

infra = InfrastructureClient(use_mock=True)
await infra.create_deployment(deployment_config)
await infra.set_traffic("api-service", "2.0.0", 50)
```

#### `health_monitor.py`
- Collects health metrics
- Performs health checks against thresholds
- Supports continuous monitoring

**Usage:**
```python
from starter.health_monitor import HealthMonitor

health = HealthMonitor(infrastructure_client)
metrics = await health.collect_metrics("api-service", "2.0.0")
result = await health.check_health("api-service", "2.0.0", thresholds)
```

#### `memory_integration.py`
- Simplified DevMemory interface
- Stores deployment history
- Recalls past failures for decision-making

**Usage:**
```python
from starter.memory_integration import DeploymentMemory

memory = DeploymentMemory()
await memory.remember_session(
    session_type="deployment",
    summary="Deployed api-service v2.0.0",
    outcome="success",
    project="api-service"
)

history = await memory.recall("deployment failure api-service")
```

### Your Work (TODOs)

#### `deployer.py`
The main deployment orchestrator. You implement:

**Exercise 1: `validate_canary()` method**
- Collect metrics over validation period
- Check against thresholds
- Query memory for past issues
- Return validation result

**Exercise 2: `rollback()` method**
- Identify stable version
- Shift traffic back
- Remove failing deployment
- Record rollback in memory

The `deploy()` method is already implemented. It calls your `validate_canary()` and `rollback()` methods.

## Running Tests

Run everything from the `hands-on-lab` directory, not from inside `starter/`.
The tests import `starter.deployer`. That import only resolves from the parent.

```bash
cd chapter-11/hands-on-lab

# Exercise 1
pytest starter/tests/test_deployer.py -v -k canary

# Exercise 2
pytest starter/tests/test_deployer.py -v -k rollback

# All unit tests (10 of them)
pytest starter/tests/test_deployer.py -v

# End-to-end (6 tests, slower)
pytest starter/tests/test_integration.py -v

# Everything, with print output visible
pytest starter/tests/ -v -s
```

The suite takes a couple of minutes. The deployer really waits through its
validation windows. The fixtures already pass short windows and
`traffic_stabilization_seconds=0`, so no test waits through a production pause.
For faster runs of your own, set `VALIDATION_DURATION_SECONDS=30` and
`TRAFFIC_STABILIZATION_SECONDS=0` in `.env`.

## Expected Test Behavior

**Before you start:** seven tests fail (six in `test_deployer.py`, one in
`test_integration.py`). This is expected. Read the failure messages. They
describe what each TODO has to produce.

**After Exercise 1:** the three `canary` tests pass. Rollback tests still fail.

**After Exercise 2:** all 10 tests in `test_deployer.py` pass. The six
integration tests pass too, because `deploy()` now calls working
`validate_canary()` and `rollback()` methods.

To see the target, run the same suite against the reference solution:

```bash
pytest complete/tests/ -v    # 16 passed
```

## Development Workflow

1. **Read the exercise** (`exercises/exercise-1-canary.md`)
2. **Open `deployer.py`** and find the TODO section
3. **Implement the method** following exercise instructions
4. **Run tests** to verify your implementation
5. **Debug** if tests fail (check test output)
6. **Move to next exercise** once tests pass

## Tips

**Use the ready-to-use modules:**
- `self.infra` for infrastructure operations
- `self.health_monitor` for metrics
- `self.memory` for history
- `config` for thresholds

**Start simple:**
- Get basic functionality working first
- Add memory integration after
- Optimize and refine last

**Test frequently:**
- Run tests after each change
- Use `-s` flag to see print statements
- Focus on one test at a time

**Check the complete/ folder:**
- If stuck, reference the complete implementation
- Compare your approach with the reference
- Understand the code before you reuse it

## Common Issues

### Import Errors
```bash
# Make sure you're in the hands-on-lab directory
cd chapter-11/hands-on-lab

# Then run the tests from there
pytest starter/tests/ -v
```

### Mock Infrastructure Not Working
```bash
# Check .env file
USE_MOCK_INFRASTRUCTURE=true
```

### Tests Timeout
The fixtures already pass short validation windows and
`traffic_stabilization_seconds=0`. If your run still hangs, check for a
hardcoded sleep. Read `self.traffic_stabilization_seconds` instead. For faster
local runs:
```env
VALIDATION_DURATION_SECONDS=30
TRAFFIC_STABILIZATION_SECONDS=0
```

### Memory Not Persisting
```bash
# Check data directory exists
mkdir -p data/memory

# Or check config
MEMORY_PERSIST_DIR=./data/memory
```

## Next Steps

1. Verify setup: `python verify_setup.py`
2. Read Exercise 1: `exercises/exercise-1-canary.md`
3. Implement `validate_canary()` in `deployer.py`
4. Run tests: `pytest starter/tests/ -v -k canary`
5. Move to Exercise 2 when those tests pass
