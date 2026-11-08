"""
Tool-using invocation: a worked solution to Exercise 4.2 in Chapter 4.

Extends the synchronous invocation pattern from Listing 4-7
(sync_invocation.py) with the two capabilities the exercise asks for:

1. The agent reads the Commands section of AGENTS.md, so it knows which
   command this project uses to run tests instead of guessing.
2. After generating code, the agent automatically calls a run_tests() tool
   and returns a combined result object holding both the generated tests
   and the test output.

Usage:
    python tool_using_invocation.py

Like the other files in this directory, this is a pattern illustration, not
an SDK integration: run_tests() simulates a test run instead of shelling out,
so the file runs anywhere with no dependencies or side effects. The parts
worth copying are the AGENTS.md Commands parsing and the generate-then-verify
loop.
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from pathlib import Path

# Minimal AGENTS.md used only when no real file is found, so the demo still
# illustrates the parsing logic.
FALLBACK_AGENTS_MD = """\
# AGENTS.md

## Persona

You are a senior Python backend engineer.

## Commands

- Run tests: `pytest`
- Run full check: `make format lint test`
"""


@dataclass
class CombinedResult:
    """Result object combining generated tests with their execution output.

    This is the shape Exercise 4.2 asks for: the caller gets both what the
    agent wrote and the proof (or refutation) that it works, in one object.
    """
    status: str  # "success", "tests_failed", "error"
    tests: Optional[str] = None
    test_command: Optional[str] = None
    test_output: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


def load_agents_md(path: str = "AGENTS.md") -> str:
    """Load AGENTS.md from the working directory, or fall back to the
    chapter's template in ../agents-md/, or to an embedded minimal sample."""
    candidates = [
        Path(path),
        Path(__file__).resolve().parent.parent / "agents-md" / "AGENTS.md",
    ]
    for candidate in candidates:
        if candidate.exists():
            print(f"Loaded agent instructions from {candidate}")
            return candidate.read_text()
    print("No AGENTS.md found; using the embedded fallback sample.")
    return FALLBACK_AGENTS_MD


def parse_commands_section(agents_md: str) -> Dict[str, str]:
    """
    Extract the Commands section from AGENTS.md as a label -> command map.

    Expects the convention used throughout the chapter:

        ## Commands

        - Run tests: `pytest`
        - Run full check: `make format lint test`

    Returns:
        Dict mapping the bullet label (lowercased) to the backtick-quoted
        command, e.g. {"run tests": "pytest"}. Empty if no section is found.
    """
    commands: Dict[str, str] = {}
    in_commands = False
    for line in agents_md.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            in_commands = stripped.lower() == "## commands"
            continue
        if in_commands and stripped.startswith("- ") and ":" in stripped:
            label, _, remainder = stripped[2:].partition(":")
            command = remainder.strip().strip("`").strip()
            if command:
                commands[label.strip().lower()] = command
    return commands


def run_tests(command: str) -> Dict[str, Any]:
    """
    Test-runner tool the agent calls after generating code.

    Simulated: a real implementation would run `command` in a sandbox
    (subprocess with a timeout, restricted filesystem) and capture the exit
    code and output. The return shape is the part that transfers.
    """
    print(f"[tool:run_tests] Executing: {command}")
    return {
        "command": command,
        "exit_code": 0,
        "output": "1 passed in 0.01s (simulated)",  # matches the one test Agent.run generates
    }


class Agent:
    """
    Minimal tool-using agent, extending the Agent from sync_invocation.py.

    The difference from the synchronous pattern: after generating code, the
    agent does not stop. It calls its test-runner tool with the command the
    project declared in AGENTS.md, and folds the tool output into the result.
    """

    def __init__(self, role: str, goal: str, system: str, model: str = "default"):
        self.role = role
        self.goal = goal
        self.system = system
        self.model = model
        self.commands = parse_commands_section(system)

    def run(self, input: str, metadata: Optional[Dict[str, Any]] = None) -> CombinedResult:
        """Generate tests for the input code, then verify them with run_tests()."""
        metadata = metadata or {}
        print(f"Agent '{self.role}' executing goal: {self.goal}")
        if metadata:
            print(f"Metadata: {metadata}")

        # 1. Generate the tests. In a real implementation this is the LLM
        #    call, with self.system (AGENTS.md) as the system prompt.
        generated_tests = (
            "def test_login_rejects_empty_credentials():\n"
            "    with pytest.raises(ValueError):\n"
            "        login('', '')\n"
        )

        # 2. Look up the project's test command from the Commands section of
        #    AGENTS.md. Falling back to pytest keeps the demo running against
        #    an AGENTS.md that has no Commands section.
        test_command = self.commands.get("run tests", "pytest")

        # 3. Automatically call the run_tests() tool: the agent verifies its
        #    own work instead of only proposing code.
        test_result = run_tests(test_command)

        return CombinedResult(
            status="success" if test_result["exit_code"] == 0 else "tests_failed",
            tests=generated_tests,
            test_command=test_result["command"],
            test_output=test_result["output"],
            metadata=metadata,
        )


def main():
    """Demonstrate the tool-using invocation pattern from Exercise 4.2."""
    system_instructions = load_agents_md()

    agent = Agent(
        role="QA Engineer",
        goal="Write tests for the login function and run them",
        system=system_instructions,
    )
    print(f"Commands parsed from AGENTS.md: {agent.commands}")

    source_code = (
        "def login(username: str, password: str) -> bool:\n"
        "    if not username or not password:\n"
        "        raise ValueError('Username and password required')\n"
        "    ...\n"
    )

    result = agent.run(
        input=source_code,
        metadata={"file": "app/auth/login.py", "ticket_id": "AUTH-123"},
    )

    print("\nCombined result object:")
    print(f"  status:       {result.status}")
    print(f"  test_command: {result.test_command}")
    print(f"  test_output:  {result.test_output}")
    print(f"  tests:\n{result.tests}")


if __name__ == "__main__":
    main()
