"""
Tests for memory scopes (Exercise 3).
"""
import pytest
from scopes import ScopedMemory
from config import DevMemoryConfig


@pytest.fixture
def scoped():
    config = DevMemoryConfig(project_name="test-scopes")
    return ScopedMemory(config)


def test_agent_scope_isolation(scoped):
    """Verify agents can't see each other's private memories."""
    scoped.remember_private(
        "Debug agent: retries fix timeout issues",
        agent_id="debug-agent"
    )
    scoped.remember_private(
        "Review agent: team prefers early returns",
        agent_id="review-agent"
    )

    debug_results = scoped.recall_for_agent(
        "timeout fixes", agent_id="debug-agent"
    )
    assert len(debug_results["agent"]) > 0


def test_shared_scope_visible_to_all(scoped):
    """Verify shared memories are visible to all agents."""
    scoped.remember_shared(
        "Team decision: use PostgreSQL for ACID compliance",
        agent_id="debug-agent"
    )

    for agent in ["debug-agent", "review-agent", "deploy-agent"]:
        results = scoped.recall_for_agent(
            "database decision", agent_id=agent
        )
        assert len(results["shared"]) > 0


def test_recall_returns_both_scopes(scoped):
    """Verify recall_for_agent returns both agent and shared results."""
    scoped.remember_private("Private memory", agent_id="test-agent")
    scoped.remember_shared("Shared memory", agent_id="test-agent")

    results = scoped.recall_for_agent("memory", agent_id="test-agent")
    assert "agent" in results
    assert "shared" in results
