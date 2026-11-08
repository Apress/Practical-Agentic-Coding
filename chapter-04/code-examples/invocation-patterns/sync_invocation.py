"""
Listing 4-7: Synchronous agent invocation with a coding persona

This example demonstrates how to:
1. Load system instructions from AGENTS.md
2. Create an agent with a specific role and goal
3. Execute the agent synchronously
4. Handle the result

Usage:
    python sync_invocation.py

Note: this is a pattern illustration, not an SDK integration. The 'Agent' and
'load_agents_md' definitions below stand in for whatever your agent framework
provides, so the file runs with no dependencies. The shape of the call is the
part worth copying.
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AgentResult:
    """Result from agent execution."""
    status: str  # "success", "blocked", "error"
    code: Optional[str] = None
    error: Optional[str] = None
    question: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


def load_agents_md(path: str = "AGENTS.md") -> str:
    """
    Load system instructions from AGENTS.md file.

    Args:
        path: Path to the AGENTS.md file

    Returns:
        String containing the system instructions

    Raises:
        FileNotFoundError: If AGENTS.md doesn't exist
    """
    agents_path = Path(path)
    if not agents_path.exists():
        raise FileNotFoundError(
            f"AGENTS.md not found at {path}. "
            "Please create one or specify the correct path."
        )
    return agents_path.read_text()


class Agent:
    """
    Minimal agent used to demonstrate the invocation pattern.

    Every agent framework has its own class name, constructor signature, and
    import path, and they change between releases. What transfers is the shape
    of the call: load the persona and rules from AGENTS.md, set a role and a
    goal, pass the context, then branch on the result status. Check the current
    documentation for whichever framework you use, and map its API onto that
    shape rather than copying the class below.
    """

    def __init__(
        self,
        role: str,
        goal: str,
        system: str,
        model: str = "default"
    ):
        """
        Initialize an agent with role, goal, and system instructions.

        Args:
            role: The agent's role (e.g., "QA Engineer")
            goal: Specific task to accomplish
            system: System instructions from AGENTS.md
            model: Model to use for execution
        """
        self.role = role
        self.goal = goal
        self.system = system
        self.model = model

    def run(
        self,
        input: str,
        metadata: Optional[Dict[str, Any]] = None,
        timeout: int = 60
    ) -> AgentResult:
        """
        Execute the agent synchronously.

        Args:
            input: Input data (e.g., source code)
            metadata: Additional context (file path, ticket ID, etc.)
            timeout: Maximum execution time in seconds

        Returns:
            AgentResult with status and output
        """
        # In a real implementation, this would:
        # 1. Format the prompt with role, goal, system, and input
        # 2. Call the LLM API
        # 3. Parse and return the result

        # Conceptual implementation for demonstration
        print(f"Agent '{self.role}' executing goal: {self.goal}")
        print(f"Using model: {self.model}")
        print(f"Input size: {len(input)} characters")
        if metadata:
            print(f"Metadata: {metadata}")

        # Simulated successful result
        return AgentResult(
            status="success",
            code="# Generated test code would appear here",
            metadata={"execution_time_ms": 1500}
        )


def main():
    """
    Main function demonstrating synchronous agent invocation.

    This pattern is from Listing 4-7 in Chapter 4.
    """
    # Load persona + project rules from AGENTS.md
    try:
        system_instructions = load_agents_md(path="AGENTS.md")
    except FileNotFoundError as e:
        print(f"Warning: {e}")
        print("Using default instructions for demonstration...")
        system_instructions = """
        You are a senior Python backend engineer.
        You prefer clean, readable code over clever one-liners.
        Always write thorough tests.
        """

    # Create the agent
    agent = Agent(
        role="QA Engineer",
        goal="Write tests for the login function",
        system=system_instructions,
    )

    # Load source code to analyze
    # In practice, this would be a real file
    source_code = '''
def login(username: str, password: str) -> bool:
    """Authenticate a user with username and password."""
    if not username or not password:
        raise ValueError("Username and password required")

    user = get_user_by_username(username)
    if not user:
        return False

    return verify_password(password, user.password_hash)
'''

    # Synchronous execution
    result = agent.run(
        input=source_code,
        metadata={
            "file": "app/auth/login.py",
            "ticket_id": "AUTH-123"
        },
    )

    # Handle the result
    if result.status == "success":
        print("\nTests generated successfully!")
        print("-" * 50)
        print(result.code)
    elif result.status == "blocked":
        print(f"\nAgent needs clarification: {result.question}")
    else:
        print(f"\nAgent failed: {result.error}")


if __name__ == "__main__":
    main()
