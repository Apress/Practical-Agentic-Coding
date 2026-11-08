"""
Immutable, hash-chained audit log for agent actions (reference solution).

Tamper-evident logging using SHA-256 hash chaining. Tampering with any
entry breaks the chain, making modifications detectable.

Reference: Chapter 12, Section 12.8 (lab Step 3).
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any


class ImmutableAuditLog:
    """Hash-chained log entries for tamper evidence.

    Each entry includes the hash of the previous entry, forming a chain.
    Verifying the chain detects any modification to past entries.
    """

    def __init__(self) -> None:
        self.entries: list[dict[str, Any]] = []
        self.previous_hash: str = "genesis"

    def append(self, agent_id: str, action: str, result: str) -> None:
        """Add a new entry to the audit log with hash chaining."""
        entry: dict[str, Any] = {
            "agent_id": agent_id,
            "action": action,
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "previous_hash": self.previous_hash,
        }
        # Hash the entry BEFORE adding the "hash" key, so verify_chain()
        # can recompute the same value later.
        entry["hash"] = hashlib.sha256(
            json.dumps(entry, sort_keys=True).encode()
        ).hexdigest()
        self.previous_hash = entry["hash"]
        self.entries.append(entry)

    def verify_chain(self, expected_head: str | None = None) -> bool:
        """Verify that no entries have been tampered with.

        Two checks per entry: the linkage (does previous_hash match the
        prior entry's hash?) and the content (does recomputing the hash
        from the entry's own fields reproduce the stored hash?). Linkage
        alone would miss an edit to the last entry.

        One gap the chain itself cannot catch: deleting entries from the
        tail leaves a shorter but still valid chain. Store the latest
        hash (the chain head) somewhere the agent cannot write, and pass
        it as `expected_head`; verification then fails when the last
        entry's hash no longer matches it.
        """
        previous = "genesis"
        for entry in self.entries:
            if entry["previous_hash"] != previous:
                return False

            payload = {
                key: value for key, value in entry.items() if key != "hash"
            }
            expected = hashlib.sha256(
                json.dumps(payload, sort_keys=True).encode()
            ).hexdigest()
            if entry["hash"] != expected:
                return False

            previous = entry["hash"]

        if expected_head is not None and previous != expected_head:
            return False
        return True
