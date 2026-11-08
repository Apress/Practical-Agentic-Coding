"""Anchors pytest's import path at this directory.

Collecting this conftest makes pytest put `hands-on-lab/` on sys.path,
so `from starter.governance...` and `from complete.governance...`
imports resolve no matter how pytest is invoked (bare `pytest`,
`python -m pytest`, or with the challenge-lab tests as the target).
No fixtures are defined here; the file's presence is the point.
"""
