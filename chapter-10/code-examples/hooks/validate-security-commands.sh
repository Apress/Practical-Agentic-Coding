#!/bin/bash
# .claude/hooks/validate-security-commands.sh
# Ensures security-ash-agent can only run approved security tools.
# Reference: Chapter 10, Section 10.5
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Allow only security analysis tools
ALLOWED="^(ash |bandit |semgrep |checkov )"
if ! echo "$COMMAND" | grep -qE "$ALLOWED"; then
  echo "Blocked: only security tools (ash, bandit, semgrep, checkov) allowed" >&2
  exit 2
fi
exit 0
