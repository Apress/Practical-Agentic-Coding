"""
Composable validators for agent tool calls.

This module implements the composable validator pattern from Chapter 12,
Section 12.3. Each validator targets one specific risk (path traversal,
credential exposure, absolute boundaries) and validators chain together
into pipelines.

Students implement the check() method for each validator and the
validate() method for the pipeline.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Data structures (given)
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
# Base class (given)
# ---------------------------------------------------------------------------

class Validator:
    """Base class for all validators.

    Subclasses must implement check() which inspects a ToolCall and
    returns a ValidationResult indicating whether the call is allowed.
    """

    def check(self, tool_call: ToolCall) -> ValidationResult:
        raise NotImplementedError("Subclasses must implement check()")


# ---------------------------------------------------------------------------
# ValidatorPipeline (partially given)
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
        """Run all validators in order. Return first blocking result.

        If no validator blocks the call, return a passing result.

        TODO: Iterate through self.validators. For each one, call
        validator.check(tool_call). If the result has blocked=True,
        return that result immediately (short-circuit). If all pass,
        return ValidationResult(passed=True).
        """
        # TODO: Implement the validation loop described above
        raise NotImplementedError("TODO: implement validate()")


# ---------------------------------------------------------------------------
# PathRestrictionValidator (starter with TODO)
# ---------------------------------------------------------------------------

class PathRestrictionValidator(Validator):
    """Blocks file access outside allowed directories.

    Denied paths are checked first (explicit blocks take priority).
    Then the path must start with at least one allowed prefix.
    """

    def __init__(
        self,
        allowed_paths: list[str],
        denied_paths: list[str] | None = None,
    ) -> None:
        self.allowed = allowed_paths
        self.denied = denied_paths or []

    def check(self, tool_call: ToolCall) -> ValidationResult:
        """Validate that tool_call's file_path is permitted.

        Steps:
          1. Extract "file_path" from tool_call.params (default to "").
          2. If the path starts with any entry in self.denied, return
             ValidationResult(blocked=True, reason=f"Path {path} is denied").
          3. If the path does NOT start with any entry in self.allowed,
             return ValidationResult(blocked=True,
                                     reason=f"Path {path} not in allowed list").
          4. Otherwise return ValidationResult(passed=True).

        TODO: Implement the logic described above.
        """
        # TODO: Implement path restriction checking
        raise NotImplementedError("TODO: implement PathRestrictionValidator.check()")


# ---------------------------------------------------------------------------
# CredentialDetector (starter with TODO)
# ---------------------------------------------------------------------------

class CredentialDetector(Validator):
    """Detects credentials and secrets in tool call parameters.

    Scans all string values in tool_call.params for patterns that
    look like API keys, passwords, or tokens.
    """

    # Common credential patterns (given)
    PATTERNS: list[re.Pattern[str]] = [
        re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*\S+"),
        re.compile(r"(?i)bearer\s+[a-zA-Z0-9\-._~+/]+=*"),
        re.compile(r"AKIA[0-9A-Z]{16}"),  # AWS access key prefix
        re.compile(r"ghp_[a-zA-Z0-9]{36}"),  # GitHub personal access token
        re.compile(r"sk-[a-zA-Z0-9]{32,}"),  # OpenAI-style API key
    ]

    def check(self, tool_call: ToolCall) -> ValidationResult:
        """Scan all string parameter values for credential patterns.

        Steps:
          1. Iterate over all values in tool_call.params.
          2. For each value that is a string, check it against every
             pattern in self.PATTERNS using pattern.search(value).
          3. If any pattern matches, return
             ValidationResult(blocked=True,
                              reason="Credential detected in parameters").
          4. If no patterns match, return ValidationResult(passed=True).

        TODO: Implement credential scanning.
        """
        # TODO: Implement credential detection
        raise NotImplementedError("TODO: implement CredentialDetector.check()")


# ---------------------------------------------------------------------------
# AbsoluteBoundary (starter with TODO)
# ---------------------------------------------------------------------------

class AbsoluteBoundary(Validator):
    """Actions that are never permitted, regardless of context.

    These are hard constraints that no override can bypass. They map
    to the AGILITY framework's Limitations (L) pillar.
    """

    FORBIDDEN: list[str] = [
        "DELETE FROM production",
        "chmod 777",
        "disable_security_controls",
        "--no-verify",
        "rm -rf /",
    ]

    def check(self, tool_call: ToolCall) -> ValidationResult:
        """Check whether the tool call contains any forbidden pattern.

        Steps:
          1. Convert tool_call.params to a string with str() and
             lowercase it.
          2. For each pattern in self.FORBIDDEN, check if
             pattern.lower() appears in the lowercased command string.
          3. If found, return ValidationResult(blocked=True,
                 reason=f"Absolute boundary: '{pattern}'").
          4. If none match, return ValidationResult(passed=True).

        TODO: Implement absolute boundary checking.
        """
        # TODO: Implement absolute boundary enforcement
        raise NotImplementedError("TODO: implement AbsoluteBoundary.check()")
