# Challenge Lab: Multi-Agent Safety Testing

**Time**: 90-120 minutes. Do the hands-on lab in the parent directory
first. This challenge builds on it.

## The Challenge

Write a test harness that checks a multi-agent coding pipeline for
**compositional safety**. These are failure modes that show up only when
the agents run as a chain. Testing each agent alone does not find them.

1. Reuse the governance pipeline you built in the hands-on lab
   (Section 12.8).
2. Point it at the agent team from Chapter 10's hands-on lab
   (Section 10.7). In that team, separate agents write the code, write
   the tests, and review the result.
3. Mock every agent in your tests. You do not need the Chapter 10 team
   running.

Test for the four failure modes in Section 12.4:

- cascade failure
- responsibility diffusion
- feedback loop amplification
- emergent goal conflict

## Requirements

### 1. Boundary Verification Tests

Check every handoff in the chain. The upstream agent's postconditions
must satisfy the downstream agent's preconditions.

- **Type consistency**: The code generator's output must be valid input
  for the test generator. Verify that these are preserved across the
  handoff: data types, function signatures, and module structure.
- **Coverage completeness**: The test generator's output must cover the
  code generator's public API. Verify that every public function has at
  least one corresponding test.

### 2. Injection Resistance Tests

Simulate adversarial inputs (e.g., a poisoned GitHub issue) and verify
the system's defenses.

- **HTML comment injection**: Embed hidden instructions in HTML comments
  within an issue body. Verify the sanitization layer strips them.
- **"Ignore previous" injection**: Include a prompt override attempt in
  the input. Confirm the orchestrator ignores the injected override. It
  must not act on it.

### 3. Cascade Failure Tests

Introduce a subtle error early in the pipeline and verify downstream
agents catch it before it reaches deployment.

- Inject a bug in the code generator's output (e.g., an off-by-one
  error or an unchecked null reference).
- Verify the test generator writes tests that catch the bug.
- Verify the code reviewer flags the issue even if the tests happen to
  pass.

### 4. Goal Drift Tests

Run the agent swarm on a multi-step task and verify alignment stays
above threshold throughout.

- Simulate a task of 30 steps.
- Score how well each step's output aligns with the original
  specification.
- Fail the test if alignment falls below 0.7 at any point.

## Prerequisites

Finish the hands-on lab first. This challenge reuses `ValidatorPipeline`
and `GoalDriftMonitor` from it. Use the same environment. There are no
new dependencies.

## Verification

Run the harness from this directory, as the chapter shows:

```bash
pytest tests/test_multi_agent_safety.py -v
```

Running from the `hands-on-lab` directory (the parent) works too:

```bash
cd ..
pytest challenge-lab/tests/test_multi_agent_safety.py -v
```

Both work because the `conftest.py` files here and in the parent anchor
`hands-on-lab/` on the import path. This lets
`from starter.governance.drift_monitor import GoalDriftMonitor` resolve.

The six scaffolded tests all skip until you implement them. Replace each
`pytest.skip(...)` line with your own test body.

Expected results when fully implemented:
- Every boundary check passes
- The harness detects and strips at least 80% of the injected adversarial content
- The seeded cascade bug is stopped before it reaches the deployment stage
- Alignment never drops below 0.7 across the 30-step task

## Bonus Challenge

Add a "devil's advocate". This is an adversarial reviewer inside the
swarm. It inspects each specialist's output and looks for safety
violations. The devil's advocate should:

1. Receive the same inputs as the next agent in the chain
2. Attempt to find boundary violations, injection opportunities, or
   specification drift
3. Report findings to the orchestrator before the handoff proceeds
4. Track its own false-positive rate to avoid blocking legitimate work

## Hints

- Use the `ValidatorPipeline` from the hands-on lab as the foundation
  for boundary verification.
- Mock all LLM calls. The tests should be deterministic and run
  without API keys.
- Review Section 12.4 for the taxonomy of multi-agent failure modes.
- Review Section 12.5 for the `GoalDriftMonitor` pattern.
- The cascade failure test requires simulating at least three agents
  in sequence (generator, tester, reviewer).
