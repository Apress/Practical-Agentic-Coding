"""
Knowledge capture: Apprentice Pattern implementation.

Observes developer sessions and extracts implicit heuristics.
Reference: Chapter 9, Section 9.6 (Phase 2)
"""
from dataclasses import dataclass, field
from datetime import datetime
from memory_core import DevMemory


@dataclass
class Action:
    """A single developer action in a session."""
    type: str          # "file_open", "search", "edit", "command"
    target: str        # File path, search query, or command
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Session:
    """A recorded development session."""
    session_type: str  # "debugging", "feature", "review"
    actions: list[Action] = field(default_factory=list)
    outcome: str = ""
    started: datetime = field(default_factory=datetime.utcnow)


class ApprenticeCapture:
    """Captures tacit knowledge from developer sessions.

    Watches what a developer does during debugging, code review,
    or feature work, then extracts the implicit heuristic that
    guided their decisions.
    """

    def __init__(self, memory: DevMemory, agent_id: str):
        self.memory = memory
        self.agent_id = agent_id
        self.current_session: Session = None

    def start_session(self, session_type: str) -> None:
        """Begin recording a new session."""
        self.current_session = Session(session_type=session_type)

    def record_action(self, action_type: str, target: str) -> None:
        """Record a developer action during the session."""
        if self.current_session is None:
            return
        self.current_session.actions.append(
            Action(type=action_type, target=target)
        )

    def end_session(self, outcome: str) -> dict:
        """End session. Extract and store the implicit heuristic.

        TODO (Exercise 2): Implement this method.

        Steps:
        1. Check if current_session is None, return {} if so
        2. Set outcome on current_session
        3. Save session reference and set self.current_session = None
        4. Call self._extract_heuristic(session) to get the heuristic
        5. Store as episodic memory using self.memory.remember() with:
           - content: formatted string with session type, summary, outcome, pattern
           - agent_id: self.agent_id
           - infer=False: store verbatim so identical sessions stay
             countable for Pattern Mining
           - metadata: type="episode", session_type, outcome, action_count, first_check
        6. Return dict with "episode" and "heuristic" keys

        Args:
            outcome: Session outcome ("success", "failure", "partial").

        Returns:
            dict: Contains "episode" (Mem0 result) and "heuristic" (extracted pattern).
        """
        # TODO: Implement session ending and knowledge extraction
        raise NotImplementedError("TODO: Implement end_session() in Exercise 2")

    def _extract_heuristic(self, session: Session) -> dict:
        """Extract implicit debugging heuristic from session actions.

        TODO (Exercise 2): Implement this method.

        Steps:
        1. Get first 3 actions as first_checks
        2. Collect search targets (actions where type == "search")
        3. Collect edit targets (actions where type == "edit")
        4. Build summary string from first_check, first search, last edit
        5. Call self._derive_pattern() for the reusable pattern
        6. Return dict with summary, pattern, first_check, searches

        Args:
            session: The completed session to analyze.

        Returns:
            dict: Heuristic with "summary", "pattern", "first_check", "searches".
        """
        # TODO: Implement heuristic extraction
        raise NotImplementedError("TODO: Implement _extract_heuristic() in Exercise 2")

    def _derive_pattern(
        self, first_checks: list[Action], searches: list[str]
    ) -> str:
        """Derive a reusable pattern from session data.

        This method is provided for you. It classifies the debugging
        approach based on what the developer checked first.

        Args:
            first_checks: First few actions in the session.
            searches: Search queries used during session.

        Returns:
            str: Human-readable pattern description.
        """
        check_types = [a.type for a in first_checks]
        if "command" in check_types:
            return "Check infrastructure (logs, config) before code"
        if any("test" in s.lower() for s in searches):
            return "Run tests to isolate failure before reading code"
        return "Start with file inspection, then search for patterns"
