"""
End-to-end demonstration of DevMemory.

Run this after completing all exercises to see the full system in action.
Reference: Chapter 9, Section 9.6
"""
from config import DevMemoryConfig
from memory_core import DevMemory, PatternMiner
from capture import ApprenticeCapture
from scopes import ScopedMemory
from trust import filter_by_trust


def main():
    config = DevMemoryConfig(project_name="my-api-service")
    scoped = ScopedMemory(config)

    # Simulate three debugging sessions (Apprentice Pattern)
    capture = ApprenticeCapture(
        DevMemory(config), agent_id="debug-agent"
    )

    for i in range(3):
        capture.start_session("debugging")
        capture.record_action("command", "docker logs api-service")
        capture.record_action("search", "timeout error")
        capture.record_action("file_open", "config/timeouts.yaml")
        capture.record_action("edit", "config/timeouts.yaml")
        capture.end_session("success")

    # Run Pattern Mining to consolidate episodes
    miner = PatternMiner(DevMemory(config), config)
    patterns = miner.mine(agent_id="debug-agent")

    print(f"Discovered {len(patterns)} patterns:")
    for p in patterns:
        print(f"  {p['knowledge']} (confidence: {p['confidence']})")

    # Share a decision to project scope
    scoped.remember_shared(
        "Team decision: use retry with exponential backoff for all "
        "external service calls. Max 3 retries, base delay 100ms.",
        agent_id="debug-agent",
        metadata={"type": "decision"}
    )

    # Any agent can recall shared decisions
    results = scoped.recall_for_agent(
        "how to handle service timeouts",
        agent_id="deploy-agent"
    )

    trusted = filter_by_trust(results["shared"], min_trust=0.3)
    for m in trusted:
        print(f"  [{m['trust_score']:.2f}] {m['memory']}")


if __name__ == "__main__":
    main()
