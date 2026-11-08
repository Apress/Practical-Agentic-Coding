"""
Goal drift detection for long-running agent sessions.

This module monitors alignment between agent outputs and the
original task specification over time. When alignment degrades
below a threshold, an alert is raised recommending specification
re-injection.

Reference: Chapter 12, Section 12.5.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


# ---------------------------------------------------------------------------
# Data structures (given)
# ---------------------------------------------------------------------------

@dataclass
class DriftAlert:
    """Alert raised when goal drift is detected."""

    severity: str
    step: int
    trend: float
    recommendation: str


# ---------------------------------------------------------------------------
# Helper function stubs (TODO)
# ---------------------------------------------------------------------------

def semantic_similarity(text_a: str, text_b: str) -> float:
    """Compute semantic similarity between two texts.

    In production, this would use an embedding model (Chapter 9,
    Section 9.5) and cosine similarity via
    sklearn.metrics.pairwise.cosine_similarity. The lab uses word
    overlap so your implementation runs offline with no model.

    For this lab, implement a simplified version using word overlap:
      1. Tokenize both texts into sets of lowercase words.
      2. Compute Jaccard similarity: |intersection| / |union|.
      3. Return the similarity score (0.0 to 1.0).

    Handle the edge case where both texts are empty (return 1.0)
    or the union is empty (return 0.0).

    TODO: Implement word-overlap similarity.
    """
    # TODO: Implement semantic similarity using word overlap
    raise NotImplementedError("TODO: implement semantic_similarity()")


def linear_regression_slope(scores: list[float]) -> float:
    """Compute the slope of a linear regression over the scores.

    Use numpy.polyfit(range(n), scores, 1)[0] to fit a line and
    return its slope. A negative slope indicates declining alignment.

    Args:
        scores: List of alignment scores over time.

    Returns:
        The slope of the best-fit line through the scores.

    TODO: Implement using numpy.polyfit.
    """
    # TODO: Implement linear regression slope
    raise NotImplementedError("TODO: implement linear_regression_slope()")


# ---------------------------------------------------------------------------
# GoalDriftMonitor (starter with TODO)
# ---------------------------------------------------------------------------

class GoalDriftMonitor:
    """Monitors agent alignment with original specification over time.

    Computes alignment scores at each step and fires an alert when
    the trend (slope of recent scores) crosses the drift threshold.
    """

    def __init__(
        self,
        original_spec: str,
        drift_threshold: float = 0.15,
    ) -> None:
        self.original_spec = original_spec
        self.threshold = drift_threshold
        self.scores: list[float] = []

    def check(self, agent_output: str, step: int) -> DriftAlert | None:
        """Check agent output for goal drift.

        Steps:
          1. Compute similarity between self.original_spec and
             agent_output using semantic_similarity().
          2. Append the score to self.scores.
          3. If there are at least 5 scores, compute the trend using
             linear_regression_slope(self.scores[-5:]). The slope uses
             only the last five scores, so one early low score cannot
             mask fresh drift.
          4. If the trend is less than -self.threshold (negative and
             steep), return a DriftAlert with severity="WARNING",
             step=step, trend=trend, and
             recommendation="Re-inject original specification".
          5. Otherwise return None.

        TODO: Implement drift detection logic.
        """
        # TODO: Implement goal drift checking
        raise NotImplementedError("TODO: implement GoalDriftMonitor.check()")
