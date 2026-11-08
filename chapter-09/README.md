# Chapter 9: Agent Memory and Context Models: Building Cognitive Architectures for Agentic Systems

Code examples, hands-on lab, and challenge lab for Chapter 9.

> **Updates to the printed book (as of November 7, 2026)**
>
> - **Python 3.15 is not supported.** ChromaDB's onnxruntime dependency has no
>   Python 3.15 wheels, so the labs' install fails on 3.15. Use Python 3.11 to
>   3.14 (3.11 to 3.13 on an Intel Mac).
> - **The lab names a model for Mem0.** OpenAI does not serve Mem0's built-in
>   default model. `memory_core.py` adds an `llm` block to `mem0_config` that
>   names `gpt-5.6-luna`.

## What's here

| Directory | What it is | Book section |
|-----------|-----------|--------------|
| `code-examples/` | Standalone scripts for the memory concepts in the chapter: the pre-embeddings session-log progression, decay, context budgeting, decision records, trust scoring, scope promotion. No services needed. | 9.2 to 9.5 |
| `hands-on-lab/` | DevMemory, the system you build: Mem0-orchestrated memory over ChromaDB, session capture, pattern mining, memory scopes, trust scoring. Five exercises, each with a test file or a verification snippet. | 9.6 |
| `challenge-lab/` | TeamMemory, the open-ended extension: Neo4j graph relationships, organizational scope, and a cross-project promotion pipeline. Scaffolds with TODOs, no reference solution. | 9.7 |

## What you do

1. Read Chapter 9, Sections 9.2 through 9.5. The lab implements the patterns
   from those sections.
2. Run the `code-examples/` scripts. Each takes about a minute. No Docker, no
   API key. The only setup is `pip install -r requirements.txt`, which
   `decision_journal.py` needs for PyYAML.
3. **Start with
   [`code-examples/session-log-progression/`](./code-examples/session-log-progression/)
   before embeddings.** It is the structured-log-then-keyword-search stage of
   episodic memory from Chapter 2 (Section 2.2). The lab's Mem0 + ChromaDB
   build starts from that baseline.
4. Work the hands-on lab: [hands-on-lab/README.md](./hands-on-lab/README.md).
   Fill in the TODOs in `starter/`. The tests tell you when each phase works.
5. Try the challenge lab: [challenge-lab/README.md](./challenge-lab/README.md).

Budget about 90 minutes for the hands-on lab.

## Directory structure

```text
chapter-09/
├── README.md                     # This file
├── code-examples/                # Concepts from the chapter, runnable
│   ├── README.md
│   ├── session-log-progression/  # 9.3: episodic memory before embeddings
│   │   ├── README.md             # When each stage suffices, when to graduate
│   │   ├── session_log.py        # Stage 1: JSONL log, query by date/task/outcome
│   │   └── keyword_search.py     # Stage 2: keyword scan over the log
│   ├── confidence_decay.py       # 9.2: decay, reinforcement, consolidation
│   ├── context_budget.py         # 9.2: per-task token budgets and placement
│   ├── decision_journal.py       # 9.4: decision records as queryable memory
│   ├── trust_scoring.py          # 9.5: provenance-based trust gating
│   ├── memory_promotion.py       # 9.5: scopes, read-through, conflicts
│   ├── decisions/                # YAML record decision_journal.py reads
│   └── requirements.txt
├── hands-on-lab/                 # DevMemory (Section 9.6)
│   ├── README.md                 # Setup and instructions, start here
│   ├── docker-compose.yml        # ChromaDB service
│   ├── requirements.txt          # Mem0, ChromaDB, pytest
│   ├── pytest.ini                # Test config (rootdir is hands-on-lab/)
│   ├── .env.example              # Config template, incl. the OpenAI key slot
│   ├── verify_setup.py           # Prerequisite check, run before exercise 1
│   ├── starter/                  # Your working copy, with TODOs
│   │   ├── __init__.py           # Package marker
│   │   ├── config.py             # DevMemoryConfig (ready to use)
│   │   ├── memory_core.py        # DevMemory + PatternMiner (exercises 1, 4)
│   │   ├── capture.py            # ApprenticeCapture (exercise 2)
│   │   ├── scopes.py             # ScopedMemory (exercise 3)
│   │   ├── trust.py              # Trust scoring (exercise 5)
│   │   ├── demo.py               # End-to-end run, after all five exercises
│   │   └── tests/                # Tests that check your implementation
│   └── exercises/                # Step-by-step guide per exercise
└── challenge-lab/                # TeamMemory (Section 9.7)
    ├── README.md                 # Setup, schema, hints, verification
    ├── docker-compose.yml        # ChromaDB + Neo4j services
    ├── requirements.txt          # Adds the neo4j driver
    └── starter/                  # Graph store and promotion scaffolds
        ├── __init__.py
        ├── graph_store.py        # Neo4j operations (TODOs)
        └── promotion.py          # Cross-project promotion (TODOs)
```

