# Hands-on Lab: Building a Governance Pipeline

Build a governance pipeline that enforces safety constraints across a
multi-agent coding system. You implement each component. The test suite
tells you when each one is right.

Maps to Chapter 12, Section 12.8.

## What You'll Build

Eight components across five modules, in the order the exercises build
them.

| Component | File | Topic | Section |
|-----------|------|-------|---------|
| Path restriction validator | `starter/governance/validators.py` | Composable validators | 12.3 |
| Credential detector | `starter/governance/validators.py` | PII and secret detection | 12.5 |
| Absolute boundary validator | `starter/governance/validators.py` | Non-negotiable boundaries | 12.5 |
| Validator pipeline | `starter/governance/validators.py` | Short-circuit composition | 12.3 |
| Resource budget | `starter/governance/budget.py` | Budget enforcement | 12.3 |
| Immutable audit log | `starter/governance/audit.py` | Hash-chained audit trail | 12.6 |
| Goal drift monitor | `starter/governance/drift_monitor.py` | Alignment decay detection | 12.5 |
| Execution rail | `starter/governance/execution_rail.py` | Four-step intercept pattern | 12.3 |

## Time required

60-90 minutes for this lab. The challenge lab at the end is a separate
90-120 minutes.

## Prerequisites

- Python 3.11+
- No Docker, no API keys, no external services

## Setup

Run every command in this README from this directory
(`chapter-12/hands-on-lab`). The `conftest.py` here anchors the import
path. This lets `starter.governance.*` resolve.

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python verify_setup.py
```

`verify_setup.py` checks:

- your Python version
- the four required packages
- that both `starter/` and `complete/` are present

Fix anything it flags before you start.

## Exercises

Open `starter/governance/` and implement the TODOs in this order. Each
row's test command runs only that component's tests.

| Order | File | TODOs | Test command |
|-------|------|-------|--------------|
| 1 | `validators.py` | 15 | `pytest tests/test_governance.py -k "TestPathRestriction or TestCredentialDetector or TestAbsoluteBoundary or TestValidatorPipeline" -v` |
| 2 | `budget.py` | 6 | `pytest tests/test_governance.py -k "TestResourceBudget" -v` |
| 3 | `audit.py` | 6 | `pytest tests/test_governance.py -k "TestAuditLog" -v` |
| 4 | `drift_monitor.py` | 11 | `pytest tests/test_governance.py -k "TestDriftMonitor" -v` |
| 5 | `execution_rail.py` | 4 | `pytest tests/test_governance.py -k "TestExecutionRail or TestEmergencyStop" -v` |

Before you start, every test fails with `NotImplementedError`. This is
expected.

## Running All Tests

```bash
pytest tests/test_governance.py -v
```

Expected when finished: 24 passed.

Each test class is tagged with the AGILITY pillar it tests. This lab
covers three of the seven pillars:

- Limitations: validators, budget
- Intervention: emergency stop, drift alerts
- Governance: audit chain

For tests across all seven pillars, see
`../code-examples/governance_tests.py`. It also marks which pillars need
manual verification.

## Reference Solution

`complete/` holds a working implementation of all eight components, with
the same module layout as `starter/`. Verify it end to end:

```bash
pytest complete/tests/test_governance.py -v
```

If you get stuck on one component, open the module that the failing test
names. In three places `complete/` is simpler than production code on
purpose. Each one is noted in its docstrings:

- `AbsoluteBoundary` matches substrings. The parsing version reads SQL
  statements and shell tokens. It is in
  `../code-examples/composable_validators.py`.
- `PathRestrictionValidator` matches raw prefixes with `startswith()`, as
  the book's Step 1 listing does. As a result, `/src/../etc/passwd` and
  `/srcevil/x.py` count as under `/src`. The same code-examples file has a
  version that normalizes paths and matches whole components.
- `semantic_similarity` uses word overlap. This lets the lab run offline.
  The production form takes embeddings. See
  `../code-examples/goal_drift_monitor.py`.

## Troubleshooting

- **`ModuleNotFoundError: No module named 'starter'`**: you ran pytest
  from the wrong directory. Run it from `chapter-12/hands-on-lab`. For the
  challenge tests only, `challenge-lab/` also works. The `conftest.py`
  files in those directories anchor the import path.
- **Every test fails with `NotImplementedError`**: expected before you
  implement the TODOs. Work through the exercise order above.
- **Async tests error with "async def functions are not natively
  supported"**: `pytest-asyncio` is missing. Run
  `pip install -r requirements.txt` again.
- **Anything else**: `python verify_setup.py` names the broken
  prerequisite and prints the fix.

## Challenge Lab

After finishing this lab, try the multi-agent safety testing challenge:

[challenge-lab/README.md](./challenge-lab/README.md)

**Time required for the challenge**: 90-120 minutes, on top of this lab's
60-90.

It tests a multi-agent system for safety as a composed whole.
