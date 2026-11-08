"""
Goal drift detection for long-running agent sessions (reference solution).

Monitors alignment between agent outputs and the original task
specification over time. When alignment degrades below a threshold, an
alert is raised recommending specification re-injection.

Reference: Chapter 12, Section 12.5.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class DriftAlert:
    """Alert raised when goal drift is detected."""

    severity: str
    step: int
    trend: float
    recommendation: str


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

_WORD = re.compile(r"[a-z0-9']+")


def semantic_similarity(text_a: str, text_b: str) -> float:
    """Word-overlap (Jaccard) similarity between two texts.

    In production this would use an embedding model (Chapter 9,
    Section 9.5) and cosine similarity via
    sklearn.metrics.pairwise.cosine_similarity. Word overlap keeps the
    lab offline and deterministic. See
    `code-examples/goal_drift_monitor.py` for the TF-IDF variant and the
    embedding swap.

    Args:
        text_a: First text (typically the original specification).
        text_b: Second text (typically the agent's recent output).

    Returns:
        Similarity score between 0.0 and 1.0.
    """
    words_a = set(_WORD.findall(text_a.lower()))
    words_b = set(_WORD.findall(text_b.lower()))

    if not words_a and not words_b:
        return 1.0  # Two empty texts are trivially identical.

    union = words_a | words_b
    if not union:
        return 0.0

    return len(words_a & words_b) / len(union)


def linear_regression_slope(scores: list[float]) -> float:
    """Slope of a degree-1 fit through the scores.

    A negative slope means alignment is declining. Fewer than two points
    has no trend, so return 0.0 rather than letting polyfit warn.

    Args:
        scores: List of alignment scores over time.

    Returns:
        The slope of the best-fit line through the scores.
    """
    if len(scores) < 2:
        return 0.0
    return float(np.polyfit(range(len(scores)), scores, 1)[0])


# ---------------------------------------------------------------------------
# GoalDriftMonitor
# ---------------------------------------------------------------------------

class GoalDriftMonitor:
    """Monitors agent alignment with original specification over time.

    Computes alignment scores at each step and fires an alert when the
    trend (slope of recent scores) crosses the drift threshold.
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
        """Score this step and return an alert if the trend is drifting."""
        score = semantic_similarity(self.original_spec, agent_output)
        self.scores.append(score)

        # Fewer than five points is noise, not a trend.
        if len(self.scores) < 5:
            return None

        trend = linear_regression_slope(self.scores[-5:])
        if trend < -self.threshold:
            return DriftAlert(
                severity="WARNING",
                step=step,
                trend=trend,
                recommendation="Re-inject original specification",
            )
        return None
