# Agent Invocation Patterns

This directory holds the agent invocation examples from Chapter 4.

When to use each invocation pattern and why: Chapter 4, Section 4.5.

## Files in This Directory

| File | Description | Source |
|------|-------------|--------|
| `sync_invocation.py` | Synchronous agent execution | Listing 4-7 |
| `model_router.py` | Task-appropriate model selection, plus a policy-driven router | Listing 4-5, extended |
| `handoff_pattern.py` | Agent-to-agent delegation | Extended example |
| `tool_using_invocation.py` | Tool-using invocation: reads Commands from AGENTS.md, auto-runs tests | Worked solution to Exercise 4.2 |

All four files run standalone. They need only the standard library. On Windows, use `py` in place of `python3`.

```bash
python3 sync_invocation.py
python3 model_router.py
python3 handoff_pattern.py
python3 tool_using_invocation.py
```

These files illustrate the pattern. They are not SDK integrations. The three agent examples each define their own small `Agent` class instead of importing a vendor SDK. `model_router.py` has no agent at all. It only picks a model tier.

Expected output when you run them from this directory. Each one exits with status 0.

- `sync_invocation.py` looks for `AGENTS.md` in the current directory, as Listing 4-7 does. There is none here. So it first prints `Warning: AGENTS.md not found at AGENTS.md...` and falls back to built-in instructions. This is expected. To see it load a real file, copy `../agents-md/AGENTS.md` into this directory.
- `model_router.py` prints the Listing 4-5 routes, then the policy router's decisions. `route_task` is the book's listing unchanged. Its keyword match is case-sensitive. The demo lowercases each description before it calls `route_task`.
- `handoff_pattern.py` prints a simple coding-to-security handoff, then a four-stage pipeline.
- `tool_using_invocation.py` loads `../agents-md/AGENTS.md`, prints the parsed Commands section, and ends with the combined result object (simulated test output).

## Exercise 4.2 solution

`tool_using_invocation.py` is a worked solution to the book's Exercise 4.2. It does three things:

1. Parses the Commands section of AGENTS.md.
2. Generates tests, then automatically calls a `run_tests()` tool.
3. Returns a combined result object with both the tests and the test output.

## Related Resources

- Chapter 5: Amazon Kiro and spec-driven development
- Chapter 8: Claude Code, including headless and SDK invocation
- Chapter 10: multi-agent orchestration, which builds a running agent team
- [AGENTS.md templates](../agents-md/) in this chapter
