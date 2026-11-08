"""Anchors the import path when pytest runs from this directory.

The chapter's verification command, `pytest
tests/test_multi_agent_safety.py -v`, is run from `challenge-lab/`.
pytest cuts its upward conftest.py search at the rootdir it determines
for the invocation, so `../conftest.py` (in `hands-on-lab/`) is never
loaded from here, and the `from starter.governance...` import you add
for the goal drift test would fail with ModuleNotFoundError.

This file puts `hands-on-lab/` (the parent directory) on sys.path
itself, so `starter.governance.*` and `complete.governance.*` resolve
whether you run pytest from this directory or from `hands-on-lab/`.
No fixtures are defined here.
"""

import sys
from pathlib import Path

_HANDS_ON_LAB = str(Path(__file__).resolve().parent.parent)
if _HANDS_ON_LAB not in sys.path:
    sys.path.insert(0, _HANDS_ON_LAB)
