"""
Tests for Apprentice Pattern capture (Exercise 2).
"""
import pytest
from capture import ApprenticeCapture
from memory_core import DevMemory
from config import DevMemoryConfig


@pytest.fixture
def capture():
    config = DevMemoryConfig(project_name="test-capture")
    memory = DevMemory(config)
    return ApprenticeCapture(memory, agent_id="debug-agent")


def test_apprentice_captures_debugging_session(capture):
    """Simulate a debugging session and verify capture."""
    capture.start_session("debugging")

    capture.record_action("command", "docker logs api-service")
    capture.record_action("search", "timeout error")
    capture.record_action("file_open", "config/timeouts.yaml")
    capture.record_action("edit", "config/timeouts.yaml")

    result = capture.end_session("success")

    assert "heuristic" in result
    assert result["heuristic"]["first_check"] == "docker logs api-service"
    assert "infrastructure" in result["heuristic"]["pattern"].lower()


def test_end_session_without_start_returns_empty(capture):
    """Verify end_session returns {} if no session was started."""
    result = capture.end_session("success")
    assert result == {}


def test_record_action_without_session_is_safe(capture):
    """Verify record_action is safe to call without a session."""
    capture.record_action("command", "docker logs api")
    # Should not raise an error
