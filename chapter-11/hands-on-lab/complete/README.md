# Reference Solution - Zero-Downtime Deployer

This is the finished implementation of the hands-on lab (Chapter 11, Section
11.6). Everything the exercises ask you to write is already here.

**Write your own version first.** Then read this one and compare the two. If you
paste `validate_canary()` into your starter file, the tests pass, but you skip
the exercise.

## What's here

Same layout as `../starter/`, fully implemented:

```text
complete/
├── deployer.py                 # ZeroDowntimeDeployer, all methods complete
├── config.py                   # Settings from .env
├── infrastructure_client.py    # Deploy and traffic operations
├── health_monitor.py           # Metric collection and threshold checks
├── memory_integration.py       # DeploymentMemory (simplified from Chapter 9)
└── tests/
    ├── test_deployer.py        # 10 unit tests
    └── test_integration.py     # 6 end-to-end tests
```

## Running it

From the `hands-on-lab` directory, not from inside `complete/`:

```bash
cd chapter-11/hands-on-lab

# Unit tests (about a minute: the validation windows are real sleeps)
pytest complete/tests/test_deployer.py -v

# End-to-end tests (about a minute)
pytest complete/tests/test_integration.py -v

# Everything (about two minutes)
pytest complete/tests/ -v
```

All 16 tests pass. If they do not, check your environment:

- Did you run `cp .env.example .env`?
- Did you install `requirements.txt`?

Each suite takes about a minute. The deployer really waits through its
validation windows. The fixtures keep those windows short and pass
`traffic_stabilization_seconds=0`. No test waits through the 30-second
production pause between traffic shifts. The suite sets its own windows, so
`VALIDATION_DURATION_SECONDS` in `.env` does not change its run time. That
value is the default for deployments you run yourself.

## The two methods to compare

Why the deployer makes these choices: Chapter 11, Section 11.6.

### `validate_canary()`

1. **Memory query first.** `self.memory.recall()` looks for past failures with
   this service before it collects any metric.
2. **History changes the plan.** A service with a past memory-leak incident
   gets half the usual error budget. Its canary validation window is three
   times longer (the book's 60s to 180s adjustment in Section 11.6).
3. **Continuous sampling.** `monitor_continuously()` samples across the whole
   window. It does not check only once.
4. **Structured result.** It returns the thresholds it used with the verdict.

### `rollback()`

1. **Find the version to roll back to.** It takes the version still serving the
   most traffic from the live deployment list. It does not hardcode a target.
   The book's Section 11.6 summary describes a memory lookup here. The lab reads
   current state instead, and uses memory to record the event.
2. **Shift traffic back first.** Then remove the failing deployment. The other
   order drops requests.
3. **Record the failure in memory.** The next deployment of this service reads
   it and is more cautious.

## How this differs from the book listing

Section 11.6 shows `deploy()` at about 40 lines. This file adds:

- Phase tracking through `DeploymentPhase`.
- Per-step error handling.
- Deployment IDs for the audit trail.
- Configurable auto-rollback.

The decision logic is the same.

## Related

- `../starter/` - the scaffold with TODOs
- `../exercises/` - the step-by-step guides
- `../challenge-lab/` - the multi-service extension (Section 11.7)
