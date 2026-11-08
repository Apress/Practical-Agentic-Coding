"""
Immutable, hash-chained audit log for agent actions.

This module implements tamper-evident logging using SHA-256 hash
chaining. Tampering with any entry breaks the chain, making
modifications detectable.

Reference: Chapter 12, Section 12.8 (lab Step 3).
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any


class ImmutableAuditLog:
    """Hash-chained log entries for tamper evidence.

    Each entry includes the hash of the previous entry, forming a
    chain. Verifying the chain detects any modification to past
    entries.
    """

    def __init__(self) -> None:
        self.entries: list[dict[str, Any]] = []
        self.previous_hash: str = "genesis"

    def append(self, agent_id: str, action: str, result: str) -> None:
        """Add a new entry to the audit log with hash chaining.

        Steps:
          1. Build a dict with keys: agent_id, action, result,
             timestamp (use datetime.now(timezone.utc).isoformat()),
             and previous_hash (from self.previous_hash).
          2. Compute the SHA-256 hash of the entry by serializing it
             with json.dumps(entry, sort_keys=True).encode() and
             calling hashlib.sha256(...).hexdigest().
          3. Store the hash in entry["hash"].
          4. Update self.previous_hash to the new hash.
          5. Append the entry to self.entries.

        Hint: The hash must be computed BEFORE adding the "hash" key
        to the entry dict. The chain links entries through
        previous_hash -> hash.

        TODO: Implement hash-chained append.
        """
        # TODO: Implement hash-chained log entry creation
        raise NotImplementedError("TODO: implement append()")

    def verify_chain(self, expected_head: str | None = None) -> bool:
        """Verify that no entries have been tampered with.

        Walk through self.entries in order. Two checks per entry:

          1. Linkage: entry["previous_hash"] matches the hash of the
             prior entry (or "genesis" for the first entry).
          2. Content: recompute the SHA-256 of the entry body (all
             keys except "hash", serialized exactly as in append())
             and compare it to entry["hash"]. Return False on a
             mismatch. Linkage alone cannot catch an edited entry,
             because the stored hash field is untouched.

        Hint: Track the expected previous_hash starting from "genesis".
        For each entry, compare entry["previous_hash"] to your
        tracked value, recompute the content hash, then update your
        tracked value to entry["hash"].

        Deleting entries from the tail leaves a shorter but still
        valid chain. When `expected_head` is provided (the chain head
        stored somewhere the agent cannot write), also compare it to
        the last entry's hash and return False on a mismatch.

        Returns:
            True if the entire chain is intact, False if any entry
            has been tampered with (or, when expected_head is given,
            if the chain has been truncated).

        TODO: Implement chain verification.
        """
        # TODO: Implement chain verification
        raise NotImplementedError("TODO: implement verify_chain()")
