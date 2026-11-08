# Exercise 1: Mem0-backed Memory Core

**File to edit**: `starter/memory_core.py`
**Tests**: `pytest starter/tests/test_memory.py -v`
**Reference**: Chapter 9, Section 9.6 (Phase 1)

## Goal

Implement the three methods in `DevMemory`: `remember()`, `recall()`, and `recall_all()`.

## What you need to know

Mem0's `Memory` class has these methods:
- `self.memory.add(content, user_id=..., metadata=..., infer=...)` - stores a memory
- `self.memory.search(query, user_id=..., limit=...)` - searches by similarity
- `self.memory.get_all(user_id=...)` - gets all memories for a user

Two details:
- `add()` takes an `infer` flag. By default, Mem0 extracts key facts and
  handles deduplication. `infer=False` stores content verbatim. `remember()`
  passes the flag through, so episodic records stay word for word.
- `search()` and `get_all()` return a dict with the matches under a
  `results` key. `recall()` and `recall_all()` unwrap it and return a plain
  list.

## Steps

1. Open `starter/memory_core.py`.
2. Find the three TODO methods.
3. Make each method wrap a single Mem0 call, as shown below.

### remember()
```python
return self.memory.add(
    content, user_id=agent_id, metadata=metadata or {}, infer=infer
)
```

### recall()
```python
response = self.memory.search(query, user_id=agent_id, limit=n_results)
return response.get("results", [])
```

### recall_all()
```python
return self.memory.get_all(user_id=agent_id).get("results", [])
```

## Verify

```bash
pytest starter/tests/test_memory.py -v
```
