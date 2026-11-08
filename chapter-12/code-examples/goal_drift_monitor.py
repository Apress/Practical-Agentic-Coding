"""
Module: Goal Drift Monitor for Long-Running Agent Sessions
Concept: Detecting and mitigating alignment decay over agent steps
Chapter Reference: Chapter 12, Section 12.5

This example demonstrates goal drift detection using semantic similarity
and linear regression trend analysis. Over long sessions, coding agents
progressively deviate from their original instructions. The monitor
tracks alignment at each step and fires alerts when the downward trend
crosses a threshold.

DELIBERATE SUBSTITUTION: the book describes `semantic_similarity` as
cosine similarity over embeddings from the project's configured
embedding model (Chapter 9, Section 9.5). This file computes cosine
similarity over TF-IDF vectors instead, using the same
`sklearn.metrics.pairwise.cosine_similarity` call. The reason is that
the example has to run for every reader with no API key, no network,
and no model download, and it has to produce the same numbers every
time so the printed output matches. TF-IDF gives that.

The trade-off is real and worth knowing: TF-IDF measures vocabulary
overlap, not meaning. A paraphrase that reuses none of the
specification's words scores low even though it is on task, and an
off-task output that happens to reuse the specification's vocabulary
scores high. Embeddings do not have that weakness. For production use,
swap `semantic_similarity` for an embedding call (see
`embedding_similarity` below for the shape of that swap). Everything
else in the module, including `GoalDriftMonitor`, is unchanged by it:
the monitor only needs a function that returns a float in [0, 1].

Key Patterns Demonstrated:
- Semantic similarity with a pluggable scoring function
- Linear regression slope for trend detection
- Specification re-injection to counteract drift
- Simulated 50-step agent session with gradual drift
- Configurable thresholds and window sizes
"""

import random
from dataclasses import dataclass, field
from typing import Callable, Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class DriftAlert:
    """Alert fired when goal drift exceeds the threshold."""
    severity: str
    step: int
    current_score: float
    trend: float
    window_scores: list[float]
    recommendation: str

    def __str__(self) -> str:
        return (
            f"[{self.severity}] Step {self.step}: "
            f"alignment={self.current_score:.3f}, "
            f"trend={self.trend:+.4f}/step -- "
            f"{self.recommendation}"
        )


@dataclass
class MonitorSnapshot:
    """Snapshot of monitor state at a given step."""
    step: int
    alignment_score: float
    trend: Optional[float]
    alert: Optional[DriftAlert]
    re_injected: bool = False


def semantic_similarity(text_a: str, text_b: str) -> float:
    """Compute similarity between two texts using TF-IDF cosine.

    This is the dependency-free stand-in for embedding similarity. It uses
    scikit-learn's TfidfVectorizer for term weighting and the same
    `cosine_similarity` the book describes, so the example runs offline
    and deterministically. See the module docstring for the trade-off and
    `embedding_similarity` for the production swap.

    Args:
        text_a: First text (typically the original specification).
        text_b: Second text (typically the agent's recent output).

    Returns:
        Cosine similarity score between 0.0 and 1.0.
    """
    if not text_a.strip() or not text_b.strip():
        return 0.0

    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        tfidf_matrix = vectorizer.fit_transform([text_a, text_b])
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        return float(sim[0][0])
    except ValueError:
        # If texts share no vocabulary at all
        return 0.0


def embedding_similarity(
    text_a: str,
    text_b: str,
    embed: Callable[[list[str]], "np.ndarray"],
) -> float:
    """Cosine similarity over embeddings, as described in the book.

    This is what `semantic_similarity` becomes in production. Pass the
    embedding function from your own stack (Chapter 9, Section 9.5): any
    callable that takes a list of strings and returns one vector per
    string. The cosine step is identical.

        from functools import partial
        score_fn = partial(embedding_similarity, embed=my_embedder)
        monitor = GoalDriftMonitor(spec, score_fn=score_fn)

    Args:
        text_a: First text (typically the original specification).
        text_b: Second text (typically the agent's recent output).
        embed: Callable mapping a list of texts to a 2-D array of vectors.

    Returns:
        Cosine similarity score, clamped to 0.0 through 1.0.
    """
    if not text_a.strip() or not text_b.strip():
        return 0.0
    vectors = np.asarray(embed([text_a, text_b]))
    sim = cosine_similarity(vectors[0:1], vectors[1:2])
    return float(min(1.0, max(0.0, sim[0][0])))


