# Chapter 9 Code Examples

Runnable Python for the memory patterns in Chapter 9, "Agent Memory and Context
Models: Building Cognitive Architectures for Agentic Systems." Each script covers
one idea from one section. It prints what it decided and why.

The full DevMemory system you build is in `../hands-on-lab/`.

## Prerequisites

- Python 3.11 or later
- No Docker, no API key, no running services. Everything here is in-process.
- `decision_journal.py` needs PyYAML. Everything else is stdlib only.

```bash
cd chapter-09/code-examples
python3 -m venv .venv && source .venv/bin/activate   # Windows: py -m venv .venv, then .venv\Scripts\activate
pip install -r requirements.txt   # only for decision_journal.py
python confidence_decay.py
```

## What maps to what

| Script | Book section | The idea it shows |
|--------|--------------|-------------------|
| `session-log-progression/` | 9.3 Developer Memory Types (and the episodic memory progression in Chapter 2, Section 2.2) | Episodic memory before embeddings. A JSONL session log queried by date/task/outcome, then keyword search over it. Start here before the lab's vector store |
| `confidence_decay.py` | 9.2 Memory Span and Cognitive Efficiency | Confidence decay with a half-life, reinforcement on confirmation, and three episodes consolidated into one semantic fact |
| `context_budget.py` | 9.2 Memory Span and Cognitive Efficiency | Per-task token budgets across memories, code, and history, plus where each item goes in the context window |
| `decision_journal.py` | 9.4 Knowledge Capture Patterns | The Decision Journal record from the chapter, validated, flattened for indexing, and queried by affected component |
| `trust_scoring.py` | 9.5 Memory Architecture for Autonomous Development (provenance and trust) | `calculate_trust_score` gating shared memories on provenance, validations, age, and contradictions |
| `memory_promotion.py` | 9.5 Memory Architecture for Autonomous Development | `MemoryPromotion` plus read-through scoping and scope-hierarchy conflict resolution across the three scopes |
| `decisions/` | Supports 9.4 | The YAML decision record `decision_journal.py` reads |

Section 9.1 has no code. Section 9.6's DevMemory is in `../hands-on-lab/`.
Section 9.7's TeamMemory is in `../challenge-lab/`.

## How these relate to the lab

The lab versions run against Mem0 and ChromaDB. Their inputs are the dicts
Mem0 returns. These versions run against plain dataclasses. You can read the
logic without a container running. Where both exist, build on the lab file:

| Concept here | Lab equivalent |
|--------------|----------------|
| `trust_scoring.calculate_trust_score` | `hands-on-lab/starter/trust.py` (`calculate_trust`, dict input) |
| `confidence_decay.consolidate` | `hands-on-lab/starter/memory_core.py` (`PatternMiner`, groups by session type) |
| `memory_promotion.MemoryPromotion` | `challenge-lab/starter/promotion.py` (adds Neo4j cross-project counting) |
| `decision_journal.decisions_affecting` | `challenge-lab/starter/graph_store.py` (`query_by_component`, a real graph traversal) |

## What each script prints

### session-log-progression/

Two scripts with their own [README](./session-log-progression/README.md).

- `session_log.py` seeds a JSONL session log. It answers "which refactors
  failed?" with a structured filter.
- `keyword_search.py` answers "what do we know about the auth module?" with a
  substring scan.

### confidence_decay.py

1. The confidence timeline for one fact at days 1, 30, and 90. It shows where
   the fact drops below the retrieval threshold.
2. Day 91, after a developer confirms the fact.
3. Three "fixed null pointer in X" episodes consolidated into one semantic
   memory.

The decay curve is in `confidence_at()`. The script filters at retrieval time.
It does not delete rows.

### context_budget.py

1. Token allocations for four task types against a 200k window. Each line
   shows where that content goes in the window.
2. The assembly order for a debugging task.

Change `TASK_WEIGHTS` to match how your team works. The numbers are only a
starting point.

### decision_journal.py

One decision record read from YAML. The output shows:

- what was chosen, and why
- what was rejected, and on what grounds
- what consequences the team accepted
- the flattened string a vector store would index

The indexed string includes the rejected options. Why the record keeps them:
Chapter 9, Section 9.4.

### trust_scoring.py

Five memories, each scored and marked admitted or blocked. Each score shows its
provenance. Three memories are blocked:

- one because it is contradicted
- one because it is 400 days stale
- one because its base confidence is low

The script logs blocked memories. It does not delete them.

### memory_promotion.py

1. Four facts evaluated for promotion, with the reason each one moved or
   stayed.
2. A read-through query over all three scopes.
3. A policy conflict. The organizational rule wins, and the narrower exception
   is flagged for a human.
