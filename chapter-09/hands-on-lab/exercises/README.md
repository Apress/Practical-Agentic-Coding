# DevMemory Exercises

Chapter 9, Section 9.6. Do these in order. Each builds on the last.

| Exercise | Guide | Topic | File you edit |
|----------|-------|-------|---------------|
| 1 | [exercise-1-memory-core.md](exercise-1-memory-core.md) | Mem0-backed memory core | `starter/memory_core.py` (`DevMemory`) |
| 2 | [exercise-2-capture.md](exercise-2-capture.md) | Apprentice Pattern capture | `starter/capture.py` |
| 3 | [exercise-3-scopes.md](exercise-3-scopes.md) | Memory scopes | `starter/scopes.py` |
| 4 | [exercise-4-mining.md](exercise-4-mining.md) | Pattern Mining | `starter/memory_core.py` (`PatternMiner`) |
| 5 | [exercise-5-trust.md](exercise-5-trust.md) | Trust scoring | `starter/trust.py` |

Exercises 1 through 3 have their own test files. Exercises 4 and 5 do not.
Each of those two guides has an inline verification snippet instead:

- Pattern Mining needs three or more captured sessions before it produces a
  pattern.
- Trust scoring needs stored memories to filter.

The demo is the end-to-end check after all five. Before exercise 5, it stops on
`trust.py`'s `NotImplementedError`.

Run every command from `chapter-09/hands-on-lab/`. Do not run them from inside
`starter/` or this directory. `pytest.ini` sets the import path relative to the
lab root.

After all five, run the end-to-end system:

```bash
python starter/demo.py
```
