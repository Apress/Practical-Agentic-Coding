"""Stage 1 of the episodic memory progression: a structured session log.

Append-only JSONL, one record per work session, queried by date, task, or
outcome. No database server, no index, no embeddings. This is the entry
point Chapter 2 describes and the stage the Chapter 9 lab graduates from.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

LOG_PATH = Path(__file__).parent / "sessions.jsonl"


def log_session(task: str, outcome: str, summary: str,
                log_path: Path = LOG_PATH) -> dict:
    """Append one session record. Append-only keeps the history honest."""
    record = {
        "date": datetime.now(timezone.utc).date().isoformat(),
        "task": task,        # e.g. "debugging", "refactor", "review"
        "outcome": outcome,  # "success" or "failure"
        "summary": summary,  # one sentence a teammate would understand
    }
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return record


def load_sessions(log_path: Path = LOG_PATH) -> list[dict]:
    """Read every record in the log, oldest first."""
    if not log_path.exists():
        return []
    with log_path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def query(task: str | None = None, outcome: str | None = None,
          since: str | None = None, log_path: Path = LOG_PATH) -> list[dict]:
    """Filter on the structured fields. ISO dates compare as strings."""
    return [
        r for r in load_sessions(log_path)
        if (task is None or r["task"] == task)
        and (outcome is None or r["outcome"] == outcome)
        and (since is None or r["date"] >= since)
    ]


if __name__ == "__main__":
    LOG_PATH.unlink(missing_ok=True)  # demo starts from an empty log
    log_session("refactor", "failure", "Refactored the auth module; "
                "12 integration tests failed on the token TTL change.")
    log_session("debugging", "success", "API 502s traced to the connection "
                "pool cap; raised the pool size to 50.")
    log_session("refactor", "success", "Split the payment service config "
                "into its own module; all tests green.")

    print("Failed refactors (the 'what went wrong last time?' question):")
    for r in query(task="refactor", outcome="failure"):
        print(f"  {r['date']}  {r['summary']}")
