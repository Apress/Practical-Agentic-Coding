"""
Composable validators for agent tool calls (reference solution).

This is the completed version of `starter/governance/validators.py`. It
implements the composable validator pattern from Chapter 12, Section 12.3.
Each validator targets one specific risk (path traversal, credential
exposure, absolute boundaries) and validators chain into pipelines.

For a production-grade AbsoluteBoundary that parses SQL and shell instead
of matching substrings, see
`companion-repo/chapter-12/code-examples/composable_validators.py`.

PathRestrictionValidator follows the book's Section 12.8 listing and matches
raw prefixes with startswith(), so on its own it does not stop ".."
traversal (/src/../etc/passwd) or a sibling prefix (/srcevil/). The version in
the same code-examples file normalizes paths and matches whole components.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ToolCall:
    """Represents a single tool invocation by an agent."""

    tool_name: str
    params: dict[str, Any] = field(default_factory=dict)
    agent_id: str = "default"
    estimated_cost: float = 0.01

    async def execute(self) -> ToolResult:
        """Simulate tool execution. In production this calls the real tool."""
        return ToolResult(blocked=False, output=f"Executed {self.tool_name}")


@dataclass
class ToolResult:
    """Result of a tool invocation, either executed or blocked."""

    blocked: bool = False
    reason: str = ""
    output: str = ""


@dataclass
class ValidationResult:
    """Outcome of a single validator check."""

    passed: bool = False
    blocked: bool = False
    reason: str = ""


# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------

class Validator:
    """Base class for all validators."""

    def check(self, tool_call: ToolCall) -> ValidationResult:
        raise NotImplementedError("Subclasses must implement check()")


# ---------------------------------------------------------------------------
# ValidatorPipeline
# ---------------------------------------------------------------------------

class ValidatorPipeline:
    """Composable safety validators for agent tool calls.

    Validators are chained and run in order. The first validator that
    blocks the call short-circuits the pipeline.
    """

    def __init__(self) -> None:
        self.validators: list[Validator] = []

    def add(self, validator: Validator) -> ValidatorPipeline:
        """Add a validator to the pipeline. Returns self for chaining."""
        self.validators.append(validator)
        return self

    async def validate(self, tool_call: ToolCall) -> ValidationResult:
        """Run all validators in order. Return the first blocking result."""
        for validator in self.validators:
            result = validator.check(tool_call)
            if result.blocked:
                return result
        return ValidationResult(passed=True)


# ---------------------------------------------------------------------------
# PathRestrictionValidator
# ---------------------------------------------------------------------------

class PathRestrictionValidator(Validator):
    """Blocks file access outside allowed directories.

    Denied paths are checked first, so an explicit block beats an allow
    even when the path also sits under an allowed prefix.
    """

    def __init__(
        self,
        allowed_paths: list[str],
        denied_paths: list[str] | None = None,
    ) -> None:
        self.allowed = allowed_paths
        self.denied = denied_paths or []

    def check(self, tool_call: ToolCall) -> ValidationResult:
        path = tool_call.params.get("file_path", "")

        for denied in self.denied:
            if path.startswith(denied):
                return ValidationResult(
                    blocked=True, reason=f"Path {path} is denied"
                )

        if not any(path.startswith(allowed) for allowed in self.allowed):
            return ValidationResult(
                blocked=True, reason=f"Path {path} not in allowed list"
            )

        return ValidationResult(passed=True)


# ---------------------------------------------------------------------------
# CredentialDetector
# ---------------------------------------------------------------------------

class CredentialDetector(Validator):
    """Detects credentials and secrets in tool call parameters."""

    PATTERNS: list[re.Pattern[str]] = [
        re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*\S+"),
        re.compile(r"(?i)bearer\s+[a-zA-Z0-9\-._~+/]+=*"),
        re.compile(r"AKIA[0-9A-Z]{16}"),  # AWS access key prefix
        re.compile(r"ghp_[a-zA-Z0-9]{36}"),  # GitHub personal access token
        re.compile(r"sk-[a-zA-Z0-9]{32,}"),  # OpenAI-style API key
    ]

    def check(self, tool_call: ToolCall) -> ValidationResult:
        for value in tool_call.params.values():
            if not isinstance(value, str):
                continue
            for pattern in self.PATTERNS:
                if pattern.search(value):
                    return ValidationResult(
                        blocked=True,
                        reason="Credential detected in parameters",
                    )
        return ValidationResult(passed=True)


# ---------------------------------------------------------------------------
# AbsoluteBoundary
# ---------------------------------------------------------------------------

class AbsoluteBoundary(Validator):
    """Actions that are never permitted, regardless of context.

    These are hard constraints that no override can bypass. They map to
    the AGILITY framework's Limitations (L) pillar.

    Substring matching is the lab's simplification. It over-blocks
    (documentation that mentions `rm -rf /` trips it) and under-blocks
    (`rm -r -f --no-preserve-root /` slips past). The parsing version in
    `code-examples/composable_validators.py` fixes both.
    """

    FORBIDDEN: list[str] = [
        "DELETE FROM production",
        "chmod 777",
        "disable_security_controls",
        "--no-verify",
        "rm -rf /",
    ]

    def check(self, tool_call: ToolCall) -> ValidationResult:
        command = str(tool_call.params).lower()
        for pattern in self.FORBIDDEN:
            if pattern.lower() in command:
                return ValidationResult(
                    blocked=True,
                    reason=f"Absolute boundary: '{pattern}'",
                )
        return ValidationResult(passed=True)
