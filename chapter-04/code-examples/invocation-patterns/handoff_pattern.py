"""
Agent handoff pattern: agent-to-agent delegation.

Extended example for Chapter 4. Not a listing in the book; it takes the A2A
delegation idea from Section 4.2 and shows it as code, so the "hire the
security agent" scenario in that section has something concrete behind it.

This is the "transfer" pattern: a specialist agent hands the task to another
agent when the work moves outside its domain, rather than attempting work it
was not built for.

Key concepts:
- Agents are specialists, not generalists
- Handoff happens when the required domain expertise changes
- The transfer itself is an explicit, inspectable step

Usage:
    python handoff_pattern.py

The Agent class here is deliberately minimal and simulates the model's
transfer decision with keyword matching, so the pattern is readable without an
SDK dependency. Real agent frameworks formalize this handoff; the decision of
when to transfer is made by the model, not by a keyword list. Chapter 10 builds
a coordinated agent team for real.
"""

from typing import Callable, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class Agent:
    """
    Minimal agent used to demonstrate the handoff pattern.

    This implementation shows how agents can:
    1. Have specialized instructions
    2. Use functions/tools
    3. Hand off to other agents, either instead of working (a task outside
       their domain) or after finishing their own work (a pipeline stage)
    """
    name: str
    instructions: str
    functions: List[Callable] = field(default_factory=list)
    # Pipeline continuation: called after this agent finishes its own work,
    # handing the task to the next stage. None makes the agent terminal.
    handoff_after_work: Optional[Callable] = None

    def process(self, message: str) -> str:
        """
        Process a message and potentially hand off to another agent.

        In a real implementation, this would:
        1. Send message to LLM with instructions
        2. Parse response for tool calls
        3. Execute handoff if transfer function called

        Args:
            message: User message to process

        Returns:
            Response from this agent or delegated agent
        """
        print(f"\n[{self.name}] Processing: {message[:50]}...")

        # Check if any function is a transfer function
        for func in self.functions:
            if func.__name__.startswith("transfer_to_"):
                # Simulated decision to transfer
                if self._should_transfer(message, func):
                    target_agent = func()
                    print(f"[{self.name}] Handing off to {target_agent.name}")
                    return target_agent.process(message)

        # Process normally, then continue the pipeline if one is configured
        response = self._generate_response(message)
        if self.handoff_after_work is not None:
            target_agent = self.handoff_after_work()
            print(f"[{self.name}] Work complete. Handing off to {target_agent.name}")
            return f"{response}\n{target_agent.process(message)}"
        return response

    def _should_transfer(self, message: str, transfer_func: Callable) -> bool:
        """
        Determine if a transfer should occur.

        In practice, the LLM would make this decision based on:
        - The message content
        - The agent's instructions
        - The available transfer functions

        Args:
            message: The message being processed
            transfer_func: The potential transfer function

        Returns:
            True if transfer should occur
        """
        # Simulated transfer logic (keywords lowercase: message is lowercased)
        security_keywords = ["security", "vulnerability", "audit", "compliance", "owasp"]
        if any(keyword in message.lower() for keyword in security_keywords):
            if "security" in transfer_func.__name__:
                return True
        return False

    def _generate_response(self, message: str) -> str:
        """Generate a response for the message."""
        return f"[{self.name}] Completed processing."


# ============================================================================
# Agent definitions
# ============================================================================

# Forward declaration for transfer function
security_agent: Optional[Agent] = None


def transfer_to_security_agent() -> Agent:
    """
    Handoff to the security specialist for compliance review.

    This function is called by the coding agent when it detects
    that a task requires security expertise.

    Returns:
        The security agent instance
    """
    global security_agent
    if security_agent is None:
        raise RuntimeError("Security agent not initialized")
    return security_agent


# Create the coding agent (primary agent)
coding_agent = Agent(
    name="Coding Specialist",
    instructions="""You write high-quality Python code.
    If a task requires a security audit, transfer the user.""",
    functions=[transfer_to_security_agent]
)

# Create the security agent (specialist)
security_agent = Agent(
    name="Security Specialist",
    instructions="""You perform SAST analysis and OWASP compliance checks.
    You review code for:
    - SQL injection vulnerabilities
    - Cross-site scripting (XSS)
    - Authentication weaknesses
    - Sensitive data exposure
    - Security misconfigurations""",
    functions=[]  # Terminal agent - no further handoffs
)


# ============================================================================
# Extended Example: Multi-Agent Pipeline
# ============================================================================

# Additional agents for a complete pipeline
compliance_agent: Optional[Agent] = None
deploy_agent: Optional[Agent] = None


