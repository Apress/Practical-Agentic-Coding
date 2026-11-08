# Exercise 3: Memory Scopes

**File to edit**: `starter/scopes.py`
**Tests**: `pytest starter/tests/test_scopes.py -v`
**Reference**: Chapter 9, Section 9.6 (Phase 3)

## Goal

Implement `recall_for_agent()` in `ScopedMemory`.

## What you need to know

- `remember_private()` and `remember_shared()` are already implemented
- Private memories use `agent_id` as the Mem0 user_id
- Shared memories use `self.SHARED_SCOPE` ("__project_shared__") as the user_id
- Read-through: check the agent scope first, then the shared scope

## Steps

1. Query agent's private memories: `self.memory.recall(query, agent_id=agent_id, n_results=n_results)`
2. Query shared memories: `self.memory.recall(query, agent_id=self.SHARED_SCOPE, n_results=n_results)`
3. Return `{"agent": agent_results, "shared": shared_results}`

## Verify

```bash
pytest starter/tests/test_scopes.py -v
```