## Section map

| Section | Topic | Where the code is |
|---------|-------|-------------------|
| 9.1 | Tacit knowledge and why documentation misses it | Conceptual (no code) |
| 9.2 | Memory span and cognitive efficiency | `code-examples/confidence_decay.py`, `context_budget.py` |
| 9.3 | Developer memory types (episodic, semantic, procedural) | `code-examples/session-log-progression/` (episodic memory before embeddings, the progression Chapter 2, Section 2.2 promises) |
| 9.4 | Knowledge capture patterns | `code-examples/decision_journal.py`; the Apprentice Pattern is exercise 2, Pattern Mining is exercise 4 |
| 9.5 | Memory architecture for autonomous development | `code-examples/memory_promotion.py`, `trust_scoring.py` |
| 9.6 | Hands-on lab: building DevMemory | `hands-on-lab/` |
| 9.7 | Challenge lab: TeamMemory with graph relationships | `challenge-lab/` |

## Stack

| Component | Purpose | Where |
|-----------|---------|-------|
| Mem0 (open source) | Memory orchestration: add, search, deduplication, conflict detection | Hands-on lab and challenge lab |
| ChromaDB | Vector storage behind Mem0, for similarity search | Hands-on lab and challenge lab |
| Neo4j | Graph relationships between decisions, patterns, services, teams | Challenge lab only |

Why the stack uses both vector and graph storage: Chapter 9, Section 9.5.

## Hands-on lab exercises

| Exercise | Topic | File to edit | How you verify |
|----------|-------|--------------|----------------|
| 1 | Mem0-backed memory core | `hands-on-lab/starter/memory_core.py` | `pytest starter/tests/test_memory.py -v` |
| 2 | Apprentice Pattern capture | `hands-on-lab/starter/capture.py` | `pytest starter/tests/test_capture.py -v` |
| 3 | Memory scopes | `hands-on-lab/starter/scopes.py` | `pytest starter/tests/test_scopes.py -v` |
| 4 | Pattern Mining | `hands-on-lab/starter/memory_core.py` | Snippet in `hands-on-lab/exercises/exercise-4-mining.md` |
| 5 | Trust scoring | `hands-on-lab/starter/trust.py` | Snippet in `hands-on-lab/exercises/exercise-5-trust.md`, then `python starter/demo.py` |

Exercises 4 and 5 have no test file of their own. Each exercise guide has an
inline verification snippet instead:

- Pattern Mining needs several captured sessions before it produces anything.
- Trust scoring needs stored memories to filter.

`demo.py` is the end-to-end check after all five exercises. Before exercise 5,
it crashes on `trust.py`'s `NotImplementedError`.

## Prerequisites

- Python 3.11 to 3.14 (3.11 to 3.13 on an Intel Mac). See the update note at
  the top of this file.
- Docker Desktop, for the ChromaDB container (and Neo4j in the challenge lab)
- An OpenAI API key for the labs. Mem0 defaults to OpenAI for both fact
  extraction and embeddings. `remember()` and `recall()` make model calls.
  To use a local Ollama model instead, see the hands-on lab README for the
  config change.
- `code-examples/` needs none of the above beyond Python.

## Where the repo differs from the printed listings

The class names, method signatures, and imports in `hands-on-lab/starter/`
match the Section 9.6 listings. You can type the listings or fill in the TODOs.
Both paths end in the same system. These things go beyond the page:

- `config.py` adds `load_config()`, which reads `.env`. The tests and `demo.py`
  still build `DevMemoryConfig` directly, as the book does.
- `trust.py` adds two small helpers for the timestamp handling inside
  `calculate_trust()`. The book's inline version works the same.
- The tests are a superset of the four the book prints (nine in all), and the
  `recall_all()` test stores its memories with `infer=False`.
- ChromaDB starts from `docker-compose.yml` instead of the book's `docker run`
  line. It uses the same port. It also adds:
  - a healthcheck
  - a pinned image (1.5.9)
  - a named data volume
  - a port published on 127.0.0.1 only

  Either one works with the lab.
- `memory_core.py` adds an `llm` block to `mem0_config` that names
  `gpt-5.6-luna`. See the update note at the top of this file.

The [hands-on lab README](./hands-on-lab/README.md) explains each one where it
comes up.

Later chapters reuse what you build here:

- Chapter 10 coordinates agents through the shared project scope.
- Chapter 11's deployer checks past failure history before it deploys.
