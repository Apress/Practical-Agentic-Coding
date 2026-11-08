"""
Tests for DevMemory core (Exercise 1).
"""
import pytest
from memory_core import DevMemory
from config import DevMemoryConfig


@pytest.fixture
def memory():
    config = DevMemoryConfig(project_name="test-memory")
    return DevMemory(config)


def test_remember_stores_content(memory):
    """Verify remember() stores content and returns a result."""
    result = memory.remember(
        "Fixed NullPointerException in payment service",
        agent_id="debug-agent",
        metadata={"type": "debugging", "outcome": "success"}
    )
    assert result is not None


def test_recall_finds_stored_memory(memory):
    """Verify recall() finds previously stored memory."""
    memory.remember(
        "Fixed NullPointerException in payment service by adding "
        "null check on config.getServiceUrl()",
        agent_id="debug-agent",
        metadata={"type": "debugging", "outcome": "success"}
    )

    results = memory.recall(
        "payment service null pointer",
        agent_id="debug-agent"
    )

    assert len(results) > 0


def test_recall_all_returns_agent_memories(memory):
    """Verify recall_all() returns all memories for an agent."""
    # infer=False stores these verbatim. With inference on, Mem0 asks the model
    # to extract facts first, and its extraction prompt tells the model to
    # return an empty list for content-free input ("Hi." is its own example),
    # so whether "Memory one" gets stored at all would depend on the model.
    memory.remember("Memory one", agent_id="test-agent", infer=False)
    memory.remember("Memory two", agent_id="test-agent", infer=False)

    results = memory.recall_all(agent_id="test-agent")
    assert len(results) >= 2