def transfer_to_compliance_agent() -> Agent:
    """Transfer to compliance agent for policy validation."""
    global compliance_agent
    if compliance_agent is None:
        raise RuntimeError("Compliance agent not initialized")
    return compliance_agent


def transfer_to_deploy_agent() -> Agent:
    """Transfer to deploy agent for production deployment."""
    global deploy_agent
    if deploy_agent is None:
        raise RuntimeError("Deploy agent not initialized")
    return deploy_agent


def transfer_to_security_agent_extended() -> Agent:
    """Handoff to the pipeline variant of the security specialist."""
    return security_agent_extended


# Pipeline variant of the security agent: it does its own review first, then
# hands off to compliance (handoff_after_work), rather than transferring
# instead of working.
security_agent_extended = Agent(
    name="Security Specialist",
    instructions="""You perform SAST analysis and OWASP compliance checks.
    After completing security review, transfer to compliance for policy validation.""",
    handoff_after_work=transfer_to_compliance_agent
)

compliance_agent = Agent(
    name="Compliance Specialist",
    instructions="""You validate code against company policies:
    - SOC2 requirements
    - GDPR compliance
    - Internal security policies
    After compliance check, transfer to deploy agent if approved.""",
    handoff_after_work=transfer_to_deploy_agent
)

deploy_agent = Agent(
    name="Deployment Specialist",
    instructions="""You handle production deployments:
    - Canary rollouts
    - Blue-green deployments
    - Rollback procedures
    This is a terminal agent - no further handoffs.""",
    functions=[]
)


# ============================================================================
# Demonstration
# ============================================================================

def demo_simple_handoff():
    """Demonstrate simple coding -> security handoff."""
    print("=" * 60)
    print("DEMO: Simple Handoff (Coding -> Security)")
    print("=" * 60)

    # Regular coding task - no handoff
    result = coding_agent.process(
        "Write a function to calculate the sum of two numbers"
    )
    print(f"Result: {result}")

    # Security-related task - triggers handoff
    result = coding_agent.process(
        "Please perform a security audit of the authentication module"
    )
    print(f"Result: {result}")


def demo_pipeline_handoff():
    """Demonstrate multi-agent pipeline handoff, executed end to end."""
    print("\n" + "=" * 60)
    print("DEMO: Pipeline Handoff (Coding -> Security -> Compliance -> Deploy)")
    print("=" * 60)

    # The pipeline's coding agent transfers security work to the extended
    # security agent, which chains onward through compliance to deployment
    # via each agent's handoff_after_work.
    pipeline_coding = Agent(
        name="Coding Specialist",
        instructions="Write code and hand off security tasks.",
        functions=[transfer_to_security_agent_extended]
    )

    result = pipeline_coding.process(
        "Run the security audit for the payment feature and take it to deployment"
    )
    print(f"\nPipeline result:\n{result}")


def demo_conversation_context():
    """Demonstrate conversation context preservation during handoff."""
    print("\n" + "=" * 60)
    print("DEMO: Context Preservation")
    print("=" * 60)

    @dataclass
    class ConversationContext:
        """Context that travels with the conversation across agents."""
        original_request: str
        code_changes: List[str] = field(default_factory=list)
        security_findings: List[str] = field(default_factory=list)
        compliance_status: Optional[str] = None
        approvals: List[str] = field(default_factory=list)

    # Create context
    context = ConversationContext(
        original_request="Add OAuth2 login to the API",
        code_changes=[
            "Added oauth_handler.py",
            "Modified auth/routes.py",
            "Added tests/test_oauth.py"
        ]
    )

    print(f"Original Request: {context.original_request}")
    print(f"Code Changes: {context.code_changes}")
    print("\nContext travels through the pipeline:")
    print("  Coding -> Security (inherits code changes)")
    print("  Security -> Compliance (inherits security findings)")
    print("  Compliance -> Deploy (inherits approvals)")


def main():
    """Run all demonstrations."""
    demo_simple_handoff()
    demo_pipeline_handoff()
    demo_conversation_context()

    print("\n" + "=" * 60)
    print("KEY TAKEAWAYS")
    print("=" * 60)
    print("""
1. Agents are SPECIALISTS, not generalists
   - Each agent has deep expertise in one domain
   - Better results than one "do-everything" agent

2. Handoffs are EXPLICIT
   - Transfer functions define valid transitions
   - No arbitrary agent-to-agent communication

3. Context TRAVELS with the conversation
   - Previous agent's findings inform next agent
   - Full audit trail maintained

4. Some agents are TERMINAL
   - Deploy agent doesn't hand off further
   - Prevents infinite handoff loops
""")


if __name__ == "__main__":
    main()
