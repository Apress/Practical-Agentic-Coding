# Session Log Progression: Episodic Memory Before Embeddings

These two scripts are the first two stages of the episodic memory progression
in Chapter 2, Section 2.2:

1. A structured session log.
2. Keyword search over that log.

The third stage, the vector store, is what the hands-on lab builds in
[`../../hands-on-lab/`](../../hands-on-lab/).

Stdlib only. No Docker, no API key, no install.

## The two stages

| Script | Stage | Answers questions like |
|--------|-------|------------------------|
| `session_log.py` | 1. Structured log (append-only JSONL, filtered on date, task, outcome) | "Which refactors failed?" "What did I work on since Monday?" |
| `keyword_search.py` | 2. Keyword search (substring scan over the summaries) | "What do we know about the auth module?" |

Run them in order, from this folder:

```bash
python session_log.py       # seeds sessions.jsonl and runs a structured query
python keyword_search.py auth
```

`session_log.py` writes `sessions.jsonl` next to itself (gitignored). It resets
the file each run, so the demo is repeatable. A SQLite table would work the
same way. The script uses JSONL because it is diffable and needs no schema
migration.

When to use each stage, and when to move to embeddings: Chapter 2,
Section 2.2, and Chapter 9, Section 9.3.