def linear_regression_slope(scores: list[float]) -> float:
    """Fit a line to the scores and return the slope.

    Uses numpy.polyfit for a degree-1 polynomial fit. A negative slope
    indicates declining alignment (drift). A slope near zero means stable.

    Args:
        scores: Sequence of alignment scores over time.

    Returns:
        Slope of the best-fit line (units: score change per step).
    """
    if len(scores) < 2:
        return 0.0
    x = np.arange(len(scores), dtype=float)
    coefficients = np.polyfit(x, scores, 1)
    return float(coefficients[0])


class GoalDriftMonitor:
    """Monitors agent alignment with original specification over time.

    At each step, the monitor computes a similarity score between the
    original specification and the agent's latest output. It fits a
    linear trend to the last N scores and fires an alert when the
    downward slope exceeds the threshold.

    Attributes:
        original_spec: The task specification the agent should follow.
        threshold: Negative slope below which an alert fires.
        window_size: Number of recent scores used for trend analysis.
        re_inject_interval: Steps between specification re-injections.
        score_fn: Scoring function, defaults to `semantic_similarity`.
            Pass an embedding-backed function in production (see
            `embedding_similarity`); the monitor logic does not change.
    """

    def __init__(
        self,
        original_spec: str,
        drift_threshold: float = 0.15,
        window_size: int = 5,
        re_inject_interval: int = 10,
        score_fn: Optional[Callable[[str, str], float]] = None,
    ) -> None:
        self.original_spec = original_spec
        self.threshold = drift_threshold
        self.window_size = window_size
        self.re_inject_interval = re_inject_interval
        self.score_fn = score_fn or semantic_similarity
        self.scores: list[float] = []
        self.alerts: list[DriftAlert] = []
        self.snapshots: list[MonitorSnapshot] = []

    def check(
        self, agent_output: str, step: int
    ) -> Optional[DriftAlert]:
        """Check alignment and return an alert if drift is detected.

        Args:
            agent_output: The agent's output at this step.
            step: The step number (0-indexed).

        Returns:
            DriftAlert if the trend exceeds the threshold, else None.
        """
        score = self.score_fn(self.original_spec, agent_output)
        self.scores.append(score)

        trend: Optional[float] = None
        alert: Optional[DriftAlert] = None

        if len(self.scores) >= self.window_size:
            window = self.scores[-self.window_size:]
            trend = linear_regression_slope(window)

            if trend < -self.threshold:
                alert = DriftAlert(
                    severity="WARNING" if trend > -0.3 else "CRITICAL",
                    step=step,
                    current_score=score,
                    trend=trend,
                    window_scores=list(window),
                    recommendation="Re-inject original specification",
                )
                self.alerts.append(alert)

        re_injected = (
            step > 0
            and step % self.re_inject_interval == 0
        )

        self.snapshots.append(
            MonitorSnapshot(
                step=step,
                alignment_score=score,
                trend=trend,
                alert=alert,
                re_injected=re_injected,
            )
        )

        return alert

    def current_alignment(self) -> float:
        """Return the most recent alignment score."""
        return self.scores[-1] if self.scores else 1.0

    def overall_trend(self) -> float:
        """Return the slope over all recorded scores."""
        return linear_regression_slope(self.scores)

    def summary(self) -> str:
        """Return a human-readable summary of the monitoring session."""
        if not self.scores:
            return "No data recorded"

        lines = [
            f"  Steps monitored: {len(self.scores)}",
            f"  Initial alignment: {self.scores[0]:.3f}",
            f"  Final alignment: {self.scores[-1]:.3f}",
            f"  Overall trend: {self.overall_trend():+.4f}/step",
            f"  Alerts fired: {len(self.alerts)}",
        ]
        if self.alerts:
            lines.append("  Alert history:")
            for a in self.alerts:
                lines.append(f"    {a}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Simulation helpers
# ---------------------------------------------------------------------------


def simulate_agent_outputs(
    spec: str,
    num_steps: int,
    drift_rate: float = 0.02,
    noise: float = 0.05,
    re_inject_at: Optional[set[int]] = None,
) -> list[str]:
    """Simulate agent outputs that gradually drift from the specification.

    The simulation starts with outputs closely related to the spec and
    progressively introduces unrelated vocabulary to simulate drift.

    Args:
        spec: The original task specification.
        num_steps: Number of agent steps to simulate.
        drift_rate: Rate at which off-topic words are introduced.
        noise: Random noise in drift (0 to 1).
        re_inject_at: Steps where specification is re-injected
                      (restoring alignment).

    Returns:
        List of simulated agent output strings.
    """
    re_inject_at = re_inject_at or set()
    spec_words = spec.split()

    # Off-topic vocabulary for simulating drift
    off_topic = [
        "banana", "submarine", "volcano", "penguin", "accordion",
        "telescope", "origami", "satellite", "cactus", "umbrella",
        "lighthouse", "kaleidoscope", "trampoline", "dinosaur",
        "carousel", "waterfall", "xylophone", "zeppelin", "bonsai",
        "catapult", "domino", "glacier", "hammock", "igloo",
    ]

    outputs: list[str] = []
    current_drift = 0.0

    for step in range(num_steps):
        if step in re_inject_at:
            # Re-injection resets drift
            current_drift = max(0.0, current_drift - 0.4)

        # Calculate how much of the output is on-topic vs off-topic
        on_topic_ratio = max(0.1, 1.0 - current_drift)
        num_words = len(spec_words)
        num_on_topic = max(2, int(num_words * on_topic_ratio))
        num_off_topic = max(0, num_words - num_on_topic)

        # Build the output
        on_words = random.sample(spec_words, min(num_on_topic, len(spec_words)))
        off_words = random.choices(off_topic, k=num_off_topic)
        all_words = on_words + off_words
        random.shuffle(all_words)

        outputs.append(" ".join(all_words))

        # Increase drift
        current_drift += drift_rate + random.uniform(-noise, noise)
        current_drift = max(0.0, min(1.0, current_drift))

    return outputs


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------


def _section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    random.seed(42)
    np.random.seed(42)

    print("=== Goal Drift Monitor Demo ===")
    print("Chapter 12, Section 12.5\n")
    print("Similarity is TF-IDF cosine so the demo runs offline and")
    print("deterministically. See the module docstring for how to swap in")
    print("your embedding model.\n")

    # ------------------------------------------------------------------
    # Define the original specification
    # ------------------------------------------------------------------
    _section("1. Original Task Specification")

    spec = (
        "Refactor the user authentication module to use JWT tokens "
        "instead of session cookies. Update the login endpoint, "
        "add token refresh logic, write unit tests for the auth "
        "service, and update the API documentation. Do not modify "
        "any other modules or add new dependencies."
    )
    print(f"  {spec}")

    # ------------------------------------------------------------------
    # Scenario A: No mitigation (drift without re-injection)
    # ------------------------------------------------------------------
    _section("2. Scenario A: 50 Steps WITHOUT Mitigation")

    outputs_no_mitigation = simulate_agent_outputs(
        spec, num_steps=50, drift_rate=0.025, noise=0.03,
    )

    # The class default threshold (0.15/step) matches the book's listing
    # and is tuned for the sharp drops real sessions show. This simulation
    # drifts gently (window slopes stay between -0.02 and -0.08/step), so
    # both scenarios pass 0.06 to make the alerting visible.
    demo_threshold = 0.06

    monitor_a = GoalDriftMonitor(
        original_spec=spec,
        drift_threshold=demo_threshold,
        window_size=5,
    )

    for step, output in enumerate(outputs_no_mitigation):
        alert = monitor_a.check(output, step)
        if alert:
            print(f"  {alert}")

    print()
    print(monitor_a.summary())

    # ------------------------------------------------------------------
    # Scenario B: With specification re-injection every 10 steps
    # ------------------------------------------------------------------
    _section("3. Scenario B: 50 Steps WITH Re-Injection Every 10 Steps")

    re_inject_steps = {10, 20, 30, 40}
    outputs_with_mitigation = simulate_agent_outputs(
        spec, num_steps=50, drift_rate=0.025, noise=0.03,
        re_inject_at=re_inject_steps,
    )

    monitor_b = GoalDriftMonitor(
        original_spec=spec,
        drift_threshold=demo_threshold,
        window_size=5,
        re_inject_interval=10,
    )

    for step, output in enumerate(outputs_with_mitigation):
        alert = monitor_b.check(output, step)
        if alert:
            print(f"  {alert}")

    print()
    print(monitor_b.summary())

    # ------------------------------------------------------------------
    # Compare the two scenarios
    # ------------------------------------------------------------------
    _section("4. Comparison")

    scores_a = monitor_a.scores
    scores_b = monitor_b.scores

    print(f"  {'Metric':<30s} {'No Mitigation':>15s} {'Re-Injection':>15s}")
    print(f"  {'-' * 60}")
    print(f"  {'Initial alignment':<30s} {scores_a[0]:>15.3f} {scores_b[0]:>15.3f}")
    print(f"  {'Final alignment':<30s} {scores_a[-1]:>15.3f} {scores_b[-1]:>15.3f}")
    print(f"  {'Min alignment':<30s} {min(scores_a):>15.3f} {min(scores_b):>15.3f}")
    print(f"  {'Mean alignment':<30s} {np.mean(scores_a):>15.3f} {np.mean(scores_b):>15.3f}")
    print(f"  {'Overall trend (slope)':<30s} "
          f"{monitor_a.overall_trend():>+15.4f} "
          f"{monitor_b.overall_trend():>+15.4f}")
    print(f"  {'Alerts fired':<30s} "
          f"{len(monitor_a.alerts):>15d} "
          f"{len(monitor_b.alerts):>15d}")

    # ------------------------------------------------------------------
    # Show alignment scores at key points
    # ------------------------------------------------------------------
    _section("5. Alignment Score Timeline (every 5 steps)")

    print(f"  {'Step':>6s}  {'No Mitigation':>15s}  {'Re-Injection':>15s}  {'Event':<20s}")
    print(f"  {'-' * 62}")
    for step in range(0, 50, 5):
        event = ""
        if step in re_inject_steps:
            event = "<- re-injected"
        print(f"  {step:>6d}  {scores_a[step]:>15.3f}  {scores_b[step]:>15.3f}  {event}")

    # ------------------------------------------------------------------
    # Demonstrate semantic_similarity directly
    # ------------------------------------------------------------------
    _section("6. Semantic Similarity Examples")

    examples = [
        (
            "Refactor JWT authentication with token refresh",
            "Very related to spec",
        ),
        (
            "Update login endpoint and write auth tests",
            "Partially related to spec",
        ),
        (
            "Optimize database query performance for reporting",
            "Unrelated to spec (scope creep)",
        ),
        (
            "banana submarine volcano penguin accordion",
            "Completely unrelated (noise)",
        ),
    ]

    for text, label in examples:
        score = semantic_similarity(spec, text)
        print(f"  {score:.3f}  {label}")
        print(f"         \"{text}\"")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    _section("Summary")
    print("  Goal drift is measurable. Over 50 steps without mitigation,")
    print("  alignment decays steadily and the monitor fires repeated")
    print("  alerts. Specification re-injection at regular intervals pulls")
    print("  alignment back to the specification each time, so the decay")
    print("  never compounds (compare the mean alignment above), and the")
    print("  alerts that do fire recover at the next re-injection.")
    print()
    print("  Detection uses:")
    print("    - TF-IDF cosine similarity (stands in for embeddings here)")
    print("    - Linear regression slope on a sliding window")
    print("    - Configurable thresholds and re-injection intervals")
    print()
    print("  In production, pass an embedding-backed score_fn to")
    print("  GoalDriftMonitor. TF-IDF measures vocabulary overlap, so an")
    print("  on-task paraphrase can score low and an off-task output that")
    print("  reuses the spec's words can score high.")
    print("\n=== Demo complete ===")
