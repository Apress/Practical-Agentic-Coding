"""Stage 2 of the episodic memory progression: keyword search over the log.

When the structured fields (date, task, outcome) cannot answer the
question, a case-insensitive substring scan over the summaries covers
much of the rest. Still no index, no embeddings, no running service.
"""

from __future__ import annotations

import sys
from pathlib import Path

from session_log import LOG_PATH, load_sessions


def search(keywords: list[str], log_path: Path = LOG_PATH) -> list[dict]:
    """Return sessions whose summary mentions every keyword."""
    wanted = [k.lower() for k in keywords]
    return [
        record for record in load_sessions(log_path)
        if all(k in record["summary"].lower() for k in wanted)
    ]


if __name__ == "__main__":
    keywords = sys.argv[1:] or ["auth"]
    hits = search(keywords)
    print(f"Sessions mentioning {', '.join(keywords)}:")
    for r in hits:
        print(f"  {r['date']}  [{r['task']}/{r['outcome']}]  {r['summary']}")
    if not hits:
        print("  (none; if the log is empty, run session_log.py first)")
